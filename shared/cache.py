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

class Node(object):
    __slots__ = ['prev', 'next', 'me']
    def __init__(self, prev, me):
        self.prev = prev
        self.me = me
        self.next = None

class LRU:
    """
    Implementation of a length-limited O(1) LRU queue.
    Built for and used by PyPE:
    http://pype.sourceforge.net
    Copyright 2003 Josiah Carlson.
    """
    def __init__(self, count, pairs=[]):
        self.count = max(count, 1)
        self.d = {}
        self.first = None
        self.last = None
        for key, value in pairs:
            self[key] = value
            
    def __contains__(self, obj):
        return obj in self.d
    
    def __getitem__(self, obj):
        a = self.d[obj].me
        self[a[0]] = a[1]
        return a[1]
    
    def __setitem__(self, obj, val):
        if obj in self.d:
            del self[obj]
        nobj = Node(self.last, (obj, val))
        
        if self.first is None:
            self.first = nobj
        
        if self.last:
            self.last.next = nobj
        
        self.last = nobj
        self.d[obj] = nobj
        
        if len(self.d) > self.count:
            if self.first == self.last:
                self.first = None
                self.last = None
                return
        
            a = self.first
            a.next.prev = None
            self.first = a.next
            a.next = None
        
            del self.d[a.me[0]]
            del a
    
    def __delitem__(self, obj):
        nobj = self.d[obj]
    
        if nobj.prev:
            nobj.prev.next = nobj.next
        else:
            self.first = nobj.next
    
        if nobj.next:
            nobj.next.prev = nobj.prev
        else:
            self.last = nobj.prev
    
        del self.d[obj]
    
    def __iter__(self):
        cur = self.first
    
        while cur != None:
            cur2 = cur.next
            yield cur.me[1]
            cur = cur2
    
    def iteritems(self):
        cur = self.first
    
        while cur != None:
            cur2 = cur.next
            yield cur.me
            cur = cur2
    
    def iterkeys(self):
        return iter(self.d)
    
    def itervalues(self):
        for i,j in self.iteritems():
            yield j
    
    def keys(self):
        return self.d.keys()
        
class NodeStore(LRU):
    def __init__(self, db, count):
        self.db = db
        LRU.__init__(self, count)
    
    def __getitem__(self, obj):
        #Try to get the item from the cache first
        if obj in self: return LRU.__getitem__(self, obj)
        
        #Pull the item from the database otherwise
        value = self.db[obj]
        self[obj] = value
        return value