#!/usr/bin/python
import os
import re
import sys
import math
import optparse

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


### columns from the controller logic
COL_TS = 0
COL_CCV = 1
COL_WUNAME = 2
COL_CYCLES = 3
COL_PERF0 = 4
COL_PERF_COUNT = 4

COLNM = ["timestamp", "ccv", "wuname", "cycles",
         "perf0", "perf1", "perf2", "perf3"]

def vp2ccv(vp):
    return "%s.%s.%s" % (vp/24, (vp%24)/4, (vp%24)%4)

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

def mk_avg(vs):

    count = len(vs)
    total = float(sum(vs))

    avg = total / count
    s = mk_stddev(vs)

    return "%s (s=%s)" % (fmt_avg(avg),  fmt_avg(s))

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

    # make the perf header section, starting with standards
    ws.hdrs = ["wu name", "count", "cycles", "avg. cycles"]

    # make the perf headers
    for i in range(0, COL_PERF_COUNT):
        ws.hdrs.append("avg. perf%s" % i)

    # make the ccv header section
    for ccv in ccvlist:
        ws.hdrs.append("ccv %s" % ccv)

    # now make all the rows
    for (_, ag) in slist:
        # standard columns
        row = [ag.name, ag.total_count, ag.total_cycles, ag.avg_cycles]

        # make the perf sections section
        for i in range(0, COL_PERF_COUNT):
            row.append(ag.total_perf[i])

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
            print "Found bench start: %s" % line
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

class Aggregate:
    def __init__(self, wuname, ilog):
        self.name = wuname
        self.total_count = 0
        self.cycles = []
        self.ccvs = []
        self.perf = [ [] for i in range(COL_PERF_COUNT) ]
        self.ccvcounts = {}
        self.ilog = ilog

    def get_by_key(self, keyname):
        # yup, that janky...
        dictkey = "total_%s" % keyname
        return self.__dict__[dictkey]

    def get_list_by_key(self, keyname):
        # yup, that janky...
        dictkey = "%s" % keyname
        return self.__dict__[dictkey]

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
    for k in samples.keys():

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
    vplist = vps.keys()
    vplist.sort()

    # now extract the wustats for those aggregates
    bench.itraces = {}
    ws0 = make_wustats(bench, ags, vplist, "count", bench.itraces, 10)
    ws1 = make_wustats(bench, ags, vplist, "cycles", bench.itraces, 10)

    # make a list of aggregates for the template
    bench.wslist = [ws0, ws1]


###
##  instruction log parsing
#

IRE = "^Trace CPU ([0-9]+) 0x([0-9a-f]+) \[([0-9a-f]+)\] ([^ ]+) @ ([0-9]+)-([0-9]+)$"

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
        return "%s\t%s\t%s" % (self.local_icount, self.pc, self.func)

global_inst_list = []

def parse_instruction_log(ifile):

    inst_by_ccv = {}

    fl = open(ifile)

    ire = re.compile(IRE)
    for line in fl.readlines():
        line = line.strip()
        m = ire.match(line)
        if (m is None):
            print "skipping line '%s'" % line
            continue

        ccv = vp2ccv(int(m.group(1)))

        # make an instruction element out of it
        inst = InstIssue(ccv, int(m.group(2), 16), m.group(3),
                         m.group(4), int(m.group(5)), int(m.group(6)))

        global_inst_list.append(inst)
        inst_by_ccv.setdefault(ccv, []).append(inst)

    return inst_by_ccv

###
##  top-level job directory processing
#
def do_all_bench_stats(jobsdir, style, opts):

    # make our pathnames
    pfile = os.path.join(jobsdir, "perf.data")
    ufile = os.path.join(jobsdir, "uart.txt")
    ifile = os.path.join(jobsdir, "stderror.out")

    # parse the different runs out of the uart
    benches = parse_uart_log_for_benches(ufile)

    if (len(benches) == 0):
        print "Failed to find any soak_bench runs in %s" % ufile

    print "Scraped %d bench soaks from %s" % (len(benches), ufile)

    # make sure we have a pickle
    pd = controller.read_pd_from_file(pfile)

    # parse the instruction log, if it exists
    ilog = parse_instruction_log(ifile)

    # for each bench, do data aggregation into the bench
    for bench in benches:
        bench_data_make_aggregates(bench, pd, ilog)

    # run that dict through the template to make the html
    s = bottle.template("wuprof.tpl", style=style, benches=benches)

    fname = os.path.join(jobsdir, 'index.html')
    fl = open(fname, "w")
    fl.write(s)
    fl.close()

    print "Write output to %s" % fname

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
## argument parsing
#
def parse_args():
    usage = "usage: %prog [options] <job directory>"
    parser = optparse.OptionParser(description='soak_bench stats processing',
                                   usage=usage)

    (opts, args) = parser.parse_args()

    if (len(args) != 1):
        parser.print_help()
        sys.exit(1)

    return (opts, args[0])

###
## entrypoint
#
def main():

    (opts, jobdir) = parse_args()

    style = do_bottle_config(opts)
    do_all_bench_stats(jobdir, style, opts)

if (__name__ == "__main__"):
    main()
