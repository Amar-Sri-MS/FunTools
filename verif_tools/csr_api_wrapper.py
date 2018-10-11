#!/usr/bin/env python
import os,sys,code
import rlcompleter, readline
import argparse

try:  
   os.environ["ROOT_DIR"]
except KeyError: 
   print "Please set the environment variable ROOT_DIR"
   sys.exit(1)

from ctypes import *

################################################################################
# some defines

def load_lib():
   global f1_csr_lib
   f1_csr_lib=cdll.LoadLibrary(os.environ["ROOT_DIR"]+"/f1/ver/f1/f1_csr_slib/f1_csr_slib.so")

def setup_verif_socket_client():
   f1_csr_lib.csr_socket_set_dbg_level(0)

def connect_verif_server():
   f1_csr_lib.open_socket(args.verif_svr)

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

#TODO add init/reset as needed      
def run_csr_at(an, inst=0, tmask=0xffff, maxerr=0xffffffff, verb=0xffffffff, seed=0xabcd):
   if an == 'pc.pc_cfg':
      offset=0x0800000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_pc_cfg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.pc_cmh':
      offset=0x0880000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_pc_cmh_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.dma_pc':
      offset=0x0881000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_dma_pc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.ec':
      offset=0x0881100000 + (0x800000000*inst)
      ret=f1_csr_lib.at_ec_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.rgx':
      offset=0x0881400000 + (0x800000000*inst)
      ret=f1_csr_lib.at_rgx_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.zip':
      offset=0x0881800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_zip_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.jpg':
      offset=0x0881A00000 + (0x800000000*inst)
      ret=f1_csr_lib.at_jpg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.sec':
      offset=0x0881A00400 + (0x800000000*inst)
      ret=f1_csr_lib.at_sec_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.le':
      offset=0x0881A80000 + (0x800000000*inst)
      ret=f1_csr_lib.at_le_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.fepw_cc':
      offset=0x0882000000 | (0x4800000000)
      ret=f1_csr_lib.at_fep_cc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.fepw_cc':
      offset=0x0882040000 | (0x4800000000)
      ret=f1_csr_lib.at__run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.fep_lsnmux':
      offset=0x0882080000 | (0x4800000000)
      ret=f1_csr_lib.at_fep_lsnmux_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.cc_eqm':
      offset=0x0883000000 | (0x4800000000)
      ret=f1_csr_lib.at_cc_eqm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.cdu':
      offset=0x0884000000 | (0x4800000000)
      ret=f1_csr_lib.at_cdu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.bn':
      offset=0x0884200000 | (0x4800000000)
      ret=f1_csr_lib.at_bn_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.snx':
      offset=0x0884240000 | (0x4800000000)
      ret=f1_csr_lib.at_snx_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.cc_dam':
      offset=0x0884400000 | (0x4800000000)
      ret=f1_csr_lib.at_cc_dam_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.pc_bp':
      offset=0x0884800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_pc_bp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.pc_cmh_pc':
      offset=0x0884C00000 + (0x800000000*inst)
      ret=f1_csr_lib.at_pc_cmh_pc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'pc.ca':
      offset=0x0884D00000 + (0x800000000*inst)
      ret=f1_csr_lib.at_ca_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ HSU
   elif an == 'hsu.hsu_pwp_fip':
      offset=0x6000000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_pwp_fip_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_pwp_core0':
      offset=0x6000800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_pwp_core0_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_pwp_core1':
      offset=0x6000880000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_pwp_core1_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_pwp_core2':
      offset=0x6000900000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_pwp_core2_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_pwp_core3':
      offset=0x6000980000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_pwp_core3_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_pta':
      offset=0x6001000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_pta_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_tgt':
      offset=0x6001800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_tgt_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_hdma_pcie_framer':
      offset=0x6002800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_hdma_pcie_framer_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.dma_hsu':
      offset=0x6002900000 + (0x800000000*inst)
      ret=f1_csr_lib.at_dma_hsu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.fepw_hu_an.fep_hu':
      offset=0x6002940000 + (0x800000000*inst)
      ret=f1_csr_lib.at_fep_hu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.fepw_hu_an.dnr':
      offset=0x6002980000 + (0x800000000*inst)
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_wqsi':
      if inst != 0 and inst != 3:
         print '%s illegal instance=%0d'%(an,inst)
      offset=0x6002C00000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_wqsi_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_wqse':
      if inst != 0 and inst != 3:
         print '%s illegal instance=%0d'%(an,inst)
      offset=0x6003000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_wqse_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_msc':
      if inst != 0 and inst != 3:
         print '%s illegal instance=%0d'%(an,inst)
      offset=0x6004000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_msc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ MUH
   elif an == 'muh.muh_soc_clk.fepw_mu.fep_mu':
      offset=0x9000000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_fep_mu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.fepw_mu.dnr':
      offset=0x9000040000 + (0x800000000*inst)
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.muh_mngr':
      offset=0x9000100000 + (0x800000000*inst)
      ret=f1_csr_lib.at_muh_mngr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.muh_qsys':
      offset=0x9000110000 + (0x800000000*inst)
      ret=f1_csr_lib.at_muh_qsys_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.muh_sna':
      offset=0x9000190000 + (0x800000000*inst)
      ret=f1_csr_lib.at_muh_sna_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.muh_dna':
      offset=0x90001b0000 + (0x800000000*inst)
      ret=f1_csr_lib.at_muh_dna_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.muh_cna':
      offset=0x90001d0000 + (0x800000000*inst)
      ret=f1_csr_lib.at_muh_cna_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_soc_clk.fla':
      offset=0x9000400000 + (0x800000000*inst)
      ret=f1_csr_lib.at_fla_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.muh_dfi_clk.muh_mci':
      offset=0x9000800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_muh_mci_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'muh.dnr':
      offset=0x9008800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ MUD
   elif an == 'mud.mud_soc_clk.fepw_mud.fep_mud':
      offset=0xa000000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_fep_mud_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.fepw_mud.dnr':
      offset=0xa000040000 + (0x800000000*inst)
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.mud_mngr':
      offset=0xa000080000 + (0x800000000*inst)
      ret=f1_csr_lib.at_mud_mngr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.mud_qsys':
      offset=0xa000090000 + (0x800000000*inst)
      ret=f1_csr_lib.at_mud_qsys_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.mud_sna':
      offset=0xa0000a0000 + (0x800000000*inst)
      ret=f1_csr_lib.at_mud_sna_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.mud_dna':
      offset=0xa0000b0000 + (0x800000000*inst)
      ret=f1_csr_lib.at_mud_dna_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.mud_cna':
      offset=0xa0000c0000 + (0x800000000*inst)
      ret=f1_csr_lib.at_mud_cna_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_soc_clk.fla':
      offset=0xa000400000 + (0x800000000*inst)
      ret=f1_csr_lib.at_fla_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'mud.mud_dfi_clk.mud_mci':
      offset=0xa000800000 + (0x800000000*inst)
      ret=f1_csr_lib.at_mud_mci_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ NU 1
   elif an == 'nu.sse':
      offset=0x5800000000
      ret=f1_csr_lib.at_sse_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg0_ffe':
      offset=0x5804000000
      ret=f1_csr_lib.at_stg0_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg1_ffe':
      offset=0x5808000000
      ret=f1_csr_lib.at_stg1_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg2_ffe':
      offset=0x580c000000
      ret=f1_csr_lib.at_stg2_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg3_ffe':
      offset=0x5810000000
      ret=f1_csr_lib.at_stg3_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg4_ffe':
      offset=0x5814000000
      ret=f1_csr_lib.at_stg4_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg5_ffe':
      offset=0x5818000000
      ret=f1_csr_lib.at_stg5_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nhp':
      offset=0x581c000000
      ret=f1_csr_lib.at_nhp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fms':
      offset=0x581c400000
      ret=f1_csr_lib.at_fms_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.sfg':
      offset=0x581c800000
      ret=f1_csr_lib.at_sfg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ NU 0
   elif an == 'nu.fpg.fpg_prs':
      offset=0x5000000000
      ret=f1_csr_lib.at_fpg_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fpg.prw':
      offset=0x5000800000
      ret=f1_csr_lib.at_prw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fpg.fpg_misc':
      offset=0x5000810000
      ret=f1_csr_lib.at_fpg_misc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fpg.fpg_sdif':
      offset=0x5000814000
      ret=f1_csr_lib.at_fpg_sdif_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fpg.fpg_mpw':
      offset=0x5000880000
      ret=f1_csr_lib.at_fpg_mpw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.wro':
      offset=0x5006000000
      ret=f1_csr_lib.at_wro_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fcb':
      offset=0x5007000000
      ret=f1_csr_lib.at_fcb_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nwqm':
      offset=0x5008000000
      ret=f1_csr_lib.at_nwqm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_pwr':
      offset=0x5009000000
      ret=f1_csr_lib.at_psw_pwr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_prd':
      offset=0x5009100000
      ret=f1_csr_lib.at_psw_prd_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_sch':
      offset=0x5009180000
      ret=f1_csr_lib.at_psw_sch_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_prm':
      offset=0x5009200000
      ret=f1_csr_lib.at_psw_prm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_orm':
      offset=0x5009280000
      ret=f1_csr_lib.at_psw_orm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_irm':
      offset=0x5009300000
      ret=f1_csr_lib.at_psw_irm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_wred':
      offset=0x5009380000
      ret=f1_csr_lib.at_psw_wred_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_clm':
      offset=0x5009400000
      ret=f1_csr_lib.at_psw_clm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_pqm':
      offset=0x5009800000
      ret=f1_csr_lib.at_psw_pqm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.psw_cfp':
      offset=0x500a000000
      ret=f1_csr_lib.at_psw_cfp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.etdp':
      offset=0x500a080000
      ret=f1_csr_lib.at_etdp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.dma_nu':
      offset=0x500a380000
      ret=f1_csr_lib.at_dma_nu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.etfp':
      offset=0x500a800000
      ret=f1_csr_lib.at_etfp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fae_prs':
      offset=0x500b000000
      ret=f1_csr_lib.at_fae_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.etp_prs':
      offset=0x500b800000
      ret=f1_csr_lib.at_etp_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.efp_rfp.erp_prs':
      offset=0x500c000000
      ret=f1_csr_lib.at_erp_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.efp_rfp.sfg':
      offset=0x500c800000
      ret=f1_csr_lib.at_sfg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.efp_rfp.fms':
      offset=0x500cc00000
      ret=f1_csr_lib.at_fms_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.efp_rfp.efp_rfp_lcl':
      offset=0x500ce00000
      ret=f1_csr_lib.at_efp_rfp_lcl_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.stg6_ffe':
      offset=0x5010000000
      ret=f1_csr_lib.at_stg6_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.efp_rfp_part1':
      offset=0x5014000000
      ret=f1_csr_lib.at_efp_rfp_part1_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.epg_rdp.prw':
      offset=0x5014020000
      ret=f1_csr_lib.at_prw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.epg_rdp.epg_rdp_lcl':
      offset=0x5014030000
      ret=f1_csr_lib.at_epg_rdp_lcl_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fepw_nu.fep_nu':
      offset=0x5014030400
      ret=f1_csr_lib.at_fep_nu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fepw_nu.dnr':
      offset=0x5014040000
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fepw_hnu.fep_hnu':
      offset=0x5014080000
      ret=f1_csr_lib.at_fep_hnu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fepw_hnu.dnr':
      offset=0x50140c0000
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_fae':
      offset=0x5014400000
      ret=f1_csr_lib.at_nu_fae_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_mpg.fpg_misc':
      offset=0x5015400000
      ret=f1_csr_lib.at_fpg_misc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_mpg.fpg_sdif':
      offset=0x5015404000
      ret=f1_csr_lib.at_fpg_sdif_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_mpg.fpg_mpw':
      offset=0x5015480000
      ret=f1_csr_lib.at_fpg_mpw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_mpg.nu_mpg_core':
      offset=0x5015600000
      ret=f1_csr_lib.at_nu_mpg_core_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.fla':
      offset=0x5015800000
      ret=f1_csr_lib.at_fla_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_nmg':
      offset=0x5015c00000
      ret=f1_csr_lib.at_nu_nmg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.nu_fnc':
      offset=0x5015c00800
      ret=f1_csr_lib.at_nu_fnc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.hsu_flink_shim':
      offset=0x5017d00000
      ret=f1_csr_lib.at_hsu_flink_shim_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.hsu_hdma_pcie_framer':
      offset=0x5018d00000
      ret=f1_csr_lib.at_hsu_hdma_pcie_framer_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.hsu_tgt':
      offset=0x5019000000
      ret=f1_csr_lib.at_hsu_tgt_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'nu.dma_hsu':
      offset=0x501a000000
      ret=f1_csr_lib.at_dma_hsu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ HNU 0
   elif an == 'hnu.fpg.fpg_prs':
      offset=0x8000000000
      ret=f1_csr_lib.at_fpg_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fpg.prw':
      offset=0x8000800000
      ret=f1_csr_lib.at_prw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fpg.fpg_misc':
      offset=0x8000810000
      ret=f1_csr_lib.at_fpg_misc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fpg.fpg_sdif':
      offset=0x8000814000
      ret=f1_csr_lib.at_fpg_sdif_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fpg.fpg_mpw':
      offset=0x8000880000
      ret=f1_csr_lib.at_fpg_mpw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.wro':
      offset=0x8006000000
      ret=f1_csr_lib.at_wro_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fcb':
      offset=0x8007000000
      ret=f1_csr_lib.at_fcb_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nwqm':
      offset=0x8008000000
      ret=f1_csr_lib.at_nwqm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_pwr':
      offset=0x8009000000
      ret=f1_csr_lib.at_psw_pwr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_prd':
      offset=0x8009100000
      ret=f1_csr_lib.at_psw_prd_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_sch':
      offset=0x8009180000
      ret=f1_csr_lib.at_psw_sch_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_prm':
      offset=0x8009200000
      ret=f1_csr_lib.at_psw_prm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_orm':
      offset=0x8009280000
      ret=f1_csr_lib.at_psw_orm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_irm':
      offset=0x8009300000
      ret=f1_csr_lib.at_psw_irm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_wred':
      offset=0x8009380000
      ret=f1_csr_lib.at_psw_wred_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_clm':
      offset=0x8009400000
      ret=f1_csr_lib.at_psw_clm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_pqm':
      offset=0x8009800000
      ret=f1_csr_lib.at_psw_pqm_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.psw_cfp':
      offset=0x800a000000
      ret=f1_csr_lib.at_psw_cfp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.etdp':
      offset=0x800a080000
      ret=f1_csr_lib.at_etdp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.dma_nu':
      offset=0x800a380000
      ret=f1_csr_lib.at_dma_nu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.etfp':
      offset=0x800a800000
      ret=f1_csr_lib.at_etfp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fae_prs':
      offset=0x800b000000
      ret=f1_csr_lib.at_fae_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.etp_prs':
      offset=0x800b800000
      ret=f1_csr_lib.at_etp_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.efp_rfp.erp_prs':
      offset=0x800c000000
      ret=f1_csr_lib.at_erp_prs_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.efp_rfp.sfg':
      offset=0x800c800000
      ret=f1_csr_lib.at_sfg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.efp_rfp.fms':
      offset=0x800cc00000
      ret=f1_csr_lib.at_fms_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.efp_rfp.efp_rfp_lcl':
      offset=0x800ce00000
      ret=f1_csr_lib.at_efp_rfp_lcl_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg6_ffe':
      offset=0x8010000000
      ret=f1_csr_lib.at_stg6_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.efp_rfp_part1':
      offset=0x8014000000
      ret=f1_csr_lib.at_efp_rfp_part1_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.epg_rdp.prw':
      offset=0x8014020000
      ret=f1_csr_lib.at_prw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.epg_rdp.epg_rdp_lcl':
      offset=0x8014030000
      ret=f1_csr_lib.at_epg_rdp_lcl_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fepw_nu.fep_nu':
      offset=0x8014030400
      ret=f1_csr_lib.at_fep_nu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fepw_nu.dnr':
      offset=0x8014040000
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fepw_hnu.fep_hnu':
      offset=0x8014080000
      ret=f1_csr_lib.at_fep_hnu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fepw_hnu.dnr':
      offset=0x80140c0000
      ret=f1_csr_lib.at_dnr_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_fae':
      offset=0x8014400000
      ret=f1_csr_lib.at_nu_fae_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_mpg.fpg_misc':
      offset=0x8015400000
      ret=f1_csr_lib.at_fpg_misc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_mpg.fpg_sdif':
      offset=0x8015404000
      ret=f1_csr_lib.at_fpg_sdif_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_mpg.fpg_mpw':
      offset=0x8015480000
      ret=f1_csr_lib.at_fpg_mpw_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_mpg.nu_mpg_core':
      offset=0x8015600000
      ret=f1_csr_lib.at_nu_mpg_core_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fla':
      offset=0x8015800000
      ret=f1_csr_lib.at_fla_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_nmg':
      offset=0x8015c00000
      ret=f1_csr_lib.at_nu_nmg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nu_fnc':
      offset=0x8015c00800
      ret=f1_csr_lib.at_nu_fnc_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.hsu_flink_shim':
      offset=0x8017d00000
      ret=f1_csr_lib.at_hsu_flink_shim_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.hsu_hdma_pcie_framer':
      offset=0x8018d00000
      ret=f1_csr_lib.at_hsu_hdma_pcie_framer_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.hsu_tgt':
      offset=0x8019000000
      ret=f1_csr_lib.at_hsu_tgt_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.dma_hsu':
      offset=0x801a000000
      ret=f1_csr_lib.at_dma_hsu_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
############ HNU 1
   elif an == 'hnu.sse':
      offset=0x8800000000
      ret=f1_csr_lib.at_sse_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg0_ffe':
      offset=0x8804000000
      ret=f1_csr_lib.at_stg0_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg1_ffe':
      offset=0x8808000000
      ret=f1_csr_lib.at_stg1_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg2_ffe':
      offset=0x880c000000
      ret=f1_csr_lib.at_stg2_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg3_ffe':
      offset=0x8810000000
      ret=f1_csr_lib.at_stg3_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg4_ffe':
      offset=0x8814000000
      ret=f1_csr_lib.at_stg4_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.stg5_ffe':
      offset=0x8818000000
      ret=f1_csr_lib.at_stg5_ffe_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.nhp':
      offset=0x881c000000
      ret=f1_csr_lib.at_nhp_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.fms':
      offset=0x881c400000
      ret=f1_csr_lib.at_fms_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hnu.sfg':
      offset=0x881C800000
      ret=f1_csr_lib.at_sfg_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   else:
      print 'unrecognized/unimplemented an %s'%(an)
      ret=1

   if ret:
      print 'run_csr_at %s inst=%0d failed'%(an,inst)
   else:
      print 'run_csr_at %s inst=%0d passed'%(an,inst)
      
################################################################################
def all_csr_tests():
   run_csr_at('cdu')
   run_csr_at('pc_cmh')

################################################################################
def proc_arg():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('--verif_svr', nargs='?', type=str, default='cadence-pc-3', help='verif server. default %(default)s')
    args = parser.parse_args()

def main():
    proc_arg()
    load_lib()
    setup_verif_socket_client()
    connect_verif_server()
    readline.parse_and_bind('tab: complete')
    code.interact(local=globals())

if (__name__ == "__main__"):
    main()
