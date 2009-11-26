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

import optparse, datetime, urllib, test_xml

MOVIE_TEMPLATE = 'netflix.com/movie/%s'
CUSTOMER_TEMPLATE = 'netflix.com/customer/%s'

def main():
    parser = optparse.OptionParser("usage: %prog <host> <output dir> <movie descriptor> <input dir>")
    (options, args) = parser.parse_args()
    
    if len(args) != 4:
        parser.error('Missing required arguments')
    
    global host
    host = args[0]
    output_dir = os.path.join(os.path.dirname(__file__), args[1])
    movie_descriptor = os.path.join(os.path.dirname(__file__), args[2])
    input_dir = os.path.join(os.path.dirname(__file__), args[3])
    
    movies = {}
    customers = set([])
    links = {}
    
    print 'Processing movie descriptor'
    for line in open(movie_descriptor, 'r'):
        line = line.strip()
        if line == '': continue
        
        parts = line.split(',', 2)
        movie_id = parts[0]
        year = int(parts[1]) if parts[1] != 'NULL' else None
        title = parts[2]
        
        movies[movie_id] = (title, year)
    
    for file in os.listdir(input_dir):
        print 'Processing file ' + file
        
        for line in open(os.path.join(input_dir, file), 'r'):
            line = line.strip()
            if line == '' or line.endswith(':'): continue
            
            parts = line.split(',', 2)
            customer_id = int(parts[0])
            rating = int(parts[1])
            
            year = int(parts[2][0:4])
            month = int(parts[2][5:7])
            day = int(parts[2][8:])
            date = datetime.date(year, month, day)
            
            customers.add(customer_id)
            links[(customer_id, movie_id)] = (rating, date)
    
    #Write the movies
    movie_root = test_xml.test()
    i = 0
    for movie in movies:
        create_movie_node(movie_root, i, movie, *movies[movie])
        i += 1
    write_file('movies', movie_root)
    
    #Write the customers
    customer_root = test_xml.test()
    i = 0
    for customer in customers:
        create_customer_node(customer_root, i, customer)
        i += 1
    write_file('customers', customer_root)
    
    #Write the links
    links_root = test_xml.test()
    i = 0
    for link in links:
        create_link(links_root, i, link[0], link[1], *links[link])
        i += 1
    write_file('links', links_root)
    
def write_file(name, root):
    ElementTree(root).write(name + '.xml')
    del root
     
def _create_node(root, i, uri, *tags):
    global host
    
    name = 'Create node #%s' % i
    url = 'http://%s/nodes/%s' % (host, urllib.quote(uri, ''))
    input_tags = ' '.join(tags)
    
    code = u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['links'] == {}
        assert json['creation_date']
        assert json['owner'] == 'netflix.com'
        assert json['type'] == 'node'
        assert json['id'] == '%s'
        assert len(json['tags']) == %s""" % (uri, len(tags))
    
    for tag in tags:
        code += u"\n        assert '%s' in json['tags']" % tag
        
    test_xml.testcase(root, name, 'PUT', url, 200, ('netflix.com', 'sandbox'), code, tags=input_tags)

def create_movie_node(root, i, movie_id, title, year):
    url = MOVIE_TEMPLATE % movie_id
    
    #TODO: fetch more tags
    tags = []
    if year != None: tags.append(str(year))
    
    _create_node(root, i, url, 'movie', *tags)

def create_customer_node(root, i, customer_id):
    url = CUSTOMER_TEMPLATE % customer_id
    _create_node(root, i, url, 'customer')

def create_link(root, i, customer_id, movie_id, rating, rating_date):
    name = 'Create link #%s' % i
    rating = 0.5 * (rating - 3)
    
    customer_uri = CUSTOMER_TEMPLATE % customer_id
    movie_uri = MOVIE_TEMPLATE % movie_id
    url = 'http://%s/links/%s/%s' % (host, urllib.quote(customer_uri, ''), urllib.quote(movie_uri, ''))
    
    code = u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['update_date']
        assert json['weight'] == %s
        assert json['tags'] == []
        """ % rating
        
    test_xml.testcase(root, name, 'PUT', url, 200, ('netflix.com', 'sandbox'), code, weight=rating)
    
if __name__ == '__main__': main()