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

import uuid
from datetime import datetime

from tornado import web
from oz.handler import *
import model, scarecrow

from web import *
from web import util
from web.serialization import *

def put_node(request, uri):
    """Updates an existing or creates a new node identified by the given URI"""
    hash = scarecrow.ident(model.node_key(uri))
    tags = util.check_tags(request.get_argument('tags', None))
    date = util.check_datetime(request.get_argument('creation_date', None))
    
    try:
        node = request.db[hash]
        
        #Update an existing node
        if node.owner != request.current_user:
            raise web.HTTPError(403, 'you do not own the node')
        if tags:
            node.tags = tags
        if date:
            node.creation_date = date
    except KeyError:
        if not tags:
            tags = set([])
        if not date:
            date = datetime.now()
        
        #Create a new node if it doesn't exist
        node = model.Entity(uri, 'node')
        node.owner = request.current_user
        node.creation_date = date
        node.tags = tags
        node.links = {}
        
        node._cache = model.Storage()
        node._cache.candidates = model.Storage()
        node._cache.expired = False
    
    node.update_date = datetime.now()
    request.db[hash] = node
    serialize(request, node)

class NodeHandler(util.SnowballHandler):
    """Endpoint for handling the manipulation of nodes"""
    
    @util.error_handler
    def get(self, uri):
        try:
            node = self.db[model.node_key(uri)]
        except KeyError:
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find node')
        
        serialize(self, node)
    
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def put(self, uri):
        return put_node(self, uri)
        
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def delete(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        
        try:
            node = self.db[hash]
        except KeyError:    
            #Return a not found if the node doesn't exist
            raise web.HTTPError(404, 'could not find node')
        
        #Return a forbidden if the current user doesn't own the node
        if node.owner != self.current_user:
            raise web.HTTPError(403, 'you do not own the node')
        
        #Iterate through each linked node and delete the link
        for link_node in self.db.index('links_index', 'get', hash):
            if uri in link_node.links:
                del link_node.links[uri]
            
            self.db[model.node_key(link_node.id)] = link_node
            
        del self.db[hash]
        
class PostNodeHandler(util.SnowballHandler):
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def post(self):
        #Put the node with a randomly generated UUID
        return put_node(self, 'urn:uuid:' + str(uuid.uuid4()))