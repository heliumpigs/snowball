# Copyright 2009 Yusuf Simonson
# This file is part of Snowball.
#
# Snowball is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Snowball is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Snowball.  If not, see <http://www.gnu.org/licenses/>.

import sys, model, util
from math import sqrt

def _weight(node, link):
    """Gets the weight of a link; returns 0.0 if the link doesn't exist"""
    value = node.links.get(link)
    return value.weight if value else 0.0
    
def _links(db, node):
    """Gets the links to and from a node"""
    links = set(node.links)
    
    for link_id in db.index('links_index', 'get_ids', id, model.account_key(node.owner)):
        links.update(link_id)
    
    return links

def _summation(node, links, func):
    """Returns the sigma of func applied to the weight of each link"""
    return sum([func(_weight(node, link)) for link in links])
    
def _parts(node, links):
    """
    Returns the summation and divisor involved in getting the similarity
    between two nodes
    """
    sum = _summation(node, links, lambda x: x)
    squared_sum = _summation(node, links, lambda x: x ** 2)
    
    return sum, squared_sum - (sum ** 2) / len(links)
    
def similarity(node_store, first, second):
    """Returns the similarity between two nodes"""
    first_links = _links(node_store.db, first)
    second_links = _links(node_store.db, second)
    links = first_links.union(second_links)
    
    mul_sum = sum([_weight(first, link) * _weight(second, link) for link in links])
    first_sum, first_divisor = _parts(first, links)
    second_sum, second_divisor = _parts(second, links)
    
    numerator = (mul_sum - first_sum * second_sum / len(links))
    divisor = sqrt(first_divisor * second_divisor)
    
    if divisor == 0.0: return 0.0
    return numerator / divisor

def bridging(node_store, node):
    """
    Gets the bridging score of a node. This is based on the TANGENT algorithm.
    """
    score = 0.0
    total = 0
    
    for first_uri in node._cache.candidates:
        first_node = node_store[model.node_key(first_uri)]
        
        for second_uri in node._cache.candidates:
            if second_uri in first_node.links:
                score += first_node.links[second_uri].weight
                total += 1
            elif second_uri in first_node._cache.candidates:
                score += first_node._cache.candidates[second_uri]
                total += 1
              
    score = 1 / (score / total) if total > 0 else 0.0
    return score

def recommendation(node_store, from_node, to_node, settings):
    """
    Provides a recommendation score between two explicitly provided nodes.
    """
    if to_node.id in from_node._cache.candidates:
        #If there is a precomputed weight between the two nodes, use it
        weight = from_node._cache.candidates[to_node.id]
    else:
        #Otherwise make the initial weight equal to the similarity between
        #the two nodes
        weight = similarity(node_store, from_node, to_node)
    
    score = weight * bridging(node_store, to_node)
    norm = util.get_dynamic_setting(node_store.db, 'max_score')
        
    #Replace the normalizer if the current score is greater than it
    if norm == None or abs(score) > norm:
        norm = abs(score)
        util.save_dynamic_setting(node_store.db, 'max_score', norm)
    
    #Return the score divided by the normalizer to ensure that the final score
    #is between [-1, 1]
    return score / norm

def recommendations(node_store, node, tags, settings):
    """Gets the recommendations for a given node"""
    max_nodes = int(settings['recommendations']['max_nodes'])
    max_visit = int(settings['recommendations']['max_visit'])
    min_threshold = float(settings['recommendations']['min_threshold'])
    
    recommended = []
    
    #Get a list of potential candidates for the node
    for candidate_uri in candidates(node_store, node, max_visit):
        to_node = node_store[model.node_key(candidate_uri)]
        
        #Skip the candidate if it doesn't have any of the requested tags
        if not has_any_tag(to_node, tags): continue
        
        #Get the recommendation score between the two nodes and add it to the
        #list if it is high enough
        score = recommendation(node_store, node, to_node, settings)
        if score > min_threshold: recommended.append([candidate_uri, score])
    
    #Return a sorted list of recommendations; ensure there are at most
    #max_nodes recommendations
    recommended.sort(cmp=_recommendation_comparator)
    return recommended[:max_nodes]
    
def has_any_tag(node, tags):
    """Returns True if the given node has one or more of the specified tags"""
    if len(tags) == 0: return True
    
    for tag in tags:
        if tag in to_node.tags:
            return True
        
    return False

def _recommendation_comparator(first, second):
    """Comparator for recommendation results so they can be sorted"""
    delta = first[1] - second[1]
    
    if delta > 0:   return 1
    elif delta < 0: return -1
    else:           return 0

def candidates(node_store, root, max_visit):
    """
    Returns a set of candidates that could be used by recommendation algorithms
    for a given node. It is a list of sub-lists, where each sub-list contains
    the uri and resized weight.
    """
    owner = model.account_key(root.owner)
    candidates = {}
    
    #Store a list of already visited links so we don't revisit them
    visited_links = set([uri for uri in root.links])
    visited_links.add(root.id)
    
    #Store a list of already visited nodes so we don't revisit them
    visited_nodes = set(root.id)
    
    #A queue of nodes to process
    queue = [[uri, root.links[uri].weight, 1] for uri in root.links]
    
    #Keep processing all the items in the queue until we reach max_visit to
    #ensure that the recommendations are returned quickly enough if there are
    #a lot of candidates
    while max_visit > 0:
        next_queue = []
        next_visited_links = set([])
        
        #Process all nodes in the current queue
        for uri, weight, count in queue:
            if max_visit <= 0: break
            if uri in visited_nodes: continue
            
            hash = model.node_key(uri)
            node = node_store[hash]
            
            #Visit each outbound link in the currently processed node
            for link_uri in node.links:
                link_weight = node.links[link_uri].weight
                _visit(candidates, visited_links, next_visited_links, next_queue, link_uri, weight, link_weight, count)
                
            #Visit each inbound link to the currently processed node
            for link_node in node_store.db.index('links_index', 'get', hash, owner):
                if uri in link_node.links:
                    link_uri = link_node.id
                    link_weight = weight + link_node.links[uri].weight
                    _visit(candidates, visited_links, next_visited_links, next_queue, link_uri, weight, link_weight, count)
                
            max_visit -= 1
            visited_nodes.add(uri)
            
        #Skip any further logic if we've processed the maximum number of nodes
        if max_visit <= 0 or len(queue) == 0: break
                
        queue = next_queue
        visited_links.update(next_visited_links)
            
    #Each node has been potentially visited multiple times. Average out the
    #scores to create an overall weight
    for uri in candidates:
        weight, count = candidates[uri]
        candidates[uri] = weight / count
        
    #Store the results in the cache
    root._cache.candidates = candidates
    node_store.db[model.node_key(root.id)] = root
    
    return candidates

def _visit(candidates, visited_links, next_visited_links, queue, uri, context_weight, weight, context_count):
    """Visits a link and adds it to the candidates"""
    
    #Skip the link if we've already processed it before
    if uri in visited_links: return
    
    #Increment the count and add the current link weight to the total weight
    weight = context_weight + weight
    count = context_count + 1
    
    #Store the results
    if uri in candidates:
        weighting = candidates[uri]
    else:
        candidates[uri] = weighting = [0.0, 0]
        
    weighting[0] += weight
    weighting[1] += count
    
    queue.append([uri, weight, count])
    next_visited_links.add(uri)

