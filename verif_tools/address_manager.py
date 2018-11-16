#!/usr/bin/env python
import os,sys
import json
import logging
import code, rlcompleter, readline

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
def red_xor64(x):
   x=(x>>32)^x
   x=(x>>16)^x
   x=(x>>8)^x
   x=(x>>4)^x
   x=(x>>2)^x
   x=(x>>1)^x
   x&=1
   return x

################################################################################
# do f1 address translation to icc/hbm/ddr
class addr_manager(object):
   def __init__(self):
      self.cfgs=addr_cfg()
      self.cfg=self.cfgs.get_cfg_info('f1')

   def set_cfg(self,cfg_name):
      self.cfg=self.cfgs.get_cfg_info('f1')

   #fep/icc ####################
   def pa_to_sa(self,pa):
      (shard,sa)=(0,0)
      if pa & 0x20000000000:
         if self.cfg['ddr_stack']:
            if self.cfg['ddr_shd_num']==0:
               shard=0
               sa=pa>>6
            else:
               if self.cfg['ddr_shd_num']==1:
                  shard=(~(pa>>38))&2
               else:
                  shard=(pa>>38)&2
               this_mask=(self.cfg['ddr_mask0']<<1)|1
               shard|=red_xor64(((pa>>6)&0x3ffffffff)&this_mask)
               sa=pa>>6
         else: #ddr spray
            this_mask=(self.cfg['ddr_mask0']<<2)|1
            this_val=((pa>>6)&0x3ffffffff)
            shard|=red_xor64(this_val&this_mask)
            this_mask=(self.cfg['ddr_mask1']<<2)|2
            shard|=(red_xor64(this_val&this_mask)<<1)
            sa=((pa>>6)&1)|(pa>>7)&0x1fffffffe
      else: #hbm
         if self.cfg['hbm_stack']:
            if self.cfg['hbm_shd_num']==0:
               shard=0
               sa=pa>>6
            elif self.cfg['hbm_shd_num']==1:
               if self.cfg['hbm_part_size']:
                  shard=(pa>>31)&1
                  sa=(pa>>6)&0x3ffffff
               else:
                  shard=(pa>>30)&1
                  sa=(pa>>6)&0x1ffffff
            else:
               if self.cfg['hbm_part_size']:
                  shard=(pa>>32)&3
                  sa=(pa>>6)&0x7ffffff
               else:
                  shard=(pa>>31)&3
                  sa=(pa>>6)&0x3ffffff
         else: #hbm spray
            if self.cfg['hbm_shd_num']==0:
               shard=0
               sa=(pa>>6)&0x3ffffff
            elif self.cfg['hbm_shd_num']&1:
               shard[1]=self.cfg['hbm_shd_num']&2
               this_mask=(self.cfg['hbm_mask0']<<1)|1
               this_val=((pa>>6)&0x3ffffff)
               shard|=(red_xor64(this_val&this_mask))
               sa=(pa>>7)
            else:
               this_mask=(self.cfg['hbm_mask0']<<2)|1
               this_val=((pa>>6)&0x3ffffff)
               shard|=red_xor64(this_val&this_mask)
               this_mask=(self.cfg['hbm_mask1']<<2)|2
               shard|=(red_xor64(this_val&this_mask)<<1)
               sa=(pa>>8)&0x3ffffff
      return (shard,sa)

   #hbm ####################
   def get_hbm_addr(self,pa,shard):
      return (0,0,0)

   #ddr ####################
   def get_ddr_addr(self,pa,shard):
      return (0,0,0)

   def translate_paddr(self,pa):
      a={}
      a['pa']=pa
      (a['shard'],a['sa'])=self.pa_to_sa(pa)
      if pa & 0x20000000000:
         (a['row'],a['bank'],a['col'])=self.get_ddr_addr(pa,a['shard'])
      else:
         (a['row'],a['bank'],a['col'])=self.get_hbm_addr(pa,a['shard'])
      return a

################################################################################
def addr_cfg_test():
    cfgs = addr_cfg()
    cfg0 = cfgs.get_cfg_info('f1')
    if cfg0 is None:
        logger.error('Failed to get cfg info!')
    else:
        logger.info('Found cfg {0} info!\n{1}'.format('f1',cfg0))

def addr_mgr_test():
   global mgr
   mgr = addr_manager()
   mgr.set_cfg('f1')
   a=mgr.translate_paddr(0x40);
   print a

if __name__== "__main__":
   #addr_cfg_test()
   addr_mgr_test()
   readline.parse_and_bind('tab: complete')
   code.interact(local=globals())
