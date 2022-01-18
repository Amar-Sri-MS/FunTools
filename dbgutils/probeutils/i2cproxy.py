#!/usr/bin/env python2.7

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
import atexit
from socket import error as socket_error
from i2cutils import *
import functools

logger = logging.getLogger("jsocket.tserver")
logger.setLevel(logging.INFO)

logger = logging.getLogger("i2cproxy")
logger.setLevel(logging.INFO)

class constants(object):
    SERVER_TCP_PORT = 44444

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error('Caught an exception in {0}'.format(f.__name__))
            logger.error(traceback.format_exc())
    return func

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class i2c_obj_db:
    def __init__(self):
        logger.info('Creating i2c object db!')
        self.i2c_objs = dict()

    def add_i2c_conn(self, dev_id, i2c_conn, user):
        if self.find(dev_id):
            logger.error('Already there is connection by {0}'
                ' for dev_id: {1}'.format(user, dev_id))
            return False
        self.i2c_objs[dev_id] = (i2c_conn, user)
        return True

    def find(self, dev_id):
        if not dev_id:
            logger.error('Invalid dev_id(Null)!')
            return False
        i2c_obj = self.i2c_objs.get(dev_id, None)
        if i2c_obj is not None:
            return True
        return False

    def del_i2c_conn(self, dev_id):
        if not dev_id:
            logger.error('Invalid dev_id(Null)!')
            return None
        if not self.find(dev_id):
            logger.error('There is no i2c connecition'
                ' for dev_id: {0}'.format(dev_id))
            return False
        self.i2c_objs.pop(dev_id)
        return True

    def get_i2c_conn(self, dev_id):
        if not dev_id:
            logger.error('Invalid dev_id(Null)!')
            return None
        i2c_obj = self.i2c_objs.get(dev_id, None)
        if i2c_obj:
            return i2c_obj[0]
        return None

    def dump(self):
        for k,v in self.i2c_objs.items():
            print('Dev: {0} User: {1} Conn_obj: {2}'.format(k, v[1], v[0]))


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
    def _close_connection(self):
        """ virtual method """
        logger.info("virtual method _close_connection")

# class for i2c server thread
class I2CFactoryThread(jsocket.ServerFactoryThread):
    i2c_dev_id = None
    def __init__(self):
        super(I2CFactoryThread, self).__init__()
        self.timeout = 2.0

    #def __del__(self):
    #    logger.info("Destroyed i2c factory thread!");
    #    self.close()

    def exit(self):
        logger.info('Exit {0}!'.format(threading.current_thread()))
        self.close()

    def __cleanup__(self):
        if self.i2c_dev_id is not None:
            logger.info('Cleaning up connection to {0}!'.format(self.i2c_dev_id))
            i2c_conn = i2c_obj_db().get_i2c_conn(self.i2c_dev_id)
            if i2c_conn:
                logger.info("Closing i2c Connection!")
                i2c_conn.i2c_disconnect()
                i2c_obj_db().del_i2c_conn(self.i2c_dev_id)
                self.i2c_dev_id = None
            else:
                logger.error('Un-expected condition(i2c_dev_id != None && i2c_conn == None)!')

    @catch_exception
    def _close_connection(self):
        logger.debug(("thread process close connection!!!! pid: {0}"
               " thread: {1}").format(os.getpid(), threading.current_thread()))
        self.__cleanup__()

    @catch_exception
    def _process_message(self, obj):
        """ virtual method - Implementer must define protocol """
        logger.debug(("Thread process message!!!! pid: {0}"
               " thread: {1}").format(os.getpid(), threading.current_thread()))
        if obj != '':
            logger.debug(obj)
            cmd = obj.get("cmd", None)
            if cmd == "CONNECT":
                connect_args = obj.get("args", None)
                if not connect_args:
                    self.send_obj({"STATUS":[False, "Invalid connect args!"]})
                    return
                logger.debug('connect args: {0}'.format(connect_args))
                dev_id = connect_args.get("dev_id", None)
                if not dev_id:
                    self.send_obj({"STATUS":[False, ("Invalid connect args. dev_id is missing!")]})
                    return
                user = connect_args.get("user", None)
                if not user:
                    self.send_obj({"STATUS":[False, ("Invalid connect args. user id is missing!")]})
                    return
                slave_addr = connect_args.get("slave_addr", None)
                if not slave_addr:
                    self.send_obj({"STATUS":[False, ("Invalid connect args. slave_addr is missing!")]})
                    return
                force_connect = connect_args.get("force_connect", None)
                chip_type = connect_args.get("chip_type", 'f1')
                bitrate = connect_args.get("i2c_bitrate", 500)

                logger.info('**** Connection request to dev_id: {0}'
                            ' slave_addr: {1} from user:"{2}"'.format(dev_id,
                                                    hex(slave_addr), user))
                if force_connect:
                    logger.info('Force connect request by {0} to dev_id: {1}'.format(user, dev_id))
                    i2c_obj_db().dump()
                i2c_conn = i2c_obj_db().get_i2c_conn(dev_id)
                if i2c_conn:
                    if force_connect:
                        logger.info("Already connected! closing it!")
                        i2c_conn.i2c_disconnect()
                        i2c_obj_db().del_i2c_conn(dev_id)
                        self.i2c_dev_id = None
                    else:
                        err_msg = ('i2c device:{0} is already connected'
                              ' by "{1}"').format(dev_id, user)
                        logger.error(err_msg)
                        self.send_obj({"STATUS":[False, err_msg]})
                try:
                    i2c_conn = self.create_i2c(chip_type, dev_id, slave_addr, bitrate)
                    (status, status_msg) = i2c_conn.i2c_connect()
                    if status is True:
                        self.i2c_dev_id = dev_id
                        i2c_obj_db().add_i2c_conn(dev_id, i2c_conn, user)
                        logger.info('i2c device connection is ready!')
                        self.send_obj({"STATUS":[True, "i2c device is ready!"]})
                    else:
                        self.i2c_dev_id = None
                        error_str = status_msg
                        self.send_obj({"STATUS":[False, error_str]})
                    return
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif cmd == "CSR_PEEK":
                print self.i2c_dev_id
                i2c_conn = i2c_obj_db().get_i2c_conn(self.i2c_dev_id)
                if not i2c_conn:
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
                        (data, status) = i2c_conn.i2c_csr_peek(csr_addr = csr_addr,
                                                           csr_width_words = csr_width_words)
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        self.send_obj({"STATUS":[False, "Exception!"]})
                        return
                    logger.debug("Peeked words: {0}".format(data))
                    if data is not None:
                        self.send_obj({"STATUS":[True, "peek success!"],
                                "DATA":data})
                    else:
                        self.send_obj({"STATUS":[False, "peek fail!"
                                                 "Error:{0}".format(status)],
                                "DATA":data})
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif cmd == "CSR_POKE":
                csr_poke_args = obj.get("args", None)
                if not csr_poke_args:
                    self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    return
                fast_poke = csr_poke_args.get("fast_poke", False)
                csr_addr = csr_poke_args.get("csr_addr", None)
                word_array = csr_poke_args.get("csr_val", None)
                if not csr_addr or not word_array:
                    if not fast_poke:
                        self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    else:
                        logger.error('Invalid poke args')
                    return
                logger.debug(("csr_addr: {0} word_array:{1}").format
                             (csr_addr, [hex(x) for x in word_array]))

                i2c_conn = i2c_obj_db().get_i2c_conn(self.i2c_dev_id)
                if not i2c_conn:
                    if not fast_poke:
                        self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    else:
                        logger.error('I2c dev is not connected!')
                    return
                status = i2c_conn.i2c_csr_poke(csr_addr = csr_addr,
                                               word_array = word_array)
                if not fast_poke:
                    self.send_obj({"STATUS":[status, "OK!" if status else "i2c csr error!"]})
            elif cmd == "DISCONNECT":
                disconnect_args = obj.get("args", None)
                user = None
                if not disconnect_args:
                    self.send_obj({"STATUS":[False, "Invalid disconnect args!"]})
                else:
                    user = disconnect_args.get("user", None)
                    if not user:
                        self.send_obj({"STATUS":[False, ("Invalid connect args. user id is missing!")]})

                logger.info('Disconnecting i2c connection to {0}'.format(self.i2c_dev_id))
                i2c_conn = i2c_obj_db().get_i2c_conn(self.i2c_dev_id)
                if i2c_conn:
                    i2c_conn.i2c_disconnect()
                    self.send_obj({"STATUS":[True, 'I2c is disconnected by "{0}"'.format(user)]})
                    i2c_obj_db().del_i2c_conn(self.i2c_dev_id)
                else:
                    self.send_obj({"STATUS":[True, "I2c is already disconnected"]})
                self.i2c_dev_id = None
            elif cmd == "DBG_CHAL_CMD":
                dbg_chal_args = obj.get("args", None)
                if not dbg_chal_args:
                    self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    return
                cmd = dbg_chal_args.get("dbg_chal_cmd", None)
                if not cmd or not type(int):
                    self.send_obj({"STATUS":[False, "Invalid dbg chal cmd args!"]})
                    return
                i2c_conn = i2c_obj_db().get_i2c_conn(self.i2c_dev_id)
                if not i2c_conn:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                logger.info("cmd: {0}".format(hex(cmd)))
                cmd_data = dbg_chal_args.get("data", None)
                logger.debug('cmd: {0} cmd_data: {1}'.format(cmd, cmd_data))
                status = False
                logger.debug("cmd data: {0}".format(cmd_data))
                try:
                    retry_cnt = 0
                    status = False
                    resp_data = None
                    while status == False:
                        logger.info('Issueing chal cmd: {0}'.format(hex(cmd)))
                        (status, resp_data) = i2c_conn.i2c_dbg_chal_cmd(cmd = cmd,
                                                                   data = cmd_data)
                        if status == False:
                            i2c_wedged = i2c_conn.i2c_wedge_detect()
                            if i2c_wedged == True:
                                err_msg = 'i2c device wedged!'
                                logger.error(err_msg)
                                retry_cnt += 1
                                if retry_cnt > 10:
                                    err_msg = 'Unwedge retry limit exceeded!'
                                    logger.error(err_msg)
                                    self.send_obj({"STATUS":[False, err_msg]})
                                    return
                                unwedge_status = i2c_conn.i2c_unwedge()
                                if unwedge_status == False:
                                    err_msg = 'i2c device unwedge failed!'
                                    logger.error(err_msg)
                                    self.send_obj({"STATUS":[False, err_msg]})
                                    return
                                else:
                                    logger.info('I2C UNWEDGED!')
                            else:
                                logger.info(('i2c not wedged! but i2c_dbg_chal_cmd failed.'
                                        ' resp data: {0}').format(resp_data))
                                err_msg = resp_data if resp_data else "Unknown error!"
                                logger.error(err_msg)
                                self.send_obj({"STATUS":[False, err_msg]})
                                return
                        else:
                            logger.debug('status: {0} resp_data: {1}'.format(status, resp_data))
                            resp = dict()
                            resp["STATUS"] = [True, "dbg cmd success!"]
                            if resp_data:
                                resp["DATA"] = list(resp_data)
                            logger.debug(resp)
                            self.send_obj(resp)
                            return
                except Exception as e:
                    logging.error("Exception")
                    logging.error(traceback.format_exc())
                    resp["STATUS"] = [False, "dbg chal cmd exception!"]
                    self.send_obj(resp)
                    return
            else:
                logger.debug("Invalid msg!")
                self.send_obj({"STATUS":[False, "Invalid message!"]})

    def create_i2c(self, chip_type, id, addr, bitrate):
        """ Simple factory for i2c """
        if chip_type == 'f1':
            return i2c(dev_id=id, slave_addr=addr, bitrate=bitrate, chip_type=chip_type)
        else:
            return csr2i2c(dev_id=id, slave_addr=addr, bitrate=bitrate, chip_type=chip_type)


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
            server.stop_all()
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

    #i2c_objs = i2c_obj_db()
    server = jsocket.ServerFactory(I2CFactoryThread, address=ip_addr,
                                   port = constants.SERVER_TCP_PORT)
    server.timeout = 2.0
    server.setDaemon(1)
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
