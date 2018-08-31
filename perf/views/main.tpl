<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="/static/style.css">
</head>
<body>
	<table class="main">
	<tr><td><a href="{{opt.path}}/samples">Show WU perf samples</a></td></tr>
	<tr><td><a href="{{opt.path}}/frames">Show WU frames</a></td></tr>
	<tr><td><a href="{{opt.path}}/wu_list">Show WU list</a></td></tr>
	<tr><td><a href="{{opt.path}}/util">Show per vp utilization (EXPERIMENTAL)</a></td></tr>
% if debug_build:
	<tr><td><a class="warning">This job appears to be a debug build which is not a good candidate for perf testing</a></td></tr>
% end
	</table>
</body>
</html>
