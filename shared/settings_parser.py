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

import sys, getpass, model

class OptionsParser:
    def __init__(self, raw_args, usage):
        self.usage = 'usage: python %s %s' % (raw_args[0], usage)
        
        self.opts = []
        self.args = []
        opt = None
        val = None
        
        for arg in raw_args[1:]:
            if arg.startswith('-'):
                if opt is not None: self.opts.append((opt, val))
                opt = arg[1:]
                val = None
            elif opt is not None and val is None:
                val = arg
            else:
                self.args.append(arg)
        
        if opt is not None: self.opts.append((opt, val))
    
    def show_usage(self):
        print self.usage
        sys.exit(0)
        
    def error(self, msg):
        print self.usage
        sys.stderr.write(msg + '\n')
        sys.exit(1)
        
class SettingsParser(OptionsParser):
    def __init__(self, raw_args, usage='[-param <value> ...] <settings profile>'):
        OptionsParser.__init__(self, raw_args, usage)
        self.settings = {}
        
        try:
            settings_container = __import__('settings', globals(), locals(), [self.args[0]], -1)
            settings_file = getattr(settings_container, self.args[0])
        except ImportError or AttributeError:
            self.error('Could not find settings file settings/%s.py' % self.args[0])
        except IndexError:
            self.error('Please specify a settings profile')
        
        for setting in settings_file.__dict__:
            if not setting.startswith('_'):
                self.settings[setting] = getattr(settings_file, setting)
        
        for opt in self.opts:
            self.settings[opt[0]] = opt[1]

    def get(self, setting, default=[None], type=unicode):
        if not setting in self.settings:
            if default == [None]:
                self.error('Missing required setting %s' % setting)
            else:
                return default
        else:
            try:
                return type(self.settings[setting])
            except ValueError:
                self.error('Setting %s could not be parsed' % setting)

def acquire_model(settings_parser):
    datastore = settings_parser.get('dstype')
    
    if datastore == 'mysql':
        host = settings_parser.get('dbhost', '127.0.0.1:3306')
        name = settings_parser.get('dbname', 'snowball')
        username = settings_parser.get('dbuser', 'root')
        
        if ('dbpass', None) in settings_parser.opts:
            password = getpass.getpass()
        else:
            password = settings_parser.get('dbpass', '')
            
        import model.mysql
        return model.mysql.db(host, name, username, password)
    else:
        settings_parser.error('Unknown datastore type: %s' % datastore)