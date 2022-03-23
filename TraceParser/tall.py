#!/usr/bin/env python3

import os, sys, time, errno, subprocess

from optparse import OptionParser

# ===== INPUTS =====
# BIJI: memory?

# dq.out.dasm.showtm.core0
# dq.out.dasm.showtm.core1
# dq.out.dasm.showtm.core2
# dq.out.dasm.showtm.core3
# dq.out.dasm.showtm.core4
# dq.out.dasm.showtm.core5

# funos-f1-wuq.dasm

# default-filterlist


# ===== OUTPUTS =====
# new folder (date + time)
#    fundata[0-5] (for each core)
#    top-level
#        overview: list of funcs & perf
#        link to each per-core
#        per-core
#            overview: list of funcs & perf, pipeline stall info
#            link to each per-VP
#            text output column execution
#            per-vp
#                overview: list of functions & their perf
#                detailed view
#
#
#
# notes
#    overview of funcs should be visual
#    wu handlers should be grouped in a special output
#
#


core_dq = ["dq.out.dasm.showtm.core0",
       "dq.out.dasm.showtm.core1",
       "dq.out.dasm.showtm.core2",
       "dq.out.dasm.showtm.core3",
       "dq.out.dasm.showtm.core4",
       "dq.out.dasm.showtm.core5"]

dasm_f = "funos-f1-wuq.dasm"


def execute_cmd(cmd):

    #print "CMD: %s" % cmd
    os.system(cmd)

    return 0


def all_inputs_ready(dfolder):

    rdy = True

    for coref in core_dq:
        if not os.path.isfile(os.path.join(dfolder, coref)):
            rdy = False
            print("Missing file: %s" % coref)

    if not os.path.isfile(os.path.join(dfolder, dasm_f)):
        rdy = False
        print("Missing file: %s" % dasm_f)

    return rdy

def generate_all(dfolder):

    # save starting point
    startdir = os.path.abspath(os.path.dirname(__file__))

    tprs_loc = os.path.join(startdir, 'tprs.py')
    tdec_loc = os.path.join(startdir, 'tdec.py')

    dasm_loc = os.path.abspath(os.path.join(dfolder, dasm_f))

    if not os.path.isfile(tprs_loc):
        print("Missing tprs.py script: %s" % tprs_loc)
        sys.exit(-1)

    if not os.path.isfile(tdec_loc):
        print("Missing tdec.py script")
        sys.exit(-1)

    # check that all input files exist
    allf = all_inputs_ready(dfolder)
    if allf == False:
        print("Cannot proceed because of missing files")
        sys.exit(errno.ENOENT)

    # if the files are available, go to the folder and start building
    os.chdir(dfolder)
    outfolder = "out_%s" % time.strftime("%Y_%m_%d_%H_%M")
    os.mkdir(outfolder)
    os.chdir(outfolder)

    # run tprs on each core file
    for core_id in range(0,6):
        coreout = core_dq[core_id]

        print("Analyzing core[%s] file: %s" % (core_id, coreout))
        #print "tprs_loc: %s" % tprs_loc
        #print "tdec_loc: %s" % tdec_loc
        #print "dasm_loc: %s" % dasm_loc
        #print "dfolder: %s" % os.path.abspath(dfolder)

        core_loc = os.path.join(os.path.abspath(dfolder), coreout)

        cwd = os.path.abspath(os.getcwd())
        #print "core_loc: %s" % core_loc

        rc = execute_cmd("%s -a %s -t %s -c %s -d %s -q" % (tprs_loc, dasm_loc, core_loc, core_id, cwd))
        if rc != 0:
            print("Error: ./tprs.py failed (rc %u)" % (rc))
            sys.exit(rc)

        print("Core[%s] analysis complete, generating HTML and stats for all VPs" % core_id)

        rc = execute_cmd("%s -a %s -t %s" % (tprs_loc, dasm_loc, core_loc))
        if rc != 0:
            print("Error: ./tprs.py failed (rc %u)" % (rc))
            sys.exit(rc)

        rc = execute_cmd("%s -t %s -c %s -f %s -d %s" % (tdec_loc, os.path.join(cwd, "fundata_c%s" % core_id), core_id, os.path.join(startdir,"filterlist.txt"), cwd ))
        if rc != 0:
            print("Error: ./tdec.py failed (rc %u)" % (rc))
            sys.exit(rc)

        print("Core[%s] HTML and stats generation complete" % core_id)

    # generate overview index.html

    print("Complete output generation complete")

    # save columns_c[0-5].txt
    # gather stats for each VP
    # generate c[0-5]_vp[0-3].html
    #    link to owning core
    #    list of funcs + perf
    #    execution tree
    #    summary graphs
    # aggregate vp stats to core level
    #    links to all VPs
    #    list of funcs + perf + summary
    # output c[0-5]_top.html
    # 

if __name__ == "__main__":

    # args: folder where all files are



    parser = OptionParser()

    parser.add_option("-d", "--data", dest="data_f", help="Data folder", metavar="FOLDER")

    (options, args) = parser.parse_args()

    if options.data_f == None:
        print("Need a data folder")
        sys.exit(-1)

    generate_all(os.path.abspath(options.data_f))

