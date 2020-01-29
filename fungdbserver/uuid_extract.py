#!/usr/bin/python

###
##  Generic utility for reading UUID of binaries on macOS or Linux.
##  macOS ld stamps every binary, for gnu ld you need --build-id=uuid
#

import subprocess
import optparse
import uuid
import sys
import re
import os

###
##  Print if we're verbose
#
VERBOSITY = 0

def VPRINT(msg, minlevel=1):
    if (VERBOSITY >= minlevel):
        print(msg)

###
##  Helpers
#

READELF_PATHS = [
    "/opt/cross/mips64/bin/mips64-unknown-elf-readelf",
    "/Users/Shared/cross/mips64/bin/mips64-unknown-elf-readelf",
    "/project/tools/cross/mips64/bin/mips64-unknown-elf-readelf",
    "/usr/bin/readelf",
]

def find_default_readelf():
    for path in READELF_PATHS:
        if (os.path.exists(path)):
            return path

    # shot in the dark
    return "readelf"

READELF = find_default_readelf()

def output4command(cmd):
    VPRINT("running command '%s'" % cmd)
    # use Popen because python2.6
    output = str(subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]).strip()
    VPRINT("results are '%s'" % output)

    return output

###
##  main functionality
#

def extract_regex(output, pattern, linkmsg = ""):

    m = re.search(pattern, output)

    if (m is None):
        # no match -- possibly an ELF binary without the right linker
        # flags
        print("Failed to find UUID in output.%s" % linkmsg)
        print(output)

        return None

    # return a parsed version of the match
    u = uuid.UUID(m.group(1))

    return u

# given output from "file a.out", extract the UUID
def extract_file_uuid(output):

    return extract_regex(output, "BuildID\[md5\/uuid\]=([a-fA-F0-9\-]+),", " Check linker settings?")

# given output from "readelf -n a.out", extract the UUID
def extract_readelf_uuid(output):

    return extract_regex(output, "Build ID: ([a-fA-F0-9\-]+)", " Check linker settings?")

# attempt to extract the UUID from a macho file
def extract_macho_uuid(fname, output):

    # don't try the macho tools unless it looks like a macho
    if (": Mach-O " not in output):
        print("File does not appear to be ELF or Mach-O")
        return None

    # run another command
    cmd = ["dwarfdump", "--uuid", fname]
    output = output4command(cmd)

    return extract_regex(output, "UUID: ([a-fA-F0-9\-]+) ")

# top-level function
def uuid_extract(fname, readelf=None):

    # our final result
    u = None

    # fixup for external callers
    if (readelf is not None):
        global READELF
        READELF = readelf

    # run a shell command and get the output
    cmd = ["file", fname]
    output = output4command(cmd)

    # check if it's an ELF file
    if (": ELF " in output):
        # run a readelf command becasue we can't rely on "file" on Centos boxes
        cmd = [READELF, "-n", fname]
        output = output4command(cmd)
        u = extract_readelf_uuid(output)
    else:
        # only try to extract macho on darwin
        if (os.uname()[0] == "Darwin"):
            u = extract_macho_uuid(fname, output)
        else:
            print("File does not appear to be ELF")

    return u

###
##  Argument parsing
#

def parse_args():

    global VERBOSITY
    global READELF

    usage = "usage: %prog filename"
    parser = optparse.OptionParser(description='Executable file UUID extractor',
                                   usage=usage)

    parser.add_option("-V", "--verbose", action="count", dest="verbosity",
                      help="Extra debug output")

    parser.add_option("-r", "--readelf", action="store", default=READELF,
                      help="Location of a modern 64b compatible readelf binary")

    # Do the parse
    (opts, args) = parser.parse_args()

    if (len(args) != 1):
        parser.error("Must specify a filename")


    VERBOSITY = opts.verbosity
    READELF = opts.readelf

    return (opts, args)

###
##  Entrypoint
#

if (__name__ == "__main__"):

    # parse command-line args
    (opts, args) = parse_args()

    # read the one argument
    u = uuid_extract(args[0])

    if (u is not None):
        print(u)
        sys.exit(0)
    else:
        sys.exit(1)
