#!/usr/bin/env python3
import argparse
import socket
import sys
import time
import datetime
import struct
import binascii #for hexdump
import string, os
import json
import threading
import random
import code, rlcompleter, readline
import logging

from threading import Thread
try:
   os.environ["WORKSPACE"]
except KeyError:
   print("Please set the environment variable WORKSPACE")
   sys.exit(1)
sys.path.append(os.environ["WORKSPACE"]+"/FunTools/dbgutils")
sys.path.append(os.environ["WORKSPACE"]+"/FunTools/dbgutils/probeutils")
from csrutils.csrutils import *
from probeutils.i2cutils import *
import dut

#first create and bind the verif server socket
HOST = ''                 # Symbolic name meaning the local host

rcv_pkt_list = list() #global variable to store the packets received from DUT

#ignore packets from any ports in this test. Port 3 is seen sending pause frames
#hence it is added to this list
#ignore_ports = []
ignore_ports = [str(i) for i in range (3,12)]

fast_poke=True
#print 'do server speed test'
#do_server_speed_test()
req_cnt=0
glb_rd_cnt=0
glb_wr_cnt=0
hnu_port_base=37
logger = logging.getLogger("verif_server")
logger.setLevel(logging.ERROR)
#logger.setLevel(logging.INFO)
verif_socket_port=0
bmc_chip_inst=0

#
# Convert hex encoding String back to raw packet
#
def pkt_decode(src):
    chars = src.split()
    ret = bytearray()
    for x in chars:
        x='0x'+x
        i = int(x, 16)
        ret.append(i)
    final="".join(map(chr, ret))
    return final

def connect_verif_client_socket(port,chip_inst=0):
    global verif_sock,verif_socket_port,bmc_chip_inst
    verif_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bmc_chip_inst=chip_inst
    logger.debug('Client Socket created')
    #Bind socket to local host and port
    try:
        verif_sock.bind((HOST, port))
    except socket.error as msg:
        logger.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    logger.debug('Client Socket bind complete')
    verif_socket_port=verif_sock.getsockname()[1]
    #Start listening on socket
    verif_sock.listen(10)
    logger.info('Client Socket now listening on port %d' % (verif_socket_port))
    return verif_socket_port

#now setup the listening socket for the PTF
#
# Receiving handling in receiving thread
#
def rcv_packets_from_server(self, sock):
    try:
        result = ptf_sock.recv(16*1024)
        if result == "":
            print("PTF socket closed remotely at server side")
            self.join()
            return
        jdata = json.loads(result)
        intf = jdata["intf"]
        print(("Received PTF Response on intf %s: " % str(intf)) + str(jdata))
        #get rid of the fpg prefix
        if("hnu" in intf):
            intf = intf.replace("hnu_fpg", "")
            port = hnu_port_base + int(intf)
            intf = str(port)
        else:
            intf = intf.replace("fpg", "")
        #pkt = pkt_decode(jdata["pkt"])
        pkt = jdata["pkt"]
        pkt_byte_list = pkt.split()
        pkt_byte_list=[int(i,16) for i in pkt_byte_list]
        print(tuple((intf, pkt_byte_list)))
        #store the return data into a list
        if not (intf in ignore_ports) :
            rcv_pkt_list.append(tuple((intf, pkt_byte_list)))
        else :
            print("Ignoring packet on intf %s from PTF" % intf)

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

def connect_ptf():
    global ptf_sock
    ptf_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ptf_sock.connect((args.ptf_host,args.ptf_port))
    print('Connected with PTF server. Start listening for packets from DUT')
    ptf_sock.settimeout(0.5)
# Start receving thread
    rcvthread = RcvThread(ptf_sock)
    rcvthread.start()

#  Frame format: 2B msglen, 1B cmd, [2B port/8B addr, payload]
#   cmd :  1byte()            Frame format
#      00:    ACK_NOP         2B msglen, 1B cmd //generic ack or nop
#      01:    reset_assert    2B msglen, 1B cmd
#      02:    reset_deassert  2B msglen, 1B cmd
#      03:    csr wr          2B msglen, 1B cmd, 8B addr, data(nx8 byte)
#      04:    csr rd          2B msglen, 1B cmd, 8B addr
#      05:    csr rd resp     2B msglen, 1B cmd, data(nx8 byte)
#      06:    pkt             2B msglen, 1B cmd, 2B port, pkt data(upto 16k byte)
#      07:    pkt req         2B msglen, 1B cmd

def test_ptf():
    print('do test_ptf')
    if 1:
       pkt_data_with_space = ""
       pkt_data="00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
       for i in range (len(pkt_data)/2):
          pkt_data_with_space += pkt_data[2*i] + pkt_data[(2*i) + 1] + " "
       #get rid of the trailing space
       pkt_data_with_space = pkt_data_with_space[0:-1]
       json_pkt = '{ "intf" :  '+ '"' + "fpg" + str(0) + '"' ', "pkt" : "' +pkt_data_with_space+'"}'
       print("Sending pkt to PTF server:")
       print(json_pkt)
       ptf_sock.sendall(json_pkt)
       time.sleep(0.5)
    else:
       try:
          result = ptf_sock.recv(16*1024)
       except(socket.timeout):
          pass

#defines for the commands
CMD_ACK_NOP       = 0
CMD_RESETA        = 1
CMD_RESETD        = 2
CMD_CSR_WRITE     = 3
CMD_CSR_READ      = 4
CMD_CSR_READ_RSP  = 5
CMD_PKT           = 6
CMD_PKT_REQ       = 7


def print_command(data):
  if (data == CMD_ACK_NOP) :
     print("ACK_NOP")
  elif (data == CMD_RESETA) :
     print("CMD_RESETA")
  elif (data == CMD_RESETD) :
     print("CMD_RESETD")
  elif (data == CMD_CSR_WRITE) :
     print("CMD_CSR_WRITE")
  elif (data == CMD_CSR_READ) :
     print("CMD_CSR_READ")
  elif (data == CMD_CSR_READ_RSP) :
     print("CMD_CSR_READ_RSP")
  elif (data == CMD_PKT) :
     print("CMD_PKT")
  elif (data == CMD_PKT_REQ) :
     print("CMD_PKT_REQ")
  else :
     print("unknown command!")

##########recv_str#################################
#recv n bytes and returns a string of size n
def recv_str(n):
    global conn
    buf = ''
    while len (buf) < n:
        data = conn.recv(n)
        if not data:
            return
        buf += data
    return buf
###################################################
##########process_cmd##############################
def process_cmd (cmd, msg_len):
  #print_command(cmd)
  if (cmd == CMD_ACK_NOP):
     print('not implemented yet')
  elif (cmd == CMD_RESETA):
     print('not implemented yet')
  elif (cmd == CMD_RESETD):
     print('not implemented yet')
  elif (cmd == CMD_CSR_WRITE):
     process_cmd_csr_write(msg_len)
  elif (cmd == CMD_CSR_READ):
     process_cmd_csr_read(msg_len)
  elif (cmd == CMD_CSR_READ_RSP):
     print('not implemented yet')
  elif (cmd == CMD_PKT):
     process_cmd_pkt(msg_len)
  elif (cmd == CMD_PKT_REQ):
     process_cmd_pkt_req(msg_len);

###################################################

##########process_cmd_csr_write####################
def process_cmd_csr_write (msg_len):
  global glb_wr_cnt
  glb_wr_cnt+=1
  #print 'in process_cmd_csr_write cnt=%0d'%(glb_wr_cnt)
  #get 8B addr
  buf = recv_str(8)
  (addr,) = struct.unpack(">Q", buf[:8])
  #logger.debug('in process_cmd_csr_write cnt=%0d, address = 0x%x '%(glb_wr_cnt,addr))
#  print 'address is 0x%x' % (addr)

  #now get the csr write data
  data_len = msg_len - 2 - 1 - 8 #msg_len - MSGLEN_SIZE - CMD_SIZE - ADDR_SIZE
  data_str = recv_str(data_len)
  data_list_bytes = [ord(i) for i in list(data_str)]
  #logger.debug("{0}".format(data_list_bytes))
  data_words_list = byte_array_to_words_be(array('B', data_list_bytes))
  #print "csr_poke data:"
  #print data_words_list

  if i2c_dis:
      (status, result) = (True,None)
  elif fast_poke:
      (status, result) = dbgprobe().csr_fast_poke(addr, data_words_list, chip_inst=bmc_chip_inst)
  else:
      (status, result) = dbgprobe().csr_poke(addr, data_words_list, chip_inst=bmc_chip_inst)
  #print "csr_poke returned"
  if status is False:
      logger.error("csr_poke returned false")
      sys.exit(1)

  #finally send reply
  #reply = []
  #reply_len = 3 #MSGLEN_SIZE + CMD_SIZE
  #reply.insert(0, reply_len >>8)
  #reply.insert(1, reply_len & 0xff)
  #reply.insert(2, CMD_ACK_NOP)

  #reply = bytearray(reply)
  ##print "server reply done for csr_write "
  #conn.sendall(reply)
###################################################
##########process_cmd_pkt##########################
def process_cmd_pkt (msg_len):

  print('in process_cmd_pkt')

  if not args.ptf_dis:
    buf = recv_str(2) #get the 2B port number
    (pkt_port,) = struct.unpack(">h", buf[:2])

    data_len = msg_len - 2 - 1 -2  #msg_len - MSGLEN_SIZE - CMD_SIZE - PORT_SIZE
    data_byte_arr = recv_str(data_len)
    print('recvd pkt from client length=%d on port %d' % (len(data_byte_arr), pkt_port))

    pkt_data = binascii.hexlify(data_byte_arr)
    #ptf server wants a space after every byte
    pkt_data_with_space = ""
    for i in range (len(pkt_data)/2):
      pkt_data_with_space += pkt_data[2*i] + pkt_data[(2*i) + 1] + " "
    #get rid of the trailing space
    pkt_data_with_space = pkt_data_with_space[0:-1]

    #do necessary FunOS API calls to make pkt_send happen
    if(pkt_port >= hnu_port_base):
        json_pkt = '{ "intf" :  '+ '"' + "hnu_fpg" + str(pkt_port-hnu_port_base) + '"' ', "pkt" : "' +pkt_data_with_space+'"}'
    else:
        json_pkt = '{ "intf" :  '+ '"' + "fpg" + str(pkt_port) + '"' ', "pkt" : "' +pkt_data_with_space+'"}'
    print("Sending pkt to PTF server:")
    print(json_pkt)
    ptf_sock.sendall(json_pkt)
    #Sleep to make sure message is out
    time.sleep(0.5)

  #finally send reply
  reply = []
  reply_len = 3 #MSGLEN_SIZE + CMD_SIZE
  reply.insert(0, reply_len >>8)
  reply.insert(1, reply_len & 0xff)
  reply.insert(2, CMD_ACK_NOP)

  reply = bytearray(reply)

  print("server reply done for pkt_send: ")
  conn.sendall(reply)
###################################################
##########process_cmd_pkt_req######################
def process_cmd_pkt_req (msg_len):
  global req_cnt;
  req_cnt += 1

#  print 'in process_cmd_pkt_req'

  exit_loop=0;
  while(exit_loop == 0):
    if (len(rcv_pkt_list)) :
      (pkt_port, pkt_bytes) = rcv_pkt_list.pop(0)
      if(len(pkt_bytes) > 127 ) :
          exit_loop = 1
      else:
          print("dropping pkt < 100 bytes  mostly icmp discovery pkts")
          exit_loop = 0
    else :
      pkt_port = 0;
      pkt_bytes = []
      exit_loop = 1

  if (len(pkt_bytes) == 0 ) :
      print("process_cmd_pkt_req:no pkt available req_cnt=%0d" %(req_cnt))
  else :
      print("process_cmd_pkt_req:reply pkt_len is %d,req_cnt=%0d" % (len(pkt_bytes),req_cnt))

  #print "reply pkt = " + ",".join(repr(hex(n)) for n in pkt_bytes)
  #print "recv pkt = " + pkt_bytes
  msg_len = 2 + 1 + 2 + len(pkt_bytes) #msg_size + command + port_size + pkt bytes
  reply = []
  reply.insert(0, msg_len >>8)
  reply.insert(1, msg_len& 0xff)
  reply.insert(2, CMD_PKT)
  reply.insert(3, int(pkt_port) >>8)
  reply.insert(4, int(pkt_port) & 0xff)
  if(len(pkt_bytes) !=0 ):
    print(pkt_bytes)
   # pkt_bytes=[int(i,16) for i in pkt_bytes]
    reply += pkt_bytes
    print(reply)


  reply = bytearray(reply)
 # print "server reply done for pkt_req "
  conn.sendall(reply)
###################################################
##########process_cmd_csr_read#####################
def process_cmd_csr_read (msg_len):
  global glb_rd_cnt
  glb_rd_cnt+=1
  #print 'in process_cmd_csr_read cnt=%0d'%(glb_rd_cnt)
  #get 8B addr
  buf = recv_str(8)
  (addr,) = struct.unpack(">Q", buf[:8])
  #print 'address is 0x%x' % (addr)

  #now get the dword_len (num dwords to read)
  data = recv_str(1)
  (dword_len,) = struct.unpack(">B", data)
  #print 'num_dwords to read is is %d' % (dword_len)

  if i2c_dis:
      (status,result) = (True,[random.randint(0,0x10000000000000000)]*dword_len)
  else:
      (status, result) = dbgprobe().csr_peek(addr, dword_len, chip_inst=bmc_chip_inst)
  #logger.debug("result={0}".format(result))

  if status is False:
      logger.error("csr_peek returned false")
      sys.exit(1)

  #print "csr_peek returned"
  if result is not None:
    read_data_hex_str = ''.join(hex(e)[2:] for e in result)
  else:
    read_data_hex_str = 'deadbeefdeadbeef' #make up a dummy result

  #logger.debug("read: addr=0x%0x data=%s,gbl_rd_cnt=%0d"%(addr,read_data_hex_str,glb_rd_cnt))

  #finally send reply
  reply_len = 2 + 1 + 8*dword_len #msg_size + command + Bytes of data
  reply = []
  reply.insert(0, reply_len >>8)
  reply.insert(1, reply_len & 0xff)
  reply.insert(2, CMD_CSR_READ_RSP)
  for i in result:
    reply += struct.pack('>Q',i)
  #reply += result
  reply = bytearray(reply)

  #print "server reply done for csr_read: " +  reply
  conn.sendall(reply)
###################################################

def do_server_speed_test():
    addr=0x5015c00078
    data_words_list=[0x12341234]
    print("start:",datetime.datetime.now())
    for i in range(1000):
         (status, result) = dbgprobe().csr_poke(addr, len(data_words_list), data_words_list, chip_inst=bmc_chip_inst)
    print("end  :",datetime.datetime.now())

def handle_connection(conn):
    buf = ''
    while True:
       #first get the 2B message length from the frame
       buf = recv_str(2)
       if not buf:
          return
       (msg_len,) = struct.unpack(">h", buf[:2])
       #print '\n\ngot message with length %d' % (msg_len)

       #now get the 1B command
       data = recv_str(1)
       (cmd,) = struct.unpack(">B", data)

       process_cmd(cmd, msg_len)


def connect_dbgprobe(tpod,tpod_jtag,tpod_pcie,tpod_force):
    duts = dut.dut()

    if tpod_jtag:
       jtag_info=duts.get_jtag_info(tpod)
       (bmc,jtag_probe_id, jtag_probe_ip,chip_type,jtag_bitrate)=jtag_info
       print("connecting to JTAG Proxy "+jtag_probe_ip)
       status = dbgprobe().connect(mode='jtag',
                                   probe_ip_addr=jtag_probe_ip,
                                   probe_id=jtag_probe_id,
                                   chip_type=chip_type,
                                   jtag_bitrate=jtag_bitrate)
       if status is True:
          print("JTAG Server Connection Successful!")
       else:
          print("JTAG Server Connection Failed!")
          sys.exit(1)
    elif tpod_pcie:
       pcie_ccu_bar=0
       pcie_probe_ip=0
       dut_pcie_info = duts.get_pcie_info(tpod)
       if dut_pcie_info[0] is False:
          pcie_ccu_bar = dut_pcie_info[1]
          pcie_probe_ip = dut_pcie_info[2]
          pcie_mem_offset = dut_pcie_info[3]
          print("connecting to PCIE bar={0} ip={1}".format(pcie_ccu_bar,pcie_probe_ip))
          status = dbgprobe().connect(mode='pcie', bmc_board=False,
                                      probe_ip_addr = pcie_probe_ip,
                                      probe_id = pcie_ccu_bar,
                                      slave_addr = pcie_mem_offset)
       else:
          bmc_ip = dut_pcie_info[1]
          pcie_ccu_bar = dut_pcie_info[2]
          pcie_probe_ip = dut_pcie_info[3]
          pcie_mem_offset = dut_pcie_info[4]
          print("connecting to PCIE bar={0} ip={1}".format(pcie_ccu_bar,pcie_probe_ip))
          status = dbgprobe().connect(mode='pcie', bmc_board=False,
                                      probe_ip_addr=pcie_probe_ip,
                                      probe_id = pcie_ccu_bar,
                                      slave_addr = pcie_mem_offset)
       print("connecting to PCIE bar={0} ip={1} status={2}".format(pcie_ccu_bar,pcie_probe_ip,status))
       if status is False:
          sys.exit(1)
    else:
       i2c_info = duts.get_i2c_info(tpod)
       if i2c_info[0] is True:
          (bmc,bmc_ip,chip_type)=i2c_info
          status = dbgprobe().connect(bmc_board=bmc,
                                      mode='i2c',
                                      bmc_ip_address=bmc_ip,
                                      chip_type=chip_type)
       else:
          (bmc,i2c_probe_serial, i2c_proxy_ip, i2c_slave_addr, this_i2c_bitrate,chip_type)=i2c_info
          print("connecting to I2C Proxy "+i2c_proxy_ip)
          status = dbgprobe().connect(bmc_board=bmc,
                                      mode='i2c',
                                      probe_ip_addr=i2c_proxy_ip,
                                      probe_id=i2c_probe_serial,
                                      slave_addr=i2c_slave_addr,
                                      force=tpod_force,
                                      i2c_bitrate=this_i2c_bitrate,
                                      chip_type=chip_type)
       if status is True:
          print("I2C Server Connection Successful!")
       else:
          print("I2C Server Connection Failed!")
          sys.exit(1)

def start_verif_server():
    global conn
    while True:
    #wait to accept a connection - blocking call
        logger.info('wait to accept a connection from client')
        conn, addr = verif_sock.accept()
        logger.info('Connected with client' + addr[0] + ':' + str(addr[1]))
        handle_connection(conn)
        logger.info('Disconnected from client' + addr[0] + ':' + str(addr[1]))
        conn.close()
    status = dbgprobe().disconnect()
    if status is not True:
        logger.error("I2C Server disconnect failed!")
        sys.exit(1)
    else:
        logger.info("I2C Server is disconnected!");
    verif_sock.close()

class CsrThread(threading.Thread):
    def __init__(self):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
    def run(self):
        global conn
        while True:
            logger.info('wait to accept a connection from client')
            conn, addr = verif_sock.accept()
            logger.info('Connected with client' + addr[0] + ':' + str(addr[1]))
            handle_connection(conn)
            logger.info('Disconnected from client' + addr[0] + ':' + str(addr[1]))
            conn.close()
    def join(self, timeout=None):
        self._stopevent.set()
        #threading.Thread.join(self, timeout)

def bg_handle_csr():
    csrthread = CsrThread()
    csrthread.start()

def auto_int(x):
    return int(x, 0)

def set_i2c_dis(x):
   global i2c_dis
   i2c_dis=x

def proc_arg():
    global parser, args, i2c_dis
    parser = argparse.ArgumentParser()
    parser.add_argument('--ptf_dis', action='store_true', default=False, help='ptf connection disable. default %(default)d')
    parser.add_argument('--ptf_host', nargs='?', type=str, default='localhost', help='ptf host to connect to. default %(default)s')
    parser.add_argument('--ptf_port', nargs='?', type=auto_int, default=9001, help='ptf port to connect to. default %(default)d')
    parser.add_argument('--test_ptf', action='store_true', default=False, help='test ptf connection. default %(default)d')
    parser.add_argument('--i2c_dis', action='store_true', default=False, help='i2cproxy connection disable. default %(default)d')
    parser.add_argument('--verif_port', nargs='?', type=auto_int, default=0, help='verif client port. default %(default)d')
    parser.add_argument('--tpod', nargs='?', type=str, default='TPOD4', help='TPOD name. default %(default)s')
    parser.add_argument('--tpod_force', action='store_true', default=False, help='TPOD force mode. default %(default)s')
    parser.add_argument('--tpod_jtag', action='store_true', default=False, help='TPOD JTAG mode. default %(default)s')
    parser.add_argument('--tpod_bmc_chip_inst', nargs='?', type=auto_int, default=0, help='TPOD chip_inst used in bmc mode. default %(default)s')
#    parser.add_argument('--i2c_svr', nargs='?', type=str, default='10.1.20.69', help='i2c server. default %(default)s')
    args = parser.parse_args()
    set_i2c_dis(args.i2c_dis)
    #args = parser.parse_args(['-ptf_dis'])

################################################################################

def main():
    proc_arg()
    connect_verif_client_socket(port=args.verif_port,chip_inst=args.tpod_bmc_chip_inst)
    if not args.ptf_dis:
       connect_ptf()
    if not i2c_dis:
       connect_dbgprobe(tpod=args.tpod,
                        tpod_jtag=args.tpod_jtag,
                        tpod_force=args.tpod_force)
    if args.test_ptf:
       test_ptf()
    start_verif_server()

if (__name__ == "__main__"):
    main()
