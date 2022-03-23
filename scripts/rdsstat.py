#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
display real-time RDS statistics

static check:
% mypy funtail
"""
import os
import sys
import argparse
import time
import json
import socket

## add some default locations to find dpc_client
OSNAME = os.uname()[0]
SCRIPTDIR = os.path.dirname(sys.argv[0])
SDKDIR = os.environ.get("SDKDIR",
                        os.environ.get("WORKSPACE",
                                       SCRIPTDIR + "/../..") + "/FunSDK")
sys.path.append(os.path.join(SCRIPTDIR, "../dcpsh"))
sys.path.append(os.path.join(SDKDIR, "bin", OSNAME))
sys.path.append("/opt/fungible/FunSDK/bin/Linux/") ## demo rootfs
sys.path.append("/usr/bin") ## demo rootfs

import dpc_client


###
##  vpusage grid
#

BARS = "▁▂▃▄▅▆▇█"

def getutil(r, o, v):

    cname = "core_%s" % o
    vpname = "vp_%s" % v

    u = r.get(cname, {}).get(vpname, None)
    if (u is None):
        return ' '

    n = u["usage_percent"]
    p = 100.0 / (len(BARS) - 1)
    
    c = BARS[int(n/p)]
    
    return c

def mkcore(r, o):

    return "%s%s%s%s" % (getutil(r, o, 0),
                         getutil(r, o, 1),
                         getutil(r, o, 2),
                         getutil(r, o, 3))

def mkrow(row, key, r, c):

    return "%s: %s-%s-%s-%s-%s-%s   %s%%\n" % (row,
                                               mkcore(r, 0), mkcore(r, 1),
                                               mkcore(r, 2), mkcore(r, 3),
                                               mkcore(r, 4), mkcore(r, 5),
                                               c[key]['usage_percent'])

def mkgrid(d):

    s = ""
    
    # dictionary of clusters
    vpu = d["vp_usage"]
    cu = d["cluster_usage"]

    keys = sorted(cu.keys())
    for key in keys[:-1]:
        s += mkrow(key, key, vpu.get(key, {}), cu)
    key = keys[-1]
    s += mkrow("control  ", key, vpu.get(key, {}), cu)

    return s

###
##  volume info
#

def mkvolinfo(d):

    stats = d.get("stats")
    if (d is None):
        s = "<no stats>"
    else:
        s = "rd bytes %s, wr bytes %s" % (stats["read_bytes"],
                                          stats["write_bytes"])

    keys = sorted(d.keys())
    if (len(keys) == 1):
        keys = ["compress", "uncompress"]
    
    for key in keys:
        if (key == "stats"):
            continue

        iops = "<unknown>"
        byts = "<unknown>"
        lat = "<unknown>"

        # extract values
        for k in list(d.get(key, {}).keys()):
            if (k.endswith("_iops")):
                iops = d.get(key, {}).get(k)
                continue
            if (k.endswith("_bytes")):
                byts = d.get(key, {}).get(k)
                continue
            if (k.endswith("_avg_latency")):
                lat = d.get(key, {}).get(k)
                continue
        
        s += "\n%s: iops %s, bytes %s, avg. latency %s" % (key,
                                                           iops, byts, lat)
    
    return s

###
##  namespaces
#

def find_all_nsids(d):

    ls = []

    # ignore error case
    if (d is None):
        return []
    
    # terminal
    if ("name_spaces" in d):
        r = []
        dflt_uuid = d.get("contoller UUID", "<unknown>")
        for ns in d["name_spaces"]:
            UUID = ns.get('UUID', dflt_uuid)
            if (UUID == ''):
                UUID = dflt_uuid
             
            rcrc = ns.get('reads_crc', ns.get('reads', "<unknown>"))
            wcrc = ns.get('writes_crc', ns.get('writes', "<unknown>"))
            r.append({'UUID':UUID, 'rcrc':rcrc, 'wcrc':wcrc})

        return r

    # recursive case
    keys = sorted(d.keys())
    for key in keys:
        ls += find_all_nsids(d.get(key))

    return ls

###
##  main
#

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
  
    # dpc host / socket name
    parser.add_argument("-a", "--dpcaddress", help="dpc proxy hostname")
  
    # dpc TCP port
    parser.add_argument("-D", "--dpcport", action="store", type=int)

    # use a unix socket
    parser.add_argument("-u", "--unix", action="store_true", default=False)

    # show nvme
    parser.add_argument("-n", "--nvme", action="store_true", default=False)

    args: argparse.Namespace = parser.parse_args()
    return args
  
def main() -> int:
    args: argparse.Namespace = parse_args()

    # work out the args
    if (args.unix):
        addr = args.dpcaddress
    elif (args.dpcaddress is not None):
        addr = (args.dpcaddress, args.dpcport)
    else:
        raise RuntimeError("unspecified dpc connection")
    

    # construct the dpc client
    conn = dpc_client.DpcClient(legacy_ok=False,
                                unix_sock = args.unix,
                                server_address = addr)

    while (True):
        # get the latest stats
        d = conn.execute("peek", ["stats/funtop"]) 

        s = mkgrid(d)

        # clear the screen
        print("\033[2J")
        print("\033[0;0H")

        # VP usage
        print("VP Usage:")
        print(s)

        # print volumes
        d = None
        try:
            d = conn.execute("peek", ["storage/volumes/VOL_TYPE_BLK_RDS"])
        except:
            pass

        print()
        if (d is None):
            print("<no rds volumes found>")
        else:
            print("RDS Volumes:")
            keys = sorted(d.keys())
            for key in keys:
                volinfo = mkvolinfo(d[key])
                volinfo = volinfo.replace("\n", "\n\t\t")
                print("\t%s: %s" % (key, volinfo))


        # print nvme
        if (args.nvme):
            d = None
            try:
                d = conn.execute("peek", ["storage/ctrlr/nvme"])
            except:
                pass

            print()
            if (d is None):
                print("<no nvme found>")
            else:
                print("Controller NVME:")
                ls = find_all_nsids(d)
                if (len(ls) == 0):
                    print("\t<no namespaces found>")
                else:
                    for l in ls:
                        print("\t%s: reads_crc %s, writes_crc %s" %
                              (l.get("UUID"), l.get("rcrc"), l.get("wcrc")))
                
        # wait for next
        time.sleep(1.0)
        
    return 0
 
###
## entrypoint
#
if __name__ == "__main__":
    main()
        
