#!/usr/bin/python
import socket
import sys
import time
import datetime
import struct
import binascii #for hexdump
import string, os
import json
import threading
from threading import Thread
sys.path.append(os.environ["WORKSPACE"]+"/FunTools/dbgutils")
from csrutils.csrutils import *
from probeutils.i2cutils import *

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


#first create and bind the verif server socket
HOST = ''                 # Symbolic name meaning the local host
PORT = 0x1234              # Arbitrary non-privileged port
I2C_SERVER = '10.1.20.69' #IP address of I2C server

rcv_pkt_list = list() #global variable to store the packets received from DUT

#ignore packets from any ports in this test. Port 3 is seen sending pause frames
#hence it is added to this list
ignore_ports = [3]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Client Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Client Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Client Socket now listening on port %d' % (PORT)

#now setup the listening socket for the PTF
#
# Receiving handling in receiving thread
#
def rcv_packets_from_server(self, sock):
    try:
        result = sock.recv(16*1024)
        if result == "":
            print("PTF socket closed remotely at server side")
            self.join()
            return
        jdata = json.loads(result)
        intf = jdata["intf"]
        print (("Received PTF Response on intf %d: " % (intf)) + str(jdata))
        #get rid of the fpg prefix
        intf = intf.replace("fpg", "")
        #pkt = pkt_decode(jdata["pkt"])
        pkt = jdata["pkt"]
        pkt_byte_list = pkt.split()
        print (tuple((intf, pkt_byte_list)))
        #store the return data into a list
        if not (intf in ignore_ports) :
            rcv_pkt_list.append(tuple((intf, pkt_byte_list)))
        else :
            print ("Ignoring packet on intf %d from PTF" % intf)

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

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 9001))
print 'Connected with PTF server. Start listening for packets from DUT'
sock.settimeout(0.5)

# Start receving thread
rcvthread = RcvThread(sock)
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
  print_command(cmd)
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
     process_cmd_pkt_req();

###################################################

##########process_cmd_csr_write####################
def process_cmd_csr_write (msg_len):
  global glb_wr_cnt
  glb_wr_cnt+=1
  print 'in process_cmd_csr_write cnt=%0d'%(glb_wr_cnt)
  #get 8B addr
  buf = recv_str(8)
  (addr,) = struct.unpack(">Q", buf[:8])
  print 'address is 0x%x' % (addr)

  #now get the csr write data
  data_len = msg_len - 2 - 1 - 8 #msg_len - MSGLEN_SIZE - CMD_SIZE - ADDR_SIZE
  data_str = recv_str(data_len)
  data_list_bytes = [ord(i) for i in list(data_str)]
  print data_list_bytes
  data_words_list = byte_array_to_words_be(array('B', data_list_bytes))
  print "csr_poke data:"
  print data_words_list

  (status, result) = dbgprobe().csr_poke(addr, len(data_words_list), data_words_list)
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
  json_pkt = '{ "intf" :  '+ '"' + "fpg" + str(pkt_port) + '"' ', "pkt" : "' +pkt_data_with_space+'"}'
  print "Sending pkt to PTF server:"
  print json_pkt
  sock.sendall(json_pkt)
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
def process_cmd_pkt_req ():

  print 'in process_cmd_pkt_req'

  if (len(rcv_pkt_list)) :
    (pkt_port, pkt_bytes) = rcv_pkt_list.pop(0)
  else :
    pkt_port = 0;
    pkt_bytes = []

  if (len(pkt_bytes) == 0) :
    print "no pkt available"
  else :
    print "reply pkt_len is %d" % len(pkt_bytes)

  #print "reply pkt = " + ",".join(repr(hex(n)) for n in pkt_bytes)
  #print "recv pkt = " + pkt_bytes
  msg_len = 2 + 1 + 2 + len(pkt_bytes) #msg_size + command + port_size + pkt bytes
  reply = []
  reply.insert(0, msg_len >>8)
  reply.insert(1, msg_len& 0xff)
  reply.insert(2, CMD_PKT)
  reply.insert(3, pkt_port >>8)
  reply.insert(4, pkt_port & 0xff)

  reply += pkt_bytes
  reply = bytearray(reply)
  print "server reply done for pkt_req "
  conn.sendall(reply)
###################################################
##########process_cmd_csr_read#####################
def process_cmd_csr_read (msg_len):
  global glb_rd_cnt
  glb_rd_cnt+=1
  print 'in process_cmd_csr_read cnt=%0d'%(glb_rd_cnt)
  #get 8B addr
  buf = recv_str(8)
  (addr,) = struct.unpack(">Q", buf[:8])
  print 'address is 0x%x' % (addr)

  #now get the dword_len (num dwords to read)
  data = recv_str(1)
  (dword_len,) = struct.unpack(">B", data)
  print 'num_dwords to read is is %d' % (dword_len)

  (status, result) = dbgprobe().csr_peek(addr, dword_len)
  print "result=",result

  if status is False:
      print ("csr_peek returned false")
      sys.exit(1)

  print "csr_peek returned"
  if result is not None:
    read_data_hex_str = ''.join(hex(e)[2:] for e in result)
  else:
    read_data_hex_str = 'deadbeefdeadbeef' #make up a dummy result

  print "read: addr=0x%0x data=%s"%(addr,read_data_hex_str)

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

  print "server reply done for csr_read: " +  reply
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
       print '\n\ngot message with length %d' % (msg_len)

       #now get the 1B command
       data = recv_str(1)
       (cmd,) = struct.unpack(">B", data)

       process_cmd(cmd, msg_len)

     
sdkdir = "/bin/" + os.uname()[0]
if ("SDKDIR" in os.environ):
    sys.path.append(os.environ["SDKDIR"] + sdkdir)
elif ("WORKSPACE" in os.environ):
    sys.path.append(os.environ["WORKSPACE"] + "/FunSDK/" + sdkdir)
else:
	raise RuntimeError("Please specify WORKSPACE or SDKDIR environment variable")

import dpc_client

# connect to an already running dpc proxy using strict JSON mode
#client = dpc_client.DpcClient(False)
#i2c_client_socket = i2c_remote_connect(I2C_SERVER)
print "connect to I2C"
#status = dbgprobe().connect('i2c', I2C_SERVER, 'TPCFbwoQ')
status = dbgprobe().connect('i2c', I2C_SERVER, 'TPCFb23b',0x70,False)

if status is True:
  print("I2C Server Connection Successful!")
else:
  print("I2C Server Connection Failed!")
  sys.exit(1)

#print 'do server speed test'
#do_server_speed_test()
glb_rd_cnt=0
glb_wr_cnt=0

#now keep talking with the dpc_client
while True:
    #wait to accept a connection - blocking call
    print 'wait to accept a connection from client'
    conn, addr = s.accept()
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

s.close()

