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
    parser = optparse.OptionParser("usage: %prog <host> <input dir> <output dir>")
    (options, args) = parser.parse_args()
    
    if len(args) < 3:
        parser.error('Missing required arguments')
        
    host = util.clean_host_arg(args[0])
    input_dir = os.path.join(os.path.dirname(__file__), args[1])
    output_dir = os.path.join(os.path.dirname(__file__), args[2])
    customers = set([])
    
    for file in os.listdir(input_dir):
        print 'Processing file ' + file
        tests = []
        
        for line in open(os.path.join(input_dir, file)):
            line = line.strip()
            if line == '' or line.endswith(':'): continue
            
            customer_id = int(line.split(',', 2)[0])
            customers.add(customer_id)
    
    tests = [] 
    i = 0
    
    for customer in customers:
        url = util.CUSTOMER_TEMPLATE % customer_id
        tests.append(util.create_testcase(host, url, 'customer'))
        
        i += 1
        if i % 1000 == 0:
            util.save_tests_from_ratings_file(tests, output_dir, str(i), 'customers')
            tests = []

if __name__ == '__main__':
    main()