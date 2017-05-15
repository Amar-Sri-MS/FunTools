//
//  ajax-1.js
//
//  Created by Charles Gray on 2017-05-15.
//  Copyright © 2017 Fungible. All rights reserved.
// 
//

var f1url = "http://localhost:9001/"

function json_loaded(result)
{
    // Called when the F1 JSON is loaded
    
    var elem = document.getElementById('ajax1-div');

    s = "<table border='1' cellpadding='2'>\n"
    s += "<tr><th>VP</th><th>WUs received</th><th>WUs sent</th></tr>\n"
    
    for (var i in result["config"]["all_vps"]) {
	v = result["config"]["all_vps"][i]
	s += "<tr><th>" + v + "</th>"
	stats = result["stats"]["per_vp"][v]
	var rx = "?";
	var tx = "?";
	
	if (stats != null) {
	    rx = stats["wus_received"]
	    tx = stats["wus_sent"]
	}

	s += "<td><center />" + rx + "</td><td><center />" + tx + "</td></tr>\n"
    }

    s += "</table>"
    
    elem.innerHTML = s;
    
}

// called when the document is ready to go
function ajax1_init() {

    console.log("init running");
    
    var elem = document.getElementById('ajax1-div');
    elem.innerHTML = "Attempting to locate F1 server...";

    jQuery.getJSON( f1url, "", json_loaded);

    console.log("init done");
}
