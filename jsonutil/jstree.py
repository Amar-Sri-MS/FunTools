#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pretty-print json as a tree
"""


import os
import sys
import json
import argparse
import subprocess

DEFAULT_SDK = os.environ.get("SDKDIR",
                             os.environ.get("WORKSPACE",
                                            os.path.dirname(sys.argv[0]) + "/../..") + "/FunSDK")

###
##  output
#

def get_indent(s, dangling=False):
    if (dangling):
        return ""
    return "\t" * s + " - "


def print_dict_node(args, js, depth):

    ks = list(js.keys())
    ks.sort()
    for (i, k) in enumerate(ks):
        if (i > args.nelem):
            print("%s... %d total elements" % (get_indent(depth), len(ks)))
            break
            
        print("%s%s: " % (get_indent(depth), k) , end="")
        print_node(args, js[k], depth+1, dangling=True)

def print_list_node(args, js, depth):
    for (i, j) in enumerate(js):
        if (i > args.nelem):
            print("%s... %d total elements" % (get_indent(depth), len(js)))
            break

        print("%s[%d]: " % (get_indent(depth), i), end="")
        print_node(args, j, depth+1, dangling=True)
       
    
def print_node(args, js, depth, dangling=False):

    if (depth > args.depth):
        js = "..."
        
    if (isinstance(js, dict)):
        if (dangling):
            print("")
        print_dict_node(args, js, depth)
    elif (isinstance(js, list)):
        if (dangling):
            print("")
        print_list_node(args, js, depth)
    else:
        print("%s%s" % (get_indent(depth, dangling), js))
        
    

###
##  main
#
def parse_args():
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("file", help="Input file name")

    # output depth
    parser.add_argument("-d", "--depth", action="store",
                        type=int, dest="depth", default=3)
    
    # input binary
    parser.add_argument("-b", "--binary", action="store_true",
                        dest="binary", default=False)

    # maximum numer of elements
    parser.add_argument("-n", "--num-elements", action="store",
                        type=int, dest="nelem", default=10)
    
    # output depth
    parser.add_argument("-S", "--sdk", action="store",
                        dest="sdkdir", default=DEFAULT_SDK)

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    #print("file {}, depth {}".format(args.file, args.depth))

    if (args.binary):
        itype = "-I"
    else:
        itype = "-i"

    # read the code as a string
    jsonutil = os.path.join(args.sdkdir, "bin",
                             os.uname()[0], os.uname()[4], "jsonutil")
    subargs = [jsonutil, itype, args.file]
    # print(subargs)
    try:
        p = subprocess.Popen(subargs,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        print("OSError Exception executing %s" % subargs)
        sys.exit(1)
    (stdout, stderr) = p.communicate()

    js = json.loads(stdout)

    print_node(args, js, 0)
    
###
##  entrypoint
#
if __name__ == "__main__":
    main()

