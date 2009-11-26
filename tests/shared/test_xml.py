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

try:
    import xml.etree.cElementTree as et
except:
    import xml.etree.ElementTree as et
    
def test():
    return et.Element('test')
    
def testcase(root, name, method, url, status=200, auth_creds=None, expected_python=None, **params):
    testcase = et.SubElement(root, 'testcase')
    testcase.set('name', name)
    
    request = et.SubElement(testcase, 'request')
    request.set('method', method)
    request.set('url', url)
    
    if auth_creds:
        auth = et.SubElement(request, 'auth')
        auth.set('username', auth_creds[0])
        auth.set('password', auth_creds[1])
        
    if len(params) > 0:
        body = et.SubElement(request, 'body')
        body.set('type', 'post')
        
        for key in params:
            param = et.SubElement(body, 'param')
            param.set('name', key)
            param.text = str(params[key])
            
    et.SubElement(testcase, 'status').text = str(status)
    
    contents = et.SubElement(testcase, 'contents')
    contents.set('type', 'python')
    contents.text = expected_python
    
    return testcase

def clean_code(code):
    lines = code.splitlines()
    if len(lines) < 2: return code
    
    sample = lines[1]
    diff = len(sample.lstrip()) - len(sample)
    
    formatted_code = lines[0] + '\n'
    for i in range(1, len(lines)):
        formatted_code += lines[diff:] + '\n'
        
    return formatted_code