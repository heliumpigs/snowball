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

function getLinksURL(uri) {
    return '/links/' + encodeURIComponent(uri);
}

function getDirection() {
    return $('#direction').val();
}

function getLinks() {
    if(nodeValue() == '') return showError('please specify a node');

    var success = function(json) {
        var linkDiv = $('<div>');
        
        for(link in json) {
            linkMap = [
                'update date', json[link]['update_date'], false,
                'weight', json[link]['weight'], false,
                'tags', json[link]['tags'].join(' '), false
            ]
            
            linkDiv.append(mapTable(link, linkMap));
            breadcrumbs('links', nodeValue(), getDirection() + ',' + nodeValue());
        }
        
        $('#linksResults').html(linkDiv);
    };

    $.ajax({
        type: 'GET',
        url: getLinksURL(nodeValue()),
        dataType: 'json',
        data: {
            'format': 'json',
            'direction': getDirection()
        },
        
        success: success,
        error: failDialog
    });
}

$(function() {
    if(window.location.hash.length > 1) {
        var parts = window.location.hash.substring(1).split(',', 2);
        if(parts.length != 2) return;
        
        $('#direction').val(parts[0]);
        $('#nodeURI').val(parts[1]);
        getLinks();
    }
});