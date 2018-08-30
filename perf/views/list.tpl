<!DOCTYPE html>
<html>
<head>
</head>
<body>
<a>List of runs:</a>
% for j in jobs:
  <p><a href="/{{j}}">{{j}}</a></p>
% end
</body>
</html>
