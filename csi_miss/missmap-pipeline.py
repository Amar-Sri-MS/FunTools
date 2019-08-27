#!/usr/bin/python

import os
import sys

# pipeline pieces
import csimiss_cook
import gdb_ident
import line_ident
import region_ident
import missmapper


FUNOS_BINARY = gdb_ident.FUNOS_BINARY

###
##  main routine
#

def do_missmap():

    # cook the raw format
    (misslist, addrlist) = csimiss_cook.do_disect(csimiss_cook.RAW_GLOB)

    # save the addrlist
    csimiss_cook.save_json(csimiss_cook.OUT_ADDR, addrlist)
        
    # scrape the region table
    regions = region_ident.find_regions(region_ident.IN_FILE)

    # gdb must go via a file becaue gdb
    # FIXME: expects well known names. Should extend this with a gdb.Command
    # for real arguments
    gdb_ident.restart_in_gdb(FUNOS_BINARY, exit=False)
    
    # line table
    lfname = line_ident.OUT_FILE
    if (os.path.exists(lfname)):
        print "Line identification file exists (%s), using cached copy" % lfname
    else:
        print "Re-generating line identification file (%s)" % lfname
        line_ident.do_line_ident(addrlist, lfname, FUNOS_BINARY)
        
    # Read the two by file
    lineinfo = missmapper.loadjs(lfname)
    gdbinfo = missmapper.loadjs(gdb_ident.OUT_FILE)

    out_fname = missmapper.OUTFILE
    print "Generating final output %s" % out_fname
    missmapper.do_missmap(misslist, lineinfo,
                          regions, gdbinfo, out_fname)
    

###
##  entrypoint
#
if (__name__ == "__main__"):

    do_missmap()
