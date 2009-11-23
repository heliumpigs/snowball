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

import uuid
from datetime import datetime

from tornado import web
from oz.handler import *
import model, scarecrow

from web import *
from web import util
from web.serialization import *

class LinkHandler(util.SnowballHandler):
    """Endpoint for handling the manipulation of links"""
    
    @util.error_handler
    def get(self, from_node, to_node):
        try:
            node = self.db[model.node_key(from_node)]
        except KeyError:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find node')
        
        try:
            link = node.links[to_node]
        except KeyError:
            #Return a not found if the link doesn't exist
            raise web.HTTPError(404, 'could not find link')
        
        serialize(self, link)
    
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def put(self, from_node, to_node):
        from_hash = scarecrow.ident(model.node_key(from_node))
        to_hash = scarecrow.ident(model.node_key(to_node))
        
        weight = util.check_weight(self.get_argument('weight', None))
        tags = util.check_tags(self.get_argument('tags', None))
        
        try:
            node = self.db[from_hash]
        except KeyError:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find from node')
            
        if not to_hash in db:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find to node')
        
        #Return a forbidden if the current user doesn't own the node
        if node.owner != self.current_user:
            raise web.HTTPError(403, 'you do not own the from node')
        
        if to_node in node.links:
            #Update the link if it already exists
            link = node.links[to_node]
            if weight != None:
                link.weight = weight
            if tags:
                link.tags = tags
        else:
            #Require the weight parameter if the link doesn't exist yet
            if weight == None:
                raise web.HTTPError(400, "requires 'weight' parameter")
            
            #Create a new link if it doesn't exist yet
            link = model.Storage()
            node.links[to_node] = link
            
            link.weight = weight
            link.tags = tags if tags else set([])
        
        link.update_date = datetime.now()
        self.db[from_hash] = node
        serialize(self, link)
    
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def delete(self, from_node, to_node):
        from_hash = scarecrow.ident(model.node_key(from_node))
        
        try:
            node = self.db[from_hash]
        except KeyError:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find node')
        
        #Return a forbidden if the current user doesn't own the node
        if node.owner != self.current_user:
            raise web.HTTPError(403, 'you do not own the from node')
        
        if to_node in node.links:
            del node.links[to_node]
        else:
            #Return a not found if the link doesn't exist
            raise web.HTTPError(404, 'could not find link')
        
        self.db[from_hash] = node
            
class LinkSetHandler(util.SnowballHandler):
    @util.error_handler
    def get_from(self, uri):
        try:
            node = self.db[model.node_key(uri)]
        except KeyError:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find node')
        
        serialize(self, node.links)
    
    @util.error_handler
    def get_to(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        
        nodes = self.db.index('links_index', 'get', hash)
        links = {}
        
        #Iterate through all the linked nodes and ensure the link still exists
        #since the index could be stale
        for node in nodes:
            try:
                link = node.links[uri]
                links[node.id] = link
            except:
                pass
        
        #If there were no results, check to see that the node exists; if not,
        #return a not found
        if len(links) == 0 and not hash in self.db:
            raise web.HTTPError(404, 'could not find node')
                
        serialize(self, links)
        
    @util.error_handler
    def get(self, uri):
        direction = self.get_argument('direction')
        util.assert_direction(direction)
        
        if direction == 'from':
            return self.get_from(uri)
        elif direction == 'to':
            return self.get_to(uri)
        
    @util.error_handler
    def delete_from(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        
        try:
            node = self.db[hash]
        except KeyError:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find node')
        
        #Return a forbidden if the current user doesn't own the node
        if node.owner != self.current_user:
            raise web.HTTPError(403, 'you do not own the node')
        
        node.links = {}
        self.db[hash] = node
    
    @util.error_handler
    def delete_to(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        results = False
        
        #Iterate through all the linked nodes and delete the link if it still
        #exists
        for node in self.db.index('links_index', 'get', hash, model.account_key(self.current_user)):
            if not uri in node.links:
                continue
            
            results = True
            
            del node.links[uri]
            self.db[model.node_key(node.id)] = node
               
        #If no changes were made, the node might not exist; throw a not found
        #if it doesn't
        if not results and not node in self.db:
            raise web.HTTPError(404, 'could not find node')
    
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def delete(self, uri):
        direction = self.get_argument('direction')
        util.assert_direction(direction)
        
        if direction == 'from':
            return self.delete_from(uri)
        elif direction == 'to':
            return self.delete_to(uri)