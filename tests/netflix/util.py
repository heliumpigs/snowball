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
import catnap.model, catnap.util, os, urllib

try:
    import cPickle as pickle
except:
    import pickle

MOVIE_TEMPLATE = 'netflix.com/movie/%s'
CUSTOMER_TEMPLATE = 'netflix.com/customer/%s'

def create_testcase(host, uri, *tags):
    name = 'Create node %s' % uri
    url = 'http://%s/nodes/%s' % (host, urllib.quote(uri, ''))
    input_tags = ' '.join(tags)
    
    code = catnap.util.detab_contents(u"""
        import simplejson
        json = simplejson.loads(contents)
        
        assert json['links'] == {}
        assert json['creation_date']
        assert json['owner'] == 'netflix.com'
        assert json['type'] == 'node'
        assert json['id'] == '%s'
        assert len(json['tags']) == %s""" % (uri, len(tags)))
    
    for tag in tags:
        code += u"\nassert '%s' in json['tags']" % tag
        
    request_body = catnap.model.RequestBody('post')
    request_body.value['tags'] = input_tags
    expected_body = catnap.model.ExpectedBody('python', code)
    
    return catnap.model.TestCase(name, 'PUT', url, headers={}, auth=('netflix.com', 'sandbox'),
                          body=request_body, expected_status=200, expected_body=expected_body)
    
def clean_host_arg(arg):
    """Sanitizes the input host argument"""
    
    if arg.startswith('http://'):
        arg = arg[7:]
    if arg.endswith('/'):
        arg = arg[:-1]
        
    return arg

def save_tests(tests, output_dir, filename):
    path = os.path.join(output_dir, filename)
    print 'Writing file ' + path
    
    with open(path, 'w') as file:
        pickle.dump(tests, file)
        
def save_tests_from_ratings_file(tests, output_dir, filename, suffix):
    without_ext = os.path.splitext(filename)[0]
    new_filename = '%s.%s.p' % (without_ext, suffix)
    save_tests(tests, output_dir, new_filename)