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

try:
    import xml.etree.cElementTree as et
except:
    import xml.etree.ElementTree as et
    
try:
    import cPickle as pickle
except:
    import pickle

import optparse, random, re, sys
from catnap import model, util

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

def create_node(host, num, account, *tags):
    name = 'Create node #%s' % num
    url = 'http://%s/nodes/%s' % (host, num)
    
    data = (str(num), account)
    input_tags = ' '.join(tags)
    
    code = util.detab_contents(u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['links'] == {}
        assert json['creation_date']
        assert json['owner'] == '%s'
        assert json['type'] == 'node'
        assert json['id'] == '%s'
        assert len(json['tags']) == %s""" % (account, num, len(tags)))
    
    for tag in tags:
        code += u"\nassert '%s' in json['tags']" % tag
        
    request_body = model.RequestBody('post')
    request_body.value['tags'] = input_tags
    expected_body = model.ExpectedBody('python', code)
        
    test = model.TestCase(name, 'PUT', url, headers={}, auth=(account, 'sandbox'),
                          body=request_body, expected_status=200, expected_body=expected_body)
    
    test.id = num
    return test

def create_link(host, from_node, to_node, weight, *tags):
    name = 'Create link from %s to %s' % (from_node.id, to_node.id)
    url = 'http://%s/links/%s/%s' % (host, from_node.id, to_node.id)
    input_tags = ' '.join(tags)
    
    code = util.detab_contents(u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['update_date']
        assert json['weight'] == %s
        assert len(json['tags']) == %s""" % (weight, len(tags)))
    
    for tag in tags:
        code += u"\nassert '%s' in json['tags']" % tag
        
    request_body = model.RequestBody('post')
    request_body.value['tags'] = input_tags
    request_body.value['weight'] = str(weight)
    expected_body = model.ExpectedBody('python', code)
    
    return model.TestCase(name, 'PUT', url, headers={}, auth=(from_node.auth[0], 'sandbox'),
                          body=request_body, expected_status=200, expected_body=expected_body)
    
def main():
    parser = optparse.OptionParser("usage: %prog [-s <seed>] <host> <number of nodes> <output file>")
    parser.add_option('-s', '--seed', dest='seed', type='int', default=None, help='Seed for randomization')
    
    (options, args) = parser.parse_args()
    
    #check to make sure required arguments have been passed in
    if len(args) != 3:
        parser.error('Missing required arguments')
    
    if options.seed:
        random.seed(options.seed)
        
    host = args[0]
    if host.startswith('http://'):
        host = host[7:]
    if host.endswith('/'):
        host = host[:-1]
        
    try:    
        n = int(args[1])
        assert n > 0
    except:
        parser.error('Number of nodes argument must be an integer greater than 0')
        
    output_file = args[2]
        
    nodes = []
    for i in xrange(0, n):
        tags = random_tags()
        account = random.choice(ACCOUNTS)
        nodes.append(create_node(host, i, account, *tags))
    
    tests = []
    tests.extend(nodes)
    
    for node in nodes:
        links = set([])
        
        for i in xrange(0, random_link_count()):
            from_node = None
            attempts = 0
            while (from_node is None or from_node == node or from_node in links) and attempts < 10:
                from_node = random.choice(nodes)
                attempts += 1
            
            links.add(from_node)
            tags = random_tags()
            weight = random.random() * 2 - 1
            
            tests.append(create_link(host, from_node, node, weight, *tags))
            
    with open(output_file, 'w') as file:
        pickle.dump(tests, file)

if __name__ == '__main__': main()