<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="/static/style.css">
</head>
<body>
<table>
<thead>
% assert len(rows[0]) == 2 and rows[0][0] == "count" and rows[0][1] == "wu"
% for i,c in enumerate(rows[0]):
<th>{{c}}
	% cls = "sort wu" if i == 1 else "sort"
	% if opt.sort_by == i:
		% if not opt.sort_invert:
<a class="{{cls}}" href="{{opt.path}}?{{opt.replace_query(sort_by=i, sort_invert=1)}}">&darr;</a>
		% else:
<a class="{{cls}}" href="{{opt.path}}?{{opt.replace_query(sort_by=i, sort_invert=None)}}">&uarr;</a>
		% end
	% else:
<a class="{{cls}}" href="{{opt.path}}?{{opt.replace_query(sort_by=i, sort_invert=None)}}">&#x2195;</a>
	% end
</th>
% end
</thead>
<tbody>
% for row in rows[1:]:
<tr>
<td>{{row[0]}}</td>
<td class="wu"><a href="/{{opt.job_id}}/samples/{{row[1]}}">{{row[1]}}</a></td>
</tr>
% end
</tbody>
</table>
</body>
</html>
