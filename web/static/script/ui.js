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

var timeoutId = null;
var curTab = null;

function tab(name) {
    if(curTab) {
        $('#' + curTab).fadeOut(100, function() {
            $('#' + name).fadeIn(100);
        });
    } else {
        $('#' + name).fadeIn(100);
    }
    
    curTab = name;
}

function showPanel(name, message) {
    if(timeoutId) clearTimeout(timeoutId);
    $('#' + name + 'Message').text(message);
    $('#' + name + 'Panel').fadeIn();
    timeoutId = setTimeout("$('#" + name + "Panel').fadeOut(); timeoutId = null;", 4000);
}

function showInfo(message) {
    showPanel('info', message);
}

function showError(message) {
    showPanel('error', message);
}

function breadcrumbs(root, name, hash) {
    if(hash == undefined || hash == null) hash = name;
    window.location.hash = '#' + hash;
    $('#subheader').html(' \u00BB <a href="/admin/' + root + "#" + hash + '">' + name + '</a>');
}

function dialog(title, contents, ok, cancel) {
    buttons = {
        'ok': function() {
            if(typeof ok == 'function') ok($(this));
            $(this).dialog('close');
            $('#dialog').remove();
        }
    };
    
    if(cancel) {
        buttons['cancel'] = function() {
            $(this).dialog('close');
            $('#dialog').remove();
        }
    }

    $("<div id='dialog'>" + contents + "</div>").dialog({
        buttons: buttons,
        modal: true,
        title: title,
        resizable: false
    });
}

function failDialog(res, status, errorThrown) {
    if(status == 'timeout') {
        var message = 'could not contact server';
    } else if(status == 'error') {
        try {
            var json = JSON.parse(res.responseText);
            var message = json['message'];
        } catch(ex) {}
        
        if(!message) {
            var message = 'HTTP error code ' + res.status;
        }
    } else if(status == 'notmodified') {
        var message = 'not modified error';
    } else if(status == 'parsererror') {
        var message = 'could not parse response';
    } else {
        var message = 'unknown';
    }

    dialog('error', '<p>request failed<br />reason: ' + message + '</p><p>response:<br />' + res.responseText + '</p>');
}

function authDialog(username, callback) {
    disabled = '';
    if(!username) {
        username = '';
        disabled = "disabled='disabled'";
    }
    
    html = "this action requires authentication<br />"
         + "username: <input id='loginUsername' type='text' value='" + username + "' " + disabled + " /><br />"
         + "password: <input id='loginPassword' type='password' />";
         
    dialog('login', html, callback, true);
}

function toIdentifier(name, ucc) {
    var toUCC = function(value) {
        return value.substring(0, 1).toUpperCase() + value.substring(1);
    };
    
    var parts = name.split(' ');
    if(ucc) {
        var id = toUCC(parts[0]);
    } else {
        var id = parts[0];
    }
    
    for(var i=1; i<parts.length; i++) {
        id += toUCC(parts[i]);
    }
    
    return id;
}

function mapTable(name, map, updateFunc, deleteFunc) {
    var getId = function(fieldName) {
        return toIdentifier(name, false) + toIdentifier(fieldName, true);
    };
    
    var appendButton = function(value, func) {
        button = $("<input type='button' value='" + value + "' class='button' />");
        button.click(func);
        div.append(button);
    };

    div = $('<div>');
    div.attr('id', name);
    div.append('<h2>' + name + '</h2>')
    
    table = $('<table>');
    div.append(table);
    table.append("<tr><th class='attrHeader'>attribute</th><th class='attrValue'>value</th></tr>");
    
    for(var i=0; i<map.length; i+=3) {
        row = $('<tr>');
        table.append(row);
        if(i % 2 == 1) row.attr('class', 'zebra');
        
        row.append("<td>" + map[i] + "</td>");
        
        td = $('<td>');
        row.append(td);
        
        if(map[i + 2] == true) {
            input = $('<input>');
            td.append(input);
            
            input.attr('id', getId(map[i]));
            input.attr('value', map[i + 1]);
        } else {
            td.attr('id', getId(map[i]));
            td.html(map[i + 1]);
        }
    }
    
    if(updateFunc) {
        appendButton('update', updateFunc);
    }
    
    if(deleteFunc) {
        appendButton('delete', deleteFunc);
    }
    
    return div;
}