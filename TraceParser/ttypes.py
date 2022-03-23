#
# ttypes.py: Parse trees for trace parser.
#
# Copyright Fungible Inc. 2017.  All Rights Reserved.

import json

# internal libraries
import tutils_hdr as tutils

class TEntry():

    def __init__(self, line_args, ttype, dasm_info):
        # TBD: use different parsers for initialization
        
        self.vpid = line_args['vpid']
        self.addr = line_args['address']
        
        # TODO(bowdidge): Implement generic way to rewrite
        # addresses.
        # Boot code in FunOS accesses the code from two separate
        # addresses, one cached and not cached.  Map the addresses
        # so they all appear as in the assembly code.
        if self.addr & 0xffffffffb0000000 == 0xffffffffb0000000:
            self.addr = self.addr & 0xffffffffdfffffff

        # XXX make generic
        #self.cycle = cycle
        #self.cycle = tutils.get_cycle(trace_line)

        self.ts = line_args['time']
        self.asm = line_args['arg']

        # TODO(bowdidge): Get true value from trace.
        self.ccount = 1
        #if "idle" in trace_line:
        #    self.func = "idle"
        #elif "Sync" in trace_line:
        #    self.func = "sync"
        #elif "mode" in trace_line:
        #    self.func = "mode"
        #else:
        self.func = tutils.find_function(self.addr, dasm_info)

        if not self.func:
            print("No function for address 0x%x\n" % (
                self.addr))

    def __str__(self):
        return "%24s: %2s cyc %24s (%s)" % (hex(self.addr),self.ccount,self.func,self.pos)

    def get_pos(self):
        return self.pos

    def get_ccount(self):
        return self.ccount

    def get_vpid(self):
        return self.vpid

    def get_func(self):
        return self.func

    def get_addr(self):
        return self.addr

    def get_cycle(self):
        return self.cycle

    def get_ts(self):
        return self.ts

    def get_op(self):
        return ""


class SummaryTree():
    """Node summarizing all calls to a specific function from caller.

    Summary trees contain similar data to call trees, but are more compact.
    If a calls b three times, we create a single entry for a calls b.
    Summary trees don't show code order because of the rewriting, but take
    up much less space, and are better for getting a sense of where time
    is going in specific instances.
    """
    def __init__(self, name):
        # Name of function.
        self.name = name
        # Number of calls times this function was called by parent.
        self.num_calls = 0
        # Total cycles spent when called from parent.
        self.cycles = 0
        # Total idle cycles.
        self.idle_cycles = 0
        # All instruction misses for this function
        self.instr_misses = 0
        # Total load store misses.
        self.load_store_misses = 0
        # SummaryTree nodes for all functions called by this function.
        # Nodes should be added in execution order.
        self.calls = []
        # Number for this SummaryTree node.  Used for serializing trees
        # without nested structures.
        self.id = 0

    def PrintTree(self, level=0):
        print(' ' * (level * 2), end=' ')
        print('%s (%d calls, %d cycles)' % (self.name, self.num_calls,
                        self.cycles))
        for child in self.calls:
            child.PrintTree(level + 1)

    def ChildWithName(self, name):
        for child in self.calls:
            if child.name == name:
                return child
        return None

    def as_dict(self):
        """Presents the TTree in JSON format."""
        result = {}
        result['name'] = self.name
        result['id' ] = self.id
        result['num_calls'] = self.num_calls
        result['cycles'] = self.cycles
        result['idle_cycles'] = self.idle_cycles
        result['instr_misses'] = self.instr_misses
        result['load_store_misses'] = self.load_store_misses
        result['calls'] = [node.id for node in self.calls]
        return result

def MakeSummaryTree(the_ttree):
    """Creates a summary tree from a TTree structure."""
    root = SummaryTree(the_ttree.name)
    root.num_calls = 0
    root.cycles = the_ttree.get_ccount()
    root.idle_cycles = the_ttree.get_idle_count()
    root.instr_misses = the_ttree.get_imcount()
    root.load_store_misses = the_ttree.get_lsmcount()    

    # Pairs of (next ttree to work on, and summary tree parent)
    # Root of TTree is a fake root.  Don't duplicate.
    worklist = [(child, root) for child in the_ttree.calls]
    while worklist:
        (next_node, parent) = worklist.pop(0)
        summary_node = parent.ChildWithName(next_node.name)
        if not summary_node:
            summary_node = SummaryTree(next_node.name)
            parent.calls.append(summary_node)
        summary_node.num_calls += 1
        summary_node.cycles += next_node.get_ccount()
        summary_node.idle_cycles += next_node.get_idle_count()
        summary_node.instr_misses += next_node.get_imcount()
        summary_node.load_store_misses += next_node.get_lsmcount()

        children_work = [(child_node, summary_node)
                         for child_node in next_node.calls]
        # Add children to front so they're processed before following roots.
        worklist = children_work + worklist
    return root
    

# on START, create new sub-node
# current node = newly created node
# on exit, go back to parent
# if parent is None, create one?

class TTree():
    """A node in the call tree."""
    def __init__(self, name, parent, start_cycle, start_idle,
             start_instr_miss, start_loadstore_miss, start_line):
        # Name of the function called.
        self.name = name

        # ParentTTree
        self.parent = parent

        # Functions called by this function.
        self.calls = []

        # Unique integer identifier for this node.
        self.id = 0

        # Start and end cycle for this function call.
        self.start_cycle = start_cycle
        self.end_cycle = start_cycle

        self.start_idle = start_idle
        self.end_idle = 0

        self.start_instr_miss = start_instr_miss
        self.end_instr_miss = start_instr_miss

        self.start_loadstore_miss = start_loadstore_miss
        self.end_loadstore_miss = start_loadstore_miss

        self.start_line = start_line
        self.end_line = start_line

        #print "TTREE: init %s" % name

    def as_dict(self):
        """Presents the TTree in JSON format."""
        result = {'name': self.name}
        result['id' ] = self.id
        if self.calls:
            result['calls'] = [x.id for x in self.calls]
            result['cycles'] = self.get_ccount()
            result['idle_cycles'] = self.get_idle_count()
            result['instr_misses'] = self.get_imcount()
            result['loadstore_misses'] = self.get_lsmcount()
            result['start_line'] = self.start_line
            result['end_line'] = self.end_line

        return result

    def get_calls(self):
        return self.calls

    def add_call(self, ttree):
        self.calls.append(ttree)
        ttree.parent = self

        #print "TTREE: %s add %s" % (self.entry.get_func(), ttree.get_name())


    def get_start_cycle(self):
        return self.start_cycle

    def get_end_cycle(self):
        return self.end_cycle

    def get_start_idle(self):
        return self.start_idle

    def get_idle_count(self):
        return self.end_idle - self.start_idle

    def get_end_cycle(self):
        return self.end_idle

    def get_ccount(self):
        #assert(self.end_cycle - self.start_cycle > 0)
        #print "getting ccount: %s to %s" % (self.start_cycle, self.end_cycle)
        return self.end_cycle - self.start_cycle + 1

    def get_start_instr_miss(self):
        return self.start_instr_miss

    def get_end_instr_miss(self):
        return self.end_instr_miss

    def get_imcount(self):
        return self.end_instr_miss - self.start_instr_miss

    def get_lsmcount(self):
        return self.end_loadstore_miss - self.start_loadstore_miss

    def get_name(self):
        return self.name

    def set_end_cycle(self, cycle):
        self.end_cycle = cycle

    def set_end_idle(self, idle):
        self.end_idle = idle

    def set_end_instr_miss(self, im):
        self.end_instr_miss = im

    def set_end_loadstore_miss(self, lsm):
        self.end_loadstore_miss = lsm

    def get_start_loadstore_miss(self):
        return self.start_loadstore_miss

    def get_end_loadstore_miss(self):
        return self.end_loadstore_miss

    def set_end_line(self, line_num):
        self.end_line = line_num

    def get_entry(self):
        return self.entry

    def get_parent(self):
        if (self.parent == self):
            return None # XXX?
        return self.parent

    def get_start_line(self):
        return self.start_line

    def get_end_line(self):
        return self.end_line

    def stats_str(self, excl_sub_calls):
        cycle_count = self.get_ccount()
        idle_count = self.get_idle_count()
        instr_miss_count = self.get_imcount()
        loadstore_miss_count = self.get_lsmcount()

        if (excl_sub_calls):
            for subcall in self.calls:
                cycle_count = cycle_count - subcall.get_ccount()
                idle_count = idle_count - subcall.get_idle_count()
                instr_miss_count = instr_miss_count - subcall.get_imcount()
                loadstore_miss_count = loadstore_miss_count - subcall.get_lsmcount()

        return "%s cycle, %s idle, %s instr miss, %s load/store miss" % (cycle_count, idle_count, instr_miss_count, loadstore_miss_count)


    def __html_start(self, filterlist, indent, excl_sub_calls):
        symbol = '-'
        style = "block"

        if self.name in filterlist:
            symbol = '+'
            style = "none"

        st =  "<div class=\"line\"><span class=\"timestamp\">%s</span> %s<span class=\"collapseButton\" onclick=\"Collapse(this);\">%s</span> %s (%s)\n" % (self.start_cycle, "&nbsp;"*4*indent, symbol, self.name, self.stats_str(excl_sub_calls))
        st = st +  "<div class=\"collapse\" style=\"display : %s;\">\n" % (style)

        return st

    def __html_end(self):
        return "</div></div>\n"

    def html_tree(self, filterlist, depth, exclude_filtered, exclude_sub_calls):

        if self.name in filterlist and exclude_filtered == True:
            return ""

        ht = self.__html_start(filterlist, depth, exclude_sub_calls)

        #if self.name not in filterlist:
        for subcall in self.calls:
            ht = ht + subcall.html_tree(filterlist, depth+1, exclude_filtered, exclude_sub_calls)

        ht = ht + self.__html_end()

        return ht

    def print_tree_annotated(self, depth, refobj):
        ann = ""

        if self is refobj:
            ann= "*"

        print("%s%s%s%s-> %s [%s]" % (ann, '\t',' '*depth, depth, self.name, self.stats_str(False)))

        for subcall in self.calls:
            subcall.print_tree_annotated(depth+1, refobj)

    def print_tree(self, depth):

        print("[%12s]\t%s%s-> %s [%s]" % (self.get_start_cycle(), ' '*depth, depth, self.name, self.stats_str(False)))

        for subcall in self.calls:
            subcall.print_tree(depth+1)

    def print_tree_ltd(self, startdepth, maxdepth, excl_sub_calls):

        if maxdepth == 0:
            return

        print("%s%s-> %s [%s]" % (' '*startdepth, startdepth, self.name, self.stats_str(excl_sub_calls)))

        for subcall in self.calls:
            subcall.print_tree_ltd(startdepth+1, maxdepth-1, excl_sub_calls)

    def print_context(self):

        if self.parent == None:
            print("----Context----")
            self.print_tree(0)
        else:
            self.get_parent().print_context()


    def propagate_start(self, cycle, idle, im):

        self.start_cycle = cycle
        self.start_idle = idle
        self.start_instr_miss = im

        if self.get_parent() != None:
            self.get_parent().propagate_start(cycle, idle, im)

    def propagate_up(self, cycles, idles, instr_misses):

        self.set_end_cycle(cycles)
        self.set_end_idle(idles)
        self.set_end_instr_miss(instr_misses)

        if self.get_parent() != None:
            self.get_parent().propagate_up(cycles,idles,instr_misses)

    # XXX verify
    def sanitycheck(self):
        subcount = 0
        for el in self.calls:
            subcount = subcount + el.get_ccount()

        if self.get_ccount() < subcount:
            print("sanity check issue:")
            print("[%s] ccount %s subcount %s" % (
                self.name, self.get_ccount(), subcount))
            return False
        else:
            return True


    def get_root(self):
        if self.parent == None:
            return self
        else:
            return self.parent.get_root()

#
# Helper functions for trees.
#

def number_nodes(root, start_number):
    """Adds an id number to every parse tree node in the tree.

    Works for both TTree and SummaryTree.

    This is used to serialize the call tree without forcing nodes
    to be nested in each other, and makes it easier to truncate
    call trees if they're too large to process.

    Returns next number to assign.
    """
    worklist = [root]
    next_id = start_number

    while worklist:
        next = worklist.pop(0)
        next.id = next_id
        next_id += 1
        if next.calls:
            worklist = next.calls + worklist
    return next_id

def max_tree_height(root):
    """Returns the maximum height of the call tree.

    Works for both SummaryTree and TTree.
    """
    max_height = 0
    worklist = [(root, 0)]
    while worklist:
        (next, height) = worklist.pop()
        if height > max_height:
            max_height = height
        if next.calls:
            for call in next.calls:
                worklist.append((call, height + 1))
    return max_height

def write_nodes_as_json(root, out_stream):
    """Writes the named call tree to out_stream in JSON format.

    Output is a list of dictionaries separated by commas.
    """
    worklist = [root]
    first = True
    while worklist:
        next = worklist.pop()
        if not first:
            out_stream.write(',\n')
        first = False
        node_dict = next.as_dict()

        json.dump(node_dict, out_stream)
        if next.calls:
            worklist += next.calls
