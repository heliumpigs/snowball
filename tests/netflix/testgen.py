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

import optparse, datetime, urllib, sys, os
from catnap import model, util

MOVIE_TEMPLATE = 'netflix.com/movie/%s'
CUSTOMER_TEMPLATE = 'netflix.com/customer/%s'

def main():
    parser = optparse.OptionParser("usage: %prog <host> <output dir> <movie descriptor> <input dir> [-c <cache size>]")
    parser.add_option('-c', '--cache', dest='cache', type='int', default=5000, help='Size of the cache (default 5000)')
    (options, args) = parser.parse_args()
    
    if len(args) != 4:
        parser.error('Missing required arguments')
        
    global host, output_dir, movie_descriptor, input_dir, cache_size
    
    cache_size = options.cache
    
    host = args[0]
    if host.startswith('http://'):
        host = host[7:]
    if host.endswith('/'):
        host = host[:-1]
    
    output_dir = os.path.join(os.path.dirname(__file__), args[1])
    movie_descriptor = os.path.join(os.path.dirname(__file__), args[2])
    input_dir = os.path.join(os.path.dirname(__file__), args[3])
    movies, customers, links = parse_data()
    
    #Write the movies
    movie_fun = lambda movie: create_movie(movie, *movies[movie])
    create_tests('movies', movies, movie_fun)
    
    #Write the customers
    customer_fun = lambda customer: create_customer(customer)
    create_tests('customers', customers, customer_fun)
    
    #Write the links
    links_fun = lambda link: create_link(link[0], link[1], *links[link])
    create_tests('links', links, links_fun)
    
def create_tests(name, input, fun, *args):
    global output_dir, cache_size
    print 'Creating %s tests' % name
    
    tests = []
    i = 0
    
    for item in input:
        tests.append(fun(item, *args))
        
        i += 1
        if i % cache_size == 0:
            path = os.path.join(output_dir, '%s_%s.p' % (name, i))
            
            print 'Writing file %s' % path
            with open(path, 'w') as file:
                pickle.dump(tests, file)
            
            tests = []
    
def parse_data():
    global output_dir, movie_descriptor, input_dir
    
    cache_file = os.path.join(output_dir, 'cache')
    if os.path.exists(cache_file):
        print 'Cache file found at ' + cache_file
        print 'Loading cache'
        
        try:
            with open(cache_file, 'r') as file:
                return pickle.load(file)
        except Exception, e:
            sys.stderr.write('Error reading cache, reprocessing data\n')
            sys.stderr.write('Cause: ' + str(e) + '\n')
    
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
            
    try:
        with open(cache_file, 'w') as file:
            print 'Writing cache'
            pickle.dump((movies, customers, links), file)
    except Exception, e:
        sys.stderr.write('Error writing cache\n')
        sys.stderr.write('Cause: ' + str(e) + '\n')
        
    return movies, customers, links
     
def _create_testcase(uri, *tags):
    global host
    
    name = 'Create node %s' % uri
    url = 'http://%s/nodes/%s' % (host, urllib.quote(uri, ''))
    input_tags = ' '.join(tags)
    
    code = util.detab_contents(u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['links'] == {}
        assert json['creation_date']
        assert json['owner'] == 'netflix.com'
        assert json['type'] == 'node'
        assert json['id'] == '%s'
        assert len(json['tags']) == %s""" % (uri, len(tags)))
    
    for tag in tags:
        code += u"\nassert '%s' in json['tags']" % tag
        
    request_body = model.RequestBody('post')
    request_body.value['tags'] = input_tags
    expected_body = model.ExpectedBody('python', code)
    
    return model.TestCase(name, 'PUT', url, headers={}, auth=('netflix.com', 'sandbox'),
                          body=request_body, expected_status=200, expected_body=expected_body)

def create_movie(movie_id, title, year):
    url = MOVIE_TEMPLATE % movie_id
    
    #TODO: fetch more tags
    tags = []
    if year != None: tags.append(str(year))
    
    return _create_testcase(url, 'movie', *tags)

def create_customer(customer_id):
    url = CUSTOMER_TEMPLATE % customer_id
    return _create_testcase(url, 'customer')

def create_link(customer_id, movie_id, rating, rating_date):
    name = 'Create link from customer %s to movie %s' % (customer_id, movie_id)
    rating = 0.5 * (rating - 3)
    
    customer_uri = CUSTOMER_TEMPLATE % customer_id
    movie_uri = MOVIE_TEMPLATE % movie_id
    url = 'http://%s/links/%s/%s' % (host, urllib.quote(customer_uri, ''), urllib.quote(movie_uri, ''))
    
    code = util.detab_contents(u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['update_date']
        assert json['weight'] == %s
        assert json['tags'] == []
        """ % rating)
    
    request_body = model.RequestBody('post')
    request_body.value['weight'] = str(rating)
    expected_body = model.ExpectedBody('python', code)
    
    return model.TestCase(name, 'PUT', url, headers={}, auth=('netflix.com', 'sandbox'),
                          body=request_body, expected_status=200, expected_body=expected_body)
    
if __name__ == '__main__': main()