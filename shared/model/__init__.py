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

import hashlib, os

import sys
sys.path.append('../../lib/Scarecrow')

SALT = '4815162342>'

#Taken from web.py <http://webpy.org/>
class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.
    
        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
    
    """
    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __repr__(self):     
        return '<Storage ' + dict.__repr__(self) + '>'

class Entity(Storage):
    def __init__(self, id, type):
        self.id = id
        self.type = type

def create_user(db, name, password):
    account = Entity(name, 'account')
    account.password_hash = account_pass(password)
    db[account_key(name)] = account
    
def auth_user(db, name, password):
    account = db[account_key(name)]
    
    if not account: return False
    return account['password_hash'] == account_pass(password)
    
def key(value):
    return hashlib.md5(value).digest()
    
def node_key(uri):
    return key('node:' + uri)
    
def rec_key(uri):
    return key('rec:' + uri)

def account_key(name):
    return key('account:' + name)
    
def account_pass(pw):
    return key(SALT + pw)
