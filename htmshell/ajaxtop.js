//
//  ajaxtop.js
//
//  Created by Charles Gray on 2017-05-15.
//  Copyright © 2017 Fungible. All rights reserved.
// 
//

var f1url = "http://localhost:9001/"

var prev_stats = null;
var latest_stats = null;
var sortidx = 0;
var sortneg = 1;

function compute_deltas(t0, t1)
{
    deltas = []

    t0 = t0["stats"]["wus"]
    t1 = t1["stats"]["wus"]
    
    for (k in t1["counts"]) {
	count = "?"
	duration = "?"

	if (k in t0["counts"]) {
	    count = t1["counts"][k] - t0["counts"][k]
	    duration = t1["durations"][k] - t0["durations"][k]
	}
    
	deltas.push([k, count, duration])
    }

    return deltas
}

function ecompare(a, b)
{
    if (sortneg) {
	d = b[sortidx] - a[sortidx];
    } else {
	d = a[sortidx] - b[sortidx];
    }
    
    return d;
    
}

function setsort(a)
{
    console.log("setsort " + a)
    
    if (sortidx == a)
	sortneg = !sortneg;

    sortidx = a;

    // force a redraw
    draw_results()
}

function noinfo()
{
    var elem = document.getElementById('wuinfo-div');
    elem.innerHTML = "";
}

function showinfo(w)
{
    console.log(w)

    h = latest_stats["config"]["wu_handlers"][w]

    a = h["attrs"]
    if (a == null) {
	a = 0
    }
    comma = ""
    
    s = "<b> Info for WU " + w + "</b>"
    s += "<p />\n"
    s += "WU ID: " + h["id"]
    s += "<p />\n"
    s += "Attributes: "

    if (a == 0) {
	s += "<i>none</i>"
    }

    if (a & 1) {
	s += comma + "Root WU"
	comma = ", "
    }

    if (a & 2) {
	s += comma + "Thread WU"
	comma = ", "
    }

    if (a & 4) {
	s += comma + "wustack ABI"
	comma = ", "
    }

    if (a & 8) {
	s += comma + "Flow Control ABI"
	comma = ", "
    }

    if (a & 16) {
	s += comma + "Top-level Shell Command"
	comma = ", "
    }

    s += "<br /><br />"
    var elem = document.getElementById('wuinfo-div');
    elem.innerHTML = s;
}

function draw_results()
{
    // compute the deltas
    ds = compute_deltas(prev_stats, latest_stats)

    // sort it
    ds.sort(ecompare)
    
    // draw it
    s = "<table border='1' cellpadding='2'>\n"
    s += "<tr><th onclick='setsort(0)'>WU</th>"
    s += "<th onclick='setsort(1)'>count</th>"
    s += "<th onclick='setsort(2)'>duration</th></tr>\n"

    for (i in ds) {
	d = ds[i]
	click_func = "showinfo(\"" + d[0] + "\")"
	console.log(click_func)
	s += "<tr><td onclick='" + click_func + "')><center />" + d[0] + "</td>"
	s += "<td><center />" + d[1] + "</td>"
	s += "<td><center />" + d[2] + "</td></tr>\n"
    }
    
    s += "</table>"
    
    var elem = document.getElementById('ajaxtop-div');
    elem.innerHTML = s;  
}

function json_loaded(result)
{
    // Called when the F1 JSON is loaded
    console.log("got a json");

    // shuffle the arrays
    prev_stats = latest_stats;
    latest_stats = result;

    // poke a timer for the next one
    setTimeout("request_json()", 2000);

    // early out if there's no data
    if (prev_stats == null) {
	return;
    }
    
    // draw the current stats
    draw_results()

    console.log("timer set");
}

function request_json()
{
    jQuery.getJSON( f1url, "", json_loaded);
}

// called when the document is ready to go
function ajaxtop_init()
{
    console.log("init running");
    
    var elem = document.getElementById('ajaxtop-div');
    elem.innerHTML = "Attempting to locate F1 server...";

    // start the ball rolling
    request_json();
    
    console.log("init done");
}
