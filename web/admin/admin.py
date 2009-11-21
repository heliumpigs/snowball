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

from web import *
from web import util
from web.serialization import *
from oz.handler import *

REALM = 'Administrator Control Panel'

def admin_auth(req, realm, name, password):
    if realm != REALM or name != 'admin': return False
    return password == req.settings['admin_pass']

class AdminHandler(util.SnowballHandler):
    """Endpoint for the admin control panel"""
    
    @basic_auth(REALM, admin_auth)
    def get(self, path):
        if path == '' or path == '/' or path == '/nodes':
            self.render('nodes.html', page='nodes')
        elif path == '/links':
            self.render('links.html', page='links')
        elif path == '/recommendations':
            self.render('recommendations.html', page='recommendations')
        elif path == '/accounts':
            self.render('accounts.html', page='accounts')