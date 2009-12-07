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

import sys, glob, os, optparse

def main():
    parser = optparse.OptionParser("usage: %prog <path to restclient> <test data dir> [-t <threads>]")
    parser.add_option('-t', '--threads', dest='threads', type='int', default=1, help='Number of concurrent threads to execute (default 1)')
    (options, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.error('Missing required arguments')
        
    global client_path, test_dir, threads
    client_path = args[0]
    test_dir = args[1]
    threads = options.threads
    
    p1, f1 = run('movies.p')    
    p2, f2 = run('*.customers.p')
    p3, f3 = run('*.ratings.p')
    
    passed = p1 + p2 + p3
    failed = f1 + f2 + f3
    
    print 'STATISTICS:'
    print '    Total Passed: %s' % passed
    print '    Total Failed: %s' % failed
    
def run(pattern):
    global client_path, test_dir, threads
    
    pattern = os.path.join(test_dir, pattern)
    passed = 0
    failed = 0
    
    for file in glob.glob(pattern):
        output_file = os.path.basename(file) + '.results.txt'
        output_path = os.path.join(test_dir, output_file)
        
        print 'Running %s' % file
        os.system('python %s -t 4 -s %s -v %s &> %s' % (client_path, threads, file, output_path))
        
        file = open(output_path, 'r')
        lines = file.readlines()
        
        line = lines[-2]
        index = line.find('PASSED: ')
        passed += int(line[index + 8:])
        
        line = lines[-1]
        index = line.find('FAILED: ')
        failed += int(line[index + 8:])
        
        file.close()
        
    return passed, failed
    

if __name__ == '__main__': main()