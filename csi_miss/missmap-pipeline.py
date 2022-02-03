#!/usr/bin/env python2.7

import argparse
import os

# pipeline pieces
import csimiss_cook
import gdb_ident
import line_ident
import region_ident
import missmapper
import thread_local_ident


FUNOS_BINARY = gdb_ident.FUNOS_BINARY

MAX_ROWS = 10000

###
##  main routine
#

def do_missmap():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--funos-bin',
                        type=str, help='path to funos binary',
                        default=FUNOS_BINARY)

    args = parser.parse_args()

    # cook the raw format
    (misslist, addrlist) = csimiss_cook.do_disect(csimiss_cook.RAW_GLOB)

    # save the addrlist
    csimiss_cook.save_json(csimiss_cook.OUT_ADDR, addrlist)
        
    # scrape the region table
    regions = region_ident.find_regions(region_ident.IN_FILE, region_ident.IN_JSON_FILE)

    # dump thread locals
    tls_base, tls_stride = thread_local_ident.get_thread_local_info(regions,
                                                                    region_ident.IN_FILE,
                                                                    thread_local_ident.IN_JSON_FILE)
    if tls_stride is not None:
        thread_local_ident.dump_thread_locals(args.funos_bin, tls_base, tls_stride)

    # gdb must go via a file becaue gdb
    # FIXME: expects well known names. Should extend this with a gdb.Command
    # for real arguments
    gdb_ident.restart_in_gdb(args.funos_bin, exit=False)

    # line table
    lfname = line_ident.OUT_FILE
    if (os.path.exists(lfname)):
        print "Line identification file exists (%s), using cached copy" % lfname
    else:
        print "Re-generating line identification file (%s)" % lfname
        line_ident.do_line_ident(addrlist, lfname, args.funos_bin)

    # Read the two by file
    lineinfo = missmapper.loadjs(lfname)
    gdbinfo = missmapper.loadjs(gdb_ident.OUT_FILE)

    out_fname = missmapper.OUTFILE_HTML
    print "Generating HTML output %s" % out_fname
    missmapper.do_missmap(misslist, lineinfo,
                          regions, gdbinfo, "html", out_fname,
                          max_rows=MAX_ROWS)

    out_fname = missmapper.OUTFILE_CSV
    print "Generating CVS output %s" % out_fname
    missmapper.do_missmap(misslist, lineinfo,
                          regions, gdbinfo, "csv", out_fname)

###
##  entrypoint
#
if (__name__ == "__main__"):

    do_missmap()
