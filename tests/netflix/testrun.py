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

import sys, glob, os

def main():
    if len(sys.argv) != 4 or sys.argv[1] == '-h':
        print 'USAGE: python testgen.py <path to restclient> <dir test data> <output dir>'
        return
        
    client_path = sys.argv[1]
    test_dir = sys.argv[2]
    output_dir = sys.argv[3]
    
    p1, f1 = run(client_path, test_dir, output_dir, 'movies')    
    p2, f2 = run(client_path, test_dir, output_dir, 'customers')
    p3, f3 = run(client_path, test_dir, output_dir, 'links')
    
    passed = p1 + p2 + p3
    failed = f1 + f2 + f3
    
    print 'STATISTICS:'
    print '    Total Passed: %s' % passed
    print '    Total Failed: %s' % failed
    
def run(client_path, test_dir, output_dir, prefix):
    pattern = os.path.join(test_dir, '%s_*.xml' % prefix)
    passed = 0
    failed = 0
    
    for file in glob.glob(pattern):
        output_file = os.path.basename(file) + '.txt'
        output_path = os.path.join(output_dir, output_file)
        
        print 'Running %s' % file
        os.system('python %s -t 4 %s &> %s' % (client_path, file, output_path))
        
        file = open(output_path, 'r')
        lines = file.readlines()
        
        line = lines[-2]
        index = line.find('Total Passed: ')
        passed += int(line[index + 14:])
        
        line = lines[-1]
        index = line.find('Total Failed: ')
        failed += int(line[index + 14:])
        
        file.close()
        
    return passed, failed
    

if __name__ == '__main__': main()