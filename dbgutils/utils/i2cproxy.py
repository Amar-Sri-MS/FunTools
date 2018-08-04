#!/usr/bin/env python

import sys, os
from array import array
import argparse
import threading
import time
import jsocket
import logging
import traceback
import signal
import socket
from socket import error as socket_error
from i2cutils import *

logger = logging.getLogger("jsocket.tserver")
logger.setLevel(logging.INFO)

logger = logging.getLogger("i2cproxy")
logger.setLevel(logging.INFO)

class constants(object):
    SERVER_TCP_PORT = 55668

class I2CServer(jsocket.ThreadedServer):
    def __init__(self):
        super(I2CServer, self).__init__()
        self.timeout = 2.0
        logger.warning("I2CServer init!")

    def _process_message(self, obj):
        """ virtual method """
        if obj != '': #Dummy implementation
            if obj['message'] == "new connection":
                logger.info("new connection.")

# class for i2c server thread
class I2CFactoryThread(jsocket.ServerFactoryThread):
    def __init__(self):
        super(I2CFactoryThread, self).__init__()
        self.timeout = 2.0
        self.i2c_handle = None
    def __del__(self):
        if self.i2c_handle is not None:
            logger.info("Closing i2c Connection!")
            i2c_disconnect(self.i2c_handle)
            self.i2c_handle = None
        logger.info("Destroyed i2c factory thread!");

    def _process_message(self, obj):
        """ virtual method - Implementer must define protocol """
        logger.debug(("New thread process message!!!! pid: {0}"
               " thread: {1}").format(os.getpid(), threading.current_thread()))
        if obj != '':
            logger.info(obj)
            cmd = obj.get("cmd", None)
            if cmd == "CONNECT":
		connect_args = obj.get("args", None)
		if not connect_args:
		    self.send_obj({"STATUS":[False, "Invalid connect args!"]})
		    return
		dev_id = connect_args.get("dev_id", None)
		if not dev_id:
		    self.send_obj({"STATUS":[False, ("Invalid connect args."
			" dev_id is missing!")]})
		    return
                logger.info("Connection Request to dev_id: {0}".format(dev_id))
                if self.i2c_handle is not None:
                    logger.info("Already connected! closing it!")
                    i2c_disconnect(self.i2c_handle)
                    self.i2c_handle = None
                try:
                    (status, value) = i2c_connect(dev_id)
                    if status is True:
                        self.i2c_handle = value
                        self.send_obj({"STATUS":[True, "i2c device is ready!"]})
                        logger.info('i2c device connection is ready!')
                    else:
                        self.i2c_handle = None
                        error_str = value
                        self.send_obj({"STATUS":[False, error_str]})
                        return
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif cmd == "CSR_PEEK":
                if self.i2c_handle is None:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                try:
                    csr_peek_args = obj.get("args", None)
                    if not csr_peek_args:
                        self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                        return
                    csr_addr = csr_peek_args.get("csr_addr", None)
                    csr_width_words = csr_peek_args.get("csr_width", None)
                    if not csr_addr or not csr_width_words:
                        self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                        return
                    logger.debug("csr_addr: {0} csr_width_words:{1}".format(csr_addr,
                                 csr_width_words))
                    try:
                        word_array = i2c_csr_peek(self.i2c_handle, csr_addr, csr_width_words)
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        self.send_obj({"STATUS":[False, "Exception!"]})
                        return
                    logger.debug("Peeked words: {0}".format(word_array))
                    if word_array is not None:
                        self.send_obj({"STATUS":[True, "peek success!"],
                                "DATA":word_array})
                    else:
                        self.send_obj({"STATUS":[False, "peek fail!"],
                                "DATA":word_array})
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif cmd == "CSR_POKE":
                csr_poke_args = obj.get("args", None)
                if not csr_poke_args:
                    self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    return
                if self.i2c_handle is None:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                csr_addr = csr_poke_args.get("csr_addr", None)
                csr_width_words = csr_poke_args.get("csr_width", None)
                word_array = csr_poke_args.get("csr_val", None)
                if not csr_addr or not csr_width_words or not word_array:
                    self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                    return
                logger.debug(("csr_addr: {0} csr_width_words:{1}"
                       " word_array:{2}").format(csr_addr, csr_width_words,
                                                 word_array))
                status = i2c_csr_poke(self.i2c_handle, csr_addr, csr_width_words, word_array)
                self.send_obj({"STATUS":[status, "OK!" if status else "i2c csr error!"]})
            elif cmd == "DISCONNECT":
                if self.i2c_handle is not None:
                    i2c_disconnect(self.i2c_handle)
                    self.send_obj({"STATUS":[True, "I2c is disconnected"]})
                else:
                    self.send_obj({"STATUS":[True, "I2c is already disconnected"]})
                self.i2c_handle = None
            else:
                logger.debug("Invalid msg!")
                self.send_obj({"STATUS":[False, "Invalid message!"]})

if __name__ == "__main__":
    server = None
    def signal_handler(signal, frame):
        # close the socket here
        if server is not None:
            logger.info(("Stopping the server!!!! pid: {0}"
                   " thread: {1}").format(os.getpid(),
                   threading.current_thread()))
            server.stop()
            server.close()
            server.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler) #Terminate cleanly on ctrl+c

    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', nargs='?', type=str,
                        help="ip address of server")
    args = parser.parse_args()
    if args.ip_addr is None:
        ip_addr = socket.gethostbyname(socket.gethostname())
    else:
        ip_addr = args.ip_addr[0]

    try:
        socket.inet_aton(ip_addr) #Validates the ip address
    except socket_error:
        logger.debug("Invalid ip address! {0}".format(socket_error))
        sys.exit(1)

    server = jsocket.ServerFactory(I2CFactoryThread, address=ip_addr,
                                   port = constants.SERVER_TCP_PORT)
    server.timeout = 2.0
    logger.info("Starting the server IP:{0} PORT:{1}".format(ip_addr,
                                            constants.SERVER_TCP_PORT))
    server.start()

    # Let the main thread stay alive and recieve contl+c
    while True:
        logger.debug(("Running server!!!! pid:{0} thread:{1}").format(os.getpid(),
                threading.current_thread()))
        server.join(600)
        if not server.isAlive():
            break


