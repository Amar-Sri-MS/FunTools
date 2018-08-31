<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="/static/style.css">
</head>
<body>
<table>
<thead>
% for i,c in enumerate(rows[0]):
<th nowrap>{{c}}
	% if opt.sort_by == i:
		% if not opt.sort_invert:
<a class="sort" href="{{opt.path}}?{{opt.replace_query(sort_by=i, sort_invert=1)}}">&darr;</a>
		% else:
<a class="sort" href="{{opt.path}}?{{opt.replace_query(sort_by=i, sort_invert=None)}}">&uarr;</a>
		% end
	% else:
<a class="sort" href="{{opt.path}}?{{opt.replace_query(sort_by=i, sort_invert=None)}}">&#x2195;</a>
	% end
</th>
% end
</thead>
<tbody>
% assert rows[0][0] == "vp"
% assert rows[0][1] == "time_bucket"
% assert rows[0][2] == "utilization"
% for row in rows[1:]:
<tr>
	% for i,c in enumerate(row):
		% if i == 0 and opt.vp is None:
<td><a href="/{{opt.job_id}}/util/{{c}}">{{c}}</a></td>
		% else:
<td>{{c}}</td>
		% end
	% end
</tr>
% end
</tbody>
</table>
</body>
</html>
