#!/usr/bin/env python
#
#  ptf_test.py
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
# Receive a message in json format from client, send raw packet based on
# the instructions in json to PTF connected port.
# Wait for 2 min for capturing packets from the given port, then
# send received packets back to client in response json format
#
def send_rcv_pkt(self, jdata):
        in_intf = jdata["in_intf"]
        out_intf = jdata["out_intfs"][0]
        pkt = Ether(pkt_decode(jdata["pkt"]))
        print ("\nReceiving Pkt from Client :\n " + str(inspect_packet(pkt)))

        rcv_pkt=""
        err = True
        message="Unchanged"
        try:            
            logging.debug(inspect_packet(pkt))
            send_packet(self, in_intf, str(pkt))
            logging.debug("\n=====================\n")
            device_number = 0
            result = dp_poll(self, device_number=device_number,
                             port_number=out_intf,
                             timeout=2)
            if isinstance(result, self.dataplane.PollFailure):
                message = "Failed to get receiving packet at port "+str(out_intf) + str(result.format())
                logging.debug(message)
            else:
                message = "Successfuled get packet at port "+str(out_intf)
                rcv_pkt = Ether(result.packet)
                logging.debug("\n\nReceived Packet::\n")
                logging.debug(inspect_packet(pkt))
                print("\nReceive packets from PTF : \n"+inspect_packet(pkt))
                err = False

        finally:
            logging.debug("Test done")

        return message, rcv_pkt, err

#
# Handle socket connection
#
def handle(self, connection, address):
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
        
            #print("Get data : " + data)
            jdata = json.loads(data)
            err = True
            pkt = ""

            try:
                ret_message, pkt, err = send_rcv_pkt(self, jdata)
            except:
                logger.debug("Send rcv pkt failed")
                ret_message = "Rcv pkt failed"
                err = True

            #
            # Form response message
            #
            ret = '{ "message" : "'+ret_message+'", "error" :"'+str(err) +'"'
            if err:
                ret = ret +'}'
            else:
                ret = ret + ', "pkt":"' + pkt_encode(str(pkt)) + '"}'
            #print(ret)
            connection.sendall(ret)
            logger.debug("Sent response %r", ret)
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

#
# PTF SVR Base class based on PTF
#
class PTFSVRBase(BaseTest):
    host_name = ""
    port = 0
    def setUp(self):
        BaseTest.setUp(self)
        test_params = testutils.test_params_get()
        self.dataplane = ptf.dataplane_instance
        if self.dataplane != None:
            self.dataplane.flush()
            if config["log_dir"] != None:
                filename = os.path.join(config["log_dir"], str(self)) + ".pcap"
                self.dataplane.start_pcap(filename)
        return

    def tearDown(self):
        if config["log_dir"] != None:
            self.dataplane.stop_pcap()
        testutils.reset_filters()        
        BaseTest.tearDown(self)

    def _set_up_bind_info(self, hostname, port):
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def _start_loop(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            handle(self, conn, address)

    def _runTest(self, pktlen=200, dscp=0, cos=0, expdscp=0):
        logging.basicConfig(level=logging.DEBUG)
        print("\nStart test : " + self.host_name + " port " + str(self.port))
        try:
            logging.info("Listening on " + str(self.port))
            print ("\nStart Loop : ")
            self._start_loop()
        except:
            logging.exception("Unexpected exception")
        finally:
            logging.info("Shutting down")
            for process in multiprocessing.active_children():
                logging.info("Shutting down process %r", process)
                process.terminate()
                process.join()
        logging.info("All done")

#
# Dummy test case for using PTF 
#
@group('ptf')
class PTFTest(PTFSVRBase):
    def runTest(self):
        PTFSVRBase._set_up_bind_info(self, "0.0.0.0", 9000)
        PTFSVRBase._runTest(self, pktlen=200)
