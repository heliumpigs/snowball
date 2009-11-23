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
import re, iso8601, ConfigParser, urllib, model, scarecrow
from datetime import datetime

from tornado import web
from web.serialization import *
from oz.handler import *

REALM = 'Snowball'

def auth(req, realm, name, password):
    """Authenticates the given credentials"""
    if realm != REALM:
        return False
        
    db = req.application.settings['db']
    return model.auth_account(db, name, password)

def assert_string(name, value, max_length):
    """
    Ensures the input value is a string whose length is less than or equal to
    max_length
    """
    assert isinstance(value, str) or isinstance(value, unicode), "%s must be a string" % name
    assert len(value) <= max_length, "%s cannot exceed %s characters" % (name, max_length)
    
tag_pattern = re.compile('[A-Za-z0-9_-]+')
def check_tags(tag_arg):
    """
    Ensures a given argument is a valid list of tags and parses it into a set of
    tags
    """
    
    if tag_arg == None:
        return None
    
    tags = tag_arg.split()
    
    for tag in tags:
        assert_string('tag item', tag, 64)
        
        match = tag_pattern.match(tag)
        assert match != None, 'tag can only contain letters, numbers, underscores and dashes'
        assert len(match.group(0)) == len(tag), 'tag can only contain letters, numbers, underscores and dashes'
        
    return set(tags)
    
def check_datetime(datetime_arg):
    """
    Ensures a given argument is a valid datetime and parses it into a datetime
    object
    """
    
    if datetime_arg == None:
        return None
    
    try:
        return iso8601.parse_date(datetime_arg)
    except:
        assert False, 'could not parse date'
        
def assert_direction(direction):
    """Ensures that a given argument is a valid direction"""
    assert direction == 'from' or direction == 'to', "direction must be either 'from' or 'to'"
    
def check_weight(weight):
    """Ensures that a given argument is a valid weight, i.e. a float >= -1 and <= 1"""
    try:
        if weight == None:
            return weight
        
        try:
            weight = float(weight)
        except ValueError:
            assert False, 'weight must be a float'
        
        assert weight >= -1.0 and weight <= 1.0, 'weight must be between -1 and 1'
        return weight
    except TypeError, e:
        assert False, 'weight must be a valid float'

def error_handler(func):
    """
    Handles certain classes of errors to return proper HTTP codes
    """
    def func_replacement(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except AssertionError, e:
            serialize(self, web.HTTPError(400, e.message))
        except web.HTTPError, e:
            serialize(self, e)
    
    return func_replacement

def get_dynamic_setting(db, name):
    """
    Gets a setting that can be altered dynamically by Snowball (i.e. a non-user
    defined setting)
    """
    try:
        settings = db[model.settings_key()]
        return settings[name]
    except KeyError:
        return None

def save_dynamic_setting(db, name, value):
    """Sets a dynamic setting (i.e. a non-user defined setting)"""
    settings_ident = scarecrow.ident(model.settings_key())
    
    try:
        settings = db[settings_ident]
    except KeyError:
        settings = model.Storage()
    
    settings[name] = value
    db[settings_ident] = settings
    
class SnowballHandler(OzHandler):
    """"
    A subclass of the Tornado request handler that mixes in Oz functionality and
    simplifies access to the database connection
    """
    def __init__(self, *args, **kwargs):
        OzHandler.__init__(self, *args, **kwargs)
        self.db = self.application.settings['db']