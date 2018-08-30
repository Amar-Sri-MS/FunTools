<!DOCTYPE html>
<html>
<head>
{{ !style }}
</head>
<body>

<font face="helvetica">
<h1>wuprof results</h1>

<p>Processed {{ len(benches) }} soak_bench runs from input files</p>

% for bench in benches:

  <h2>{{bench.name}}</h2>
  <p>timestamp {{bench.t0}} -> {{bench.t1}}</p>
  <p>{{bench.perf_line}}</p>
  
  % for wus in bench.wslist:

    <h3>WU stats sorted by {{ wus.sort }}</h3>

    <table>
    <thead>
      % for hdr in wus.hdrs:
	<th>{{ hdr }}</th>
      %  end
      </thead>
      <tbody>
    % for row in wus.rows:
      <tr>
      % for data in row:
	<td>{{ data }}</td>
      %  end
      </tr>
    % end
    </tbody>
    </table>
  % end

  % for wuname in bench.itraces.keys():

    <h3> Instruction traces for WU {{ wuname }} </h3>

    <table>
    <thead>
      <th>tag</th>
      <th>ccv</th>
      <th>ts delta</th>
      <th>perf0 (instrs)</th>
      <th>perf1</th>
      <th>perf2</th>
      <th>perf3</th>
      <th>trace reference</th>
    </thead>
    <tbody>
    % for itrace in bench.itraces[wuname]:
      <tr>
      % for data in itrace.row:
	<td>{{ data }}</td>
      %  end
      </tr>
    % end
    <tr>
    </tr>
    </tbody>
    </table>

    <br />

    <table>
    <thead>
    % for itrace in bench.itraces[wuname]:
      <th>
      {{ itrace.name }}
      </th>
    % end    
    </thead>
    <tbody>
    <tr>
      % for itrace in bench.itraces[wuname]:
      <td style="text-align:left">
      <pre>
{{ itrace.mk_func_histogram() }}
      </pre>
      </td>
      % end
    </tr>
    <tr>
    </tr>
    <tr>
      % for itrace in bench.itraces[wuname]:
      <td style="text-align:left">
      <pre>
{{ itrace.mk_inst_dump() }}
      </pre>
      </td>
      % end
    </tr>
    </tbody>
    </table>


  % end
  
% end
</font>
</body>
</html>
