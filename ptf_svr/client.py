#!/usr/bin/env python
#
#  client.py
#
#  Created by eddie.ruan@fungible.com on 2018 05-11
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#

import os
import logging
import unittest
import ptf
from ptf.base_tests import BaseTest
from ptf import config
import ptf.dataplane as dataplane
import ptf.testutils as testutils
from ptf.testutils import *
import time
import errno
import sys
import socket
import json
from util import *

#
# Testing client for ptf server
# This script would trigger following steps
# 1. Read from ptf_svr_test.json how to prepare testing packet
# 2. Create a testing packet and form an instruction json message
# 3. Set up socket connection with server and send createed instruction json message
# 4. Wait for response message in JSON back
#

#
# Test JSON file to provide Testing data
#
test_json_file = "ptf_svr_test.json"


#
# Create Testing packet and message
#
def create_send_data(sock):
    _path = os.path.dirname(os.path.realpath(__file__))
    full_path = _path + "/" + test_json_file
    jt_data = json.load(open(full_path))
    #print(jt_data)
    if "ptf_svr_test" not in jt_data:
        return False
    testarray = jt_data["ptf_svr_test"]
    for jdata in testarray:
        dst = jdata["dst"]
        src = jdata["src"]
        in_intf = jdata["in_intf"]
        out_intf = jdata["out_intf"]
        local_mac =  jdata["local_mac"]
        router_mac = jdata["router_mac"]
        pktlen=200
        print "Sending packet fpg "+str(in_intf)+" -> fpg "+str(out_intf)+" (" + src+" -> " + dst +")"
        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src=local_mac,
		                dl_vlan_enable=False,
		                vlan_vid=0,
		                vlan_pcp=0,
                                ip_dst=dst,
                                ip_src=src,
                                ip_id=105,
                                ip_ttl=64,
		                ip_dscp = 0,
                                pktlen=pktlen)
    
        pkt_data = pkt_encode(str(pkt))
        #
        # Format instruction JSON Message
        #
        ret = '{ "in_intf" : '+ str(in_intf) +', "out_intfs": ['+str(out_intf) + '], "pkt" : "' +str(pkt_data)+'"}'
        sock.sendall(ret)
        result = sock.recv(1024)
        returndata = json.loads(result)
        print ("Receive JSON Response : "+ str(returndata))
    return True

#
# Testing Main
#
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9000))
    ret = create_send_data(sock)
    if ret is False:
        sock.close()
        print("Can't get sending data")
        return
    sock.close()

if __name__ == "__main__":
    main()
