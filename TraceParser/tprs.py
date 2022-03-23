#!/usr/bin/env python2.7

# external libs
import sys, pickle, json, os, time

# specific imports
from optparse import OptionParser

# internal libs

import parse_dasm
import ttypes
from ttypes import TEntry
from ttypes import TTree

import tutils_hdr as tutils
import tutils_sim
#
# 

# True if should print extra messages explaining what the tree builder i
# doing.
debug = False

# True if should drop into debugger on failure.
debug_halt = False

def make_stat():
    """Create an empty stat dictionary for a single function.

    We initialize all possible values so we know that the resulting JSON
    will always have some value for each key.
    """
    return {'calls': 0,
        # Total cycles for function and callers.
        'cycles': 0 ,
        # Total idle time for tree.
        'tree_idle': 0,
        # Instruction misses seen during subtree execution.
        'instr_miss': 0,
        # Load/store misses seen during subtree exexcution.
        'loadstore_miss': 0,
        # Individual number of cycles for each call to function.
        'cycle_values': [],
        # Average number of cycles for any call
        'cycles_average': 0,
        # Maximum number of cycles for execution of function.
        'cycles_max': 0,
        # Minimum number of cycles for execution of function.
        'cycles_min': 0,
        'cycles_std_dev': 0 }

def gather_stats_in_tree(root, stats):
    """Update stats for every function in the tree.

    root is the root of the call tree to process.
    stats is the dictionary mapping function names to stats that receives the
    statistics.
    """
    worklist = [root]
    while worklist:
        next = worklist.pop()
        if next.name not in stats:
            stats[next.name] = make_stat()
        call_cycles = next.end_cycle - next.start_cycle
        stats[next.name]['calls'] += 1
        stats[next.name]['cycles'] += call_cycles
        stats[next.name]['cycle_values'].append(call_cycles)

        idle_cycles = 0
        if next.end_idle > next.start_idle:
            idle_cycles = next.end_idle - next.start_idle
            stats[next.name]['tree_idle'] += idle_cycles

        instr_misses = 0
        if next.end_instr_miss > next.start_instr_miss:
            instr_misses = (next.end_instr_miss -
                            next.start_instr_miss)
        stats[next.name]['instr_miss'] += instr_misses

        loadstore_misses = 0
        if next.end_loadstore_miss > next.start_loadstore_miss:
            loadstore_misses = (next.end_loadstore_miss -
                                next.start_loadstore_miss)
        stats[next.name]['loadstore_miss'] += loadstore_misses
        if next.calls:
            worklist += next.calls

def generate_function_stats(roots):
    """Returns array summarizing behavior of each function.

    The result is a map of function names to dictionary of stat values for
    that function.
    """
    stats = {}
    result = []
    for root in roots:
        gather_stats_in_tree(root, stats)
    for fn_name in stats:
            # Ignore roots.
            if fn_name.startswith('core '):
                continue
            fn_stats = stats[fn_name]
            stat = {}
            stat['name'] = fn_name
            stat['cycles'] = sum(fn_stats['cycle_values'])
            stat['calls'] = len(fn_stats['cycle_values'])
            stat['cycles_min'] = min(fn_stats['cycle_values'])
            stat['cycles_max'] = max(fn_stats['cycle_values'])
            average = stat['cycles'] / fn_stats['calls']
            stat['cycles_average'] = average
            result.append(stat)

    return sorted(result, key=lambda x: x['name'])

def output_trace_as_json(output_stream, roots, stats):
    """Outputs trace information as JSON.
    output_stream is the stream to write the output.
    root is list of roots of SummaryTree for each VP.
    stats is a map of function names to stats for the function.
    """
    first = True
    root_ids_str = ','.join([str(root.id) for root in roots])
    out_stream.write('{"roots": [%s],\n' % root_ids_str)
    out_stream.write(' "call_nodes": [')
    for root in roots:
        if not first:
            out_stream.write(',\n')
        first = False
        ttypes.write_nodes_as_json(root, out_stream)
    out_stream.write('],\n')
    out_stream.write('"function_stats": %s\n' % json.dumps(stats))
    out_stream.write('}\n')

def ValidateSummaryTrees(roots):
    """Returns False if tree is invalid or odd.
    
    For now, only check that the number of cycles spent in a child is
    smaller than the number of cycles spent in the parent.
    ."""
    success = True
    worklist = list(roots)
    while worklist:
        next = worklist.pop(0)
        if next.calls:
            for child in next.calls:
                if next.name.startswith('core '):
                    # TODO(bowdidge): Fix numbers for root nodes.
                    continue
                if child.cycles > next.cycles:
                    print ('Unexpected time: cycles for %s is %d,'
                           'cycles for child %s is %d' %
                           (next.name, next.cycles, child.name, child.cycles))
                    success = False
    return success

def read_a_line(infile, follow):
    """Reads a single line from the trace file.
    infile is file handle or generator containing lines.
    follow is true if file should be checked continually for new input.
    """
    # easy case
    if (not follow):
        return infile.readline()

    # follow case
    do_pause = False
    line = ""
    while (True):
        if do_pause:
            time.sleep(1)
        part_line = infile.readline()

        do_pause = True
        # if we read nothing
        if part_line == "":
            continue

        line += part_line

        # if we read a newline, we're good
        if (line[-1] == "\n"):
            return line
        # go back and try for more


class TreeBuilder:
    """Creates a call tree from a sequence of TEntry objects."""

    def __init__(self, dasm_parser, core_id):
        """ Create a new TreeBuilder.

        dasm_parser stores information about the binary - symbol locations,
        code, etc.
        core_id gives the integer number of the current core for printing
        """
        # Name of last function running on each VP.
        # Used to determine when we started executing a different function.
        self.last_found_func = [None, None, None, None]

        # Address of last instruction executed on each VP.
        self.last_address = [0, 0, 0, 0]

        self.roots = [TTree('core %d vp0' % core_id, None, 0, 0, 0, 0, 0),
                      TTree('core %d vp1' % core_id, None, 0, 0, 0, 0, 0),
                      TTree('core %d vp2' % core_id, None, 0, 0, 0, 0, 0),
                      TTree('core %d vp3' % core_id, None, 0, 0, 0, 0, 0)]
        # TTree node for current function executing in the Current function e
        self.current_ttree = list(self.roots)

        # Assembly parser that knows more about calling patterns.
        self.dasm_parser = dasm_parser

    def AddEntry(self, entry, stats):
        """Add a TEntry representing an instruction to the parse tree.

        If the entry shows that we've changed functions, then the TreeBuilder
        needs to create a new tree node.
        """

        last_func = self.last_found_func[entry.vpid]
        current = self.current_ttree[entry.vpid]

        if entry.func == None:
            # Can't say anything about unmapped code.
            return

        if not last_func:
            leaf = TTree(entry.func, None, stats.cycles,
                         stats.real_idles, stats.instr_misses,
                         stats.loadstore_misses, stats.lines)
            current.add_call(leaf)
            self.current_ttree[entry.vpid] = leaf
            self.last_found_func[entry.vpid] = entry.func
            self.last_address[entry.vpid] = entry.addr
            return

        # Ignore instructions where execution was within the same
        # function unless the function is known to be recursive.
        if entry.func == last_func:
            if entry.func == 'parse_json_recursive':
                if entry.addr == self.last_address[entry.vpid] - 4:
                    self.last_address[entry.vpid] = entry.addr
                    return
            else:
                # We didn't change functions.
                # TODO(bowdidge): Update stats here.
                self.last_address[entry.vpid] = entry.addr
                return

        # Why did we change functions?
        kind = self.dasm_parser.GetBranchKind(last_func,
                                              self.last_address[entry.vpid],
                                              entry.func, entry.addr)
        if debug:
            # Identify changes to call tree.
            print '%d (line %d) %s %x %s %s %x' % (
                stats.cycles, stats.lines, self.last_found_func[entry.vpid],
                self.last_address[entry.vpid],
                kind, entry.func, entry.addr)

        if kind is None:
            print 'Unknown reason why we changed functions!'
            print 'Line %d cycle %d' % (stats.cycles, stats.lines)
            print 'Prev fn %s addr %x next fn %s next addr %x' % (
                last_func,
                self.last_address[entry.vpid],
                entry.func, entry.addr)
            # TODO(bowdidge): Figure out more gentle solution.
            if debug_halt:
                import pdb
                pdb.set_trace()

        if kind == 'IGNORE':
            # Not an interesting transition.
            self.last_address[entry.vpid] = entry.addr
            return

        elif kind == 'JUMP' or kind == 'FALLTHROUGH':
            # Add this node to the list of parent calls. so the source
            # and destination of the jump are on the same level.
            # TODO(bowdidge): Put tail calls as children of caller, rather
            # than siblings.
            current.set_end_cycle(stats.cycles)
            current.set_end_idle(stats.real_idles)
            current.set_end_instr_miss(stats.instr_misses)
            current.set_end_loadstore_miss(stats.loadstore_misses)

            leaf = TTree(entry.func, None, stats.cycles,
                         stats.real_idles, stats.instr_misses,
                         stats.loadstore_misses, stats.lines)

            if current.parent:
                current.parent.add_call(leaf)
            else:
                # If this was a fallthrough in the first function in the trace,
                # treat as a call to the first function.
                current.add_call(leaf)
            self.current_ttree[entry.vpid] = leaf

        elif kind == 'CALL':
            # Add new child node to current parent.
            leaf = TTree(entry.func, None, stats.cycles,
                         stats.real_idles, stats.instr_misses,
                         stats.loadstore_misses, stats.lines)
            # Set up as call.
            current.add_call(leaf)
            self.current_ttree[entry.vpid] = leaf

        elif kind == 'RET':
            # Return from current node to parent.
            if not current.parent:
                # TODO(bowdidge): Handle case of returning too many times.
                # Should add new parent nodefor subtree.
                pass
            else:
                current.set_end_cycle(stats.cycles)
                current.set_end_idle(stats.real_idles)
                current.set_end_instr_miss(stats.instr_misses)
                current.set_end_loadstore_miss(stats.loadstore_misses)
                self.current_ttree[entry.vpid] = current.parent
                current = current.parent

                # Should do more checking like this.
                # current.parent.parent is trying to check for we're in assembly.
                if (entry.func != current.name and current.parent and
                    current.parent.parent and (
                    # Ignore some assembly functions that are building a
                    # stack and returning when no call was seen.
                    entry.func != 'init_done' and
                    entry.func != 'kernel_entry_asm' and
                    entry.func != '__cpu_init')):

                    print 'Mismatch on return'
                    print 'Caller was %s' % entry.func

                    print 'Return to %s' % entry.func
                    print 'Stack is: '
                    a = current.parent
                    while a is not None:
                        print a.name
                        a = a.parent
                    if debug_halt:
                        import pdb
                        pdb.set_trace()

        elif kind == 'ROOT':
            # Add the new node as a child of the current root.
            while current != self.roots[entry.vpid]:
                current.set_end_cycle(stats.cycles)
                current.set_end_idle(stats.real_idles)
                current.set_end_instr_miss(stats.instr_misses)
                current.set_end_loadstore_miss(stats.loadstore_misses)
                current = current.parent
            self.current_ttree[entry.vpid] = self.roots[entry.vpid]
            current = self.current_ttree[entry.vpid]
            leaf = TTree(entry.func, None, stats.cycles,
                         stats.real_idles, stats.instr_misses,
                         stats.loadstore_misses, stats.lines)
            current.add_call(leaf)
            self.current_ttree[entry.vpid] = leaf

        self.last_found_func[entry.vpid] = entry.func
        self.last_address[entry.vpid] = entry.addr

    def PrintTrees(self):
        """Dumps all call trees to stdout."""
        for tr in self.roots:
            tr.print_tree(0)

    def FinishEntry(self, stats):
        """Walk all trees and close out durations for all functions."""
        for tree in self.current_ttree:
            while tree.parent is not None:
                tree.set_end_cycle(stats.cycles)
                tree.set_end_idle(stats.real_idles)
                tree.set_end_instr_miss(stats.instr_misses)
                tree.set_end_loadstore_miss(stats.loadstore_misses)
                tree = tree.parent

    def Roots(self):
        return self.roots


class TraceStats():
  """Single object holding cumulative stats gathered on the trace."""
  def __init__(self):
      self.instr_misses = 0
      self.loadstore_misses = 0
      self.cycles = 0
      self.real_idles = 0
      self.lines = 0


def read_trace(trace_fname, dasm_info, filter_fns, follow, core_id):
    """Parses a trace file and creates a tree of function calls.

    trace_fname is the file containing the samurai trace.

    dasm_info is a DasmInfo object giving information about the location
    of symbols and calls in the code.

    filterlist is list of functions that should be ignored.

    follow is true if the file should be checked repeatedly for new content.

    core_id is the core number being processed.
    """

    # to be refined based on understanding of pipeline
    real_cycles = 0
    idles = 0
    stats = TraceStats()
    nxtprint = 0
    last_print_cycles = 0
    tree_builder = TreeBuilder(dasm_info, core_id)

    with open(trace_fname) as infile:
        while (True):
            line = read_a_line(infile, follow)
            if not line:
                break
            stats.lines += 1
            # TODO(bowdidge): Fix other trace formatss to split line
            # once during parsing.
            args = tutils_sim.ParseLine(line)

            if not args:
                continue
            # TODO(bowdidge): Define constants for instr (1) or data (2)
            if args['type'] == 'I':
                entry = TEntry(args, 0, dasm_info)

                vp = entry.vpid
                stats.cycles += entry.get_ccount()
                real_cycles = stats.cycles/tutils.get_num_pipelines()

                func = entry.get_func()
                if func == "idle":
                    stat['idles'] += entry.get_ccount()
                    stats.real_idles += (
                        stat['idles']/tutils.get_num_pipelines())
                    
                if func in filterlist:
                    continue

                tree_builder.AddEntry(entry, stats)

            elif False:
                stats.instr_misses += 1

            elif False:
                if tutils.is_loadstore_miss(line):
                    stats.loadstore_misses += 1
    infile.close()

    print "Run complete..."

    tree_builder.FinishEntry(stats)
    roots = tree_builder.Roots()
    for root in roots:
        sc = root.sanitycheck()
        print "Sanity check for %s: %s" % (root.name, sc)

    max_call_depth = max([ttypes.max_tree_height(root)
              for root in roots])

    elapsed_secs = real_cycles/float(1000000000)
    elapsed_msecs = real_cycles/float(1000000)

    print "Total cycles: %s" % stats.cycles
    print "Time elapsed @ 1GHz: %s seconds (%s ms)" % (elapsed_secs,
                               elapsed_msecs)
    print "Max call depth: %d" % max_call_depth
    print "Total idles: %s" % stats.real_idles
    print "Total instr misses: %s" % stats.instr_misses
    print "Total load/store misses: %s" % stats.loadstore_misses

    return roots


def print_funcs(ranges):

    flist = []

    query = 0xffffffff8010e2f8

    for item in ranges:
        flag = ""
        if query >= item[1] and query < item[2]:
            flag = "*"


        print "%s\t%s\t%s\t%s" % (flag, hex(item[1]), hex(item[2]), item[0])

        if item[0] in flist:
            print "%s already in list" % item[0]
        else:
            flist.append(item[0])


#
#
#
if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-a", "--asm", dest="asm_f", help="asm file", metavar="FILE")
    parser.add_option("-t", "--trace", dest="trc_f", help="trace file", metavar="FILE")
    parser.add_option("-r", "--reverse", dest="reverse_order", help="order last instruction first", action="store_true")
    parser.add_option("-f", "--filter", dest="filter_f", help="filter file", metavar="FILE")
    parser.add_option("-c", "--core", dest="core_id", help="Core ID")
    parser.add_option("-d", "--data", dest="data_f", help="Data folder", metavar="FOLDER")
    parser.add_option("-F", "--format", dest="format", help="Trace file format %s" % tutils.VALID_FORMATS, metavar="FORMAT", default=None)
    parser.add_option("-w", "--follow", dest="follow", help="Keep polling trace file for new data to process", default=False, action="store_true")
    parser.add_option("-q", "--quiet", action='store_true', default=False, dest="quiet", help="No output during parsing")
    parser.add_option("--debug", action='store_true', default=False,
                      dest='debug',
                      help='Print debugging messages explaining behavior.')

    parser.add_option("--debug-halt", action='store_true', default=False,
                      dest='debug_halt',
                      help='Drop into the debugger in case of unusual problems.')

    (options, args) = parser.parse_args()

    if options.debug:
        debug = True

    if options.debug_halt:
        debug_halt = True

    if options.asm_f is None:
        print "ASM file is mandatory. Use -h for more information"
        sys.exit(1)

    if options.format not in tutils.VALID_FORMATS:
        print "Format must be one of %s" % tutils.VALID_FORMATS
        sys.exit(1)

    # set the format
    tutils.set_format(options.format)

    filterlist = ["idle", "sync", "mode"] # XXX we shouldn't need this, it should be handled by is_instruction (to be renamed)

    core_id = 0

    if options.core_id != None:
        core_id = int(options.core_id)

    dst = ''
    if options.data_f != None:
        dst = os.path.abspath(options.data_f)
        if not os.path.exists(dst):
            print "Invalid folder for dst"
            sys.exit(1)

    if options.filter_f:
        f = open(options.filter_f)
        for line in f.readlines():
            filterlist.append(line.strip())
        f.close()

        print "Filter list: %s" % filterlist

    if options.reverse_order:
        print "Reverse order not currently supported, my apologies."
        sys.exit(0)

        sys.stderr.write('Parsing disassembly.\n')
    f = open(options.asm_f)
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(f.readlines())
    f.close()

    sys.stderr.write('Parsing trace.\n')
    roots = read_trace(options.trc_f, dasm_info,
               filterlist, options.follow, core_id)

    sys.stderr.write('Done reading trace.\n')
    dasm_info.PrintMisses()
    roots = [r for r in roots if r is not None]

    sys.stderr.write('Numbering nodes.\n')
    next_id = 1
    for root in roots:
        next_id = ttypes.number_nodes(root, next_id)

    for root in roots:
            # Used for tests.
            print 'Tree height: %d' % ttypes.max_tree_height(root)

    next_id = 1
    summary_trees = [ttypes.MakeSummaryTree(root) for root in roots]
    ValidateSummaryTrees(summary_trees)
    for summary_tree in summary_trees:

            next_id = ttypes.number_nodes(summary_tree, next_id)

    function_stats = generate_function_stats(roots)

    # Output the data in JSON format for consumption by the web pages.
    out_path = os.path.join(dst, 'fundata_c%s.json' % core_id)
    out_stream = open(out_path, 'w')

        # Don't include raw call tree for now - just summary tree.
    output_trace_as_json(out_stream, summary_trees, function_stats)
    out_stream.close()


