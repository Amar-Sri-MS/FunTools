<!DOCTYPE html>
<html>
<head>
{{ !style }}
</head>
<body>

<font face="helvetica">
<h1>wuprof wuvp results</h1>

<p>Processed {{ len(benches) }} benchmark(s) from input files</p>

Parameters<br />
first wu: {{ opts.first_wu }} <br />
last wu: {{ opts.last_wu }} <br />
start-time: {{ pp.time(opts.start_time_orig) }} <br />
end-time: {{ pp.time(opts.end_time_orig) }} <br />
<br />
vp sort: {{ opts.sort_vp }} <br />
wu sort: {{ opts.sort_wu }} <br />

Sample trim histogram:

{{ !histograms["trim"] }}

% for bench in benches:

   <h2>Benchmark {{ pp.time(bench.t0) }} -> {{ pp.time(bench.tN) }}</h2>
   <p>duration: {{ pp.time(bench.tN  - bench.t0) }}</p>
   <p>non-idle WUs: {{bench.wucount}}</p>
   <p>{{ len(bench.vps.keys()) }} VP(s) found:</p>

   <table>
     <tr>
	<th></th>
	% for core in range(6):
       	  % for vp in range(4):
	    <th>{{core}}.{{vp}}</th>
	  % end
	  % if core < 5:
            <td></td>
       	  % end
	% end
     </tr>
   % for cluster in range(9):
     <tr> <th> {{ cluster }} </th>
     % for core in range(6):
       % for vp in range(4):
       	 <td>
	 % vvp = bench.vps.get("%d.%d.%d" % (cluster, core, vp))
	 % if vvp is not None:
	 {{ int(10 * vvp.util) }}
	 % end
	 </td>
       % end
       % if core < 5:
         <td></td>
       % end
     % end
     </tr>
   % end
   </table>

   <center>
	{{ !bench.histogram }}
   </center>
   <h3>Top {{ opts.nvps }} VP(s) sorted by {{opts.sort_vp}}</h3>

   % for i in range(len(bench.sorted_vps)):
      % vp = bench.sorted_vps[i]
      <div
      % if i % 2:
         style="background-color:#f8f8f8"
      % end
      >
      <h4>{{ i }}) VP {{ vp.ccv }}</h4>
      <p>WU utilisation: {{ pp.pct(vp.util) }}%</p>
      <p>Idle time %: {{ pp.pct(vp.idleutil) }}<p>
      <p>utilisation error: {{ pp.pct(1.0 - vp.util - vp.idleutil) }}</p>
      <p>non-idle WUs: {{ vp.wucount }}</p>
      <p>Showing top {{ opts.nwus }} WU(s)</p>
      <table>
      <thead>
      % for hdr in bench.headers:
      	 <th>{{ hdr }}</th>
      % end
      </thead>
      <tbody>
      % for wu in vp.sorted_wus:
      	 <tr>
	 % for field in wu.get_data_row():
	    <td>{{ field }}</td>
	 % end
      	 </tr>
       % end
    </tbody>
    </table>
    </div>
    <p />
   % end

% end

