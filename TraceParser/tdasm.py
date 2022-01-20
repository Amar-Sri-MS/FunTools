#!/usr/bin/env python2.7

#external libs
import sys, pickle, re
from optparse import OptionParser

#internal libs
from ttypes import TEntry
from ttypes import TTree

import tutils_hdr as tutils


# XXX to be optimized, this is terrible
def tdasm_get_dasm(dasm_f, find_addr):

    # XXX create object representing dasm

    f = open(dasm_f)

    # XXX reading from disk
    for i, line in enumerate(f):

        if line.startswith(hex(find_addr).rstrip("L").lower().replace('0x','')):

            if tutils.asm_isfunc(line)[0] == True:
                continue

            return line.strip()

    return "???"
            

def tdasm_print_lines(pdt_f, dasm_f, vpid, start_line, end_line):

    f = open(pdt_f)

    for i, line in enumerate(f):

        if i >= start_line-1 and i < end_line :
            #print i

            if tutils.is_instruction(line):
                if tutils.get_vpid(line) == vpid:
                    if 'idle' in line: # XXX improve
                        print line.strip()
                    elif 'Sync' in line:
                        pass
                    else:
                        print "%s\t\t\t\t%s" % (line.strip(), tdasm_get_dasm(dasm_f, tutils.get_address(line)))
                else:
                    print "-- (vp %s)" % tutils.get_vpid(line) # XXX

    f.close()

def tdasm_show_func_rec(vpid, pdt_f, dasm_f, tree, funcname, printed, max_prints, min_cycles, max_cycles):

    if funcname == tree.get_name():

        if tree.get_ccount() >= min_cycles and tree.get_ccount() <= max_cycles:
            
            printed = printed + 1

            print "\n\n"

            print "=========== NEW OCCURRENCE OF %s (count: %s/%s) ===========" % (funcname, printed, max_prints)
            print "=========== cycle count: %s\t===========" % tree.get_ccount()
            print "=========== vp: %s\t\t===========" % vpid

            tdasm_print_lines(pdt_f, dasm_f, vpid, tree.get_start_line(), tree.get_end_line())


    for sc in tree.get_calls():
        printed  = tdasm_show_func_rec(vpid, pdt_f, dasm_f, sc, funcname, printed, max_prints, min_cycles, max_cycles)

        if printed >= max_prints:
            return printed


    return printed


# returns: True if we hit the limit, False otherwise
def tdasm_show_func(pdt_f, dasm_f, funtrc, funcname, max_prints, min_cycles, max_cycles):

    vpid = 0

    for tree in funtrc:

        printed = tdasm_show_func_rec(vpid, pdt_f, dasm_f, tree, funcname, 0, max_prints, min_cycles, max_cycles)

        vpid = vpid + 1

        if printed >= max_prints:
            return True

    return False

if __name__ == "__main__":

    parser = OptionParser()

    parser.add_option("-a", "--dasm-file", dest="fun_dasm_txt_f", help="funos.dasm file", metavar="FILE")
    parser.add_option("-t", "--funtrc-data", dest="funtrc_data_f", help="fungible trace object", metavar="FILE")
    parser.add_option("-f", "--func", dest="func", help="function name")
    parser.add_option("-T", "--funtrc-txt", dest="fun_trc_txt_f", help="fungible trace txt", metavar="FILE")
    parser.add_option("-F", "--format", dest="format", help="Trace file format %s" % tutils.VALID_FORMATS, metavar="FORMAT", default=None)
    parser.add_option("-q", "--quiet", action='store_true', default=False, dest="quiet", help="No output during parsing")
    parser.add_option("-m", "--max", dest="max_prints", help="maximum occurrences to show (default:10)")
    parser.add_option("-r", "--range", dest="cycle_range", help="min/max num cycles to display")

    (options, args) = parser.parse_args()

    min_cycles = 0
    max_cycles = sys.maxint

    if options.fun_dasm_txt_f is None:
        print "Need to specify a fungible dasm file"
        sys.exit(1)

    if options.funtrc_data_f is None:
        print "Need to specify a fungible option trace file"
        sys.exit(1)

    if options.fun_trc_txt_f is None:
        print "Need to specify a fungible trace text file"
        sys.exit(1)

    if options.func is None:
        print "Need to specify a function to look at"
        sys.exit(1)

    if options.cycle_range is not None:

        cycles = options.cycle_range.split(',')

        min_cycles = int(cycles[0])

        if len(cycles) == 1:
            max_cycles = int(cycles[0])
        else:
            max_cycles = int(cycles[1])

    print "Cycle range: %s to %s" % (min_cycles, max_cycles)

    if options.format not in tutils.VALID_FORMATS:
        print "Format must be one of %s" % tutils.VALID_FORMATS
        sys.exit(1)

    max_prints = 10

    if options.max_prints is not None:
        max_prints = int(options.max_prints)

        # set the format
        tutils.set_format(options.format)

    f = open(options.funtrc_data_f, 'r')
    funtrc = pickle.load(f)
    f.close()

    ret = tdasm_show_func(options.fun_trc_txt_f, options.fun_dasm_txt_f, funtrc, options.func, max_prints, min_cycles, max_cycles)

    if ret == True:

        print "Printed the first %s occurrences of %s" % (max_prints, options.func)
        print "Note: Iteration order is VP0-3 and then within the VP ordered by time, i.e. ALL VP0 entries will print before VP1."
