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

import model, pickle
from scarecrow import mysql
    
class MysqlLinksIndex(object):
    def __init__(self, name):
        self.name = name
        
    def install(self, db):
        db.execute("""CREATE TABLE %s (
                        entity_id BINARY(16) NOT NULL,
                        to_link BINARY(16) NOT NULL,
                        owner BINARY(16) NOT NULL,
                        PRIMARY KEY (entity_id, to_link)
                      ) ENGINE=InnoDB
                   """ % self.name)
    
    def map(self, db, obj_id, obj):
        if 'links' in obj and 'type' in obj and obj['type'] == 'node':
            for link_uri in obj.links:
                link_hash = model.node_key(link_uri)
                link_obj = self.model[link_hash]
                
                if link_obj == None: continue
                link_owner = model.account_key(link_obj.owner)
                
                db.execute("INSERT INTO " + self.name + " VALUES (%s, %s, %s)", obj_id, link_hash, link_owner)
                
    def get(self, db, to_link, owner=None):
        query = "SELECT body FROM entities JOIN %s ON entities.id=%s.entity_id WHERE to_link=%s" % (self.name, self.name, '%s')
        
        if owner:
            query += " AND owner=%s"
            results = db.query(query, to_link, owner)
        else:
            results = db.query(query, to_link)
        
        if results == None: return
        
        for row in results:
            yield pickle.loads(row.body)
                
    def get_ids(self, db, to_link, owner=None):
        query = "SELECT entity_id FROM entities JOIN %s ON entities.id=%s.entity_id WHERE to_link=%s" % (self.name, self.name, '%s')
        
        if owner:
            query += " AND owner=%s"
            results = db.query(query, to_link, owner)
        else:
            results = db.query(query, to_link)
        
        if results == None: return
        
        for row in results:
            yield row.entity_id
        
    def random(self, db, seed='', count=1):
        if seed != '': int(seed)
        int(count)
        
        results = db.query("SELECT entity_id, to_link FROM %s ORDER BY RAND(%s) LIMIT %s" % (self.name, seed, count))
        for row in results: yield row.entity_id, row.to_link

def db(host, dbname, user, password):
    links_index = MysqlLinksIndex('links_index')
    type_index = mysql.AttributeIndex('type_index', 'type', unicode)
    return mysql.Model(host, dbname, user, password, links_index, type_index)