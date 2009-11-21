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

#server settings
type = 'tornado'
debug = True
port = 8080
default_format = 'json'

#admin settings
admin_enabled = True
admin_pass = 'admin'

#datastore settings
dstype = 'mysql'
dbhost = 'localhost:3306'
dbname = 'sandbox'
dbuser = 'root'

#recommendation settings
max_visit = 300
min_threshold = 0.0
max_nodes = 100