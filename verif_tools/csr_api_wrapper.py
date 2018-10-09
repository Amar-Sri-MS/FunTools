#!/usr/bin/python
import os,sys

try:  
   os.environ["ROOT_DIR"]
except KeyError: 
   print "Please set the environment variable ROOT_DIR"
   sys.exit(1)

from ctypes import *

################################################################################
# some defines
VERIF_SERVER='server119'
#VERIF_SERVER='cadence-pc-3'

def load_lib():
   global f1_csr_lib
   f1_csr_lib=cdll.LoadLibrary(os.environ["ROOT_DIR"]+"/f1/ver/f1/f1_csr_slib/f1_csr_slib.so")

def setup_verif_socket_client():
   f1_csr_lib.csr_socket_set_dbg_level(0)

def connect_verif_server():
   f1_csr_lib.open_socket(VERIF_SERVER)

def csr_wr(addr,data):
    status=[0]
    dlen = len(data)
    data_type = c_ulonglong * dlen
    status_type = c_uint * 1
    f1_csr_lib.csr_sv_write(c_ulonglong(addr),c_uint(dlen),data_type(*data),status_type(*status))

def csr_rd(addr,dlen):
    status=[0]
    status_type = c_uint * 1
    data=(c_ulonglong*dlen)()
    f1_csr_lib.csr_sv_read(c_ulonglong(addr),c_uint(dlen),data,status_type(*status))
    temp=[int(i) for i in data]
    return temp

def csr_get_offset(an,inst=0):
   if an == 'pc_cfg':
      offset=0x0800000000 | (0x800000000*(inst+1))
   elif an == 'pc_cmh':
      offset=0x0880000000 | (0x800000000*(inst+1))
   elif an == 'dma_pc':
      offset=0x0881000000 | (0x800000000*(inst+1))
   elif an == 'ec':
      offset=0x0881100000 | (0x800000000*(inst+1))
   elif an == 'rgx':
      offset=0x0881400000 | (0x800000000*(inst+1))
   elif an == 'zip':
      offset=0x0881800000 | (0x800000000*(inst+1))
   elif an == 'jpg':
      offset=0x0881A00000 | (0x800000000*(inst+1))
   elif an == 'sec':
      offset=0x0881A00400 | (0x800000000*(inst+1))
   elif an == 'le':
      offset=0x0881A80000 | (0x800000000*(inst+1))
   elif an == 'fepw_cc':
      offset=0x0882000000 | (0x4800000000)
   elif an == 'fepw_cc':
      offset=0x0882040000 | (0x4800000000)
   elif an == 'fep_lsnmux':
      offset=0x0882080000 | (0x4800000000)
   elif an == 'cc_eqm':
      offset=0x0883000000 | (0x4800000000)
   elif an == 'cdu':
      offset=0x0884000000 | (0x4800000000)
   elif an == 'bn':
      offset=0x0884200000 | (0x4800000000)
   elif an == 'snx':
      offset=0x0884240000 | (0x4800000000)
   elif an == 'cc_dam':
      offset=0x0884400000 | (0x4800000000)
   elif an == 'pc_bp':
      offset=0x0884800000 | (0x800000000*(inst+1))
   elif an == 'pc_cmh_pc':
      offset=0x0884C00000 | (0x800000000*(inst+1))
   elif an == 'ca':
      offset=0x0884D00000 | (0x800000000*(inst+1))
   elif an == 'hsu_pwp_fip':
      offset=0x6000000000 + (0x800000000*inst)
   elif an == 'hsu_pwp_core0':
      offset=0x6000800000 + (0x800000000*inst)
   elif an == 'hsu_pwp_core1':
      offset=0x6000880000 + (0x800000000*inst)
   elif an == 'hsu_pwp_core2':
      offset=0x6000900000 + (0x800000000*inst)
   elif an == 'hsu_pwp_core3':
      offset=0x6000980000 + (0x800000000*inst)
   elif an == 'hsu_pta':
      offset=0x6001000000 + (0x800000000*inst)
   elif an == 'hsu_tgt':
      offset=0x6001800000 + (0x800000000*inst)
   elif an == 'hsu_hdma_pcie_framer':
      offset=0x6002800000 + (0x800000000*inst)
   elif an == 'dma_hsu':
      offset=0x6002900000 + (0x800000000*inst)
   elif an == 'fepw_hu_an.fep_hu':
      offset=0x6002940000 + (0x800000000*inst)
   elif an == 'fepw_hu_an.dnr':
      offset=0x6002980000 + (0x800000000*inst)
   elif an == 'hsu_wqsi':
      if inst != 0 and inst != 3:
         printf '%s illegal instance=%0d'%(an,inst)
      offset=0x6002C00000 + (0x800000000*inst)
   elif an == 'hsu_wqse':
      if inst != 0 and inst != 3:
         printf '%s illegal instance=%0d'%(an,inst)
      offset=0x6003000000 + (0x800000000*inst)
   elif an == 'hsu_msc':
      if inst != 0 and inst != 3:
         printf '%s illegal instance=%0d'%(an,inst)
      offset=0x6004000000 + (0x800000000*inst)
   else:
      printf 'unrecognized/unimplemented an %s'%(an)
      offset=0
   return offset

#if offset negative
def reset_csr_at(an, inst=0):
   if an == 'cdu':
      temp=1
   elif an == 'pc_cmh':
      temp=1
   else:
      temp=1
      
def run_csr_at(an, inst=0, tmask=0xffff, maxerr=0xffffffff, verb=0xffffffff, seed=0xabcd):
   offset=csr_get_offset(an,inst)
   if an == 'pc_cfg':
      ret=f1_csr_lib.at_pc_cfg(offset,tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc_cmh':
      ret=f1_csr_lib.at_pc_cmh_run(offset,tmask,0xffffffff,maxerr,verb,seed)
   else:
      print 'unrecognized %s inst=%0d '%(an,inst)
      ret=1
   if ret:
      print 'run_csr_at %s inst=%0d failed'%(an,inst)
      
################################################################################
def all_csr_tests():
   reset_csr_at('cdu')
   run_csr_at('cdu')
   run_csr_at('pc_cmh')
################################################################################

def main():
    load_lib()
    setup_verif_socket_client()
    connect_verif_server()

if (__name__ == "__main__"):
    main()
