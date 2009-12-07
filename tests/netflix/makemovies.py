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
import optparse, os, util

def main():
    parser = optparse.OptionParser("usage: %prog <host> <movie descriptor> <output dir>")
    (options, args) = parser.parse_args()
    
    if len(args) < 3:
        parser.error('Missing required arguments')
        
    host = util.clean_host_arg(args[0])
    movie_descriptor = os.path.join(os.path.dirname(__file__), args[1])
    output_dir = os.path.join(os.path.dirname(__file__), args[2])
    tests = []
    
    print 'Processing file ' + movie_descriptor
    for line in open(movie_descriptor):
        line = line.strip()
        if line == '': continue
        
        parts = line.split(',', 2)
        movie_id = parts[0]
        year = int(parts[1]) if parts[1] != 'NULL' else None
        title = parts[2]
        
        url = util.MOVIE_TEMPLATE % movie_id
        tags = []
        if year != None: tags.append(str(year))
        
        tests.append(util.create_testcase(host, url, 'movie', *tags))
        
    util.save_tests(tests, output_dir, 'movies.p')

if __name__ == '__main__':
    main()