#!/usr/bin/python

import os,sys

try:  
   os.environ["ROOT_DIR"]
except KeyError: 
   print "Please set the environment variable ROOT_DIR"
   sys.exit(1)


from ctypes import *

f1_lib=cdll.LoadLibrary(os.environ["ROOT_DIR"]+"/f1/ver/f1/f1_csr_slib/f1_csr_slib.so")

#sys.path.append(os.environ["ROOT_DIR"]+"/FunTools/verif_tools")
#from verif_server2 import *
connect_verif_client_socket()
connect_dbgprobe()
bg_handle_csr()

f1_lib.open_socket('localhost')
f1_lib.csr_socket_set_dbg_level(0)


def csr_wr(addr,data):
    status=[0]
    dlen = len(data)
    data_type = c_ulonglong * dlen
    status_type = c_uint * 1
    f1_lib.csr_sv_write(c_ulonglong(addr),c_uint(dlen),data_type(*data),status_type(*status))

def csr_rd(addr,dlen):
    status=[0]
    status_type = c_uint * 1
    data=[0]*dlen
    data_type = c_ulonglong * dlen
    f1_lib.csr_sv_read(c_ulonglong(addr),c_uint(dlen),data_type(*data),status_type(*status))
    return data

addr=0xaabbccddeeffaabb
data=[0x0102030405060708,0x0102030405060708]
status=[0]
dlen=len(data)
f1_lib.csr_sv_write(c_ulonglong(addr),c_uint(dlen),data_type(*data),status_type(*status))
csr_wr(addr,data)
csr_rd(addr,1)
ret=f1_lib.at_pc_cmh_run(0,0x4,0xffffffff,0xffffffff,0xffffffff,0x1)
ret=f1_lib.at_pc_cmh_run(0,0x4,0xffffffff,1,0xffffffff,0x1)
ret=f1_lib.at_cdu_run(0,0xf,0xffffffff,0,1,0xabcd)
ret=f1_lib.at_cdu_run(0,0x2,0xffffffff,0,1,0xabcd)
