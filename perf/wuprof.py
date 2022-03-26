#!/usr/bin/env python3
import io
import os
import re
import cgi
import sys
import math
import urllib.request, urllib.error, urllib.parse
import optparse
import subprocess
import svghistogram

# we lean on the controller API to load the pickled data
import controller
from controller import PerfData # XXX?

# for parsing helpers
# XXX: python is pants, can't do this with directories
#perf_parse = __import__('tools/perf-parse')

# and we use the bottle framework to make HTML
import bottle

## do all the analysis and spit out a bunch of status about the
## details of a soak_bench run. Scrape the start/end points for all
## the bench runs, analyse the WUs for each run, and generate a summay
## for each of those runs.
##
## TODO: add instruction trace and call graph logic

###
##  Pulling data from a URL
#

BLOCK_SIZE = 1024 * 1024 # decent size payload

def read_web_file(url):
    print("Reading text URL %s" % url)

    s = ""
    u = urllib.request.urlopen(url)
    while True:
        buf = u.read(BLOCK_SIZE)
        if (not buf):
            break

        s += buf

    print("Read %d bytes from remote" % len(s))
    return s

def download_file(url, dest):

    print("Downloading file %s" % url)

    try:
        u = urllib.request.urlopen(url)
    except Exception as e:
        print("Failed to download file\n")
        print("(Exception was %s)" % e)
        return False

    f = open(dest, "wb")

    total_bytes = 0
    while True:
        buf = u.read(BLOCK_SIZE)
        if (not buf):
            break

        total_bytes += len(buf)
        f.write(buf)
        sys.stdout.write("#")
        sys.stdout.flush()

    print(" Downloaded %dkB" % (total_bytes / 1024))

    return True

def download_rel_file(url, path, dest, dest_file = None):

    if (dest_file is not None):
        dest = "%s/%s" % (dest, dest_file)
        
    src = "%s/%s" % (url, path)
    return download_file(src, dest)
    
###
##  perf row details
#

### columns from the perf controller logic
COL_TS = 0
COL_CCV = 1
COL_WUNAME = 2
COL_CYCLES = 3
COL_PERF0 = 4
COL_PERF_COUNT = 4

COLNM = ["timestamp", "ccv", "wuname", "cycles",
         "perf0", "perf1", "perf2", "perf3"]


SAMPNM = ["timestamp", "vp", "wu", "cycles", None,
          None, None, None, "arg0"]

def vp2ccv(vp):
    return "%s.%s.%s" % (vp/24, (vp%24)/4, (vp%24)%4)

def get_cluster(ccv):
    toks = ccv.split(".")
    return toks[0]

###
##  nominal frequency
#

FREQ_DIV = 1.6

def cycles_to_ns(cycles):
    return (cycles / FREQ_DIV)

def cycles_to_us(cycles):
    return cycles_to_ns(cycles) / 1000.0


###
## Given an ag + list, find the sample instruction traces to show
#
def find_itraces(ag, keyname):

    ls = ag.get_list_by_key(keyname)
    ls.sort()

    extrs = []
    extrs.append(ag.itrace_by_idx("min", keyname, ls[0]))
    if (len(ls) > 2):
        extrs.append(ag.itrace_by_idx("median", keyname, ls[len(ls)/2]))
    if (len(ls) > 1):
        extrs.append(ag.itrace_by_idx("max", keyname, ls[-1]))

    return extrs

###
##   Make a string of average + variance
#
def fmt_avg(avg):
    return "%.1f" % avg

def mk_stddev(vs):
    n = len(vs)
    vsum = sum(vs)
    vmean = float(vsum) / n
    sqs = [ (v - vmean) * (v - vmean) for v in vs ]
    ssqs = sum(sqs)
    s2 = ssqs / n
    s = math.sqrt(s2)

    # print "variance %s = %s" % (vs, s2)

    return s

# make it sortable
def mk_avg_tuple(vs):

    count = len(vs)
    total = float(sum(vs))

    avg = total / count
    s = mk_stddev(vs)

    return (avg, "%s (s=%s)" % (fmt_avg(avg),  fmt_avg(s)))

# just the string
def mk_avg(vs):

    return mk_avg_tuple(vs)[1]

###
##  summarise aggregate data into wustats
#

class WuStats(object):
    pass

def make_wustats(bench, aglist, ccvlist, keyname, itraces, max_count = None):

    ws = WuStats()

    ws.sort = keyname
    ws.max_count = max_count
    ws.rows = []

    # make a list of tuples with the key and sort it
    slist = []
    for ag in aglist:
        slist.append((ag.get_by_key(keyname), ag))

    slist.sort(reverse=True)
    if (max_count is not None):
        slist = slist[:max_count]

    # make hte header row from the first sample
    ws.hdrs = slist[0][1].get_header_row()

    # make the ccv header section
    for ccv in ccvlist:
        ws.hdrs.append("ccv %s" % ccv)

    # now make all the rows
    for (_, ag) in slist:
        # standard columns
        row = ag.get_data_row()

        # make the ccv header section
        for ccv in ccvlist:
            row.append(ag.ccvcounts.get(ccv, 0))

        # now capture the min, median and max record for this wu
        # firstly, by finding the samples, then stashing them in itraces
        its = find_itraces(ag, "cycles")
        itraces[ag.name] = its

        # append all the rows to the output
        ws.rows.append(row)

    return ws

###
##  placeholder for a soak_bench run. just a struct for now
#
RE_DONE = ".*soak_bench results:.*\(([0-9]+)->([0-9]+)\)$"
RE_PERF = ".*soak_bench result: (.*) = ([0-9]+.[0-9]+) ops/sec$"
class SoakBench(object):

    def __init__(self, line):
        self.header_line = line
        self.collects = [] # our list of info

    def set_done(self, line):
        self.done_line = line
        self.parse_done()

    def set_perf(self, line):
        self.perf_line = line
        self.parse_perf()

    def parse_done(self):
        p = re.compile(RE_DONE)
        m = p.match(self.done_line)
        self.t0 = int(m.group(1))
        self.t1 = int(m.group(2))

    def parse_perf(self):
        p = re.compile(RE_PERF)
        m = p.match(self.perf_line)
        self.name = m.group(1)
        self.rate = float(m.group(2))


###
##  given a uart dump, turn it into a list of benchmarks
#
BENCH_HDR = "soak_bench going"
BENCH_COLLECT = "soak_bench collect:"
BENCH_DONE = "soak_bench results: all"
BENCH_PERF = "soak_bench result: "
def parse_uart_log_for_benches(ufile):

    benches = []
    bench = None

    # mini parser / state machine
    lines = open(ufile).readlines()
    for line in lines:
        line = line.strip()

        # check for new bench
        if (BENCH_HDR in line):
            print("Found bench start: %s" % line)
            assert(bench is None)
            bench = SoakBench(line)
            continue

        # check for a collection item
        if (BENCH_COLLECT in line):
            assert(bench is not None)
            bench.collects.append(line)
            continue

        # check for a done item
        if (BENCH_DONE in line):
            bench.set_done(line)
            continue

        if (BENCH_PERF in line):
            bench.set_perf(line)

            # add it to the list
            benches.append(bench)
            bench = None
            continue

        # just ignore it

    return benches


def scrape_boot_args(log):

    lines = log.split("\n")
    sargs = ""
    for line in lines:
        if ("] [boot command] argv[" not in line):
            continue

        sargs += " %s" % line.split(": ")[1]

    return sargs

def scrape_version(log):
    lines = log.split("\n")
    for line in lines:
        if ("] [kernel] Version=" in line):
            return line.split("]")[-1]

    return "not found"


###
##  instruction trace wrapper
#

class ITrace:
    def __init__(self, name, ccv, cycles, perfs, instref, ilog):
        self.name = name
        self.instref = instref
        self.cycles = perfs[0]
        self.perfs = perfs
        self.ccv = ccv
        self.row = [name, ccv, cycles] + perfs + ["%x" % instref]

        read_instruction_trace(self, ilog)

    def mk_inst_dump(self):
        s = "\n".join([ str(i) for i in self.ilist])
        return s

    def mk_func_histogram(self):
        tlist = [ (count, func) for (func, count) in sorted(self.funcref.items()) ]
        tlist.sort(reverse=True)
        hist = [ "%s\t%.1f%%\t%s" % (count, 100 * float(count) / self.cycles, func) for (count, func) in tlist ]
        s = "\n".join(hist)
        return s

# given an itrace object, inject into it the function call breakdown
# and instruction list. FIXME: and red-flag instructions
def read_instruction_trace(itrace, ilog):

    # XXX: Qemu calcuation
    inst0 = itrace.instref - itrace.cycles
    instN = itrace.instref

    # extract the instruction trace for this ccv
    ccv = itrace.ccv
    cilog = ilog[ccv]

    ilist = []
    funcref = {}

    for i in cilog:
        # ignore out of bounds instructions
        if ((i.local_icount < inst0)
            or (i.local_icount > instN)):
            continue

        ilist.append(i)
        funcref[i.func] = funcref.get(i.func, 0) + 1

    itrace.ilist = ilist
    itrace.funcref = funcref

###
##  sample aggregation -- turns a list of samples into dicts of
##  (summed) values, possibly with some stats magic to be applied
##  later. stash the instruction log for later use
#

def checkt(x):
    if (isinstance(x, tuple)):
        return x[1]

    return x

def checkv(x):
    if (isinstance(x, tuple)):
        return x[0]

    return x

CCCs = "8"

class Aggregate:
    def __init__(self, wuname, ilog=None, bench=None, count_vps=False):
        self.name = wuname
        self.total_count = 0
        self.cycles = []
        self.ccvs = []
        self.perf = [ [] for i in range(COL_PERF_COUNT) ]
        self.ccvcounts = {}
        self.ilog = ilog
        self.bench = bench
        self.count_vps = count_vps
        # default perf headers
        self.set_perf_headers(["perf%d" % i for i in range(4)])


    def get_by_key(self, keyname):
        # yup, that janky...
        dictkey = "total_%s" % keyname
        return self.__dict__[dictkey]

    def get_list_by_key(self, keyname):
        # yup, that janky...
        dictkey = "%s" % keyname
        return self.__dict__[dictkey]

    def get_header_row(self):
        # make the perf header section, starting with standards
        hdrs = ["wu name", "count", "rate", "cycles", "time", "avg. cycles", "avg. time"] + self.perf_headers

        if (self.count_vps):
            hdrs += ["num vps", "avg. count per vp"]
        
        return hdrs

    def set_perf_headers(self, headers):
        self.perf_headers = [ "avg. %s" % i for i in headers]

    def total_time(self):
        pct = ""
        if ((self.bench is not None) and (not self.count_vps)):
            # for a single VP, compute the % runtime of this vp
            # FIXME: account for utilisation gap per WU
            pct = " (~%.2g%%)" % (100 * cycles_to_ns(self.total_cycles) / (self.bench.tN - self.bench.t0))
        return "%.3fus%s" % (cycles_to_us(self.total_cycles), pct)

    def avg_time(self):
        return "%.3fus" % cycles_to_us(checkv(self.avg_cycles))

    def rate(self):
        if (self.bench is None):
            return "?"
        fdelta = (self.bench.tN - self.bench.t0) / 1e9
        return "%d/s" % (self.total_count / fdelta)

    def nvps(self):
        ccvps = [vp for vp in list(self.ccvcounts.keys()) if get_cluster(vp) in CCCs]
        pcvps = [vp for vp in list(self.ccvcounts.keys()) if get_cluster(vp) not in CCCs]
       
        return "%spc/%scc" % (len(pcvps), len(ccvps))

    def avg_per_vp(self):
        return "?"
    
    def get_data_row(self):
        # standard columns
        row = [self.name, self.total_count, self.rate(), self.total_cycles,
               self.total_time(), checkt(self.avg_cycles), self.avg_time()]

        # make the perf sections section
        for i in range(0, COL_PERF_COUNT):
            row.append(checkt(self.total_perf[i]))

        # maybe add the per-vp stats
        if (self.count_vps):
            row += [self.nvps(), checkt(self.avg_vp_count)]
            
        return row
    
    # given a list (keyname) and value to find (val)
    # find the right row, then return a tuple suitable for printing
    # that has all the fields
    def itrace_by_idx(self, name, keyname, val):
        ls = self.get_list_by_key(keyname)
        n = ls.index(val)

        # XXX: doesn't abide variable width perf
        return ITrace(name, self.ccvs[n], self.cycles[n],
                      [self.perf[0][n], self.perf[1][n],
                       self.perf[2][n], self.perf[3][n]],
                      self.perf[1][n], self.ilog)


def aggregate_samples(samples, ilog):

    aglist = []
    for k in list(samples.keys()):

        # make an aggregate for this WU name
        ag = Aggregate(k, ilog)

        # compile all the samples for it
        for sample in samples[k]:
            ag.total_count += 1
            ag.cycles.append(sample[COL_CYCLES])
            ag.ccvs.append(sample[COL_CCV])
            for i in range(0, COL_PERF_COUNT):
                ag.perf[i].append(sample[COL_PERF0+i])
            ccv = sample[COL_CCV]
            ag.ccvcounts[ccv] = ag.ccvcounts.get(ccv, 0) + 1

        # now aggregate the aggregates. TODO stats
        ag.total_cycles = sum(ag.cycles)
        ag.avg_cycles = mk_avg(ag.cycles)
        ag.total_perf = []
        for i in range(0, COL_PERF_COUNT):
            ag.total_perf.append(mk_avg(ag.perf[i]))

        # put it on the list
        aglist.append(ag)

    return aglist

###
##  process a single soak_bench call
#
def bench_data_make_aggregates(bench, pd, ilog):

    # work out the start and stop times
    t0 = bench.t0
    t1 = bench.t1

    # dict indexed by WU name, with a list of every sample for that WU ID
    samples = {}

    # a dict of all the VPs we've encountered
    vps = {}

    # split the table
    header = pd.rows[0]
    rows = pd.rows[1:]

    # validate all the headers
    assert(header[COL_TS] == "timestamp")
    assert(header[COL_CCV] == "vp")
    assert(header[COL_WUNAME] == "wu")
    assert(header[COL_CYCLES] == "cycles")
    assert(len(header) >= (COL_PERF0 + COL_PERF_COUNT))

    for row in rows:
        # keep it simple for now by scanning the whole file
        if ((row[COL_TS] < t0) or (row[COL_TS] > t1)):
            continue

        # just dump the rows in the table and we'll re-process them later
        wu = row[2]
        wu_list = samples.setdefault(wu, [])
        wu_list.append(row)

        # make sure we know this VP exists
        vps[row[1]] = True

    # now process the list into aggregates for each wu, with named columns
    ags = aggregate_samples(samples, ilog)

    # the VP list sorted
    vplist = list(vps.keys())
    vplist.sort()

    # now extract the wustats for those aggregates
    bench.itraces = {}
    ws0 = make_wustats(bench, ags, vplist, "count", bench.itraces, 10)
    ws1 = make_wustats(bench, ags, vplist, "cycles", bench.itraces, 10)

    # make a list of aggregates for the template
    bench.wslist = [ws0, ws1]


###
##  dasm parsing
#

DRE = r"^(?P<addr>[0-9a-f]+):\s+[0-9a-f]+\s+(?P<inst>[^\s].*)$"
dasm_insts = {}

def parse_dasm_file(dfile):

    count = 0
    fl = open(dfile)

    dre = re.compile(DRE)
    for line in fl.readlines():
        line = line.strip()
        m = dre.match(line)
        if (m is None):
            continue

        addr = m.group("addr")
        inst = m.group("inst")

        count += 1
        dasm_insts[addr] = inst
    fl.close()

    print("Parsed %d instructions from dasm  file" % count)

###
##  instruction log parsing
#

IRE = r"^Trace CPU (?P<vpnum>[0-9]+) 0x(?P<ts>[0-9a-f]+) \[(?P<pc>[0-9a-f]+)\] (?P<func>[^ ]+) @ (?P<licount>[0-9]+)-(?P<gicount>[0-9]+)$"

# an issued instruction
class InstIssue:
    def __init__(self, ccv, timestamp, pc, func, local_icount, global_icount):
        self.ccv = ccv
        self.timestamp = timestamp
        self.pc = pc
        self.func = func
        self.local_icount = local_icount
        self.global_icount = global_icount

    def __str__(self):
        return "%s\t%s\t%s\t%s" % (self.local_icount, self.pc, self.func, dasm_insts.get(self.pc, "<unknown>"))

global_inst_list = []

def parse_instruction_log(ifile):

    inst_by_ccv = {}

    fl = open(ifile)

    ire = re.compile(IRE)
    for line in fl.readlines():
        line = line.strip()
        m = ire.match(line)
        if (m is None):
            print("skipping line '%s'" % line)
            continue

        ccv = vp2ccv(int(m.group("vpnum")))

        # make an instruction element out of it
        inst = InstIssue(ccv, int(m.group("ts"), 16), m.group("pc"),
                         m.group("func"), int(m.group("licount")),
                         int(m.group("gicount")))

        global_inst_list.append(inst)
        inst_by_ccv.setdefault(ccv, []).append(inst)

    return inst_by_ccv

###
##  top-level job directory processing for instruction log analysis
#
def do_all_bench_stats(jobsdir, style, opts):

    # make our pathnames
    pfile = os.path.join(jobsdir, "perf.data")
    ufile = os.path.join(jobsdir, "uart.txt")
    ifile = os.path.join(jobsdir, "stderror.out")
    dfile = os.path.join(jobsdir, "funos.dasm")
    ffile = os.path.join(jobsdir, "funos-f1-palladium")

    # make sure our perf data is up to date
    maybe_regen_perf_data(jobsdir, ufile, pfile, dfile, ffile)

    # parse the different runs out of the uart
    benches = parse_uart_log_for_benches(ufile)

    if (len(benches) == 0):
        print("Failed to find any soak_bench runs in %s" % ufile)

    print("Scraped %d bench soaks from %s" % (len(benches), ufile))

    # make sure we have a pickle
    pd = controller.read_pd_from_file(pfile)

    # parse the instruction log, if it exists
    print("parsing instruction log")
    ilog = parse_instruction_log(ifile)

    # parse the dasm dump
    print("parsing dasm file")
    parse_dasm_file(dfile)

    # for each bench, do data aggregation into the bench
    print("Crunching benchmark data")
    for bench in benches:
        bench_data_make_aggregates(bench, pd, ilog)

    # run that dict through the template to make the html
    s = bottle.template("wuprof.tpl", style=style, benches=benches)

    fname = os.path.join(jobsdir, check_default_output(opts.output))
    fl = io.open(fname, "w", encoding="utf-8")
    fl.write(s)
    fl.close()

    print("Write output to %s" % fname)

###
##   histogramming
#
HSTEPS = 100
def do_histogram(rows, trim_timestamp = None):

    t0 = rows[0][COL_TS]
    tN = rows[-1][COL_TS]

    # delta and step (-1 for rounding)
    td = tN - t0
    step = td / (HSTEPS-1)

    h = HSTEPS * [0]

    for row in rows:
        i = int((row[COL_TS] - tN) / step)
        h[i] = h[i] + 1

    # make a (timesamp, value, colour) list
    hist = []
    for i in range(len(h)):
        t = t0 + i * step
        if ((trim_timestamp is None) or (t >= trim_timestamp)):
            c = 0x00bfff
        else:
            c = 0xbebebe
        hist.append((t/1e9, h[i], c))

    return svghistogram.plot_svg(hist)

###
##  bench & vp objects and sort functions
#

class WUVPBench:
    def __init__(self, bid):
        self.vps = {}
        self.bid = bid
        self.sorted_vps = None
        self.t0 = None
        self.tN = None
        self.wucount = 0

class WUVPVP:
    def __init__(self, ccv):
        self.wus = {}
        self.sorted_wus = None
        self.ccv = ccv
        self.runtime = 0.0
        self.idletime = 0.0
        self.idle_fixup = 0.0
        self.wucount = 0
        self.util = None
        self.last_ts = 0
        self.first_ts = None

    # some VPs may be very inactive and the idle WU tracking may lose
    # data and they end up looking busier than they are. Make sure we
    # account for extra idle time
    def check_edge_timestamp(self, timestamp, runtime):
        ts = timestamp + runtime
        if (ts > self.last_ts):
            self.last_ts = ts

        if ((self.first_ts is None)
            or (timestamp < self.first_ts)):
            self.first_ts = timestamp
        
    def compute_util(self, bench):
        self.wuutil = self.runtime / (bench.tN - bench.t0)
        self.idle_fixup = (bench.tN - self.last_ts) + (self.first_ts - bench.t0)
        self.idleutil = (self.idletime + self.idle_fixup) / (bench.tN - bench.t0)

        if (self.idleutil < 1.0):
            # default: utilisation = 1 - adjusted idletime
            self.util = 1.0 - self.idleutil
        else:
            # some VPs see idle time > runtime, so use the odl algorithm
            self.util = self.wuutil

    def util_char(self):
        # compute the char like in FunOS
        u = self.util * 100
        if (u < 2.0):
            return "."
        if (u > 98.0):
            return "%"
        return "%d" % int(u / 10)
        
    def get_count(self):
        return self.wucount
    
    def get_runtime(self):
        return self.runtime

    def get_field(self, field):
        if (field == "count"):
            return self.get_count()
        elif (field == "util"):
            return int(self.util * 100.0)
        else:
            raise RuntimeError("bad field %s" % field)

###
##  acquiring samples
#

SAMPLE_FILE = "perf_table.txt"
REMOTE_SAMPLES = "raw_file/perf_table.txt"

REMOTE_UARTS = ["raw_file/odp/uartout0.0.txt",
                "raw_file/odp/uartout0.txt",
                "raw_file/rdp/Compute3/cdn_uartout0.txt",
                "raw_file/rdp/Compute2/cdn_uartout0.txt",
                "raw_file/rdp/StorageNetwork2/cdn_uartout0.txt",
]

def cached_samples(dname):
    return "%s/%s" % (dname, SAMPLE_FILE)

def cached_uart(dname):
    return "%s/uartout0.txt" % dname

def id_for_url(url, opts):
    toks = url.split("/")

    if (toks[-2] != "job"):
        raise RuntimeError("expected URL of the form http://host/job/num")

    return toks[-1]


def cache_path_for_url(input_name, opts):
    return "palladium-job-%s" % id_for_url(input_name, opts)

def output_file_for_url(input_name, opts):
    return "%s/index-%s.html" % (cache_path_for_url(input_name, opts),
                                 id_for_url(input_name, opts))
    

def download_missing_sample_files(opts, url):

    # get the cache directory name
    dname = cache_path_for_url(url, opts)

    # create the directory if it doesn't exist
    if (not os.path.exists(dname)):
        os.mkdir(dname)
    elif (not os.path.isdir(dname)):
        # barf if it exists but isn't a directory
        raise RuntimeError("expected directory: '%s'" % dname)

    # if the sample file doesn't exist, download it
    if (not os.path.exists(cached_samples(dname))):
        if (not download_rel_file(url, REMOTE_SAMPLES, cached_samples(dname))):
            raise RuntimeError("could not download samples file from job")

    # if the uart file doesn't exist, download it
    if (not os.path.exists(cached_uart(dname))):
        for uart in REMOTE_UARTS:
            r = download_rel_file(url, uart, cached_uart(dname))
            if (r):
                break
        else:
            # create a dummy so we don't need network on subsequent runs
            fl = open(cached_uart(dname), "w")
            fl.write("could not find uart log\n")
            
def load_sample_directory(opts, dname):

    if (opts.uart is None):
        opts.uart = cached_uart(dname)

    # read the samples
    pd = load_sample_file(opts, cached_samples(dname))

    return pd

# given a URL/path/file, load the samples, caching locally if necessary
def samples_from_input(input_name, opts):

    # see if it looks like a URL
    if (input_name.startswith("http://")):

        # construct the local path and download any missing files
        dname = cache_path_for_url(input_name, opts)
        download_missing_sample_files(opts, input_name)

        if (opts.output is None):
            opts.output = output_file_for_url(input_name, opts)
        
        # load from the cache
        return load_sample_directory(opts, dname)

    # see if it's a local directory
    if (os.path.isdir(input_name)):
        return load_sample_directory(opts, input_name)

    # see if it's just a local file
    if (os.path.isfile(input_name)):
        # load the tabulated samples file
        return load_sample_file(opts, input_name)

    # otherwise, don't know
    raise RuntimeError("Could not find valid input from '%s'" % input_name)
    

###
##  top-level job processing for WU VP analysis
#

def aggregate_wus(vp_wu_list, perf_headers, bench, count_vps=False):

    ags = []
    for wu_list in vp_wu_list:
        # make an aggregate for this WU name & set its headers
        ag = Aggregate(wu_list[0][COL_WUNAME], bench=bench, count_vps=count_vps)
        ag.set_perf_headers(perf_headers)

        for wu in wu_list:
            ag.total_count += 1
            ag.cycles.append(wu[COL_CYCLES])
            ccv = wu[COL_CCV]
            ag.ccvs.append(ccv)
            ag.ccvcounts[ccv] = ag.ccvcounts.get(ccv, 0) + 1
            for i in range(0, COL_PERF_COUNT):
                ag.perf[i].append(wu[COL_PERF0+i])

        # now aggregate the aggregates. TODO stats
        ag.total_cycles = sum(ag.cycles)
        ag.avg_cycles = mk_avg_tuple(ag.cycles)
        ag.total_perf = []
        for i in range(0, COL_PERF_COUNT):
            ag.total_perf.append(mk_avg_tuple(ag.perf[i]))
        if (count_vps):
            vs = list(ag.ccvcounts.values())
            ag.avg_vp_count = mk_avg_tuple(vs)

        ags.append(ag)
        
    return ags

def wuvp_split_trace(pd, opts):

    # split the table
    header = pd.rows[0]
    rows = pd.rows[1:]

    print(header)

    # validate all the headers
    assert(header[COL_TS] == "timestamp")
    assert(header[COL_CCV] == "vp")
    assert(header[COL_WUNAME] == "wu")
    assert(header[COL_CYCLES] == "cycles")
    assert(len(header) >= (COL_PERF0 + COL_PERF_COUNT))

    # see if we're just doing everyting
    if ((opts.start_time is None)
        and (opts.first_wu is None)):
        depth = 1
    else:
        depth = 0

    benches = []
    bench = []
    check_done = False
    lastts = 0
    for row in rows:

        wuname = row[COL_WUNAME]
        ts = row[COL_TS]
        if (ts < lastts):
            raise RuntimeError("last")
        lastts = ts
        if (wuname == opts.first_wu):
            depth += 1
        if (wuname == opts.last_wu):
            depth -= 1
            check_done = True

        ## FIXME: all this logic
        if ((opts.start_time is not None)
            and (ts >= opts.start_time)):
            depth += 1
            opts.start_time = None
        if ((opts.end_time is not None)
            and (opts.end_time <= ts)):
            depth -= 1
            check_done = True
            opts.end_time = None
            
        if (check_done and (depth == 0)):
            benches.append(bench)
            bench = []
        if (depth > 0):
            bench.append(row) 
        if (depth < 0):
            depth = 0
        check_done = False

    # and add what's left
    if (len(bench) > 0):
        benches.append(bench)
        
    for bench in benches:
        print("bench span:")
        print("\t%s" % (bench[0],))
        print("\t%s" % (bench[-1],))

    return benches


def is_idle_wuid(wuid):
    if (wuid == "wuh_idle"):
        return True

    if (wuid == "__wu_handler__wuh_idle"):
        return True

    return False

def process_bench(opts, rows, perf_headers, bid):

    # construct the bench
    bench = WUVPBench(bid)

    bench.histogram = do_histogram(rows)
    bench.wus = {}
    for row in rows:

        # capture timestamps
        if (bench.t0 is None):
            bench.t0 = row[COL_TS]
        bench.tN = row[COL_TS]
        
        # get the vp for this WU
        ccv = row[COL_CCV]
        vp = bench.vps.get(ccv)
        if (vp is None):
            vp = WUVPVP(ccv)
            bench.vps[ccv] = vp

        # add it to the vp list
        wuid = row[COL_WUNAME]
        wus = vp.wus.setdefault(wuid, [])
        wus.append(row)

        # runtime (cycles -> ns)
        rt = row[COL_CYCLES] / FREQ_DIV

        # track idle edge-case
        vp.check_edge_timestamp(row[COL_TS], rt)
        
        # compute counts and runtime if it's not idle
        if (not is_idle_wuid(wuid)):
            vp.runtime += rt

            vp.wucount += 1
            bench.wucount += 1

            # and to the global list
            wus = bench.wus.setdefault(wuid, [])
            wus.append(row)
        else:
            vp.idletime += rt

    # compute the utilisation on the vps and setup their href name
    for vp in list(bench.vps.values()):
        vp.href = "%s-%s" % (bench.bid, vp.ccv)
        vp.compute_util(bench)

    # sort and trim the VPs
    bench.sorted_vps = list(bench.vps.values())
    bench.sorted_vps.sort(key=lambda vp: vp.get_field(opts.sort_vp), reverse=True)
    bench.sorted_vps = bench.sorted_vps[:opts.nvps]

    # aggregate the global WUs
    bench.global_wus = aggregate_wus(list(bench.wus.values()), perf_headers,
                                     bench, count_vps=True)
    bench.global_wus.sort(key=lambda ag:ag.get_by_key(opts.sort_wu),
                          reverse=True)
    bench.global_wus = bench.global_wus[:opts.nwus]
    
    # for each of the VPs, sort and trim the WUs
    for vp in bench.sorted_vps:
        vp.sorted_wus = aggregate_wus(list(vp.wus.values()), perf_headers, bench)
        vp.sorted_wus.sort(key=lambda ag:ag.get_by_key(opts.sort_wu), reverse=True)
        vp.sorted_wus = vp.sorted_wus[:opts.nwus]

    # add the header
    bench.global_headers = bench.global_wus[0].get_header_row()
    bench.headers = vp.sorted_wus[0].get_header_row()
        
    return bench

    
            
def wuvp_process_trace(pd, opts):

    brows = wuvp_split_trace(pd, opts)
    perf_headers = pd.rows[0][COL_PERF0:COL_PERF0+COL_PERF_COUNT]
    
    # make actual bench objects from the row sets
    benches = []
    bid = 0
    for rows in brows:
        benches.append(process_bench(opts, rows, perf_headers, bid))
        bid = bid + 1

    return benches

def html_uart_log(opts):

    s = opts.uart_log
    
    # XXX: finding this is a bit gross
    try:
        fpath = os.path.dirname(os.path.realpath(__file__))
        p = "%s/../silicon_on_demand" % (fpath)
        print("appending %s" % p)
        sys.path.append(p)

        import uart2html
        s = uart2html.str2html(s)

        # deal with potentially corrupt chars
        s = str(s, errors="replace")
        opts.uart_log = s
    except Exception as e:
        print("Error processing UART to HTML: " + str(e))

        s = str(s, errors="replace")
        opts.uart_log = "<pre>\n" + cgi.escape(s) + "\n</pre>\n"


def load_sample_file(opts, fname):

    if (opts.uart is not None):
        print("reading uart file %s" % opts.uart)

        fl = open(opts.uart)
        opts.uart_log = "".join(fl.readlines())

        # scrape some interesting stuff out of the uart
        opts.uart_scrape["boot-args"] = scrape_boot_args(opts.uart_log)
        opts.uart_scrape["version"] = scrape_version(opts.uart_log)

        # turn the uart log into HTML
        html_uart_log(opts)
    else:
        opts.uart_scrape["boot-args"] = "[no uart log]"
        opts.uart_scrape["version"] = "[no uart log]"

        
    print("loading samples file %s" % fname)

    fl = open(fname)
    rows = []

    line = fl.readline()
    toks = line.split()
    # validate the table headers
    for i in range(len(SAMPNM)):
        if ((SAMPNM[i] is not None) and (toks[i] != SAMPNM[i])):
            print("Invalid sample header row: %s (%s)" % (toks, toks[i]))
            sys.exit(1)            

    # FIXME: it would be good to understand the perf count headers
    # propertly
    header = [toks]

    # process the rest of the lines
    for line in fl.readlines():
        toks = line.split()

        # build a row in original pd format
        rows.append((
            int(toks[0]),  # timestamp
            toks[1],       # ccv
            toks[2],       # wu
            int(toks[3]),  # cycles
            int(toks[4]),  # perf0
            int(toks[5]),  # perf1
            int(toks[6]),  # perf2
            int(toks[7]),  # perf3
            int(toks[8]),  # arg0
        ))

    # sort the rows because input is messed up
    rows.sort()

    # unless specified, trim down to make sure we see every cluster
    all_rows = header + rows
    if (not opts.no_trim):
        start = None
        seen = set()
        for i in range(len(rows)):
            row = rows[i]
            cluster = row[COL_CCV][0]
            if (cluster not in seen):
                start = i
                seen.add(cluster)
        rows = rows[start:]
        print("trimmed to %d rows" % len(rows))

    # re-prepend the header
    rows = header + rows
            
    pd = PerfData()
    pd.rows = rows
    pd.all_rows = all_rows
    pd.trim_start = rows[1][COL_TS]
    return pd

def do_wu_vp_stats(input_name, style, opts):

    # import the sample file/url
    pd = samples_from_input(input_name, opts)

    # generate the histogram
    histograms = {}
    histograms["trim"] = do_histogram(pd.all_rows[1:], pd.trim_start)    
    
    # process the file
    benches = wuvp_process_trace(pd, opts)

    # run that dict through the template to make the html
    s = bottle.template("wuprof-wuvp.tpl", style=style, opts=opts, benches=benches, histograms=histograms, pp=PP())

    # save it to a file
    fname = check_default_output(opts.output)
    fl = open(fname, "w")
    fl.write(s)
    fl.close()

    print("Write output to %s" % fname)

    if (opts.open):
        os.system("open '%s'" % fname)

###
##  pretty-printers for bottle
#

class PP():
    def __init__(self):
        pass

    def time(self, nsec):
        if (nsec is None):
            return "(none)"
        return "%.6f" % (nsec / 1e9)

    def pct(self, num):
        return "%.2f" % (num * 100.0)
    
###
##  bottle path config
#
def do_bottle_config(opts):
    global abs_views_path
    abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
    abs_views_path = os.path.join(abs_app_dir_path, 'views')
    bottle.TEMPLATE_PATH.insert(0, abs_views_path )

    # decide how we want to include the style sheet
    style_inline = True
    if style_inline:
        # inline the whole file for single HTML file goodness
        css_fname = os.path.join(abs_app_dir_path, "static/style.css")
        fl = open(css_fname)
        style_raw = "\n".join(fl.readlines())
        style = "<style>%s</style>" % style_raw
    else:
        # out of line css for maximum webserver cromulence
        style = '<link rel="stylesheet" type="text/css" href="/static/style.css">'

    return style

###
##  generating perf data
#

def do_parse_perf(jobsdir):
    abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
    abs_parse_path = os.path.join(abs_app_dir_path,
                                  'tools', "perf-parse.py")
    subprocess.check_call("%s %s" % (abs_parse_path, jobsdir), shell=True)
        

def maybe_parse_perf(jobsdir, ufile, pfile, ffile):

    if (os.stat(ufile).st_mtime < os.stat(pfile).st_mtime):
        print("Cached perf data OK")
    else:
        print("Rebuilding perf data")
        do_parse_perf(jobsdir)


OBJDUMP = "/Users/Shared/cross/mips64/bin/mips64-unknown-elf-objdump"
def maybe_dasm_dump(dfile, ffile):
    if (os.path.exists(dfile)
        and (os.stat(ffile).st_mtime < os.stat(dfile).st_mtime)):
        print("Cached DASM file OK")
    else:
        print("Rebuilding DASM dump")
        subprocess.check_call("%s -d -z %s > %s" % (OBJDUMP, ffile, dfile), shell=True)

def maybe_regen_perf_data(jobsdir, ufile, pfile, dfile, ffile):

    # make make a pickle of the raw samples
    maybe_parse_perf(jobsdir, ufile, pfile, ffile)

    # maybe dump the DASM
    maybe_dasm_dump(dfile, ffile)
    


###
## argument parsing
#

POWS = { 'u': 1000,
         'm': 1000 * 1000,
         's': 1000 * 1000 * 1000 }

def check_default_output(d):
    if (d is None):
        return "index.html"
    return d

def fixtime(t):
    
    # nothing specified
    if (t is None):
        return None

    mul = 1
    if (t[-1] in POWS):
        mul = POWS[t[-1]]
        t = t[:-1]

    return float(t) * mul

def parse_args():
    usage =  "usage: %prog [options] ilog <job directory>\n"
    usage += "       %prog [options] wuvp <pickle file>"
    parser = optparse.OptionParser(description='soak_bench stats processing',
                                   usage=usage)

    parser.add_option("-f", "--first-wu", default=None,
                      help="first WU of each sample (wuvp)")
    parser.add_option("-l", "--last-wu", default=None,
                      help="last WU of each sample (wuvp)")
    parser.add_option("-s", "--start-time", default=None,
                      help="time to start a sample (wuvp)")
    parser.add_option("-e", "--end-time", default=None,
                      help="time to stop a sample (wuvp)")
    parser.add_option("-v", "--sort-vp", default="util",
                      help="parameter to sort VPs by")
    parser.add_option("-w", "--sort-wu", default="cycles",
                      help="which column to sort WUs by")
    parser.add_option("-n", "--nwus", type="int", default=5,
                      help="number of WUs per VP to display")
    parser.add_option("-m", "--nvps", type="int", default=10,
                      help="number of VPs per benchmark to display")
    parser.add_option("-T", "--no-trim", default=False, action="store_true",
                      help="don't trim the input")
    parser.add_option("-o", "--output", default=None,
                      help="output filename (default=index.html)")
    parser.add_option("-u", "--uart", default=None,
                      help="uart log to append to the run for information")
    parser.add_option("-x", "--open", default=False, action="store_true",
                      help="execute 'open' on the output file when successful")
    parser.add_option("-C", "--cc-clusters", default="8",
                      help="list of control plane cluster GIDs: a,b,c,d")
    
    (opts, args) = parser.parse_args()

    if (len(args) != 2):
        parser.print_help()
        sys.exit(1)

    # default
    global CCCs
    opts.uart_log = "no log specified"
    opts.uart_scrape = {}
    CCCs = opts.cc_clusters
        
    # process times
    opts.start_time = fixtime(opts.start_time)
    opts.end_time = fixtime(opts.end_time)

    # take a copy for the output
    opts.start_time_orig = opts.start_time
    opts.end_time_orig = opts.end_time

    return (opts, args[0], args[1])

###
## entrypoint
#
def main():

    (opts, mode, arg1) = parse_args()

    style = do_bottle_config(opts)

    if (mode == "ilog"):
        # instruction log stats
        jobdir = arg1
        do_all_bench_stats(jobdir, style, opts)
    elif (mode == "wuvp"):
        # WU log by VP
        sample_file = arg1
        do_wu_vp_stats(sample_file, style, opts)

if (__name__ == "__main__"):
    main()
