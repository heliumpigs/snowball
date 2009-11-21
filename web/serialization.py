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

from tornado import web
from datetime import datetime
import simplejson, types, model

try:
    import xml.etree.cElementTree as et
except:
    import xml.etree.ElementTree as et

COLLECTIONS = set, list, tuple
PRIMITIVES = str, unicode, int, float, bool, long
TOSTR = datetime,

class objdict(dict):
    """
    A stub class that serves as a flag that this dict was originally an object
    """
    pass

def _is_object(obj):
    """
    Returns True if obj
    1) inherits object
    2) is not a type descriptor
    3) is not a function
    """
    return isinstance(obj, object) and type(obj) is not types.TypeType and type(obj) is not types.FunctionType

def _flatten(obj):
    """
    Converts an arbtirary object into a dict so it can be properly handled by
    simplejson's serializer
    """
    obj_type = type(obj)
    
    if obj_type in PRIMITIVES:
        return obj
        
    elif obj_type in COLLECTIONS:
        #Convert all collections to lists
        return [_flatten(item) for item in obj]
        
    elif obj_type in TOSTR:
        #See if this object can be converted into a string
        return str(obj)
        
    elif isinstance(obj, dict):
        if isinstance(obj, model.Storage):
            new_dict = objdict()
        else:
            new_dict = {}
                    
        for key in obj:
            #Ignore 'private' keys that start with an underscore
            if key.startswith('_'): continue
            new_dict[key] = _flatten(obj[key])
        
        return new_dict
        
    elif _is_object(obj):
        new_obj = objdict()
        
        for key in dir(obj):
            #Ignore 'private' attributes that start with an underscore
            if key.startswith('_'): continue
            
            #Do not add functions to the filtered dict
            value = getattr(obj, key)
            if type(value) is types.FunctionType: continue
            
            new_obj[key] = _flatten(value)
            
        return new_obj

def serialize(request, obj, finish=True):
    """
    Serializes an arbitrary object and writes the results to the connection. The
    connection is closed if finish = True.
    """
    default_format = request.application.settings.get('default_format', 'json')
    
    #Get the format if it was explicitly specified by the client
    format = request.get_argument('format', None)
    if format == None: format = default_format
    
    #Get the serializer method for the format
    serializer = SERIALIZERS.get(format, None)
    if serializer == None: serializer = SERIALIZERS[default_format]
    
    #If it's an error, change the object to fit a standard error message schema
    if isinstance(obj, web.HTTPError):
        error = {
            'type': 'error',
            'code': obj.status_code,
        }
        
        if obj.log_message != None and obj.log_message != '':
            error['message'] = obj.log_message
            
        request.set_status(obj.status_code)
        obj = error

    result = serializer(request, obj)
    request.set_header('Content-Type', result[0])
    request.write(result[1])
    
    if finish: request.finish()
    
def _to_xml(request, obj):
    """Serializes an arbitrary object into xml"""
    
    root = et.Element(obj.__class__.__name__)
    _to_xml_item(root, _flatten(obj))
    return ('application/xml', et.tostring(root, encoding='utf-8'))
    
def _to_xml_item(root, obj):
    """Recurses through an object's attributes, converting them into xml"""
    
    if isinstance(obj, objdict):
        #Type and id attributes are special; handle them as such
        if 'type' in obj: root.tag = obj['type']
        if 'id' in obj: root.set('id', obj['id'])
        
        for key in obj:
            if key != 'id' and key != 'type':
                _to_xml_item(et.SubElement(root, key), obj[key])
    
    elif isinstance(obj, dict):
        for key in obj:
            elem = et.SubElement(root, 'item')
            elem.set('id', key)
            _to_xml_item(elem, obj[key])
                
    elif isinstance(obj, list):
        for item in obj:
            _to_xml_item(et.SubElement(root, 'item'), item)
            
    else:
        root.text = str(obj)
        
    return root

def _to_json(request, obj):
    """Serializes an arbitrary object into json"""
    
    json = simplejson.dumps(_flatten(obj))
    callback = request.get_argument('callback', None)
    
    if callback is not None:
        json = callback + '(' + json + ')'
    
    #TODO: application/json content type
    return ('text/javascript', json)

#Mapping of formats to their serialization methods
SERIALIZERS = {
    'json': _to_json,
    'xml': _to_xml,
}