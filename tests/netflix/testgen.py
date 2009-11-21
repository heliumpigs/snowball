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

import os, optparse, datetime, urllib

MOVIE_TEMPLATE = 'netflix.com/movie/%s'
CUSTOMER_TEMPLATE = 'netflix.com/customer/%s'

def main():
    parser = optparse.OptionParser("usage: %prog -o <output dir> <movie descriptor> <input dir>")
    parser.add_option("-o", "--host", action="store", type="string", dest="host", help="REQ: hostname")
    (options, args) = parser.parse_args()
    
    #check to make sure required arguments have been passed in
    if options.host == None:
        parser.error("Hostname parameter required")
        
    if len(args) != 3:
        parser.error("Must specify an output dir, movie descriptor file and an input dir")
        
    global host
    host = options.host
    
    output_dir = args[0]
    movie_descriptor = args[1]
    input_dir = args[2]
    
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
    
    handle = None
    
    i = 0
    for movie in movies:
        if i % 10000 == 0:
            handle = acquire_handle(handle, output_dir, 'movies', i)
        
        create_movie_node(handle, i, movie, *movies[movie])
        i += 1
        
    i = 0
    for customer in customers:
        if i % 10000 == 0:
            handle = acquire_handle(handle, output_dir, 'customers', i)
            
        create_customer_node(handle, i, customer)
        i += 1
        
    i = 0
    for link in links:
        if i % 10000 == 0:
            handle = acquire_handle(handle, output_dir, 'links', i)
            
        create_link(handle, i, link[0], link[1], *links[link])
        i += 1
        
    close_handle(handle)
        
def close_handle(handle):
    handle.write(u"</test>")
    handle.close()
        
def acquire_handle(handle, output_dir, prefix, i):
    if handle != None: close_handle(handle)
    
    file = '%s_%s.xml' % (prefix, i)
    print 'Writing file ' + file
    
    handle = open(os.path.join(output_dir, file), 'w')
    handle.write(u'<?xml version="1.0" encoding="UTF-8" ?><test>')
    return handle

def _format_tags(*tags):
    if len(tags) > 0:
        return ' '.join(tags)
    else:
        return ''
        
def _create_node(handle, i, uri, *tags):
    input_tags = _format_tags(*tags)
    
    code = u"""
import simplejson
json = simplejson.loads(contents)

assert json['links'] == {}
assert json['creation_date']
assert json['owner'] == 'netflix.com'
assert json['type'] == 'node'
assert json['id'] == '%s'
assert len(json['tags']) == %s
""" % (uri, len(tags))
    
    for tag in tags:
        code += u"assert '%s' in json['tags']\n" % tag
    
    handle.write(u"""<testcase>
                  <name>Create node #%s</name>
                  <requestMethod>PUT</requestMethod>
                  <requestURL>http://%s/nodes/%s</requestURL>
                  <headers />
                  <authentication>
                      <username>netflix.com</username>
                      <password>sandbox</password>
                  </authentication>
                  <inputbody type="post">
                      <tags>%s</tags>
                  </inputbody>
<expectedOutput type="python">
%s
</expectedOutput>
              </testcase>
           """ % (i, host, urllib.quote(uri, ''), input_tags, code))

def create_movie_node(handle, i, movie_id, title, year):
    #TODO: fetch more tags
    tags = []
    if year != None: tags.append(str(year))
    
    _create_node(handle, i, MOVIE_TEMPLATE % movie_id, 'movie', *tags)

def create_customer_node(handle, i, customer_id):
    _create_node(handle, i, CUSTOMER_TEMPLATE % customer_id, 'customer')

def create_link(handle, i, customer_id, movie_id, rating, rating_date):
    rating = 0.5 * (rating - 3)
    customer_uri = CUSTOMER_TEMPLATE % customer_id
    movie_uri = MOVIE_TEMPLATE % movie_id
    
    code = u"""
import simplejson
json = simplejson.loads(contents)

assert json['update_date']
assert json['weight'] == %s
assert json['tags'] == []
""" % rating
    
    handle.write(u"""<testcase>
                        <name>Create link #%s</name>
                        <requestMethod>PUT</requestMethod>
                        <requestURL>http://%s/links/%s/%s</requestURL>
                        <headers />
                        <authentication>
                            <username>netflix.com</username>
                            <password>sandbox</password>
                        </authentication>
                        <inputbody type="post">
                            <weight>%s</weight>
                        </inputbody>
<expectedOutput type="python">
%s
</expectedOutput>
                    </testcase>
           """ % (i, host, urllib.quote(customer_uri, ''), urllib.quote(movie_uri, ''), rating, code))

if __name__ == '__main__': main()