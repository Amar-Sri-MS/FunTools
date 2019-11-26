#!/usr/bin/env python
from __future__ import print_function

import os
import sys

from SimpleXMLRPCServer import SimpleXMLRPCServer

import subprocess
import logging
import time

from i2cutils import *

class DEFAULTS:
    I2CPROXY_SERVER = '10.1.20.69'
    I2CPROXY_PORT   = 60444

try:
    basestring
except NameError:   # Python 3
    basestring = str

FORMAT = "%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('s1emu')

class remoteException(Exception):
    pass

class ProxyLibrary(object):
    def __init__(self, server=DEFAULTS.I2CPROXY_SERVER, port=DEFAULTS.I2CPROXY_PORT):
        self.server = server
        self.port = port
        logger.info("initialize server=%s at port=%s" % (self.server, self.port))
        self.i2cprobe = None

    def connect(self, serial, ip_addr, addr, args='abc'):
        logger.debug('instantiating s1 csr2 probe ...')
        self.i2cprobe = s1i2c(int(serial), addr)
        (status, status_msg) = self.i2cprobe.i2c_connect()
        if not status:
            self.i2cprobe = None
            raise Exception("s1-i2c-probe connect failed: status_msg={} ...".format(status_msg))
        return (True, "CSR connect is success! {} {} {} {}".format(serial, ip_addr, addr, args))

    def csr_rawpeek(self, regadr, reglen):
        print('\nregadr={} reglen={}'.format(hex(regadr), hex(reglen)))
        status, word_array = self.i2cprobe.local_csr_peek(regadr, reglen)
        if not status:
            raise Exception("peek failed")
        return (True, map(hex, word_array) if word_array else None)

    def csr_rawpoke(self, regadr, regval):
        print('\nregadr={} regval={}'.format(hex(regadr), map(int, regval)))
        status = self.i2cprobe.local_csr_poke(regadr, map(int, regval))
        if not status:
            raise Exception("poke failed")
        return (True, None)

if __name__ == '__main__':
    # A simple server with simple api between server and client functions
    server = SimpleXMLRPCServer((DEFAULTS.I2CPROXY_SERVER, DEFAULTS.I2CPROXY_PORT))
    proxy = ProxyLibrary()
    server.register_function(proxy.connect, 'connect')
    server.register_function(proxy.csr_rawpeek, 'peek')
    server.register_function(proxy.csr_rawpoke, 'poke')
    server.serve_forever()
