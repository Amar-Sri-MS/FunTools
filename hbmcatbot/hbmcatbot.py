#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compress and concatenate dpu hbmdump files found in a given path.

static check:
% mypy myfile.py
"""

import argparse
import os
import glob
import datetime
import time
import sys

try:
    import idzip
except:
    print("Failed to import idzip compressor")
    print("Please use 'pip3 install python-idzip'")
    sys.exit(1)
    
# command-line arguments
args: argparse.Namespace = None

###
##  file classes
#

# 16 * ~1/2GB shards
NSHARDS = 16
DUMPSIZE = 8 * 1024 * 1024 * 1024
ZSKIP = (1024 * 1024) # bothersome 1mb hole
SHARDSIZE = int((DUMPSIZE-ZSKIP) / NSHARDS)
assert(((DUMPSIZE-ZSKIP) % NSHARDS) == 0)

class HBMShard:
    def __init__(self, fullname):
        assert(os.path.exists(fullname))
        self.fullname = fullname
        self.stat = os.stat(fullname)
        self.filename = os.path.split(fullname)[1]


class HBMDump:
    def __init__(self, fileprefix):
        self.prefix = fileprefix
        self.shards = [None] * NSHARDS

    def add_shard(self, fullname):

        # extract the number
        toks = fullname.split("_")
        tail = toks[-1]
        assert(tail[3] == ".")
        n = tail[:3]
        n = int(n)
        assert(n >= 0)
        if (n >= NSHARDS):
            raise RuntimeError("shard number too high: %s" % fullname)

        assert(self.shards[n] is None)
        self.shards[n] = HBMShard(fullname)

    def is_complete(self):

        for shard in self.shards:
            if (shard is None):
                # not complete if we're missing a shard
                return False
            if (shard.stat.st_size < SHARDSIZE):
                # not complete if a shard is incomplete
                return False

        # everything was there and big enough
        return True
       
    def incomplete_pct(self):

        total = 0
        for shard in self.shards:
            if (shard is None):
                continue
            total += min(shard.stat.st_size, SHARDSIZE)

        pct = int(100 * total / (NSHARDS * SHARDSIZE))
        return pct

    def is_timedout(self):

        # see if all shards are old
        for shard in self.shards:
            if (shard is None):
                # not complete if we're missing a shard
                continue

            ctime = datetime.datetime.fromtimestamp(shard.stat.st_ctime)
            delta = datetime.datetime.now() - ctime
            if (delta < datetime.timedelta(seconds=60*10)):
                # any shard modified less than 10min ago means
                # we're not timing out yet
                return False
        
        return True


###
##  compression routine
#

def compress_dump(dump: HBMDump, incomplete: bool = False) -> None:

    # make a filename
    istr = ""
    if (incomplete):
        pct = dump.incomplete_pct()
        istr = ".incomplete-%d" % pct
    filename = dump.prefix + istr + ".in.gz"
    fname = os.path.join(args.outpath, filename)

    if (os.path.exists(fname)):
        print("ERROR: output file exists: '%s' Likely issue with rm. Ignoring",
              fname)
        return
        
    # compress it
    print("Writing idgz to file %s" % fname)
    idzip.Writer.enforce_extension = False
    wr = idzip.Writer(fname)

    for shard in dump.shards:
        written = 0
        if (shard is not None):
            print("adding shard %s" % shard.fullname)
            fl = open(shard.fullname, "rb")

            # add all the data 
            while (True):
                data = fl.read(10*1024*1024)
                wr.write(data)
                written += len(data)
                if (written > SHARDSIZE):
                    print("shard too long, truncating")
                    break
                if (written == SHARDSIZE):
                    print("shard complete")
                    break
                if (len(data) == 0):
                    print("short shard, padding")
                    break
        else:
            print("whole shard missing, padding with 0xff")
                  
        # 0xff pad any remaining
        while (written < SHARDSIZE):
            data = b"\xff" * min(SHARDSIZE - written, 10*1024*1024)
            wr.write(data)
            written += len(data)

    # close it
    wr.close()
    
    # clean up
    for shard in dump.shards:
        if (shard is not None):
            print("Removing %s" % shard.fullname)
            os.remove(shard.fullname)
    
    # invoke the handler
    if (args.exec_done is not None):
        cmd = args.exec_done + " %s" % fname
        print("Invoking exec handler: %s" % cmd)
        os.system(cmd)
        
    

###
##  input scanning
#

def get_prefix(fname):
    # just strip "_000.bin"
    return os.path.basename(fname[:-8])


def build_dump_list(verbose):

    # find all the potential input files in the source path
    sglob = os.path.join(args.inpath, "*_0[01][0-9].bin")
    fnames = glob.glob(sglob)

    # early out if there's not matching files
    if (len(fnames) == 0):
        if (verbose):
            print("no shard files found")
        return []

    dumps = {}
    for fname in fnames:
        # find the name of the final output
        prefix = get_prefix(fname)

        # find / create the dump
        dump = dumps.setdefault(prefix, HBMDump(prefix))

        # add the filename
        dump.add_shard(fname)

    # just the list
    return list(dumps.values())


def process_dump(verbose, dump):

    if (verbose):
            print("examining dump '%s'" % dump.prefix)

    # first see if it's complete and we can roll it up
    if (dump.is_complete()):
        print("dump '%s' is complete, compressing" % dump.prefix)
        compress_dump(dump)
    elif (dump.is_timedout()):
        print("dump '%s' timed out, compressing" % dump.prefix)
        compress_dump(dump, True)
    else:
        # update status
        if (verbose):
            print("dump '%s' incomplete, leaving for next time" % dump.prefix)
    
        if (args.exec_progress):
            # progress % with the prefix
            pct = dump.incomplete_pct()
            cmd = args.exec_progress + " %s" % dump.prefix
            d = {"pct": pct}
            cmd = cmd.format(cmd, **d)
            os.system(cmd)
        

def scan_input(verbose):

    # generate the list of dumps
    dumps = build_dump_list(verbose)
    if (len(dumps) == 0):
        if (verbose):
            print("no dumps found")
        return

    # process them all
    for dump in dumps:
        process_dump(verbose, dump)

        
            

###
##  bot loop
#

def fork_scan(verbose):

    # synchronously execute a scan in a differe process so we can
    # avoid crashes due to built up state

    pid = os.fork()

    if (pid == 0):
        # child
        scan_input(verbose)
        sys.exit(0)
    else:
        os.waitpid(pid, 0)

COUNT_MAX = 300.0
def main_loop():

    # dump the full info on the first run
    verbose = True
    do_print = True
    count = 0

    while (True):
        if (do_print):
            print("Running a scan...")
        fork_scan(verbose)

        date = datetime.datetime.now()
        if (do_print):
            print("Sleeping for interval")
        time.sleep(args.interval)
        count += args.interval

        # only print occasionally
        verbose = args.verbose
        if (count > COUNT_MAX):
            count = 0
            do_print = True
        else:
            do_print = verbose
            
###
##  main
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Required positional argument
    parser.add_argument("inpath", help="Input shard path")
    parser.add_argument("outpath", help="Output concatenated path")
 
    parser.add_argument("-i", "--interval", action="store", default=10.0,
                        type=float, help="Poll Frequency")
    parser.add_argument("-o", "--once", action="store_true")
    parser.add_argument("-p", "--exec-progress", action="store", default=None)
    parser.add_argument("-e", "--exec-done", action="store", default=None)
    parser.add_argument("-C", "--cleanup", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
 
    args: argparse.Namespace = parser.parse_args()
    return args
 
def main() -> int:
    # parse arguments
    global args
    args = parse_args()

    if (args.once):
        r = scan_input(True)
    else:
        r = main_loop()
    
    return r

###
##  entrypoint
#
if __name__ == "__main__":
    r = main()
    sys.exit(r)
