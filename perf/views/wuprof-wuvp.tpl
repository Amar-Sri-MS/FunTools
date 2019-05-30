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
   <p>{{ len(bench.vps.keys()) }} VP(s) found</p>

   <center>
   <div>
   <font size="+2">
   <pre>
VP Utilisation:
   % for cluster in range(9):
{{ cluster }}: \\
     % for core in range(6):
       % for vp in range(4):
	 % vvp = bench.vps.get("%d.%d.%d" % (cluster, core, vp))
	 % if vvp is None:
 \\
	 % end
	 % if vvp is not None:
	   % util = int(10 * vvp.util)
	   % if vvp in bench.sorted_vps:
<a href="#{{vvp.href}}">\\
	   % end
{{ vvp.util_char() }}\\
	   % if vvp in bench.sorted_vps:
</a>\\
	   % end
	 % end
       % end
       % if core < 5:
-\\
       % end
     % end
     
   % end
   </pre>
   </font>
   </div>
   </center>

   <center>
	{{ !bench.histogram }}
   </center>

   <h3>Global WU stats</h3>
     <font size="-1">
     <table>
      <thead>
      % for hdr in bench.global_headers:
      	 <th>{{ hdr }}</th>
      % end
      </thead>
      <tbody>
      % for wu in bench.global_wus:
      	 <tr>
	 % for field in wu.get_data_row():
	    <td>{{ field }}</td>
	 % end
      	 </tr>
       % end
    </tbody>
    </table>
    </font>


   <h3>Top {{ opts.nvps }} VP(s) sorted by {{opts.sort_vp}}</h3>

   % for i in range(len(bench.sorted_vps)):
      % vp = bench.sorted_vps[i]
      <div
      % if i % 2:
         style="background-color:#f8f8f8"
      % end
      >
      <h4><a name="{{vp.href}}">{{ i }}) VP {{ vp.ccv }}</a></h4>
      <p>WU utilisation: {{ pp.pct(vp.util) }}%</p>
      <p>Idle time: {{ pp.pct(vp.idleutil) }}%<p>
      <p>utilisation gap: {{ pp.pct(1.0 - vp.wuutil - vp.idleutil) }}</p>
      <p>non-idle WUs: {{ vp.wucount }}</p>
      <p>Showing top {{ opts.nwus }} WU(s)</p>
      <font size="-1">
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
    </font>
    </div>
    <p />
   % end

   <h3>UART log</h3>
   <div style="width=80%;max-height:500px;overflow:auto;background-color:#f8f8f8">
   <pre>
{{ opts.uart_log }}
   </pre>
   </div>
% end

