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

import optparse, pprint, model, settings_parser

supported_modes = ('add', 'iter', 'query', 'delete')

def main():
    parser = settings_parser.SettingsParser(sys.argv, '<settings profile> <mode>')
    db = settings_parser.acquire_model(parser)
    
    supported_modes_str = ', '.join(supported_modes[:-1]) + ' or ' + supported_modes[-1]
    if len(args) < 2: parser.error('Mode parameter required (%s)', supported_modes_str)
    if not args[1] in supported_modes: parser.error('Unknown mode: %s. Must be %s', supported_modes_str)
    
    #Read all of the input code until the user feeds a blank line
    code = ''
    while True:
        line = sys.stdin.readline()
        
        if line == '\n':
            break
        else:
            code += line
        
    if options.mode == 'add':
        add(db, code)
    else:
        pp = pprint.PrettyPrinter()
    
        for entity_id in db:
            entity = db[entity_id]
            
            if options.mode == 'iter':
                #Just execute the input code for each entity
                exec code
            elif options.mode == 'query':
                #Print the current entity if the input code returns True for this
                #entity
                if eval(code): pp.pprint(entity)
            elif options.mode == 'delete':
                #Delete the current entity if the input code returns True
                import base64
    
                if eval(code):
                    print 'Deleting entity ' + base64.b16encode(entity_id)
                    del db[entity_id]

def add(db, code):
    """Adds a new entity to the database"""
    import base64
    
    entity_id = None
    entity_key = None
    entity = None
    
    exec code
    
    if entity_key:
        #Generate an id from the key provided by the input key
        import hashlib
        entity_id = hashlib.md5(entity_key).digest()
    elif not entity_id:
        #Throw an error if neither an entity_key or entity_id was specified by
        #the input code
        raise KeyError("Must specify an entity_key or entity_id")
    
    print 'Saved entity ' + base64.b16encode(entity_id)
    db[entity_id] = entity

if __name__ == '__main__': main()