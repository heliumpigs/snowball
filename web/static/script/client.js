function getNodeURL() {
    return '/nodes/' + encodeURIComponent($('#nodeURI').attr('value'));
}

function getNode() {
    var success = function(json) {
        var linkHtml = "";
        var links = json['links'];
        
        for(var link in links) {
            linkMap = [
                'update date', links[link]['update_date'], false,
                'weight', links[link]['weight'], false,
                'tags', links[link]['tags'].join(', '), false
            ]
            
            linkHtml += "<h2>" + link + "</h2>";
            linkHtml += mapTable(linkMap);
        }
        
        var map = [
            'raw output', JSON.stringify(json), false,
            'id', json['id'], true,
            'owner', json['owner'], false,
            'tags', json['tags'].join(' '), true,
            'creation date', json['creation_date'], false,
            'update date', json['update_date'], false,
            'links', linkHtml, false
        ]
        
        $("#nodeResults").html(mapTable(map)).show();
    };

    $.ajax({
        type: 'GET',
        url: getNodeURL(),
        dataType: 'json',
        data: 'format=json',
        
        success: success,
        error: failDialog
    });
}

function updateNode() {
    var ok = function(dlg) {
        authDialog()
    };
    
    dialog('are you sure?', 'update the node will delete the links and alter the update date. continue?', ok, true);
}

function deleteNode() {
    var success = function() {
        
    };
    
    var ok = function(dlg) {
        $.ajax({
            type: 'DELETE',
            url: getNodeURL(),
            dataType: 'json',
            data: 'format=json',
            
            success: success,
            error: failDialog
        });
    }
}