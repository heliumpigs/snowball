# Copyright 2009 Michael Whidby
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

from tornado import web
from oz.handler import *
import model, scarecrow, uuid, datetime

from web import *
from web import util
from web.serialization import *

class TagHandler(util.SnowballHandler):
    """Endpoint for handling the manipulation of tags"""
    
    @util.error_handler
    def get(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        node = request.db[hash]
        
        try:
            node = self.db[hash]
        except KeyError:
            raise web.HTTPError(404)       
        
        serialize(self, node.tags)
    
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def put(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        
        tags = util.check_tags(self.get_argument('tags', None))
        if not tags:
            raise web.HTTPError(400, "requires 'tags' parameter")
        
        try:
            node = self.db[hash]
        except KeyError:
            #return a not found if the node doesn't exist
            raise web.HTTPError(404)
            
        if node.owner != self.current_user:
            #return a forbidden if the current user doesn't own the node
            raise web.HTTPError(403)
        
        for tag in tags:
            node.tags.add(tag)
        
        self.db[hash] = node
        serialize(self, tags)
    
    @basic_auth(util.REALM, util.auth)
    @util.error_handler
    def delete(self, uri):
        hash = scarecrow.ident(model.node_key(uri))
        delete_tags = util.check_tags(self.get_argument('tags', None))
        
        try:
            node = self.db[hash]
        except KeyError:
            #return a not found if the node doesn't exist
            raise web.HTTPError(404)
        
        if node['owner'] != self.current_user:
            #return a forbidden if the current user doesn't own the node
            raise web.HTTPError(403)
        
        try:
            if delete_tags == None:
                node.tags = ([])
            else:
                for tag in delete_tags:
                    node.tags.remove(tag)
        except KeyError:
            raise web.HTTPError(404)
            
        self.db[hash] = node