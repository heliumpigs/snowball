/*
  Copyright 2009 Yusuf Simonson
  This file is part of Snowball.
  
  Snowball is free software: you can redistribute it and/or modify it under the
  terms of the GNU Affero General Public License as published by the Free
  Software Foundation, either version 3 of the License, or (at your option) any
  later version.

  Snowball is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
  A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
  details.

  You should have received a copy of the GNU Affero General Public License
  along with Snowball.  If not, see <http://www.gnu.org/licenses/>.
*/

function nodeValue() {
    return $('#nodeURI').val();
}

function authRequest(method, url, username, message, params, callback) {
    if(params == null || params == undefined) {
        params = {};
        params['format'] = 'json';
    }
    
    var onAuth = function(dlg) {
        var success = function() {
            showInfo(message);
            
            if(typeof callback == 'function') {
                callback();
            }
        };
        
        $.ajax({
            type: method,
            url: url,
            dataType: 'json',
            data: params,
            username: $('#loginUsername').val(),
            password: $('#loginPassword').val(),
            
            success: success,
            error: failDialog
        });
    };
    
    authDialog(username, onAuth);
}