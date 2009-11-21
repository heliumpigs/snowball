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
import model

from web import *
from web import util
from web.serialization import *

class ErrorHandler(util.SnowballHandler):
    """
    Returns Snowball formatted error messages if the client requests an unknown
    resource
    """
    
    @util.error_handler
    def head(self, path):
        raise web.HTTPError(404)
        
    @util.error_handler
    def get(self, path):
        raise web.HTTPError(404)
        
    @util.error_handler
    def post(self, path):
        raise web.HTTPError(404)
    
    @util.error_handler
    def delete(self, from_node, to_node):
        raise web.HTTPError(404)
    
    @util.error_handler
    def put(self, from_node, to_node):
        raise web.HTTPError(404)