#!/usr/bin/env python2.7
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
import time
import threading
from threading import Thread

intf_json_file = "intf_map.json"
#
# Receive a message in json format from client, send raw packet based on
# the instructions to PTF connected ports.
#
def send_rcvd_pkt_to_ptf(self, jdata):
        intf = jdata["intf"]
        in_intf, err = get_ptf_port_from_intf_name(self.intf_jt_data, intf)
        if err:
                message = "\nFailed to get ptf port for " + intf
                print(message)
                logging.debug(message)
                return
        
        pkt = Ether(pkt_decode(jdata["pkt"]))
        print ("\nReceiving Pkt from Client and send to port " + str(in_intf)+ " :\n " + str(inspect_packet(pkt)))

        try:            
            logging.debug(inspect_packet(pkt))
            send_packet(self, in_intf, str(pkt))
        finally:
            logging.debug("Send cleint packet done to port " + str(in_intf))

#
# Receive packets from ptf and send back to client via socket connection
#
def send_received_pkt_to_client(self, sock, pkt, intf):
        #
        # Form response message
        #
        intf_str, err = get_intf_name_from_ptf_port(self.intf_jt_data, intf)
        if (err):
                message = "\nFailed to get intf name for ptf port"+str(intf)
                print(message)
                logging.debug(message)
                return
        ret = '{ "intf" : "'+intf_str +'"'
        ret = ret + ', "pkt":"' + pkt_encode(str(pkt)) + '"}'
        #print(ret)
        sock.sendall(ret)
        logging.debug("Sent response %r to client", ret)        
#
# Poll data from all port and send received packets via socket
#
def poll_data_from_all_ports(self, socket):
    device_number = 0
    try:
        logging.debug("\n=====================\n")
        result = dp_poll(self, device_number=device_number, timeout=2)
        if isinstance(result, self.dataplane.PollSuccess):
                message = "Successfuled get packet at port "+str(result.port)
                rcv_pkt = Ether(result.packet)
                logging.debug("\n\nReceived Packet::\n")
                logging.debug(inspect_packet(rcv_pkt))
                print("\nReceive packets from PTF : \n"+ str(inspect_packet(rcv_pkt)))
                send_received_pkt_to_client(self, socket, rcv_pkt, result.port)
    finally:
        logging.debug("End of one poll")

#
# Launching polling thread
#
class PollingThread(threading.Thread):
        def __init__(self, ptf_self, socket):
                self._stopevent = threading.Event()
                self._socket = socket
                self._ptf_self = ptf_self
                threading.Thread.__init__(self)
        def run(self):
                while not self._stopevent.isSet():
                      poll_data_from_all_ports(self._ptf_self, self._socket)
        def join(self, timeout=None):
                self._stopevent.set()
                threading.Thread.join(self, timeout)
                
#
# Handle socket connection
#
def recv_all(sock):
    sock.setblocking(0)
    total_data=''
    data=''
    while 1:
        try:
            data = sock.recv(16*1024)
            total_data = total_data + data
            print("DEBUGME: total " + total_data)
            if data.find("}") != -1:
                break
            
            time.sleep(0.1)
        except:
            pass

    return total_data


def handle(self, connection, address):
    logger = logging.getLogger("process-%r" % (address,))
    pollthread = PollingThread(self, connection)
    pollthread.start()
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            logger.debug("Wait for data")
            data = recv_all(connection)
            if data == "":
                message = "\nSocket is closed remotely"
                print(message)
                logger.debug(message)
                break
        
            print("Get data : " + data)
            logger.debug("Get data from client socket: " + data)
            jdata = json.loads(data)
            try:
                send_rcvd_pkt_to_ptf(self, jdata)
            except:
                logger.debug("Send rcvd pkt failed")
    except:
        logger.exception("Hit some problem in handling requests")
    finally:
        pollthread.join()
        print("Stopped polling thread")
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
        _path = os.path.dirname(os.path.realpath(__file__))
        full_path = _path + "/" + intf_json_file
        self.intf_jt_data = json.load(open(full_path))
        print("Reading intf map :  "+full_path)
        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            handle(self, conn, address)

    def _runTest(self, pktlen=200, dscp=0, cos=0, expdscp=0):
        logging.basicConfig(level=logging.DEBUG)
        print("\nStart test : " + self.host_name + " port " + str(self.port))
        try:
            logging.info("Listening on " + str(self.port))
            print ("\nStart main execution Loop : ")
            self._start_loop()
        except:
            logging.exception("Unexpected exception")
        finally:
            logging.info("Shutting down")
        logging.info("All done")

#
# Dummy test case for using PTF 
#
@group('ptf')
class PTFTest(PTFSVRBase):
    def runTest(self):
        PTFSVRBase._set_up_bind_info(self, "0.0.0.0", 9001)
        PTFSVRBase._runTest(self, pktlen=200)
