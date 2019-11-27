#!/bin/bash
IN_DIR=../../FunSDK/FunSDK/chip/s1/include/FunChip/csr2
OUT_DIR=.
LIST="dma_nu efp_rfp_lcl_csr2 efp_rfp_part1_csr2 epg_rdp_lcl_csr2 "`
	`"etdp_rf etfp_rf fcb fep_nu0 fep_nu1 "`
	`"ffe_rf_0 ffe_rf_1 ffe_rf_2 fms "`
	`"fpg_misc fpg_mpw fpg_sdif "`
	`"mpg_mpw nhp nu_fae nu_mpg_core nu_nmg nwqm prw "`
	`"psw_cfp psw_clm psw_irm psw_orm psw_pqm psw_prd psw_prm psw_pwr "`
	`"psw_sch psw_wred "`
	`"rf_prs_nu_erp rf_prs_nu_etp rf_prs_nu_fae rf_prs_nu_fpg "`
	`"sfg sse wro" 
for i in ${LIST}; do
	echo $i
	python s1_nu_intr_gen.py . ${IN_DIR}/$i.h
done
