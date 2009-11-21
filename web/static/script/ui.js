curTab = null;

function tab(id) {
    $('#' + curTab).fadeOut(100, function() {
        $('#' + id).fadeIn(100);
    });
    
    curTab = id;
    breadcrumbs(curTab);
    window.location.hash = '#' + curTab;
}

function breadcrumbs() {
    var text = '';
    
    for(var i=0; i<arguments.length; i++) {
        text += ' \u00BB ' + arguments[i];
    }
    
    $('#subheader').text(text);
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
        button['cancel'] = function() {
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

    dialog('error', 'request failed<br />reason: ' + message);
}

function authDialog(username, callback) {
    disabled = '';
    if(!username) {
        username = '';
        disabled = "disabled='disabled'";
    }
    
    html = "this action requires authentication<br />"
         + "username: <input id='loginUsername' type='text' value='" + username + "' " + disabled + " /><br />"
         + "password: <input id='loginPassword' type='text' />";
         
    dialog('login', html, callback, true);
}

function mapTable(map, updateFunc, deleteFunc) {
    table = "<table><tr><th class='attrHeader'>attribute</th><th class='attrValue'>value</th></tr>";
        
    for(var i=0; i<map.length; i+=3) {
        var cssClass = '';
        if(i % 2 == 1) cssClass = 'zebra';
        
        table += "<tr class='" + cssClass + "'><td>" + map[i] + "</td>";
        
        if(map[i + 2] == true) {
            table += "<td><input id='" + map[i] + "Value' type='text' value='" + map[i + 1] + "' /></td>";
        } else {
            table += "<td>" + map[i + 1] + "</td>";
        }
        
        table += "</tr>";
    }
    
    table += "</table>";
    
    if(updateFunc) {
        table += "<input type='button' value='update' class='button' onclick='" + updateFunc + "()' />"
    }
    
    if(deleteFunc) {
        table += "<input type='button' value='delete' class='button' onclick='" + deleteFunc + "()' />"
    }
    
    return table;
}

$(function() {
    curTab = $('.tab:first').attr('id');
    if(window.location.hash.length > 1) {
        tab(window.location.hash.substring(1));
    } else {
        $('#' + curTab).fadeIn(100);
    }
});