#!/usr/bin/env python
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

from threading import Thread
try:  
   os.environ["WORKSPACE"]
except KeyError: 
   print "Please set the environment variable WORKSPACE"
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

def connect_verif_client_socket():
    global verif_sock
    verif_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Client Socket created'
    #Bind socket to local host and port
    try:
        verif_sock.bind((HOST, args.verif_port))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
        
    print 'Client Socket bind complete'
    #Start listening on socket
    verif_sock.listen(10)
    print 'Client Socket now listening on port %d' % (args.verif_port)

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
        print (("Received PTF Response on intf %s: " % str(intf)) + str(jdata))
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
        print (tuple((intf, pkt_byte_list)))
        #store the return data into a list
        if not (intf in ignore_ports) :
            rcv_pkt_list.append(tuple((intf, pkt_byte_list)))
        else :
            print ("Ignoring packet on intf %s from PTF" % intf)

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
    print 'Connected with PTF server. Start listening for packets from DUT'
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
    print 'do test_ptf'
    if 1:
       pkt_data_with_space = ""
       pkt_data="00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
       for i in range (len(pkt_data)/2):
          pkt_data_with_space += pkt_data[2*i] + pkt_data[(2*i) + 1] + " "
       #get rid of the trailing space
       pkt_data_with_space = pkt_data_with_space[0:-1]
       json_pkt = '{ "intf" :  '+ '"' + "fpg" + str(0) + '"' ', "pkt" : "' +pkt_data_with_space+'"}'
       print "Sending pkt to PTF server:"
       print json_pkt
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

def test_ptf():
    print 'do test_ptf'
    while 1:
       pkt_data_with_space = ""
       pkt_data="0000f6f67d2600006df0dafb0800454001f200000000141c44af751331995cf85c5d1df650c383a9a020db81ca872c3b60c8abece382d9b08fd71de7a8589e3d5791cd037b8aeb89c18cdfd9174281e0f80c5fbd05b8338619e9d81a24f10dc1620700ed465205f6a9bf29a2159af47c7937cbbdddb459542879a02957dc162c323fd2a0765c3c6680191d3db5b604fec3270e54125c553b619c99ace1a1f9869a010a50bd0a87d5107392759fc0f2ffa1579c3cd55cc69e73d4477b1894817a9b9eb8da16dc8756043fd33d3fba57e04ad99ba01430d8011da2052e898661945b0255eedc295aabf1c6e6fd9c7dc32f89304e2b79af38ffe6af45b335435019cdbcaebf83aae73e76eec6e242c2bd2200b677bf30a90807a5b313eca43ea717d7ecb87f4bf308aefae3b332365fb9ec45e5e6fbf7603fb57880dd64609548d2a6ee97e962e2bf8548d3d64f6149cc662c462c46c4fb59c5b1b174c13ce96676bdf1b09f5882f93fec0012f65b826f372709ca4a5ff33560a79f9a1897572bb7133ebef1a3d771648cc39f3313fd88a0bc5ef0b75a5c12ea4cbe5c8eedbbb97cfe474d3fbfda5d2e67baeea8c2c5cb8ee2325b92dfbc6e3b12a72429c97f0112c6ebe083e4511f2962ab19fb7317b03dcbc4db45be2ad88c5252681178e4b9413abba6742affc848c91aa56fba74f9d000000000000000040000000000000000"
       for i in range (len(pkt_data)/2):
          pkt_data_with_space += pkt_data[2*i] + pkt_data[(2*i) + 1] + " "
       #get rid of the trailing space
       pkt_data_with_space = pkt_data_with_space[0:-1]
       json_pkt = '{ "intf" :  '+ '"' + "fpg" + str(1) + '"' ', "pkt" : "' +pkt_data_with_space+'"}'
       print "Sending pkt to PTF server:"
       print json_pkt
       ptf_sock.sendall(json_pkt)
       time.sleep(0.5)
    else:
       try:
          result = ptf_sock.recv(16*1024)
       except(socket.timeout):
          pass

def print_command(data):
  if (data == CMD_ACK_NOP) :
     print "ACK_NOP"
  elif (data == CMD_RESETA) : 
     print "CMD_RESETA"
  elif (data == CMD_RESETD) : 
     print "CMD_RESETD"
  elif (data == CMD_CSR_WRITE) : 
     print "CMD_CSR_WRITE"
  elif (data == CMD_CSR_READ) : 
     print "CMD_CSR_READ"
  elif (data == CMD_CSR_READ_RSP) : 
     print "CMD_CSR_READ_RSP"
  elif (data == CMD_PKT) : 
     print "CMD_PKT"
  elif (data == CMD_PKT_REQ) : 
     print "CMD_PKT_REQ"
  else :
     print "unknown command!"

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
     print 'not implemented yet'
  elif (cmd == CMD_RESETA):
     print 'not implemented yet'
  elif (cmd == CMD_RESETD):
     print 'not implemented yet'
  elif (cmd == CMD_CSR_WRITE):
     process_cmd_csr_write(msg_len)
  elif (cmd == CMD_CSR_READ):
     process_cmd_csr_read(msg_len)
  elif (cmd == CMD_CSR_READ_RSP):
     print 'not implemented yet'
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
  print 'in process_cmd_csr_write cnt=%0d, address = 0x%x '%(glb_wr_cnt,addr)
#  print 'address is 0x%x' % (addr)

  #now get the csr write data
  data_len = msg_len - 2 - 1 - 8 #msg_len - MSGLEN_SIZE - CMD_SIZE - ADDR_SIZE
  data_str = recv_str(data_len)
  data_list_bytes = [ord(i) for i in list(data_str)]
  print data_list_bytes
  data_words_list = byte_array_to_words_be(array('B', data_list_bytes))
  #print "csr_poke data:"
  #print data_words_list

  if args.i2c_dis:
      (status, result) = (True,None)
  elif fast_poke:
      (status, result) = dbgprobe().csr_fast_poke(addr, data_words_list)
  else:
      (status, result) = dbgprobe().csr_poke(addr, data_words_list)
  #print "csr_poke returned"
  if status is False:
      print "csr_poke returned false"
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

  print 'in process_cmd_pkt'

  if not args.ptf_dis:
    buf = recv_str(2) #get the 2B port number
    (pkt_port,) = struct.unpack(">h", buf[:2])

    data_len = msg_len - 2 - 1 -2  #msg_len - MSGLEN_SIZE - CMD_SIZE - PORT_SIZE
    data_byte_arr = recv_str(data_len)
    print 'recvd pkt from client length=%d on port %d' % (len(data_byte_arr), pkt_port)

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
    print "Sending pkt to PTF server:"
    print json_pkt
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

  print "server reply done for pkt_send: "
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
          print "dropping pkt < 100 bytes  mostly icmp discovery pkts"
          exit_loop = 0
    else :
      pkt_port = 0;
      pkt_bytes = []
      exit_loop = 1

  if (len(pkt_bytes) == 0 ) :
      print "process_cmd_pkt_req:no pkt available req_cnt=%0d" %(req_cnt)
  else :
      print "process_cmd_pkt_req:reply pkt_len is %d,req_cnt=%0d" % (len(pkt_bytes),req_cnt)

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
    print pkt_bytes
   # pkt_bytes=[int(i,16) for i in pkt_bytes]
    reply += pkt_bytes
    print reply


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

  if args.i2c_dis:
      (status,result) = (True,[random.randint(0,0x10000000000000000)]*dword_len)
  else:
      (status, result) = dbgprobe().csr_peek(addr, dword_len)
  print "result=",result

  if status is False:
      print ("csr_peek returned false")
      sys.exit(1)

  #print "csr_peek returned"
  if result is not None:
    read_data_hex_str = ''.join(hex(e)[2:] for e in result)
  else:
    read_data_hex_str = 'deadbeefdeadbeef' #make up a dummy result

  print "read: addr=0x%0x data=%s,gbl_rd_cnt=%0d"%(addr,read_data_hex_str,glb_rd_cnt)

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
    print "start:",datetime.datetime.now()
    for i in range(1000):
         (status, result) = dbgprobe().csr_poke(addr, len(data_words_list), data_words_list)
    print "end  :",datetime.datetime.now()

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


def connect_dbgprobe():
    print "connect to I2C"
#status = dbgprobe().connect('i2c', args.i2c_svr, 'TPCFbwoQ')
#    status = dbgprobe().connect('i2c', args.i2c_svr, 'TPCFb23b',0x70,False)
#always hard code slave addr to 0x70
    status = dbgprobe().connect('i2c', i2c_proxy_ip , i2c_probe_serial , 0x70,False)
    if status is True:
        print("I2C Server Connection Successful!")
    else:
        print("I2C Server Connection Failed!")
        sys.exit(1)

def start_verif_server():
    global conn
    while True:
    #wait to accept a connection - blocking call
        print 'wait to accept a connection from client'
        conn, addr = verif_sock.accept()
        print 'Connected with client' + addr[0] + ':' + str(addr[1])
        handle_connection(conn)
        print 'Disconnected from client' + addr[0] + ':' + str(addr[1])
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
            print 'wait to accept a connection from client'
            conn, addr = verif_sock.accept()
            print 'Connected with client' + addr[0] + ':' + str(addr[1])
            handle_connection(conn)
            print 'Disconnected from client' + addr[0] + ':' + str(addr[1])
            conn.close()
    def join(self, timeout=None):
        self._stopevent.set()
        #threading.Thread.join(self, timeout)

def bg_handle_csr():
    csrthread = CsrThread()
    csrthread.start()

def auto_int(x):
    return int(x, 0)

def proc_arg():
    global parser, args, i2c_probe_serial, i2c_proxy_ip, i2c_slave_addr
    parser = argparse.ArgumentParser()
    parser.add_argument('--ptf_dis', action='store_true', default=False, help='ptf connection disable. default %(default)d')
    parser.add_argument('--ptf_host', nargs='?', type=str, default='localhost', help='ptf host to connect to. default %(default)s')
    parser.add_argument('--ptf_port', nargs='?', type=auto_int, default=9001, help='ptf port to connect to. default %(default)d')
    parser.add_argument('--test_ptf', action='store_true', default=False, help='test ptf connection. default %(default)d')
    parser.add_argument('--i2c_dis', action='store_true', default=False, help='i2cproxy connection disable. default %(default)d')
    parser.add_argument('--verif_port', nargs='?', type=auto_int, default=0x1234, help='verif client port. default %(default)d')
    parser.add_argument('--tpod', nargs='?', type=str, default='TPOD4', help='TPOD name. default %(default)s')
#    parser.add_argument('--i2c_svr', nargs='?', type=str, default='10.1.20.69', help='i2c server. default %(default)s')
    args = parser.parse_args()
    duts = dut.dut()
    (i2c_probe_serial, i2c_proxy_ip, i2c_slave_addr) = duts.get_i2c_info(args.tpod)

    #args = parser.parse_args(['-ptf_dis'])

################################################################################

def main():
    proc_arg()
    connect_verif_client_socket()
    if not args.ptf_dis:
       connect_ptf()
    if not args.i2c_dis:
       connect_dbgprobe()
    if args.test_ptf:
       test_ptf()
    start_verif_server()

if (__name__ == "__main__"):
    main()
