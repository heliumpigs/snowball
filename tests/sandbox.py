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

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    import xml.etree.cElementTree as et
except:
    import xml.etree.ElementTree as et

import optparse, random, urllib, re, test_xml
from xml.dom import minidom

ACCOUNTS = (
    'site1',
    'site2',
    'site3',
    'site4',
    'site5',
    'site6',
    'site7',
    'site8',
    'site9',
    'site10',
)

TAGS = ('product', 'user', 'a', 'b', 'c',)

LINK_PROBABILITY = 0.55
MAX_LINKS = 100

def random_link_count():
    multiplier = 0
    while random.random() < LINK_PROBABILITY: multiplier += 1
    
    return random.randint(0, int(random.random() * multiplier * 10))
    
def random_tags():
    tags = set([])
    
    for i in range(0, random.randint(0, len(TAGS) - 1)):
        tag = None
        while tag is None or tag in tags: tag = random.choice(TAGS)
        tags.add(tag)
        
    return tags

def create_node_xml(root, host, num, account, *tags):
    name = 'Create node #%s' % num
    
    uri = '%s/%s' % (account, num)
    url = 'http://%s/nodes/%s' % (host, urllib.quote(uri, ''))
    
    data = (uri, account)
    input_tags = ' '.join(tags)
    
    code = u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['links'] == {}
        assert json['creation_date']
        assert json['owner'] == '%s'
        assert json['type'] == 'node'
        assert json['id'] == '%s'
        assert len(json['tags']) == %s""" % (account, uri, len(tags))
    
    for tag in tags:
        code += u"\n        assert '%s' in json['tags']" % tag
        
    test_xml.testcase(root, name, 'PUT', url, 200, (account, 'sandbox'), code, tags=input_tags)
    return data

def create_link_xml(root, host, num, from_node, to_node, weight, *tags):
    name = 'Create link #%s' % num
    url = 'http://%s/links/%s/%s' % (host, urllib.quote(from_node[0], ''), urllib.quote(to_node[0], ''))
    input_tags = ' '.join(tags)
    
    code = u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['update_date']
        assert json['weight'] == %s
        assert len(json['tags']) == %s""" % (weight, len(tags))
    
    for tag in tags:
        code += u"\n        assert '%s' in json['tags']" % tag
        
    test_xml.testcase(root, name, 'PUT', url, 200, (from_node[1], 'sandbox'), code, tags=input_tags, weight=weight)
    
def main():
    parser = optparse.OptionParser("usage: %prog [-s <seed>] <host> <number of nodes>")
    parser.add_option('-s', '--seed', dest='seed', type='int', default=None, help='Seed for randomization')
    
    (options, args) = parser.parse_args()
    
    #check to make sure required arguments have been passed in
    if len(args) != 2:
        parser.error('Missing required arguments')
    
    if options.seed:
        random.seed(options.seed)
        
    try:    
        n = int(args[1])
    except:
        parser.error('Number of nodes argument must be an integer')
        
    host = args[0]
    root = test_xml.test()
    
    nodes = []
    for i in range(0, n):
        tags = random_tags()
        account = random.choice(ACCOUNTS)
        
        node_data = create_node_xml(root, host, i, account, *tags)
        nodes.append(node_data)
    
    i = 0
    for node in nodes:
        links = set([])
        
        for j in range(0, random_link_count()):
            i += 1
            
            from_node = None
            attempts = 0
            while (from_node is None or from_node == node or from_node in links) and attempts < 10:
                from_node = random.choice(nodes)
                attempts += 1
            
            links.add(from_node)
            tags = random_tags()
            weight = random.random() * 2 - 1
            
            create_link_xml(root, host, i, from_node, node, weight, *tags)
            
    et.ElementTree(root).write(sys.stdout)

if __name__ == '__main__': main()