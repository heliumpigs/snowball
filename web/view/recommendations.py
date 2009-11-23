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

import uuid, cache, datetime, model

from tornado import web
from oz.handler import *

from web import *
from web import util, engine
from web.serialization import *

class RecommendationHandler(util.SnowballHandler):
    """Endpoint for handling recommendations between two nodes"""
    
    @util.error_handler
    def get(self, from_uri, to_uri):
        node_store = cache.NodeStore(self.db, 4)
        
        try:
            from_node = node_store[model.node_key(from_uri)]
        except KeyError:
            raise web.HTTPError(404, 'could not find from node')
        
        try:
            to_node = node_store[model.node_key(to_uri)]
        except KeyError:
            raise web.HTTPError(404, 'could not find to node')
        
        rec = engine.recommendation(node_store, from_node, to_node, self.application.settings)
        if not rec:
            rec = 0.0
        
        serialize(self, rec)
        
class RecommendationSetHandler(util.SnowballHandler):
    """Endpoint for handling recommendations for a given node"""
    
    @util.error_handler
    def get(self, uri):
        max_visit = self.application.settings['recommendations']['max_visit']
        
        tags = util.check_tags(self.get_argument('tags', ''))
        node_store = cache.NodeStore(self.db, max_visit + 1)
        
        try:
            from_node = node_store[model.node_key(uri)]
        except KeyError:
            raise web.HTTPError(404, 'could not find node')
        
        recs = engine.recommendations(node_store, from_node, tags, self.application.settings)
        serialize(self, recs)