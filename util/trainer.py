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
sys.path.append(os.path.join(os.path.dirname(__file__), '../shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pprint, httplib2, socket, urllib2, model, settings_parser

def main():
    parser = settings_parser.SettingsParser(sys.argv, '[-server <server host>] [-timeout <timeout>] <settings profile>')
    server = parser.get('server', '127.0.0.1:8080', string)
    timeout = parser.get('timeout', '5', int)
    db = settings_parser.acquire_model(parser)
    
    if not server.startswith('http://'): server = 'http://' + server
    if server.endswith('/'): server = server[:len(server) - 1]
    if options.timeout > 0: socket.timeout = options.timeout
    
    successful = failed = 0
    http = httplib2.Http()
    
    for node in db.index('type_index', 'get', 'node'):
        try:
            url = '%s/recommendations/%s' % (server, urllib2.quote(node.id))
            res, content = http.request(url)
            
            if res.status < 200 or res.status > 299:
                sys.stderr.write("Training node '%s' failed: HTTP error code %s\n" % (node.id, res.status))
                failed += 1
        except Exception, e:
            sys.stderr.write("Training node '%s' failed: %s\n" % (node.id, e.message))
            failed += 1
            
    print 'STATISTICS:'
    print '  Successful: %s' % successful
    print '  Failed: %s' % failed

if __name__ == '__main__': main()