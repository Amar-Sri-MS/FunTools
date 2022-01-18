#!/usr/bin/env python2.7
import os,sys
import json
import logging
import code, rlcompleter, readline

try:  
   os.environ["WORKSPACE"]
except KeyError: 
   print "Please set the environment variable WORKSPACE"
   sys.exit(1)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("address_manager")
logger.setLevel(logging.ERROR)

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
      self.ddr_qaddr_mask=(~((1<<self.cfg['ddr_ba_0'])|(1<<self.cfg['ddr_ba_1'])|(1<<self.cfg['ddr_ba_2'])|(1<<self.cfg['ddr_ba_3'])|(1<<self.cfg['ddr_rank_sel'])))

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
   def get_hbm_addr(self,pa,shard,sa):
      (bank,col,row,ch,pch,qsys)=(0,0,0,0,0,0)
      qsn0=red_xor64(self.cfg['hbm_qsn_0']&sa)
      qsn1=red_xor64(self.cfg['hbm_qsn_1']&sa)
      qn1=red_xor64(self.cfg['hbm_qn_1']&sa)
      qn2=red_xor64(self.cfg['hbm_qn_2']&sa)
      qn3=red_xor64(self.cfg['hbm_qn_3']&sa)
      qn4=red_xor64(self.cfg['hbm_qn_4']&sa)
      qn5=red_xor64(self.cfg['hbm_qn_5']&sa)
      qn6=red_xor64(self.cfg['hbm_qn_6']&sa)
      qsys=(qsn1<<1)|qsn0
      if qsys==0:
         ch=2
      elif qsys==1:
         ch=3
      elif qsys==2:
         ch=6
      elif qsys==3:
         ch=7
      elif qsys==4:
         ch=0
      elif qsys==5:
         ch=1
      elif qsys==6:
         ch=4
      elif qsys==7:
         ch=5
      elif qsys==8:
         ch=10
      elif qsys==9:
         ch=11
      elif qsys==10:
         ch=14
      elif qsys==11:
         ch=15
      elif qsys==12:
         ch=8
      elif qsys==13:
         ch=9
      elif qsys==14:
         ch=12
      elif qsys==15:
         ch=13
      pch=(qn6<<4)+ch
      row=(sa>>11)&0x3fff
      col=(sa&0xf0)>>1
      bank=(qn4<<3)|(qn3<<2)|(qn2<<1)|qn1
      return (row,bank,col,ch,pch,qsys)

   #ddr ####################
   def get_ddr_addr(self,pa,shard,sa):
      (bank,col,row)=(0,0,0)
      rank_mask=(1<<self.cfg['ddr_rank_sel'])
      addr_prehash=((sa&(~rank_mask))>>1)|((sa&1)<<self.cfg['ddr_rank_sel'])
      #print "rank_mask=0x%0x addr_prehash=0x%0x ddr_rank_sel=%0d"%(rank_mask,addr_prehash,self.cfg['ddr_rank_sel'])
      addr_hashed=addr_prehash & self.ddr_qaddr_mask & 0x3ffffffff;
      addr_hashed|=((red_xor64(addr_prehash & self.cfg['ddr_qn_1'])&1)<<self.cfg['ddr_ba_0']);
      addr_hashed|=((red_xor64(addr_prehash & self.cfg['ddr_qn_2'])&1)<<self.cfg['ddr_ba_1']);
      addr_hashed|=((red_xor64(addr_prehash & self.cfg['ddr_qn_3'])&1)<<self.cfg['ddr_ba_2']);
      addr_hashed|=((red_xor64(addr_prehash & self.cfg['ddr_qn_4'])&1)<<self.cfg['ddr_ba_3']);
      addr_hashed|=((red_xor64(addr_prehash & self.cfg['ddr_qn_5'])&1)<<self.cfg['ddr_rank_sel']);
      col=(addr_hashed&0x7f)<<3
      ba0=(addr_hashed>>self.cfg['ddr_ba_0'])&1
      ba1=(addr_hashed>>self.cfg['ddr_ba_1'])&1
      ba2=(addr_hashed>>self.cfg['ddr_ba_2'])&1
      ba3=(addr_hashed>>self.cfg['ddr_ba_3'])&1
      rank=(addr_hashed>>self.cfg['ddr_rank_sel'])&1
      bank=(ba1<<1)|ba0
      bankGrp=(ba3<<1)|(ba2)
      row=(addr_hashed>>11)&0xffff
      inst=(addr_hashed>>27)&3
      slot=0
      ch=(shard<<3)|(inst<<1)|rank
      return (row,bank,col,bankGrp,ch)

   def translate_paddr(self,pa):
      a={}
      a['pa']=pa
      (a['shard'],a['sa'])=self.pa_to_sa(pa)
      if pa & 0x20000000000:
         (a['row'],a['bank'],a['col'],a['bankGrp'],a['ch'])=self.get_ddr_addr(pa,a['shard'],a['sa'])
      else:
         (a['row'],a['bank'],a['col'],a['ch'],a['pch'],a['qsys'])=self.get_hbm_addr(pa,a['shard'],a['sa'])
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
#   for addr in range(0,0x1000,0x40):
#      a=mgr.translate_paddr(addr);
#      print a
   for addr in range(0x20000000000,0x20000010000,0x40):
      a=mgr.translate_paddr(addr);
      print a


if __name__== "__main__":
   #addr_cfg_test()
   addr_mgr_test()
   readline.parse_and_bind('tab: complete')
   code.interact(local=globals())
