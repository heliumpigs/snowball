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

function getNodeURL(uri) {
    return '/nodes/' + encodeURIComponent(uri);
}

function displayLinks(json) {
    var linkDiv = $('<div>');
    
    for(var link in json) {
        var getLinkURL = function() {
            var from = encodeURIComponent($('#nodeResultsId').val());
            var to = encodeURIComponent(link);
            return '/links/' + from + '/' + to;
        };
        
        var updateLink = function() {
            var username = $('#nodeResultsOwner').text();
            var id = '#' + toIdentifier(link, false);
            
            params = {
                'weight': $(id + 'Weight').val(),
                'tags': $(id + 'Tags').val()
            }
            
            authRequest('PUT', getLinkURL(), username, 'link successfully updated', params);
        };
        
        var deleteLink = function() {
            var onDelete = function() {
                $('#' + toIdentifier(link, false)).remove();
            };
            
            var username = $('#nodeResultsOwner').text();
            authRequest('DELETE', getLinkURL(), username, 'link successfully deleted', null, onDelete);
        };
        
        linkMap = [
            'update date', json[link]['update_date'], false,
            'weight', json[link]['weight'], true,
            'tags', json[link]['tags'].join(' '), true
        ]
        
        linkDiv.append(mapTable(link, linkMap, updateLink, deleteLink));
    }
    
    return linkDiv;
}

function getNode() {
    if(nodeValue() == '') return showError('please specify a node');
    
    var success = function(json) {
        var map = [
            'raw output', JSON.stringify(json), false,
            'id', json['id'], true,
            'owner', json['owner'], false,
            'tags', json['tags'].join(' '), true,
            'creation date', json['creation_date'], false,
            'update date', json['update_date'], false,
            'links', displayLinks(json['links']), false
        ];
        
        $("#nodeResults").html(mapTable('node results', map, updateNode, deleteNode)).show();
        breadcrumbs('nodes', nodeValue());
    };

    $.ajax({
        type: 'GET',
        url: getNodeURL(nodeValue()),
        dataType: 'json',
        data: 'format=json',
        
        success: success,
        error: failDialog
    });
}

function updateNode() {
    var url = getNodeURL(nodeValue());
    var username = $('#nodeResultsOwner').text();
    var params = {
        'tags': $('nodeResultsTags').val()
    };
    
    authRequest('PUT', url, username, 'node successfully updated');
}

function deleteNode() {
    var url = getNodeURL(nodeValue());
    var username = $('#nodeResultsOwner').text();
    authRequest('DELETE', url, username, 'node successfully deleted');
}

$(function() {
    if(window.location.hash.length > 1) {
        $('#nodeURI').val(window.location.hash.substring(1));
        getNode();
    }
});