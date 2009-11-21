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

import optparse, random, urllib, re
from xml.dom import minidom

class NodeData:
    def __init__(self, uri, account):
        self.uri = uri
        self.account = account

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

def format_tags(*tags):
    if len(tags) > 0:
        return ' '.join(tags)
    else:
        return ''

def create_node_xml(host, num, account, *tags):
    uri = account + '/' + str(num)
    data = NodeData(uri, account)
    input_tags = format_tags(*tags)
    
    code = u"""
assert response.code == 200, 'expected response code 200 but got ' + str(response.code)
    
import simplejson
json = simplejson.loads(contents)

assert json['links'] == {}
assert json['creation_date']
assert json['owner'] == '%s'
assert json['type'] == 'node'
assert json['id'] == '%s'
assert len(json['tags']) == %s
""" % (account, uri, len(tags))
    
    for tag in tags:
        code += u"assert '%s' in json['tags']\n" % tag
    
    print u"""
<testcase>
<name>Create node #%s</name>
<requestMethod>PUT</requestMethod>
<requestURL>http://%s/nodes/%s</requestURL>
<headers />
<authentication>
    <username>%s</username>
    <password>sandbox</password>
</authentication>
<inputbody type="post">
    <tags>%s</tags>
</inputbody>
<expectedOutput type="python">
%s
</expectedOutput>
</testcase>""" % (num, host, urllib.quote(data.uri, ''), account, input_tags, code)
           
    return data

def create_link_xml(host, num, from_node, to_node, weight, *tags):
    input_tags = format_tags(*tags)
    
    code = u"""
assert response.code == 200, 'expected response code 200 but got ' + str(response.code)
    
import simplejson
json = simplejson.loads(contents)

assert json['update_date']
assert json['weight'] == %s
assert len(json['tags']) == %s
""" % (weight, len(tags))
    
    for tag in tags:
        code += u"assert '%s' in json['tags']\n" % tag
    
    print u"""
<testcase>
<name>Create link #%s</name>
<requestMethod>PUT</requestMethod>
<requestURL>http://%s/links/%s/%s</requestURL>
<headers />
<authentication>
    <username>%s</username>
    <password>sandbox</password>
</authentication>
<inputbody type="post">
    <tags>%s</tags>
    <weight>%s</weight>
</inputbody>
<expectedOutput type="python">
%s
</expectedOutput>
</testcase>""" % (num, host, urllib.quote(from_node.uri, ''), urllib.quote(to_node.uri, ''),
                  urllib.quote(from_node.account, ''), input_tags, weight, code)

def main():
    parser = optparse.OptionParser("usage: %prog [-s] -o -n")
    parser.add_option("-s", "--seed", action="store", type="int", dest="seed", help="a seed for randomization")
    parser.add_option("-o", "--host", action="store", type="string", dest="host", help="REQ: hostname")
    parser.add_option("-n", "--nodes", action="store", type="int", dest="nodes", help="REQ: number of nodes to populate")
    
    (options, args) = parser.parse_args()
    
    #check to make sure required arguments have been passed in
    if options.host == None:
        parser.error("Hostname parameter required")
    elif options.nodes == None:
        parser.error("Nodes parameter required")
        
    if options.seed: random.seed(parser.seed)
    
    print u'<?xml version="1.0" encoding="UTF-8" ?><test>'
    nodes = []
    
    for i in range(0, options.nodes):
        tags = random_tags()
        account = random.choice(ACCOUNTS)
        
        node_data = create_node_xml(options.host, i, account, *tags)
        nodes.append(node_data)
    
    i = 0
    for node in nodes:
        links = set([])
        
        for j in range(0, random_link_count()):
            i += 1
            
            from_node = None
            while from_node is None or from_node == node or from_node in links:
                from_node = random.choice(nodes)
            
            links.add(from_node)
            tags = random_tags()
            weight = random.random() * 2 - 1
            
            create_link_xml(options.host, i, from_node, node, weight, *tags)
        
    print u'</test>'

if __name__ == '__main__': main()