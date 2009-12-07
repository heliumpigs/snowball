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
import catnap.util, catnap.model
import optparse, os, util, datetime, urllib

def main():
    parser = optparse.OptionParser("usage: %prog <host> <input dir> <output dir>")
    (options, args) = parser.parse_args()
    
    if len(args) < 3:
        parser.error('Missing required arguments')
        
    host = util.clean_host_arg(args[0])
    input_dir = os.path.join(os.path.dirname(__file__), args[1])
    output_dir = os.path.join(os.path.dirname(__file__), args[2])
    
    for file in os.listdir(input_dir):
        print 'Processing file ' + file
        movie_id = None
        tests = []
        
        for line in open(os.path.join(input_dir, file)):
            line = line.strip()
            if line == '':
                pass
            if line.endswith(':'):
                movie_id = line[:-1]
            else:
                parts = line.split(',', 2)
                customer_id = int(parts[0])
                rating = 0.5 * (int(parts[1]) - 3)
                
                year = int(parts[2][0:4])
                month = int(parts[2][5:7])
                day = int(parts[2][8:])
                date = datetime.date(year, month, day)
                
                name = 'Create link from customer #%s to movie #%s' % (customer_id, movie_id)
                
                customer_uri = util.CUSTOMER_TEMPLATE % customer_id
                movie_uri = util.MOVIE_TEMPLATE % movie_id
                url = 'http://%s/links/%s/%s' % (host, urllib.quote(customer_uri, ''), urllib.quote(movie_uri, ''))
                
                code = catnap.util.detab_contents(u"""
                    import simplejson
                    json = simplejson.loads(contents)
                    
                    assert json['update_date']
                    assert json['weight'] == %s
                    assert json['tags'] == []
                    """ % rating)
                
                request_body = catnap.model.RequestBody('post')
                request_body.value['weight'] = str(rating)
                expected_body = catnap.model.ExpectedBody('python', code)
                
                test = catnap.model.TestCase(name, 'PUT', url, headers={}, auth=('netflix.com', 'sandbox'),
                                      body=request_body, expected_status=200, expected_body=expected_body)
                tests.append(test)
    
        util.save_tests_from_ratings_file(tests, output_dir, file, 'ratings')

if __name__ == '__main__':
    main()