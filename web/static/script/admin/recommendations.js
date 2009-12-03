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

function type() {
    return $('#return').val();
}

function toNodeURI() {
    return $('#toNodeURI').val();
}

function toSpecificNode() {
    return type() == 'to a specific node';
}

function getRecommendationsToNode() {
    if(toNodeURI() == '') return showError('please specify a to node');
    
    var success = function(json) {
        $('#recommendationsResults').html(json);
    }
    
    $.ajax({
        type: 'GET',
        url: '/recommendations/' + nodeValue() + '/' + toNodeURI(),
        dataType: 'json',
        data: 'format=json',
        
        success: success,
        error: failDialog
    });
}

function getAllRecommendations() {
    var success = function(json) {
        if(json.length == 0) {
            showInfo('no recommendations available for this node');
            return;
        }
        
        var ol = $('<ol>');
            
        for(var i=0; i<json.length; i++) {
            node = json[i][0];
            value = json[i][1];
            ol.append('<li>' + node + ': ' + value + '</li>')
        }
        
        $('#recommendationsResults').html(ol);
    };
    
    $.ajax({
        type: 'GET',
        url: '/recommendations/' + nodeValue(),
        dataType: 'json',
        data: 'format=json',
        
        success: success,
        error: failDialog
    });
}

function getRecommendations() {
    if(nodeValue() == '') return showError('please specify a node');
    
    if(toSpecificNode()) {
        getRecommendationsToNode();
    } else {
        getAllRecommendations();
    }
}

$(function() {
    $('#return').change(function() {
        if(toSpecificNode()) {
            $('#toNodeURIContainer').html('to URI: <input id="toNodeURI" type="text" />');
        } else {
            $('#toNodeURIContainer').empty();
        }
    });
});