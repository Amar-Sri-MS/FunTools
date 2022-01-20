#!/usr/bin/env python2.7
import os,sys,code
import rlcompleter, readline
import argparse
import logging
from verif_server import *

from ctypes import *

logger = logging.getLogger("csr_api_wrapper")
#logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

verif_svr_port=0

################################################################################
# some defines

def load_lib():
   global f1_csr_lib
   f1_csr_lib=cdll.LoadLibrary(args.csr_lib)

def setup_verif_socket_client():
   f1_csr_lib.csr_socket_set_dbg_level(0)
   #f1_csr_lib.csr_socket_set_dbg_level(0)

def connect_verif_server():
   f1_csr_lib.open_socket_port(verif_svr_port,args.verif_svr_hostname)

def run_verif_server():
   global verif_svr_port
   verif_svr_port=connect_verif_client_socket(port=args.verif_svr_port,chip_inst=args.tpod_bmc_chip_inst)
   logger.debug("port in={0} out={1}".format(args.verif_svr_port,verif_svr_port))
   set_i2c_dis(args.i2c_dis)
   if not args.i2c_dis:
      connect_dbgprobe(args.tpod,args.tpod_jtag,args.tpod_pcie,args.tpod_force)
   csrthread = CsrThread()
   csrthread.start()
   if args.verif_svr_verbose:
      logger2 = logging.getLogger("verif_server")
      logger2.setLevel(logging.DEBUG)

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
         logger.error('%s illegal instance=%0d'%(an,inst))
      offset=0x6002C00000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_wqsi_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_wqse':
      if inst != 0 and inst != 3:
         logger.error('%s illegal instance=%0d'%(an,inst))
      offset=0x6003000000 + (0x800000000*inst)
      ret=f1_csr_lib.at_hsu_wqse_run(c_ulonglong(offset),tmask,0xffffffff,maxerr,verb,seed)
   elif an == 'hsu.hsu_msc':
      if inst != 0 and inst != 3:
         logger.error('%s illegal instance=%0d'%(an,inst))
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
      logger.error('unrecognized/unimplemented an %s'%(an))
      ret=1

   if ret:
      logger.error('run_csr_at %s inst=%0d failed'%(an,inst))
   else:
      logger.info('run_csr_at %s inst=%0d passed'%(an,inst))
      
################################################################################
def all_csr_tests():
   run_csr_at('cdu')
   run_csr_at('pc_cmh')

class csr_api_wrapper(object):
   def __init__(self):
      self.f1_csr_slib=f1_csr_lib

   def aacs(self,port):
      f1_csr_lib.serdes_aacs(port)
      
  #uint32_t f1_config_chk_ca(uint32_t cluster);
   def f1_config_chk_ca(self,cluster):
      return f1_csr_lib.f1_config_chk_ca(cluster)

  #uint32_t f1_config_chk_cdu();
   def f1_config_chk_cdu(self):
      return f1_csr_lib.f1_config_chk_cdu()

  #uint32_t f1_idle_chk_ca(uint32_t cluster);
   def f1_idle_chk_ca(self,cluster):
      return f1_csr_lib.f1_idle_chk_ca(cluster)

  #uint32_t f1_idle_chk_cdu();
   def f1_idle_chk_cdu(self):
      return f1_csr_lib.f1_idle_chk_cdu();

  #void f1_stat_ca(uint32_t cluster);
   def f1_stat_ca(self,cluster):
      return f1_csr_lib.f1_stat_ca(cluster);

  #void f1_stat_cdu();
   def f1_stat_cdu(self):
      return f1_csr_lib.f1_stat_cdu();

  #void f1_stat_clear_ca(uint32_t cluster);
   def f1_stat_clear_ca(self,cluster):
      return f1_csr_lib.f1_stat_clear_ca(cluster);

  #void f1_stat_clear_cdu();
   def f1_stat_clear_cdu(self):
      return f1_csr_lib.f1_stat_clear_cdu();

  #void f1_debug_ca(uint32_t cluster);
   def f1_debug_ca(self,cluster):
      return f1_csr_lib.f1_debug_ca(cluster);

  #void f1_debug_cdu();
   def f1_debug_cdu(self):
      return f1_csr_lib.f1_debug_cdu();

  #uint32_t f1_intr_chk_ca(uint32_t cluster);
   def f1_intr_chk_ca(self,cluster):
      return f1_csr_lib.f1_intr_chk_ca(cluster);

  #uint32_t f1_intr_chk_cdu();
   def f1_intr_chk_cdu(self):
      return f1_csr_lib.f1_intr_chk_cdu();

  #uint32_t f1_idle_chk_bp_cnt(uint32_t cluster_mask, uint32_t pref_mask);
   def f1_idle_chk_bp_cnt(self,cluster_mask, pref_mask):
      return f1_csr_lib.f1_idle_chk_bp_cnt(cluster_mask, pref_mask);

  #uint32_t f1_idle_chk_wu_cred(uint32_t cluster_mask, uint32_t unit_mask, uint32_t per_vp_cred, uint32_t per_core_cred, uint32_t per_unit_cred);
   def f1_idle_chk_wu_cred(self,cluster_mask, unit_mask, per_vp_cred, per_core_cred, per_unit_cred):
      return f1_csr_lib.f1_idle_chk_wu_cred(cluster_mask, unit_mask, per_vp_cred, per_core_cred, per_unit_cred);

  #uint32_t f1_idle_chk_wu_index(uint32_t cluster_mask);
   def f1_idle_chk_wu_index(self,cluster_mask):
      return f1_csr_lib.f1_idle_chk_wu_index(cluster_mask);

  #uint32_t f1_pll_lock_status(uint32_t mask);
   def f1_pll_lock_status(self,mask):
      return f1_csr_lib.f1_pll_lock_status(mask);

#void f1_dnr_config(
#                   uint8_t coor_x,
#                   uint8_t coor_y,
#                   uint64_t ibuf_min_rsvd_credits_vc0,
#                   uint64_t ibuf_min_rsvd_credits_vc1,
#                   uint64_t ibuf_min_rsvd_credits_vc2,
#                   uint64_t ibuf_min_rsvd_credits_vc3,
#                   uint64_t ibuf_max_shared_credits,
#                   uint64_t ebuf_min_rsvd_credits_vc_set0,
#                   uint64_t ebuf_min_rsvd_credits_vc_set1,
#                   uint64_t ebuf_max_shared_credits,
#                   uint64_t ibuf_shared_credits_hysteresis,
#                   uint64_t ebuf_shared_credits_hysteresis,
#                   uint64_t inj_ibuf_min_rsvd_credits_vc0,
#                   uint64_t inj_ibuf_min_rsvd_credits_vc1,
#                   uint64_t inj_ibuf_min_rsvd_credits_vc2,
#                   uint64_t inj_ibuf_min_rsvd_credits_vc3
#                   ) {
   def f1_dnr_config(self,coor_x,coor_y,ibuf_min_rsvd_credits_vc0,ibuf_min_rsvd_credits_vc1,ibuf_min_rsvd_credits_vc2,ibuf_min_rsvd_credits_vc3,ibuf_max_shared_credits,ebuf_min_rsvd_credits_vc_set0,ebuf_min_rsvd_credits_vc_set1,ebuf_max_shared_credits,ibuf_shared_credits_hysteresis,ebuf_shared_credits_hysteresis,inj_ibuf_min_rsvd_credits_vc0,inj_ibuf_min_rsvd_credits_vc1,inj_ibuf_min_rsvd_credits_vc2,inj_ibuf_min_rsvd_credits_vc3):
      return f1_csr_lib.f1_dnr_config(c_uint8(coor_x),c_uint8(coor_y),c_uint64(ibuf_min_rsvd_credits_vc0),c_uint64(ibuf_min_rsvd_credits_vc1),c_uint64(ibuf_min_rsvd_credits_vc2),c_uint64(ibuf_min_rsvd_credits_vc3),c_uint64(ibuf_max_shared_credits),c_uint64(ebuf_min_rsvd_credits_vc_set0),c_uint64(ebuf_min_rsvd_credits_vc_set1),c_uint64(ebuf_max_shared_credits),c_uint64(ibuf_shared_credits_hysteresis),c_uint64(ebuf_shared_credits_hysteresis),c_uint64(inj_ibuf_min_rsvd_credits_vc0),c_uint64(inj_ibuf_min_rsvd_credits_vc1),c_uint64(inj_ibuf_min_rsvd_credits_vc2),c_uint64(inj_ibuf_min_rsvd_credits_vc3))

#void f1_dnr_route_config(
#                         uint8_t coor_x,
#                         uint8_t coor_y,
#                         uint64_t val_o1turn_en,
#                         uint64_t val_adaptive_en,
#                         uint64_t val_xy_en,
#                         uint64_t val_adaptive_vc_sel_en,
#                         uint64_t val_o1turn_vc_sel_en) {
   def f1_dnr_route_config(self,coor_x,coor_y,val_o1turn_en,val_adaptive_en,val_xy_en,val_adaptive_vc_sel_en,val_o1turn_vc_sel_en):
      return f1_csr_lib.f1_dnr_route_config(c_uint8(coor_x),c_uint8(coor_y),c_uint64(val_o1turn_en),c_uint64(val_adaptive_en),c_uint64(val_xy_en),c_uint64(val_adaptive_vc_sel_en),c_uint64(val_o1turn_vc_sel_en))

#void f1_dnr_stat_probe_config(
#                         uint8_t coor_x,
#                         uint8_t coor_y,
#                         uint8_t on_port, // 0 = E, 1 = W, 2 = N, 3 = S, 4 = H
#                         uint8_t on_vcset, // 0 - coh, 1 - non-coh
#                         uint64_t val_vcid, uint64_t val_vcid_mask,
#                         uint64_t val_so, uint64_t val_so_mask,
#                         uint64_t val_dgid, uint64_t val_dgid_mask,
#                         uint64_t val_out_port, uint64_t val_out_port_mask) {
   def f1_dnr_stat_probe_config(self,coor_x,coor_y,on_port,on_vcset,val_vcid,val_vcid_mask,val_so,val_so_mask,val_dgid,val_dgid_mask,val_out_port,val_out_port_mask):
      return f1_csr_lib.f1_dnr_stat_probe_config(c_uint8(coor_x),c_uint8(coor_y),c_uint8(on_port),c_uint8(on_vcset),c_uint64(val_vcid),c_uint64(val_vcid_mask),c_uint64(val_so),c_uint64(val_so_mask),c_uint64(val_dgid),c_uint64(val_dgid_mask),c_uint64(val_out_port),c_uint64(val_out_port_mask))

#void f1_dnr_stat_probe_counter (
#                         uint8_t coor_x,
#                         uint8_t coor_y,
#                         uint8_t on_port, // 0 = E, 1 = W, 2 = N, 3 = S, 4 = H
#                         uint8_t on_vcset // 0 - coh, 1 - non-coh
#                         ) {
   def f1_dnr_stat_probe_counter(self,coor_x,coor_y,on_port,on_vcset):
      return f1_csr_lib.f1_dnr_stat_probe_counter(c_uint8(coor_x),c_uint8(coor_y),c_uint8(on_port),c_uint8(on_vcset))

#void f1_stat_en_fep(uint8_t coor_x, uint8_t coor_y, uint8_t vc_en) {
   def f1_stat_en_fep(self,coor_x, coor_y, vc_en):
      return f1_csr_lib.f1_stat_en_fep(c_uint8(coor_x),c_uint8( coor_y),c_uint8( vc_en))

#void f1_stat_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_stat_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_stat_fep(c_uint8(coor_x),c_uint8( coor_y))

#void f1_stat_clear_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_stat_clear_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_stat_clear_fep(c_uint8(coor_x),c_uint8( coor_y))

#uint32_t f1_config_chk_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_config_chk_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_config_chk_fep(c_uint8(coor_x),c_uint8( coor_y))

#uint32_t f1_debug_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_debug_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_debug_fep(c_uint8(coor_x),c_uint8( coor_y))

#uint32_t f1_eot_chk_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_eot_chk_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_eot_chk_fep(c_uint8(coor_x),c_uint8( coor_y))

#uint32_t f1_intr_chk_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_intr_chk_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_intr_chk_fep(c_uint8(coor_x),c_uint8( coor_y))

#uint32_t f1_intr_clear_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_intr_clear_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_intr_clear_fep(c_uint8(coor_x),c_uint8( coor_y))

#void f1_err_stat_clear_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_err_stat_clear_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_err_stat_clear_fep(c_uint8(coor_x),c_uint8( coor_y))

#void f1_err_stat_fep(uint8_t coor_x, uint8_t coor_y) {
   def f1_err_stat_fep(self,coor_x, coor_y):
      return f1_csr_lib.f1_err_stat_fep(c_uint8(coor_x),c_uint8( coor_y))

#void f1_config_snx(uint8_t coor_x, uint8_t coor_y, uint8_t is_cdu) {
   def f1_config_snx(self,coor_x, coor_y, is_cdu):
      return f1_csr_lib.f1_config_snx(c_uint8(coor_x),c_uint8( coor_y),c_uint8( is_cdu))

#void f1_stat_snx(uint8_t coor_x, uint8_t coor_y, uint8_t is_cdu, uint8_t is_rx) {
   def f1_stat_snx(self,coor_x, coor_y, is_cdu, is_rx):
      return f1_csr_lib.f1_stat_snx(c_uint8(coor_x),c_uint8( coor_y),c_uint8( is_cdu),c_uint8( is_rx))

   def f1_chk_intr(self):
      f1_csr_lib.cmh_chk_interrupts(1,8)
      for i in range(8):
         f1_csr_lib.cmh_chk_interrupts(0,i) #is cc , clus
         f1_csr_lib.f1_intr_chk_ca(i)
         f1_csr_lib.f1_rgx_check_interrupts(i) #clus
      f1_csr_lib.f1_eqm_check_interrupts()
      f1_csr_lib.f1_sec_check_interrupts()
      f1_csr_lib.f1_intr_chk_cdu()
      for x in range(5):
         for y in range(5):
            f1_csr_lib.f1_intr_chk_fep(x,y) #x,y
   def f1_chk_intr_hu(self):
      f1_csr_lib.hsu_api_print_fmr_intr_status(0) #ring
      f1_csr_lib.hsu_api_print_hudma_intr_status(0)
      f1_csr_lib.hsu_api_print_msc_intr_status(0)
      f1_csr_lib.hsu_api_print_pta_intr_status(0)
      f1_csr_lib.hsu_api_print_pwp_intr_status(0)
      f1_csr_lib.hsu_api_print_tgt_intr_status(0)
      f1_csr_lib.hsu_api_print_wqse_intr_status(0)
      f1_csr_lib.hsu_api_print_wqsi_intr_status(0)
   def f1_chk_intr_nu(self):
      f1_csr_lib.nu_efp_rfp_interrupt(0,0) #shape,filter
      f1_csr_lib.nu_epg_rdp_interrupt(0,0)
      f1_csr_lib.nu_erp_interrupt(0,0)
      f1_csr_lib.nu_etdp_interrupt(0,0)
      f1_csr_lib.nu_etfp_interrupt(0,0)
      f1_csr_lib.nu_etp_interrupt(0,0)
      f1_csr_lib.nu_fae_interrupt(0,0)
      f1_csr_lib.nu_fcb_interrupt_print(0,0)
      f1_csr_lib.nu_fpg_interrupt(0,0)
      f1_csr_lib.nu_prw_interrupt(0,0)
      f1_csr_lib.nu_psw_interrupt(0,0)
      f1_csr_lib.nu_sfg_interrupt(0,0)
      f1_csr_lib.nu_wro_interrupt(0,0)

################################################################################
def auto_int(x):
    return int(x, 0)

def proc_arg():
    global args, i2c_dis
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_verif_svr', action='store_true', default=False, help='run own verif server. default %(default)s')
    parser.add_argument('--run_aacs_port', nargs='?', type=auto_int, default=0, help='run aacs server port. default %(default)s not run')
    parser.add_argument('--verif_svr_hostname', nargs='?', type=str, default='localhost', help='verif server hostname. default %(default)s')
    parser.add_argument('--verif_svr_port', nargs='?', type=auto_int, default=0, help='verif server port. default %(default)s auto select')
    parser.add_argument('--verif_svr_verbose', action='store_true', default=False, help='verif server verbose. default %(default)s')
    parser.add_argument('--csr_lib', nargs='?', type=str, default="./f1_csr_slib.so", help='f1_csr_slib.so location. default %(default)s')
    parser.add_argument('--i2c_dis', action='store_true', default=False, help='i2cproxy connection disable. default %(default)d')
    parser.add_argument('--tpod', nargs='?', type=str, default='TPOD4', help='TPOD name. default %(default)s')
    parser.add_argument('--tpod_force', action='store_true', default=False, help='TPOD force mode. default %(default)s')
    parser.add_argument('--tpod_jtag', action='store_true', default=False, help='TPOD JTAG mode. default %(default)s')
    parser.add_argument('--tpod_pcie', action='store_true', default=False, help='TPOD PCIE mode. default %(default)s')
    parser.add_argument('--tpod_bmc_chip_inst', nargs='?', type=auto_int, default=0, help='TPOD chip_inst used in bmc mode. default %(default)s')
    args = parser.parse_args()
    if args.tpod_jtag and args.tpod_pcie:
       logger.error("tpod both jtag and pcie mode specified")
       sys.exit(1)
    i2c_dis=args.i2c_dis

def main():
   global f1w
   proc_arg()
   load_lib()
   f1w=csr_api_wrapper()
   setup_verif_socket_client()
   if (args.run_verif_svr):
      run_verif_server()
   connect_verif_server()
   if (args.run_aacs_port):
      try:
         f1w.aacs(args.run_aacs_port)
      except:
         logger.error("aacs error")
         sys.exit(1)
   readline.parse_and_bind('tab: complete')
   code.interact(local=globals())

if (__name__ == "__main__"):
    main()
