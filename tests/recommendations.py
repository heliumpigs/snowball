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
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import optparse, httplib2, settings_parser, model
from math import sqrt

def main():
    parser = settings_parser.SettingsParser(sys.argv, '[-s <seed>] <config file> <num tests>')
    
    if len(parser.args) != 2:
        parser.error('Must specify number of tests to run')
    
    try:
        tests = int(parser.args[1])
        assert tests > 0
    except:
        parser.error('Test count must be an int greater than 0')
    
    seed = parser.get('seed', '', int)
    db = settings_parser.acquire_model(parser)
    links = db.index('links_index', 'random', seed, tests)
    
    http = httplib2.Http()
    rmse = avg = 0.0
    total = 0
    
    for link in links:
        from_hash, to_hash = link
        from_node = db[from_hash]
        to_node = db[to_hash]
        
        if not to_node.id in from_node.links:
            continue
        
        link = from_node.links[to_node.id]
        del from_node.links[to_node.id]
        db[from_hash] = from_node
        
        url = 'http://localhost:8080/recommendations/%s/%s' % (from_node.id, to_node.id)
        res, content = http.request(url)
        
        if res.status != 200:
            sys.stderr.write('%s returned unexpected HTTP code %s\n' % (url, res.status))
        else:
            try:
                distance = float(content) - link.weight
                rmse += distance ** 2
                avg += distance
                total += 1
            except:
                sys.std.err.write('could not parse %s\n' % url)
                
        from_node.links[to_node.id] = link
        db[from_hash] = from_node
        
    rmse = sqrt(rmse / total) if total > 0 else 0.0
    print 'rmse: %s' % rmse
    
    avg = avg / total
    print 'average distance: %s' % avg
    
if __name__ == '__main__': main()