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

import model, settings_parser

#Sample accounts used by the test scripts
SAMPLE_DATA_ACCOUNTS = (
    'netflix.com',
    
    'blackbox1',
    'blackbox2',
    
    'site1',
    'site2',
    'site3',
    'site4',
    'site5',
    'site6',
    'site7',
    'site8',
    'site9',
    'site10',
)

def main():
    """Exposes utilities for setting up a Snowball instance"""
    
    parser = settings_parser.SettingsParser(sys.argv, '<settings profile> <command 1> ... <command n>')
    db = settings_parser.acquire_model(parser)
    
    for arg in parser.args[1:]:
        if arg == 'db':
            setup_db(db)
        elif arg == 'testusers':
            add_test_users(db)
        else:
            sys.stderr.write("Unknown task: '%s'" % arg)
    
def setup_db(db):
    """Creates the database and tables; deletes any old data"""
    
    print 'Setting up the database'
    print 'WARNING: This operation will remove any data in the database'
    print 'Are you sure you want to continue? (y/n)'
    
    response = sys.stdin.read(1)
    if response != 'y':
        print 'Operation aborted'
        return
    
    db.install(True)

def add_test_users(db):
    """Adds the users that are used in the test cases to the database"""
        
    for account in SAMPLE_DATA_ACCOUNTS:
        model.create_account(db, account, 'sandbox')

if __name__ == '__main__': main()