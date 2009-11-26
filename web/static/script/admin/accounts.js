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

function getAccountURL() {
    return '/admin/controller/accounts/' + encodeURIComponent($('#name').attr('value'));
}

function createAccount() {
    var success = function(json) {
        dialog('huzzah!', 'account created', true);
    };
    
    $.ajax({
        type: 'PUT',
        url: getAccountURL(),
        dataType: 'json',
        data: {
            'format': 'json',
            'password': $('password').attr('value')
        },
        
        success: success,
        error: failDialog
    });
}

function deleteAccount() {
    var success = function(json) {
        dialog('huzzah!', 'account deleted', true);
    };
    
    $.ajax({
        type: 'DELETE',
        url: getAccountURL(),
        dataType: 'json',
        data: {
            'format': 'json',
            'password': $('password').attr('value')
        },
        
        success: success,
        error: failDialog
    });
}