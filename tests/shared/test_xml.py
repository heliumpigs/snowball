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
    
def testcase(root, name, method, url, username, password, expected_python, **params):
    testcase = et.SubElement(root, 'testcase')
    
    et.SubElement(testcase, 'name').text = name
    et.SubElement(testcase, 'requestMethod').text = method
    et.SubElement(testcase, 'requestURL').text = url
    et.SubElement(testcase, 'headers')
    
    auth = et.SubElement(testcase, 'authentication')
    et.SubElement(auth, 'username').username = username
    et.SubElement(auth, 'password').password = password
    
    input_body = et.SubElement(testcase, 'inputbody')
    input_body.set('type', 'post')
    for param in params: et.SubElement(input_body, param).text = params[param]
    
    expected_output = et.SubElement(testcase, 'expectedOutput')
    expected_output.set('type', 'python')
    expected_output.text = expected_python
    
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