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
% assert rows[0][1] == "vp"
% assert rows[0][2] == "wu"
% assert rows[0][8] == "arg0"
% for row in rows[1+opt.from_row:1+opt.from_row+opt.show_max]:
<tr>
	% for i,c in enumerate(row):
		% if i == 1 and opt.vp is None:
<td><a href="/{{opt.job_id}}/vp/{{c}}">{{c}}</a></td>
		% elif i == 2 and not opt.wu:
<td><a href="/{{opt.job_id}}/samples/{{c}}">{{c}}</a></td>
		% elif i == 8:
			% xc = "%x" % c
			% if not opt.frame and opt.is_wustack(c):
<td><a href="/{{opt.job_id}}/frames/{{xc}}">{{xc}}</a></td>
			% else:
<td>{{xc}}</td>
			% end
		% else:
<td>{{c}}</td>
		% end
	% end
</tr>
% end
</tbody>
</table>
% if len(rows) > opt.show_max:
<div class="pager">
  <div class="prev">
	% if opt.from_row > 0:
	<a href="{{opt.path}}?{{opt.replace_query(from_row=max(0, opt.from_row-opt.show_max))}}">Previous {{opt.show_max}}</a>
	% else:
	<span>Previous {{opt.show_max}}</span>
	% end
  </div>
  <div class="next">
	% if opt.from_row + opt.show_max < len(rows) - 1:
	<a href="{{opt.path}}?{{opt.replace_query(from_row=opt.from_row+opt.show_max)}}">Next {{opt.show_max}}</a>
	% else:
	<span">Next {{opt.show_max}}</span>
	% end
  </div>
  <div class="all">
    <a href="{{opt.path}}?{{opt.replace_query(from_row=None, show_max=-1)}}">Show All</a>
  </div>
  <div>{{len(rows)-opt.show_max}} rows not shown.</div>
</div>
% end
</body>
</html>
