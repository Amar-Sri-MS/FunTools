#!/usr/bin/env python
import os,sys
import json
import logging

try:  
   os.environ["WORKSPACE"]
except KeyError: 
   print "Please set the environment variable WORKSPACE"
   sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("address_manager")
logger.setLevel(logging.INFO)

################################################################################
# read in predefined cfg values from addr_cfg.txt
class addr_cfg(object):
   def __init__(self):
      addr_cfg_file = os.environ["WORKSPACE"]+"/FunTools/verif_tools/addr_cfg.txt"
      with open(addr_cfg_file) as f:
         self.data = json.load(f)

   def get_cfg_info(self, dut):
      addr_cfg_file = os.environ["WORKSPACE"]+"/FunTools/verif_tools/addr_cfg.txt"
      with open(addr_cfg_file) as f:
         self.data = json.load(f)
      if dut == None:
         logger.error('Invalid dut: None')
         return None
      dut_cfg = self.data.get(dut, None)
      if dut_cfg == None:
         logger.error('dut:{} does not exist in dut db!'.format(dut))
         logger.info('Valid duts: {}'.format(self.data))
         return None

        #convert to int
      for x,y in dut_cfg.items():
         dut_cfg[x]=int(y,0)
        
      return dut_cfg

################################################################################
# do f1 address translation to icc/hbm/ddr
class addr_manager(object):
   def __init__(self):
      self.cfgs=addr_cfg()
      self.cfg=self.cfgs.get_cfg_info('f1')

   def set_cfg(self,cfg_name):
      self.cfg=self.cfgs.get_cfg_info('f1')

   def pa_to_sa(self,pa):
      return (1,0x2)

   def translate_paddr(self,pa):
      addr={}
      addr['pa']=pa
      (addr['shard'],addr['sa'])=self.pa_to_sa(pa)
      return addr

################################################################################
def addr_cfg_test():
    cfgs = addr_cfg()
    cfg0 = cfgs.get_cfg_info('f1')
    if cfg0 is None:
        logger.error('Failed to get cfg info!')
    else:
        logger.info('Found cfg {0} info!\n{1}'.format('f1',cfg0))

def addr_mgr_test():
    mgr = addr_manager()
    mgr.set_cfg('f1')
    a=mgr.translate_paddr(0x40);
    print a

if __name__== "__main__":
    #addr_cfg_test()
    addr_mgr_test()
