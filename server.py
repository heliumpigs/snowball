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

import tornado.web
import logging, model, settings_parser, os
from web.view import recommendations, links, nodes, tags, error
from web.admin import admin

def main():
    """Runs the Snowball server"""
    
    #Parse the settings
    parser = settings_parser.SettingsParser(sys.argv)
    type = parser.get('type', 'tornado')
    port = parser.get('port', 8080, int)
    db = settings_parser.acquire_model(parser)
    
    admin_enabled = parser.get('admin_enabled', False)
    admin_pass = parser.get('admin_pass')
    
    #Delete db settings, which contains sensitive data (like the database password)
    for setting in parser.settings.keys():
        if setting.startswith('db'):
            del parser.settings[setting]
            
    #This setting means that clients can set an error_format parameter to control the format of error outputs
    parser.settings['output_type_override'] = 'error_format'
    
    #Store a connection to the database in the settings
    parser.settings['db'] = db
    
    #Tornado setting for the path to static files
    parser.settings['static_path'] = os.path.join(os.path.dirname(__file__), 'web/static')
    
    routes = [
        (r'^/recommendations/(.+)/(.+)$', recommendations.RecommendationHandler),
        (r'^/recommendations/(.+)$', recommendations.RecommendationSetHandler),
        
        (r'^/links/(.+)/(.+)$', links.LinkHandler),
        (r'^/links/(.+)$', links.LinkSetHandler),
        
        (r'^/tags/(.+)/(.+)$', tags.TagHandler),
        (r'^/tags/(.+)$', tags.TagHandler),
        (r'^/tags$', tags.TagHandler),
        
        (r'^/nodes/(.+)$', nodes.NodeHandler),
        (r'^/nodes$', nodes.PostNodeHandler),
    ]
    
    #Conditional endpoints
    if admin_enabled:
        routes.append((r'/admin(.*)$', admin.AdminHandler))
        
    #Error endpoint
    routes.append((r'^(?!\/static\/)(.*)$', error.ErrorHandler))
                
    if type == 'wsgi':
        #Runs a WSGI-compliant server
        import tornado.wsgi
        import wsgiref.handlers
        
        app = tornado.wsgi.WSGIApplication(routes, **parser.settings)
        wsgiref.handlers.CGIHandler().run(app)
    elif type == 'tornado':
        #Runs the tornado server
        import tornado.httpserver
        import tornado.ioloop
        
        app = tornado.web.Application(routes, **parser.settings)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    else:
        parser.error('Unknown server type: %s' % type)

if __name__ == "__main__": main()