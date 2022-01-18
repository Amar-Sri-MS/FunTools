#!/usr/bin/env python2.7
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
import threading
from threading import Thread

#
# Testing client for ptf server
# This script would trigger following steps
# 1. Read from ptf_svr_test.json how to prepare testing packets
# 2. Set up socket connection with server and launching a receiving thread for getting messages
# 3. Send out testing packets
# 4. Hold on process for receiving thread testing.
#

#
# Test JSON file to provide Testing data
#
test_json_file = "ptf_svr_test.json"

#
# Receiving handling in receiving thread
#
def rcv_packets_from_server(self, sock):
    try:
        result = sock.recv(16*1024)
        if result == "":
            print("socket closed remotely at server side")
            self.join()
            return
        returndata = json.loads(result)
        print ("Receive JSON Response : "+ str(returndata))
    except(socket.timeout):
        pass
   
class RcvThread(threading.Thread):
        def __init__(self, socket):
                self._stopevent = threading.Event()
                self._socket = socket
                threading.Thread.__init__(self)
        def run(self):
                while not self._stopevent.isSet():
                      rcv_packets_from_server(self, self._socket)
        def join(self, timeout=None):
                self._stopevent.set()
                #threading.Thread.join(self, timeout)

#
# Create Testing packets and send out them one by one
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
        local_mac =  jdata["local_mac"]
        router_mac = jdata["router_mac"]
        pktlen=200
        print "Sending packet "+str(in_intf)+" (" + src+" -> " + dst +")"
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
        ret = '{ "intf" : "'+ str(in_intf) + '", "pkt" : "' +str(pkt_data)+'"}'
        print("Sending data : "+ret)
        sock.sendall(ret)
        #Sleep to make sure message is out
        time.sleep(0.5)
    return True

#
# Testing Main
#
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9001))
    sock.settimeout(0.5)
    #
    # Start receving thread
    #
    rcvthread = RcvThread(sock)
    rcvthread.start()

    #
    # Send testing packets once
    #
    ret = create_send_data(sock)

    #
    # Hold on process for receiving thread
    #
    while rcvthread.isAlive():
        try:
            #print("rcvthread is alive")
            time.sleep(5.0)
        except KeyboardInterrupt:
            sock.close()
            print("Send kill ...")
            rcvthread.join()
            time.sleep(1.0)
            return

    # End of client
    sock.close()

if __name__ == "__main__":
    main()
