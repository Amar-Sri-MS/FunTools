/*
 *  csr_gen.cpp
 *
 *  !!!!!AUTO-GENERATED FILE. DO NOT EDIT!!!!
 *
 *  Copyright 2018 Fungible Inc. All rights reserved.
 */

#include "csr.h"

F1NS::F1NS(rd_fptr rd_fn, wr_fptr wr_fn):
m_rd_fn(rd_fn), m_wr_fn(wr_fn) {
   ring_coll_t cc_rng;
cc_rng.add_ring(0, 0x4800000000);
sys_rings["CC"] = cc_rng;
ring_coll_t hnu_rng;
hnu_rng.add_ring(0, 0x8000000000);
hnu_rng.add_ring(1, 0x8800000000);
sys_rings["HNU"] = hnu_rng;
ring_coll_t hsu_rng;
hsu_rng.add_ring(0, 0x6000000000);
hsu_rng.add_ring(1, 0x6800000000);
hsu_rng.add_ring(2, 0x7000000000);
hsu_rng.add_ring(3, 0x7800000000);
sys_rings["HSU"] = hsu_rng;
ring_coll_t mio2_rng;
mio2_rng.add_ring(0, 0xB800000000);
sys_rings["MIO2"] = mio2_rng;
ring_coll_t mio_rng;
mio_rng.add_ring(0, 0xB000000000);
sys_rings["MIO"] = mio_rng;
ring_coll_t mud_rng;
mud_rng.add_ring(0, 0xA000000000);
mud_rng.add_ring(1, 0xA800000000);
sys_rings["MUD"] = mud_rng;
ring_coll_t muh_rng;
muh_rng.add_ring(0, 0x9000000000);
muh_rng.add_ring(1, 0x9800000000);
sys_rings["MUH"] = muh_rng;
ring_coll_t nu_rng;
nu_rng.add_ring(0, 0x5000000000);
{
 // BEGIN fpg_prs 
auto fpg_prs_0 = nu_rng[0].add_an({"fpg","fpg_prs"}, 0x0, 6, 0x1000000);
fld_map_t fpg_prs_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_prs_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_timeout_thresh_cfg", fpg_prs_timeout_thresh_cfg_prop);
fld_map_t fpg_prs_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_prs_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_timedout_sta", fpg_prs_timedout_sta_prop);
fld_map_t fpg_prs_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_prs_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_timeout_clr", fpg_prs_timeout_clr_prop);
fld_map_t fpg_prs_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_prs_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_features", fpg_prs_features_prop);
fld_map_t fpg_prs_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_prs_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_spare_pio", fpg_prs_spare_pio_prop);
fld_map_t fpg_prs_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_prs_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_scratchpad", fpg_prs_scratchpad_prop);
fld_map_t fpg_prs_sram_log_err {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto fpg_prs_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_sram_log_err),
0x80,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_sram_log_err", fpg_prs_sram_log_err_prop);
fld_map_t fpg_prs_sram_log_syndrome {
CREATE_ENTRY("val", 0, 10),
CREATE_ENTRY("__rsvd", 10, 54)
};auto fpg_prs_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_sram_log_syndrome),
0x88,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_sram_log_syndrome", fpg_prs_sram_log_syndrome_prop);
fld_map_t fpg_prs_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto fpg_prs_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_sram_log_addr),
0x90,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_sram_log_addr", fpg_prs_sram_log_addr_prop);
fld_map_t fpg_prs_mem_err_inj_cfg {
CREATE_ENTRY("prs_dsp_fifo_mem0", 0, 1),
CREATE_ENTRY("prs_dsp_fifo_mem1", 1, 1),
CREATE_ENTRY("prs_dsp_fifo_mem2", 2, 1),
CREATE_ENTRY("prs_dsp_fifo_mem3", 3, 1),
CREATE_ENTRY("prs_rob_prv_mem", 4, 1),
CREATE_ENTRY("prs_action_mem0", 5, 1),
CREATE_ENTRY("prs_action_mem1", 6, 1),
CREATE_ENTRY("prs_action_mem2", 7, 1),
CREATE_ENTRY("prs_action_mem3", 8, 1),
CREATE_ENTRY("err_type", 9, 1),
CREATE_ENTRY("__rsvd", 10, 54)
};auto fpg_prs_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_mem_err_inj_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_mem_err_inj_cfg", fpg_prs_mem_err_inj_cfg_prop);
fld_map_t prs_dsp_dfifo_mem_af_thold {
CREATE_ENTRY("data", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
fld_map_t prs_intf_cfg {
CREATE_ENTRY("intf0mode", 0, 2),
CREATE_ENTRY("intf1mode", 2, 2),
CREATE_ENTRY("intf2mode", 4, 2),
CREATE_ENTRY("intf3mode", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prs_intf_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_intf_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_intf_cfg", prs_intf_cfg_prop);
fld_map_t prs_err_chk_en {
CREATE_ENTRY("outer_ipv4_checksum", 0, 1),
CREATE_ENTRY("inner_ipv4_checksum", 1, 1),
CREATE_ENTRY("no_tcam_match", 2, 1),
CREATE_ENTRY("parser_timeout", 3, 1),
CREATE_ENTRY("prv_oor", 4, 1),
CREATE_ENTRY("pkt_ptr_oor", 5, 1),
CREATE_ENTRY("hdr_buf_overflow", 6, 1),
CREATE_ENTRY("hdr_byte_oor", 7, 1),
CREATE_ENTRY("gp_byte_oor", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto prs_err_chk_en_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_chk_en),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_err_chk_en", prs_err_chk_en_prop);
fld_map_t prs_err_tcode0 {
CREATE_ENTRY("outer_ipv4_checksum", 0, 7),
CREATE_ENTRY("inner_ipv4_checksum", 7, 7),
CREATE_ENTRY("no_tcam_match", 14, 7),
CREATE_ENTRY("parser_timeout", 21, 7),
CREATE_ENTRY("prv_oor", 28, 7),
CREATE_ENTRY("pkt_ptr_oor", 35, 7),
CREATE_ENTRY("hdr_buf_overflow", 42, 7),
CREATE_ENTRY("hdr_byte_oor", 49, 7),
CREATE_ENTRY("__rsvd", 56, 8)
};auto prs_err_tcode0_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode0),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
fld_map_t prs_err_tcode1 {
CREATE_ENTRY("gp_byte_oor", 0, 7),
CREATE_ENTRY("action_mem_perr", 7, 7),
CREATE_ENTRY("__rsvd", 14, 50)
};auto prs_err_tcode1_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode1),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
fld_map_t prs_max_lu_cycle_cfg {
CREATE_ENTRY("use_fixed", 0, 1),
CREATE_ENTRY("fixed_cnt", 1, 8),
CREATE_ENTRY("init_cycle_cnt", 9, 6),
CREATE_ENTRY("acct_for_prv_bg_rd", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
fld_map_t prs_stream_cfg {
CREATE_ENTRY("fixed_stream_en", 0, 1),
CREATE_ENTRY("intf0_stream", 1, 2),
CREATE_ENTRY("intf1_stream", 3, 2),
CREATE_ENTRY("intf2_stream", 5, 2),
CREATE_ENTRY("intf3_stream", 7, 2),
CREATE_ENTRY("__rsvd", 9, 55)
};auto prs_stream_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_stream_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
fld_map_t prs_static_ctx_sel {
CREATE_ENTRY("use_one_ctx", 0, 1),
CREATE_ENTRY("ctx_num", 1, 2),
CREATE_ENTRY("__rsvd", 3, 61)
};auto prs_static_ctx_sel_prop = csr_prop_t(
std::make_shared<csr_s>(prs_static_ctx_sel),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
fld_map_t prs_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
fld_map_t prs_hdb_fifo_empty {
CREATE_ENTRY("ctx0", 0, 1),
CREATE_ENTRY("ctx1", 1, 1),
CREATE_ENTRY("ctx2", 2, 1),
CREATE_ENTRY("ctx3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto prs_hdb_fifo_empty_prop = csr_prop_t(
std::make_shared<csr_s>(prs_hdb_fifo_empty),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "prs_hdb_fifo_empty", prs_hdb_fifo_empty_prop);
 // END fpg_prs 
}
{
 // BEGIN prw 
auto prw_0 = nu_rng[0].add_an({"fpg","prw"}, 0x800000, 6, 0x1000000);
fld_map_t prw_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto prw_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prw_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_timeout_thresh_cfg", prw_timeout_thresh_cfg_prop);
fld_map_t prw_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto prw_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(prw_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_timedout_sta", prw_timedout_sta_prop);
fld_map_t prw_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto prw_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(prw_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_timeout_clr", prw_timeout_clr_prop);
fld_map_t prw_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto prw_features_prop = csr_prop_t(
std::make_shared<csr_s>(prw_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_features", prw_features_prop);
fld_map_t prw_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto prw_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(prw_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_spare_pio", prw_spare_pio_prop);
fld_map_t prw_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto prw_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(prw_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_scratchpad", prw_scratchpad_prop);
fld_map_t prw_holdoff_thr {
CREATE_ENTRY("strm0", 0, 14),
CREATE_ENTRY("strm1", 14, 14),
CREATE_ENTRY("strm2", 28, 14),
CREATE_ENTRY("strm3", 42, 14),
CREATE_ENTRY("__rsvd", 56, 8)
};auto prw_holdoff_thr_prop = csr_prop_t(
std::make_shared<csr_s>(prw_holdoff_thr),
0x80,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_holdoff_thr", prw_holdoff_thr_prop);
fld_map_t prw_holdoff_timer {
CREATE_ENTRY("strm0", 0, 16),
CREATE_ENTRY("strm1", 16, 16),
CREATE_ENTRY("strm2", 32, 16),
CREATE_ENTRY("strm3", 48, 16)
};auto prw_holdoff_timer_prop = csr_prop_t(
std::make_shared<csr_s>(prw_holdoff_timer),
0x88,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_holdoff_timer", prw_holdoff_timer_prop);
fld_map_t prw_disp_wrr_wt {
CREATE_ENTRY("use_sw_weights", 0, 1),
CREATE_ENTRY("strm0", 1, 5),
CREATE_ENTRY("strm1", 6, 5),
CREATE_ENTRY("strm2", 11, 5),
CREATE_ENTRY("strm3", 16, 5),
CREATE_ENTRY("__rsvd", 21, 43)
};auto prw_disp_wrr_wt_prop = csr_prop_t(
std::make_shared<csr_s>(prw_disp_wrr_wt),
0x90,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_disp_wrr_wt", prw_disp_wrr_wt_prop);
fld_map_t prw_lfa_ethertype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prw_lfa_ethertype_prop = csr_prop_t(
std::make_shared<csr_s>(prw_lfa_ethertype),
0x98,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_lfa_ethertype", prw_lfa_ethertype_prop);
fld_map_t prw_vlan_ethertype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prw_vlan_ethertype_prop = csr_prop_t(
std::make_shared<csr_s>(prw_vlan_ethertype),
0xA0,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_vlan_ethertype", prw_vlan_ethertype_prop);
fld_map_t prw_exe_control {
CREATE_ENTRY("ignore_psw_spd_f", 0, 1),
CREATE_ENTRY("enable_2byte_addition", 1, 1),
CREATE_ENTRY("corrupt_crc_if_ibp_out_of_bound", 2, 1),
CREATE_ENTRY("corrupt_crc_if_ebp_out_of_bound", 3, 1),
CREATE_ENTRY("corrupt_crc_if_instr_looking_at_bytes_beyond_pkt_len", 4, 1),
CREATE_ENTRY("corrupt_crc_if_new_head_sz_out_of_range", 5, 1),
CREATE_ENTRY("corrupt_crc_if_move_sz_greater_than_64byte", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto prw_exe_control_prop = csr_prop_t(
std::make_shared<csr_s>(prw_exe_control),
0xA8,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_exe_control", prw_exe_control_prop);
fld_map_t prw_mem_err_inj_cfg {
CREATE_ENTRY("prw_rdm_even_mem", 0, 1),
CREATE_ENTRY("prw_rdm_odd_mem", 1, 1),
CREATE_ENTRY("prw_hcb_mem", 2, 1),
CREATE_ENTRY("prw_bcb_mem", 3, 1),
CREATE_ENTRY("prw_nhcb_mem", 4, 1),
CREATE_ENTRY("err_type", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto prw_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prw_mem_err_inj_cfg),
0xB0,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_mem_err_inj_cfg", prw_mem_err_inj_cfg_prop);
fld_map_t prw_pkt_capture_control {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("en_capture_with_snapshot_flag", 1, 1),
CREATE_ENTRY("en_capture_for_ttl_zero", 2, 1),
CREATE_ENTRY("en_capture_for_ip_ver_err", 3, 1),
CREATE_ENTRY("capture_modified_hd", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto prw_pkt_capture_control_prop = csr_prop_t(
std::make_shared<csr_s>(prw_pkt_capture_control),
0xB8,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_pkt_capture_control", prw_pkt_capture_control_prop);
fld_map_t prw_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prw_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prw_fla_ring_module_id_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_fla_ring_module_id_cfg", prw_fla_ring_module_id_cfg_prop);
fld_map_t prw_pkt_capture_log {
CREATE_ENTRY("strm", 0, 2),
CREATE_ENTRY("wall_clock_time", 2, 32),
CREATE_ENTRY("__rsvd", 34, 30)
};auto prw_pkt_capture_log_prop = csr_prop_t(
std::make_shared<csr_s>(prw_pkt_capture_log),
0x150,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_pkt_capture_log", prw_pkt_capture_log_prop);
fld_map_t prw_sram_log_err {
CREATE_ENTRY("val", 0, 10),
CREATE_ENTRY("__rsvd", 10, 54)
};auto prw_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(prw_sram_log_err),
0x158,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_sram_log_err", prw_sram_log_err_prop);
fld_map_t prw_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prw_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(prw_sram_log_syndrome),
0x160,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_sram_log_syndrome", prw_sram_log_syndrome_prop);
fld_map_t prw_sram_log_addr {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prw_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(prw_sram_log_addr),
0x168,
CSR_TYPE::REG,
1);
add_csr(prw_0, "prw_sram_log_addr", prw_sram_log_addr_prop);
 // END prw 
}
{
 // BEGIN prw 
auto prw_1 = nu_rng[0].add_an({"epg_rdp","prw"}, 0x14020000, 3, 0x3000000);
fld_map_t prw_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto prw_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prw_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_timeout_thresh_cfg", prw_timeout_thresh_cfg_prop);
fld_map_t prw_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto prw_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(prw_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_timedout_sta", prw_timedout_sta_prop);
fld_map_t prw_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto prw_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(prw_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_timeout_clr", prw_timeout_clr_prop);
fld_map_t prw_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto prw_features_prop = csr_prop_t(
std::make_shared<csr_s>(prw_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_features", prw_features_prop);
fld_map_t prw_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto prw_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(prw_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_spare_pio", prw_spare_pio_prop);
fld_map_t prw_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto prw_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(prw_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_scratchpad", prw_scratchpad_prop);
fld_map_t prw_holdoff_thr {
CREATE_ENTRY("strm0", 0, 14),
CREATE_ENTRY("strm1", 14, 14),
CREATE_ENTRY("strm2", 28, 14),
CREATE_ENTRY("strm3", 42, 14),
CREATE_ENTRY("__rsvd", 56, 8)
};auto prw_holdoff_thr_prop = csr_prop_t(
std::make_shared<csr_s>(prw_holdoff_thr),
0x80,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_holdoff_thr", prw_holdoff_thr_prop);
fld_map_t prw_holdoff_timer {
CREATE_ENTRY("strm0", 0, 16),
CREATE_ENTRY("strm1", 16, 16),
CREATE_ENTRY("strm2", 32, 16),
CREATE_ENTRY("strm3", 48, 16)
};auto prw_holdoff_timer_prop = csr_prop_t(
std::make_shared<csr_s>(prw_holdoff_timer),
0x88,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_holdoff_timer", prw_holdoff_timer_prop);
fld_map_t prw_disp_wrr_wt {
CREATE_ENTRY("use_sw_weights", 0, 1),
CREATE_ENTRY("strm0", 1, 5),
CREATE_ENTRY("strm1", 6, 5),
CREATE_ENTRY("strm2", 11, 5),
CREATE_ENTRY("strm3", 16, 5),
CREATE_ENTRY("__rsvd", 21, 43)
};auto prw_disp_wrr_wt_prop = csr_prop_t(
std::make_shared<csr_s>(prw_disp_wrr_wt),
0x90,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_disp_wrr_wt", prw_disp_wrr_wt_prop);
fld_map_t prw_lfa_ethertype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prw_lfa_ethertype_prop = csr_prop_t(
std::make_shared<csr_s>(prw_lfa_ethertype),
0x98,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_lfa_ethertype", prw_lfa_ethertype_prop);
fld_map_t prw_vlan_ethertype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prw_vlan_ethertype_prop = csr_prop_t(
std::make_shared<csr_s>(prw_vlan_ethertype),
0xA0,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_vlan_ethertype", prw_vlan_ethertype_prop);
fld_map_t prw_exe_control {
CREATE_ENTRY("ignore_psw_spd_f", 0, 1),
CREATE_ENTRY("enable_2byte_addition", 1, 1),
CREATE_ENTRY("corrupt_crc_if_ibp_out_of_bound", 2, 1),
CREATE_ENTRY("corrupt_crc_if_ebp_out_of_bound", 3, 1),
CREATE_ENTRY("corrupt_crc_if_instr_looking_at_bytes_beyond_pkt_len", 4, 1),
CREATE_ENTRY("corrupt_crc_if_new_head_sz_out_of_range", 5, 1),
CREATE_ENTRY("corrupt_crc_if_move_sz_greater_than_64byte", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto prw_exe_control_prop = csr_prop_t(
std::make_shared<csr_s>(prw_exe_control),
0xA8,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_exe_control", prw_exe_control_prop);
fld_map_t prw_mem_err_inj_cfg {
CREATE_ENTRY("prw_rdm_even_mem", 0, 1),
CREATE_ENTRY("prw_rdm_odd_mem", 1, 1),
CREATE_ENTRY("prw_hcb_mem", 2, 1),
CREATE_ENTRY("prw_bcb_mem", 3, 1),
CREATE_ENTRY("prw_nhcb_mem", 4, 1),
CREATE_ENTRY("err_type", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto prw_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prw_mem_err_inj_cfg),
0xB0,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_mem_err_inj_cfg", prw_mem_err_inj_cfg_prop);
fld_map_t prw_pkt_capture_control {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("en_capture_with_snapshot_flag", 1, 1),
CREATE_ENTRY("en_capture_for_ttl_zero", 2, 1),
CREATE_ENTRY("en_capture_for_ip_ver_err", 3, 1),
CREATE_ENTRY("capture_modified_hd", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto prw_pkt_capture_control_prop = csr_prop_t(
std::make_shared<csr_s>(prw_pkt_capture_control),
0xB8,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_pkt_capture_control", prw_pkt_capture_control_prop);
fld_map_t prw_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prw_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prw_fla_ring_module_id_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_fla_ring_module_id_cfg", prw_fla_ring_module_id_cfg_prop);
fld_map_t prw_pkt_capture_log {
CREATE_ENTRY("strm", 0, 2),
CREATE_ENTRY("wall_clock_time", 2, 32),
CREATE_ENTRY("__rsvd", 34, 30)
};auto prw_pkt_capture_log_prop = csr_prop_t(
std::make_shared<csr_s>(prw_pkt_capture_log),
0x150,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_pkt_capture_log", prw_pkt_capture_log_prop);
fld_map_t prw_sram_log_err {
CREATE_ENTRY("val", 0, 10),
CREATE_ENTRY("__rsvd", 10, 54)
};auto prw_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(prw_sram_log_err),
0x158,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_sram_log_err", prw_sram_log_err_prop);
fld_map_t prw_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prw_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(prw_sram_log_syndrome),
0x160,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_sram_log_syndrome", prw_sram_log_syndrome_prop);
fld_map_t prw_sram_log_addr {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prw_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(prw_sram_log_addr),
0x168,
CSR_TYPE::REG,
1);
add_csr(prw_1, "prw_sram_log_addr", prw_sram_log_addr_prop);
 // END prw 
}
{
 // BEGIN fpg_misc 
auto fpg_misc_0 = nu_rng[0].add_an({"fpg","fpg_misc"}, 0x810000, 6, 0x1000000);
fld_map_t fpg_misc_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_misc_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_timeout_thresh_cfg", fpg_misc_timeout_thresh_cfg_prop);
fld_map_t fpg_misc_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_timedout_sta", fpg_misc_timedout_sta_prop);
fld_map_t fpg_misc_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_timeout_clr", fpg_misc_timeout_clr_prop);
fld_map_t fpg_misc_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_misc_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_features", fpg_misc_features_prop);
fld_map_t fpg_misc_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_misc_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_spare_pio", fpg_misc_spare_pio_prop);
fld_map_t fpg_misc_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_misc_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_scratchpad", fpg_misc_scratchpad_prop);
fld_map_t fpg_misc_stream_speed {
CREATE_ENTRY("stream_speed", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_misc_stream_speed_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_stream_speed),
0x80,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_stream_speed", fpg_misc_stream_speed_prop);
fld_map_t fpg_misc_get_flit_tdm_en {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_get_flit_tdm_en_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_get_flit_tdm_en),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_get_flit_tdm_en", fpg_misc_get_flit_tdm_en_prop);
fld_map_t fpg_misc_get_flit_tdm_clnd {
CREATE_ENTRY("stream_num", 0, 2),
CREATE_ENTRY("vld", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto fpg_misc_get_flit_tdm_clnd_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_get_flit_tdm_clnd),
0xA8,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_get_flit_tdm_clnd", fpg_misc_get_flit_tdm_clnd_prop);
fld_map_t fpg_misc_tx_max_pkt_len {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto fpg_misc_tx_max_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_max_pkt_len),
0xC8,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_max_pkt_len", fpg_misc_tx_max_pkt_len_prop);
fld_map_t fpg_misc_tx_min_pkt_len {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_tx_min_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_min_pkt_len),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_min_pkt_len", fpg_misc_tx_min_pkt_len_prop);
fld_map_t fpg_misc_tx_ptp_cfg {
CREATE_ENTRY("peer_delay_en", 0, 4),
CREATE_ENTRY("one_step_en", 4, 4),
CREATE_ENTRY("timestamp_overwrite_en", 8, 4),
CREATE_ENTRY("timestamp_capture_en", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_ptp_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_ptp_cfg),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_ptp_cfg", fpg_misc_tx_ptp_cfg_prop);
fld_map_t fpg_misc_mac0_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac0_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac0_peer_delay_cfg),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_mac0_peer_delay_cfg", fpg_misc_mac0_peer_delay_cfg_prop);
fld_map_t fpg_misc_mac1_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac1_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac1_peer_delay_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_mac1_peer_delay_cfg", fpg_misc_mac1_peer_delay_cfg_prop);
fld_map_t fpg_misc_mac2_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac2_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac2_peer_delay_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_mac2_peer_delay_cfg", fpg_misc_mac2_peer_delay_cfg_prop);
fld_map_t fpg_misc_mac3_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac3_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac3_peer_delay_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_mac3_peer_delay_cfg", fpg_misc_mac3_peer_delay_cfg_prop);
fld_map_t fpg_misc_tx_pfc_ctrl {
CREATE_ENTRY("sw_override_en", 0, 16),
CREATE_ENTRY("sw_override_val", 16, 16),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fpg_misc_tx_pfc_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_pfc_ctrl),
0x118,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_pfc_ctrl", fpg_misc_tx_pfc_ctrl_prop);
fld_map_t fpg_misc_tx_failure_bcast_ctrl {
CREATE_ENTRY("failure_bcast_en", 0, 1),
CREATE_ENTRY("use_local_fault_status", 1, 1),
CREATE_ENTRY("use_rem_fault_status", 2, 1),
CREATE_ENTRY("use_li_fault_status", 3, 1),
CREATE_ENTRY("use_pcs_link_status", 4, 1),
CREATE_ENTRY("use_serdes_signal_ok", 5, 1),
CREATE_ENTRY("sw_triggered_fault_bcast", 6, 1),
CREATE_ENTRY("failure_bcast_delay_timer", 7, 16),
CREATE_ENTRY("__rsvd", 23, 41)
};auto fpg_misc_tx_failure_bcast_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_failure_bcast_ctrl),
0x138,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_failure_bcast_ctrl", fpg_misc_tx_failure_bcast_ctrl_prop);
fld_map_t fpg_misc_tx_fsf_frame_data {
CREATE_ENTRY("gph_index", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_fsf_frame_data_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_data),
0x158,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_data", fpg_misc_tx_fsf_frame_data_prop);
fld_map_t fpg_misc_tx_fsf_xmit_en {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_tx_fsf_xmit_en_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_xmit_en),
0x218,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_fsf_xmit_en", fpg_misc_tx_fsf_xmit_en_prop);
fld_map_t fpg_misc_tx_fsf_strm_is_glb_link {
CREATE_ENTRY("val", 0, 24),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fpg_misc_tx_fsf_strm_is_glb_link_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_strm_is_glb_link),
0x238,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_fsf_strm_is_glb_link", fpg_misc_tx_fsf_strm_is_glb_link_prop);
fld_map_t fpg_misc_tx_fsf_frame_opcode {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_fsf_frame_opcode_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_opcode),
0x240,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_opcode", fpg_misc_tx_fsf_frame_opcode_prop);
fld_map_t fpg_misc_tx_fsf_frame_dmac {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fpg_misc_tx_fsf_frame_dmac_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_dmac),
0x248,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_dmac", fpg_misc_tx_fsf_frame_dmac_prop);
fld_map_t fpg_misc_tx_fsf_frame_ethertype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_fsf_frame_ethertype_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_ethertype),
0x250,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_ethertype", fpg_misc_tx_fsf_frame_ethertype_prop);
fld_map_t fpg_misc_psw_tdm_clnd {
CREATE_ENTRY("stream_num", 0, 2),
CREATE_ENTRY("vld", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto fpg_misc_psw_tdm_clnd_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_psw_tdm_clnd),
0x318,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_psw_tdm_clnd", fpg_misc_psw_tdm_clnd_prop);
fld_map_t fpg_misc_stream_rate_limit {
CREATE_ENTRY("credits_per_interval", 0, 13),
CREATE_ENTRY("interval", 13, 3),
CREATE_ENTRY("eop_charge", 16, 6),
CREATE_ENTRY("__rsvd", 22, 42)
};auto fpg_misc_stream_rate_limit_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_stream_rate_limit),
0x338,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_stream_rate_limit", fpg_misc_stream_rate_limit_prop);
fld_map_t fpg_misc_rx_max_pkt_len {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("val", 1, 14),
CREATE_ENTRY("__rsvd", 15, 49)
};auto fpg_misc_rx_max_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_max_pkt_len),
0x358,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_max_pkt_len", fpg_misc_rx_max_pkt_len_prop);
fld_map_t fpg_misc_rx_min_pkt_len {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto fpg_misc_rx_min_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_min_pkt_len),
0x378,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_min_pkt_len", fpg_misc_rx_min_pkt_len_prop);
fld_map_t fpg_misc_rx_runt_filter_cfg {
CREATE_ENTRY("buffer_64byte", 0, 1),
CREATE_ENTRY("runt_err_en", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_misc_rx_runt_filter_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_runt_filter_cfg),
0x380,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_runt_filter_cfg", fpg_misc_rx_runt_filter_cfg_prop);
fld_map_t fpg_misc_rx_pfc_ctrl {
CREATE_ENTRY("sw_override_en", 0, 16),
CREATE_ENTRY("sw_override_val", 16, 16),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fpg_misc_rx_pfc_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_pfc_ctrl),
0x388,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_pfc_ctrl", fpg_misc_rx_pfc_ctrl_prop);
fld_map_t fpg_misc_rx_eop_timeout_cfg {
CREATE_ENTRY("en", 0, 4),
CREATE_ENTRY("timeout_val", 4, 16),
CREATE_ENTRY("__rsvd", 20, 44)
};auto fpg_misc_rx_eop_timeout_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_eop_timeout_cfg),
0x3A8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_eop_timeout_cfg", fpg_misc_rx_eop_timeout_cfg_prop);
fld_map_t fpg_misc_rx_bb_af_hdrm {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_rx_bb_af_hdrm_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_bb_af_hdrm),
0x3B0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_bb_af_hdrm", fpg_misc_rx_bb_af_hdrm_prop);
fld_map_t fpg_misc_tx_sch_cfg {
CREATE_ENTRY("gr_wt_eth", 0, 12),
CREATE_ENTRY("gr_wt_flink", 12, 12),
CREATE_ENTRY("gr_per", 24, 4),
CREATE_ENTRY("dwrr_wt_eth", 28, 4),
CREATE_ENTRY("dwrr_wt_flink", 32, 4),
CREATE_ENTRY("flink_extra_holdoff_en", 36, 1),
CREATE_ENTRY("__rsvd", 37, 27)
};auto fpg_misc_tx_sch_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_sch_cfg),
0x3B8,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_0, "fpg_misc_tx_sch_cfg", fpg_misc_tx_sch_cfg_prop);
fld_map_t fpg_misc_rx_flink_etype_cfg {
CREATE_ENTRY("etype_bypass_en", 0, 1),
CREATE_ENTRY("flink_en", 1, 1),
CREATE_ENTRY("val", 2, 16),
CREATE_ENTRY("__rsvd", 18, 46)
};auto fpg_misc_rx_flink_etype_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_flink_etype_cfg),
0x3D8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_flink_etype_cfg", fpg_misc_rx_flink_etype_cfg_prop);
fld_map_t fpg_misc_mem_err_inj_cfg {
CREATE_ENTRY("fpg_misc_rx_bb0_mem", 0, 1),
CREATE_ENTRY("fpg_misc_rx_bb1_mem", 1, 1),
CREATE_ENTRY("fpg_misc_rx_bb2_mem", 2, 1),
CREATE_ENTRY("fpg_misc_rx_bb3_mem", 3, 1),
CREATE_ENTRY("err_type", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto fpg_misc_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mem_err_inj_cfg),
0x3E0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_mem_err_inj_cfg", fpg_misc_mem_err_inj_cfg_prop);
fld_map_t fpg_misc_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_fla_ring_module_id_cfg),
0x3E8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_fla_ring_module_id_cfg", fpg_misc_fla_ring_module_id_cfg_prop);
fld_map_t fpg_misc_rx_bb_occ_cnt {
CREATE_ENTRY("bb00_cnt", 0, 10),
CREATE_ENTRY("bb0_cnt", 10, 10),
CREATE_ENTRY("bb1_cnt", 20, 10),
CREATE_ENTRY("bb2_cnt", 30, 10),
CREATE_ENTRY("bb3_cnt", 40, 10),
CREATE_ENTRY("__rsvd", 50, 14)
};auto fpg_misc_rx_bb_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_bb_occ_cnt),
0x3F0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_bb_occ_cnt", fpg_misc_rx_bb_occ_cnt_prop);
fld_map_t fpg_misc_rx_bb_sticky_max_occ_cnt {
CREATE_ENTRY("bb00_cnt", 0, 10),
CREATE_ENTRY("bb0_cnt", 10, 10),
CREATE_ENTRY("bb1_cnt", 20, 10),
CREATE_ENTRY("bb2_cnt", 30, 10),
CREATE_ENTRY("bb3_cnt", 40, 10),
CREATE_ENTRY("__rsvd", 50, 14)
};auto fpg_misc_rx_bb_sticky_max_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_bb_sticky_max_occ_cnt),
0x3F8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_rx_bb_sticky_max_occ_cnt", fpg_misc_rx_bb_sticky_max_occ_cnt_prop);
fld_map_t fpg_misc_sram_log_err {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_sram_log_err),
0x400,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_sram_log_err", fpg_misc_sram_log_err_prop);
fld_map_t fpg_misc_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_sram_log_syndrome),
0x408,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_sram_log_syndrome", fpg_misc_sram_log_syndrome_prop);
fld_map_t fpg_misc_sram_log_addr {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_sram_log_addr),
0x410,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_0, "fpg_misc_sram_log_addr", fpg_misc_sram_log_addr_prop);
 // END fpg_misc 
}
{
 // BEGIN fpg_misc 
auto fpg_misc_1 = nu_rng[0].add_an({"nu_mpg","fpg_misc"}, 0x15400000, 1, 0x0);
fld_map_t fpg_misc_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_misc_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_timeout_thresh_cfg", fpg_misc_timeout_thresh_cfg_prop);
fld_map_t fpg_misc_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_timedout_sta", fpg_misc_timedout_sta_prop);
fld_map_t fpg_misc_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_timeout_clr", fpg_misc_timeout_clr_prop);
fld_map_t fpg_misc_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_misc_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_features", fpg_misc_features_prop);
fld_map_t fpg_misc_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_misc_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_spare_pio", fpg_misc_spare_pio_prop);
fld_map_t fpg_misc_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_misc_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_scratchpad", fpg_misc_scratchpad_prop);
fld_map_t fpg_misc_stream_speed {
CREATE_ENTRY("stream_speed", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_misc_stream_speed_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_stream_speed),
0x80,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_stream_speed", fpg_misc_stream_speed_prop);
fld_map_t fpg_misc_get_flit_tdm_en {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_get_flit_tdm_en_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_get_flit_tdm_en),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_get_flit_tdm_en", fpg_misc_get_flit_tdm_en_prop);
fld_map_t fpg_misc_get_flit_tdm_clnd {
CREATE_ENTRY("stream_num", 0, 2),
CREATE_ENTRY("vld", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto fpg_misc_get_flit_tdm_clnd_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_get_flit_tdm_clnd),
0xA8,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_get_flit_tdm_clnd", fpg_misc_get_flit_tdm_clnd_prop);
fld_map_t fpg_misc_tx_max_pkt_len {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto fpg_misc_tx_max_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_max_pkt_len),
0xC8,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_max_pkt_len", fpg_misc_tx_max_pkt_len_prop);
fld_map_t fpg_misc_tx_min_pkt_len {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_tx_min_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_min_pkt_len),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_min_pkt_len", fpg_misc_tx_min_pkt_len_prop);
fld_map_t fpg_misc_tx_ptp_cfg {
CREATE_ENTRY("peer_delay_en", 0, 4),
CREATE_ENTRY("one_step_en", 4, 4),
CREATE_ENTRY("timestamp_overwrite_en", 8, 4),
CREATE_ENTRY("timestamp_capture_en", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_ptp_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_ptp_cfg),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_ptp_cfg", fpg_misc_tx_ptp_cfg_prop);
fld_map_t fpg_misc_mac0_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac0_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac0_peer_delay_cfg),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_mac0_peer_delay_cfg", fpg_misc_mac0_peer_delay_cfg_prop);
fld_map_t fpg_misc_mac1_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac1_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac1_peer_delay_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_mac1_peer_delay_cfg", fpg_misc_mac1_peer_delay_cfg_prop);
fld_map_t fpg_misc_mac2_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac2_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac2_peer_delay_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_mac2_peer_delay_cfg", fpg_misc_mac2_peer_delay_cfg_prop);
fld_map_t fpg_misc_mac3_peer_delay_cfg {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fpg_misc_mac3_peer_delay_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mac3_peer_delay_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_mac3_peer_delay_cfg", fpg_misc_mac3_peer_delay_cfg_prop);
fld_map_t fpg_misc_tx_pfc_ctrl {
CREATE_ENTRY("sw_override_en", 0, 16),
CREATE_ENTRY("sw_override_val", 16, 16),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fpg_misc_tx_pfc_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_pfc_ctrl),
0x118,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_pfc_ctrl", fpg_misc_tx_pfc_ctrl_prop);
fld_map_t fpg_misc_tx_failure_bcast_ctrl {
CREATE_ENTRY("failure_bcast_en", 0, 1),
CREATE_ENTRY("use_local_fault_status", 1, 1),
CREATE_ENTRY("use_rem_fault_status", 2, 1),
CREATE_ENTRY("use_li_fault_status", 3, 1),
CREATE_ENTRY("use_pcs_link_status", 4, 1),
CREATE_ENTRY("use_serdes_signal_ok", 5, 1),
CREATE_ENTRY("sw_triggered_fault_bcast", 6, 1),
CREATE_ENTRY("failure_bcast_delay_timer", 7, 16),
CREATE_ENTRY("__rsvd", 23, 41)
};auto fpg_misc_tx_failure_bcast_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_failure_bcast_ctrl),
0x138,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_failure_bcast_ctrl", fpg_misc_tx_failure_bcast_ctrl_prop);
fld_map_t fpg_misc_tx_fsf_frame_data {
CREATE_ENTRY("gph_index", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_fsf_frame_data_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_data),
0x158,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_data", fpg_misc_tx_fsf_frame_data_prop);
fld_map_t fpg_misc_tx_fsf_xmit_en {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_misc_tx_fsf_xmit_en_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_xmit_en),
0x218,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_fsf_xmit_en", fpg_misc_tx_fsf_xmit_en_prop);
fld_map_t fpg_misc_tx_fsf_strm_is_glb_link {
CREATE_ENTRY("val", 0, 24),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fpg_misc_tx_fsf_strm_is_glb_link_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_strm_is_glb_link),
0x238,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_fsf_strm_is_glb_link", fpg_misc_tx_fsf_strm_is_glb_link_prop);
fld_map_t fpg_misc_tx_fsf_frame_opcode {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_fsf_frame_opcode_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_opcode),
0x240,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_opcode", fpg_misc_tx_fsf_frame_opcode_prop);
fld_map_t fpg_misc_tx_fsf_frame_dmac {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fpg_misc_tx_fsf_frame_dmac_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_dmac),
0x248,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_dmac", fpg_misc_tx_fsf_frame_dmac_prop);
fld_map_t fpg_misc_tx_fsf_frame_ethertype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_tx_fsf_frame_ethertype_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_ethertype),
0x250,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_ethertype", fpg_misc_tx_fsf_frame_ethertype_prop);
fld_map_t fpg_misc_psw_tdm_clnd {
CREATE_ENTRY("stream_num", 0, 2),
CREATE_ENTRY("vld", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto fpg_misc_psw_tdm_clnd_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_psw_tdm_clnd),
0x318,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_psw_tdm_clnd", fpg_misc_psw_tdm_clnd_prop);
fld_map_t fpg_misc_stream_rate_limit {
CREATE_ENTRY("credits_per_interval", 0, 13),
CREATE_ENTRY("interval", 13, 3),
CREATE_ENTRY("eop_charge", 16, 6),
CREATE_ENTRY("__rsvd", 22, 42)
};auto fpg_misc_stream_rate_limit_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_stream_rate_limit),
0x338,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_stream_rate_limit", fpg_misc_stream_rate_limit_prop);
fld_map_t fpg_misc_rx_max_pkt_len {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("val", 1, 14),
CREATE_ENTRY("__rsvd", 15, 49)
};auto fpg_misc_rx_max_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_max_pkt_len),
0x358,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_max_pkt_len", fpg_misc_rx_max_pkt_len_prop);
fld_map_t fpg_misc_rx_min_pkt_len {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto fpg_misc_rx_min_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_min_pkt_len),
0x378,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_min_pkt_len", fpg_misc_rx_min_pkt_len_prop);
fld_map_t fpg_misc_rx_runt_filter_cfg {
CREATE_ENTRY("buffer_64byte", 0, 1),
CREATE_ENTRY("runt_err_en", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_misc_rx_runt_filter_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_runt_filter_cfg),
0x380,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_runt_filter_cfg", fpg_misc_rx_runt_filter_cfg_prop);
fld_map_t fpg_misc_rx_pfc_ctrl {
CREATE_ENTRY("sw_override_en", 0, 16),
CREATE_ENTRY("sw_override_val", 16, 16),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fpg_misc_rx_pfc_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_pfc_ctrl),
0x388,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_pfc_ctrl", fpg_misc_rx_pfc_ctrl_prop);
fld_map_t fpg_misc_rx_eop_timeout_cfg {
CREATE_ENTRY("en", 0, 4),
CREATE_ENTRY("timeout_val", 4, 16),
CREATE_ENTRY("__rsvd", 20, 44)
};auto fpg_misc_rx_eop_timeout_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_eop_timeout_cfg),
0x3A8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_eop_timeout_cfg", fpg_misc_rx_eop_timeout_cfg_prop);
fld_map_t fpg_misc_rx_bb_af_hdrm {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_rx_bb_af_hdrm_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_bb_af_hdrm),
0x3B0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_bb_af_hdrm", fpg_misc_rx_bb_af_hdrm_prop);
fld_map_t fpg_misc_tx_sch_cfg {
CREATE_ENTRY("gr_wt_eth", 0, 12),
CREATE_ENTRY("gr_wt_flink", 12, 12),
CREATE_ENTRY("gr_per", 24, 4),
CREATE_ENTRY("dwrr_wt_eth", 28, 4),
CREATE_ENTRY("dwrr_wt_flink", 32, 4),
CREATE_ENTRY("flink_extra_holdoff_en", 36, 1),
CREATE_ENTRY("__rsvd", 37, 27)
};auto fpg_misc_tx_sch_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_tx_sch_cfg),
0x3B8,
CSR_TYPE::REG_LST,
1);
add_csr(fpg_misc_1, "fpg_misc_tx_sch_cfg", fpg_misc_tx_sch_cfg_prop);
fld_map_t fpg_misc_rx_flink_etype_cfg {
CREATE_ENTRY("etype_bypass_en", 0, 1),
CREATE_ENTRY("flink_en", 1, 1),
CREATE_ENTRY("val", 2, 16),
CREATE_ENTRY("__rsvd", 18, 46)
};auto fpg_misc_rx_flink_etype_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_flink_etype_cfg),
0x3D8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_flink_etype_cfg", fpg_misc_rx_flink_etype_cfg_prop);
fld_map_t fpg_misc_mem_err_inj_cfg {
CREATE_ENTRY("fpg_misc_rx_bb0_mem", 0, 1),
CREATE_ENTRY("fpg_misc_rx_bb1_mem", 1, 1),
CREATE_ENTRY("fpg_misc_rx_bb2_mem", 2, 1),
CREATE_ENTRY("fpg_misc_rx_bb3_mem", 3, 1),
CREATE_ENTRY("err_type", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto fpg_misc_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_mem_err_inj_cfg),
0x3E0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_mem_err_inj_cfg", fpg_misc_mem_err_inj_cfg_prop);
fld_map_t fpg_misc_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_fla_ring_module_id_cfg),
0x3E8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_fla_ring_module_id_cfg", fpg_misc_fla_ring_module_id_cfg_prop);
fld_map_t fpg_misc_rx_bb_occ_cnt {
CREATE_ENTRY("bb00_cnt", 0, 10),
CREATE_ENTRY("bb0_cnt", 10, 10),
CREATE_ENTRY("bb1_cnt", 20, 10),
CREATE_ENTRY("bb2_cnt", 30, 10),
CREATE_ENTRY("bb3_cnt", 40, 10),
CREATE_ENTRY("__rsvd", 50, 14)
};auto fpg_misc_rx_bb_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_bb_occ_cnt),
0x3F0,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_bb_occ_cnt", fpg_misc_rx_bb_occ_cnt_prop);
fld_map_t fpg_misc_rx_bb_sticky_max_occ_cnt {
CREATE_ENTRY("bb00_cnt", 0, 10),
CREATE_ENTRY("bb0_cnt", 10, 10),
CREATE_ENTRY("bb1_cnt", 20, 10),
CREATE_ENTRY("bb2_cnt", 30, 10),
CREATE_ENTRY("bb3_cnt", 40, 10),
CREATE_ENTRY("__rsvd", 50, 14)
};auto fpg_misc_rx_bb_sticky_max_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_rx_bb_sticky_max_occ_cnt),
0x3F8,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_rx_bb_sticky_max_occ_cnt", fpg_misc_rx_bb_sticky_max_occ_cnt_prop);
fld_map_t fpg_misc_sram_log_err {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_sram_log_err),
0x400,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_sram_log_err", fpg_misc_sram_log_err_prop);
fld_map_t fpg_misc_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_misc_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_sram_log_syndrome),
0x408,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_sram_log_syndrome", fpg_misc_sram_log_syndrome_prop);
fld_map_t fpg_misc_sram_log_addr {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_misc_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_misc_sram_log_addr),
0x410,
CSR_TYPE::REG,
1);
add_csr(fpg_misc_1, "fpg_misc_sram_log_addr", fpg_misc_sram_log_addr_prop);
 // END fpg_misc 
}
{
 // BEGIN fpg_sdif 
auto fpg_sdif_0 = nu_rng[0].add_an({"fpg","fpg_sdif"}, 0x814000, 6, 0x1000000);
fld_map_t fpg_sdif_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_sdif_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_timeout_thresh_cfg", fpg_sdif_timeout_thresh_cfg_prop);
fld_map_t fpg_sdif_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_sdif_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_timedout_sta", fpg_sdif_timedout_sta_prop);
fld_map_t fpg_sdif_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_sdif_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_timeout_clr", fpg_sdif_timeout_clr_prop);
fld_map_t fpg_sdif_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_sdif_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_features", fpg_sdif_features_prop);
fld_map_t fpg_sdif_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_sdif_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_spare_pio", fpg_sdif_spare_pio_prop);
fld_map_t fpg_sdif_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_sdif_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_scratchpad", fpg_sdif_scratchpad_prop);
fld_map_t fpg_sdif_pcs_tx_clk_ena_msel {
CREATE_ENTRY("ln0", 0, 3),
CREATE_ENTRY("ln1", 3, 3),
CREATE_ENTRY("ln2", 6, 3),
CREATE_ENTRY("ln3", 9, 3),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fpg_sdif_pcs_tx_clk_ena_msel_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_pcs_tx_clk_ena_msel),
0x80,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_pcs_tx_clk_ena_msel", fpg_sdif_pcs_tx_clk_ena_msel_prop);
fld_map_t fpg_sdif_sd_en {
CREATE_ENTRY("tx_ln_en", 0, 4),
CREATE_ENTRY("rx_ln_en", 4, 4),
CREATE_ENTRY("rx_tx_ln_loopback_en", 8, 4),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fpg_sdif_sd_en_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_sd_en),
0x88,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_sd_en", fpg_sdif_sd_en_prop);
fld_map_t fpg_sdif_fifo_rst {
CREATE_ENTRY("tx_ln_rst_n", 0, 4),
CREATE_ENTRY("rx_ln_rst_n", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_sdif_fifo_rst_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_fifo_rst),
0x90,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_fifo_rst", fpg_sdif_fifo_rst_prop);
fld_map_t fpg_sdif_tx_fifo_start_txmit_thr {
CREATE_ENTRY("val_ln0", 0, 6),
CREATE_ENTRY("val_ln1", 6, 6),
CREATE_ENTRY("val_ln2", 12, 6),
CREATE_ENTRY("val_ln3", 18, 6),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fpg_sdif_tx_fifo_start_txmit_thr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_tx_fifo_start_txmit_thr),
0x98,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_tx_fifo_start_txmit_thr", fpg_sdif_tx_fifo_start_txmit_thr_prop);
fld_map_t fpg_sdif_rx_signal_det {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_rx_signal_det_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_rx_signal_det),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_rx_signal_det", fpg_sdif_rx_signal_det_prop);
fld_map_t fpg_sdif_rx_use_energy_det_frm_serdes {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_rx_use_energy_det_frm_serdes_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_rx_use_energy_det_frm_serdes),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_rx_use_energy_det_frm_serdes", fpg_sdif_rx_use_energy_det_frm_serdes_prop);
fld_map_t fpg_sdif_rx_use_signal_det_frm_serdes {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_rx_use_signal_det_frm_serdes_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_rx_use_signal_det_frm_serdes),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_rx_use_signal_det_frm_serdes", fpg_sdif_rx_use_signal_det_frm_serdes_prop);
fld_map_t fpg_sdif_serdes_rdy_status {
CREATE_ENTRY("rx_rdy", 0, 4),
CREATE_ENTRY("tx_rdy", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_sdif_serdes_rdy_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_rdy_status),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_serdes_rdy_status", fpg_sdif_serdes_rdy_status_prop);
fld_map_t fpg_sdif_serdes_mode_is_50g {
CREATE_ENTRY("sd0_is_50g", 0, 1),
CREATE_ENTRY("sd2_is_50g", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_sdif_serdes_mode_is_50g_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_mode_is_50g),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_serdes_mode_is_50g", fpg_sdif_serdes_mode_is_50g_prop);
fld_map_t fpg_sdif_spico_intr_data_out_vld {
CREATE_ENTRY("ln0_data_out_vld", 0, 1),
CREATE_ENTRY("ln1_data_out_vld", 1, 1),
CREATE_ENTRY("ln2_data_out_vld", 2, 1),
CREATE_ENTRY("ln3_data_out_vld", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_spico_intr_data_out_vld_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_spico_intr_data_out_vld),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_spico_intr_data_out_vld", fpg_sdif_spico_intr_data_out_vld_prop);
fld_map_t fpg_sdif_spico_intr_data_out {
CREATE_ENTRY("ln0_data_out", 0, 16),
CREATE_ENTRY("ln1_data_out", 16, 16),
CREATE_ENTRY("ln2_data_out", 32, 16),
CREATE_ENTRY("ln3_data_out", 48, 16)
};auto fpg_sdif_spico_intr_data_out_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_spico_intr_data_out),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_spico_intr_data_out", fpg_sdif_spico_intr_data_out_prop);
fld_map_t fpg_sdif_serdes_status0 {
CREATE_ENTRY("ln0", 0, 32),
CREATE_ENTRY("ln1", 32, 32)
};auto fpg_sdif_serdes_status0_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_status0),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_serdes_status0", fpg_sdif_serdes_status0_prop);
fld_map_t fpg_sdif_serdes_status1 {
CREATE_ENTRY("ln2", 0, 32),
CREATE_ENTRY("ln3", 32, 32)
};auto fpg_sdif_serdes_status1_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_status1),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_serdes_status1", fpg_sdif_serdes_status1_prop);
fld_map_t fpg_sdif_analog_to_core_status {
CREATE_ENTRY("ln0", 0, 8),
CREATE_ENTRY("ln1", 8, 8),
CREATE_ENTRY("ln2", 16, 8),
CREATE_ENTRY("ln3", 24, 8),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fpg_sdif_analog_to_core_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_analog_to_core_status),
0x100,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_analog_to_core_status", fpg_sdif_analog_to_core_status_prop);
fld_map_t fpg_sdif_core_to_cntl {
CREATE_ENTRY("ln0", 0, 16),
CREATE_ENTRY("ln1", 16, 16),
CREATE_ENTRY("ln2", 32, 16),
CREATE_ENTRY("ln3", 48, 16)
};auto fpg_sdif_core_to_cntl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_core_to_cntl),
0x108,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_core_to_cntl", fpg_sdif_core_to_cntl_prop);
fld_map_t fpg_sdif_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_sdif_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_fla_ring_module_id_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_0, "fpg_sdif_fla_ring_module_id_cfg", fpg_sdif_fla_ring_module_id_cfg_prop);
 // END fpg_sdif 
}
{
 // BEGIN fpg_sdif 
auto fpg_sdif_1 = nu_rng[0].add_an({"nu_mpg","fpg_sdif"}, 0x15404000, 1, 0x0);
fld_map_t fpg_sdif_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_sdif_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_timeout_thresh_cfg", fpg_sdif_timeout_thresh_cfg_prop);
fld_map_t fpg_sdif_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_sdif_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_timedout_sta", fpg_sdif_timedout_sta_prop);
fld_map_t fpg_sdif_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_sdif_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_timeout_clr", fpg_sdif_timeout_clr_prop);
fld_map_t fpg_sdif_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_sdif_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_features", fpg_sdif_features_prop);
fld_map_t fpg_sdif_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_sdif_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_spare_pio", fpg_sdif_spare_pio_prop);
fld_map_t fpg_sdif_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_sdif_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_scratchpad", fpg_sdif_scratchpad_prop);
fld_map_t fpg_sdif_pcs_tx_clk_ena_msel {
CREATE_ENTRY("ln0", 0, 3),
CREATE_ENTRY("ln1", 3, 3),
CREATE_ENTRY("ln2", 6, 3),
CREATE_ENTRY("ln3", 9, 3),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fpg_sdif_pcs_tx_clk_ena_msel_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_pcs_tx_clk_ena_msel),
0x80,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_pcs_tx_clk_ena_msel", fpg_sdif_pcs_tx_clk_ena_msel_prop);
fld_map_t fpg_sdif_sd_en {
CREATE_ENTRY("tx_ln_en", 0, 4),
CREATE_ENTRY("rx_ln_en", 4, 4),
CREATE_ENTRY("rx_tx_ln_loopback_en", 8, 4),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fpg_sdif_sd_en_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_sd_en),
0x88,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_sd_en", fpg_sdif_sd_en_prop);
fld_map_t fpg_sdif_fifo_rst {
CREATE_ENTRY("tx_ln_rst_n", 0, 4),
CREATE_ENTRY("rx_ln_rst_n", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_sdif_fifo_rst_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_fifo_rst),
0x90,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_fifo_rst", fpg_sdif_fifo_rst_prop);
fld_map_t fpg_sdif_tx_fifo_start_txmit_thr {
CREATE_ENTRY("val_ln0", 0, 6),
CREATE_ENTRY("val_ln1", 6, 6),
CREATE_ENTRY("val_ln2", 12, 6),
CREATE_ENTRY("val_ln3", 18, 6),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fpg_sdif_tx_fifo_start_txmit_thr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_tx_fifo_start_txmit_thr),
0x98,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_tx_fifo_start_txmit_thr", fpg_sdif_tx_fifo_start_txmit_thr_prop);
fld_map_t fpg_sdif_rx_signal_det {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_rx_signal_det_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_rx_signal_det),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_rx_signal_det", fpg_sdif_rx_signal_det_prop);
fld_map_t fpg_sdif_rx_use_energy_det_frm_serdes {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_rx_use_energy_det_frm_serdes_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_rx_use_energy_det_frm_serdes),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_rx_use_energy_det_frm_serdes", fpg_sdif_rx_use_energy_det_frm_serdes_prop);
fld_map_t fpg_sdif_rx_use_signal_det_frm_serdes {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_rx_use_signal_det_frm_serdes_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_rx_use_signal_det_frm_serdes),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_rx_use_signal_det_frm_serdes", fpg_sdif_rx_use_signal_det_frm_serdes_prop);
fld_map_t fpg_sdif_serdes_rdy_status {
CREATE_ENTRY("rx_rdy", 0, 4),
CREATE_ENTRY("tx_rdy", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_sdif_serdes_rdy_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_rdy_status),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_serdes_rdy_status", fpg_sdif_serdes_rdy_status_prop);
fld_map_t fpg_sdif_serdes_mode_is_50g {
CREATE_ENTRY("sd0_is_50g", 0, 1),
CREATE_ENTRY("sd2_is_50g", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_sdif_serdes_mode_is_50g_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_mode_is_50g),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_serdes_mode_is_50g", fpg_sdif_serdes_mode_is_50g_prop);
fld_map_t fpg_sdif_spico_intr_data_out_vld {
CREATE_ENTRY("ln0_data_out_vld", 0, 1),
CREATE_ENTRY("ln1_data_out_vld", 1, 1),
CREATE_ENTRY("ln2_data_out_vld", 2, 1),
CREATE_ENTRY("ln3_data_out_vld", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_sdif_spico_intr_data_out_vld_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_spico_intr_data_out_vld),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_spico_intr_data_out_vld", fpg_sdif_spico_intr_data_out_vld_prop);
fld_map_t fpg_sdif_spico_intr_data_out {
CREATE_ENTRY("ln0_data_out", 0, 16),
CREATE_ENTRY("ln1_data_out", 16, 16),
CREATE_ENTRY("ln2_data_out", 32, 16),
CREATE_ENTRY("ln3_data_out", 48, 16)
};auto fpg_sdif_spico_intr_data_out_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_spico_intr_data_out),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_spico_intr_data_out", fpg_sdif_spico_intr_data_out_prop);
fld_map_t fpg_sdif_serdes_status0 {
CREATE_ENTRY("ln0", 0, 32),
CREATE_ENTRY("ln1", 32, 32)
};auto fpg_sdif_serdes_status0_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_status0),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_serdes_status0", fpg_sdif_serdes_status0_prop);
fld_map_t fpg_sdif_serdes_status1 {
CREATE_ENTRY("ln2", 0, 32),
CREATE_ENTRY("ln3", 32, 32)
};auto fpg_sdif_serdes_status1_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_serdes_status1),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_serdes_status1", fpg_sdif_serdes_status1_prop);
fld_map_t fpg_sdif_analog_to_core_status {
CREATE_ENTRY("ln0", 0, 8),
CREATE_ENTRY("ln1", 8, 8),
CREATE_ENTRY("ln2", 16, 8),
CREATE_ENTRY("ln3", 24, 8),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fpg_sdif_analog_to_core_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_analog_to_core_status),
0x100,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_analog_to_core_status", fpg_sdif_analog_to_core_status_prop);
fld_map_t fpg_sdif_core_to_cntl {
CREATE_ENTRY("ln0", 0, 16),
CREATE_ENTRY("ln1", 16, 16),
CREATE_ENTRY("ln2", 32, 16),
CREATE_ENTRY("ln3", 48, 16)
};auto fpg_sdif_core_to_cntl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_core_to_cntl),
0x108,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_core_to_cntl", fpg_sdif_core_to_cntl_prop);
fld_map_t fpg_sdif_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_sdif_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_sdif_fla_ring_module_id_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fpg_sdif_1, "fpg_sdif_fla_ring_module_id_cfg", fpg_sdif_fla_ring_module_id_cfg_prop);
 // END fpg_sdif 
}
{
 // BEGIN fpg_mpw 
auto fpg_mpw_0 = nu_rng[0].add_an({"fpg","fpg_mpw"}, 0x880000, 6, 0x1000000);
fld_map_t fpg_mpw_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_mpw_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_timeout_thresh_cfg", fpg_mpw_timeout_thresh_cfg_prop);
fld_map_t fpg_mpw_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_mpw_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_timedout_sta", fpg_mpw_timedout_sta_prop);
fld_map_t fpg_mpw_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_mpw_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_timeout_clr", fpg_mpw_timeout_clr_prop);
fld_map_t fpg_mpw_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_mpw_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_features),
0x90,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_features", fpg_mpw_features_prop);
fld_map_t fpg_mpw_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_mpw_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_spare_pio),
0x98,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_spare_pio", fpg_mpw_spare_pio_prop);
fld_map_t fpg_mpw_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_mpw_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_scratchpad),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_scratchpad", fpg_mpw_scratchpad_prop);
fld_map_t fpg_mpw_mac_status {
CREATE_ENTRY("mac0_tx_underflow", 0, 1),
CREATE_ENTRY("mac0_tx_overflow", 1, 1),
CREATE_ENTRY("mac0_tx_empty", 2, 1),
CREATE_ENTRY("mac0_loc_fault", 3, 1),
CREATE_ENTRY("mac0_rem_fault", 4, 1),
CREATE_ENTRY("mac0_li_fault", 5, 1),
CREATE_ENTRY("mac0_phy_txena", 6, 1),
CREATE_ENTRY("mac1_tx_underflow", 7, 1),
CREATE_ENTRY("mac1_tx_overflow", 8, 1),
CREATE_ENTRY("mac1_tx_empty", 9, 1),
CREATE_ENTRY("mac1_loc_fault", 10, 1),
CREATE_ENTRY("mac1_rem_fault", 11, 1),
CREATE_ENTRY("mac1_li_fault", 12, 1),
CREATE_ENTRY("mac1_phy_txena", 13, 1),
CREATE_ENTRY("mac2_tx_underflow", 14, 1),
CREATE_ENTRY("mac2_tx_overflow", 15, 1),
CREATE_ENTRY("mac2_tx_empty", 16, 1),
CREATE_ENTRY("mac2_loc_fault", 17, 1),
CREATE_ENTRY("mac2_rem_fault", 18, 1),
CREATE_ENTRY("mac2_li_fault", 19, 1),
CREATE_ENTRY("mac2_phy_txena", 20, 1),
CREATE_ENTRY("mac3_tx_underflow", 21, 1),
CREATE_ENTRY("mac3_tx_overflow", 22, 1),
CREATE_ENTRY("mac3_tx_empty", 23, 1),
CREATE_ENTRY("mac3_loc_fault", 24, 1),
CREATE_ENTRY("mac3_rem_fault", 25, 1),
CREATE_ENTRY("mac3_li_fault", 26, 1),
CREATE_ENTRY("mac3_phy_txena", 27, 1),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fpg_mpw_mac_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_status),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_mac_status", fpg_mpw_mac_status_prop);
fld_map_t fpg_mpw_mac_tx_ts_avl {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_mpw_mac_tx_ts_avl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_tx_ts_avl),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_mac_tx_ts_avl", fpg_mpw_mac_tx_ts_avl_prop);
fld_map_t fpg_mpw_mac_tx_fault_cfg {
CREATE_ENTRY("mac0_tx_loc_fault", 0, 1),
CREATE_ENTRY("mac0_tx_rem_fault", 1, 1),
CREATE_ENTRY("mac0_tx_li_fault", 2, 1),
CREATE_ENTRY("mac1_tx_loc_fault", 3, 1),
CREATE_ENTRY("mac1_tx_rem_fault", 4, 1),
CREATE_ENTRY("mac1_tx_li_fault", 5, 1),
CREATE_ENTRY("mac2_tx_loc_fault", 6, 1),
CREATE_ENTRY("mac2_tx_rem_fault", 7, 1),
CREATE_ENTRY("mac2_tx_li_fault", 8, 1),
CREATE_ENTRY("mac3_tx_loc_fault", 9, 1),
CREATE_ENTRY("mac3_tx_rem_fault", 10, 1),
CREATE_ENTRY("mac3_tx_li_fault", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fpg_mpw_mac_tx_fault_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_tx_fault_cfg),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_mac_tx_fault_cfg", fpg_mpw_mac_tx_fault_cfg_prop);
fld_map_t fpg_mpw_mac_lpi_cfg {
CREATE_ENTRY("mac0_lowp_ena", 0, 1),
CREATE_ENTRY("mac0_lpi_txhold", 1, 1),
CREATE_ENTRY("mac1_lowp_ena", 2, 1),
CREATE_ENTRY("mac1_lpi_txhold", 3, 1),
CREATE_ENTRY("mac2_lowp_ena", 4, 1),
CREATE_ENTRY("mac2_lpi_txhold", 5, 1),
CREATE_ENTRY("mac3_lowp_ena", 6, 1),
CREATE_ENTRY("mac3_lpi_txhold", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_mpw_mac_lpi_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_lpi_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_mac_lpi_cfg", fpg_mpw_mac_lpi_cfg_prop);
fld_map_t fpg_mpw_lpi_tick_cnt_incr_val {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto fpg_mpw_lpi_tick_cnt_incr_val_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_lpi_tick_cnt_incr_val),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_lpi_tick_cnt_incr_val", fpg_mpw_lpi_tick_cnt_incr_val_prop);
fld_map_t fpg_mpw_lpi_status {
CREATE_ENTRY("mac0_lowp", 0, 1),
CREATE_ENTRY("xpcs0_tx_lpi_mode", 1, 2),
CREATE_ENTRY("xpcs0_tx_lpi_state", 3, 3),
CREATE_ENTRY("xpcs0_rx_lpi_mode", 6, 1),
CREATE_ENTRY("xpcs0_rx_lpi_state", 7, 3),
CREATE_ENTRY("xpcs0_rx_lpi_active", 10, 1),
CREATE_ENTRY("mac1_lowp", 11, 1),
CREATE_ENTRY("xpcs1_tx_lpi_mode", 12, 2),
CREATE_ENTRY("xpcs1_tx_lpi_state", 14, 3),
CREATE_ENTRY("xpcs1_rx_lpi_mode", 17, 1),
CREATE_ENTRY("xpcs1_rx_lpi_state", 18, 3),
CREATE_ENTRY("xpcs1_rx_lpi_active", 21, 1),
CREATE_ENTRY("mac2_lowp", 22, 1),
CREATE_ENTRY("xpcs2_tx_lpi_mode", 23, 2),
CREATE_ENTRY("xpcs2_tx_lpi_state", 25, 3),
CREATE_ENTRY("xpcs2_rx_lpi_mode", 28, 1),
CREATE_ENTRY("xpcs2_rx_lpi_state", 29, 3),
CREATE_ENTRY("xpcs2_rx_lpi_active", 32, 1),
CREATE_ENTRY("mac3_lowp", 33, 1),
CREATE_ENTRY("xpcs3_tx_lpi_mode", 34, 2),
CREATE_ENTRY("xpcs3_tx_lpi_state", 36, 3),
CREATE_ENTRY("xpcs3_rx_lpi_mode", 39, 1),
CREATE_ENTRY("xpcs3_rx_lpi_state", 40, 3),
CREATE_ENTRY("xpcs3_rx_lpi_active", 43, 1),
CREATE_ENTRY("sg0_tx_lpi_active", 44, 1),
CREATE_ENTRY("sg0_pma_txmode_quiet", 45, 1),
CREATE_ENTRY("sg0_rx_lpi_active", 46, 1),
CREATE_ENTRY("sg0_pma_rxmode_quiet", 47, 1),
CREATE_ENTRY("sg0_rx_wake_err", 48, 1),
CREATE_ENTRY("__rsvd", 49, 15)
};auto fpg_mpw_lpi_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_lpi_status),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_lpi_status", fpg_mpw_lpi_status_prop);
fld_map_t fpg_mpw_sw_reset {
CREATE_ENTRY("rst_sd_tx_n", 0, 4),
CREATE_ENTRY("rst_sd_rx_n", 4, 4),
CREATE_ENTRY("rst_xpcs_n", 8, 1),
CREATE_ENTRY("rst_spcs_n", 9, 1),
CREATE_ENTRY("rst_ref_clk_n", 10, 1),
CREATE_ENTRY("rst_mac_ref_clk_n", 11, 4),
CREATE_ENTRY("rst_reg_clk_n", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_mpw_sw_reset_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_sw_reset),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_sw_reset", fpg_mpw_sw_reset_prop);
fld_map_t fpg_mpw_pcs_cfg {
CREATE_ENTRY("fec91_en", 0, 4),
CREATE_ENTRY("fec91_kp_mode", 4, 4),
CREATE_ENTRY("sd_n2", 8, 4),
CREATE_ENTRY("fec91_1lane_strm0", 12, 1),
CREATE_ENTRY("fec91_1lane_strm2", 13, 1),
CREATE_ENTRY("rxlaui_en_strm0", 14, 1),
CREATE_ENTRY("rxlaui_en_strm2", 15, 1),
CREATE_ENTRY("pcs100_en", 16, 1),
CREATE_ENTRY("mode40_en", 17, 1),
CREATE_ENTRY("sg0_en", 18, 1),
CREATE_ENTRY("mode50_1lane_strm0", 19, 1),
CREATE_ENTRY("mode50_1lane_strm2", 20, 1),
CREATE_ENTRY("mode100_2lane_strm0", 21, 1),
CREATE_ENTRY("__rsvd", 22, 42)
};auto fpg_mpw_pcs_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_pcs_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_pcs_cfg", fpg_mpw_pcs_cfg_prop);
fld_map_t fpg_mpw_pcs_status {
CREATE_ENTRY("align_done", 0, 1),
CREATE_ENTRY("block_lock", 1, 20),
CREATE_ENTRY("hi_ber", 21, 4),
CREATE_ENTRY("link_status", 25, 4),
CREATE_ENTRY("ber_timer_done", 29, 4),
CREATE_ENTRY("amps_lock", 33, 4),
CREATE_ENTRY("rsfec_aligned", 37, 4),
CREATE_ENTRY("sg0_rx_sync", 41, 1),
CREATE_ENTRY("sg0_an_done", 42, 1),
CREATE_ENTRY("sg0_speed", 43, 2),
CREATE_ENTRY("__rsvd", 45, 19)
};auto fpg_mpw_pcs_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_pcs_status),
0x108,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_pcs_status", fpg_mpw_pcs_status_prop);
fld_map_t fpg_mpw_tx_rx_loopback_cfg {
CREATE_ENTRY("en", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_mpw_tx_rx_loopback_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_tx_rx_loopback_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_tx_rx_loopback_cfg", fpg_mpw_tx_rx_loopback_cfg_prop);
fld_map_t fpg_mpw_rx_err_mask {
CREATE_ENTRY("len_err_mask", 0, 1),
CREATE_ENTRY("crc_err_mask", 1, 1),
CREATE_ENTRY("dec_err_mask", 2, 1),
CREATE_ENTRY("fifo_ovfl_err_mask", 3, 1),
CREATE_ENTRY("fault_err_mask", 4, 1),
CREATE_ENTRY("phy_err_mask", 5, 1),
CREATE_ENTRY("poisoned_crc_err_mask", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto fpg_mpw_rx_err_mask_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_rx_err_mask),
0x118,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_rx_err_mask", fpg_mpw_rx_err_mask_prop);
fld_map_t fpg_mpw_mem_err_inj_cfg {
CREATE_ENTRY("fpg_mpw_desk0_mem", 0, 1),
CREATE_ENTRY("fpg_mpw_desk1_mem", 1, 1),
CREATE_ENTRY("fpg_mpw_desk2_mem", 2, 1),
CREATE_ENTRY("fpg_mpw_desk3_mem", 3, 1),
CREATE_ENTRY("fpg_mpw_desk4_mem", 4, 1),
CREATE_ENTRY("fpg_mpw_desk5_mem", 5, 1),
CREATE_ENTRY("fpg_mpw_desk6_mem", 6, 1),
CREATE_ENTRY("fpg_mpw_desk7_mem", 7, 1),
CREATE_ENTRY("fpg_mpw_tstm_mem", 8, 1),
CREATE_ENTRY("fpg_mpw_rstm_mem", 9, 1),
CREATE_ENTRY("fpg_mpw_f91m_mem", 10, 1),
CREATE_ENTRY("fpg_mpw_f91dm0_mem", 11, 1),
CREATE_ENTRY("fpg_mpw_f91dm1_mem", 12, 1),
CREATE_ENTRY("fpg_mpw_f91dm2_mem", 13, 1),
CREATE_ENTRY("fpg_mpw_f91dm3_mem", 14, 1),
CREATE_ENTRY("err_type", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_mpw_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mem_err_inj_cfg),
0x130,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_mem_err_inj_cfg", fpg_mpw_mem_err_inj_cfg_prop);
fld_map_t fpg_mpw_sram_log_err {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto fpg_mpw_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_sram_log_err),
0x138,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_sram_log_err", fpg_mpw_sram_log_err_prop);
fld_map_t fpg_mpw_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto fpg_mpw_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_sram_log_addr),
0x140,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_sram_log_addr", fpg_mpw_sram_log_addr_prop);
fld_map_t fpg_mpw_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_mpw_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_fla_ring_module_id_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_0, "fpg_mpw_fla_ring_module_id_cfg", fpg_mpw_fla_ring_module_id_cfg_prop);
 // END fpg_mpw 
}
{
 // BEGIN fpg_mpw 
auto fpg_mpw_1 = nu_rng[0].add_an({"nu_mpg","fpg_mpw"}, 0x15480000, 1, 0x0);
fld_map_t fpg_mpw_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_mpw_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_timeout_thresh_cfg", fpg_mpw_timeout_thresh_cfg_prop);
fld_map_t fpg_mpw_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_mpw_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_timedout_sta", fpg_mpw_timedout_sta_prop);
fld_map_t fpg_mpw_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_mpw_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_timeout_clr", fpg_mpw_timeout_clr_prop);
fld_map_t fpg_mpw_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fpg_mpw_features_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_features),
0x90,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_features", fpg_mpw_features_prop);
fld_map_t fpg_mpw_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fpg_mpw_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_spare_pio),
0x98,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_spare_pio", fpg_mpw_spare_pio_prop);
fld_map_t fpg_mpw_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fpg_mpw_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_scratchpad),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_scratchpad", fpg_mpw_scratchpad_prop);
fld_map_t fpg_mpw_mac_status {
CREATE_ENTRY("mac0_tx_underflow", 0, 1),
CREATE_ENTRY("mac0_tx_overflow", 1, 1),
CREATE_ENTRY("mac0_tx_empty", 2, 1),
CREATE_ENTRY("mac0_loc_fault", 3, 1),
CREATE_ENTRY("mac0_rem_fault", 4, 1),
CREATE_ENTRY("mac0_li_fault", 5, 1),
CREATE_ENTRY("mac0_phy_txena", 6, 1),
CREATE_ENTRY("mac1_tx_underflow", 7, 1),
CREATE_ENTRY("mac1_tx_overflow", 8, 1),
CREATE_ENTRY("mac1_tx_empty", 9, 1),
CREATE_ENTRY("mac1_loc_fault", 10, 1),
CREATE_ENTRY("mac1_rem_fault", 11, 1),
CREATE_ENTRY("mac1_li_fault", 12, 1),
CREATE_ENTRY("mac1_phy_txena", 13, 1),
CREATE_ENTRY("mac2_tx_underflow", 14, 1),
CREATE_ENTRY("mac2_tx_overflow", 15, 1),
CREATE_ENTRY("mac2_tx_empty", 16, 1),
CREATE_ENTRY("mac2_loc_fault", 17, 1),
CREATE_ENTRY("mac2_rem_fault", 18, 1),
CREATE_ENTRY("mac2_li_fault", 19, 1),
CREATE_ENTRY("mac2_phy_txena", 20, 1),
CREATE_ENTRY("mac3_tx_underflow", 21, 1),
CREATE_ENTRY("mac3_tx_overflow", 22, 1),
CREATE_ENTRY("mac3_tx_empty", 23, 1),
CREATE_ENTRY("mac3_loc_fault", 24, 1),
CREATE_ENTRY("mac3_rem_fault", 25, 1),
CREATE_ENTRY("mac3_li_fault", 26, 1),
CREATE_ENTRY("mac3_phy_txena", 27, 1),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fpg_mpw_mac_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_status),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_mac_status", fpg_mpw_mac_status_prop);
fld_map_t fpg_mpw_mac_tx_ts_avl {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_mpw_mac_tx_ts_avl_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_tx_ts_avl),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_mac_tx_ts_avl", fpg_mpw_mac_tx_ts_avl_prop);
fld_map_t fpg_mpw_mac_tx_fault_cfg {
CREATE_ENTRY("mac0_tx_loc_fault", 0, 1),
CREATE_ENTRY("mac0_tx_rem_fault", 1, 1),
CREATE_ENTRY("mac0_tx_li_fault", 2, 1),
CREATE_ENTRY("mac1_tx_loc_fault", 3, 1),
CREATE_ENTRY("mac1_tx_rem_fault", 4, 1),
CREATE_ENTRY("mac1_tx_li_fault", 5, 1),
CREATE_ENTRY("mac2_tx_loc_fault", 6, 1),
CREATE_ENTRY("mac2_tx_rem_fault", 7, 1),
CREATE_ENTRY("mac2_tx_li_fault", 8, 1),
CREATE_ENTRY("mac3_tx_loc_fault", 9, 1),
CREATE_ENTRY("mac3_tx_rem_fault", 10, 1),
CREATE_ENTRY("mac3_tx_li_fault", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fpg_mpw_mac_tx_fault_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_tx_fault_cfg),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_mac_tx_fault_cfg", fpg_mpw_mac_tx_fault_cfg_prop);
fld_map_t fpg_mpw_mac_lpi_cfg {
CREATE_ENTRY("mac0_lowp_ena", 0, 1),
CREATE_ENTRY("mac0_lpi_txhold", 1, 1),
CREATE_ENTRY("mac1_lowp_ena", 2, 1),
CREATE_ENTRY("mac1_lpi_txhold", 3, 1),
CREATE_ENTRY("mac2_lowp_ena", 4, 1),
CREATE_ENTRY("mac2_lpi_txhold", 5, 1),
CREATE_ENTRY("mac3_lowp_ena", 6, 1),
CREATE_ENTRY("mac3_lpi_txhold", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_mpw_mac_lpi_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mac_lpi_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_mac_lpi_cfg", fpg_mpw_mac_lpi_cfg_prop);
fld_map_t fpg_mpw_lpi_tick_cnt_incr_val {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto fpg_mpw_lpi_tick_cnt_incr_val_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_lpi_tick_cnt_incr_val),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_lpi_tick_cnt_incr_val", fpg_mpw_lpi_tick_cnt_incr_val_prop);
fld_map_t fpg_mpw_lpi_status {
CREATE_ENTRY("mac0_lowp", 0, 1),
CREATE_ENTRY("xpcs0_tx_lpi_mode", 1, 2),
CREATE_ENTRY("xpcs0_tx_lpi_state", 3, 3),
CREATE_ENTRY("xpcs0_rx_lpi_mode", 6, 1),
CREATE_ENTRY("xpcs0_rx_lpi_state", 7, 3),
CREATE_ENTRY("xpcs0_rx_lpi_active", 10, 1),
CREATE_ENTRY("mac1_lowp", 11, 1),
CREATE_ENTRY("xpcs1_tx_lpi_mode", 12, 2),
CREATE_ENTRY("xpcs1_tx_lpi_state", 14, 3),
CREATE_ENTRY("xpcs1_rx_lpi_mode", 17, 1),
CREATE_ENTRY("xpcs1_rx_lpi_state", 18, 3),
CREATE_ENTRY("xpcs1_rx_lpi_active", 21, 1),
CREATE_ENTRY("mac2_lowp", 22, 1),
CREATE_ENTRY("xpcs2_tx_lpi_mode", 23, 2),
CREATE_ENTRY("xpcs2_tx_lpi_state", 25, 3),
CREATE_ENTRY("xpcs2_rx_lpi_mode", 28, 1),
CREATE_ENTRY("xpcs2_rx_lpi_state", 29, 3),
CREATE_ENTRY("xpcs2_rx_lpi_active", 32, 1),
CREATE_ENTRY("mac3_lowp", 33, 1),
CREATE_ENTRY("xpcs3_tx_lpi_mode", 34, 2),
CREATE_ENTRY("xpcs3_tx_lpi_state", 36, 3),
CREATE_ENTRY("xpcs3_rx_lpi_mode", 39, 1),
CREATE_ENTRY("xpcs3_rx_lpi_state", 40, 3),
CREATE_ENTRY("xpcs3_rx_lpi_active", 43, 1),
CREATE_ENTRY("sg0_tx_lpi_active", 44, 1),
CREATE_ENTRY("sg0_pma_txmode_quiet", 45, 1),
CREATE_ENTRY("sg0_rx_lpi_active", 46, 1),
CREATE_ENTRY("sg0_pma_rxmode_quiet", 47, 1),
CREATE_ENTRY("sg0_rx_wake_err", 48, 1),
CREATE_ENTRY("__rsvd", 49, 15)
};auto fpg_mpw_lpi_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_lpi_status),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_lpi_status", fpg_mpw_lpi_status_prop);
fld_map_t fpg_mpw_sw_reset {
CREATE_ENTRY("rst_sd_tx_n", 0, 4),
CREATE_ENTRY("rst_sd_rx_n", 4, 4),
CREATE_ENTRY("rst_xpcs_n", 8, 1),
CREATE_ENTRY("rst_spcs_n", 9, 1),
CREATE_ENTRY("rst_ref_clk_n", 10, 1),
CREATE_ENTRY("rst_mac_ref_clk_n", 11, 4),
CREATE_ENTRY("rst_reg_clk_n", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_mpw_sw_reset_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_sw_reset),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_sw_reset", fpg_mpw_sw_reset_prop);
fld_map_t fpg_mpw_pcs_cfg {
CREATE_ENTRY("fec91_en", 0, 4),
CREATE_ENTRY("fec91_kp_mode", 4, 4),
CREATE_ENTRY("sd_n2", 8, 4),
CREATE_ENTRY("fec91_1lane_strm0", 12, 1),
CREATE_ENTRY("fec91_1lane_strm2", 13, 1),
CREATE_ENTRY("rxlaui_en_strm0", 14, 1),
CREATE_ENTRY("rxlaui_en_strm2", 15, 1),
CREATE_ENTRY("pcs100_en", 16, 1),
CREATE_ENTRY("mode40_en", 17, 1),
CREATE_ENTRY("sg0_en", 18, 1),
CREATE_ENTRY("mode50_1lane_strm0", 19, 1),
CREATE_ENTRY("mode50_1lane_strm2", 20, 1),
CREATE_ENTRY("mode100_2lane_strm0", 21, 1),
CREATE_ENTRY("__rsvd", 22, 42)
};auto fpg_mpw_pcs_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_pcs_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_pcs_cfg", fpg_mpw_pcs_cfg_prop);
fld_map_t fpg_mpw_pcs_status {
CREATE_ENTRY("align_done", 0, 1),
CREATE_ENTRY("block_lock", 1, 20),
CREATE_ENTRY("hi_ber", 21, 4),
CREATE_ENTRY("link_status", 25, 4),
CREATE_ENTRY("ber_timer_done", 29, 4),
CREATE_ENTRY("amps_lock", 33, 4),
CREATE_ENTRY("rsfec_aligned", 37, 4),
CREATE_ENTRY("sg0_rx_sync", 41, 1),
CREATE_ENTRY("sg0_an_done", 42, 1),
CREATE_ENTRY("sg0_speed", 43, 2),
CREATE_ENTRY("__rsvd", 45, 19)
};auto fpg_mpw_pcs_status_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_pcs_status),
0x108,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_pcs_status", fpg_mpw_pcs_status_prop);
fld_map_t fpg_mpw_tx_rx_loopback_cfg {
CREATE_ENTRY("en", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fpg_mpw_tx_rx_loopback_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_tx_rx_loopback_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_tx_rx_loopback_cfg", fpg_mpw_tx_rx_loopback_cfg_prop);
fld_map_t fpg_mpw_rx_err_mask {
CREATE_ENTRY("len_err_mask", 0, 1),
CREATE_ENTRY("crc_err_mask", 1, 1),
CREATE_ENTRY("dec_err_mask", 2, 1),
CREATE_ENTRY("fifo_ovfl_err_mask", 3, 1),
CREATE_ENTRY("fault_err_mask", 4, 1),
CREATE_ENTRY("phy_err_mask", 5, 1),
CREATE_ENTRY("poisoned_crc_err_mask", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto fpg_mpw_rx_err_mask_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_rx_err_mask),
0x118,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_rx_err_mask", fpg_mpw_rx_err_mask_prop);
fld_map_t fpg_mpw_mem_err_inj_cfg {
CREATE_ENTRY("fpg_mpw_desk0_mem", 0, 1),
CREATE_ENTRY("fpg_mpw_desk1_mem", 1, 1),
CREATE_ENTRY("fpg_mpw_desk2_mem", 2, 1),
CREATE_ENTRY("fpg_mpw_desk3_mem", 3, 1),
CREATE_ENTRY("fpg_mpw_desk4_mem", 4, 1),
CREATE_ENTRY("fpg_mpw_desk5_mem", 5, 1),
CREATE_ENTRY("fpg_mpw_desk6_mem", 6, 1),
CREATE_ENTRY("fpg_mpw_desk7_mem", 7, 1),
CREATE_ENTRY("fpg_mpw_tstm_mem", 8, 1),
CREATE_ENTRY("fpg_mpw_rstm_mem", 9, 1),
CREATE_ENTRY("fpg_mpw_f91m_mem", 10, 1),
CREATE_ENTRY("fpg_mpw_f91dm0_mem", 11, 1),
CREATE_ENTRY("fpg_mpw_f91dm1_mem", 12, 1),
CREATE_ENTRY("fpg_mpw_f91dm2_mem", 13, 1),
CREATE_ENTRY("fpg_mpw_f91dm3_mem", 14, 1),
CREATE_ENTRY("err_type", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fpg_mpw_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_mem_err_inj_cfg),
0x130,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_mem_err_inj_cfg", fpg_mpw_mem_err_inj_cfg_prop);
fld_map_t fpg_mpw_sram_log_err {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto fpg_mpw_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_sram_log_err),
0x138,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_sram_log_err", fpg_mpw_sram_log_err_prop);
fld_map_t fpg_mpw_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto fpg_mpw_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_sram_log_addr),
0x140,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_sram_log_addr", fpg_mpw_sram_log_addr_prop);
fld_map_t fpg_mpw_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fpg_mpw_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_mpw_fla_ring_module_id_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(fpg_mpw_1, "fpg_mpw_fla_ring_module_id_cfg", fpg_mpw_fla_ring_module_id_cfg_prop);
 // END fpg_mpw 
}
{
 // BEGIN wro 
auto wro_0 = nu_rng[0].add_an({"wro"}, 0x6000000, 1, 0x0);
fld_map_t wro_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto wro_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_timeout_thresh_cfg", wro_timeout_thresh_cfg_prop);
fld_map_t wro_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto wro_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_timedout_sta", wro_timedout_sta_prop);
fld_map_t wro_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto wro_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(wro_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_timeout_clr", wro_timeout_clr_prop);
fld_map_t wro_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto wro_features_prop = csr_prop_t(
std::make_shared<csr_s>(wro_features),
0xB8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_features", wro_features_prop);
fld_map_t wro_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto wro_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(wro_spare_pio),
0xC0,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_spare_pio", wro_spare_pio_prop);
fld_map_t wro_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto wro_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(wro_scratchpad),
0xC8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_scratchpad", wro_scratchpad_prop);
fld_map_t wro_mem_init_start_cfg {
CREATE_ENTRY("fld_hash_tbl_h10_mem", 0, 1),
CREATE_ENTRY("fld_hash_tbl_h11_mem", 1, 1),
CREATE_ENTRY("fld_hash_tbl_h12_mem", 2, 1),
CREATE_ENTRY("fld_hash_tbl_h13_mem", 3, 1),
CREATE_ENTRY("fld_hash_tbl_h20_mem", 4, 1),
CREATE_ENTRY("fld_hash_tbl_h21_mem", 5, 1),
CREATE_ENTRY("fld_hash_tbl_h22_mem", 6, 1),
CREATE_ENTRY("fld_hash_tbl_h23_mem", 7, 1),
CREATE_ENTRY("fld_hash_tbl_h30_mem", 8, 1),
CREATE_ENTRY("fld_hash_tbl_h31_mem", 9, 1),
CREATE_ENTRY("fld_hash_tbl_h32_mem", 10, 1),
CREATE_ENTRY("fld_hash_tbl_h33_mem", 11, 1),
CREATE_ENTRY("fld_hash_tbl_h40_mem", 12, 1),
CREATE_ENTRY("fld_hash_tbl_h41_mem", 13, 1),
CREATE_ENTRY("fld_hash_tbl_h42_mem", 14, 1),
CREATE_ENTRY("fld_hash_tbl_h43_mem", 15, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h1_mem", 16, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h2_mem", 17, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h3_mem", 18, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h4_mem", 19, 1),
CREATE_ENTRY("fld_dequeue_fifo0_mem", 20, 1),
CREATE_ENTRY("fld_dequeue_fifo1_mem", 21, 1),
CREATE_ENTRY("fld_wun_db_mem", 22, 1),
CREATE_ENTRY("fld_fcb_pkt_ctx_mem", 23, 1),
CREATE_ENTRY("fld_wun_fl_mem", 24, 1),
CREATE_ENTRY("fld_tunnel_ctx_psn_mem", 25, 1),
CREATE_ENTRY("fld_tunnel_ctx_pktcnt_mem", 26, 1),
CREATE_ENTRY("fld_tunnel_cfg_role_tbl_mem", 27, 1),
CREATE_ENTRY("fld_tunnel_timeout_event_log_mem", 28, 1),
CREATE_ENTRY("fld_tunnel_seqn_error_event_log_mem", 29, 1),
CREATE_ENTRY("__rsvd", 30, 34)
};auto wro_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_mem_init_start_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_mem_init_start_cfg", wro_mem_init_start_cfg_prop);
fld_map_t wro_mem_init_done_sta {
CREATE_ENTRY("fld_hash_tbl_h10_mem", 0, 1),
CREATE_ENTRY("fld_hash_tbl_h11_mem", 1, 1),
CREATE_ENTRY("fld_hash_tbl_h12_mem", 2, 1),
CREATE_ENTRY("fld_hash_tbl_h13_mem", 3, 1),
CREATE_ENTRY("fld_hash_tbl_h20_mem", 4, 1),
CREATE_ENTRY("fld_hash_tbl_h21_mem", 5, 1),
CREATE_ENTRY("fld_hash_tbl_h22_mem", 6, 1),
CREATE_ENTRY("fld_hash_tbl_h23_mem", 7, 1),
CREATE_ENTRY("fld_hash_tbl_h30_mem", 8, 1),
CREATE_ENTRY("fld_hash_tbl_h31_mem", 9, 1),
CREATE_ENTRY("fld_hash_tbl_h32_mem", 10, 1),
CREATE_ENTRY("fld_hash_tbl_h33_mem", 11, 1),
CREATE_ENTRY("fld_hash_tbl_h40_mem", 12, 1),
CREATE_ENTRY("fld_hash_tbl_h41_mem", 13, 1),
CREATE_ENTRY("fld_hash_tbl_h42_mem", 14, 1),
CREATE_ENTRY("fld_hash_tbl_h43_mem", 15, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h1_mem", 16, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h2_mem", 17, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h3_mem", 18, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h4_mem", 19, 1),
CREATE_ENTRY("fld_dequeue_fifo0_mem", 20, 1),
CREATE_ENTRY("fld_dequeue_fifo1_mem", 21, 1),
CREATE_ENTRY("fld_wun_db_mem", 22, 1),
CREATE_ENTRY("fld_fcb_pkt_ctx_mem", 23, 1),
CREATE_ENTRY("fld_wun_fl_mem", 24, 1),
CREATE_ENTRY("fld_tunnel_ctx_psn_mem", 25, 1),
CREATE_ENTRY("fld_tunnel_ctx_pktcnt_mem", 26, 1),
CREATE_ENTRY("fld_tunnel_cfg_role_tbl_mem", 27, 1),
CREATE_ENTRY("fld_tunnel_timeout_event_log_mem", 28, 1),
CREATE_ENTRY("fld_tunnel_seqn_error_event_log_mem", 29, 1),
CREATE_ENTRY("__rsvd", 30, 34)
};auto wro_mem_init_done_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_mem_init_done_sta),
0xD8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_mem_init_done_sta", wro_mem_init_done_sta_prop);
fld_map_t wro_mem_log_err_sta {
CREATE_ENTRY("fld_hash_tbl_h10_mem_cerr", 0, 1),
CREATE_ENTRY("fld_hash_tbl_h11_mem_cerr", 1, 1),
CREATE_ENTRY("fld_hash_tbl_h12_mem_cerr", 2, 1),
CREATE_ENTRY("fld_hash_tbl_h13_mem_cerr", 3, 1),
CREATE_ENTRY("fld_hash_tbl_h20_mem_cerr", 4, 1),
CREATE_ENTRY("fld_hash_tbl_h21_mem_cerr", 5, 1),
CREATE_ENTRY("fld_hash_tbl_h22_mem_cerr", 6, 1),
CREATE_ENTRY("fld_hash_tbl_h23_mem_cerr", 7, 1),
CREATE_ENTRY("fld_hash_tbl_h30_mem_cerr", 8, 1),
CREATE_ENTRY("fld_hash_tbl_h31_mem_cerr", 9, 1),
CREATE_ENTRY("fld_hash_tbl_h32_mem_cerr", 10, 1),
CREATE_ENTRY("fld_hash_tbl_h33_mem_cerr", 11, 1),
CREATE_ENTRY("fld_hash_tbl_h40_mem_cerr", 12, 1),
CREATE_ENTRY("fld_hash_tbl_h41_mem_cerr", 13, 1),
CREATE_ENTRY("fld_hash_tbl_h42_mem_cerr", 14, 1),
CREATE_ENTRY("fld_hash_tbl_h43_mem_cerr", 15, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h1_mem_cerr", 16, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h2_mem_cerr", 17, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h3_mem_cerr", 18, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h4_mem_cerr", 19, 1),
CREATE_ENTRY("fld_dequeue_fifo0_mem_cerr", 20, 1),
CREATE_ENTRY("fld_dequeue_fifo1_mem_cerr", 21, 1),
CREATE_ENTRY("fld_wun_db_mem_cerr", 22, 1),
CREATE_ENTRY("fld_fcb_pkt_ctx_mem_cerr", 23, 1),
CREATE_ENTRY("fld_wun_fl_mem_cerr", 24, 1),
CREATE_ENTRY("fld_tunnel_ctx_psn_mem_cerr", 25, 1),
CREATE_ENTRY("fld_tunnel_ctx_pktcnt_mem_cerr", 26, 1),
CREATE_ENTRY("fld_tunnel_cfg_role_tbl_mem_cerr", 27, 1),
CREATE_ENTRY("fld_tunnel_timeout_event_log_mem_cerr", 28, 1),
CREATE_ENTRY("fld_tunnel_seqn_error_event_log_mem_cerr", 29, 1),
CREATE_ENTRY("fld_hash_tbl_h10_mem_ucerr", 30, 1),
CREATE_ENTRY("fld_hash_tbl_h11_mem_ucerr", 31, 1),
CREATE_ENTRY("fld_hash_tbl_h12_mem_ucerr", 32, 1),
CREATE_ENTRY("fld_hash_tbl_h13_mem_ucerr", 33, 1),
CREATE_ENTRY("fld_hash_tbl_h20_mem_ucerr", 34, 1),
CREATE_ENTRY("fld_hash_tbl_h21_mem_ucerr", 35, 1),
CREATE_ENTRY("fld_hash_tbl_h22_mem_ucerr", 36, 1),
CREATE_ENTRY("fld_hash_tbl_h23_mem_ucerr", 37, 1),
CREATE_ENTRY("fld_hash_tbl_h30_mem_ucerr", 38, 1),
CREATE_ENTRY("fld_hash_tbl_h31_mem_ucerr", 39, 1),
CREATE_ENTRY("fld_hash_tbl_h32_mem_ucerr", 40, 1),
CREATE_ENTRY("fld_hash_tbl_h33_mem_ucerr", 41, 1),
CREATE_ENTRY("fld_hash_tbl_h40_mem_ucerr", 42, 1),
CREATE_ENTRY("fld_hash_tbl_h41_mem_ucerr", 43, 1),
CREATE_ENTRY("fld_hash_tbl_h42_mem_ucerr", 44, 1),
CREATE_ENTRY("fld_hash_tbl_h43_mem_ucerr", 45, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h1_mem_ucerr", 46, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h2_mem_ucerr", 47, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h3_mem_ucerr", 48, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h4_mem_ucerr", 49, 1),
CREATE_ENTRY("fld_dequeue_fifo0_mem_ucerr", 50, 1),
CREATE_ENTRY("fld_dequeue_fifo1_mem_ucerr", 51, 1),
CREATE_ENTRY("fld_wun_db_mem_ucerr", 52, 1),
CREATE_ENTRY("fld_fcb_pkt_ctx_mem_ucerr", 53, 1),
CREATE_ENTRY("fld_wun_fl_mem_ucerr", 54, 1),
CREATE_ENTRY("fld_tunnel_ctx_psn_mem_ucerr", 55, 1),
CREATE_ENTRY("fld_tunnel_ctx_pktcnt_mem_ucerr", 56, 1),
CREATE_ENTRY("fld_tunnel_cfg_role_tbl_mem_ucerr", 57, 1),
CREATE_ENTRY("fld_tunnel_timeout_event_log_mem_ucerr", 58, 1),
CREATE_ENTRY("fld_tunnel_seqn_error_event_log_mem_ucerr", 59, 1),
CREATE_ENTRY("__rsvd", 60, 4)
};auto wro_mem_log_err_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_mem_log_err_sta),
0xE0,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_mem_log_err_sta", wro_mem_log_err_sta_prop);
fld_map_t wro_mem_log_syndrome_sta {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto wro_mem_log_syndrome_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_mem_log_syndrome_sta),
0xE8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_mem_log_syndrome_sta", wro_mem_log_syndrome_sta_prop);
fld_map_t wro_mem_log_addr_sta {
CREATE_ENTRY("fld_val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto wro_mem_log_addr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_mem_log_addr_sta),
0xF0,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_mem_log_addr_sta", wro_mem_log_addr_sta_prop);
fld_map_t wro_mem_err_inj_cfg {
CREATE_ENTRY("fld_hash_tbl_h10_mem", 0, 1),
CREATE_ENTRY("fld_hash_tbl_h11_mem", 1, 1),
CREATE_ENTRY("fld_hash_tbl_h12_mem", 2, 1),
CREATE_ENTRY("fld_hash_tbl_h13_mem", 3, 1),
CREATE_ENTRY("fld_hash_tbl_h20_mem", 4, 1),
CREATE_ENTRY("fld_hash_tbl_h21_mem", 5, 1),
CREATE_ENTRY("fld_hash_tbl_h22_mem", 6, 1),
CREATE_ENTRY("fld_hash_tbl_h23_mem", 7, 1),
CREATE_ENTRY("fld_hash_tbl_h30_mem", 8, 1),
CREATE_ENTRY("fld_hash_tbl_h31_mem", 9, 1),
CREATE_ENTRY("fld_hash_tbl_h32_mem", 10, 1),
CREATE_ENTRY("fld_hash_tbl_h33_mem", 11, 1),
CREATE_ENTRY("fld_hash_tbl_h40_mem", 12, 1),
CREATE_ENTRY("fld_hash_tbl_h41_mem", 13, 1),
CREATE_ENTRY("fld_hash_tbl_h42_mem", 14, 1),
CREATE_ENTRY("fld_hash_tbl_h43_mem", 15, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h1_mem", 16, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h2_mem", 17, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h3_mem", 18, 1),
CREATE_ENTRY("fld_hash_tbl_vldmap_h4_mem", 19, 1),
CREATE_ENTRY("fld_dequeue_fifo0_mem", 20, 1),
CREATE_ENTRY("fld_dequeue_fifo1_mem", 21, 1),
CREATE_ENTRY("fld_wun_db_mem", 22, 1),
CREATE_ENTRY("fld_fcb_pkt_ctx_mem", 23, 1),
CREATE_ENTRY("fld_wun_fl_mem", 24, 1),
CREATE_ENTRY("fld_tunnel_ctx_psn_mem", 25, 1),
CREATE_ENTRY("fld_tunnel_ctx_pktcnt_mem", 26, 1),
CREATE_ENTRY("fld_tunnel_cfg_role_tbl_mem", 27, 1),
CREATE_ENTRY("fld_tunnel_timeout_event_log_mem", 28, 1),
CREATE_ENTRY("fld_tunnel_seqn_error_event_log_mem", 29, 1),
CREATE_ENTRY("fld_err_type", 30, 1),
CREATE_ENTRY("__rsvd", 31, 33)
};auto wro_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_mem_err_inj_cfg),
0xF8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_mem_err_inj_cfg", wro_mem_err_inj_cfg_prop);
fld_map_t wro_timer_ctrl_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_tick_cnt", 1, 8),
CREATE_ENTRY("fld_normal_tov", 9, 4),
CREATE_ENTRY("fld_fast_tov", 13, 4),
CREATE_ENTRY("fld_timestamp_cnt_max", 17, 10),
CREATE_ENTRY("fld_fast_tov_pkt_thrsh", 27, 15),
CREATE_ENTRY("__rsvd", 42, 22)
};auto wro_timer_ctrl_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_timer_ctrl_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_timer_ctrl_cfg", wro_timer_ctrl_cfg_prop);
fld_map_t wro_misc_dbg_cfg {
CREATE_ENTRY("fld_dbg_tunnel_id", 0, 14),
CREATE_ENTRY("fld_hnu_mode_flush_enable", 14, 1),
CREATE_ENTRY("fld_flow_ctrl_cnt_enable", 15, 1),
CREATE_ENTRY("fld_tdm_enable", 16, 1),
CREATE_ENTRY("fld_psn_range", 17, 1),
CREATE_ENTRY("fld_cuckoo_hash_idx_mask", 18, 2),
CREATE_ENTRY("fld_tunnel0_byp_enable", 20, 1),
CREATE_ENTRY("fld_sn_spray_hash_disable", 21, 1),
CREATE_ENTRY("fld_stash_cam_full_thresh", 22, 8),
CREATE_ENTRY("__rsvd", 30, 34)
};auto wro_misc_dbg_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_misc_dbg_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_misc_dbg_cfg", wro_misc_dbg_cfg_prop);
fld_map_t wro_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto wro_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_fla_ring_module_id_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_fla_ring_module_id_cfg", wro_fla_ring_module_id_cfg_prop);
fld_map_t wro_cuckoo_hash_seed_cfg {
CREATE_ENTRY("fld_seed_h1", 0, 8),
CREATE_ENTRY("fld_seed_h2", 8, 8),
CREATE_ENTRY("fld_seed_h3", 16, 8),
CREATE_ENTRY("fld_seed_h4", 24, 8),
CREATE_ENTRY("__rsvd", 32, 32)
};auto wro_cuckoo_hash_seed_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_cuckoo_hash_seed_cfg),
0x128,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_cuckoo_hash_seed_cfg", wro_cuckoo_hash_seed_cfg_prop);
fld_map_t wro_wu_msg_map_cfg {
CREATE_ENTRY("fld_so", 0, 1),
CREATE_ENTRY("fld_vc0", 1, 2),
CREATE_ENTRY("fld_vc1", 3, 2),
CREATE_ENTRY("fld_sgid_base", 5, 5),
CREATE_ENTRY("fld_slid", 10, 5),
CREATE_ENTRY("fld_en_arg1_buf_addr", 15, 1),
CREATE_ENTRY("fld_en_arg2_buf_addr", 16, 1),
CREATE_ENTRY("fld_en_opaq1_buf_addr", 17, 1),
CREATE_ENTRY("fld_en_opaq2_buf_addr", 18, 1),
CREATE_ENTRY("__rsvd", 19, 45)
};auto wro_wu_msg_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_wu_msg_map_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_wu_msg_map_cfg", wro_wu_msg_map_cfg_prop);
fld_map_t wro_vp_wu_msg_type_map_cfg {
CREATE_ENTRY("fld_dlid0", 0, 1),
CREATE_ENTRY("fld_dlid1", 1, 1),
CREATE_ENTRY("fld_dlid2", 2, 1),
CREATE_ENTRY("fld_dlid3", 3, 1),
CREATE_ENTRY("fld_dlid4", 4, 1),
CREATE_ENTRY("fld_dlid5", 5, 1),
CREATE_ENTRY("fld_dlid6", 6, 1),
CREATE_ENTRY("fld_dlid7", 7, 1),
CREATE_ENTRY("fld_dlid8", 8, 1),
CREATE_ENTRY("fld_dlid9", 9, 1),
CREATE_ENTRY("fld_dlid10", 10, 1),
CREATE_ENTRY("fld_dlid11", 11, 1),
CREATE_ENTRY("fld_dlid12", 12, 1),
CREATE_ENTRY("fld_dlid13", 13, 1),
CREATE_ENTRY("fld_dlid14", 14, 1),
CREATE_ENTRY("fld_dlid15", 15, 1),
CREATE_ENTRY("fld_dlid16", 16, 1),
CREATE_ENTRY("fld_dlid17", 17, 1),
CREATE_ENTRY("fld_dlid18", 18, 1),
CREATE_ENTRY("fld_dlid19", 19, 1),
CREATE_ENTRY("fld_dlid20", 20, 1),
CREATE_ENTRY("fld_dlid21", 21, 1),
CREATE_ENTRY("fld_dlid22", 22, 1),
CREATE_ENTRY("fld_dlid23", 23, 1),
CREATE_ENTRY("fld_dlid24", 24, 1),
CREATE_ENTRY("fld_dlid25", 25, 1),
CREATE_ENTRY("fld_dlid26", 26, 1),
CREATE_ENTRY("fld_dlid27", 27, 1),
CREATE_ENTRY("fld_dlid28", 28, 1),
CREATE_ENTRY("fld_dlid29", 29, 1),
CREATE_ENTRY("fld_dlid30", 30, 1),
CREATE_ENTRY("fld_dlid31", 31, 1),
CREATE_ENTRY("__rsvd", 32, 32)
};auto wro_vp_wu_msg_type_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_vp_wu_msg_type_map_cfg),
0x158,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_vp_wu_msg_type_map_cfg", wro_vp_wu_msg_type_map_cfg_prop);
fld_map_t wro_vpp_wu_msg_cfg {
CREATE_ENTRY("fld_arg0", 0, 16),
CREATE_ENTRY("fld_arg1", 16, 16),
CREATE_ENTRY("fld_arg2", 32, 16),
CREATE_ENTRY("__rsvd", 48, 16)
};auto wro_vpp_wu_msg_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_vpp_wu_msg_cfg),
0x170,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_vpp_wu_msg_cfg", wro_vpp_wu_msg_cfg_prop);
fld_map_t wro_le_wu_msg_cfg {
CREATE_ENTRY("fld_keyptr", 0, 16),
CREATE_ENTRY("fld_opaque1", 16, 16),
CREATE_ENTRY("fld_opaque2", 32, 16),
CREATE_ENTRY("__rsvd", 48, 16)
};auto wro_le_wu_msg_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_le_wu_msg_cfg),
0x178,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_le_wu_msg_cfg", wro_le_wu_msg_cfg_prop);
fld_map_t wro_nu_wu_msg_cfg {
CREATE_ENTRY("fld_err_sw_opcode", 0, 24),
CREATE_ENTRY("fld_cmdlist_ptr_flags", 24, 8),
CREATE_ENTRY("fld_cmdlist_size", 32, 8),
CREATE_ENTRY("fld_arg1_rsvd", 40, 24)
};auto wro_nu_wu_msg_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_nu_wu_msg_cfg),
0x180,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_nu_wu_msg_cfg", wro_nu_wu_msg_cfg_prop);
fld_map_t wro_buffer_address_cfg {
CREATE_ENTRY("fld_buffer_handle_pos", 0, 6),
CREATE_ENTRY("fld_pc_pos", 6, 6),
CREATE_ENTRY("fld_base_val", 12, 48),
CREATE_ENTRY("__rsvd", 60, 4)
};auto wro_buffer_address_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_buffer_address_cfg),
0x188,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_buffer_address_cfg", wro_buffer_address_cfg_prop);
fld_map_t wro_sn_msg_map_cfg {
CREATE_ENTRY("fld_tag", 0, 8),
CREATE_ENTRY("fld_bm_flags", 8, 8),
CREATE_ENTRY("fld_so", 16, 1),
CREATE_ENTRY("fld_vc", 17, 2),
CREATE_ENTRY("fld_slid", 19, 5),
CREATE_ENTRY("fld_dlid", 24, 5),
CREATE_ENTRY("fld_sgid_base", 29, 5),
CREATE_ENTRY("__rsvd", 34, 30)
};auto wro_sn_msg_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_sn_msg_map_cfg),
0x190,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_sn_msg_map_cfg", wro_sn_msg_map_cfg_prop);
fld_map_t wro_sn_msg_dgid_map_cfg {
CREATE_ENTRY("fld_pc0", 0, 5),
CREATE_ENTRY("fld_pc1", 5, 5),
CREATE_ENTRY("fld_pc2", 10, 5),
CREATE_ENTRY("fld_pc3", 15, 5),
CREATE_ENTRY("fld_pc4", 20, 5),
CREATE_ENTRY("fld_pc5", 25, 5),
CREATE_ENTRY("fld_pc6", 30, 5),
CREATE_ENTRY("fld_pc7", 35, 5),
CREATE_ENTRY("__rsvd", 40, 24)
};auto wro_sn_msg_dgid_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_sn_msg_dgid_map_cfg),
0x198,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_sn_msg_dgid_map_cfg", wro_sn_msg_dgid_map_cfg_prop);
fld_map_t wro_wun_fl_cfg {
CREATE_ENTRY("fld_psw_xoff_thresh", 0, 15),
CREATE_ENTRY("fld_psw_xon_thresh", 15, 15),
CREATE_ENTRY("fld_fcb_xoff_thresh", 30, 15),
CREATE_ENTRY("fld_fcb_xon_thresh", 45, 15),
CREATE_ENTRY("__rsvd", 60, 4)
};auto wro_wun_fl_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(wro_wun_fl_cfg),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_wun_fl_cfg", wro_wun_fl_cfg_prop);
fld_map_t wro_wun_fl_sta {
CREATE_ENTRY("fld_avail_cnt", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto wro_wun_fl_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_wun_fl_sta),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_wun_fl_sta", wro_wun_fl_sta_prop);
fld_map_t wro_intf_flow_control_sta {
CREATE_ENTRY("fld_efp_if", 0, 1),
CREATE_ENTRY("fld_sn_if0", 1, 4),
CREATE_ENTRY("fld_sn_if1", 5, 4),
CREATE_ENTRY("fld_sn_if2", 9, 4),
CREATE_ENTRY("__rsvd", 13, 51)
};auto wro_intf_flow_control_sta_prop = csr_prop_t(
std::make_shared<csr_s>(wro_intf_flow_control_sta),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(wro_0, "wro_intf_flow_control_sta", wro_intf_flow_control_sta_prop);
 // END wro 
}
{
 // BEGIN fcb 
auto fcb_0 = nu_rng[0].add_an({"fcb"}, 0x7000000, 1, 0x0);
fld_map_t fcb_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fcb_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_timeout_thresh_cfg", fcb_timeout_thresh_cfg_prop);
fld_map_t fcb_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fcb_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_timedout_sta", fcb_timedout_sta_prop);
fld_map_t fcb_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fcb_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_timeout_clr", fcb_timeout_clr_prop);
fld_map_t fcb_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fcb_features_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_features),
0x90,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_features", fcb_features_prop);
fld_map_t fcb_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fcb_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_spare_pio),
0x98,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_spare_pio", fcb_spare_pio_prop);
fld_map_t fcb_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fcb_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_scratchpad),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_scratchpad", fcb_scratchpad_prop);
fld_map_t fcb_mem_init_start_cfg {
CREATE_ENTRY("fld_src_cfg_role_tbl_mem", 0, 1),
CREATE_ENTRY("fld_src_queue_ctx_mem", 1, 1),
CREATE_ENTRY("fld_src_timer_mem", 2, 1),
CREATE_ENTRY("fld_src_flow_wt_tbl_mem", 3, 1),
CREATE_ENTRY("fld_src_impairment_tbl_mem", 4, 1),
CREATE_ENTRY("fld_scale_dn_fact_tbl_mem", 5, 1),
CREATE_ENTRY("fld_req_sch_llist_mem", 6, 1),
CREATE_ENTRY("fld_pkt_sch_llist_mem", 7, 1),
CREATE_ENTRY("fld_ncv_seqncer_mem", 8, 1),
CREATE_ENTRY("fld_ncv_status_tbl_mem", 9, 1),
CREATE_ENTRY("fld_dst_queue_ctx_mem", 10, 1),
CREATE_ENTRY("fld_dst_cfg_role_tbl_mem", 11, 1),
CREATE_ENTRY("fld_dst_timer_mem", 12, 1),
CREATE_ENTRY("fld_gnt_sch_ctx_mem", 13, 1),
CREATE_ENTRY("fld_gnt_sch_llist_mem", 14, 1),
CREATE_ENTRY("fld_dst_flow_wt_tbl_mem", 15, 1),
CREATE_ENTRY("fld_src_stats_cntr_mem", 16, 1),
CREATE_ENTRY("fld_dst_stats_cntr_mem", 17, 1),
CREATE_ENTRY("fld_gnt_sch_deq_updt_corr_mem", 18, 1),
CREATE_ENTRY("fld_src_trace_fifo_mem", 19, 1),
CREATE_ENTRY("fld_dst_trace_fifo_mem", 20, 1),
CREATE_ENTRY("__rsvd", 21, 43)
};auto fcb_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_mem_init_start_cfg),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_mem_init_start_cfg", fcb_mem_init_start_cfg_prop);
fld_map_t fcb_mem_init_done_sta {
CREATE_ENTRY("fld_src_cfg_role_tbl_mem", 0, 1),
CREATE_ENTRY("fld_src_queue_ctx_mem", 1, 1),
CREATE_ENTRY("fld_src_timer_mem", 2, 1),
CREATE_ENTRY("fld_src_flow_wt_tbl_mem", 3, 1),
CREATE_ENTRY("fld_src_impairment_tbl_mem", 4, 1),
CREATE_ENTRY("fld_scale_dn_fact_tbl_mem", 5, 1),
CREATE_ENTRY("fld_req_sch_llist_mem", 6, 1),
CREATE_ENTRY("fld_pkt_sch_llist_mem", 7, 1),
CREATE_ENTRY("fld_ncv_seqncer_mem", 8, 1),
CREATE_ENTRY("fld_ncv_status_tbl_mem", 9, 1),
CREATE_ENTRY("fld_dst_queue_ctx_mem", 10, 1),
CREATE_ENTRY("fld_dst_cfg_role_tbl_mem", 11, 1),
CREATE_ENTRY("fld_dst_timer_mem", 12, 1),
CREATE_ENTRY("fld_gnt_sch_ctx_mem", 13, 1),
CREATE_ENTRY("fld_gnt_sch_llist_mem", 14, 1),
CREATE_ENTRY("fld_dst_flow_wt_tbl_mem", 15, 1),
CREATE_ENTRY("fld_src_stats_cntr_mem", 16, 1),
CREATE_ENTRY("fld_dst_stats_cntr_mem", 17, 1),
CREATE_ENTRY("fld_gnt_sch_deq_updt_corr_mem", 18, 1),
CREATE_ENTRY("fld_src_trace_fifo_mem", 19, 1),
CREATE_ENTRY("fld_dst_trace_fifo_mem", 20, 1),
CREATE_ENTRY("__rsvd", 21, 43)
};auto fcb_mem_init_done_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_mem_init_done_sta),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_mem_init_done_sta", fcb_mem_init_done_sta_prop);
fld_map_t fcb_mem_log_err_sta {
CREATE_ENTRY("fld_src_cfg_role_tbl_mem_cerr", 0, 1),
CREATE_ENTRY("fld_src_queue_ctx_mem_cerr", 1, 1),
CREATE_ENTRY("fld_src_timer_mem_cerr", 2, 1),
CREATE_ENTRY("fld_src_flow_wt_tbl_mem_cerr", 3, 1),
CREATE_ENTRY("fld_src_impairment_tbl_mem_cerr", 4, 1),
CREATE_ENTRY("fld_scale_dn_fact_tbl_mem_cerr", 5, 1),
CREATE_ENTRY("fld_req_sch_llist_mem_cerr", 6, 1),
CREATE_ENTRY("fld_pkt_sch_llist_mem_cerr", 7, 1),
CREATE_ENTRY("fld_ncv_seqncer_mem_cerr", 8, 1),
CREATE_ENTRY("fld_ncv_status_tbl_mem_cerr", 9, 1),
CREATE_ENTRY("fld_dst_queue_ctx_mem_cerr", 10, 1),
CREATE_ENTRY("fld_dst_cfg_role_tbl_mem_cerr", 11, 1),
CREATE_ENTRY("fld_dst_timer_mem_cerr", 12, 1),
CREATE_ENTRY("fld_gnt_sch_ctx_mem_cerr", 13, 1),
CREATE_ENTRY("fld_gnt_sch_llist_mem_cerr", 14, 1),
CREATE_ENTRY("fld_dst_flow_wt_tbl_mem_cerr", 15, 1),
CREATE_ENTRY("fld_src_stats_cntr_mem_cerr", 16, 1),
CREATE_ENTRY("fld_dst_stats_cntr_mem_cerr", 17, 1),
CREATE_ENTRY("fld_gnt_sch_deq_updt_corr_mem_cerr", 18, 1),
CREATE_ENTRY("fld_src_trace_fifo_mem_cerr", 19, 1),
CREATE_ENTRY("fld_dst_trace_fifo_mem_cerr", 20, 1),
CREATE_ENTRY("fld_src_cfg_role_tbl_mem_ucerr", 21, 1),
CREATE_ENTRY("fld_src_queue_ctx_mem_ucerr", 22, 1),
CREATE_ENTRY("fld_src_timer_mem_ucerr", 23, 1),
CREATE_ENTRY("fld_src_flow_wt_tbl_mem_ucerr", 24, 1),
CREATE_ENTRY("fld_src_impairment_tbl_mem_ucerr", 25, 1),
CREATE_ENTRY("fld_scale_dn_fact_tbl_mem_ucerr", 26, 1),
CREATE_ENTRY("fld_req_sch_llist_mem_ucerr", 27, 1),
CREATE_ENTRY("fld_pkt_sch_llist_mem_ucerr", 28, 1),
CREATE_ENTRY("fld_ncv_seqncer_mem_ucerr", 29, 1),
CREATE_ENTRY("fld_ncv_status_tbl_mem_ucerr", 30, 1),
CREATE_ENTRY("fld_dst_queue_ctx_mem_ucerr", 31, 1),
CREATE_ENTRY("fld_dst_cfg_role_tbl_mem_ucerr", 32, 1),
CREATE_ENTRY("fld_dst_timer_mem_ucerr", 33, 1),
CREATE_ENTRY("fld_gnt_sch_ctx_mem_ucerr", 34, 1),
CREATE_ENTRY("fld_gnt_sch_llist_mem_ucerr", 35, 1),
CREATE_ENTRY("fld_dst_flow_wt_tbl_mem_ucerr", 36, 1),
CREATE_ENTRY("fld_src_stats_cntr_mem_ucerr", 37, 1),
CREATE_ENTRY("fld_dst_stats_cntr_mem_ucerr", 38, 1),
CREATE_ENTRY("fld_gnt_sch_deq_updt_corr_mem_ucerr", 39, 1),
CREATE_ENTRY("fld_src_trace_fifo_mem_ucerr", 40, 1),
CREATE_ENTRY("fld_dst_trace_fifo_mem_ucerr", 41, 1),
CREATE_ENTRY("__rsvd", 42, 22)
};auto fcb_mem_log_err_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_mem_log_err_sta),
0xC8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_mem_log_err_sta", fcb_mem_log_err_sta_prop);
fld_map_t fcb_mem_log_syndrome_sta {
CREATE_ENTRY("fld_val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto fcb_mem_log_syndrome_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_mem_log_syndrome_sta),
0xD0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_mem_log_syndrome_sta", fcb_mem_log_syndrome_sta_prop);
fld_map_t fcb_mem_log_addr_sta {
CREATE_ENTRY("fld_val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto fcb_mem_log_addr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_mem_log_addr_sta),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_mem_log_addr_sta", fcb_mem_log_addr_sta_prop);
fld_map_t fcb_mem_err_inj_cfg {
CREATE_ENTRY("fld_src_cfg_role_tbl_mem", 0, 1),
CREATE_ENTRY("fld_src_queue_ctx_mem", 1, 1),
CREATE_ENTRY("fld_src_timer_mem", 2, 1),
CREATE_ENTRY("fld_src_flow_wt_tbl_mem", 3, 1),
CREATE_ENTRY("fld_src_impairment_tbl_mem", 4, 1),
CREATE_ENTRY("fld_scale_dn_fact_tbl_mem", 5, 1),
CREATE_ENTRY("fld_req_sch_llist_mem", 6, 1),
CREATE_ENTRY("fld_pkt_sch_llist_mem", 7, 1),
CREATE_ENTRY("fld_ncv_seqncer_mem", 8, 1),
CREATE_ENTRY("fld_ncv_status_tbl_mem", 9, 1),
CREATE_ENTRY("fld_dst_queue_ctx_mem", 10, 1),
CREATE_ENTRY("fld_dst_cfg_role_tbl_mem", 11, 1),
CREATE_ENTRY("fld_dst_timer_mem", 12, 1),
CREATE_ENTRY("fld_gnt_sch_ctx_mem", 13, 1),
CREATE_ENTRY("fld_gnt_sch_llist_mem", 14, 1),
CREATE_ENTRY("fld_dst_flow_wt_tbl_mem", 15, 1),
CREATE_ENTRY("fld_src_stats_cntr_mem", 16, 1),
CREATE_ENTRY("fld_dst_stats_cntr_mem", 17, 1),
CREATE_ENTRY("fld_gnt_sch_deq_updt_corr_mem", 18, 1),
CREATE_ENTRY("fld_src_trace_fifo_mem", 19, 1),
CREATE_ENTRY("fld_dst_trace_fifo_mem", 20, 1),
CREATE_ENTRY("fld_err_type", 21, 1),
CREATE_ENTRY("__rsvd", 22, 42)
};auto fcb_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_mem_err_inj_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_mem_err_inj_cfg", fcb_mem_err_inj_cfg_prop);
fld_map_t fcb_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcb_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_fla_ring_module_id_cfg),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_fla_ring_module_id_cfg", fcb_fla_ring_module_id_cfg_prop);
fld_map_t fcb_gbl_cfg {
CREATE_ENTRY("fld_blk_sz", 0, 4),
CREATE_ENTRY("fld_fcp_num_qos", 4, 2),
CREATE_ENTRY("fld_bn_if_enable", 6, 1),
CREATE_ENTRY("fld_local_impl_adj_enable", 7, 1),
CREATE_ENTRY("fld_data_local_impl_adj_enable", 8, 1),
CREATE_ENTRY("fld_src_impl_updt_enable", 9, 1),
CREATE_ENTRY("fld_src_impl_req_adj_enable", 10, 1),
CREATE_ENTRY("fld_src_impl_gnt_adj_enable", 11, 1),
CREATE_ENTRY("fld_ctrl_tx_gbl_adj_enable", 12, 1),
CREATE_ENTRY("fld_ctrl_tx_fcp_adj_enable", 13, 1),
CREATE_ENTRY("fld_src_flow_wt_override_enable", 14, 1),
CREATE_ENTRY("fld_src_flow_wt_mantissa", 15, 4),
CREATE_ENTRY("fld_src_flow_wt_exponent", 19, 4),
CREATE_ENTRY("fld_scale_dn_override_enable", 23, 1),
CREATE_ENTRY("fld_pkt_flush_ignore_psw_xoff", 24, 1),
CREATE_ENTRY("fld_flow_ctrl_cnt_enable", 25, 1),
CREATE_ENTRY("fld_scale_dn_cong_thresh", 26, 8),
CREATE_ENTRY("__rsvd", 34, 30)
};auto fcb_gbl_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_gbl_cfg),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_gbl_cfg", fcb_gbl_cfg_prop);
fld_map_t fcb_req_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_req_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_req_datarate_pacer_cfg),
0x120,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_req_datarate_pacer_cfg", fcb_req_datarate_pacer_cfg_prop);
fld_map_t fcb_req_ctlmsg_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_msg_tx_adj_enable", 1, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 2, 12),
CREATE_ENTRY("fld_base_leak_rate", 14, 12),
CREATE_ENTRY("fld_admit_lvl_thresh", 26, 24),
CREATE_ENTRY("fld_update_val", 50, 12),
CREATE_ENTRY("__rsvd", 62, 2)
};auto fcb_req_ctlmsg_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_req_ctlmsg_pacer_cfg),
0x128,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_req_ctlmsg_pacer_cfg", fcb_req_ctlmsg_pacer_cfg_prop);
fld_map_t fcb_unsol_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_unsol_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_unsol_datarate_pacer_cfg),
0x130,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_unsol_datarate_pacer_cfg", fcb_unsol_datarate_pacer_cfg_prop);
fld_map_t fcb_src_gbl_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_src_gbl_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_datarate_pacer_cfg),
0x138,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_datarate_pacer_cfg", fcb_src_gbl_datarate_pacer_cfg_prop);
fld_map_t fcb_src_fcp_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_src_fcp_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_fcp_datarate_pacer_cfg),
0x140,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_fcp_datarate_pacer_cfg", fcb_src_fcp_datarate_pacer_cfg_prop);
fld_map_t fcb_src_nfcp_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_src_nfcp_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_nfcp_datarate_pacer_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_nfcp_datarate_pacer_cfg", fcb_src_nfcp_datarate_pacer_cfg_prop);
fld_map_t fcb_src_nfcp_pipe_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_src_nfcp_pipe_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_nfcp_pipe_datarate_pacer_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_nfcp_pipe_datarate_pacer_cfg", fcb_src_nfcp_pipe_datarate_pacer_cfg_prop);
fld_map_t fcb_src_drop_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_src_drop_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_drop_datarate_pacer_cfg),
0x158,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_drop_datarate_pacer_cfg", fcb_src_drop_datarate_pacer_cfg_prop);
fld_map_t fcb_tdp_lb_cfg {
CREATE_ENTRY("fld_pipe_pend_blks_thresh", 0, 16),
CREATE_ENTRY("fld_fcp_pend_blks_thresh", 16, 16),
CREATE_ENTRY("fld_nfcp_pend_blks_thresh", 32, 16),
CREATE_ENTRY("fld_gbl_pend_blks_thresh", 48, 16)
};auto fcb_tdp_lb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_tdp_lb_cfg),
0x160,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_tdp_lb_cfg", fcb_tdp_lb_cfg_prop);
fld_map_t fcb_gbl_pend_blks_sta {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcb_gbl_pend_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_gbl_pend_blks_sta),
0x168,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_gbl_pend_blks_sta", fcb_gbl_pend_blks_sta_prop);
fld_map_t fcb_fcp_pend_blks_sta {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcb_fcp_pend_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_fcp_pend_blks_sta),
0x170,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_fcp_pend_blks_sta", fcb_fcp_pend_blks_sta_prop);
fld_map_t fcb_nfcp_pend_blks_sta {
CREATE_ENTRY("fld_pipe0_val", 0, 16),
CREATE_ENTRY("fld_pipe1_val", 16, 16),
CREATE_ENTRY("fld_pipe2_val", 32, 16),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_nfcp_pend_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_nfcp_pend_blks_sta),
0x178,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_nfcp_pend_blks_sta", fcb_nfcp_pend_blks_sta_prop);
fld_map_t fcb_tdp_pend_blks_sta {
CREATE_ENTRY("fld_pipe0_val", 0, 16),
CREATE_ENTRY("fld_pipe1_val", 16, 16),
CREATE_ENTRY("fld_pipe2_val", 32, 16),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_tdp_pend_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_tdp_pend_blks_sta),
0x180,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_tdp_pend_blks_sta", fcb_tdp_pend_blks_sta_prop);
fld_map_t fcb_pkt_sch_cfg {
CREATE_ENTRY("fld_pipe_fair_mode_enable", 0, 1),
CREATE_ENTRY("fld_fcp_strict_pri", 1, 1),
CREATE_ENTRY("fld_fcp_dwrr_wt", 2, 7),
CREATE_ENTRY("fld_nfcp_dwrr_wt", 9, 7),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcb_pkt_sch_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_pkt_sch_cfg),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_pkt_sch_cfg", fcb_pkt_sch_cfg_prop);
fld_map_t fcb_src_gbl_fcp_enq_blks_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_src_gbl_fcp_enq_blks_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_fcp_enq_blks_stats_cntr),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_fcp_enq_blks_stats_cntr", fcb_src_gbl_fcp_enq_blks_stats_cntr_prop);
fld_map_t fcb_src_gbl_fcp_req_blks_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_src_gbl_fcp_req_blks_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_fcp_req_blks_stats_cntr),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_fcp_req_blks_stats_cntr", fcb_src_gbl_fcp_req_blks_stats_cntr_prop);
fld_map_t fcb_src_gbl_nfcp_enq_blks_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_src_gbl_nfcp_enq_blks_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_nfcp_enq_blks_stats_cntr),
0x1E0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_nfcp_enq_blks_stats_cntr", fcb_src_gbl_nfcp_enq_blks_stats_cntr_prop);
fld_map_t fcb_src_fcp_xmt_bytes_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_src_fcp_xmt_bytes_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_fcp_xmt_bytes_stats_cntr),
0x1E8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_fcp_xmt_bytes_stats_cntr", fcb_src_fcp_xmt_bytes_stats_cntr_prop);
fld_map_t fcb_src_nfcp_xmt_bytes_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_src_nfcp_xmt_bytes_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_nfcp_xmt_bytes_stats_cntr),
0x1F0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_nfcp_xmt_bytes_stats_cntr", fcb_src_nfcp_xmt_bytes_stats_cntr_prop);
fld_map_t fcb_src_gbl_wu_cnt_sta {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcb_src_gbl_wu_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_wu_cnt_sta),
0x1F8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_wu_cnt_sta", fcb_src_gbl_wu_cnt_sta_prop);
fld_map_t fcb_src_gbl_fcp_enq_blks_sta {
CREATE_ENTRY("fld_val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_src_gbl_fcp_enq_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_fcp_enq_blks_sta),
0x200,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_fcp_enq_blks_sta", fcb_src_gbl_fcp_enq_blks_sta_prop);
fld_map_t fcb_src_gbl_fcp_requested_blks_sta {
CREATE_ENTRY("fld_val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_src_gbl_fcp_requested_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_fcp_requested_blks_sta),
0x208,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_fcp_requested_blks_sta", fcb_src_gbl_fcp_requested_blks_sta_prop);
fld_map_t fcb_src_gbl_fcp_pend_gntd_blks_sta {
CREATE_ENTRY("fld_val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_src_gbl_fcp_pend_gntd_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_fcp_pend_gntd_blks_sta),
0x210,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_fcp_pend_gntd_blks_sta", fcb_src_gbl_fcp_pend_gntd_blks_sta_prop);
fld_map_t fcb_src_gbl_fcp_unsol_blks_sta {
CREATE_ENTRY("fld_val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_src_gbl_fcp_unsol_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_fcp_unsol_blks_sta),
0x218,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_fcp_unsol_blks_sta", fcb_src_gbl_fcp_unsol_blks_sta_prop);
fld_map_t fcb_fcp_ncv_thresh_role_cfg {
CREATE_ENTRY("fld_gbl_enq_blks", 0, 4),
CREATE_ENTRY("fld_qos0_enq_blks", 4, 4),
CREATE_ENTRY("fld_qos1_enq_blks", 8, 4),
CREATE_ENTRY("fld_qos2_enq_blks", 12, 4),
CREATE_ENTRY("fld_qos3_enq_blks", 16, 4),
CREATE_ENTRY("fld_qos4_enq_blks", 20, 4),
CREATE_ENTRY("fld_qos5_enq_blks", 24, 4),
CREATE_ENTRY("fld_qos6_enq_blks", 28, 4),
CREATE_ENTRY("fld_qos7_enq_blks", 32, 4),
CREATE_ENTRY("__rsvd", 36, 28)
};auto fcb_fcp_ncv_thresh_role_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_fcp_ncv_thresh_role_cfg),
0x220,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_fcp_ncv_thresh_role_cfg", fcb_fcp_ncv_thresh_role_cfg_prop);
fld_map_t fcb_src_gbl_nfcp_enq_blks_sta {
CREATE_ENTRY("fld_val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_src_gbl_nfcp_enq_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_gbl_nfcp_enq_blks_sta),
0x228,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_gbl_nfcp_enq_blks_sta", fcb_src_gbl_nfcp_enq_blks_sta_prop);
fld_map_t fcb_dst_fcp_rcv_bytes_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_dst_fcp_rcv_bytes_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_fcp_rcv_bytes_stats_cntr),
0x230,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_fcp_rcv_bytes_stats_cntr", fcb_dst_fcp_rcv_bytes_stats_cntr_prop);
fld_map_t fcb_dst_nfcp_rcv_bytes_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_dst_nfcp_rcv_bytes_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_nfcp_rcv_bytes_stats_cntr),
0x238,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_nfcp_rcv_bytes_stats_cntr", fcb_dst_nfcp_rcv_bytes_stats_cntr_prop);
fld_map_t fcb_nfcp_ncv_thresh_role_cfg {
CREATE_ENTRY("fld_gbl_enq_blks", 0, 4),
CREATE_ENTRY("fld_qos0_enq_blks", 4, 4),
CREATE_ENTRY("fld_qos1_enq_blks", 8, 4),
CREATE_ENTRY("fld_qos2_enq_blks", 12, 4),
CREATE_ENTRY("fld_qos3_enq_blks", 16, 4),
CREATE_ENTRY("fld_qos4_enq_blks", 20, 4),
CREATE_ENTRY("fld_qos5_enq_blks", 24, 4),
CREATE_ENTRY("fld_qos6_enq_blks", 28, 4),
CREATE_ENTRY("fld_qos7_enq_blks", 32, 4),
CREATE_ENTRY("__rsvd", 36, 28)
};auto fcb_nfcp_ncv_thresh_role_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_nfcp_ncv_thresh_role_cfg),
0x240,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_nfcp_ncv_thresh_role_cfg", fcb_nfcp_ncv_thresh_role_cfg_prop);
fld_map_t fcb_bn_msg_if_misc_cfg {
CREATE_ENTRY("fld_up_val", 0, 4),
CREATE_ENTRY("fld_dn_val", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcb_bn_msg_if_misc_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_bn_msg_if_misc_cfg),
0x250,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_bn_msg_if_misc_cfg", fcb_bn_msg_if_misc_cfg_prop);
fld_map_t fcb_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_gnt_datarate_pacer_cfg),
0x260,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_gnt_datarate_pacer_cfg", fcb_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_gnt_ctlmsg_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_msg_tx_adj_enable", 1, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 2, 12),
CREATE_ENTRY("fld_base_leak_rate", 14, 12),
CREATE_ENTRY("fld_admit_lvl_thresh", 26, 24),
CREATE_ENTRY("fld_update_val", 50, 12),
CREATE_ENTRY("__rsvd", 62, 2)
};auto fcb_gnt_ctlmsg_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_gnt_ctlmsg_pacer_cfg),
0x268,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_gnt_ctlmsg_pacer_cfg", fcb_gnt_ctlmsg_pacer_cfg_prop);
fld_map_t fcb_host_intf0_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf0_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf0_gnt_datarate_pacer_cfg),
0x270,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf0_gnt_datarate_pacer_cfg", fcb_host_intf0_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf1_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf1_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf1_gnt_datarate_pacer_cfg),
0x278,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf1_gnt_datarate_pacer_cfg", fcb_host_intf1_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf2_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf2_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf2_gnt_datarate_pacer_cfg),
0x280,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf2_gnt_datarate_pacer_cfg", fcb_host_intf2_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf3_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf3_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf3_gnt_datarate_pacer_cfg),
0x288,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf3_gnt_datarate_pacer_cfg", fcb_host_intf3_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf4_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf4_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf4_gnt_datarate_pacer_cfg),
0x290,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf4_gnt_datarate_pacer_cfg", fcb_host_intf4_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf5_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf5_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf5_gnt_datarate_pacer_cfg),
0x298,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf5_gnt_datarate_pacer_cfg", fcb_host_intf5_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf6_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf6_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf6_gnt_datarate_pacer_cfg),
0x2A0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf6_gnt_datarate_pacer_cfg", fcb_host_intf6_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_host_intf7_gnt_datarate_pacer_cfg {
CREATE_ENTRY("fld_enable", 0, 1),
CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
CREATE_ENTRY("fld_base_leak_rate", 9, 16),
CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
CREATE_ENTRY("fld_min_thresh", 40, 15),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fcb_host_intf7_gnt_datarate_pacer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_host_intf7_gnt_datarate_pacer_cfg),
0x2A8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_host_intf7_gnt_datarate_pacer_cfg", fcb_host_intf7_gnt_datarate_pacer_cfg_prop);
fld_map_t fcb_dst_gbl_pbof_blks_thresh_cfg {
CREATE_ENTRY("fld_xon_thresh", 0, 16),
CREATE_ENTRY("fld_xoff_thresh", 16, 16),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_dst_gbl_pbof_blks_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_gbl_pbof_blks_thresh_cfg),
0x2C8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_gbl_pbof_blks_thresh_cfg", fcb_dst_gbl_pbof_blks_thresh_cfg_prop);
fld_map_t fcb_dst_gbl_req_blks_sta {
CREATE_ENTRY("fld_val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcb_dst_gbl_req_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_gbl_req_blks_sta),
0x2D0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_gbl_req_blks_sta", fcb_dst_gbl_req_blks_sta_prop);
fld_map_t fcb_dst_gbl_pbof_blks_sta {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcb_dst_gbl_pbof_blks_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_gbl_pbof_blks_sta),
0x2D8,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_gbl_pbof_blks_sta", fcb_dst_gbl_pbof_blks_sta_prop);
fld_map_t fcb_dst_gbl_fcp_gntd_blks_stats_cntr {
CREATE_ENTRY("fld_val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcb_dst_gbl_fcp_gntd_blks_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_gbl_fcp_gntd_blks_stats_cntr),
0x2E0,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_gbl_fcp_gntd_blks_stats_cntr", fcb_dst_gbl_fcp_gntd_blks_stats_cntr_prop);
fld_map_t fcb_gph_cache_sta {
CREATE_ENTRY("fld_free_cnt", 0, 8),
CREATE_ENTRY("fld_unlocked_cnt", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcb_gph_cache_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_gph_cache_sta),
0x350,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_gph_cache_sta", fcb_gph_cache_sta_prop);
fld_map_t fcb_src_trace_fifo_cfg {
CREATE_ENTRY("fld_trace_enable", 0, 1),
CREATE_ENTRY("fld_opcode_map", 1, 32),
CREATE_ENTRY("fld_wu_qid", 33, 14),
CREATE_ENTRY("__rsvd", 47, 17)
};auto fcb_src_trace_fifo_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_trace_fifo_cfg),
0x358,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_trace_fifo_cfg", fcb_src_trace_fifo_cfg_prop);
fld_map_t fcb_src_trace_fifo_cnt_sta {
CREATE_ENTRY("fld_cnt", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcb_src_trace_fifo_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_src_trace_fifo_cnt_sta),
0x360,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_src_trace_fifo_cnt_sta", fcb_src_trace_fifo_cnt_sta_prop);
fld_map_t fcb_dst_trace_fifo_cfg {
CREATE_ENTRY("fld_trace_enable", 0, 1),
CREATE_ENTRY("fld_opcode_map", 1, 16),
CREATE_ENTRY("fld_wu_qid", 17, 14),
CREATE_ENTRY("__rsvd", 31, 33)
};auto fcb_dst_trace_fifo_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_trace_fifo_cfg),
0x380,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_trace_fifo_cfg", fcb_dst_trace_fifo_cfg_prop);
fld_map_t fcb_dst_trace_fifo_cnt_sta {
CREATE_ENTRY("fld_cnt", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcb_dst_trace_fifo_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fcb_dst_trace_fifo_cnt_sta),
0x388,
CSR_TYPE::REG,
1);
add_csr(fcb_0, "fcb_dst_trace_fifo_cnt_sta", fcb_dst_trace_fifo_cnt_sta_prop);
 // END fcb 
}
{
 // BEGIN nwqm 
auto nwqm_0 = nu_rng[0].add_an({"nwqm"}, 0x8000000, 1, 0x0);
fld_map_t nwqm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nwqm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_timeout_thresh_cfg", nwqm_timeout_thresh_cfg_prop);
fld_map_t nwqm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nwqm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_timedout_sta", nwqm_timedout_sta_prop);
fld_map_t nwqm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nwqm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_timeout_clr", nwqm_timeout_clr_prop);
fld_map_t nwqm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto nwqm_features_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_features", nwqm_features_prop);
fld_map_t nwqm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto nwqm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_spare_pio", nwqm_spare_pio_prop);
fld_map_t nwqm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto nwqm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_scratchpad", nwqm_scratchpad_prop);
fld_map_t nwqm_cfg {
CREATE_ENTRY("fae_qid", 0, 14),
CREATE_ENTRY("nq_drop_wu_crd_inc_ena", 14, 1),
CREATE_ENTRY("pbuf_max_qid", 15, 15),
CREATE_ENTRY("__rsvd", 30, 34)
};auto nwqm_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_cfg", nwqm_cfg_prop);
fld_map_t nwqm_pc_to_if_cfg {
CREATE_ENTRY("pc7", 0, 2),
CREATE_ENTRY("pc6", 2, 2),
CREATE_ENTRY("pc5", 4, 2),
CREATE_ENTRY("pc4", 6, 2),
CREATE_ENTRY("pc3", 8, 2),
CREATE_ENTRY("pc2", 10, 2),
CREATE_ENTRY("pc1", 12, 2),
CREATE_ENTRY("pc0", 14, 2),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_pc_to_if_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_pc_to_if_cfg),
0x88,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_pc_to_if_cfg", nwqm_pc_to_if_cfg_prop);
fld_map_t nwqm_sram_init_done {
CREATE_ENTRY("wu_index_pf", 0, 1),
CREATE_ENTRY("states", 1, 1),
CREATE_ENTRY("all", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto nwqm_sram_init_done_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_sram_init_done),
0x98,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_sram_init_done", nwqm_sram_init_done_prop);
fld_map_t nwqm_wu_crd_cfg {
CREATE_ENTRY("alloc_dry_th", 0, 16),
CREATE_ENTRY("efp_hi_th", 16, 16),
CREATE_ENTRY("efp_lo_th", 32, 16),
CREATE_ENTRY("efp_send_th", 48, 16)
};auto nwqm_wu_crd_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cfg),
0xA0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cfg", nwqm_wu_crd_cfg_prop);
fld_map_t nwqm_wu_index_cfg {
CREATE_ENTRY("drain_bitalloc", 0, 8),
CREATE_ENTRY("wm_ena", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_index_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_index_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_index_cfg", nwqm_wu_index_cfg_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_1 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_1_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_1),
0xB0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_1", nwqm_wu_crd_cnt_ncv_th_1_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_2 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_2_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_2),
0xB8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_2", nwqm_wu_crd_cnt_ncv_th_2_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_3 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_3_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_3),
0xC0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_3", nwqm_wu_crd_cnt_ncv_th_3_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_4 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_4_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_4),
0xC8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_4", nwqm_wu_crd_cnt_ncv_th_4_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_5 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_5_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_5),
0xD0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_5", nwqm_wu_crd_cnt_ncv_th_5_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_6 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_6_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_6),
0xD8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_6", nwqm_wu_crd_cnt_ncv_th_6_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_7 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_7_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_7),
0xE0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_7", nwqm_wu_crd_cnt_ncv_th_7_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_8 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_8_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_8),
0xE8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_8", nwqm_wu_crd_cnt_ncv_th_8_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_9 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_9_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_9),
0xF0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_9", nwqm_wu_crd_cnt_ncv_th_9_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_10 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_10_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_10),
0xF8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_10", nwqm_wu_crd_cnt_ncv_th_10_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_11 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_11_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_11),
0x100,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_11", nwqm_wu_crd_cnt_ncv_th_11_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_12 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_12_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_12),
0x108,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_12", nwqm_wu_crd_cnt_ncv_th_12_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_13 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_13_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_13),
0x110,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_13", nwqm_wu_crd_cnt_ncv_th_13_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_14 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_14_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_14),
0x118,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_14", nwqm_wu_crd_cnt_ncv_th_14_prop);
fld_map_t nwqm_wu_crd_cnt_ncv_th_15 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nwqm_wu_crd_cnt_ncv_th_15_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th_15),
0x120,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th_15", nwqm_wu_crd_cnt_ncv_th_15_prop);
fld_map_t nwqm_wu_crd_index_pf_misc_cfg {
CREATE_ENTRY("dgid", 0, 5),
CREATE_ENTRY("dlid", 5, 5),
CREATE_ENTRY("crd_alloc_if", 10, 2),
CREATE_ENTRY("crd_dealloc_if", 12, 2),
CREATE_ENTRY("index_alloc_if", 14, 2),
CREATE_ENTRY("index_dealloc_if", 16, 2),
CREATE_ENTRY("__rsvd", 18, 46)
};auto nwqm_wu_crd_index_pf_misc_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_index_pf_misc_cfg),
0x190,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_index_pf_misc_cfg", nwqm_wu_crd_index_pf_misc_cfg_prop);
fld_map_t nwqm_wu_crd_pf_cfg {
CREATE_ENTRY("dealloc_th", 0, 10),
CREATE_ENTRY("avg_th", 10, 10),
CREATE_ENTRY("alloc_th", 20, 10),
CREATE_ENTRY("max_alloc_cnt", 30, 10),
CREATE_ENTRY("dry_wait_timer", 40, 10),
CREATE_ENTRY("__rsvd", 50, 14)
};auto nwqm_wu_crd_pf_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_crd_pf_cfg),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_crd_pf_cfg", nwqm_wu_crd_pf_cfg_prop);
fld_map_t nwqm_wu_index_pf_cfg {
CREATE_ENTRY("max_num_alloc_req", 0, 2),
CREATE_ENTRY("dry_wait_timer", 2, 10),
CREATE_ENTRY("dealloc_th", 12, 11),
CREATE_ENTRY("avg_th", 23, 11),
CREATE_ENTRY("alloc_th", 34, 11),
CREATE_ENTRY("max_th", 45, 7),
CREATE_ENTRY("__rsvd", 52, 12)
};auto nwqm_wu_index_pf_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_wu_index_pf_cfg),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_wu_index_pf_cfg", nwqm_wu_index_pf_cfg_prop);
fld_map_t nwqm_fla_cfg {
CREATE_ENTRY("fla_module_id", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nwqm_fla_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nwqm_fla_cfg),
0x390,
CSR_TYPE::REG,
1);
add_csr(nwqm_0, "nwqm_fla_cfg", nwqm_fla_cfg_prop);
 // END nwqm 
}
{
 // BEGIN psw_pwr 
auto psw_pwr_0 = nu_rng[0].add_an({"psw_pwr"}, 0x9000000, 1, 0x0);
fld_map_t psw_pwr_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_pwr_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_timeout_thresh_cfg", psw_pwr_timeout_thresh_cfg_prop);
fld_map_t psw_pwr_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_timedout_sta", psw_pwr_timedout_sta_prop);
fld_map_t psw_pwr_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_timeout_clr", psw_pwr_timeout_clr_prop);
fld_map_t psw_pwr_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_pwr_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_features),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_features", psw_pwr_features_prop);
fld_map_t psw_pwr_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_pwr_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_spare_pio),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_spare_pio", psw_pwr_spare_pio_prop);
fld_map_t psw_pwr_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_pwr_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_scratchpad),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_scratchpad", psw_pwr_scratchpad_prop);
fld_map_t psw_non_fatal_interrupt_status {
CREATE_ENTRY("pwr_intr", 0, 1),
CREATE_ENTRY("prd_intr", 1, 1),
CREATE_ENTRY("sch_intr", 2, 1),
CREATE_ENTRY("prm_intr", 3, 1),
CREATE_ENTRY("orm_intr", 4, 1),
CREATE_ENTRY("irm_intr", 5, 1),
CREATE_ENTRY("wred_intr", 6, 1),
CREATE_ENTRY("clm_intr", 7, 1),
CREATE_ENTRY("pqm_intr", 8, 1),
CREATE_ENTRY("cfp_intr", 9, 1),
CREATE_ENTRY("__rsvd", 10, 54)
};auto psw_non_fatal_interrupt_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_non_fatal_interrupt_status),
0xD0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_non_fatal_interrupt_status", psw_non_fatal_interrupt_status_prop);
fld_map_t psw_fatal_interrupt_status {
CREATE_ENTRY("pwr_intr", 0, 1),
CREATE_ENTRY("prd_intr", 1, 1),
CREATE_ENTRY("sch_intr", 2, 1),
CREATE_ENTRY("prm_intr", 3, 1),
CREATE_ENTRY("orm_intr", 4, 1),
CREATE_ENTRY("irm_intr", 5, 1),
CREATE_ENTRY("wred_intr", 6, 1),
CREATE_ENTRY("clm_intr", 7, 1),
CREATE_ENTRY("pqm_intr", 8, 1),
CREATE_ENTRY("cfp_intr", 9, 1),
CREATE_ENTRY("__rsvd", 10, 54)
};auto psw_fatal_interrupt_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_fatal_interrupt_status),
0xD8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_fatal_interrupt_status", psw_fatal_interrupt_status_prop);
fld_map_t psw_pwr_cfg_min_pkt_size {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_min_pkt_size_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_min_pkt_size),
0xE0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_min_pkt_size", psw_pwr_cfg_min_pkt_size_prop);
fld_map_t psw_pwr_cfg_min_pkt_size_after_rewrite {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_min_pkt_size_after_rewrite_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_min_pkt_size_after_rewrite),
0xE8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_min_pkt_size_after_rewrite", psw_pwr_cfg_min_pkt_size_after_rewrite_prop);
fld_map_t psw_pwr_sta_unexpected_frv_rcvd_error {
CREATE_ENTRY("streams_fpg0", 0, 4),
CREATE_ENTRY("streams_fpg1", 4, 4),
CREATE_ENTRY("streams_fpg2", 8, 4),
CREATE_ENTRY("streams_fpg3", 12, 4),
CREATE_ENTRY("streams_fpg4", 16, 4),
CREATE_ENTRY("streams_fpg5", 20, 4),
CREATE_ENTRY("epg0", 24, 1),
CREATE_ENTRY("epg1", 25, 1),
CREATE_ENTRY("epg2", 26, 1),
CREATE_ENTRY("__rsvd", 27, 37)
};auto psw_pwr_sta_unexpected_frv_rcvd_error_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sta_unexpected_frv_rcvd_error),
0xF0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sta_unexpected_frv_rcvd_error", psw_pwr_sta_unexpected_frv_rcvd_error_prop);
fld_map_t psw_pwr_mem_init_start_cfg {
CREATE_ENTRY("q_drop_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("src_pri_enq_cntr", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_mem_init_start_cfg),
0xF8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_mem_init_start_cfg", psw_pwr_mem_init_start_cfg_prop);
fld_map_t psw_pwr_mem_init_done_status {
CREATE_ENTRY("q_drop_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("src_pri_enq_cntr", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_mem_init_done_status),
0x100,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_mem_init_done_status", psw_pwr_mem_init_done_status_prop);
fld_map_t psw_pwr_fla_slave_id {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_fla_slave_id_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fla_slave_id),
0x108,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_fla_slave_id", psw_pwr_fla_slave_id_prop);
fld_map_t psw_pwr_cfg_stream_mem_sel_ifpg {
CREATE_ENTRY("section0", 0, 2),
CREATE_ENTRY("section1", 2, 2),
CREATE_ENTRY("section2", 4, 2),
CREATE_ENTRY("section3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_stream_mem_sel_ifpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_stream_mem_sel_ifpg),
0x110,
CSR_TYPE::REG_LST,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_stream_mem_sel_ifpg", psw_pwr_cfg_stream_mem_sel_ifpg_prop);
fld_map_t psw_pwr_cfg_flex_clear_ifpg {
CREATE_ENTRY("stream0", 0, 1),
CREATE_ENTRY("stream1", 1, 1),
CREATE_ENTRY("stream2", 2, 1),
CREATE_ENTRY("stream3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_flex_clear_ifpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_flex_clear_ifpg),
0x140,
CSR_TYPE::REG_LST,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_flex_clear_ifpg", psw_pwr_cfg_flex_clear_ifpg_prop);
fld_map_t psw_pwr_cfg_back_pressure_ifpg {
CREATE_ENTRY("depth_stream0", 0, 8),
CREATE_ENTRY("depth_stream1", 8, 8),
CREATE_ENTRY("depth_stream2", 16, 8),
CREATE_ENTRY("depth_stream3", 24, 8),
CREATE_ENTRY("bkpr_thresh_stream0", 32, 8),
CREATE_ENTRY("bkpr_thresh_stream1", 40, 8),
CREATE_ENTRY("bkpr_thresh_stream2", 48, 8),
CREATE_ENTRY("bkpr_thresh_stream3", 56, 8)
};auto psw_pwr_cfg_back_pressure_ifpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_back_pressure_ifpg),
0x170,
CSR_TYPE::REG_LST,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_back_pressure_ifpg", psw_pwr_cfg_back_pressure_ifpg_prop);
fld_map_t psw_pwr_cfg_repl_fifo_th {
CREATE_ENTRY("headroom", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto psw_pwr_cfg_repl_fifo_th_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_repl_fifo_th),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_repl_fifo_th", psw_pwr_cfg_repl_fifo_th_prop);
fld_map_t psw_pwr_cfg_cfp_hysteresis {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("thresh", 1, 14),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pwr_cfg_cfp_hysteresis_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_cfp_hysteresis),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_cfp_hysteresis", psw_pwr_cfg_cfp_hysteresis_prop);
fld_map_t psw_pwr_cfg_egress_mirror_ecn {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_egress_mirror_ecn_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_egress_mirror_ecn),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_egress_mirror_ecn", psw_pwr_cfg_egress_mirror_ecn_prop);
fld_map_t psw_pwr_cfg_q_drop_stats {
CREATE_ENTRY("psw_drop", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_q_drop_stats_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_q_drop_stats),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_q_drop_stats", psw_pwr_cfg_q_drop_stats_prop);
fld_map_t psw_pwr_cfg_spd {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("sofs", 1, 1),
CREATE_ENTRY("scopy_pkt_sz_adj", 2, 7),
CREATE_ENTRY("dest_stream", 9, 6),
CREATE_ENTRY("dest_q", 15, 4),
CREATE_ENTRY("__rsvd", 19, 45)
};auto psw_pwr_cfg_spd_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_spd),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_spd", psw_pwr_cfg_spd_prop);
fld_map_t psw_pwr_cfg_egress_sample_info {
CREATE_ENTRY("send_to_fpg_en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_egress_sample_info_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_egress_sample_info),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_egress_sample_info", psw_pwr_cfg_egress_sample_info_prop);
fld_map_t psw_pwr_cfg_stream_dis {
CREATE_ENTRY("fp_stream_dis", 0, 24),
CREATE_ENTRY("epg_dis", 24, 3),
CREATE_ENTRY("__rsvd", 27, 37)
};auto psw_pwr_cfg_stream_dis_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_stream_dis),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_stream_dis", psw_pwr_cfg_stream_dis_prop);
fld_map_t psw_pwr_cfg_clear_hwm {
CREATE_ENTRY("repl_fifo", 0, 1),
CREATE_ENTRY("fpg0", 1, 1),
CREATE_ENTRY("fpg1", 2, 1),
CREATE_ENTRY("fpg2", 3, 1),
CREATE_ENTRY("fpg3", 4, 1),
CREATE_ENTRY("fpg4", 5, 1),
CREATE_ENTRY("fpg5", 6, 1),
CREATE_ENTRY("epg0", 7, 1),
CREATE_ENTRY("epg1", 8, 1),
CREATE_ENTRY("epg2", 9, 1),
CREATE_ENTRY("__rsvd", 10, 54)
};auto psw_pwr_cfg_clear_hwm_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_clear_hwm),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_clear_hwm", psw_pwr_cfg_clear_hwm_prop);
fld_map_t psw_pwr_fpg_stream_mem_cnt {
CREATE_ENTRY("curr_val_stream0", 0, 8),
CREATE_ENTRY("hwm_val_stream0", 8, 8),
CREATE_ENTRY("curr_val_stream1", 16, 8),
CREATE_ENTRY("hwm_val_stream1", 24, 8),
CREATE_ENTRY("curr_val_stream2", 32, 8),
CREATE_ENTRY("hwm_val_stream2", 40, 8),
CREATE_ENTRY("curr_val_stream3", 48, 8),
CREATE_ENTRY("hwm_val_stream3", 56, 8)
};auto psw_pwr_fpg_stream_mem_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fpg_stream_mem_cnt),
0x1E0,
CSR_TYPE::REG_LST,
1);
add_csr(psw_pwr_0, "psw_pwr_fpg_stream_mem_cnt", psw_pwr_fpg_stream_mem_cnt_prop);
fld_map_t psw_pwr_epg_stream_mem_cnt {
CREATE_ENTRY("curr_val", 0, 8),
CREATE_ENTRY("hwm_val", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_epg_stream_mem_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_epg_stream_mem_cnt),
0x210,
CSR_TYPE::REG_LST,
1);
add_csr(psw_pwr_0, "psw_pwr_epg_stream_mem_cnt", psw_pwr_epg_stream_mem_cnt_prop);
fld_map_t psw_pwr_repl_fifo_cnt {
CREATE_ENTRY("curr_val", 0, 8),
CREATE_ENTRY("hwm_val", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_repl_fifo_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_repl_fifo_cnt),
0x228,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_repl_fifo_cnt", psw_pwr_repl_fifo_cnt_prop);
fld_map_t psw_pwr_cpr_cnt {
CREATE_ENTRY("cfp_prefetch_fifo", 0, 4),
CREATE_ENTRY("drop_cell_fifo", 4, 5),
CREATE_ENTRY("__rsvd", 9, 55)
};auto psw_pwr_cpr_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cpr_cnt),
0x230,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cpr_cnt", psw_pwr_cpr_cnt_prop);
fld_map_t psw_pwr_sram_err_inj_cfg {
CREATE_ENTRY("src_pri_enq_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("q_drop_cntr", 2, 1),
CREATE_ENTRY("repl_fifo", 3, 1),
CREATE_ENTRY("epg2_pkt_ctrl", 4, 1),
CREATE_ENTRY("epg2_stream_ctrl", 5, 1),
CREATE_ENTRY("epg2_stream_bank1", 6, 1),
CREATE_ENTRY("epg2_stream_bank0", 7, 1),
CREATE_ENTRY("epg1_pkt_ctrl", 8, 1),
CREATE_ENTRY("epg1_stream_ctrl", 9, 1),
CREATE_ENTRY("epg1_stream_bank1", 10, 1),
CREATE_ENTRY("epg1_stream_bank0", 11, 1),
CREATE_ENTRY("epg0_pkt_ctrl", 12, 1),
CREATE_ENTRY("epg0_stream_ctrl", 13, 1),
CREATE_ENTRY("epg0_stream_bank1", 14, 1),
CREATE_ENTRY("epg0_stream_bank0", 15, 1),
CREATE_ENTRY("fpg5_pkt_ctrl", 16, 1),
CREATE_ENTRY("fpg5_stream_ctrl", 17, 1),
CREATE_ENTRY("fpg5_stream_bank3", 18, 1),
CREATE_ENTRY("fpg5_stream_bank2", 19, 1),
CREATE_ENTRY("fpg5_stream_bank1", 20, 1),
CREATE_ENTRY("fpg5_stream_bank0", 21, 1),
CREATE_ENTRY("fpg4_pkt_ctrl", 22, 1),
CREATE_ENTRY("fpg4_stream_ctrl", 23, 1),
CREATE_ENTRY("fpg4_stream_bank3", 24, 1),
CREATE_ENTRY("fpg4_stream_bank2", 25, 1),
CREATE_ENTRY("fpg4_stream_bank1", 26, 1),
CREATE_ENTRY("fpg4_stream_bank0", 27, 1),
CREATE_ENTRY("fpg3_pkt_ctrl", 28, 1),
CREATE_ENTRY("fpg3_stream_ctrl", 29, 1),
CREATE_ENTRY("fpg3_stream_bank3", 30, 1),
CREATE_ENTRY("fpg3_stream_bank2", 31, 1),
CREATE_ENTRY("fpg3_stream_bank1", 32, 1),
CREATE_ENTRY("fpg3_stream_bank0", 33, 1),
CREATE_ENTRY("fpg2_pkt_ctrl", 34, 1),
CREATE_ENTRY("fpg2_stream_ctrl", 35, 1),
CREATE_ENTRY("fpg2_stream_bank3", 36, 1),
CREATE_ENTRY("fpg2_stream_bank2", 37, 1),
CREATE_ENTRY("fpg2_stream_bank1", 38, 1),
CREATE_ENTRY("fpg2_stream_bank0", 39, 1),
CREATE_ENTRY("fpg1_pkt_ctrl", 40, 1),
CREATE_ENTRY("fpg1_stream_ctrl", 41, 1),
CREATE_ENTRY("fpg1_stream_bank3", 42, 1),
CREATE_ENTRY("fpg1_stream_bank2", 43, 1),
CREATE_ENTRY("fpg1_stream_bank1", 44, 1),
CREATE_ENTRY("fpg1_stream_bank0", 45, 1),
CREATE_ENTRY("fpg0_pkt_ctrl", 46, 1),
CREATE_ENTRY("fpg0_stream_ctrl", 47, 1),
CREATE_ENTRY("fpg0_stream_bank3", 48, 1),
CREATE_ENTRY("fpg0_stream_bank2", 49, 1),
CREATE_ENTRY("fpg0_stream_bank1", 50, 1),
CREATE_ENTRY("fpg0_stream_bank0", 51, 1),
CREATE_ENTRY("err_type", 52, 1),
CREATE_ENTRY("__rsvd", 53, 11)
};auto psw_pwr_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_err_inj_cfg),
0x238,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_err_inj_cfg", psw_pwr_sram_err_inj_cfg_prop);
fld_map_t psw_pwr_sram_log_cerr_vec {
CREATE_ENTRY("src_pri_enq_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("q_drop_cntr", 2, 1),
CREATE_ENTRY("repl_fifo", 3, 1),
CREATE_ENTRY("epg2_pkt_ctrl", 4, 1),
CREATE_ENTRY("epg2_stream_ctrl", 5, 1),
CREATE_ENTRY("epg2_stream_bank1", 6, 1),
CREATE_ENTRY("epg2_stream_bank0", 7, 1),
CREATE_ENTRY("epg1_pkt_ctrl", 8, 1),
CREATE_ENTRY("epg1_stream_ctrl", 9, 1),
CREATE_ENTRY("epg1_stream_bank1", 10, 1),
CREATE_ENTRY("epg1_stream_bank0", 11, 1),
CREATE_ENTRY("epg0_pkt_ctrl", 12, 1),
CREATE_ENTRY("epg0_stream_ctrl", 13, 1),
CREATE_ENTRY("epg0_stream_bank1", 14, 1),
CREATE_ENTRY("epg0_stream_bank0", 15, 1),
CREATE_ENTRY("fpg5_pkt_ctrl", 16, 1),
CREATE_ENTRY("fpg5_stream_ctrl", 17, 1),
CREATE_ENTRY("fpg5_stream_bank3", 18, 1),
CREATE_ENTRY("fpg5_stream_bank2", 19, 1),
CREATE_ENTRY("fpg5_stream_bank1", 20, 1),
CREATE_ENTRY("fpg5_stream_bank0", 21, 1),
CREATE_ENTRY("fpg4_pkt_ctrl", 22, 1),
CREATE_ENTRY("fpg4_stream_ctrl", 23, 1),
CREATE_ENTRY("fpg4_stream_bank3", 24, 1),
CREATE_ENTRY("fpg4_stream_bank2", 25, 1),
CREATE_ENTRY("fpg4_stream_bank1", 26, 1),
CREATE_ENTRY("fpg4_stream_bank0", 27, 1),
CREATE_ENTRY("fpg3_pkt_ctrl", 28, 1),
CREATE_ENTRY("fpg3_stream_ctrl", 29, 1),
CREATE_ENTRY("fpg3_stream_bank3", 30, 1),
CREATE_ENTRY("fpg3_stream_bank2", 31, 1),
CREATE_ENTRY("fpg3_stream_bank1", 32, 1),
CREATE_ENTRY("fpg3_stream_bank0", 33, 1),
CREATE_ENTRY("fpg2_pkt_ctrl", 34, 1),
CREATE_ENTRY("fpg2_stream_ctrl", 35, 1),
CREATE_ENTRY("fpg2_stream_bank3", 36, 1),
CREATE_ENTRY("fpg2_stream_bank2", 37, 1),
CREATE_ENTRY("fpg2_stream_bank1", 38, 1),
CREATE_ENTRY("fpg2_stream_bank0", 39, 1),
CREATE_ENTRY("fpg1_pkt_ctrl", 40, 1),
CREATE_ENTRY("fpg1_stream_ctrl", 41, 1),
CREATE_ENTRY("fpg1_stream_bank3", 42, 1),
CREATE_ENTRY("fpg1_stream_bank2", 43, 1),
CREATE_ENTRY("fpg1_stream_bank1", 44, 1),
CREATE_ENTRY("fpg1_stream_bank0", 45, 1),
CREATE_ENTRY("fpg0_pkt_ctrl", 46, 1),
CREATE_ENTRY("fpg0_stream_ctrl", 47, 1),
CREATE_ENTRY("fpg0_stream_bank3", 48, 1),
CREATE_ENTRY("fpg0_stream_bank2", 49, 1),
CREATE_ENTRY("fpg0_stream_bank1", 50, 1),
CREATE_ENTRY("fpg0_stream_bank0", 51, 1),
CREATE_ENTRY("__rsvd", 52, 12)
};auto psw_pwr_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_cerr_vec),
0x240,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_log_cerr_vec", psw_pwr_sram_log_cerr_vec_prop);
fld_map_t psw_pwr_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_cerr_syndrome),
0x248,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_log_cerr_syndrome", psw_pwr_sram_log_cerr_syndrome_prop);
fld_map_t psw_pwr_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_cerr_addr),
0x250,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_log_cerr_addr", psw_pwr_sram_log_cerr_addr_prop);
fld_map_t psw_pwr_sram_log_uerr_vec {
CREATE_ENTRY("src_pri_enq_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("q_drop_cntr", 2, 1),
CREATE_ENTRY("repl_fifo", 3, 1),
CREATE_ENTRY("epg2_pkt_ctrl", 4, 1),
CREATE_ENTRY("epg2_stream_ctrl", 5, 1),
CREATE_ENTRY("epg2_stream_bank1", 6, 1),
CREATE_ENTRY("epg2_stream_bank0", 7, 1),
CREATE_ENTRY("epg1_pkt_ctrl", 8, 1),
CREATE_ENTRY("epg1_stream_ctrl", 9, 1),
CREATE_ENTRY("epg1_stream_bank1", 10, 1),
CREATE_ENTRY("epg1_stream_bank0", 11, 1),
CREATE_ENTRY("epg0_pkt_ctrl", 12, 1),
CREATE_ENTRY("epg0_stream_ctrl", 13, 1),
CREATE_ENTRY("epg0_stream_bank1", 14, 1),
CREATE_ENTRY("epg0_stream_bank0", 15, 1),
CREATE_ENTRY("fpg5_pkt_ctrl", 16, 1),
CREATE_ENTRY("fpg5_stream_ctrl", 17, 1),
CREATE_ENTRY("fpg5_stream_bank3", 18, 1),
CREATE_ENTRY("fpg5_stream_bank2", 19, 1),
CREATE_ENTRY("fpg5_stream_bank1", 20, 1),
CREATE_ENTRY("fpg5_stream_bank0", 21, 1),
CREATE_ENTRY("fpg4_pkt_ctrl", 22, 1),
CREATE_ENTRY("fpg4_stream_ctrl", 23, 1),
CREATE_ENTRY("fpg4_stream_bank3", 24, 1),
CREATE_ENTRY("fpg4_stream_bank2", 25, 1),
CREATE_ENTRY("fpg4_stream_bank1", 26, 1),
CREATE_ENTRY("fpg4_stream_bank0", 27, 1),
CREATE_ENTRY("fpg3_pkt_ctrl", 28, 1),
CREATE_ENTRY("fpg3_stream_ctrl", 29, 1),
CREATE_ENTRY("fpg3_stream_bank3", 30, 1),
CREATE_ENTRY("fpg3_stream_bank2", 31, 1),
CREATE_ENTRY("fpg3_stream_bank1", 32, 1),
CREATE_ENTRY("fpg3_stream_bank0", 33, 1),
CREATE_ENTRY("fpg2_pkt_ctrl", 34, 1),
CREATE_ENTRY("fpg2_stream_ctrl", 35, 1),
CREATE_ENTRY("fpg2_stream_bank3", 36, 1),
CREATE_ENTRY("fpg2_stream_bank2", 37, 1),
CREATE_ENTRY("fpg2_stream_bank1", 38, 1),
CREATE_ENTRY("fpg2_stream_bank0", 39, 1),
CREATE_ENTRY("fpg1_pkt_ctrl", 40, 1),
CREATE_ENTRY("fpg1_stream_ctrl", 41, 1),
CREATE_ENTRY("fpg1_stream_bank3", 42, 1),
CREATE_ENTRY("fpg1_stream_bank2", 43, 1),
CREATE_ENTRY("fpg1_stream_bank1", 44, 1),
CREATE_ENTRY("fpg1_stream_bank0", 45, 1),
CREATE_ENTRY("fpg0_pkt_ctrl", 46, 1),
CREATE_ENTRY("fpg0_stream_ctrl", 47, 1),
CREATE_ENTRY("fpg0_stream_bank3", 48, 1),
CREATE_ENTRY("fpg0_stream_bank2", 49, 1),
CREATE_ENTRY("fpg0_stream_bank1", 50, 1),
CREATE_ENTRY("fpg0_stream_bank0", 51, 1),
CREATE_ENTRY("__rsvd", 52, 12)
};auto psw_pwr_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_uerr_vec),
0x258,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_log_uerr_vec", psw_pwr_sram_log_uerr_vec_prop);
fld_map_t psw_pwr_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_uerr_syndrome),
0x260,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_log_uerr_syndrome", psw_pwr_sram_log_uerr_syndrome_prop);
fld_map_t psw_pwr_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_uerr_addr),
0x268,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_sram_log_uerr_addr", psw_pwr_sram_log_uerr_addr_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_cln {
CREATE_ENTRY("vld", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_pbuf_arb_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_cln),
0x270,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_cln", psw_pwr_cfg_pbuf_arb_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg0_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg0_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg0_streams_en),
0x278,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg0_streams_en", psw_pwr_cfg_pbuf_arb_fpg0_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg1_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg1_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg1_streams_en),
0x280,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg1_streams_en", psw_pwr_cfg_pbuf_arb_fpg1_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg2_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg2_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg2_streams_en),
0x288,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg2_streams_en", psw_pwr_cfg_pbuf_arb_fpg2_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg3_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg3_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg3_streams_en),
0x290,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg3_streams_en", psw_pwr_cfg_pbuf_arb_fpg3_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg4_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg4_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg4_streams_en),
0x298,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg4_streams_en", psw_pwr_cfg_pbuf_arb_fpg4_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg5_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg5_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg5_streams_en),
0x2A0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg5_streams_en", psw_pwr_cfg_pbuf_arb_fpg5_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg0_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg0_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg0_cln),
0x2A8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg0_cln", psw_pwr_cfg_pbuf_arb_fpg0_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg1_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg1_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg1_cln),
0x2B0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg1_cln", psw_pwr_cfg_pbuf_arb_fpg1_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg2_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg2_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg2_cln),
0x2B8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg2_cln", psw_pwr_cfg_pbuf_arb_fpg2_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg3_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg3_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg3_cln),
0x2C0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg3_cln", psw_pwr_cfg_pbuf_arb_fpg3_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg4_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg4_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg4_cln),
0x2C8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg4_cln", psw_pwr_cfg_pbuf_arb_fpg4_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg5_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg5_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg5_cln),
0x2D0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg5_cln", psw_pwr_cfg_pbuf_arb_fpg5_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_wrr_weights {
CREATE_ENTRY("epg0", 0, 4),
CREATE_ENTRY("epg1", 4, 4),
CREATE_ENTRY("epg2", 8, 4),
CREATE_ENTRY("spl_port", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_cfg_pbuf_arb_wrr_weights_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_wrr_weights),
0x2D8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_wrr_weights", psw_pwr_cfg_pbuf_arb_wrr_weights_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_min_spacing {
CREATE_ENTRY("epg", 0, 5),
CREATE_ENTRY("spl_port", 5, 5),
CREATE_ENTRY("null_slot", 10, 16),
CREATE_ENTRY("__rsvd", 26, 38)
};auto psw_pwr_cfg_pbuf_arb_min_spacing_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_min_spacing),
0x2E0,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_min_spacing", psw_pwr_cfg_pbuf_arb_min_spacing_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_sync_tdm_delay {
CREATE_ENTRY("cnt", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_pwr_cfg_pbuf_arb_sync_tdm_delay_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_sync_tdm_delay),
0x2E8,
CSR_TYPE::REG,
1);
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_sync_tdm_delay", psw_pwr_cfg_pbuf_arb_sync_tdm_delay_prop);
 // END psw_pwr 
}
{
 // BEGIN psw_prd 
auto psw_prd_0 = nu_rng[0].add_an({"psw_prd"}, 0x9100000, 1, 0x0);
fld_map_t psw_prd_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_prd_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_timeout_thresh_cfg", psw_prd_timeout_thresh_cfg_prop);
fld_map_t psw_prd_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prd_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_timedout_sta", psw_prd_timedout_sta_prop);
fld_map_t psw_prd_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prd_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_timeout_clr", psw_prd_timeout_clr_prop);
fld_map_t psw_prd_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_prd_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_features", psw_prd_features_prop);
fld_map_t psw_prd_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_prd_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_spare_pio", psw_prd_spare_pio_prop);
fld_map_t psw_prd_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_prd_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_scratchpad", psw_prd_scratchpad_prop);
fld_map_t psw_prd_cfg_pb_bytes_adj {
CREATE_ENTRY("fpg_val", 0, 5),
CREATE_ENTRY("epg_val", 5, 5),
CREATE_ENTRY("__rsvd", 10, 54)
};auto psw_prd_cfg_pb_bytes_adj_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pb_bytes_adj),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pb_bytes_adj", psw_prd_cfg_pb_bytes_adj_prop);
fld_map_t psw_prd_cfg_min_pkt_size {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_min_pkt_size_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_min_pkt_size),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_min_pkt_size", psw_prd_cfg_min_pkt_size_prop);
fld_map_t psw_prd_cfg_mcd_epg_sampled_pkt {
CREATE_ENTRY("enable", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prd_cfg_mcd_epg_sampled_pkt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_mcd_epg_sampled_pkt),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_mcd_epg_sampled_pkt", psw_prd_cfg_mcd_epg_sampled_pkt_prop);
fld_map_t psw_prd_cfg_edb_credits_efpg {
CREATE_ENTRY("stream0_credit_val", 0, 4),
CREATE_ENTRY("stream0_credit_init", 4, 1),
CREATE_ENTRY("stream1_credit_val", 5, 4),
CREATE_ENTRY("stream1_credit_init", 9, 1),
CREATE_ENTRY("stream2_credit_val", 10, 4),
CREATE_ENTRY("stream2_credit_init", 14, 1),
CREATE_ENTRY("stream3_credit_val", 15, 4),
CREATE_ENTRY("stream3_credit_init", 19, 1),
CREATE_ENTRY("__rsvd", 20, 44)
};auto psw_prd_cfg_edb_credits_efpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_edb_credits_efpg),
0x98,
CSR_TYPE::REG_LST,
1);
add_csr(psw_prd_0, "psw_prd_cfg_edb_credits_efpg", psw_prd_cfg_edb_credits_efpg_prop);
fld_map_t psw_prd_cfg_stream_drain {
CREATE_ENTRY("fp_stream_en", 0, 24),
CREATE_ENTRY("epg_en", 24, 3),
CREATE_ENTRY("__rsvd", 27, 37)
};auto psw_prd_cfg_stream_drain_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_stream_drain),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_stream_drain", psw_prd_cfg_stream_drain_prop);
fld_map_t psw_prd_sta_credits_efpg {
CREATE_ENTRY("stream0_pkt_info_fifo_cnt", 0, 4),
CREATE_ENTRY("stream0_edb_credit_cnt", 4, 4),
CREATE_ENTRY("stream1_pkt_info_fifo_cnt", 8, 4),
CREATE_ENTRY("stream1_edb_credit_cnt", 12, 4),
CREATE_ENTRY("stream2_pkt_info_fifo_cnt", 16, 4),
CREATE_ENTRY("stream2_edb_credit_cnt", 20, 4),
CREATE_ENTRY("stream3_pkt_info_fifo_cnt", 24, 4),
CREATE_ENTRY("stream3_edb_credit_cnt", 28, 4),
CREATE_ENTRY("__rsvd", 32, 32)
};auto psw_prd_sta_credits_efpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_sta_credits_efpg),
0xD0,
CSR_TYPE::REG_LST,
1);
add_csr(psw_prd_0, "psw_prd_sta_credits_efpg", psw_prd_sta_credits_efpg_prop);
fld_map_t psw_prd_cfg_edb_credits_erp {
CREATE_ENTRY("credit_val", 0, 4),
CREATE_ENTRY("credit_init", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto psw_prd_cfg_edb_credits_erp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_edb_credits_erp),
0x100,
CSR_TYPE::REG_LST,
1);
add_csr(psw_prd_0, "psw_prd_cfg_edb_credits_erp", psw_prd_cfg_edb_credits_erp_prop);
fld_map_t psw_prd_sta_credits_erp {
CREATE_ENTRY("pkt_info_fifo_cnt", 0, 4),
CREATE_ENTRY("edb_credit_cnt", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_sta_credits_erp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_sta_credits_erp),
0x118,
CSR_TYPE::REG_LST,
1);
add_csr(psw_prd_0, "psw_prd_sta_credits_erp", psw_prd_sta_credits_erp_prop);
fld_map_t psw_prd_sta_credits_purge_port {
CREATE_ENTRY("pkt_info_fifo_cnt", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_sta_credits_purge_port_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_sta_credits_purge_port),
0x130,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_sta_credits_purge_port", psw_prd_sta_credits_purge_port_prop);
fld_map_t psw_prd_cfg_spd {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("dest_stream", 1, 6),
CREATE_ENTRY("dest_q", 7, 4),
CREATE_ENTRY("num_scopy_rw_instr", 11, 4),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_prd_cfg_spd_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_spd),
0x138,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_spd", psw_prd_cfg_spd_prop);
fld_map_t psw_prd_cfg_spd_scopy_rw_instr_lowerhalf {
CREATE_ENTRY("val", 0, 64)
};auto psw_prd_cfg_spd_scopy_rw_instr_lowerhalf_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_spd_scopy_rw_instr_lowerhalf),
0x140,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_spd_scopy_rw_instr_lowerhalf", psw_prd_cfg_spd_scopy_rw_instr_lowerhalf_prop);
fld_map_t psw_prd_cfg_spd_scopy_rw_instr_upperhalf {
CREATE_ENTRY("val", 0, 64)
};auto psw_prd_cfg_spd_scopy_rw_instr_upperhalf_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_spd_scopy_rw_instr_upperhalf),
0x148,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_spd_scopy_rw_instr_upperhalf", psw_prd_cfg_spd_scopy_rw_instr_upperhalf_prop);
fld_map_t psw_prd_stats_cfg_deq_cntr {
CREATE_ENTRY("count_rewrite_bytes", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prd_stats_cfg_deq_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_stats_cfg_deq_cntr),
0x150,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_stats_cfg_deq_cntr", psw_prd_stats_cfg_deq_cntr_prop);
fld_map_t psw_prd_cfg_pbuf_arb_cln {
CREATE_ENTRY("vld", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prd_cfg_pbuf_arb_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_cln),
0x160,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_cln", psw_prd_cfg_pbuf_arb_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg0_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_cfg_pbuf_arb_fpg0_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg0_streams_en),
0x168,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg0_streams_en", psw_prd_cfg_pbuf_arb_fpg0_streams_en_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg1_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_cfg_pbuf_arb_fpg1_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg1_streams_en),
0x170,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg1_streams_en", psw_prd_cfg_pbuf_arb_fpg1_streams_en_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg2_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_cfg_pbuf_arb_fpg2_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg2_streams_en),
0x178,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg2_streams_en", psw_prd_cfg_pbuf_arb_fpg2_streams_en_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg3_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_cfg_pbuf_arb_fpg3_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg3_streams_en),
0x180,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg3_streams_en", psw_prd_cfg_pbuf_arb_fpg3_streams_en_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg4_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_cfg_pbuf_arb_fpg4_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg4_streams_en),
0x188,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg4_streams_en", psw_prd_cfg_pbuf_arb_fpg4_streams_en_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg5_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prd_cfg_pbuf_arb_fpg5_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg5_streams_en),
0x190,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg5_streams_en", psw_prd_cfg_pbuf_arb_fpg5_streams_en_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg0_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_pbuf_arb_fpg0_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg0_cln),
0x198,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg0_cln", psw_prd_cfg_pbuf_arb_fpg0_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg1_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_pbuf_arb_fpg1_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg1_cln),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg1_cln", psw_prd_cfg_pbuf_arb_fpg1_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg2_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_pbuf_arb_fpg2_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg2_cln),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg2_cln", psw_prd_cfg_pbuf_arb_fpg2_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg3_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_pbuf_arb_fpg3_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg3_cln),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg3_cln", psw_prd_cfg_pbuf_arb_fpg3_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg4_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_pbuf_arb_fpg4_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg4_cln),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg4_cln", psw_prd_cfg_pbuf_arb_fpg4_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_fpg5_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prd_cfg_pbuf_arb_fpg5_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg5_cln),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg5_cln", psw_prd_cfg_pbuf_arb_fpg5_cln_prop);
fld_map_t psw_prd_cfg_pbuf_arb_wrr_weights {
CREATE_ENTRY("epg0", 0, 4),
CREATE_ENTRY("epg1", 4, 4),
CREATE_ENTRY("epg2", 8, 4),
CREATE_ENTRY("spl_port", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_prd_cfg_pbuf_arb_wrr_weights_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_wrr_weights),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_wrr_weights", psw_prd_cfg_pbuf_arb_wrr_weights_prop);
fld_map_t psw_prd_cfg_pbuf_arb_min_spacing {
CREATE_ENTRY("epg", 0, 5),
CREATE_ENTRY("spl_port", 5, 5),
CREATE_ENTRY("null_slot", 10, 16),
CREATE_ENTRY("__rsvd", 26, 38)
};auto psw_prd_cfg_pbuf_arb_min_spacing_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_min_spacing),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_min_spacing", psw_prd_cfg_pbuf_arb_min_spacing_prop);
fld_map_t psw_prd_cfg_pbuf_arb_sync_tdm_delay {
CREATE_ENTRY("cnt", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_prd_cfg_pbuf_arb_sync_tdm_delay_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_sync_tdm_delay),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_sync_tdm_delay", psw_prd_cfg_pbuf_arb_sync_tdm_delay_prop);
 // END psw_prd 
}
{
 // BEGIN psw_sch 
auto psw_sch_0 = nu_rng[0].add_an({"psw_sch"}, 0x9180000, 1, 0x0);
fld_map_t psw_sch_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_sch_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_timeout_thresh_cfg", psw_sch_timeout_thresh_cfg_prop);
fld_map_t psw_sch_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_sch_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_timedout_sta", psw_sch_timedout_sta_prop);
fld_map_t psw_sch_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_sch_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_timeout_clr", psw_sch_timeout_clr_prop);
fld_map_t psw_sch_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_sch_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_features", psw_sch_features_prop);
fld_map_t psw_sch_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_sch_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_spare_pio", psw_sch_spare_pio_prop);
fld_map_t psw_sch_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_sch_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_scratchpad", psw_sch_scratchpad_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_0 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_0),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_0", psw_sch_psch_cfg_credits_fp_0_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_1 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_1),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_1", psw_sch_psch_cfg_credits_fp_1_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_2 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_2),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_2", psw_sch_psch_cfg_credits_fp_2_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_3 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_3),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_3", psw_sch_psch_cfg_credits_fp_3_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_4 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_4),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_4", psw_sch_psch_cfg_credits_fp_4_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_5 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_5),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_5", psw_sch_psch_cfg_credits_fp_5_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_6 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_6),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_6", psw_sch_psch_cfg_credits_fp_6_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_7 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_7),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_7", psw_sch_psch_cfg_credits_fp_7_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_8 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_8),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_8", psw_sch_psch_cfg_credits_fp_8_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_9 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_9),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_9", psw_sch_psch_cfg_credits_fp_9_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_10 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_10),
0xD0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_10", psw_sch_psch_cfg_credits_fp_10_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_11 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_11),
0xD8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_11", psw_sch_psch_cfg_credits_fp_11_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_12 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_12),
0xE0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_12", psw_sch_psch_cfg_credits_fp_12_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_13 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_13),
0xE8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_13", psw_sch_psch_cfg_credits_fp_13_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_14 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_14),
0xF0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_14", psw_sch_psch_cfg_credits_fp_14_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_15 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_15),
0xF8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_15", psw_sch_psch_cfg_credits_fp_15_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_16 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_16),
0x100,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_16", psw_sch_psch_cfg_credits_fp_16_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_17 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_17),
0x108,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_17", psw_sch_psch_cfg_credits_fp_17_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_18 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_18),
0x110,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_18", psw_sch_psch_cfg_credits_fp_18_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_19 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_19),
0x118,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_19", psw_sch_psch_cfg_credits_fp_19_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_20 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_20),
0x120,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_20", psw_sch_psch_cfg_credits_fp_20_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_21 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_21),
0x128,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_21", psw_sch_psch_cfg_credits_fp_21_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_22 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_22),
0x130,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_22", psw_sch_psch_cfg_credits_fp_22_prop);
fld_map_t psw_sch_psch_cfg_credits_fp_23 {
CREATE_ENTRY("credit_val", 0, 3),
CREATE_ENTRY("credit_init", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_credits_fp_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp_23),
0x138,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp_23", psw_sch_psch_cfg_credits_fp_23_prop);
fld_map_t psw_sch_psch_cfg_credits_erp {
CREATE_ENTRY("credit_val", 0, 4),
CREATE_ENTRY("credit_init", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto psw_sch_psch_cfg_credits_erp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_erp),
0x140,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_erp", psw_sch_psch_cfg_credits_erp_prop);
fld_map_t psw_sch_psch_cfg_credits_purge_port {
CREATE_ENTRY("credit_val", 0, 4),
CREATE_ENTRY("credit_init", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto psw_sch_psch_cfg_credits_purge_port_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_credits_purge_port),
0x158,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_purge_port", psw_sch_psch_cfg_credits_purge_port_prop);
fld_map_t psw_sch_psch_sta_credits_purge_port {
CREATE_ENTRY("credit_val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_sta_credits_purge_port_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_sta_credits_purge_port),
0x160,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_sta_credits_purge_port", psw_sch_psch_sta_credits_purge_port_prop);
fld_map_t psw_sch_psch_sta_credits_erp {
CREATE_ENTRY("credit_val", 0, 12),
CREATE_ENTRY("__rsvd", 12, 52)
};auto psw_sch_psch_sta_credits_erp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_sta_credits_erp),
0x168,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_psch_sta_credits_erp", psw_sch_psch_sta_credits_erp_prop);
fld_map_t psw_sch_psch_cfg_select_credits_fp_stream {
CREATE_ENTRY("fp_num", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto psw_sch_psch_cfg_select_credits_fp_stream_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_select_credits_fp_stream),
0x180,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_select_credits_fp_stream", psw_sch_psch_cfg_select_credits_fp_stream_prop);
fld_map_t psw_sch_psch_sta_credits_fp_stream {
CREATE_ENTRY("credit_val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto psw_sch_psch_sta_credits_fp_stream_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_sta_credits_fp_stream),
0x188,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_sta_credits_fp_stream", psw_sch_psch_sta_credits_fp_stream_prop);
fld_map_t psw_sch_psch_cfg_arb_sync_tdm_delay {
CREATE_ENTRY("cnt", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_sch_psch_cfg_arb_sync_tdm_delay_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_sync_tdm_delay),
0x190,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_sync_tdm_delay", psw_sch_psch_cfg_arb_sync_tdm_delay_prop);
fld_map_t psw_sch_psch_cfg_arb {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_sch_psch_cfg_arb_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb),
0x198,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb", psw_sch_psch_cfg_arb_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg0_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_fpg0_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg0_streams_en),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg0_streams_en", psw_sch_psch_cfg_arb_fpg0_streams_en_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg1_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_fpg1_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg1_streams_en),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg1_streams_en", psw_sch_psch_cfg_arb_fpg1_streams_en_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg2_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_fpg2_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg2_streams_en),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg2_streams_en", psw_sch_psch_cfg_arb_fpg2_streams_en_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg3_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_fpg3_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg3_streams_en),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg3_streams_en", psw_sch_psch_cfg_arb_fpg3_streams_en_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg4_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_fpg4_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg4_streams_en),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg4_streams_en", psw_sch_psch_cfg_arb_fpg4_streams_en_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg5_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_fpg5_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg5_streams_en),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg5_streams_en", psw_sch_psch_cfg_arb_fpg5_streams_en_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg0_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_fpg0_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg0_cln),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg0_cln", psw_sch_psch_cfg_arb_fpg0_cln_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg1_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_fpg1_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg1_cln),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg1_cln", psw_sch_psch_cfg_arb_fpg1_cln_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg2_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_fpg2_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg2_cln),
0x1E0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg2_cln", psw_sch_psch_cfg_arb_fpg2_cln_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg3_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_fpg3_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg3_cln),
0x1E8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg3_cln", psw_sch_psch_cfg_arb_fpg3_cln_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg4_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_fpg4_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg4_cln),
0x1F0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg4_cln", psw_sch_psch_cfg_arb_fpg4_cln_prop);
fld_map_t psw_sch_psch_cfg_arb_fpg5_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_fpg5_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg5_cln),
0x1F8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg5_cln", psw_sch_psch_cfg_arb_fpg5_cln_prop);
fld_map_t psw_sch_psch_cfg_arb_fp_tdm_slots_mask {
CREATE_ENTRY("num_slots_fp0", 0, 2),
CREATE_ENTRY("num_slots_fp1", 2, 2),
CREATE_ENTRY("num_slots_fp2", 4, 2),
CREATE_ENTRY("num_slots_fp3", 6, 2),
CREATE_ENTRY("num_slots_fp4", 8, 2),
CREATE_ENTRY("num_slots_fp5", 10, 2),
CREATE_ENTRY("num_slots_fp6", 12, 2),
CREATE_ENTRY("num_slots_fp7", 14, 2),
CREATE_ENTRY("num_slots_fp8", 16, 2),
CREATE_ENTRY("num_slots_fp9", 18, 2),
CREATE_ENTRY("num_slots_fp10", 20, 2),
CREATE_ENTRY("num_slots_fp11", 22, 2),
CREATE_ENTRY("num_slots_fp12", 24, 2),
CREATE_ENTRY("num_slots_fp13", 26, 2),
CREATE_ENTRY("num_slots_fp14", 28, 2),
CREATE_ENTRY("num_slots_fp15", 30, 2),
CREATE_ENTRY("num_slots_fp16", 32, 2),
CREATE_ENTRY("num_slots_fp17", 34, 2),
CREATE_ENTRY("num_slots_fp18", 36, 2),
CREATE_ENTRY("num_slots_fp19", 38, 2),
CREATE_ENTRY("num_slots_fp20", 40, 2),
CREATE_ENTRY("num_slots_fp21", 42, 2),
CREATE_ENTRY("num_slots_fp22", 44, 2),
CREATE_ENTRY("num_slots_fp23", 46, 2),
CREATE_ENTRY("__rsvd", 48, 16)
};auto psw_sch_psch_cfg_arb_fp_tdm_slots_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fp_tdm_slots_mask),
0x200,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fp_tdm_slots_mask", psw_sch_psch_cfg_arb_fp_tdm_slots_mask_prop);
fld_map_t psw_sch_psch_cfg_arb_min_spacing {
CREATE_ENTRY("epg", 0, 5),
CREATE_ENTRY("ep_streams", 5, 5),
CREATE_ENTRY("purge_port", 10, 5),
CREATE_ENTRY("null_slot", 15, 16),
CREATE_ENTRY("__rsvd", 31, 33)
};auto psw_sch_psch_cfg_arb_min_spacing_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_min_spacing),
0x208,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_min_spacing", psw_sch_psch_cfg_arb_min_spacing_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_period {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_psch_cfg_arb_gr_period_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_period),
0x210,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_period", psw_sch_psch_cfg_arb_gr_period_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_0 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_0),
0x218,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_0", psw_sch_psch_cfg_arb_gr_wt_ep_stream_0_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_1 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_1),
0x220,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_1", psw_sch_psch_cfg_arb_gr_wt_ep_stream_1_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_2 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_2),
0x228,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_2", psw_sch_psch_cfg_arb_gr_wt_ep_stream_2_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_3 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_3),
0x230,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_3", psw_sch_psch_cfg_arb_gr_wt_ep_stream_3_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_4 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_4),
0x238,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_4", psw_sch_psch_cfg_arb_gr_wt_ep_stream_4_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_5 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_5),
0x240,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_5", psw_sch_psch_cfg_arb_gr_wt_ep_stream_5_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_6 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_6),
0x248,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_6", psw_sch_psch_cfg_arb_gr_wt_ep_stream_6_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_7 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_7),
0x250,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_7", psw_sch_psch_cfg_arb_gr_wt_ep_stream_7_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_8 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_8),
0x258,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_8", psw_sch_psch_cfg_arb_gr_wt_ep_stream_8_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_9 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_9),
0x260,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_9", psw_sch_psch_cfg_arb_gr_wt_ep_stream_9_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_10 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_10),
0x268,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_10", psw_sch_psch_cfg_arb_gr_wt_ep_stream_10_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_11 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_11),
0x270,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_11", psw_sch_psch_cfg_arb_gr_wt_ep_stream_11_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_12 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_12),
0x278,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_12", psw_sch_psch_cfg_arb_gr_wt_ep_stream_12_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_13 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_13),
0x280,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_13", psw_sch_psch_cfg_arb_gr_wt_ep_stream_13_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_14 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_14),
0x288,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_14", psw_sch_psch_cfg_arb_gr_wt_ep_stream_14_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_15 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_15),
0x290,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_15", psw_sch_psch_cfg_arb_gr_wt_ep_stream_15_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_16 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_16),
0x298,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_16", psw_sch_psch_cfg_arb_gr_wt_ep_stream_16_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_17 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_17),
0x2A0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_17", psw_sch_psch_cfg_arb_gr_wt_ep_stream_17_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_18 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_18),
0x2A8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_18", psw_sch_psch_cfg_arb_gr_wt_ep_stream_18_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_19 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_19),
0x2B0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_19", psw_sch_psch_cfg_arb_gr_wt_ep_stream_19_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_20 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_20),
0x2B8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_20", psw_sch_psch_cfg_arb_gr_wt_ep_stream_20_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_21 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_21),
0x2C0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_21", psw_sch_psch_cfg_arb_gr_wt_ep_stream_21_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_22 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_22),
0x2C8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_22", psw_sch_psch_cfg_arb_gr_wt_ep_stream_22_prop);
fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream_23 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream_23),
0x2D0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream_23", psw_sch_psch_cfg_arb_gr_wt_ep_stream_23_prop);
fld_map_t psw_sch_psch_sta_port_active {
CREATE_ENTRY("vec", 0, 49),
CREATE_ENTRY("__rsvd", 49, 15)
};auto psw_sch_psch_sta_port_active_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_psch_sta_port_active),
0x2D8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_psch_sta_port_active", psw_sch_psch_sta_port_active_prop);
fld_map_t psw_sch_qsch_mem_init_start_cfg {
CREATE_ENTRY("chnl_dwrr_sc", 0, 1),
CREATE_ENTRY("q_dwrr_sc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_sch_qsch_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_mem_init_start_cfg),
0x2E0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_qsch_mem_init_start_cfg", psw_sch_qsch_mem_init_start_cfg_prop);
fld_map_t psw_sch_qsch_mem_init_done_status {
CREATE_ENTRY("chnl_dwrr_sc", 0, 1),
CREATE_ENTRY("q_dwrr_sc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_sch_qsch_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_mem_init_done_status),
0x2E8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_qsch_mem_init_done_status", psw_sch_qsch_mem_init_done_status_prop);
fld_map_t psw_sch_qsch_cfg_chnl_q_mapping_fp {
CREATE_ENTRY("mode_fp0", 0, 1),
CREATE_ENTRY("mode_fp1", 1, 1),
CREATE_ENTRY("mode_fp2", 2, 1),
CREATE_ENTRY("mode_fp3", 3, 1),
CREATE_ENTRY("mode_fp4", 4, 1),
CREATE_ENTRY("mode_fp5", 5, 1),
CREATE_ENTRY("mode_fp6", 6, 1),
CREATE_ENTRY("mode_fp7", 7, 1),
CREATE_ENTRY("mode_fp8", 8, 1),
CREATE_ENTRY("mode_fp9", 9, 1),
CREATE_ENTRY("mode_fp10", 10, 1),
CREATE_ENTRY("mode_fp11", 11, 1),
CREATE_ENTRY("mode_fp12", 12, 1),
CREATE_ENTRY("mode_fp13", 13, 1),
CREATE_ENTRY("mode_fp14", 14, 1),
CREATE_ENTRY("mode_fp15", 15, 1),
CREATE_ENTRY("mode_fp16", 16, 1),
CREATE_ENTRY("mode_fp17", 17, 1),
CREATE_ENTRY("mode_fp18", 18, 1),
CREATE_ENTRY("mode_fp19", 19, 1),
CREATE_ENTRY("mode_fp20", 20, 1),
CREATE_ENTRY("mode_fp21", 21, 1),
CREATE_ENTRY("mode_fp22", 22, 1),
CREATE_ENTRY("mode_fp23", 23, 1),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_qsch_cfg_chnl_q_mapping_fp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_chnl_q_mapping_fp),
0x2F0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_chnl_q_mapping_fp", psw_sch_qsch_cfg_chnl_q_mapping_fp_prop);
fld_map_t psw_sch_qsch_cfg_cr_sp_queues_fp {
CREATE_ENTRY("vec", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_qsch_cfg_cr_sp_queues_fp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_cr_sp_queues_fp),
0x2F8,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_cr_sp_queues_fp", psw_sch_qsch_cfg_cr_sp_queues_fp_prop);
fld_map_t psw_sch_qsch_cfg_extrabw_sp_queues_fp {
CREATE_ENTRY("vec", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_qsch_cfg_extrabw_sp_queues_fp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_extrabw_sp_queues_fp),
0x3B8,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_extrabw_sp_queues_fp", psw_sch_qsch_cfg_extrabw_sp_queues_fp_prop);
fld_map_t psw_sch_qsch_cfg_cr_sp_channels_fp {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_qsch_cfg_cr_sp_channels_fp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_cr_sp_channels_fp),
0x478,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_cr_sp_channels_fp", psw_sch_qsch_cfg_cr_sp_channels_fp_prop);
fld_map_t psw_sch_qsch_cfg_extrabw_sp_channels_fp {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_sch_qsch_cfg_extrabw_sp_channels_fp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_extrabw_sp_channels_fp),
0x538,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_extrabw_sp_channels_fp", psw_sch_qsch_cfg_extrabw_sp_channels_fp_prop);
fld_map_t psw_sch_qsch_cfg_cr_sp_queues_ep {
CREATE_ENTRY("vec", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_qsch_cfg_cr_sp_queues_ep_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_cr_sp_queues_ep),
0x5F8,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_cr_sp_queues_ep", psw_sch_qsch_cfg_cr_sp_queues_ep_prop);
fld_map_t psw_sch_qsch_cfg_extrabw_sp_queues_ep {
CREATE_ENTRY("vec", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_qsch_cfg_extrabw_sp_queues_ep_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_extrabw_sp_queues_ep),
0x6B8,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_extrabw_sp_queues_ep", psw_sch_qsch_cfg_extrabw_sp_queues_ep_prop);
fld_map_t psw_sch_qsch_cfg_flush_queues_fp {
CREATE_ENTRY("vec", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_qsch_cfg_flush_queues_fp_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_flush_queues_fp),
0x778,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_flush_queues_fp", psw_sch_qsch_cfg_flush_queues_fp_prop);
fld_map_t psw_sch_qsch_cfg_flush_queues_ep {
CREATE_ENTRY("vec", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_qsch_cfg_flush_queues_ep_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_qsch_cfg_flush_queues_ep),
0x838,
CSR_TYPE::REG_LST,
1);
add_csr(psw_sch_0, "psw_sch_qsch_cfg_flush_queues_ep", psw_sch_qsch_cfg_flush_queues_ep_prop);
fld_map_t psw_sch_orl_cfg_refresh_period {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("en", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto psw_sch_orl_cfg_refresh_period_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_orl_cfg_refresh_period),
0x8F8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_orl_cfg_refresh_period", psw_sch_orl_cfg_refresh_period_prop);
fld_map_t psw_sch_orl_cfg_deq_upd {
CREATE_ENTRY("dis", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_sch_orl_cfg_deq_upd_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_orl_cfg_deq_upd),
0x900,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_orl_cfg_deq_upd", psw_sch_orl_cfg_deq_upd_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_0 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_0),
0x908,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_0", psw_sch_pfcrx_q_to_pri_fp_0_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_1 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_1),
0x910,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_1", psw_sch_pfcrx_q_to_pri_fp_1_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_2 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_2),
0x918,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_2", psw_sch_pfcrx_q_to_pri_fp_2_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_3 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_3),
0x920,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_3", psw_sch_pfcrx_q_to_pri_fp_3_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_4 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_4),
0x928,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_4", psw_sch_pfcrx_q_to_pri_fp_4_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_5 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_5),
0x930,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_5", psw_sch_pfcrx_q_to_pri_fp_5_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_6 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_6),
0x938,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_6", psw_sch_pfcrx_q_to_pri_fp_6_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_7 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_7),
0x940,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_7", psw_sch_pfcrx_q_to_pri_fp_7_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_8 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_8),
0x948,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_8", psw_sch_pfcrx_q_to_pri_fp_8_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_9 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_9),
0x950,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_9", psw_sch_pfcrx_q_to_pri_fp_9_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_10 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_10),
0x958,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_10", psw_sch_pfcrx_q_to_pri_fp_10_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_11 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_11),
0x960,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_11", psw_sch_pfcrx_q_to_pri_fp_11_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_12 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_12),
0x968,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_12", psw_sch_pfcrx_q_to_pri_fp_12_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_13 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_13),
0x970,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_13", psw_sch_pfcrx_q_to_pri_fp_13_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_14 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_14),
0x978,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_14", psw_sch_pfcrx_q_to_pri_fp_14_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_15 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_15),
0x980,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_15", psw_sch_pfcrx_q_to_pri_fp_15_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_16 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_16),
0x988,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_16", psw_sch_pfcrx_q_to_pri_fp_16_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_17 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_17),
0x990,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_17", psw_sch_pfcrx_q_to_pri_fp_17_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_18 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_18),
0x998,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_18", psw_sch_pfcrx_q_to_pri_fp_18_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_19 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_19),
0x9A0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_19", psw_sch_pfcrx_q_to_pri_fp_19_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_20 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_20),
0x9A8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_20", psw_sch_pfcrx_q_to_pri_fp_20_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_21 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_21),
0x9B0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_21", psw_sch_pfcrx_q_to_pri_fp_21_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_22 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_22),
0x9B8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_22", psw_sch_pfcrx_q_to_pri_fp_22_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_fp_23 {
CREATE_ENTRY("q0", 0, 4),
CREATE_ENTRY("q1", 4, 4),
CREATE_ENTRY("q2", 8, 4),
CREATE_ENTRY("q3", 12, 4),
CREATE_ENTRY("q4", 16, 4),
CREATE_ENTRY("q5", 20, 4),
CREATE_ENTRY("q6", 24, 4),
CREATE_ENTRY("q7", 28, 4),
CREATE_ENTRY("q8", 32, 4),
CREATE_ENTRY("q9", 36, 4),
CREATE_ENTRY("q10", 40, 4),
CREATE_ENTRY("q11", 44, 4),
CREATE_ENTRY("q12", 48, 4),
CREATE_ENTRY("q13", 52, 4),
CREATE_ENTRY("q14", 56, 4),
CREATE_ENTRY("q15", 60, 4)
};auto psw_sch_pfcrx_q_to_pri_fp_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp_23),
0x9C0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp_23", psw_sch_pfcrx_q_to_pri_fp_23_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_0 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_0),
0x9C8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_0", psw_sch_pfcrx_q_to_pri_ep_0_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_1 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_1),
0x9D0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_1", psw_sch_pfcrx_q_to_pri_ep_1_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_2 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_2),
0x9D8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_2", psw_sch_pfcrx_q_to_pri_ep_2_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_3 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_3),
0x9E0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_3", psw_sch_pfcrx_q_to_pri_ep_3_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_4 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_4),
0x9E8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_4", psw_sch_pfcrx_q_to_pri_ep_4_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_5 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_5),
0x9F0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_5", psw_sch_pfcrx_q_to_pri_ep_5_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_6 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_6),
0x9F8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_6", psw_sch_pfcrx_q_to_pri_ep_6_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_7 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_7),
0xA00,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_7", psw_sch_pfcrx_q_to_pri_ep_7_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_8 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_8),
0xA08,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_8", psw_sch_pfcrx_q_to_pri_ep_8_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_9 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_9),
0xA10,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_9", psw_sch_pfcrx_q_to_pri_ep_9_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_10 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_10),
0xA18,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_10", psw_sch_pfcrx_q_to_pri_ep_10_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_11 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_11),
0xA20,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_11", psw_sch_pfcrx_q_to_pri_ep_11_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_12 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_12),
0xA28,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_12", psw_sch_pfcrx_q_to_pri_ep_12_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_13 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_13),
0xA30,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_13", psw_sch_pfcrx_q_to_pri_ep_13_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_14 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_14),
0xA38,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_14", psw_sch_pfcrx_q_to_pri_ep_14_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_15 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_15),
0xA40,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_15", psw_sch_pfcrx_q_to_pri_ep_15_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_16 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_16),
0xA48,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_16", psw_sch_pfcrx_q_to_pri_ep_16_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_17 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_17),
0xA50,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_17", psw_sch_pfcrx_q_to_pri_ep_17_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_18 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_18),
0xA58,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_18", psw_sch_pfcrx_q_to_pri_ep_18_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_19 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_19),
0xA60,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_19", psw_sch_pfcrx_q_to_pri_ep_19_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_20 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_20),
0xA68,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_20", psw_sch_pfcrx_q_to_pri_ep_20_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_21 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_21),
0xA70,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_21", psw_sch_pfcrx_q_to_pri_ep_21_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_22 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_22),
0xA78,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_22", psw_sch_pfcrx_q_to_pri_ep_22_prop);
fld_map_t psw_sch_pfcrx_q_to_pri_ep_23 {
CREATE_ENTRY("q0", 0, 3),
CREATE_ENTRY("q1", 3, 3),
CREATE_ENTRY("q2", 6, 3),
CREATE_ENTRY("q3", 9, 3),
CREATE_ENTRY("q4", 12, 3),
CREATE_ENTRY("q5", 15, 3),
CREATE_ENTRY("q6", 18, 3),
CREATE_ENTRY("q7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_sch_pfcrx_q_to_pri_ep_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep_23),
0xA80,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep_23", psw_sch_pfcrx_q_to_pri_ep_23_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_0 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_0),
0xA88,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_0", psw_sch_pfcrx_xoff_set_fp_0_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_1 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_1),
0xA90,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_1", psw_sch_pfcrx_xoff_set_fp_1_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_2 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_2),
0xA98,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_2", psw_sch_pfcrx_xoff_set_fp_2_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_3 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_3),
0xAA0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_3", psw_sch_pfcrx_xoff_set_fp_3_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_4 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_4),
0xAA8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_4", psw_sch_pfcrx_xoff_set_fp_4_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_5 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_5),
0xAB0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_5", psw_sch_pfcrx_xoff_set_fp_5_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_6 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_6),
0xAB8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_6", psw_sch_pfcrx_xoff_set_fp_6_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_7 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_7),
0xAC0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_7", psw_sch_pfcrx_xoff_set_fp_7_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_8 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_8),
0xAC8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_8", psw_sch_pfcrx_xoff_set_fp_8_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_9 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_9),
0xAD0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_9", psw_sch_pfcrx_xoff_set_fp_9_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_10 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_10),
0xAD8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_10", psw_sch_pfcrx_xoff_set_fp_10_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_11 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_11),
0xAE0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_11", psw_sch_pfcrx_xoff_set_fp_11_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_12 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_12),
0xAE8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_12", psw_sch_pfcrx_xoff_set_fp_12_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_13 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_13),
0xAF0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_13", psw_sch_pfcrx_xoff_set_fp_13_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_14 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_14),
0xAF8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_14", psw_sch_pfcrx_xoff_set_fp_14_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_15 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_15),
0xB00,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_15", psw_sch_pfcrx_xoff_set_fp_15_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_16 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_16),
0xB08,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_16", psw_sch_pfcrx_xoff_set_fp_16_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_17 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_17),
0xB10,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_17", psw_sch_pfcrx_xoff_set_fp_17_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_18 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_18),
0xB18,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_18", psw_sch_pfcrx_xoff_set_fp_18_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_19 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_19),
0xB20,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_19", psw_sch_pfcrx_xoff_set_fp_19_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_20 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_20),
0xB28,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_20", psw_sch_pfcrx_xoff_set_fp_20_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_21 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_21),
0xB30,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_21", psw_sch_pfcrx_xoff_set_fp_21_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_22 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_22),
0xB38,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_22", psw_sch_pfcrx_xoff_set_fp_22_prop);
fld_map_t psw_sch_pfcrx_xoff_set_fp_23 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_set_fp_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp_23),
0xB40,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp_23", psw_sch_pfcrx_xoff_set_fp_23_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_0 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_0),
0xB48,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_0", psw_sch_pfcrx_xoff_reset_fp_0_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_1 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_1),
0xB50,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_1", psw_sch_pfcrx_xoff_reset_fp_1_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_2 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_2),
0xB58,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_2", psw_sch_pfcrx_xoff_reset_fp_2_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_3 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_3),
0xB60,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_3", psw_sch_pfcrx_xoff_reset_fp_3_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_4 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_4),
0xB68,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_4", psw_sch_pfcrx_xoff_reset_fp_4_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_5 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_5),
0xB70,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_5", psw_sch_pfcrx_xoff_reset_fp_5_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_6 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_6),
0xB78,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_6", psw_sch_pfcrx_xoff_reset_fp_6_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_7 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_7),
0xB80,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_7", psw_sch_pfcrx_xoff_reset_fp_7_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_8 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_8),
0xB88,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_8", psw_sch_pfcrx_xoff_reset_fp_8_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_9 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_9),
0xB90,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_9", psw_sch_pfcrx_xoff_reset_fp_9_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_10 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_10),
0xB98,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_10", psw_sch_pfcrx_xoff_reset_fp_10_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_11 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_11),
0xBA0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_11", psw_sch_pfcrx_xoff_reset_fp_11_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_12 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_12),
0xBA8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_12", psw_sch_pfcrx_xoff_reset_fp_12_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_13 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_13),
0xBB0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_13", psw_sch_pfcrx_xoff_reset_fp_13_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_14 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_14),
0xBB8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_14", psw_sch_pfcrx_xoff_reset_fp_14_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_15 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_15),
0xBC0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_15", psw_sch_pfcrx_xoff_reset_fp_15_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_16 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_16),
0xBC8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_16", psw_sch_pfcrx_xoff_reset_fp_16_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_17 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_17),
0xBD0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_17", psw_sch_pfcrx_xoff_reset_fp_17_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_18 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_18),
0xBD8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_18", psw_sch_pfcrx_xoff_reset_fp_18_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_19 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_19),
0xBE0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_19", psw_sch_pfcrx_xoff_reset_fp_19_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_20 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_20),
0xBE8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_20", psw_sch_pfcrx_xoff_reset_fp_20_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_21 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_21),
0xBF0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_21", psw_sch_pfcrx_xoff_reset_fp_21_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_22 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_22),
0xBF8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_22", psw_sch_pfcrx_xoff_reset_fp_22_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_fp_23 {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_pfcrx_xoff_reset_fp_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp_23),
0xC00,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp_23", psw_sch_pfcrx_xoff_reset_fp_23_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_0 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_0),
0xC08,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_0", psw_sch_pfcrx_xoff_set_ep_0_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_1 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_1),
0xC10,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_1", psw_sch_pfcrx_xoff_set_ep_1_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_2 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_2),
0xC18,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_2", psw_sch_pfcrx_xoff_set_ep_2_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_3 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_3),
0xC20,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_3", psw_sch_pfcrx_xoff_set_ep_3_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_4 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_4),
0xC28,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_4", psw_sch_pfcrx_xoff_set_ep_4_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_5 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_5),
0xC30,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_5", psw_sch_pfcrx_xoff_set_ep_5_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_6 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_6),
0xC38,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_6", psw_sch_pfcrx_xoff_set_ep_6_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_7 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_7),
0xC40,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_7", psw_sch_pfcrx_xoff_set_ep_7_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_8 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_8),
0xC48,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_8", psw_sch_pfcrx_xoff_set_ep_8_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_9 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_9),
0xC50,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_9", psw_sch_pfcrx_xoff_set_ep_9_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_10 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_10),
0xC58,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_10", psw_sch_pfcrx_xoff_set_ep_10_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_11 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_11),
0xC60,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_11", psw_sch_pfcrx_xoff_set_ep_11_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_12 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_12),
0xC68,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_12", psw_sch_pfcrx_xoff_set_ep_12_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_13 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_13),
0xC70,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_13", psw_sch_pfcrx_xoff_set_ep_13_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_14 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_14),
0xC78,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_14", psw_sch_pfcrx_xoff_set_ep_14_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_15 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_15),
0xC80,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_15", psw_sch_pfcrx_xoff_set_ep_15_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_16 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_16),
0xC88,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_16", psw_sch_pfcrx_xoff_set_ep_16_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_17 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_17),
0xC90,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_17", psw_sch_pfcrx_xoff_set_ep_17_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_18 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_18),
0xC98,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_18", psw_sch_pfcrx_xoff_set_ep_18_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_19 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_19),
0xCA0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_19", psw_sch_pfcrx_xoff_set_ep_19_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_20 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_20),
0xCA8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_20", psw_sch_pfcrx_xoff_set_ep_20_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_21 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_21),
0xCB0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_21", psw_sch_pfcrx_xoff_set_ep_21_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_22 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_22),
0xCB8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_22", psw_sch_pfcrx_xoff_set_ep_22_prop);
fld_map_t psw_sch_pfcrx_xoff_set_ep_23 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_set_ep_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep_23),
0xCC0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep_23", psw_sch_pfcrx_xoff_set_ep_23_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_0 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_0),
0xCC8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_0", psw_sch_pfcrx_xoff_reset_ep_0_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_1 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_1),
0xCD0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_1", psw_sch_pfcrx_xoff_reset_ep_1_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_2 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_2),
0xCD8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_2", psw_sch_pfcrx_xoff_reset_ep_2_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_3 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_3),
0xCE0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_3", psw_sch_pfcrx_xoff_reset_ep_3_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_4 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_4),
0xCE8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_4", psw_sch_pfcrx_xoff_reset_ep_4_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_5 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_5),
0xCF0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_5", psw_sch_pfcrx_xoff_reset_ep_5_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_6 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_6),
0xCF8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_6", psw_sch_pfcrx_xoff_reset_ep_6_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_7 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_7),
0xD00,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_7", psw_sch_pfcrx_xoff_reset_ep_7_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_8 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_8),
0xD08,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_8", psw_sch_pfcrx_xoff_reset_ep_8_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_9 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_9),
0xD10,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_9", psw_sch_pfcrx_xoff_reset_ep_9_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_10 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_10),
0xD18,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_10", psw_sch_pfcrx_xoff_reset_ep_10_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_11 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_11),
0xD20,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_11", psw_sch_pfcrx_xoff_reset_ep_11_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_12 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_12),
0xD28,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_12", psw_sch_pfcrx_xoff_reset_ep_12_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_13 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_13),
0xD30,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_13", psw_sch_pfcrx_xoff_reset_ep_13_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_14 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_14),
0xD38,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_14", psw_sch_pfcrx_xoff_reset_ep_14_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_15 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_15),
0xD40,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_15", psw_sch_pfcrx_xoff_reset_ep_15_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_16 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_16),
0xD48,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_16", psw_sch_pfcrx_xoff_reset_ep_16_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_17 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_17),
0xD50,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_17", psw_sch_pfcrx_xoff_reset_ep_17_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_18 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_18),
0xD58,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_18", psw_sch_pfcrx_xoff_reset_ep_18_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_19 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_19),
0xD60,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_19", psw_sch_pfcrx_xoff_reset_ep_19_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_20 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_20),
0xD68,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_20", psw_sch_pfcrx_xoff_reset_ep_20_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_21 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_21),
0xD70,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_21", psw_sch_pfcrx_xoff_reset_ep_21_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_22 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_22),
0xD78,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_22", psw_sch_pfcrx_xoff_reset_ep_22_prop);
fld_map_t psw_sch_pfcrx_xoff_reset_ep_23 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_sch_pfcrx_xoff_reset_ep_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep_23),
0xD80,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep_23", psw_sch_pfcrx_xoff_reset_ep_23_prop);
fld_map_t psw_sch_sram_err_inj_cfg {
CREATE_ENTRY("orl_mem9", 0, 1),
CREATE_ENTRY("orl_mem8", 1, 1),
CREATE_ENTRY("orl_mem7", 2, 1),
CREATE_ENTRY("orl_mem6", 3, 1),
CREATE_ENTRY("orl_mem5", 4, 1),
CREATE_ENTRY("orl_mem4", 5, 1),
CREATE_ENTRY("orl_mem3", 6, 1),
CREATE_ENTRY("orl_mem2", 7, 1),
CREATE_ENTRY("orl_mem1", 8, 1),
CREATE_ENTRY("orl_mem0", 9, 1),
CREATE_ENTRY("qsch_chnl_dwrr_sc", 10, 1),
CREATE_ENTRY("qsch_q_dwrr_sc", 11, 1),
CREATE_ENTRY("qsch_q_dwrr_weight", 12, 1),
CREATE_ENTRY("err_type", 13, 1),
CREATE_ENTRY("__rsvd", 14, 50)
};auto psw_sch_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_err_inj_cfg),
0xD90,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_err_inj_cfg", psw_sch_sram_err_inj_cfg_prop);
fld_map_t psw_sch_sram_log_cerr_vec {
CREATE_ENTRY("orl_mem9", 0, 1),
CREATE_ENTRY("orl_mem8", 1, 1),
CREATE_ENTRY("orl_mem7", 2, 1),
CREATE_ENTRY("orl_mem6", 3, 1),
CREATE_ENTRY("orl_mem5", 4, 1),
CREATE_ENTRY("orl_mem4", 5, 1),
CREATE_ENTRY("orl_mem3", 6, 1),
CREATE_ENTRY("orl_mem2", 7, 1),
CREATE_ENTRY("orl_mem1", 8, 1),
CREATE_ENTRY("orl_mem0", 9, 1),
CREATE_ENTRY("qsch_chnl_dwrr_sc", 10, 1),
CREATE_ENTRY("qsch_q_dwrr_sc", 11, 1),
CREATE_ENTRY("qsch_q_dwrr_weight", 12, 1),
CREATE_ENTRY("__rsvd", 13, 51)
};auto psw_sch_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_log_cerr_vec),
0xD98,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_log_cerr_vec", psw_sch_sram_log_cerr_vec_prop);
fld_map_t psw_sch_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_log_cerr_syndrome),
0xDA0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_log_cerr_syndrome", psw_sch_sram_log_cerr_syndrome_prop);
fld_map_t psw_sch_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_log_cerr_addr),
0xDA8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_log_cerr_addr", psw_sch_sram_log_cerr_addr_prop);
fld_map_t psw_sch_sram_log_uerr_vec {
CREATE_ENTRY("orl_mem9", 0, 1),
CREATE_ENTRY("orl_mem8", 1, 1),
CREATE_ENTRY("orl_mem7", 2, 1),
CREATE_ENTRY("orl_mem6", 3, 1),
CREATE_ENTRY("orl_mem5", 4, 1),
CREATE_ENTRY("orl_mem4", 5, 1),
CREATE_ENTRY("orl_mem3", 6, 1),
CREATE_ENTRY("orl_mem2", 7, 1),
CREATE_ENTRY("orl_mem1", 8, 1),
CREATE_ENTRY("orl_mem0", 9, 1),
CREATE_ENTRY("qsch_chnl_dwrr_sc", 10, 1),
CREATE_ENTRY("qsch_q_dwrr_sc", 11, 1),
CREATE_ENTRY("qsch_q_dwrr_weight", 12, 1),
CREATE_ENTRY("__rsvd", 13, 51)
};auto psw_sch_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_log_uerr_vec),
0xDB0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_log_uerr_vec", psw_sch_sram_log_uerr_vec_prop);
fld_map_t psw_sch_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_log_uerr_syndrome),
0xDB8,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_log_uerr_syndrome", psw_sch_sram_log_uerr_syndrome_prop);
fld_map_t psw_sch_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_sch_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_sch_sram_log_uerr_addr),
0xDC0,
CSR_TYPE::REG,
1);
add_csr(psw_sch_0, "psw_sch_sram_log_uerr_addr", psw_sch_sram_log_uerr_addr_prop);
 // END psw_sch 
}
{
 // BEGIN psw_prm 
auto psw_prm_0 = nu_rng[0].add_an({"psw_prm"}, 0x9200000, 1, 0x0);
fld_map_t psw_prm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_prm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_timeout_thresh_cfg", psw_prm_timeout_thresh_cfg_prop);
fld_map_t psw_prm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_timedout_sta", psw_prm_timedout_sta_prop);
fld_map_t psw_prm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_prm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_timeout_clr", psw_prm_timeout_clr_prop);
fld_map_t psw_prm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_prm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_features", psw_prm_features_prop);
fld_map_t psw_prm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_prm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_spare_pio", psw_prm_spare_pio_prop);
fld_map_t psw_prm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_prm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_scratchpad", psw_prm_scratchpad_prop);
fld_map_t psw_prm_mem_init_start_cfg {
CREATE_ENTRY("irm", 0, 1),
CREATE_ENTRY("orm", 1, 1),
CREATE_ENTRY("wred", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_prm_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_mem_init_start_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_mem_init_start_cfg", psw_prm_mem_init_start_cfg_prop);
fld_map_t psw_prm_mem_init_done_status {
CREATE_ENTRY("irm", 0, 1),
CREATE_ENTRY("orm", 1, 1),
CREATE_ENTRY("wred", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_prm_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_mem_init_done_status),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_mem_init_done_status", psw_prm_mem_init_done_status_prop);
fld_map_t psw_prm_blk_en {
CREATE_ENTRY("orm_en", 0, 1),
CREATE_ENTRY("irm_en", 1, 1),
CREATE_ENTRY("grm_en", 2, 1),
CREATE_ENTRY("ctm_en", 3, 1),
CREATE_ENTRY("wred_en_main_pkt", 4, 1),
CREATE_ENTRY("ecn_en_main_pkt", 5, 1),
CREATE_ENTRY("wred_en_sampled_pkt", 6, 1),
CREATE_ENTRY("ecn_en_sampled_pkt", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_prm_blk_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_blk_en),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_blk_en", psw_prm_blk_en_prop);
fld_map_t psw_prm_cfg_spd {
CREATE_ENTRY("en_main_only_pkt", 0, 1),
CREATE_ENTRY("cfp_th", 1, 14),
CREATE_ENTRY("refresh_en", 15, 1),
CREATE_ENTRY("credits_refresh_period", 16, 14),
CREATE_ENTRY("num_pkt_credits", 30, 14),
CREATE_ENTRY("__rsvd", 44, 20)
};auto psw_prm_cfg_spd_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_cfg_spd),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_cfg_spd", psw_prm_cfg_spd_prop);
fld_map_t psw_prm_grm_cfg_sampled_copy_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("clear_hwm", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_prm_grm_cfg_sampled_copy_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_sampled_copy_thresh),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_sampled_copy_thresh", psw_prm_grm_cfg_sampled_copy_thresh_prop);
fld_map_t psw_prm_grm_sta_sampled_copy_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_sampled_copy_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_sampled_copy_cnt),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_sampled_copy_cnt", psw_prm_grm_sta_sampled_copy_cnt_prop);
fld_map_t psw_prm_grm_cfg_sf_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("xoff_thr", 14, 14),
CREATE_ENTRY("xon_thr", 28, 14),
CREATE_ENTRY("clear_hwm", 42, 1),
CREATE_ENTRY("__rsvd", 43, 21)
};auto psw_prm_grm_cfg_sf_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_sf_thresh),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_sf_thresh", psw_prm_grm_cfg_sf_thresh_prop);
fld_map_t psw_prm_grm_sta_sf_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_sf_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_sf_cnt),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_sf_cnt", psw_prm_grm_sta_sf_cnt_prop);
fld_map_t psw_prm_grm_cfg_sx_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("clear_hwm", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_prm_grm_cfg_sx_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_sx_thresh),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_sx_thresh", psw_prm_grm_cfg_sx_thresh_prop);
fld_map_t psw_prm_grm_sta_sx_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_sx_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_sx_cnt),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_sx_cnt", psw_prm_grm_sta_sx_cnt_prop);
fld_map_t psw_prm_grm_cfg_dx_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("clear_hwm", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_prm_grm_cfg_dx_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_dx_thresh),
0xD0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_dx_thresh", psw_prm_grm_cfg_dx_thresh_prop);
fld_map_t psw_prm_grm_sta_dx_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_dx_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_dx_cnt),
0xD8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_dx_cnt", psw_prm_grm_sta_dx_cnt_prop);
fld_map_t psw_prm_grm_cfg_df_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("clear_hwm", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_prm_grm_cfg_df_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_df_thresh),
0xE0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_df_thresh", psw_prm_grm_cfg_df_thresh_prop);
fld_map_t psw_prm_grm_sta_df_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_df_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_df_cnt),
0xE8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_df_cnt", psw_prm_grm_sta_df_cnt_prop);
fld_map_t psw_prm_grm_cfg_fcp_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("xoff_thr", 14, 14),
CREATE_ENTRY("xon_thr", 28, 14),
CREATE_ENTRY("clear_hwm", 42, 1),
CREATE_ENTRY("__rsvd", 43, 21)
};auto psw_prm_grm_cfg_fcp_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_fcp_thresh),
0xF0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_fcp_thresh", psw_prm_grm_cfg_fcp_thresh_prop);
fld_map_t psw_prm_grm_sta_fcp_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_fcp_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_fcp_cnt),
0xF8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_fcp_cnt", psw_prm_grm_sta_fcp_cnt_prop);
fld_map_t psw_prm_grm_cfg_nonfcp_thresh {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("xoff_thr", 14, 14),
CREATE_ENTRY("xon_thr", 28, 14),
CREATE_ENTRY("clear_hwm", 42, 1),
CREATE_ENTRY("__rsvd", 43, 21)
};auto psw_prm_grm_cfg_nonfcp_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_cfg_nonfcp_thresh),
0x100,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_cfg_nonfcp_thresh", psw_prm_grm_cfg_nonfcp_thresh_prop);
fld_map_t psw_prm_grm_sta_nonfcp_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_prm_grm_sta_nonfcp_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_grm_sta_nonfcp_cnt),
0x108,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_grm_sta_nonfcp_cnt", psw_prm_grm_sta_nonfcp_cnt_prop);
fld_map_t psw_prm_ctm_cfg_cfp_th {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto psw_prm_ctm_cfg_cfp_th_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_cfp_th),
0x110,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_cfp_th", psw_prm_ctm_cfg_cfp_th_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_0 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_0),
0x118,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_0", psw_prm_ctm_cfg_speed_fp_stream_0_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_1 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_1),
0x120,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_1", psw_prm_ctm_cfg_speed_fp_stream_1_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_2 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_2),
0x128,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_2", psw_prm_ctm_cfg_speed_fp_stream_2_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_3 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_3),
0x130,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_3", psw_prm_ctm_cfg_speed_fp_stream_3_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_4 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_4),
0x138,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_4", psw_prm_ctm_cfg_speed_fp_stream_4_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_5 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_5),
0x140,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_5", psw_prm_ctm_cfg_speed_fp_stream_5_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_6 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_6),
0x148,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_6", psw_prm_ctm_cfg_speed_fp_stream_6_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_7 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_7),
0x150,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_7", psw_prm_ctm_cfg_speed_fp_stream_7_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_8 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_8),
0x158,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_8", psw_prm_ctm_cfg_speed_fp_stream_8_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_9 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_9),
0x160,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_9", psw_prm_ctm_cfg_speed_fp_stream_9_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_10 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_10),
0x168,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_10", psw_prm_ctm_cfg_speed_fp_stream_10_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_11 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_11),
0x170,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_11", psw_prm_ctm_cfg_speed_fp_stream_11_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_12 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_12),
0x178,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_12", psw_prm_ctm_cfg_speed_fp_stream_12_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_13 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_13),
0x180,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_13", psw_prm_ctm_cfg_speed_fp_stream_13_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_14 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_14),
0x188,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_14", psw_prm_ctm_cfg_speed_fp_stream_14_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_15 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_15),
0x190,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_15", psw_prm_ctm_cfg_speed_fp_stream_15_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_16 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_16),
0x198,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_16", psw_prm_ctm_cfg_speed_fp_stream_16_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_17 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_17),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_17", psw_prm_ctm_cfg_speed_fp_stream_17_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_18 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_18),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_18", psw_prm_ctm_cfg_speed_fp_stream_18_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_19 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_19),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_19", psw_prm_ctm_cfg_speed_fp_stream_19_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_20 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_20),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_20", psw_prm_ctm_cfg_speed_fp_stream_20_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_21 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_21),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_21", psw_prm_ctm_cfg_speed_fp_stream_21_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_22 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_22),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_22", psw_prm_ctm_cfg_speed_fp_stream_22_prop);
fld_map_t psw_prm_ctm_cfg_speed_fp_stream_23 {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_prm_ctm_cfg_speed_fp_stream_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream_23),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream_23", psw_prm_ctm_cfg_speed_fp_stream_23_prop);
fld_map_t psw_prm_ctm_cfg_ct_disable_dest_fp_streams {
CREATE_ENTRY("vec", 0, 24),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_prm_ctm_cfg_ct_disable_dest_fp_streams_prop = csr_prop_t(
std::make_shared<csr_s>(psw_prm_ctm_cfg_ct_disable_dest_fp_streams),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(psw_prm_0, "psw_prm_ctm_cfg_ct_disable_dest_fp_streams", psw_prm_ctm_cfg_ct_disable_dest_fp_streams_prop);
 // END psw_prm 
}
{
 // BEGIN psw_orm 
auto psw_orm_0 = nu_rng[0].add_an({"psw_orm"}, 0x9280000, 1, 0x0);
fld_map_t psw_orm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_orm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_timeout_thresh_cfg", psw_orm_timeout_thresh_cfg_prop);
fld_map_t psw_orm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_orm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_timedout_sta", psw_orm_timedout_sta_prop);
fld_map_t psw_orm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_orm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_timeout_clr", psw_orm_timeout_clr_prop);
fld_map_t psw_orm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_orm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_features", psw_orm_features_prop);
fld_map_t psw_orm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_orm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_spare_pio", psw_orm_spare_pio_prop);
fld_map_t psw_orm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_orm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_scratchpad", psw_orm_scratchpad_prop);
fld_map_t psw_orm_cfg_glb_sh_thr {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("clear_hwm", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_cfg_glb_sh_thr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_cfg_glb_sh_thr),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_cfg_glb_sh_thr", psw_orm_cfg_glb_sh_thr_prop);
fld_map_t psw_orm_glb_sh_cnt {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_glb_sh_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_glb_sh_cnt),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_glb_sh_cnt", psw_orm_glb_sh_cnt_prop);
fld_map_t psw_orm_glb_sh_cnt_hwm {
CREATE_ENTRY("hwm_val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_glb_sh_cnt_hwm_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_glb_sh_cnt_hwm),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_glb_sh_cnt_hwm", psw_orm_glb_sh_cnt_hwm_prop);
fld_map_t psw_orm_glb_sh_pending_cnt {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto psw_orm_glb_sh_pending_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_glb_sh_pending_cnt),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_glb_sh_pending_cnt", psw_orm_glb_sh_pending_cnt_prop);
fld_map_t psw_orm_cfg_stats_color_en {
CREATE_ENTRY("green", 0, 1),
CREATE_ENTRY("yellow", 1, 1),
CREATE_ENTRY("red", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_orm_cfg_stats_color_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_cfg_stats_color_en),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_cfg_stats_color_en", psw_orm_cfg_stats_color_en_prop);
fld_map_t psw_orm_sram_err_inj_cfg {
CREATE_ENTRY("stats_port_sh_peak_cnt", 0, 1),
CREATE_ENTRY("stats_port_sh_drop_cnt", 1, 1),
CREATE_ENTRY("stats_q_peak_cnt", 2, 1),
CREATE_ENTRY("stats_q_drop_cnt", 3, 1),
CREATE_ENTRY("port_cnt_inst3", 4, 1),
CREATE_ENTRY("port_cnt_inst2", 5, 1),
CREATE_ENTRY("port_cnt_inst1", 6, 1),
CREATE_ENTRY("port_cnt_inst0", 7, 1),
CREATE_ENTRY("q_cnt_inst3", 8, 1),
CREATE_ENTRY("q_cnt_inst2", 9, 1),
CREATE_ENTRY("q_cnt_inst1", 10, 1),
CREATE_ENTRY("q_cnt_inst0", 11, 1),
CREATE_ENTRY("port_cfg", 12, 1),
CREATE_ENTRY("q_cfg", 13, 1),
CREATE_ENTRY("err_type", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_err_inj_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_err_inj_cfg", psw_orm_sram_err_inj_cfg_prop);
fld_map_t psw_orm_sram_log_cerr_vec {
CREATE_ENTRY("stats_port_sh_peak_cnt", 0, 1),
CREATE_ENTRY("stats_port_sh_drop_cnt", 1, 1),
CREATE_ENTRY("stats_q_peak_cnt", 2, 1),
CREATE_ENTRY("stats_q_drop_cnt", 3, 1),
CREATE_ENTRY("port_cnt_inst3", 4, 1),
CREATE_ENTRY("port_cnt_inst2", 5, 1),
CREATE_ENTRY("port_cnt_inst1", 6, 1),
CREATE_ENTRY("port_cnt_inst0", 7, 1),
CREATE_ENTRY("q_cnt_inst3", 8, 1),
CREATE_ENTRY("q_cnt_inst2", 9, 1),
CREATE_ENTRY("q_cnt_inst1", 10, 1),
CREATE_ENTRY("q_cnt_inst0", 11, 1),
CREATE_ENTRY("port_cfg", 12, 1),
CREATE_ENTRY("q_cfg", 13, 1),
CREATE_ENTRY("__rsvd", 14, 50)
};auto psw_orm_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_cerr_vec),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_log_cerr_vec", psw_orm_sram_log_cerr_vec_prop);
fld_map_t psw_orm_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_cerr_syndrome),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_log_cerr_syndrome", psw_orm_sram_log_cerr_syndrome_prop);
fld_map_t psw_orm_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_cerr_addr),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_log_cerr_addr", psw_orm_sram_log_cerr_addr_prop);
fld_map_t psw_orm_sram_log_uerr_vec {
CREATE_ENTRY("stats_port_sh_peak_cnt", 0, 1),
CREATE_ENTRY("stats_port_sh_drop_cnt", 1, 1),
CREATE_ENTRY("stats_q_peak_cnt", 2, 1),
CREATE_ENTRY("stats_q_drop_cnt", 3, 1),
CREATE_ENTRY("port_cnt_inst3", 4, 1),
CREATE_ENTRY("port_cnt_inst2", 5, 1),
CREATE_ENTRY("port_cnt_inst1", 6, 1),
CREATE_ENTRY("port_cnt_inst0", 7, 1),
CREATE_ENTRY("q_cnt_inst3", 8, 1),
CREATE_ENTRY("q_cnt_inst2", 9, 1),
CREATE_ENTRY("q_cnt_inst1", 10, 1),
CREATE_ENTRY("q_cnt_inst0", 11, 1),
CREATE_ENTRY("port_cfg", 12, 1),
CREATE_ENTRY("q_cfg", 13, 1),
CREATE_ENTRY("__rsvd", 14, 50)
};auto psw_orm_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_uerr_vec),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_log_uerr_vec", psw_orm_sram_log_uerr_vec_prop);
fld_map_t psw_orm_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_uerr_syndrome),
0xD0,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_log_uerr_syndrome", psw_orm_sram_log_uerr_syndrome_prop);
fld_map_t psw_orm_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_uerr_addr),
0xD8,
CSR_TYPE::REG,
1);
add_csr(psw_orm_0, "psw_orm_sram_log_uerr_addr", psw_orm_sram_log_uerr_addr_prop);
 // END psw_orm 
}
{
 // BEGIN psw_irm 
auto psw_irm_0 = nu_rng[0].add_an({"psw_irm"}, 0x9300000, 1, 0x0);
fld_map_t psw_irm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_irm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_timeout_thresh_cfg", psw_irm_timeout_thresh_cfg_prop);
fld_map_t psw_irm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_irm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_timedout_sta", psw_irm_timedout_sta_prop);
fld_map_t psw_irm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_irm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_timeout_clr", psw_irm_timeout_clr_prop);
fld_map_t psw_irm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_irm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_features", psw_irm_features_prop);
fld_map_t psw_irm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_irm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_spare_pio", psw_irm_spare_pio_prop);
fld_map_t psw_irm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_irm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_scratchpad", psw_irm_scratchpad_prop);
fld_map_t psw_irm_glb_sh_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_irm_glb_sh_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_glb_sh_cnt),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_glb_sh_cnt", psw_irm_glb_sh_cnt_prop);
fld_map_t psw_irm_cfg_glb_sh_thr {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("clear_hwm", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_irm_cfg_glb_sh_thr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_glb_sh_thr),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_glb_sh_thr", psw_irm_cfg_glb_sh_thr_prop);
fld_map_t psw_irm_glb_hdrm_cnt {
CREATE_ENTRY("curr_val", 0, 14),
CREATE_ENTRY("hwm_val", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto psw_irm_glb_hdrm_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_glb_hdrm_cnt),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_glb_hdrm_cnt", psw_irm_glb_hdrm_cnt_prop);
fld_map_t psw_irm_cfg_glb_hdrm_thr {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("clear_hwm", 14, 1),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_irm_cfg_glb_hdrm_thr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_glb_hdrm_thr),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_glb_hdrm_thr", psw_irm_cfg_glb_hdrm_thr_prop);
fld_map_t psw_irm_cfg_glb_sh_xon_thr {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto psw_irm_cfg_glb_sh_xon_thr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_glb_sh_xon_thr),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_glb_sh_xon_thr", psw_irm_cfg_glb_sh_xon_thr_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_0 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_0),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_0", psw_irm_cfg_pri_to_pg_fp_0_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_1 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_1),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_1", psw_irm_cfg_pri_to_pg_fp_1_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_2 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_2),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_2", psw_irm_cfg_pri_to_pg_fp_2_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_3 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_3),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_3", psw_irm_cfg_pri_to_pg_fp_3_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_4 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_4),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_4", psw_irm_cfg_pri_to_pg_fp_4_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_5 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_5),
0xD0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_5", psw_irm_cfg_pri_to_pg_fp_5_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_6 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_6),
0xD8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_6", psw_irm_cfg_pri_to_pg_fp_6_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_7 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_7),
0xE0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_7", psw_irm_cfg_pri_to_pg_fp_7_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_8 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_8),
0xE8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_8", psw_irm_cfg_pri_to_pg_fp_8_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_9 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_9),
0xF0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_9", psw_irm_cfg_pri_to_pg_fp_9_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_10 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_10),
0xF8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_10", psw_irm_cfg_pri_to_pg_fp_10_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_11 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_11),
0x100,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_11", psw_irm_cfg_pri_to_pg_fp_11_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_12 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_12),
0x108,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_12", psw_irm_cfg_pri_to_pg_fp_12_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_13 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_13),
0x110,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_13", psw_irm_cfg_pri_to_pg_fp_13_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_14 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_14),
0x118,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_14", psw_irm_cfg_pri_to_pg_fp_14_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_15 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_15),
0x120,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_15", psw_irm_cfg_pri_to_pg_fp_15_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_16 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_16),
0x128,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_16", psw_irm_cfg_pri_to_pg_fp_16_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_17 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_17),
0x130,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_17", psw_irm_cfg_pri_to_pg_fp_17_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_18 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_18),
0x138,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_18", psw_irm_cfg_pri_to_pg_fp_18_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_19 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_19),
0x140,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_19", psw_irm_cfg_pri_to_pg_fp_19_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_20 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_20),
0x148,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_20", psw_irm_cfg_pri_to_pg_fp_20_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_21 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_21),
0x150,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_21", psw_irm_cfg_pri_to_pg_fp_21_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_22 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_22),
0x158,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_22", psw_irm_cfg_pri_to_pg_fp_22_prop);
fld_map_t psw_irm_cfg_pri_to_pg_fp_23 {
CREATE_ENTRY("pri0", 0, 4),
CREATE_ENTRY("pri1", 4, 4),
CREATE_ENTRY("pri2", 8, 4),
CREATE_ENTRY("pri3", 12, 4),
CREATE_ENTRY("pri4", 16, 4),
CREATE_ENTRY("pri5", 20, 4),
CREATE_ENTRY("pri6", 24, 4),
CREATE_ENTRY("pri7", 28, 4),
CREATE_ENTRY("pri8", 32, 4),
CREATE_ENTRY("pri9", 36, 4),
CREATE_ENTRY("pri10", 40, 4),
CREATE_ENTRY("pri11", 44, 4),
CREATE_ENTRY("pri12", 48, 4),
CREATE_ENTRY("pri13", 52, 4),
CREATE_ENTRY("pri14", 56, 4),
CREATE_ENTRY("pri15", 60, 4)
};auto psw_irm_cfg_pri_to_pg_fp_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp_23),
0x160,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp_23", psw_irm_cfg_pri_to_pg_fp_23_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_0 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_0),
0x168,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_0", psw_irm_cfg_pri_to_pg_ep_0_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_1 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_1),
0x170,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_1", psw_irm_cfg_pri_to_pg_ep_1_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_2 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_2),
0x178,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_2", psw_irm_cfg_pri_to_pg_ep_2_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_3 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_3),
0x180,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_3", psw_irm_cfg_pri_to_pg_ep_3_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_4 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_4),
0x188,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_4", psw_irm_cfg_pri_to_pg_ep_4_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_5 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_5),
0x190,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_5", psw_irm_cfg_pri_to_pg_ep_5_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_6 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_6_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_6),
0x198,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_6", psw_irm_cfg_pri_to_pg_ep_6_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_7 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_7_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_7),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_7", psw_irm_cfg_pri_to_pg_ep_7_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_8 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_8_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_8),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_8", psw_irm_cfg_pri_to_pg_ep_8_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_9 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_9_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_9),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_9", psw_irm_cfg_pri_to_pg_ep_9_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_10 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_10_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_10),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_10", psw_irm_cfg_pri_to_pg_ep_10_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_11 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_11_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_11),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_11", psw_irm_cfg_pri_to_pg_ep_11_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_12 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_12_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_12),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_12", psw_irm_cfg_pri_to_pg_ep_12_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_13 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_13_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_13),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_13", psw_irm_cfg_pri_to_pg_ep_13_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_14 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_14_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_14),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_14", psw_irm_cfg_pri_to_pg_ep_14_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_15 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_15_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_15),
0x1E0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_15", psw_irm_cfg_pri_to_pg_ep_15_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_16 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_16_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_16),
0x1E8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_16", psw_irm_cfg_pri_to_pg_ep_16_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_17 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_17_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_17),
0x1F0,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_17", psw_irm_cfg_pri_to_pg_ep_17_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_18 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_18_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_18),
0x1F8,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_18", psw_irm_cfg_pri_to_pg_ep_18_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_19 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_19_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_19),
0x200,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_19", psw_irm_cfg_pri_to_pg_ep_19_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_20 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_20_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_20),
0x208,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_20", psw_irm_cfg_pri_to_pg_ep_20_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_21 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_21_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_21),
0x210,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_21", psw_irm_cfg_pri_to_pg_ep_21_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_22 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_22_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_22),
0x218,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_22", psw_irm_cfg_pri_to_pg_ep_22_prop);
fld_map_t psw_irm_cfg_pri_to_pg_ep_23 {
CREATE_ENTRY("pri0", 0, 3),
CREATE_ENTRY("pri1", 3, 3),
CREATE_ENTRY("pri2", 6, 3),
CREATE_ENTRY("pri3", 9, 3),
CREATE_ENTRY("pri4", 12, 3),
CREATE_ENTRY("pri5", 15, 3),
CREATE_ENTRY("pri6", 18, 3),
CREATE_ENTRY("pri7", 21, 3),
CREATE_ENTRY("__rsvd", 24, 40)
};auto psw_irm_cfg_pri_to_pg_ep_23_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep_23),
0x220,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep_23", psw_irm_cfg_pri_to_pg_ep_23_prop);
fld_map_t psw_irm_cfg_pfc_en {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_irm_cfg_pfc_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_pfc_en),
0x228,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_pfc_en", psw_irm_cfg_pfc_en_prop);
fld_map_t psw_irm_cfg_use_hdrm_after_xoff {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_irm_cfg_use_hdrm_after_xoff_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_cfg_use_hdrm_after_xoff),
0x230,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_cfg_use_hdrm_after_xoff", psw_irm_cfg_use_hdrm_after_xoff_prop);
fld_map_t psw_irm_sram_err_inj_cfg {
CREATE_ENTRY("stats_pg_peak_cnt", 0, 1),
CREATE_ENTRY("stats_pg_drop_cnt", 1, 1),
CREATE_ENTRY("pg_cnt_inst3", 2, 1),
CREATE_ENTRY("pg_cnt_inst2", 3, 1),
CREATE_ENTRY("pg_cnt_inst1", 4, 1),
CREATE_ENTRY("pg_cnt_inst0", 5, 1),
CREATE_ENTRY("deq_pg_cfg", 6, 1),
CREATE_ENTRY("enq_pg_cfg", 7, 1),
CREATE_ENTRY("err_type", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto psw_irm_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_err_inj_cfg),
0x238,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_err_inj_cfg", psw_irm_sram_err_inj_cfg_prop);
fld_map_t psw_irm_sram_log_cerr_vec {
CREATE_ENTRY("stats_pg_peak_cnt", 0, 1),
CREATE_ENTRY("stats_pg_drop_cnt", 1, 1),
CREATE_ENTRY("pg_cnt_inst3", 2, 1),
CREATE_ENTRY("pg_cnt_inst2", 3, 1),
CREATE_ENTRY("pg_cnt_inst1", 4, 1),
CREATE_ENTRY("pg_cnt_inst0", 5, 1),
CREATE_ENTRY("deq_pg_cfg", 6, 1),
CREATE_ENTRY("enq_pg_cfg", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_irm_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_log_cerr_vec),
0x240,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_log_cerr_vec", psw_irm_sram_log_cerr_vec_prop);
fld_map_t psw_irm_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_irm_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_log_cerr_syndrome),
0x248,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_log_cerr_syndrome", psw_irm_sram_log_cerr_syndrome_prop);
fld_map_t psw_irm_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_irm_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_log_cerr_addr),
0x250,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_log_cerr_addr", psw_irm_sram_log_cerr_addr_prop);
fld_map_t psw_irm_sram_log_uerr_vec {
CREATE_ENTRY("stats_pg_peak_cnt", 0, 1),
CREATE_ENTRY("stats_pg_drop_cnt", 1, 1),
CREATE_ENTRY("pg_cnt_inst3", 2, 1),
CREATE_ENTRY("pg_cnt_inst2", 3, 1),
CREATE_ENTRY("pg_cnt_inst1", 4, 1),
CREATE_ENTRY("pg_cnt_inst0", 5, 1),
CREATE_ENTRY("deq_pg_cfg", 6, 1),
CREATE_ENTRY("enq_pg_cfg", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_irm_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_log_uerr_vec),
0x258,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_log_uerr_vec", psw_irm_sram_log_uerr_vec_prop);
fld_map_t psw_irm_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_irm_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_log_uerr_syndrome),
0x260,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_log_uerr_syndrome", psw_irm_sram_log_uerr_syndrome_prop);
fld_map_t psw_irm_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_irm_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_irm_sram_log_uerr_addr),
0x268,
CSR_TYPE::REG,
1);
add_csr(psw_irm_0, "psw_irm_sram_log_uerr_addr", psw_irm_sram_log_uerr_addr_prop);
 // END psw_irm 
}
{
 // BEGIN psw_wred 
auto psw_wred_0 = nu_rng[0].add_an({"psw_wred"}, 0x9380000, 1, 0x0);
fld_map_t psw_wred_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_wred_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_timeout_thresh_cfg", psw_wred_timeout_thresh_cfg_prop);
fld_map_t psw_wred_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_wred_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_timedout_sta", psw_wred_timedout_sta_prop);
fld_map_t psw_wred_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_wred_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_timeout_clr", psw_wred_timeout_clr_prop);
fld_map_t psw_wred_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_wred_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_features", psw_wred_features_prop);
fld_map_t psw_wred_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_wred_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_spare_pio", psw_wred_spare_pio_prop);
fld_map_t psw_wred_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_wred_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_scratchpad", psw_wred_scratchpad_prop);
fld_map_t psw_wred_cfg_avg_q {
CREATE_ENTRY("period", 0, 16),
CREATE_ENTRY("avg_en", 16, 1),
CREATE_ENTRY("cap_avg_size", 17, 1),
CREATE_ENTRY("__rsvd", 18, 46)
};auto psw_wred_cfg_avg_q_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_cfg_avg_q),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_cfg_avg_q", psw_wred_cfg_avg_q_prop);
fld_map_t psw_wred_cfg_ecn_glb_sh_thresh {
CREATE_ENTRY("red", 0, 15),
CREATE_ENTRY("yellow", 15, 15),
CREATE_ENTRY("green", 30, 15),
CREATE_ENTRY("en", 45, 1),
CREATE_ENTRY("__rsvd", 46, 18)
};auto psw_wred_cfg_ecn_glb_sh_thresh_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_cfg_ecn_glb_sh_thresh),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_cfg_ecn_glb_sh_thresh", psw_wred_cfg_ecn_glb_sh_thresh_prop);
fld_map_t psw_wred_cfg_stats_color_en {
CREATE_ENTRY("green", 0, 1),
CREATE_ENTRY("yellow", 1, 1),
CREATE_ENTRY("red", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_wred_cfg_stats_color_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_cfg_stats_color_en),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_cfg_stats_color_en", psw_wred_cfg_stats_color_en_prop);
fld_map_t psw_wred_sram_err_inj_cfg {
CREATE_ENTRY("stats_q_ecn_cnt", 0, 1),
CREATE_ENTRY("stats_q_drop_cnt", 1, 1),
CREATE_ENTRY("deq_prob", 2, 1),
CREATE_ENTRY("deq_profile", 3, 1),
CREATE_ENTRY("deq_q_cfg", 4, 1),
CREATE_ENTRY("enq_prob", 5, 1),
CREATE_ENTRY("enq_profile", 6, 1),
CREATE_ENTRY("enq_q_cfg", 7, 1),
CREATE_ENTRY("enq_q_cnt", 8, 1),
CREATE_ENTRY("avg_q_cfg", 9, 1),
CREATE_ENTRY("avg_q_cnt", 10, 1),
CREATE_ENTRY("err_type", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto psw_wred_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_err_inj_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_err_inj_cfg", psw_wred_sram_err_inj_cfg_prop);
fld_map_t psw_wred_sram_log_cerr_vec {
CREATE_ENTRY("stats_q_ecn_cnt", 0, 1),
CREATE_ENTRY("stats_q_drop_cnt", 1, 1),
CREATE_ENTRY("deq_prob", 2, 1),
CREATE_ENTRY("deq_profile", 3, 1),
CREATE_ENTRY("deq_q_cfg", 4, 1),
CREATE_ENTRY("enq_prob", 5, 1),
CREATE_ENTRY("enq_profile", 6, 1),
CREATE_ENTRY("enq_q_cfg", 7, 1),
CREATE_ENTRY("enq_q_cnt", 8, 1),
CREATE_ENTRY("avg_q_cfg", 9, 1),
CREATE_ENTRY("avg_q_cnt", 10, 1),
CREATE_ENTRY("__rsvd", 11, 53)
};auto psw_wred_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_log_cerr_vec),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_log_cerr_vec", psw_wred_sram_log_cerr_vec_prop);
fld_map_t psw_wred_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_wred_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_log_cerr_syndrome),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_log_cerr_syndrome", psw_wred_sram_log_cerr_syndrome_prop);
fld_map_t psw_wred_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_wred_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_log_cerr_addr),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_log_cerr_addr", psw_wred_sram_log_cerr_addr_prop);
fld_map_t psw_wred_sram_log_uerr_vec {
CREATE_ENTRY("stats_q_ecn_cnt", 0, 1),
CREATE_ENTRY("stats_q_drop_cnt", 1, 1),
CREATE_ENTRY("deq_prob", 2, 1),
CREATE_ENTRY("deq_profile", 3, 1),
CREATE_ENTRY("deq_q_cfg", 4, 1),
CREATE_ENTRY("enq_prob", 5, 1),
CREATE_ENTRY("enq_profile", 6, 1),
CREATE_ENTRY("enq_q_cfg", 7, 1),
CREATE_ENTRY("enq_q_cnt", 8, 1),
CREATE_ENTRY("avg_q_cfg", 9, 1),
CREATE_ENTRY("avg_q_cnt", 10, 1),
CREATE_ENTRY("__rsvd", 11, 53)
};auto psw_wred_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_log_uerr_vec),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_log_uerr_vec", psw_wred_sram_log_uerr_vec_prop);
fld_map_t psw_wred_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_wred_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_log_uerr_syndrome),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_log_uerr_syndrome", psw_wred_sram_log_uerr_syndrome_prop);
fld_map_t psw_wred_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_wred_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_wred_sram_log_uerr_addr),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_wred_0, "psw_wred_sram_log_uerr_addr", psw_wred_sram_log_uerr_addr_prop);
 // END psw_wred 
}
{
 // BEGIN psw_clm 
auto psw_clm_0 = nu_rng[0].add_an({"psw_clm"}, 0x9400000, 1, 0x0);
fld_map_t psw_clm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_clm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_timeout_thresh_cfg", psw_clm_timeout_thresh_cfg_prop);
fld_map_t psw_clm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_clm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_timedout_sta", psw_clm_timedout_sta_prop);
fld_map_t psw_clm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_clm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_timeout_clr", psw_clm_timeout_clr_prop);
fld_map_t psw_clm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_clm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_features", psw_clm_features_prop);
fld_map_t psw_clm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_clm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_spare_pio", psw_clm_spare_pio_prop);
fld_map_t psw_clm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_clm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_scratchpad", psw_clm_scratchpad_prop);
fld_map_t psw_clm_mem_init_start_cfg {
CREATE_ENTRY("clm_link", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_clm_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_mem_init_start_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_mem_init_start_cfg", psw_clm_mem_init_start_cfg_prop);
fld_map_t psw_clm_mem_init_done_status {
CREATE_ENTRY("clm_link", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_clm_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_mem_init_done_status),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_mem_init_done_status", psw_clm_mem_init_done_status_prop);
fld_map_t psw_clm_sram_err_inj_cfg {
CREATE_ENTRY("pbuf_ucell3", 0, 1),
CREATE_ENTRY("pbuf_ucell2", 1, 1),
CREATE_ENTRY("pbuf_ucell1", 2, 1),
CREATE_ENTRY("pbuf_ucell0", 3, 1),
CREATE_ENTRY("link", 4, 1),
CREATE_ENTRY("err_type", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_clm_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_err_inj_cfg),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_err_inj_cfg", psw_clm_sram_err_inj_cfg_prop);
fld_map_t psw_clm_sram_log_cerr_vec {
CREATE_ENTRY("pbuf_ucell3", 0, 1),
CREATE_ENTRY("pbuf_ucell2", 1, 1),
CREATE_ENTRY("pbuf_ucell1", 2, 1),
CREATE_ENTRY("pbuf_ucell0", 3, 1),
CREATE_ENTRY("link", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto psw_clm_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_log_cerr_vec),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_log_cerr_vec", psw_clm_sram_log_cerr_vec_prop);
fld_map_t psw_clm_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_clm_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_log_cerr_syndrome),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_log_cerr_syndrome", psw_clm_sram_log_cerr_syndrome_prop);
fld_map_t psw_clm_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_clm_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_log_cerr_addr),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_log_cerr_addr", psw_clm_sram_log_cerr_addr_prop);
fld_map_t psw_clm_sram_log_uerr_vec {
CREATE_ENTRY("pbuf_ucell3", 0, 1),
CREATE_ENTRY("pbuf_ucell2", 1, 1),
CREATE_ENTRY("pbuf_ucell1", 2, 1),
CREATE_ENTRY("pbuf_ucell0", 3, 1),
CREATE_ENTRY("link", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto psw_clm_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_log_uerr_vec),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_log_uerr_vec", psw_clm_sram_log_uerr_vec_prop);
fld_map_t psw_clm_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_clm_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_log_uerr_syndrome),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_log_uerr_syndrome", psw_clm_sram_log_uerr_syndrome_prop);
fld_map_t psw_clm_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_clm_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_clm_sram_log_uerr_addr),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_clm_0, "psw_clm_sram_log_uerr_addr", psw_clm_sram_log_uerr_addr_prop);
 // END psw_clm 
}
{
 // BEGIN psw_pqm 
auto psw_pqm_0 = nu_rng[0].add_an({"psw_pqm"}, 0x9800000, 1, 0x0);
fld_map_t psw_pqm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_pqm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_timeout_thresh_cfg", psw_pqm_timeout_thresh_cfg_prop);
fld_map_t psw_pqm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pqm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_timedout_sta", psw_pqm_timedout_sta_prop);
fld_map_t psw_pqm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pqm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_timeout_clr", psw_pqm_timeout_clr_prop);
fld_map_t psw_pqm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_pqm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_features", psw_pqm_features_prop);
fld_map_t psw_pqm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_spare_pio", psw_pqm_spare_pio_prop);
fld_map_t psw_pqm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_scratchpad", psw_pqm_scratchpad_prop);
fld_map_t psw_pqm_mem_init_start_cfg {
CREATE_ENTRY("head_main", 0, 1),
CREATE_ENTRY("head_shd", 1, 1),
CREATE_ENTRY("tail_main", 2, 1),
CREATE_ENTRY("tail_shd", 3, 1),
CREATE_ENTRY("stats_q_deq_cntr", 4, 1),
CREATE_ENTRY("stats_pg_deq_cntr", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_pqm_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_init_start_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_mem_init_start_cfg", psw_pqm_mem_init_start_cfg_prop);
fld_map_t psw_pqm_mem_init_done_status {
CREATE_ENTRY("head_main", 0, 1),
CREATE_ENTRY("head_shd", 1, 1),
CREATE_ENTRY("tail_main", 2, 1),
CREATE_ENTRY("tail_shd", 3, 1),
CREATE_ENTRY("stats_q_deq_cntr", 4, 1),
CREATE_ENTRY("stats_pg_deq_cntr", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_pqm_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_init_done_status),
0x88,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_mem_init_done_status", psw_pqm_mem_init_done_status_prop);
fld_map_t psw_pqm_sram_err_inj_cfg {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("err_type", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto psw_pqm_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_err_inj_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_err_inj_cfg", psw_pqm_sram_err_inj_cfg_prop);
fld_map_t psw_pqm_sram_log_cerr_vec {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_cerr_vec),
0xE8,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_log_cerr_vec", psw_pqm_sram_log_cerr_vec_prop);
fld_map_t psw_pqm_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_cerr_syndrome),
0xF0,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_log_cerr_syndrome", psw_pqm_sram_log_cerr_syndrome_prop);
fld_map_t psw_pqm_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_cerr_addr),
0xF8,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_log_cerr_addr", psw_pqm_sram_log_cerr_addr_prop);
fld_map_t psw_pqm_sram_log_uerr_vec {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_uerr_vec),
0x100,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_log_uerr_vec", psw_pqm_sram_log_uerr_vec_prop);
fld_map_t psw_pqm_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_uerr_syndrome),
0x108,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_log_uerr_syndrome", psw_pqm_sram_log_uerr_syndrome_prop);
fld_map_t psw_pqm_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_uerr_addr),
0x110,
CSR_TYPE::REG,
1);
add_csr(psw_pqm_0, "psw_pqm_sram_log_uerr_addr", psw_pqm_sram_log_uerr_addr_prop);
 // END psw_pqm 
}
{
 // BEGIN psw_cfp 
auto psw_cfp_0 = nu_rng[0].add_an({"psw_cfp"}, 0xA000000, 1, 0x0);
fld_map_t psw_cfp_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_timeout_thresh_cfg", psw_cfp_timeout_thresh_cfg_prop);
fld_map_t psw_cfp_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_timedout_sta", psw_cfp_timedout_sta_prop);
fld_map_t psw_cfp_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_timeout_clr", psw_cfp_timeout_clr_prop);
fld_map_t psw_cfp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_cfp_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_features),
0x90,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_features", psw_cfp_features_prop);
fld_map_t psw_cfp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_cfp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_spare_pio),
0x98,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_spare_pio", psw_cfp_spare_pio_prop);
fld_map_t psw_cfp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_cfp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_scratchpad),
0xA0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_scratchpad", psw_cfp_scratchpad_prop);
fld_map_t psw_cfp_mem_init_start_cfg {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_mem_init_start_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_mem_init_start_cfg", psw_cfp_mem_init_start_cfg_prop);
fld_map_t psw_cfp_mem_init_done_status {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_mem_init_done_status),
0xB0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_mem_init_done_status", psw_cfp_mem_init_done_status_prop);
fld_map_t psw_cfp_cnt {
CREATE_ENTRY("curr_val", 0, 15),
CREATE_ENTRY("hwm_val", 15, 15),
CREATE_ENTRY("__rsvd", 30, 34)
};auto psw_cfp_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_cnt),
0xB8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_cnt", psw_cfp_cnt_prop);
fld_map_t psw_cfp_cfg_clear_hwm {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_cfg_clear_hwm_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_cfg_clear_hwm),
0xC0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_cfg_clear_hwm", psw_cfp_cfg_clear_hwm_prop);
fld_map_t psw_cfp_sram_err_inj_cfg {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("err_type", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_cfp_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_err_inj_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_err_inj_cfg", psw_cfp_sram_err_inj_cfg_prop);
fld_map_t psw_cfp_sram_log_cerr_vec {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_cerr_vec),
0xD0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_log_cerr_vec", psw_cfp_sram_log_cerr_vec_prop);
fld_map_t psw_cfp_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_cerr_syndrome),
0xD8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_log_cerr_syndrome", psw_cfp_sram_log_cerr_syndrome_prop);
fld_map_t psw_cfp_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_cerr_addr),
0xE0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_log_cerr_addr", psw_cfp_sram_log_cerr_addr_prop);
fld_map_t psw_cfp_sram_log_uerr_vec {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_uerr_vec),
0xE8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_log_uerr_vec", psw_cfp_sram_log_uerr_vec_prop);
fld_map_t psw_cfp_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_uerr_syndrome),
0xF0,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_log_uerr_syndrome", psw_cfp_sram_log_uerr_syndrome_prop);
fld_map_t psw_cfp_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_uerr_addr),
0xF8,
CSR_TYPE::REG,
1);
add_csr(psw_cfp_0, "psw_cfp_sram_log_uerr_addr", psw_cfp_sram_log_uerr_addr_prop);
 // END psw_cfp 
}
{
 // BEGIN etdp 
auto etdp_0 = nu_rng[0].add_an({"etdp"}, 0xA080000, 3, 0x100000);
fld_map_t etdp_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto etdp_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_timeout_thresh_cfg", etdp_timeout_thresh_cfg_prop);
fld_map_t etdp_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etdp_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_timedout_sta", etdp_timedout_sta_prop);
fld_map_t etdp_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etdp_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_timeout_clr", etdp_timeout_clr_prop);
fld_map_t etdp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto etdp_features_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_features", etdp_features_prop);
fld_map_t etdp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto etdp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_spare_pio", etdp_spare_pio_prop);
fld_map_t etdp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto etdp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_scratchpad", etdp_scratchpad_prop);
fld_map_t etdp_cfg {
CREATE_ENTRY("fcp_hdr_udp_sport_ctrl", 0, 2),
CREATE_ENTRY("pswif_xmt_halt", 2, 1),
CREATE_ENTRY("lso_only_pkt_ctrl", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto etdp_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_cfg", etdp_cfg_prop);
fld_map_t etdp_instance_number {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto etdp_instance_number_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_instance_number),
0x88,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_instance_number", etdp_instance_number_prop);
fld_map_t etdp_fcp_data_blk_sz_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto etdp_fcp_data_blk_sz_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_fcp_data_blk_sz_cfg),
0x90,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_fcp_data_blk_sz_cfg", etdp_fcp_data_blk_sz_cfg_prop);
fld_map_t etdp_pkt_sz_adj {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etdp_pkt_sz_adj_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_pkt_sz_adj),
0x98,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_pkt_sz_adj", etdp_pkt_sz_adj_prop);
fld_map_t etdp_fpkt_tcp_flags {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etdp_fpkt_tcp_flags_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_fpkt_tcp_flags),
0xA0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_fpkt_tcp_flags", etdp_fpkt_tcp_flags_prop);
fld_map_t etdp_lpkt_tcp_flags {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etdp_lpkt_tcp_flags_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_lpkt_tcp_flags),
0xA8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_lpkt_tcp_flags", etdp_lpkt_tcp_flags_prop);
fld_map_t etdp_mpkt_tcp_flags {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etdp_mpkt_tcp_flags_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_mpkt_tcp_flags),
0xB0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_mpkt_tcp_flags", etdp_mpkt_tcp_flags_prop);
fld_map_t fcp_cfg {
CREATE_ENTRY("gph_size", 0, 2),
CREATE_ENTRY("fcp_qos_count", 2, 2),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fcp_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_cfg),
0xB8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_cfg", fcp_cfg_prop);
fld_map_t fcp_hdr_dmac {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcp_hdr_dmac_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_dmac),
0xC0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_dmac", fcp_hdr_dmac_prop);
fld_map_t fcp_hdr_smac {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fcp_hdr_smac_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_smac),
0xC8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_smac", fcp_hdr_smac_prop);
fld_map_t fcp_hdr_v4_etype {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcp_hdr_v4_etype_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_v4_etype),
0xD0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_v4_etype", fcp_hdr_v4_etype_prop);
fld_map_t fcp_hdr_req_dscp_ecn {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_req_dscp_ecn_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_req_dscp_ecn),
0xD8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_req_dscp_ecn", fcp_hdr_req_dscp_ecn_prop);
fld_map_t fcp_hdr_gnt_dscp_ecn {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_gnt_dscp_ecn_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_gnt_dscp_ecn),
0xE0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_gnt_dscp_ecn", fcp_hdr_gnt_dscp_ecn_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q0 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q0_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q0),
0xE8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q0", fcp_hdr_data_dscp_ecn_q0_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q1 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q1_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q1),
0xF0,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q1", fcp_hdr_data_dscp_ecn_q1_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q2 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q2_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q2),
0xF8,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q2", fcp_hdr_data_dscp_ecn_q2_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q3 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q3_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q3),
0x100,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q3", fcp_hdr_data_dscp_ecn_q3_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q4 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q4_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q4),
0x108,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q4", fcp_hdr_data_dscp_ecn_q4_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q5 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q5_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q5),
0x110,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q5", fcp_hdr_data_dscp_ecn_q5_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q6 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q6_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q6),
0x118,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q6", fcp_hdr_data_dscp_ecn_q6_prop);
fld_map_t fcp_hdr_data_dscp_ecn_q7 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_data_dscp_ecn_q7_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q7),
0x120,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q7", fcp_hdr_data_dscp_ecn_q7_prop);
fld_map_t fcp_hdr_ipv4_id {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcp_hdr_ipv4_id_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_ipv4_id),
0x128,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_ipv4_id", fcp_hdr_ipv4_id_prop);
fld_map_t fcp_hdr_frag_flags_offset {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcp_hdr_frag_flags_offset_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_frag_flags_offset),
0x130,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_frag_flags_offset", fcp_hdr_frag_flags_offset_prop);
fld_map_t fcp_hdr_ipv4_ttl {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_hdr_ipv4_ttl_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_ipv4_ttl),
0x138,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_ipv4_ttl", fcp_hdr_ipv4_ttl_prop);
fld_map_t udp_over_ipv4_proto {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto udp_over_ipv4_proto_prop = csr_prop_t(
std::make_shared<csr_s>(udp_over_ipv4_proto),
0x140,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "udp_over_ipv4_proto", udp_over_ipv4_proto_prop);
fld_map_t fcp_over_ipv4_proto {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fcp_over_ipv4_proto_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_over_ipv4_proto),
0x148,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_over_ipv4_proto", fcp_over_ipv4_proto_prop);
fld_map_t fcp_hdr_ipv4_sip {
CREATE_ENTRY("val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fcp_hdr_ipv4_sip_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_ipv4_sip),
0x150,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_ipv4_sip", fcp_hdr_ipv4_sip_prop);
fld_map_t fcp_hdr_udp_dport {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcp_hdr_udp_dport_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_udp_dport),
0x158,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_udp_dport", fcp_hdr_udp_dport_prop);
fld_map_t fcp_hdr_udp_csum {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fcp_hdr_udp_csum_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_udp_csum),
0x160,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_udp_csum", fcp_hdr_udp_csum_prop);
fld_map_t fcp_hdr_ver {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fcp_hdr_ver_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_ver),
0x168,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_ver", fcp_hdr_ver_prop);
fld_map_t fcp_hdr_rsvd {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fcp_hdr_rsvd_prop = csr_prop_t(
std::make_shared<csr_s>(fcp_hdr_rsvd),
0x170,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "fcp_hdr_rsvd", fcp_hdr_rsvd_prop);
fld_map_t etdp_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etdp_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_fla_ring_module_id_cfg),
0x178,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_fla_ring_module_id_cfg", etdp_fla_ring_module_id_cfg_prop);
fld_map_t etdp_key_lu_63_0 {
CREATE_ENTRY("key", 0, 64)
};auto etdp_key_lu_63_0_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_key_lu_63_0),
0x180,
CSR_TYPE::REG_LST,
1);
add_csr(etdp_0, "etdp_key_lu_63_0", etdp_key_lu_63_0_prop);
fld_map_t etdp_key_lu_127_64 {
CREATE_ENTRY("key", 0, 64)
};auto etdp_key_lu_127_64_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_key_lu_127_64),
0x208,
CSR_TYPE::REG_LST,
1);
add_csr(etdp_0, "etdp_key_lu_127_64", etdp_key_lu_127_64_prop);
fld_map_t etdp_key_lu_191_128 {
CREATE_ENTRY("key", 0, 64)
};auto etdp_key_lu_191_128_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_key_lu_191_128),
0x290,
CSR_TYPE::REG_LST,
1);
add_csr(etdp_0, "etdp_key_lu_191_128", etdp_key_lu_191_128_prop);
fld_map_t etdp_key_lu_255_192 {
CREATE_ENTRY("key", 0, 64)
};auto etdp_key_lu_255_192_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_key_lu_255_192),
0x318,
CSR_TYPE::REG_LST,
1);
add_csr(etdp_0, "etdp_key_lu_255_192", etdp_key_lu_255_192_prop);
fld_map_t etdp_key_len_lu {
CREATE_ENTRY("key_len", 0, 2),
CREATE_ENTRY("salt", 2, 16),
CREATE_ENTRY("__rsvd", 18, 46)
};auto etdp_key_len_lu_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_key_len_lu),
0x3A0,
CSR_TYPE::REG_LST,
1);
add_csr(etdp_0, "etdp_key_len_lu", etdp_key_len_lu_prop);
fld_map_t etdp_fcp_stream_map {
CREATE_ENTRY("fcp_stream", 0, 3),
CREATE_ENTRY("fcp_present", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto etdp_fcp_stream_map_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_fcp_stream_map),
0x428,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_fcp_stream_map", etdp_fcp_stream_map_prop);
fld_map_t etdp_sram_err_inj_cfg {
CREATE_ENTRY("pswif_mem", 0, 1),
CREATE_ENTRY("tmem", 1, 1),
CREATE_ENTRY("lso_hmem_i1_b1", 2, 1),
CREATE_ENTRY("lso_hmem_i1_b0", 3, 1),
CREATE_ENTRY("lso_hmem_i0_b1", 4, 1),
CREATE_ENTRY("lso_hmem_i0_b0", 5, 1),
CREATE_ENTRY("lso_pmem", 6, 1),
CREATE_ENTRY("err_type", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etdp_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_sram_err_inj_cfg),
0x430,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_sram_err_inj_cfg", etdp_sram_err_inj_cfg_prop);
fld_map_t etdp_sram_cerr_log_vec {
CREATE_ENTRY("pswif_mem", 0, 1),
CREATE_ENTRY("tmem", 1, 1),
CREATE_ENTRY("lso_hmem_i1_b1", 2, 1),
CREATE_ENTRY("lso_hmem_i1_b0", 3, 1),
CREATE_ENTRY("lso_hmem_i0_b1", 4, 1),
CREATE_ENTRY("lso_hmem_i0_b0", 5, 1),
CREATE_ENTRY("lso_pmem", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto etdp_sram_cerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_sram_cerr_log_vec),
0x438,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_sram_cerr_log_vec", etdp_sram_cerr_log_vec_prop);
fld_map_t etdp_sram_ucerr_log_vec {
CREATE_ENTRY("pswif_mem", 0, 1),
CREATE_ENTRY("tmem", 1, 1),
CREATE_ENTRY("lso_hmem_i1_b1", 2, 1),
CREATE_ENTRY("lso_hmem_i1_b0", 3, 1),
CREATE_ENTRY("lso_hmem_i0_b1", 4, 1),
CREATE_ENTRY("lso_hmem_i0_b0", 5, 1),
CREATE_ENTRY("lso_pmem", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto etdp_sram_ucerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_sram_ucerr_log_vec),
0x440,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_sram_ucerr_log_vec", etdp_sram_ucerr_log_vec_prop);
fld_map_t etdp_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto etdp_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_sram_log_syndrome),
0x448,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_sram_log_syndrome", etdp_sram_log_syndrome_prop);
fld_map_t etdp_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto etdp_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_sram_log_addr),
0x450,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_sram_log_addr", etdp_sram_log_addr_prop);
fld_map_t etdp_wus_eot {
CREATE_ENTRY("val", 0, 64)
};auto etdp_wus_eot_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_wus_eot),
0x458,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_wus_eot", etdp_wus_eot_prop);
fld_map_t etdp_lso_eot {
CREATE_ENTRY("val", 0, 64)
};auto etdp_lso_eot_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_lso_eot),
0x460,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_lso_eot", etdp_lso_eot_prop);
fld_map_t etdp_fcp_eot {
CREATE_ENTRY("val", 0, 64)
};auto etdp_fcp_eot_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_fcp_eot),
0x468,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_fcp_eot", etdp_fcp_eot_prop);
fld_map_t etdp_pswif_eot {
CREATE_ENTRY("val", 0, 64)
};auto etdp_pswif_eot_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_pswif_eot),
0x470,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_pswif_eot", etdp_pswif_eot_prop);
fld_map_t etdp_status {
CREATE_ENTRY("ready_to_reset", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etdp_status_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_status),
0x478,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_status", etdp_status_prop);
fld_map_t etdp_watchdog_timer_period {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto etdp_watchdog_timer_period_prop = csr_prop_t(
std::make_shared<csr_s>(etdp_watchdog_timer_period),
0x488,
CSR_TYPE::REG,
1);
add_csr(etdp_0, "etdp_watchdog_timer_period", etdp_watchdog_timer_period_prop);
 // END etdp 
}
{
 // BEGIN etfp 
auto etfp_0 = nu_rng[0].add_an({"etfp"}, 0xA800000, 1, 0x0);
fld_map_t etfp_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto etfp_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_timeout_thresh_cfg", etfp_timeout_thresh_cfg_prop);
fld_map_t etfp_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etfp_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_timedout_sta", etfp_timedout_sta_prop);
fld_map_t etfp_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etfp_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_timeout_clr", etfp_timeout_clr_prop);
fld_map_t etfp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto etfp_features_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_features", etfp_features_prop);
fld_map_t etfp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto etfp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_spare_pio", etfp_spare_pio_prop);
fld_map_t etfp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto etfp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_scratchpad", etfp_scratchpad_prop);
fld_map_t etfp_cfg {
CREATE_ENTRY("fcp_sec_seq_num_ctrl", 0, 1),
CREATE_ENTRY("dis_gseq_num_check", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto etfp_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_cfg", etfp_cfg_prop);
fld_map_t etfp_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etfp_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_fla_ring_module_id_cfg),
0x88,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_fla_ring_module_id_cfg", etfp_fla_ring_module_id_cfg_prop);
fld_map_t etfp_sram_err_inj_cfg {
CREATE_ENTRY("fcp_dtunnel", 0, 1),
CREATE_ENTRY("fcp_dip", 1, 1),
CREATE_ENTRY("fcp_eainfo", 2, 1),
CREATE_ENTRY("fcp_psn", 3, 1),
CREATE_ENTRY("hdr_bf_inst0", 4, 1),
CREATE_ENTRY("hdr_bf_inst1", 5, 1),
CREATE_ENTRY("hdr_bf_inst2", 6, 1),
CREATE_ENTRY("err_type", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etfp_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_sram_err_inj_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_sram_err_inj_cfg", etfp_sram_err_inj_cfg_prop);
fld_map_t etfp_sram_cerr_log_vec {
CREATE_ENTRY("fcp_dtunnel", 0, 1),
CREATE_ENTRY("fcp_dip", 1, 1),
CREATE_ENTRY("fcp_eainfo", 2, 1),
CREATE_ENTRY("fcp_psn", 3, 1),
CREATE_ENTRY("hdr_bf_inst0", 4, 1),
CREATE_ENTRY("hdr_bf_inst1", 5, 1),
CREATE_ENTRY("hdr_bf_inst2", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto etfp_sram_cerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_sram_cerr_log_vec),
0xB0,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_sram_cerr_log_vec", etfp_sram_cerr_log_vec_prop);
fld_map_t etfp_sram_ucerr_log_vec {
CREATE_ENTRY("fcp_dtunnel", 0, 1),
CREATE_ENTRY("fcp_dip", 1, 1),
CREATE_ENTRY("fcp_eainfo", 2, 1),
CREATE_ENTRY("fcp_psn", 3, 1),
CREATE_ENTRY("hdr_bf_inst0", 4, 1),
CREATE_ENTRY("hdr_bf_inst1", 5, 1),
CREATE_ENTRY("hdr_bf_inst2", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto etfp_sram_ucerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_sram_ucerr_log_vec),
0xB8,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_sram_ucerr_log_vec", etfp_sram_ucerr_log_vec_prop);
fld_map_t etfp_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto etfp_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_sram_log_syndrome),
0xC0,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_sram_log_syndrome", etfp_sram_log_syndrome_prop);
fld_map_t etfp_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto etfp_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_sram_log_addr),
0xC8,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_sram_log_addr", etfp_sram_log_addr_prop);
fld_map_t etfp_qst_eot {
CREATE_ENTRY("val", 0, 64)
};auto etfp_qst_eot_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_qst_eot),
0xD0,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_qst_eot", etfp_qst_eot_prop);
fld_map_t etfp_prs_eot {
CREATE_ENTRY("val", 0, 64)
};auto etfp_prs_eot_prop = csr_prop_t(
std::make_shared<csr_s>(etfp_prs_eot),
0xD8,
CSR_TYPE::REG,
1);
add_csr(etfp_0, "etfp_prs_eot", etfp_prs_eot_prop);
 // END etfp 
}
{
 // BEGIN fae_prs 
auto fae_prs_0 = nu_rng[0].add_an({"fae_prs"}, 0xB000000, 1, 0x0);
fld_map_t fae_prs_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fae_prs_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_timeout_thresh_cfg", fae_prs_timeout_thresh_cfg_prop);
fld_map_t fae_prs_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fae_prs_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_timedout_sta", fae_prs_timedout_sta_prop);
fld_map_t fae_prs_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fae_prs_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_timeout_clr", fae_prs_timeout_clr_prop);
fld_map_t fae_prs_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fae_prs_features_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_features", fae_prs_features_prop);
fld_map_t fae_prs_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fae_prs_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_spare_pio", fae_prs_spare_pio_prop);
fld_map_t fae_prs_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fae_prs_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_scratchpad", fae_prs_scratchpad_prop);
fld_map_t fae_prs_sram_log_err {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_prs_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_sram_log_err),
0x80,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_sram_log_err", fae_prs_sram_log_err_prop);
fld_map_t fae_prs_sram_log_syndrome {
CREATE_ENTRY("val", 0, 10),
CREATE_ENTRY("__rsvd", 10, 54)
};auto fae_prs_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_sram_log_syndrome),
0x88,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_sram_log_syndrome", fae_prs_sram_log_syndrome_prop);
fld_map_t fae_prs_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto fae_prs_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_sram_log_addr),
0x90,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_sram_log_addr", fae_prs_sram_log_addr_prop);
fld_map_t fae_prs_mem_err_inj_cfg {
CREATE_ENTRY("prs_dsp_fifo_mem0", 0, 1),
CREATE_ENTRY("prs_rob_prv_mem", 1, 1),
CREATE_ENTRY("prs_action_mem0", 2, 1),
CREATE_ENTRY("prs_action_mem1", 3, 1),
CREATE_ENTRY("prs_action_mem2", 4, 1),
CREATE_ENTRY("prs_action_mem3", 5, 1),
CREATE_ENTRY("err_type", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto fae_prs_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fae_prs_mem_err_inj_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "fae_prs_mem_err_inj_cfg", fae_prs_mem_err_inj_cfg_prop);
fld_map_t prs_dsp_dfifo_mem_af_thold {
CREATE_ENTRY("data", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
fld_map_t prs_intf_cfg {
CREATE_ENTRY("intf0mode", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto prs_intf_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_intf_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_intf_cfg", prs_intf_cfg_prop);
fld_map_t prs_err_chk_en {
CREATE_ENTRY("outer_ipv4_checksum", 0, 1),
CREATE_ENTRY("inner_ipv4_checksum", 1, 1),
CREATE_ENTRY("no_tcam_match", 2, 1),
CREATE_ENTRY("parser_timeout", 3, 1),
CREATE_ENTRY("prv_oor", 4, 1),
CREATE_ENTRY("pkt_ptr_oor", 5, 1),
CREATE_ENTRY("hdr_buf_overflow", 6, 1),
CREATE_ENTRY("hdr_byte_oor", 7, 1),
CREATE_ENTRY("gp_byte_oor", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto prs_err_chk_en_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_chk_en),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_err_chk_en", prs_err_chk_en_prop);
fld_map_t prs_err_tcode0 {
CREATE_ENTRY("outer_ipv4_checksum", 0, 7),
CREATE_ENTRY("inner_ipv4_checksum", 7, 7),
CREATE_ENTRY("no_tcam_match", 14, 7),
CREATE_ENTRY("parser_timeout", 21, 7),
CREATE_ENTRY("prv_oor", 28, 7),
CREATE_ENTRY("pkt_ptr_oor", 35, 7),
CREATE_ENTRY("hdr_buf_overflow", 42, 7),
CREATE_ENTRY("hdr_byte_oor", 49, 7),
CREATE_ENTRY("__rsvd", 56, 8)
};auto prs_err_tcode0_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode0),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
fld_map_t prs_err_tcode1 {
CREATE_ENTRY("gp_byte_oor", 0, 7),
CREATE_ENTRY("action_mem_perr", 7, 7),
CREATE_ENTRY("__rsvd", 14, 50)
};auto prs_err_tcode1_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode1),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
fld_map_t prs_max_lu_cycle_cfg {
CREATE_ENTRY("use_fixed", 0, 1),
CREATE_ENTRY("fixed_cnt", 1, 8),
CREATE_ENTRY("init_cycle_cnt", 9, 6),
CREATE_ENTRY("acct_for_prv_bg_rd", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
fld_map_t prs_stream_cfg {
CREATE_ENTRY("fixed_stream_en", 0, 1),
CREATE_ENTRY("intf0_stream", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto prs_stream_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_stream_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
fld_map_t prs_static_ctx_sel {
CREATE_ENTRY("use_one_ctx", 0, 1),
CREATE_ENTRY("ctx_num", 1, 2),
CREATE_ENTRY("__rsvd", 3, 61)
};auto prs_static_ctx_sel_prop = csr_prop_t(
std::make_shared<csr_s>(prs_static_ctx_sel),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
fld_map_t prs_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
fld_map_t prs_hdb_fifo_empty {
CREATE_ENTRY("ctx0", 0, 1),
CREATE_ENTRY("ctx1", 1, 1),
CREATE_ENTRY("ctx2", 2, 1),
CREATE_ENTRY("ctx3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto prs_hdb_fifo_empty_prop = csr_prop_t(
std::make_shared<csr_s>(prs_hdb_fifo_empty),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fae_prs_0, "prs_hdb_fifo_empty", prs_hdb_fifo_empty_prop);
 // END fae_prs 
}
{
 // BEGIN etp_prs 
auto etp_prs_0 = nu_rng[0].add_an({"etp_prs"}, 0xB800000, 1, 0x0);
fld_map_t etp_prs_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto etp_prs_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_timeout_thresh_cfg", etp_prs_timeout_thresh_cfg_prop);
fld_map_t etp_prs_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etp_prs_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_timedout_sta", etp_prs_timedout_sta_prop);
fld_map_t etp_prs_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto etp_prs_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_timeout_clr", etp_prs_timeout_clr_prop);
fld_map_t etp_prs_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto etp_prs_features_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_features", etp_prs_features_prop);
fld_map_t etp_prs_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto etp_prs_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_spare_pio", etp_prs_spare_pio_prop);
fld_map_t etp_prs_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto etp_prs_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_scratchpad", etp_prs_scratchpad_prop);
fld_map_t etp_prs_sram_log_err {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto etp_prs_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_sram_log_err),
0x80,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_sram_log_err", etp_prs_sram_log_err_prop);
fld_map_t etp_prs_sram_log_syndrome {
CREATE_ENTRY("val", 0, 10),
CREATE_ENTRY("__rsvd", 10, 54)
};auto etp_prs_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_sram_log_syndrome),
0x88,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_sram_log_syndrome", etp_prs_sram_log_syndrome_prop);
fld_map_t etp_prs_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto etp_prs_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_sram_log_addr),
0x90,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_sram_log_addr", etp_prs_sram_log_addr_prop);
fld_map_t etp_prs_mem_err_inj_cfg {
CREATE_ENTRY("prs_dsp_fifo_mem0", 0, 1),
CREATE_ENTRY("prs_rob_prv_mem", 1, 1),
CREATE_ENTRY("prs_action_mem0", 2, 1),
CREATE_ENTRY("prs_action_mem1", 3, 1),
CREATE_ENTRY("prs_action_mem2", 4, 1),
CREATE_ENTRY("prs_action_mem3", 5, 1),
CREATE_ENTRY("err_type", 6, 1),
CREATE_ENTRY("__rsvd", 7, 57)
};auto etp_prs_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(etp_prs_mem_err_inj_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "etp_prs_mem_err_inj_cfg", etp_prs_mem_err_inj_cfg_prop);
fld_map_t prs_dsp_dfifo_mem_af_thold {
CREATE_ENTRY("data", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
0xA0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
fld_map_t prs_intf_cfg {
CREATE_ENTRY("intf0mode", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto prs_intf_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_intf_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_intf_cfg", prs_intf_cfg_prop);
fld_map_t prs_err_chk_en {
CREATE_ENTRY("outer_ipv4_checksum", 0, 1),
CREATE_ENTRY("inner_ipv4_checksum", 1, 1),
CREATE_ENTRY("no_tcam_match", 2, 1),
CREATE_ENTRY("parser_timeout", 3, 1),
CREATE_ENTRY("prv_oor", 4, 1),
CREATE_ENTRY("pkt_ptr_oor", 5, 1),
CREATE_ENTRY("hdr_buf_overflow", 6, 1),
CREATE_ENTRY("hdr_byte_oor", 7, 1),
CREATE_ENTRY("gp_byte_oor", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto prs_err_chk_en_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_chk_en),
0xB0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_err_chk_en", prs_err_chk_en_prop);
fld_map_t prs_err_tcode0 {
CREATE_ENTRY("outer_ipv4_checksum", 0, 7),
CREATE_ENTRY("inner_ipv4_checksum", 7, 7),
CREATE_ENTRY("no_tcam_match", 14, 7),
CREATE_ENTRY("parser_timeout", 21, 7),
CREATE_ENTRY("prv_oor", 28, 7),
CREATE_ENTRY("pkt_ptr_oor", 35, 7),
CREATE_ENTRY("hdr_buf_overflow", 42, 7),
CREATE_ENTRY("hdr_byte_oor", 49, 7),
CREATE_ENTRY("__rsvd", 56, 8)
};auto prs_err_tcode0_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode0),
0xB8,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
fld_map_t prs_err_tcode1 {
CREATE_ENTRY("gp_byte_oor", 0, 7),
CREATE_ENTRY("action_mem_perr", 7, 7),
CREATE_ENTRY("__rsvd", 14, 50)
};auto prs_err_tcode1_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode1),
0xC0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
fld_map_t prs_max_lu_cycle_cfg {
CREATE_ENTRY("use_fixed", 0, 1),
CREATE_ENTRY("fixed_cnt", 1, 8),
CREATE_ENTRY("init_cycle_cnt", 9, 6),
CREATE_ENTRY("acct_for_prv_bg_rd", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
fld_map_t prs_stream_cfg {
CREATE_ENTRY("fixed_stream_en", 0, 1),
CREATE_ENTRY("intf0_stream", 1, 5),
CREATE_ENTRY("__rsvd", 6, 58)
};auto prs_stream_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_stream_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
fld_map_t prs_static_ctx_sel {
CREATE_ENTRY("use_one_ctx", 0, 1),
CREATE_ENTRY("ctx_num", 1, 2),
CREATE_ENTRY("__rsvd", 3, 61)
};auto prs_static_ctx_sel_prop = csr_prop_t(
std::make_shared<csr_s>(prs_static_ctx_sel),
0xD8,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
fld_map_t prs_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
fld_map_t prs_hdb_fifo_empty {
CREATE_ENTRY("ctx0", 0, 1),
CREATE_ENTRY("ctx1", 1, 1),
CREATE_ENTRY("ctx2", 2, 1),
CREATE_ENTRY("ctx3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto prs_hdb_fifo_empty_prop = csr_prop_t(
std::make_shared<csr_s>(prs_hdb_fifo_empty),
0xF0,
CSR_TYPE::REG,
1);
add_csr(etp_prs_0, "prs_hdb_fifo_empty", prs_hdb_fifo_empty_prop);
 // END etp_prs 
}
{
 // BEGIN erp_prs 
auto erp_prs_0 = nu_rng[0].add_an({"efp_rfp","erp_prs"}, 0xC000000, 1, 0x0);
fld_map_t erp_prs_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto erp_prs_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_timeout_thresh_cfg", erp_prs_timeout_thresh_cfg_prop);
fld_map_t erp_prs_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto erp_prs_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_timedout_sta", erp_prs_timedout_sta_prop);
fld_map_t erp_prs_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto erp_prs_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_timeout_clr", erp_prs_timeout_clr_prop);
fld_map_t erp_prs_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto erp_prs_features_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_features", erp_prs_features_prop);
fld_map_t erp_prs_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto erp_prs_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_spare_pio", erp_prs_spare_pio_prop);
fld_map_t erp_prs_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto erp_prs_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_scratchpad", erp_prs_scratchpad_prop);
fld_map_t erp_prs_sram_log_err {
CREATE_ENTRY("val", 0, 12),
CREATE_ENTRY("__rsvd", 12, 52)
};auto erp_prs_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_sram_log_err),
0x80,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_sram_log_err", erp_prs_sram_log_err_prop);
fld_map_t erp_prs_sram_log_syndrome {
CREATE_ENTRY("val", 0, 10),
CREATE_ENTRY("__rsvd", 10, 54)
};auto erp_prs_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_sram_log_syndrome),
0x88,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_sram_log_syndrome", erp_prs_sram_log_syndrome_prop);
fld_map_t erp_prs_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto erp_prs_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_sram_log_addr),
0x90,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_sram_log_addr", erp_prs_sram_log_addr_prop);
fld_map_t erp_prs_mem_err_inj_cfg {
CREATE_ENTRY("prs_dsp_fifo_mem0", 0, 1),
CREATE_ENTRY("prs_dsp_fifo_mem1", 1, 1),
CREATE_ENTRY("prs_rob_prv_mem", 2, 1),
CREATE_ENTRY("prs_action_mem0", 3, 1),
CREATE_ENTRY("prs_action_mem1", 4, 1),
CREATE_ENTRY("prs_action_mem2", 5, 1),
CREATE_ENTRY("prs_action_mem3", 6, 1),
CREATE_ENTRY("prs_action_mem4", 7, 1),
CREATE_ENTRY("prs_action_mem5", 8, 1),
CREATE_ENTRY("err_type", 9, 1),
CREATE_ENTRY("__rsvd", 10, 54)
};auto erp_prs_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prs_mem_err_inj_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "erp_prs_mem_err_inj_cfg", erp_prs_mem_err_inj_cfg_prop);
fld_map_t prs_dsp_dfifo_mem_af_thold {
CREATE_ENTRY("data", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
0xA0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
fld_map_t prs_intf_cfg {
CREATE_ENTRY("intf0mode", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto prs_intf_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_intf_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_intf_cfg", prs_intf_cfg_prop);
fld_map_t prs_err_chk_en {
CREATE_ENTRY("outer_ipv4_checksum", 0, 1),
CREATE_ENTRY("inner_ipv4_checksum", 1, 1),
CREATE_ENTRY("no_tcam_match", 2, 1),
CREATE_ENTRY("parser_timeout", 3, 1),
CREATE_ENTRY("prv_oor", 4, 1),
CREATE_ENTRY("pkt_ptr_oor", 5, 1),
CREATE_ENTRY("hdr_buf_overflow", 6, 1),
CREATE_ENTRY("hdr_byte_oor", 7, 1),
CREATE_ENTRY("gp_byte_oor", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto prs_err_chk_en_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_chk_en),
0xB0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_err_chk_en", prs_err_chk_en_prop);
fld_map_t prs_err_tcode0 {
CREATE_ENTRY("outer_ipv4_checksum", 0, 7),
CREATE_ENTRY("inner_ipv4_checksum", 7, 7),
CREATE_ENTRY("no_tcam_match", 14, 7),
CREATE_ENTRY("parser_timeout", 21, 7),
CREATE_ENTRY("prv_oor", 28, 7),
CREATE_ENTRY("pkt_ptr_oor", 35, 7),
CREATE_ENTRY("hdr_buf_overflow", 42, 7),
CREATE_ENTRY("hdr_byte_oor", 49, 7),
CREATE_ENTRY("__rsvd", 56, 8)
};auto prs_err_tcode0_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode0),
0xB8,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
fld_map_t prs_err_tcode1 {
CREATE_ENTRY("gp_byte_oor", 0, 7),
CREATE_ENTRY("action_mem_perr", 7, 7),
CREATE_ENTRY("__rsvd", 14, 50)
};auto prs_err_tcode1_prop = csr_prop_t(
std::make_shared<csr_s>(prs_err_tcode1),
0xC0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
fld_map_t prs_max_lu_cycle_cfg {
CREATE_ENTRY("use_fixed", 0, 1),
CREATE_ENTRY("fixed_cnt", 1, 8),
CREATE_ENTRY("init_cycle_cnt", 9, 6),
CREATE_ENTRY("acct_for_prv_bg_rd", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
fld_map_t prs_stream_cfg {
CREATE_ENTRY("fixed_stream_en", 0, 1),
CREATE_ENTRY("intf0_stream", 1, 5),
CREATE_ENTRY("__rsvd", 6, 58)
};auto prs_stream_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_stream_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
fld_map_t prs_static_ctx_sel {
CREATE_ENTRY("use_one_ctx", 0, 1),
CREATE_ENTRY("ctx_num", 1, 3),
CREATE_ENTRY("__rsvd", 4, 60)
};auto prs_static_ctx_sel_prop = csr_prop_t(
std::make_shared<csr_s>(prs_static_ctx_sel),
0xD8,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
fld_map_t prs_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
fld_map_t prs_hdb_fifo_empty {
CREATE_ENTRY("ctx0", 0, 1),
CREATE_ENTRY("ctx1", 1, 1),
CREATE_ENTRY("ctx2", 2, 1),
CREATE_ENTRY("ctx3", 3, 1),
CREATE_ENTRY("ctx4", 4, 1),
CREATE_ENTRY("ctx5", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto prs_hdb_fifo_empty_prop = csr_prop_t(
std::make_shared<csr_s>(prs_hdb_fifo_empty),
0xF0,
CSR_TYPE::REG,
1);
add_csr(erp_prs_0, "prs_hdb_fifo_empty", prs_hdb_fifo_empty_prop);
 // END erp_prs 
}
{
 // BEGIN efp_rfp_lcl 
auto efp_rfp_lcl_0 = nu_rng[0].add_an({"efp_rfp","efp_rfp_lcl"}, 0xCE00000, 1, 0x0);
fld_map_t efp_rfp_lcl_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_lcl_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timeout_thresh_cfg", efp_rfp_lcl_timeout_thresh_cfg_prop);
fld_map_t efp_rfp_lcl_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_lcl_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timedout_sta", efp_rfp_lcl_timedout_sta_prop);
fld_map_t efp_rfp_lcl_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_lcl_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timeout_clr", efp_rfp_lcl_timeout_clr_prop);
fld_map_t efp_rfp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto efp_rfp_features_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_features", efp_rfp_features_prop);
fld_map_t efp_rfp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_spare_pio", efp_rfp_spare_pio_prop);
fld_map_t efp_rfp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_scratchpad", efp_rfp_scratchpad_prop);
fld_map_t efp_rfp_parser_offset {
CREATE_ENTRY("offset", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_parser_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_parser_offset),
0x80,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_parser_offset", efp_rfp_parser_offset_prop);
fld_map_t efp_rfp_trfc_prfl {
CREATE_ENTRY("efp_rfp_trfc_pri", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_trfc_prfl_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_trfc_prfl),
0x98,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_trfc_prfl", efp_rfp_trfc_prfl_prop);
fld_map_t efp_rfp_rsrc_prf_strt {
CREATE_ENTRY("start_pref", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto efp_rfp_rsrc_prf_strt_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rsrc_prf_strt),
0x298,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prf_strt", efp_rfp_rsrc_prf_strt_prop);
fld_map_t efp_rfp_rsrc_prf_done {
CREATE_ENTRY("pref_done", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto efp_rfp_rsrc_prf_done_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rsrc_prf_done),
0x2A0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prf_done", efp_rfp_rsrc_prf_done_prop);
fld_map_t efp_rfp_num_bh_prf {
CREATE_ENTRY("num_bh", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_num_bh_prf_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_num_bh_prf),
0x2A8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_num_bh_prf", efp_rfp_num_bh_prf_prop);
fld_map_t efp_rfp_num_au_prf {
CREATE_ENTRY("num_au", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto efp_rfp_num_au_prf_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_num_au_prf),
0x2B0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_num_au_prf", efp_rfp_num_au_prf_prop);
fld_map_t efp_rfp_bh_req_thr {
CREATE_ENTRY("bh_req_thr", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_bh_req_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bh_req_thr),
0x2B8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_bh_req_thr", efp_rfp_bh_req_thr_prop);
fld_map_t efp_rfp_au_req_thr {
CREATE_ENTRY("au_req_thr", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto efp_rfp_au_req_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_au_req_thr),
0x2C0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_au_req_thr", efp_rfp_au_req_thr_prop);
fld_map_t efp_rfp_au_cntr {
CREATE_ENTRY("num_au_pref", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_au_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_au_cntr),
0x2C8,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_au_cntr", efp_rfp_au_cntr_prop);
fld_map_t efp_rfp_bh_sts {
CREATE_ENTRY("num_bh_pref", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_bh_sts_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bh_sts),
0x310,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_bh_sts", efp_rfp_bh_sts_prop);
fld_map_t efp_rfp_pc_cl_opts {
CREATE_ENTRY("opt0", 0, 4),
CREATE_ENTRY("opt1", 4, 4),
CREATE_ENTRY("opt2", 8, 4),
CREATE_ENTRY("opt3", 12, 4),
CREATE_ENTRY("opt4", 16, 4),
CREATE_ENTRY("opt5", 20, 4),
CREATE_ENTRY("opt6", 24, 4),
CREATE_ENTRY("opt7", 28, 4),
CREATE_ENTRY("opt0_vld", 32, 1),
CREATE_ENTRY("opt1_vld", 33, 1),
CREATE_ENTRY("opt2_vld", 34, 1),
CREATE_ENTRY("opt3_vld", 35, 1),
CREATE_ENTRY("opt4_vld", 36, 1),
CREATE_ENTRY("opt5_vld", 37, 1),
CREATE_ENTRY("opt6_vld", 38, 1),
CREATE_ENTRY("opt7_vld", 39, 1),
CREATE_ENTRY("__rsvd", 40, 24)
};auto efp_rfp_pc_cl_opts_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_pc_cl_opts),
0x358,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_pc_cl_opts", efp_rfp_pc_cl_opts_prop);
fld_map_t efp_rfp_max_bh_allc_rq {
CREATE_ENTRY("num_bh", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_max_bh_allc_rq_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_max_bh_allc_rq),
0x3A0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_max_bh_allc_rq", efp_rfp_max_bh_allc_rq_prop);
fld_map_t efp_rfp_max_au_allc_rq {
CREATE_ENTRY("num_au", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_max_au_allc_rq_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_max_au_allc_rq),
0x3A8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_max_au_allc_rq", efp_rfp_max_au_allc_rq_prop);
fld_map_t efp_rfp_max_pend_allc_req {
CREATE_ENTRY("max_num", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_max_pend_allc_req_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_max_pend_allc_req),
0x3B0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_max_pend_allc_req", efp_rfp_max_pend_allc_req_prop);
fld_map_t efp_rfp_rsrc_prefetch_pool {
CREATE_ENTRY("pool", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_rsrc_prefetch_pool_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rsrc_prefetch_pool),
0x3B8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prefetch_pool", efp_rfp_rsrc_prefetch_pool_prop);
fld_map_t efp_rfp_clr_map_indv_pool {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_indv_pool_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_indv_pool),
0x3C0,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_indv_pool", efp_rfp_clr_map_indv_pool_prop);
fld_map_t efp_rfp_clr_map_tot_pool {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_tot_pool_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_tot_pool),
0x440,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_tot_pool", efp_rfp_clr_map_tot_pool_prop);
fld_map_t efp_rfp_tot_bmpool_xoff {
CREATE_ENTRY("psw_sch_node", 0, 24),
CREATE_ENTRY("psw_xoff_q_vec", 24, 8),
CREATE_ENTRY("fcb_sch_node", 32, 8),
CREATE_ENTRY("fcb_xoff_q_vec", 40, 8),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_tot_bmpool_xoff_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_tot_bmpool_xoff),
0x4C0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_tot_bmpool_xoff", efp_rfp_tot_bmpool_xoff_prop);
fld_map_t efp_rfp_wu_thr_xoff {
CREATE_ENTRY("psw_sch_node", 0, 24),
CREATE_ENTRY("psw_xoff_q_vec", 24, 8),
CREATE_ENTRY("fcb_sch_node", 32, 8),
CREATE_ENTRY("fcb_xoff_q_vec", 40, 8),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_wu_thr_xoff_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_wu_thr_xoff),
0x4C8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_wu_thr_xoff", efp_rfp_wu_thr_xoff_prop);
fld_map_t efp_rfp_psw_nd_st {
CREATE_ENTRY("node_state", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_psw_nd_st_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_psw_nd_st),
0x4D0,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_psw_nd_st", efp_rfp_psw_nd_st_prop);
fld_map_t efp_rfp_fcb_nd_st {
CREATE_ENTRY("node_state", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_fcb_nd_st_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcb_nd_st),
0x590,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_fcb_nd_st", efp_rfp_fcb_nd_st_prop);
fld_map_t efp_rfp_clr_map_tot_wu_occ {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_tot_wu_occ_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_tot_wu_occ),
0x5D0,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_tot_wu_occ", efp_rfp_clr_map_tot_wu_occ_prop);
fld_map_t efp_rfp_clr_map_nut_wu_occ {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_nut_wu_occ_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_nut_wu_occ),
0x650,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_nut_wu_occ", efp_rfp_clr_map_nut_wu_occ_prop);
fld_map_t efp_rfp_l4cs_kuc {
CREATE_ENTRY("en_cs", 0, 1),
CREATE_ENTRY("l4_type", 1, 1),
CREATE_ENTRY("skip_zero_cs", 2, 1),
CREATE_ENTRY("dis_ip_len_chk", 3, 1),
CREATE_ENTRY("l3_hdr_num", 4, 3),
CREATE_ENTRY("l4_hdr_num", 7, 3),
CREATE_ENTRY("__rsvd", 10, 54)
};auto efp_rfp_l4cs_kuc_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_l4cs_kuc),
0x6D0,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_kuc", efp_rfp_l4cs_kuc_prop);
fld_map_t efp_rfp_proto_lst {
CREATE_ENTRY("tcp_proto", 0, 8),
CREATE_ENTRY("udp_proto", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_proto_lst_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_proto_lst),
0x750,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_proto_lst", efp_rfp_proto_lst_prop);
fld_map_t efp_rfp_rad_past_thr {
CREATE_ENTRY("age_delta", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_rad_past_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_past_thr),
0x758,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_past_thr", efp_rfp_rad_past_thr_prop);
fld_map_t efp_rfp_rad_futr_thr {
CREATE_ENTRY("age_delta", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_rad_futr_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_futr_thr),
0x760,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_futr_thr", efp_rfp_rad_futr_thr_prop);
fld_map_t efp_rfp_rad_enable {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_rad_enable_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_enable),
0x768,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_enable", efp_rfp_rad_enable_prop);
fld_map_t efp_rfp_estrm_bmpool_map {
CREATE_ENTRY("bmpool", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_estrm_bmpool_map_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_estrm_bmpool_map),
0x770,
CSR_TYPE::REG_LST,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_estrm_bmpool_map", efp_rfp_estrm_bmpool_map_prop);
fld_map_t efp_rfp_fcp_pkt_adj {
CREATE_ENTRY("fcb_adj_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_fcp_pkt_adj_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_pkt_adj),
0x830,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_pkt_adj", efp_rfp_fcp_pkt_adj_prop);
fld_map_t efp_rfp_fcp_block_sz {
CREATE_ENTRY("fld_blk_sz", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto efp_rfp_fcp_block_sz_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_block_sz),
0x838,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_block_sz", efp_rfp_fcp_block_sz_prop);
fld_map_t efp_rfp_gph_sz {
CREATE_ENTRY("gph_sz", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_gph_sz_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_gph_sz),
0x840,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_gph_sz", efp_rfp_gph_sz_prop);
fld_map_t efp_rfp_fcp_qos_slct {
CREATE_ENTRY("bit_slct", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_fcp_qos_slct_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_qos_slct),
0x848,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_qos_slct", efp_rfp_fcp_qos_slct_prop);
fld_map_t efp_rfp_fcp_stream_cfg {
CREATE_ENTRY("fcp_stream", 0, 3),
CREATE_ENTRY("fcp_present", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_fcp_stream_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_stream_cfg),
0x850,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_stream_cfg", efp_rfp_fcp_stream_cfg_prop);
fld_map_t efp_rfp_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fla_ring_module_id_cfg),
0x858,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_fla_ring_module_id_cfg", efp_rfp_fla_ring_module_id_cfg_prop);
fld_map_t efp_rfp_bm_pool_rid_offset {
CREATE_ENTRY("offset", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_bm_pool_rid_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bm_pool_rid_offset),
0x860,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_bm_pool_rid_offset", efp_rfp_bm_pool_rid_offset_prop);
fld_map_t efp_rfp_num_bm_pools {
CREATE_ENTRY("num_pools", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_num_bm_pools_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_num_bm_pools),
0x868,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_num_bm_pools", efp_rfp_num_bm_pools_prop);
fld_map_t efp_rfp_nut_wu_occ_offset {
CREATE_ENTRY("offset", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_nut_wu_occ_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_nut_wu_occ_offset),
0x870,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_nut_wu_occ_offset", efp_rfp_nut_wu_occ_offset_prop);
fld_map_t efp_rfp_all_wu_occ_offset {
CREATE_ENTRY("offset", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_all_wu_occ_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_all_wu_occ_offset),
0x878,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_all_wu_occ_offset", efp_rfp_all_wu_occ_offset_prop);
fld_map_t efp_rfp_bm_master_id {
CREATE_ENTRY("client_id", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto efp_rfp_bm_master_id_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bm_master_id),
0x880,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_bm_master_id", efp_rfp_bm_master_id_prop);
fld_map_t efp_rfp_sram_err_inj_cfg {
CREATE_ENTRY("efp_rfp_clbp_mem", 0, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem", 1, 1),
CREATE_ENTRY("efp_rfp_rad_mem", 2, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem", 3, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0", 4, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1", 5, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2", 6, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0", 7, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1", 8, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem", 9, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf", 10, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf", 11, 1),
CREATE_ENTRY("efp_rfp_misc_buf", 12, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf", 13, 1),
CREATE_ENTRY("efp_rfp_tag_data", 14, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq", 15, 1),
CREATE_ENTRY("err_type", 16, 1),
CREATE_ENTRY("__rsvd", 17, 47)
};auto efp_rfp_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_err_inj_cfg),
0x888,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_err_inj_cfg", efp_rfp_sram_err_inj_cfg_prop);
fld_map_t efp_rfp_sram_cerr_log_vec {
CREATE_ENTRY("efp_rfp_clbp_mem", 0, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem", 1, 1),
CREATE_ENTRY("efp_rfp_rad_mem", 2, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem", 3, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0", 4, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1", 5, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2", 6, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0", 7, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1", 8, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem", 9, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf", 10, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf", 11, 1),
CREATE_ENTRY("efp_rfp_misc_buf", 12, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf", 13, 1),
CREATE_ENTRY("efp_rfp_tag_data", 14, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_sram_cerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_cerr_log_vec),
0x890,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_cerr_log_vec", efp_rfp_sram_cerr_log_vec_prop);
fld_map_t efp_rfp_sram_ucerr_log_vec {
CREATE_ENTRY("efp_rfp_clbp_mem", 0, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem", 1, 1),
CREATE_ENTRY("efp_rfp_rad_mem", 2, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem", 3, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0", 4, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1", 5, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2", 6, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0", 7, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1", 8, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem", 9, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf", 10, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf", 11, 1),
CREATE_ENTRY("efp_rfp_misc_buf", 12, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf", 13, 1),
CREATE_ENTRY("efp_rfp_tag_data", 14, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_sram_ucerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_ucerr_log_vec),
0x898,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_ucerr_log_vec", efp_rfp_sram_ucerr_log_vec_prop);
fld_map_t efp_rfp_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_log_syndrome),
0x8A0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_log_syndrome", efp_rfp_sram_log_syndrome_prop);
fld_map_t efp_rfp_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_log_addr),
0x8A8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_log_addr", efp_rfp_sram_log_addr_prop);
fld_map_t efp_rfp_mhg_eot {
CREATE_ENTRY("val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto efp_rfp_mhg_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_mhg_eot),
0x8C0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_mhg_eot", efp_rfp_mhg_eot_prop);
fld_map_t efp_rfp_lsn_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_lsn_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lsn_eot),
0x8C8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_lsn_eot", efp_rfp_lsn_eot_prop);
fld_map_t efp_rfp_cs_pipe0_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_cs_pipe0_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_cs_pipe0_eot),
0x8D0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_cs_pipe0_eot", efp_rfp_cs_pipe0_eot_prop);
fld_map_t efp_rfp_cs_pipe1_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_cs_pipe1_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_cs_pipe1_eot),
0x8D8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_cs_pipe1_eot", efp_rfp_cs_pipe1_eot_prop);
fld_map_t efp_rfp_misc_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_misc_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_misc_eot),
0x8E0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_misc_eot", efp_rfp_misc_eot_prop);
fld_map_t efp_rfp_prs_wrapper_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_prs_wrapper_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_prs_wrapper_eot),
0x8E8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_prs_wrapper_eot", efp_rfp_prs_wrapper_eot_prop);
fld_map_t efp_rfp_upd_if_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_upd_if_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_upd_if_eot),
0x8F0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_upd_if_eot", efp_rfp_upd_if_eot_prop);
fld_map_t efp_rfp_watchdog_timer_period {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_watchdog_timer_period_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_watchdog_timer_period),
0x8F8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_watchdog_timer_period", efp_rfp_watchdog_timer_period_prop);
fld_map_t efp_rfp_err_drop_mask {
CREATE_ENTRY("hw_err", 0, 1),
CREATE_ENTRY("sw_err", 1, 1),
CREATE_ENTRY("rad_drop", 2, 1),
CREATE_ENTRY("pol_drop", 3, 1),
CREATE_ENTRY("fwd_drop", 4, 1),
CREATE_ENTRY("outer_cs_err", 5, 1),
CREATE_ENTRY("inner_cs_err", 6, 1),
CREATE_ENTRY("fcpea_sec_fail", 7, 1),
CREATE_ENTRY("fcp_req", 8, 1),
CREATE_ENTRY("fcp_gnt", 9, 1),
CREATE_ENTRY("fcp_dummy", 10, 1),
CREATE_ENTRY("__rsvd", 11, 53)
};auto efp_rfp_err_drop_mask_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_err_drop_mask),
0x900,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_err_drop_mask", efp_rfp_err_drop_mask_prop);
fld_map_t efp_rfp_err_drop_wu_gen {
CREATE_ENTRY("cluster_id", 0, 4),
CREATE_ENTRY("dlid", 4, 5),
CREATE_ENTRY("wu_queue_id", 9, 8),
CREATE_ENTRY("sw_opcode", 17, 24),
CREATE_ENTRY("__rsvd", 41, 23)
};auto efp_rfp_err_drop_wu_gen_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_err_drop_wu_gen),
0x908,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_lcl_0, "efp_rfp_err_drop_wu_gen", efp_rfp_err_drop_wu_gen_prop);
 // END efp_rfp_lcl 
}
{
 // BEGIN efp_rfp_part1 
auto efp_rfp_part1_0 = nu_rng[0].add_an({"efp_rfp_part1"}, 0x14000000, 1, 0x0);
fld_map_t efp_rfp_part1_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_part1_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_timeout_thresh_cfg", efp_rfp_part1_timeout_thresh_cfg_prop);
fld_map_t efp_rfp_part1_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_part1_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_timedout_sta", efp_rfp_part1_timedout_sta_prop);
fld_map_t efp_rfp_part1_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_part1_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_timeout_clr", efp_rfp_part1_timeout_clr_prop);
fld_map_t efp_rfp_part1_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto efp_rfp_part1_features_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_features", efp_rfp_part1_features_prop);
fld_map_t efp_rfp_part1_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_part1_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_spare_pio", efp_rfp_part1_spare_pio_prop);
fld_map_t efp_rfp_part1_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_part1_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_scratchpad", efp_rfp_part1_scratchpad_prop);
fld_map_t efp_rfp_rng_cfg {
CREATE_ENTRY("mode", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_rng_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rng_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_rng_cfg", efp_rfp_rng_cfg_prop);
fld_map_t efp_rfp_ffe_icount_cfg {
CREATE_ENTRY("itr_cnt", 0, 3),
CREATE_ENTRY("__rsvd", 3, 61)
};auto efp_rfp_ffe_icount_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_ffe_icount_cfg),
0x88,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_ffe_icount_cfg", efp_rfp_ffe_icount_cfg_prop);
fld_map_t efp_rfp_part1_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_part1_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_fla_ring_module_id_cfg),
0x90,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_fla_ring_module_id_cfg", efp_rfp_part1_fla_ring_module_id_cfg_prop);
fld_map_t efp_rfp_snpsht_cfg {
CREATE_ENTRY("enable", 0, 1),
CREATE_ENTRY("prv_fld_extr", 1, 56),
CREATE_ENTRY("__rsvd", 57, 7)
};auto efp_rfp_snpsht_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_cfg", efp_rfp_snpsht_cfg_prop);
fld_map_t efp_rfp_snpsht_mask_0 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_mask_0_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_mask_0),
0xA0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_mask_0", efp_rfp_snpsht_mask_0_prop);
fld_map_t efp_rfp_snpsht_mask_1 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_mask_1_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_mask_1),
0xA8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_mask_1", efp_rfp_snpsht_mask_1_prop);
fld_map_t efp_rfp_snpsht_mask_2 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_mask_2_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_mask_2),
0xB0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_mask_2", efp_rfp_snpsht_mask_2_prop);
fld_map_t efp_rfp_snpsht_mask_3 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_mask_3_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_mask_3),
0xB8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_mask_3", efp_rfp_snpsht_mask_3_prop);
fld_map_t efp_rfp_snpsht_mask_4 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_mask_4_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_mask_4),
0xC0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_mask_4", efp_rfp_snpsht_mask_4_prop);
fld_map_t efp_rfp_snpsht_val_0 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_val_0_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_val_0),
0xC8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_val_0", efp_rfp_snpsht_val_0_prop);
fld_map_t efp_rfp_snpsht_val_1 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_val_1_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_val_1),
0xD0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_val_1", efp_rfp_snpsht_val_1_prop);
fld_map_t efp_rfp_snpsht_val_2 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_val_2_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_val_2),
0xD8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_val_2", efp_rfp_snpsht_val_2_prop);
fld_map_t efp_rfp_snpsht_val_3 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_val_3_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_val_3),
0xE0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_val_3", efp_rfp_snpsht_val_3_prop);
fld_map_t efp_rfp_snpsht_val_4 {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_snpsht_val_4_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snpsht_val_4),
0xE8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_val_4", efp_rfp_snpsht_val_4_prop);
fld_map_t efp_rfp_part1_sram_err_inj_cfg {
CREATE_ENTRY("efp_rfp_mdi_mem", 0, 1),
CREATE_ENTRY("err_type", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_part1_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_sram_err_inj_cfg),
0xF0,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_sram_err_inj_cfg", efp_rfp_part1_sram_err_inj_cfg_prop);
fld_map_t efp_rfp_part1_sram_cerr_log_vec {
CREATE_ENTRY("efp_rfp_mdi_mem", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_part1_sram_cerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_sram_cerr_log_vec),
0xF8,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_sram_cerr_log_vec", efp_rfp_part1_sram_cerr_log_vec_prop);
fld_map_t efp_rfp_part1_sram_ucerr_log_vec {
CREATE_ENTRY("efp_rfp_mdi_mem", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_part1_sram_ucerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_sram_ucerr_log_vec),
0x100,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_sram_ucerr_log_vec", efp_rfp_part1_sram_ucerr_log_vec_prop);
fld_map_t efp_rfp_part1_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_part1_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_sram_log_syndrome),
0x108,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_sram_log_syndrome", efp_rfp_part1_sram_log_syndrome_prop);
fld_map_t efp_rfp_part1_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_part1_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_part1_sram_log_addr),
0x110,
CSR_TYPE::REG,
1);
add_csr(efp_rfp_part1_0, "efp_rfp_part1_sram_log_addr", efp_rfp_part1_sram_log_addr_prop);
 // END efp_rfp_part1 
}
{
 // BEGIN epg_rdp_lcl 
auto epg_rdp_lcl_0 = nu_rng[0].add_an({"epg_rdp","epg_rdp_lcl"}, 0x14030000, 3, 0x3000000);
fld_map_t epg_rdp_lcl_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto epg_rdp_lcl_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_lcl_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_lcl_timeout_thresh_cfg", epg_rdp_lcl_timeout_thresh_cfg_prop);
fld_map_t epg_rdp_lcl_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto epg_rdp_lcl_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_lcl_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_lcl_timedout_sta", epg_rdp_lcl_timedout_sta_prop);
fld_map_t epg_rdp_lcl_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto epg_rdp_lcl_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_lcl_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_lcl_timeout_clr", epg_rdp_lcl_timeout_clr_prop);
fld_map_t epg_rdp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto epg_rdp_features_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_features", epg_rdp_features_prop);
fld_map_t epg_rdp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto epg_rdp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_spare_pio", epg_rdp_spare_pio_prop);
fld_map_t epg_rdp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto epg_rdp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_scratchpad", epg_rdp_scratchpad_prop);
fld_map_t parser_offset {
CREATE_ENTRY("offset", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto parser_offset_prop = csr_prop_t(
std::make_shared<csr_s>(parser_offset),
0x80,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "parser_offset", parser_offset_prop);
fld_map_t erp_key_lu_63_0 {
CREATE_ENTRY("key", 0, 64)
};auto erp_key_lu_63_0_prop = csr_prop_t(
std::make_shared<csr_s>(erp_key_lu_63_0),
0x88,
CSR_TYPE::REG_LST,
1);
add_csr(epg_rdp_lcl_0, "erp_key_lu_63_0", erp_key_lu_63_0_prop);
fld_map_t erp_key_lu_127_64 {
CREATE_ENTRY("key", 0, 64)
};auto erp_key_lu_127_64_prop = csr_prop_t(
std::make_shared<csr_s>(erp_key_lu_127_64),
0x110,
CSR_TYPE::REG_LST,
1);
add_csr(epg_rdp_lcl_0, "erp_key_lu_127_64", erp_key_lu_127_64_prop);
fld_map_t erp_key_lu_191_128 {
CREATE_ENTRY("key", 0, 64)
};auto erp_key_lu_191_128_prop = csr_prop_t(
std::make_shared<csr_s>(erp_key_lu_191_128),
0x198,
CSR_TYPE::REG_LST,
1);
add_csr(epg_rdp_lcl_0, "erp_key_lu_191_128", erp_key_lu_191_128_prop);
fld_map_t erp_key_lu_255_192 {
CREATE_ENTRY("key", 0, 64)
};auto erp_key_lu_255_192_prop = csr_prop_t(
std::make_shared<csr_s>(erp_key_lu_255_192),
0x220,
CSR_TYPE::REG_LST,
1);
add_csr(epg_rdp_lcl_0, "erp_key_lu_255_192", erp_key_lu_255_192_prop);
fld_map_t erp_key_len_lu {
CREATE_ENTRY("key_len", 0, 2),
CREATE_ENTRY("salt", 2, 16),
CREATE_ENTRY("__rsvd", 18, 46)
};auto erp_key_len_lu_prop = csr_prop_t(
std::make_shared<csr_s>(erp_key_len_lu),
0x2A8,
CSR_TYPE::REG_LST,
1);
add_csr(epg_rdp_lcl_0, "erp_key_len_lu", erp_key_len_lu_prop);
fld_map_t erp_prw_cfg_min_pkt_len {
CREATE_ENTRY("min_pkt_len", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto erp_prw_cfg_min_pkt_len_prop = csr_prop_t(
std::make_shared<csr_s>(erp_prw_cfg_min_pkt_len),
0x330,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "erp_prw_cfg_min_pkt_len", erp_prw_cfg_min_pkt_len_prop);
fld_map_t erp_fcp_stream_map {
CREATE_ENTRY("fcp_stream", 0, 3),
CREATE_ENTRY("fcp_present", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto erp_fcp_stream_map_prop = csr_prop_t(
std::make_shared<csr_s>(erp_fcp_stream_map),
0x338,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "erp_fcp_stream_map", erp_fcp_stream_map_prop);
fld_map_t erp_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto erp_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(erp_fla_ring_module_id_cfg),
0x340,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "erp_fla_ring_module_id_cfg", erp_fla_ring_module_id_cfg_prop);
fld_map_t epg_rdp_sram_err_inj_cfg {
CREATE_ENTRY("plb_mem0", 0, 1),
CREATE_ENTRY("ctrlb_mem0", 1, 1),
CREATE_ENTRY("modh_data_mem0", 2, 1),
CREATE_ENTRY("modh_ctrl_mem0", 3, 1),
CREATE_ENTRY("plb_mem1", 4, 1),
CREATE_ENTRY("ctrlb_mem1", 5, 1),
CREATE_ENTRY("modh_data_mem1", 6, 1),
CREATE_ENTRY("modh_ctrl_mem1", 7, 1),
CREATE_ENTRY("err_type", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto epg_rdp_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_sram_err_inj_cfg),
0x348,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_sram_err_inj_cfg", epg_rdp_sram_err_inj_cfg_prop);
fld_map_t epg_rdp_sram_cerr_log_vec {
CREATE_ENTRY("plb_mem0", 0, 1),
CREATE_ENTRY("ctrlb_mem0", 1, 1),
CREATE_ENTRY("modh_data_mem0", 2, 1),
CREATE_ENTRY("modh_ctrl_mem0", 3, 1),
CREATE_ENTRY("plb_mem1", 4, 1),
CREATE_ENTRY("ctrlb_mem1", 5, 1),
CREATE_ENTRY("modh_data_mem1", 6, 1),
CREATE_ENTRY("modh_ctrl_mem1", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto epg_rdp_sram_cerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_sram_cerr_log_vec),
0x350,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_sram_cerr_log_vec", epg_rdp_sram_cerr_log_vec_prop);
fld_map_t epg_rdp_sram_ucerr_log_vec {
CREATE_ENTRY("plb_mem0", 0, 1),
CREATE_ENTRY("ctrlb_mem0", 1, 1),
CREATE_ENTRY("modh_data_mem0", 2, 1),
CREATE_ENTRY("modh_ctrl_mem0", 3, 1),
CREATE_ENTRY("plb_mem1", 4, 1),
CREATE_ENTRY("ctrlb_mem1", 5, 1),
CREATE_ENTRY("modh_data_mem1", 6, 1),
CREATE_ENTRY("modh_ctrl_mem1", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto epg_rdp_sram_ucerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_sram_ucerr_log_vec),
0x358,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_sram_ucerr_log_vec", epg_rdp_sram_ucerr_log_vec_prop);
fld_map_t epg_rdp_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto epg_rdp_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_sram_log_syndrome),
0x360,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_sram_log_syndrome", epg_rdp_sram_log_syndrome_prop);
fld_map_t epg_rdp_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto epg_rdp_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(epg_rdp_sram_log_addr),
0x368,
CSR_TYPE::REG,
1);
add_csr(epg_rdp_lcl_0, "epg_rdp_sram_log_addr", epg_rdp_sram_log_addr_prop);
 // END epg_rdp_lcl 
}
{
 // BEGIN fep_nu 
auto fep_nu_0 = nu_rng[0].add_an({"fepw_nu","fep_nu"}, 0x14030400, 3, 0x80000);
fld_map_t fep_nu_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fep_nu_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_timeout_thresh_cfg", fep_nu_timeout_thresh_cfg_prop);
fld_map_t fep_nu_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fep_nu_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_timedout_sta", fep_nu_timedout_sta_prop);
fld_map_t fep_nu_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fep_nu_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_timeout_clr", fep_nu_timeout_clr_prop);
fld_map_t fep_nu_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fep_nu_features_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_features", fep_nu_features_prop);
fld_map_t fep_nu_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fep_nu_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_spare_pio", fep_nu_spare_pio_prop);
fld_map_t fep_nu_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fep_nu_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_scratchpad", fep_nu_scratchpad_prop);
fld_map_t fep_nu_misc_cfg {
CREATE_ENTRY("addr_trans_dn_vc1_en", 0, 1),
CREATE_ENTRY("addr_trans_sn_vc3_en", 1, 1),
CREATE_ENTRY("addr_trans_sn_vc2_en", 2, 1),
CREATE_ENTRY("addr_trans_sn_vc1_en", 3, 1),
CREATE_ENTRY("addr_trans_sn_vc0_en", 4, 1),
CREATE_ENTRY("remote_crd_load", 5, 1),
CREATE_ENTRY("enable", 6, 1),
CREATE_ENTRY("metadata_err_drop_dis", 7, 1),
CREATE_ENTRY("hbm_stacked_mode", 8, 1),
CREATE_ENTRY("ddr_stacked_mode", 9, 1),
CREATE_ENTRY("__rsvd", 10, 54)
};auto fep_nu_misc_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_misc_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_misc_cfg", fep_nu_misc_cfg_prop);
fld_map_t fep_nu_mem_err_inj_cfg {
CREATE_ENTRY("ibuf_mem_metadata", 0, 1),
CREATE_ENTRY("ibuf_mem_data", 1, 1),
CREATE_ENTRY("err_type", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto fep_nu_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_mem_err_inj_cfg),
0x88,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_mem_err_inj_cfg", fep_nu_mem_err_inj_cfg_prop);
fld_map_t fep_nu_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_nu_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_fla_ring_module_id_cfg),
0x90,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_fla_ring_module_id_cfg", fep_nu_fla_ring_module_id_cfg_prop);
fld_map_t fep_nu_fla_cfg {
CREATE_ENTRY("mux_sel_0", 0, 7),
CREATE_ENTRY("mux_sel_1", 7, 7),
CREATE_ENTRY("mux_sel_2", 14, 7),
CREATE_ENTRY("mux_sel_3", 21, 7),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fep_nu_fla_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_fla_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_fla_cfg", fep_nu_fla_cfg_prop);
fld_map_t fep_nu_fla_sta {
CREATE_ENTRY("dbus_0", 0, 16),
CREATE_ENTRY("dbus_1", 16, 16),
CREATE_ENTRY("dbus_2", 32, 16),
CREATE_ENTRY("dbus_3", 48, 16)
};auto fep_nu_fla_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_fla_sta),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_fla_sta", fep_nu_fla_sta_prop);
fld_map_t fep_nu_local_id {
CREATE_ENTRY("erp_local_id", 0, 5),
CREATE_ENTRY("etp_min_local_id", 5, 5),
CREATE_ENTRY("nwqm_local_id", 10, 5),
CREATE_ENTRY("wro_local_id", 15, 5),
CREATE_ENTRY("fae_local_id", 20, 5),
CREATE_ENTRY("mpg_local_id", 25, 5),
CREATE_ENTRY("etp_max_local_id", 30, 5),
CREATE_ENTRY("__rsvd", 35, 29)
};auto fep_nu_local_id_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_local_id),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_local_id", fep_nu_local_id_prop);
fld_map_t fep_nu_strict_order {
CREATE_ENTRY("erp_strict_ord", 0, 1),
CREATE_ENTRY("erp_strict_ord_for_pwr", 1, 1),
CREATE_ENTRY("nwqm_strict_ord", 2, 1),
CREATE_ENTRY("nwqm_strict_ord_for_pwr", 3, 1),
CREATE_ENTRY("fae_strict_ord", 4, 1),
CREATE_ENTRY("fae_strict_ord_for_pwr", 5, 1),
CREATE_ENTRY("mpg_strict_ord", 6, 1),
CREATE_ENTRY("mpg_strict_ord_for_pwr", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_nu_strict_order_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_strict_order),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_strict_order", fep_nu_strict_order_prop);
fld_map_t fep_nu_erp_snx_cdt_init_val {
CREATE_ENTRY("erp_vc0_cdt", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_nu_erp_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_erp_snx_cdt_init_val),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_erp_snx_cdt_init_val", fep_nu_erp_snx_cdt_init_val_prop);
fld_map_t fep_nu_nwqm_snx_cdt_init_val {
CREATE_ENTRY("nwqm_vc0_cdt", 0, 8),
CREATE_ENTRY("nwqm_vc1_cdt", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fep_nu_nwqm_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_nwqm_snx_cdt_init_val),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_nwqm_snx_cdt_init_val", fep_nu_nwqm_snx_cdt_init_val_prop);
fld_map_t fep_nu_wro_snx_cdt_init_val {
CREATE_ENTRY("wro_vc0_cdt", 0, 8),
CREATE_ENTRY("wro_vc2_cdt", 8, 8),
CREATE_ENTRY("wro_vc3_cdt", 16, 8),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fep_nu_wro_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_wro_snx_cdt_init_val),
0xC8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_wro_snx_cdt_init_val", fep_nu_wro_snx_cdt_init_val_prop);
fld_map_t fep_nu_fae_snx_cdt_init_val {
CREATE_ENTRY("fae_vc0_cdt", 0, 8),
CREATE_ENTRY("fae_vc2_cdt", 8, 8),
CREATE_ENTRY("fae_vc3_cdt", 16, 8),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fep_nu_fae_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_fae_snx_cdt_init_val),
0xD0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_fae_snx_cdt_init_val", fep_nu_fae_snx_cdt_init_val_prop);
fld_map_t fep_nu_mpg_snx_cdt_init_val {
CREATE_ENTRY("mpg_vc0_cdt", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_nu_mpg_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_mpg_snx_cdt_init_val),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_mpg_snx_cdt_init_val", fep_nu_mpg_snx_cdt_init_val_prop);
fld_map_t fep_nu_erp_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_nu_erp_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_erp_sn_filter),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_erp_sn_filter", fep_nu_erp_sn_filter_prop);
fld_map_t fep_nu_nwqm_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_nu_nwqm_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_nwqm_sn_filter),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_nwqm_sn_filter", fep_nu_nwqm_sn_filter_prop);
fld_map_t fep_nu_fae_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_nu_fae_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_fae_sn_filter),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_fae_sn_filter", fep_nu_fae_sn_filter_prop);
fld_map_t fep_nu_mpg_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_nu_mpg_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_mpg_sn_filter),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_mpg_sn_filter", fep_nu_mpg_sn_filter_prop);
fld_map_t fep_nu_snx_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_nu_snx_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_snx_sn_filter),
0x100,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_snx_sn_filter", fep_nu_snx_sn_filter_prop);
fld_map_t fep_nu_nwqm_lsn_arb_cfg {
CREATE_ENTRY("gr_wt_in0", 0, 4),
CREATE_ENTRY("wrr_wt_in0", 4, 4),
CREATE_ENTRY("gr_wt_in1", 8, 4),
CREATE_ENTRY("wrr_wt_in1", 12, 4),
CREATE_ENTRY("gr_wt_in2", 16, 4),
CREATE_ENTRY("wrr_wt_in2", 20, 4),
CREATE_ENTRY("gr_wt_in3", 24, 4),
CREATE_ENTRY("wrr_wt_in3", 28, 4),
CREATE_ENTRY("gr_per_in", 32, 8),
CREATE_ENTRY("__rsvd", 40, 24)
};auto fep_nu_nwqm_lsn_arb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_nwqm_lsn_arb_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_nwqm_lsn_arb_cfg", fep_nu_nwqm_lsn_arb_cfg_prop);
fld_map_t fep_nu_snx_lsn_arb_cfg {
CREATE_ENTRY("gr_wt_in0", 0, 4),
CREATE_ENTRY("wrr_wt_in0", 4, 4),
CREATE_ENTRY("gr_wt_in1", 8, 4),
CREATE_ENTRY("wrr_wt_in1", 12, 4),
CREATE_ENTRY("gr_wt_in2", 16, 4),
CREATE_ENTRY("wrr_wt_in2", 20, 4),
CREATE_ENTRY("gr_wt_in3", 24, 4),
CREATE_ENTRY("wrr_wt_in3", 28, 4),
CREATE_ENTRY("gr_per_in", 32, 8),
CREATE_ENTRY("__rsvd", 40, 24)
};auto fep_nu_snx_lsn_arb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_snx_lsn_arb_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_snx_lsn_arb_cfg", fep_nu_snx_lsn_arb_cfg_prop);
fld_map_t fep_nu_dest_cfg_cmd_0 {
CREATE_ENTRY("cmd0_vld", 0, 1),
CREATE_ENTRY("cmd0_lid", 1, 5),
CREATE_ENTRY("cmd1_vld", 6, 1),
CREATE_ENTRY("cmd1_lid", 7, 5),
CREATE_ENTRY("cmd2_vld", 12, 1),
CREATE_ENTRY("cmd2_lid", 13, 5),
CREATE_ENTRY("cmd3_vld", 18, 1),
CREATE_ENTRY("cmd3_lid", 19, 5),
CREATE_ENTRY("cmd4_vld", 24, 1),
CREATE_ENTRY("cmd4_lid", 25, 5),
CREATE_ENTRY("cmd5_vld", 30, 1),
CREATE_ENTRY("cmd5_lid", 31, 5),
CREATE_ENTRY("cmd6_vld", 36, 1),
CREATE_ENTRY("cmd6_lid", 37, 5),
CREATE_ENTRY("cmd7_vld", 42, 1),
CREATE_ENTRY("cmd7_lid", 43, 5),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fep_nu_dest_cfg_cmd_0_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_dest_cfg_cmd_0),
0x118,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_dest_cfg_cmd_0", fep_nu_dest_cfg_cmd_0_prop);
fld_map_t fep_nu_dest_cfg_cmd_1 {
CREATE_ENTRY("cmd8_vld", 0, 1),
CREATE_ENTRY("cmd8_lid", 1, 5),
CREATE_ENTRY("cmd9_vld", 6, 1),
CREATE_ENTRY("cmd9_lid", 7, 5),
CREATE_ENTRY("cmd10_vld", 12, 1),
CREATE_ENTRY("cmd10_lid", 13, 5),
CREATE_ENTRY("cmd11_vld", 18, 1),
CREATE_ENTRY("cmd11_lid", 19, 5),
CREATE_ENTRY("cmd12_vld", 24, 1),
CREATE_ENTRY("cmd12_lid", 25, 5),
CREATE_ENTRY("cmd13_vld", 30, 1),
CREATE_ENTRY("cmd13_lid", 31, 5),
CREATE_ENTRY("cmd14_vld", 36, 1),
CREATE_ENTRY("cmd14_lid", 37, 5),
CREATE_ENTRY("cmd15_vld", 42, 1),
CREATE_ENTRY("cmd15_lid", 43, 5),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fep_nu_dest_cfg_cmd_1_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_dest_cfg_cmd_1),
0x120,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_dest_cfg_cmd_1", fep_nu_dest_cfg_cmd_1_prop);
fld_map_t fep_nu_dest_cfg_cmd_2 {
CREATE_ENTRY("cmd16_vld", 0, 1),
CREATE_ENTRY("cmd16_lid", 1, 5),
CREATE_ENTRY("cmd17_vld", 6, 1),
CREATE_ENTRY("cmd17_lid", 7, 5),
CREATE_ENTRY("cmd18_vld", 12, 1),
CREATE_ENTRY("cmd18_lid", 13, 5),
CREATE_ENTRY("cmd19_vld", 18, 1),
CREATE_ENTRY("cmd19_lid", 19, 5),
CREATE_ENTRY("cmd20_vld", 24, 1),
CREATE_ENTRY("cmd20_lid", 25, 5),
CREATE_ENTRY("cmd21_vld", 30, 1),
CREATE_ENTRY("cmd21_lid", 31, 5),
CREATE_ENTRY("cmd22_vld", 36, 1),
CREATE_ENTRY("cmd22_lid", 37, 5),
CREATE_ENTRY("cmd23_vld", 42, 1),
CREATE_ENTRY("cmd23_lid", 43, 5),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fep_nu_dest_cfg_cmd_2_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_dest_cfg_cmd_2),
0x128,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_dest_cfg_cmd_2", fep_nu_dest_cfg_cmd_2_prop);
fld_map_t fep_nu_dest_cfg_cmd_3 {
CREATE_ENTRY("cmd24_vld", 0, 1),
CREATE_ENTRY("cmd24_lid", 1, 5),
CREATE_ENTRY("cmd25_vld", 6, 1),
CREATE_ENTRY("cmd25_lid", 7, 5),
CREATE_ENTRY("cmd26_vld", 12, 1),
CREATE_ENTRY("cmd26_lid", 13, 5),
CREATE_ENTRY("cmd27_vld", 18, 1),
CREATE_ENTRY("cmd27_lid", 19, 5),
CREATE_ENTRY("cmd28_vld", 24, 1),
CREATE_ENTRY("cmd28_lid", 25, 5),
CREATE_ENTRY("cmd29_vld", 30, 1),
CREATE_ENTRY("cmd29_lid", 31, 5),
CREATE_ENTRY("cmd30_vld", 36, 1),
CREATE_ENTRY("cmd30_lid", 37, 5),
CREATE_ENTRY("cmd31_vld", 42, 1),
CREATE_ENTRY("cmd31_lid", 43, 5),
CREATE_ENTRY("__rsvd", 48, 16)
};auto fep_nu_dest_cfg_cmd_3_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_dest_cfg_cmd_3),
0x130,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_dest_cfg_cmd_3", fep_nu_dest_cfg_cmd_3_prop);
fld_map_t fep_nu_hbm_ddr_hash {
CREATE_ENTRY("ddr_buf_mode", 0, 2),
CREATE_ENTRY("ddr_coh_mode", 2, 2),
CREATE_ENTRY("hbm_buf_mode", 4, 2),
CREATE_ENTRY("hbm_coh_mode", 6, 2),
CREATE_ENTRY("num_shard_log2", 8, 2),
CREATE_ENTRY("mask0", 10, 26),
CREATE_ENTRY("mask1", 36, 26),
CREATE_ENTRY("__rsvd", 62, 2)
};auto fep_nu_hbm_ddr_hash_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_hbm_ddr_hash),
0x138,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_hbm_ddr_hash", fep_nu_hbm_ddr_hash_prop);
fld_map_t fep_nu_ddr_hash {
CREATE_ENTRY("mask0", 0, 32),
CREATE_ENTRY("mask1", 32, 32)
};auto fep_nu_ddr_hash_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_ddr_hash),
0x140,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_ddr_hash", fep_nu_ddr_hash_prop);
fld_map_t fep_nu_addr_trans_hbm_pc_rsvd0_cfg {
CREATE_ENTRY("coh_base", 0, 5),
CREATE_ENTRY("coh_lid", 5, 5),
CREATE_ENTRY("buf_base", 10, 5),
CREATE_ENTRY("buf_lid", 15, 5),
CREATE_ENTRY("rsvd0_gid", 20, 5),
CREATE_ENTRY("rsvd0_lid", 25, 5),
CREATE_ENTRY("pc_gid_min", 30, 5),
CREATE_ENTRY("pc_gid_max", 35, 5),
CREATE_ENTRY("pc_lid0", 40, 5),
CREATE_ENTRY("pc_lid1", 45, 5),
CREATE_ENTRY("pc_lid2", 50, 5),
CREATE_ENTRY("pc_lid3", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto fep_nu_addr_trans_hbm_pc_rsvd0_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_addr_trans_hbm_pc_rsvd0_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_addr_trans_hbm_pc_rsvd0_cfg", fep_nu_addr_trans_hbm_pc_rsvd0_cfg_prop);
fld_map_t fep_nu_addr_trans_nu_mu_cfg {
CREATE_ENTRY("nu_gid_min", 0, 5),
CREATE_ENTRY("nu_gid_max", 5, 5),
CREATE_ENTRY("nu_lid0", 10, 5),
CREATE_ENTRY("nu_lid1", 15, 5),
CREATE_ENTRY("nu_lid2", 20, 5),
CREATE_ENTRY("nu_lid3", 25, 5),
CREATE_ENTRY("mu_gid_min", 30, 5),
CREATE_ENTRY("mu_gid_max", 35, 5),
CREATE_ENTRY("mu_lid0", 40, 5),
CREATE_ENTRY("mu_lid1", 45, 5),
CREATE_ENTRY("mu_lid2", 50, 5),
CREATE_ENTRY("mu_lid3", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto fep_nu_addr_trans_nu_mu_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_addr_trans_nu_mu_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_addr_trans_nu_mu_cfg", fep_nu_addr_trans_nu_mu_cfg_prop);
fld_map_t fep_nu_addr_trans_hu_nvram_ddr_cfg {
CREATE_ENTRY("hu_gid_min", 0, 5),
CREATE_ENTRY("hu_gid_max", 5, 5),
CREATE_ENTRY("hu_lid0", 10, 5),
CREATE_ENTRY("hu_lid1", 15, 5),
CREATE_ENTRY("hu_lid2", 20, 5),
CREATE_ENTRY("hu_lid3", 25, 5),
CREATE_ENTRY("nvram_base", 30, 5),
CREATE_ENTRY("nvram_lid", 35, 5),
CREATE_ENTRY("coh_base", 40, 5),
CREATE_ENTRY("coh_lid", 45, 5),
CREATE_ENTRY("buf_base", 50, 5),
CREATE_ENTRY("buf_lid", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto fep_nu_addr_trans_hu_nvram_ddr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_addr_trans_hu_nvram_ddr_cfg),
0x158,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_addr_trans_hu_nvram_ddr_cfg", fep_nu_addr_trans_hu_nvram_ddr_cfg_prop);
fld_map_t fep_nu_addr_trans_rsvd1_cfg {
CREATE_ENTRY("addr_min", 0, 13),
CREATE_ENTRY("addr_max", 13, 13),
CREATE_ENTRY("gid", 26, 5),
CREATE_ENTRY("lid", 31, 5),
CREATE_ENTRY("__rsvd", 36, 28)
};auto fep_nu_addr_trans_rsvd1_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_addr_trans_rsvd1_cfg),
0x160,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_addr_trans_rsvd1_cfg", fep_nu_addr_trans_rsvd1_cfg_prop);
fld_map_t fep_nu_addr_trans_rsvd2_cfg {
CREATE_ENTRY("addr_min", 0, 13),
CREATE_ENTRY("addr_max", 13, 13),
CREATE_ENTRY("gid", 26, 5),
CREATE_ENTRY("lid", 31, 5),
CREATE_ENTRY("__rsvd", 36, 28)
};auto fep_nu_addr_trans_rsvd2_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_addr_trans_rsvd2_cfg),
0x168,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_addr_trans_rsvd2_cfg", fep_nu_addr_trans_rsvd2_cfg_prop);
fld_map_t fep_nu_addr_trans_default_cfg {
CREATE_ENTRY("gid", 0, 5),
CREATE_ENTRY("lid", 5, 5),
CREATE_ENTRY("__rsvd", 10, 54)
};auto fep_nu_addr_trans_default_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_addr_trans_default_cfg),
0x170,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_addr_trans_default_cfg", fep_nu_addr_trans_default_cfg_prop);
fld_map_t fep_nu_sn_msg_sent_incr_en {
CREATE_ENTRY("erp_vc0_en", 0, 1),
CREATE_ENTRY("erp_vc1_en", 1, 1),
CREATE_ENTRY("erp_vc2_en", 2, 1),
CREATE_ENTRY("erp_vc3_en", 3, 1),
CREATE_ENTRY("etp_vc0_en", 4, 1),
CREATE_ENTRY("etp_vc1_en", 5, 1),
CREATE_ENTRY("etp_vc2_en", 6, 1),
CREATE_ENTRY("etp_vc3_en", 7, 1),
CREATE_ENTRY("nwqm_vc0_en", 8, 1),
CREATE_ENTRY("nwqm_vc1_en", 9, 1),
CREATE_ENTRY("nwqm_vc2_en", 10, 1),
CREATE_ENTRY("nwqm_vc3_en", 11, 1),
CREATE_ENTRY("wro_vc0_en", 12, 1),
CREATE_ENTRY("wro_vc1_en", 13, 1),
CREATE_ENTRY("wro_vc2_en", 14, 1),
CREATE_ENTRY("wro_vc3_en", 15, 1),
CREATE_ENTRY("fae_vc0_en", 16, 1),
CREATE_ENTRY("fae_vc1_en", 17, 1),
CREATE_ENTRY("fae_vc2_en", 18, 1),
CREATE_ENTRY("fae_vc3_en", 19, 1),
CREATE_ENTRY("mpg_vc0_en", 20, 1),
CREATE_ENTRY("mpg_vc1_en", 21, 1),
CREATE_ENTRY("mpg_vc2_en", 22, 1),
CREATE_ENTRY("mpg_vc3_en", 23, 1),
CREATE_ENTRY("snx_vc0_en", 24, 1),
CREATE_ENTRY("snx_vc1_en", 25, 1),
CREATE_ENTRY("snx_vc2_en", 26, 1),
CREATE_ENTRY("snx_vc3_en", 27, 1),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fep_nu_sn_msg_sent_incr_en_prop = csr_prop_t(
std::make_shared<csr_s>(fep_nu_sn_msg_sent_incr_en),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(fep_nu_0, "fep_nu_sn_msg_sent_incr_en", fep_nu_sn_msg_sent_incr_en_prop);
 // END fep_nu 
}
{
 // BEGIN dnr 
auto dnr_0 = nu_rng[0].add_an({"fepw_nu","dnr"}, 0x14040000, 3, 0x80000);
fld_map_t dnr_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto dnr_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_timeout_thresh_cfg", dnr_timeout_thresh_cfg_prop);
fld_map_t dnr_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto dnr_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_timedout_sta", dnr_timedout_sta_prop);
fld_map_t dnr_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto dnr_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_timeout_clr", dnr_timeout_clr_prop);
fld_map_t dnr_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto dnr_features_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_features", dnr_features_prop);
fld_map_t dnr_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto dnr_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_spare_pio", dnr_spare_pio_prop);
fld_map_t dnr_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto dnr_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_scratchpad", dnr_scratchpad_prop);
fld_map_t dnr_alt_ej_port {
CREATE_ENTRY("val", 0, 3),
CREATE_ENTRY("__rsvd", 3, 61)
};auto dnr_alt_ej_port_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_alt_ej_port),
0x80,
CSR_TYPE::REG_LST,
1);
add_csr(dnr_0, "dnr_alt_ej_port", dnr_alt_ej_port_prop);
fld_map_t dnr_cong_ctrl {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("incl_last_router_ibuf_occ", 1, 1),
CREATE_ENTRY("green_thr_vc_set0", 2, 7),
CREATE_ENTRY("yellow_thr_vc_set0", 9, 7),
CREATE_ENTRY("orange_thr_vc_set0", 16, 7),
CREATE_ENTRY("red_thr_vc_set0", 23, 7),
CREATE_ENTRY("green_thr_vc_set1", 30, 7),
CREATE_ENTRY("yellow_thr_vc_set1", 37, 7),
CREATE_ENTRY("orange_thr_vc_set1", 44, 7),
CREATE_ENTRY("red_thr_vc_set1", 51, 7),
CREATE_ENTRY("__rsvd", 58, 6)
};auto dnr_cong_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_cong_ctrl),
0xA8,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_cong_ctrl", dnr_cong_ctrl_prop);
fld_map_t dnr_route_cfg {
CREATE_ENTRY("o1turn_en", 0, 1),
CREATE_ENTRY("adaptive_en", 1, 1),
CREATE_ENTRY("xy_en", 2, 1),
CREATE_ENTRY("adaptive_vc_sel_en", 3, 1),
CREATE_ENTRY("o1turn_vc_sel_en", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto dnr_route_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_route_cfg),
0xB0,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_route_cfg", dnr_route_cfg_prop);
fld_map_t dnr_vc_sel_wt_cfg {
CREATE_ENTRY("vc0_wt", 0, 2),
CREATE_ENTRY("vc1_wt", 2, 2),
CREATE_ENTRY("vc2_wt", 4, 2),
CREATE_ENTRY("vc3_wt", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto dnr_vc_sel_wt_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_vc_sel_wt_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_vc_sel_wt_cfg", dnr_vc_sel_wt_cfg_prop);
fld_map_t dnr_default_dgid_cfg {
CREATE_ENTRY("val", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto dnr_default_dgid_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_default_dgid_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_default_dgid_cfg", dnr_default_dgid_cfg_prop);
fld_map_t dnr_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto dnr_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_fla_ring_module_id_cfg),
0xD8,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_fla_ring_module_id_cfg", dnr_fla_ring_module_id_cfg_prop);
fld_map_t dnr_credit_watchdog_timer_cfg {
CREATE_ENTRY("val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto dnr_credit_watchdog_timer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_credit_watchdog_timer_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_credit_watchdog_timer_cfg", dnr_credit_watchdog_timer_cfg_prop);
fld_map_t dnr_dbg_ibuf_occ_cnt {
CREATE_ENTRY("ibuf0_occ_cnt", 0, 6),
CREATE_ENTRY("ibuf0_sticky_max_occ_cnt", 6, 6),
CREATE_ENTRY("ibuf1_occ_cnt", 12, 6),
CREATE_ENTRY("ibuf1_sticky_max_occ_cnt", 18, 6),
CREATE_ENTRY("ibuf2_occ_cnt", 24, 6),
CREATE_ENTRY("ibuf2_sticky_max_occ_cnt", 30, 6),
CREATE_ENTRY("ibuf3_occ_cnt", 36, 6),
CREATE_ENTRY("ibuf3_sticky_max_occ_cnt", 42, 6),
CREATE_ENTRY("ibuf4_occ_cnt", 48, 6),
CREATE_ENTRY("ibuf4_sticky_max_occ_cnt", 54, 6),
CREATE_ENTRY("__rsvd", 60, 4)
};auto dnr_dbg_ibuf_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_ibuf_occ_cnt),
0xE8,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_dbg_ibuf_occ_cnt", dnr_dbg_ibuf_occ_cnt_prop);
fld_map_t dnr_dbg_intf_buf_occ_cnt {
CREATE_ENTRY("injbuf_occ_cnt", 0, 5),
CREATE_ENTRY("injbuf_sticky_max_occ_cnt", 5, 5),
CREATE_ENTRY("ejbuf_occ_cnt", 10, 6),
CREATE_ENTRY("ejbuf_sticky_max_occ_cnt", 16, 6),
CREATE_ENTRY("__rsvd", 22, 42)
};auto dnr_dbg_intf_buf_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_intf_buf_occ_cnt),
0xF0,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_dbg_intf_buf_occ_cnt", dnr_dbg_intf_buf_occ_cnt_prop);
fld_map_t dnr_dbg_inj_credit_cnt {
CREATE_ENTRY("ibuf_rsvd_credits_vc0", 0, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc0", 5, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc1", 10, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc1", 15, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc2", 20, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc2", 25, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc3", 30, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc3", 35, 5),
CREATE_ENTRY("ibuf_shared_credits", 40, 5),
CREATE_ENTRY("__rsvd", 45, 19)
};auto dnr_dbg_inj_credit_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_inj_credit_cnt),
0xF8,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_dbg_inj_credit_cnt", dnr_dbg_inj_credit_cnt_prop);
fld_map_t dnr_dbg_ibuf_credit_cnt {
CREATE_ENTRY("ibuf_rsvd_credits_vc0", 0, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc0", 5, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc1", 10, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc1", 15, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc2", 20, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc2", 25, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc3", 30, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc3", 35, 5),
CREATE_ENTRY("ibuf_shared_credits", 40, 5),
CREATE_ENTRY("__rsvd", 45, 19)
};auto dnr_dbg_ibuf_credit_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_ibuf_credit_cnt),
0x100,
CSR_TYPE::REG_LST,
1);
add_csr(dnr_0, "dnr_dbg_ibuf_credit_cnt", dnr_dbg_ibuf_credit_cnt_prop);
fld_map_t dnr_dbg_ebuf_credit_cnt {
CREATE_ENTRY("ebuf_rsvd_credits_vc_set0", 0, 7),
CREATE_ENTRY("ebuf_shared_credits_usage_vc_set0", 7, 7),
CREATE_ENTRY("ebuf_rsvd_credits_vc_set1", 14, 7),
CREATE_ENTRY("ebuf_shared_credits_usage_vc_set1", 21, 7),
CREATE_ENTRY("ebuf_shared_credits", 28, 7),
CREATE_ENTRY("__rsvd", 35, 29)
};auto dnr_dbg_ebuf_credit_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_ebuf_credit_cnt),
0x120,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_dbg_ebuf_credit_cnt", dnr_dbg_ebuf_credit_cnt_prop);
fld_map_t dnr_intr_dgid_out_of_range_log {
CREATE_ENTRY("slid", 0, 5),
CREATE_ENTRY("dgid", 5, 5),
CREATE_ENTRY("dlid", 10, 5),
CREATE_ENTRY("vc_set", 15, 1),
CREATE_ENTRY("mdata_flags", 16, 4),
CREATE_ENTRY("__rsvd", 20, 44)
};auto dnr_intr_dgid_out_of_range_log_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_intr_dgid_out_of_range_log),
0x128,
CSR_TYPE::REG,
1);
add_csr(dnr_0, "dnr_intr_dgid_out_of_range_log", dnr_intr_dgid_out_of_range_log_prop);
 // END dnr 
}
{
 // BEGIN dnr 
auto dnr_1 = nu_rng[0].add_an({"fepw_hnu","dnr"}, 0x140C0000, 2, 0x80000);
fld_map_t dnr_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto dnr_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_timeout_thresh_cfg", dnr_timeout_thresh_cfg_prop);
fld_map_t dnr_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto dnr_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_timedout_sta", dnr_timedout_sta_prop);
fld_map_t dnr_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto dnr_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_timeout_clr", dnr_timeout_clr_prop);
fld_map_t dnr_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto dnr_features_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_features", dnr_features_prop);
fld_map_t dnr_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto dnr_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_spare_pio", dnr_spare_pio_prop);
fld_map_t dnr_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto dnr_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_scratchpad", dnr_scratchpad_prop);
fld_map_t dnr_alt_ej_port {
CREATE_ENTRY("val", 0, 3),
CREATE_ENTRY("__rsvd", 3, 61)
};auto dnr_alt_ej_port_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_alt_ej_port),
0x80,
CSR_TYPE::REG_LST,
1);
add_csr(dnr_1, "dnr_alt_ej_port", dnr_alt_ej_port_prop);
fld_map_t dnr_cong_ctrl {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("incl_last_router_ibuf_occ", 1, 1),
CREATE_ENTRY("green_thr_vc_set0", 2, 7),
CREATE_ENTRY("yellow_thr_vc_set0", 9, 7),
CREATE_ENTRY("orange_thr_vc_set0", 16, 7),
CREATE_ENTRY("red_thr_vc_set0", 23, 7),
CREATE_ENTRY("green_thr_vc_set1", 30, 7),
CREATE_ENTRY("yellow_thr_vc_set1", 37, 7),
CREATE_ENTRY("orange_thr_vc_set1", 44, 7),
CREATE_ENTRY("red_thr_vc_set1", 51, 7),
CREATE_ENTRY("__rsvd", 58, 6)
};auto dnr_cong_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_cong_ctrl),
0xA8,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_cong_ctrl", dnr_cong_ctrl_prop);
fld_map_t dnr_route_cfg {
CREATE_ENTRY("o1turn_en", 0, 1),
CREATE_ENTRY("adaptive_en", 1, 1),
CREATE_ENTRY("xy_en", 2, 1),
CREATE_ENTRY("adaptive_vc_sel_en", 3, 1),
CREATE_ENTRY("o1turn_vc_sel_en", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto dnr_route_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_route_cfg),
0xB0,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_route_cfg", dnr_route_cfg_prop);
fld_map_t dnr_vc_sel_wt_cfg {
CREATE_ENTRY("vc0_wt", 0, 2),
CREATE_ENTRY("vc1_wt", 2, 2),
CREATE_ENTRY("vc2_wt", 4, 2),
CREATE_ENTRY("vc3_wt", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto dnr_vc_sel_wt_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_vc_sel_wt_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_vc_sel_wt_cfg", dnr_vc_sel_wt_cfg_prop);
fld_map_t dnr_default_dgid_cfg {
CREATE_ENTRY("val", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto dnr_default_dgid_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_default_dgid_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_default_dgid_cfg", dnr_default_dgid_cfg_prop);
fld_map_t dnr_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto dnr_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_fla_ring_module_id_cfg),
0xD8,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_fla_ring_module_id_cfg", dnr_fla_ring_module_id_cfg_prop);
fld_map_t dnr_credit_watchdog_timer_cfg {
CREATE_ENTRY("val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto dnr_credit_watchdog_timer_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_credit_watchdog_timer_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_credit_watchdog_timer_cfg", dnr_credit_watchdog_timer_cfg_prop);
fld_map_t dnr_dbg_ibuf_occ_cnt {
CREATE_ENTRY("ibuf0_occ_cnt", 0, 6),
CREATE_ENTRY("ibuf0_sticky_max_occ_cnt", 6, 6),
CREATE_ENTRY("ibuf1_occ_cnt", 12, 6),
CREATE_ENTRY("ibuf1_sticky_max_occ_cnt", 18, 6),
CREATE_ENTRY("ibuf2_occ_cnt", 24, 6),
CREATE_ENTRY("ibuf2_sticky_max_occ_cnt", 30, 6),
CREATE_ENTRY("ibuf3_occ_cnt", 36, 6),
CREATE_ENTRY("ibuf3_sticky_max_occ_cnt", 42, 6),
CREATE_ENTRY("ibuf4_occ_cnt", 48, 6),
CREATE_ENTRY("ibuf4_sticky_max_occ_cnt", 54, 6),
CREATE_ENTRY("__rsvd", 60, 4)
};auto dnr_dbg_ibuf_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_ibuf_occ_cnt),
0xE8,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_dbg_ibuf_occ_cnt", dnr_dbg_ibuf_occ_cnt_prop);
fld_map_t dnr_dbg_intf_buf_occ_cnt {
CREATE_ENTRY("injbuf_occ_cnt", 0, 5),
CREATE_ENTRY("injbuf_sticky_max_occ_cnt", 5, 5),
CREATE_ENTRY("ejbuf_occ_cnt", 10, 6),
CREATE_ENTRY("ejbuf_sticky_max_occ_cnt", 16, 6),
CREATE_ENTRY("__rsvd", 22, 42)
};auto dnr_dbg_intf_buf_occ_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_intf_buf_occ_cnt),
0xF0,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_dbg_intf_buf_occ_cnt", dnr_dbg_intf_buf_occ_cnt_prop);
fld_map_t dnr_dbg_inj_credit_cnt {
CREATE_ENTRY("ibuf_rsvd_credits_vc0", 0, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc0", 5, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc1", 10, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc1", 15, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc2", 20, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc2", 25, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc3", 30, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc3", 35, 5),
CREATE_ENTRY("ibuf_shared_credits", 40, 5),
CREATE_ENTRY("__rsvd", 45, 19)
};auto dnr_dbg_inj_credit_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_inj_credit_cnt),
0xF8,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_dbg_inj_credit_cnt", dnr_dbg_inj_credit_cnt_prop);
fld_map_t dnr_dbg_ibuf_credit_cnt {
CREATE_ENTRY("ibuf_rsvd_credits_vc0", 0, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc0", 5, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc1", 10, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc1", 15, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc2", 20, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc2", 25, 5),
CREATE_ENTRY("ibuf_rsvd_credits_vc3", 30, 5),
CREATE_ENTRY("ibuf_shared_credits_usage_vc3", 35, 5),
CREATE_ENTRY("ibuf_shared_credits", 40, 5),
CREATE_ENTRY("__rsvd", 45, 19)
};auto dnr_dbg_ibuf_credit_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_ibuf_credit_cnt),
0x100,
CSR_TYPE::REG_LST,
1);
add_csr(dnr_1, "dnr_dbg_ibuf_credit_cnt", dnr_dbg_ibuf_credit_cnt_prop);
fld_map_t dnr_dbg_ebuf_credit_cnt {
CREATE_ENTRY("ebuf_rsvd_credits_vc_set0", 0, 7),
CREATE_ENTRY("ebuf_shared_credits_usage_vc_set0", 7, 7),
CREATE_ENTRY("ebuf_rsvd_credits_vc_set1", 14, 7),
CREATE_ENTRY("ebuf_shared_credits_usage_vc_set1", 21, 7),
CREATE_ENTRY("ebuf_shared_credits", 28, 7),
CREATE_ENTRY("__rsvd", 35, 29)
};auto dnr_dbg_ebuf_credit_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_dbg_ebuf_credit_cnt),
0x120,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_dbg_ebuf_credit_cnt", dnr_dbg_ebuf_credit_cnt_prop);
fld_map_t dnr_intr_dgid_out_of_range_log {
CREATE_ENTRY("slid", 0, 5),
CREATE_ENTRY("dgid", 5, 5),
CREATE_ENTRY("dlid", 10, 5),
CREATE_ENTRY("vc_set", 15, 1),
CREATE_ENTRY("mdata_flags", 16, 4),
CREATE_ENTRY("__rsvd", 20, 44)
};auto dnr_intr_dgid_out_of_range_log_prop = csr_prop_t(
std::make_shared<csr_s>(dnr_intr_dgid_out_of_range_log),
0x128,
CSR_TYPE::REG,
1);
add_csr(dnr_1, "dnr_intr_dgid_out_of_range_log", dnr_intr_dgid_out_of_range_log_prop);
 // END dnr 
}
{
 // BEGIN fep_hnu 
auto fep_hnu_0 = nu_rng[0].add_an({"fepw_hnu","fep_hnu"}, 0x14080000, 2, 0x80000);
fld_map_t fep_hnu_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fep_hnu_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_timeout_thresh_cfg", fep_hnu_timeout_thresh_cfg_prop);
fld_map_t fep_hnu_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fep_hnu_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_timedout_sta", fep_hnu_timedout_sta_prop);
fld_map_t fep_hnu_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fep_hnu_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_timeout_clr", fep_hnu_timeout_clr_prop);
fld_map_t fep_hnu_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fep_hnu_features_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_features", fep_hnu_features_prop);
fld_map_t fep_hnu_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fep_hnu_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_spare_pio", fep_hnu_spare_pio_prop);
fld_map_t fep_hnu_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fep_hnu_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_scratchpad", fep_hnu_scratchpad_prop);
fld_map_t fep_hnu_misc_cfg {
CREATE_ENTRY("addr_trans_dn_vc1_en", 0, 1),
CREATE_ENTRY("addr_trans_sn_vc3_en", 1, 1),
CREATE_ENTRY("addr_trans_sn_vc2_en", 2, 1),
CREATE_ENTRY("addr_trans_sn_vc1_en", 3, 1),
CREATE_ENTRY("addr_trans_sn_vc0_en", 4, 1),
CREATE_ENTRY("nwqm_wu_lid", 5, 2),
CREATE_ENTRY("remote_crd_load", 7, 1),
CREATE_ENTRY("enable", 8, 1),
CREATE_ENTRY("metadata_err_drop_dis", 9, 1),
CREATE_ENTRY("hbm_stacked_mode", 10, 1),
CREATE_ENTRY("ddr_stacked_mode", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto fep_hnu_misc_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_misc_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_misc_cfg", fep_hnu_misc_cfg_prop);
fld_map_t fep_hnu_mem_err_inj_cfg {
CREATE_ENTRY("ibuf_mem_metadata", 0, 1),
CREATE_ENTRY("ibuf_mem_data", 1, 1),
CREATE_ENTRY("err_type", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto fep_hnu_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_mem_err_inj_cfg),
0x88,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_mem_err_inj_cfg", fep_hnu_mem_err_inj_cfg_prop);
fld_map_t fep_hnu_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_hnu_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_fla_ring_module_id_cfg),
0x90,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_fla_ring_module_id_cfg", fep_hnu_fla_ring_module_id_cfg_prop);
fld_map_t fep_hnu_fla_cfg {
CREATE_ENTRY("mux_sel_0", 0, 7),
CREATE_ENTRY("mux_sel_1", 7, 7),
CREATE_ENTRY("mux_sel_2", 14, 7),
CREATE_ENTRY("mux_sel_3", 21, 7),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fep_hnu_fla_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_fla_cfg),
0x98,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_fla_cfg", fep_hnu_fla_cfg_prop);
fld_map_t fep_hnu_fla_sta {
CREATE_ENTRY("dbus_0", 0, 16),
CREATE_ENTRY("dbus_1", 16, 16),
CREATE_ENTRY("dbus_2", 32, 16),
CREATE_ENTRY("dbus_3", 48, 16)
};auto fep_hnu_fla_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_fla_sta),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_fla_sta", fep_hnu_fla_sta_prop);
fld_map_t fep_hnu_local_id {
CREATE_ENTRY("erp_local_id", 0, 5),
CREATE_ENTRY("etp_min_local_id", 5, 5),
CREATE_ENTRY("nwqm_local_id", 10, 5),
CREATE_ENTRY("wro_local_id", 15, 5),
CREATE_ENTRY("tgt_min_local_id", 20, 5),
CREATE_ENTRY("hdma_min_local_id", 25, 5),
CREATE_ENTRY("cmn_local_id", 30, 5),
CREATE_ENTRY("hdma_o_local_id", 35, 5),
CREATE_ENTRY("etp_max_local_id", 40, 5),
CREATE_ENTRY("tgt_max_local_id", 45, 5),
CREATE_ENTRY("hdma_max_local_id", 50, 5),
CREATE_ENTRY("__rsvd", 55, 9)
};auto fep_hnu_local_id_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_local_id),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_local_id", fep_hnu_local_id_prop);
fld_map_t fep_hnu_strict_order {
CREATE_ENTRY("erp_strict_ord", 0, 1),
CREATE_ENTRY("erp_strict_ord_for_pwr", 1, 1),
CREATE_ENTRY("nwqm_strict_ord", 2, 1),
CREATE_ENTRY("nwqm_strict_ord_for_pwr", 3, 1),
CREATE_ENTRY("tgt_strict_ord", 4, 1),
CREATE_ENTRY("tgt_strict_ord_for_pwr", 5, 1),
CREATE_ENTRY("hdma_o_strict_ord", 6, 1),
CREATE_ENTRY("hdma_o_strict_ord_for_pwr", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_hnu_strict_order_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_strict_order),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_strict_order", fep_hnu_strict_order_prop);
fld_map_t fep_hnu_erp_snx_cdt_init_val {
CREATE_ENTRY("erp_vc0_cdt", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fep_hnu_erp_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_erp_snx_cdt_init_val),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_erp_snx_cdt_init_val", fep_hnu_erp_snx_cdt_init_val_prop);
fld_map_t fep_hnu_nwqm_snx_cdt_init_val {
CREATE_ENTRY("nwqm_vc0_cdt", 0, 8),
CREATE_ENTRY("nwqm_vc1_cdt", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fep_hnu_nwqm_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_nwqm_snx_cdt_init_val),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_nwqm_snx_cdt_init_val", fep_hnu_nwqm_snx_cdt_init_val_prop);
fld_map_t fep_hnu_wro_snx_cdt_init_val {
CREATE_ENTRY("wro_vc0_cdt", 0, 8),
CREATE_ENTRY("wro_vc2_cdt", 8, 8),
CREATE_ENTRY("wro_vc3_cdt", 16, 8),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fep_hnu_wro_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_wro_snx_cdt_init_val),
0xC8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_wro_snx_cdt_init_val", fep_hnu_wro_snx_cdt_init_val_prop);
fld_map_t fep_hnu_cmn_snx_cdt_init_val {
CREATE_ENTRY("cmn_vc0_cdt", 0, 8),
CREATE_ENTRY("cmn_vc1_cdt", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fep_hnu_cmn_snx_cdt_init_val_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_cmn_snx_cdt_init_val),
0xD0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_cmn_snx_cdt_init_val", fep_hnu_cmn_snx_cdt_init_val_prop);
fld_map_t fep_hnu_erp_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_hnu_erp_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_erp_sn_filter),
0xD8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_erp_sn_filter", fep_hnu_erp_sn_filter_prop);
fld_map_t fep_hnu_nwqm_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_hnu_nwqm_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_nwqm_sn_filter),
0xE0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_nwqm_sn_filter", fep_hnu_nwqm_sn_filter_prop);
fld_map_t fep_hnu_hdma_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_hnu_hdma_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_hdma_sn_filter),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_hdma_sn_filter", fep_hnu_hdma_sn_filter_prop);
fld_map_t fep_hnu_cmn_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_hnu_cmn_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_cmn_sn_filter),
0xF0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_cmn_sn_filter", fep_hnu_cmn_sn_filter_prop);
fld_map_t fep_hnu_snx_sn_filter {
CREATE_ENTRY("permitted_cmds", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_hnu_snx_sn_filter_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_snx_sn_filter),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_snx_sn_filter", fep_hnu_snx_sn_filter_prop);
fld_map_t fep_hnu_nwqm_lsn_arb_cfg {
CREATE_ENTRY("gr_wt_in0", 0, 4),
CREATE_ENTRY("wrr_wt_in0", 4, 4),
CREATE_ENTRY("gr_wt_in1", 8, 4),
CREATE_ENTRY("wrr_wt_in1", 12, 4),
CREATE_ENTRY("gr_wt_in2", 16, 4),
CREATE_ENTRY("wrr_wt_in2", 20, 4),
CREATE_ENTRY("gr_wt_in3", 24, 4),
CREATE_ENTRY("wrr_wt_in3", 28, 4),
CREATE_ENTRY("gr_per_in", 32, 8),
CREATE_ENTRY("__rsvd", 40, 24)
};auto fep_hnu_nwqm_lsn_arb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_nwqm_lsn_arb_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_nwqm_lsn_arb_cfg", fep_hnu_nwqm_lsn_arb_cfg_prop);
fld_map_t fep_hnu_cmn_lsn_arb_cfg {
CREATE_ENTRY("gr_wt_in0", 0, 4),
CREATE_ENTRY("wrr_wt_in0", 4, 4),
CREATE_ENTRY("gr_wt_in1", 8, 4),
CREATE_ENTRY("wrr_wt_in1", 12, 4),
CREATE_ENTRY("gr_per_in", 16, 8),
CREATE_ENTRY("__rsvd", 24, 40)
};auto fep_hnu_cmn_lsn_arb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_cmn_lsn_arb_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_cmn_lsn_arb_cfg", fep_hnu_cmn_lsn_arb_cfg_prop);
fld_map_t fep_hnu_snx_lsn_arb_cfg {
CREATE_ENTRY("gr_wt_in0", 0, 4),
CREATE_ENTRY("wrr_wt_in0", 4, 4),
CREATE_ENTRY("gr_wt_in1", 8, 4),
CREATE_ENTRY("wrr_wt_in1", 12, 4),
CREATE_ENTRY("gr_wt_in2", 16, 4),
CREATE_ENTRY("wrr_wt_in2", 20, 4),
CREATE_ENTRY("gr_wt_in3", 24, 4),
CREATE_ENTRY("wrr_wt_in3", 28, 4),
CREATE_ENTRY("gr_per_in", 32, 8),
CREATE_ENTRY("__rsvd", 40, 24)
};auto fep_hnu_snx_lsn_arb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_snx_lsn_arb_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_snx_lsn_arb_cfg", fep_hnu_snx_lsn_arb_cfg_prop);
fld_map_t fep_hnu_dest_cfg_cmd_0 {
CREATE_ENTRY("cmd0_wu_routing_mode", 0, 1),
CREATE_ENTRY("cmd0_vld", 1, 1),
CREATE_ENTRY("cmd0_lid", 2, 5),
CREATE_ENTRY("cmd1_wu_routing_mode", 7, 1),
CREATE_ENTRY("cmd1_vld", 8, 1),
CREATE_ENTRY("cmd1_lid", 9, 5),
CREATE_ENTRY("cmd2_wu_routing_mode", 14, 1),
CREATE_ENTRY("cmd2_vld", 15, 1),
CREATE_ENTRY("cmd2_lid", 16, 5),
CREATE_ENTRY("cmd3_wu_routing_mode", 21, 1),
CREATE_ENTRY("cmd3_vld", 22, 1),
CREATE_ENTRY("cmd3_lid", 23, 5),
CREATE_ENTRY("cmd4_wu_routing_mode", 28, 1),
CREATE_ENTRY("cmd4_vld", 29, 1),
CREATE_ENTRY("cmd4_lid", 30, 5),
CREATE_ENTRY("cmd5_wu_routing_mode", 35, 1),
CREATE_ENTRY("cmd5_vld", 36, 1),
CREATE_ENTRY("cmd5_lid", 37, 5),
CREATE_ENTRY("cmd6_wu_routing_mode", 42, 1),
CREATE_ENTRY("cmd6_vld", 43, 1),
CREATE_ENTRY("cmd6_lid", 44, 5),
CREATE_ENTRY("cmd7_wu_routing_mode", 49, 1),
CREATE_ENTRY("cmd7_vld", 50, 1),
CREATE_ENTRY("cmd7_lid", 51, 5),
CREATE_ENTRY("__rsvd", 56, 8)
};auto fep_hnu_dest_cfg_cmd_0_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_dest_cfg_cmd_0),
0x118,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_dest_cfg_cmd_0", fep_hnu_dest_cfg_cmd_0_prop);
fld_map_t fep_hnu_dest_cfg_cmd_1 {
CREATE_ENTRY("cmd8_wu_routing_mode", 0, 1),
CREATE_ENTRY("cmd8_vld", 1, 1),
CREATE_ENTRY("cmd8_lid", 2, 5),
CREATE_ENTRY("cmd9_wu_routing_mode", 7, 1),
CREATE_ENTRY("cmd9_vld", 8, 1),
CREATE_ENTRY("cmd9_lid", 9, 5),
CREATE_ENTRY("cmd10_wu_routing_mode", 14, 1),
CREATE_ENTRY("cmd10_vld", 15, 1),
CREATE_ENTRY("cmd10_lid", 16, 5),
CREATE_ENTRY("cmd11_wu_routing_mode", 21, 1),
CREATE_ENTRY("cmd11_vld", 22, 1),
CREATE_ENTRY("cmd11_lid", 23, 5),
CREATE_ENTRY("cmd12_wu_routing_mode", 28, 1),
CREATE_ENTRY("cmd12_vld", 29, 1),
CREATE_ENTRY("cmd12_lid", 30, 5),
CREATE_ENTRY("cmd13_wu_routing_mode", 35, 1),
CREATE_ENTRY("cmd13_vld", 36, 1),
CREATE_ENTRY("cmd13_lid", 37, 5),
CREATE_ENTRY("cmd14_wu_routing_mode", 42, 1),
CREATE_ENTRY("cmd14_vld", 43, 1),
CREATE_ENTRY("cmd14_lid", 44, 5),
CREATE_ENTRY("cmd15_wu_routing_mode", 49, 1),
CREATE_ENTRY("cmd15_vld", 50, 1),
CREATE_ENTRY("cmd15_lid", 51, 5),
CREATE_ENTRY("__rsvd", 56, 8)
};auto fep_hnu_dest_cfg_cmd_1_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_dest_cfg_cmd_1),
0x120,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_dest_cfg_cmd_1", fep_hnu_dest_cfg_cmd_1_prop);
fld_map_t fep_hnu_dest_cfg_cmd_2 {
CREATE_ENTRY("cmd16_wu_routing_mode", 0, 1),
CREATE_ENTRY("cmd16_vld", 1, 1),
CREATE_ENTRY("cmd16_lid", 2, 5),
CREATE_ENTRY("cmd17_wu_routing_mode", 7, 1),
CREATE_ENTRY("cmd17_vld", 8, 1),
CREATE_ENTRY("cmd17_lid", 9, 5),
CREATE_ENTRY("cmd18_wu_routing_mode", 14, 1),
CREATE_ENTRY("cmd18_vld", 15, 1),
CREATE_ENTRY("cmd18_lid", 16, 5),
CREATE_ENTRY("cmd19_wu_routing_mode", 21, 1),
CREATE_ENTRY("cmd19_vld", 22, 1),
CREATE_ENTRY("cmd19_lid", 23, 5),
CREATE_ENTRY("cmd20_wu_routing_mode", 28, 1),
CREATE_ENTRY("cmd20_vld", 29, 1),
CREATE_ENTRY("cmd20_lid", 30, 5),
CREATE_ENTRY("cmd21_wu_routing_mode", 35, 1),
CREATE_ENTRY("cmd21_vld", 36, 1),
CREATE_ENTRY("cmd21_lid", 37, 5),
CREATE_ENTRY("cmd22_wu_routing_mode", 42, 1),
CREATE_ENTRY("cmd22_vld", 43, 1),
CREATE_ENTRY("cmd22_lid", 44, 5),
CREATE_ENTRY("cmd23_wu_routing_mode", 49, 1),
CREATE_ENTRY("cmd23_vld", 50, 1),
CREATE_ENTRY("cmd23_lid", 51, 5),
CREATE_ENTRY("__rsvd", 56, 8)
};auto fep_hnu_dest_cfg_cmd_2_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_dest_cfg_cmd_2),
0x128,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_dest_cfg_cmd_2", fep_hnu_dest_cfg_cmd_2_prop);
fld_map_t fep_hnu_dest_cfg_cmd_3 {
CREATE_ENTRY("cmd24_wu_routing_mode", 0, 1),
CREATE_ENTRY("cmd24_vld", 1, 1),
CREATE_ENTRY("cmd24_lid", 2, 5),
CREATE_ENTRY("cmd25_wu_routing_mode", 7, 1),
CREATE_ENTRY("cmd25_vld", 8, 1),
CREATE_ENTRY("cmd25_lid", 9, 5),
CREATE_ENTRY("cmd26_wu_routing_mode", 14, 1),
CREATE_ENTRY("cmd26_vld", 15, 1),
CREATE_ENTRY("cmd26_lid", 16, 5),
CREATE_ENTRY("cmd27_wu_routing_mode", 21, 1),
CREATE_ENTRY("cmd27_vld", 22, 1),
CREATE_ENTRY("cmd27_lid", 23, 5),
CREATE_ENTRY("cmd28_wu_routing_mode", 28, 1),
CREATE_ENTRY("cmd28_vld", 29, 1),
CREATE_ENTRY("cmd28_lid", 30, 5),
CREATE_ENTRY("cmd29_wu_routing_mode", 35, 1),
CREATE_ENTRY("cmd29_vld", 36, 1),
CREATE_ENTRY("cmd29_lid", 37, 5),
CREATE_ENTRY("cmd30_wu_routing_mode", 42, 1),
CREATE_ENTRY("cmd30_vld", 43, 1),
CREATE_ENTRY("cmd30_lid", 44, 5),
CREATE_ENTRY("cmd31_wu_routing_mode", 49, 1),
CREATE_ENTRY("cmd31_vld", 50, 1),
CREATE_ENTRY("cmd31_lid", 51, 5),
CREATE_ENTRY("__rsvd", 56, 8)
};auto fep_hnu_dest_cfg_cmd_3_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_dest_cfg_cmd_3),
0x130,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_dest_cfg_cmd_3", fep_hnu_dest_cfg_cmd_3_prop);
fld_map_t fep_hnu_hbm_ddr_hash {
CREATE_ENTRY("ddr_buf_mode", 0, 2),
CREATE_ENTRY("ddr_coh_mode", 2, 2),
CREATE_ENTRY("hbm_buf_mode", 4, 2),
CREATE_ENTRY("hbm_coh_mode", 6, 2),
CREATE_ENTRY("num_shard_log2", 8, 2),
CREATE_ENTRY("mask0", 10, 26),
CREATE_ENTRY("mask1", 36, 26),
CREATE_ENTRY("__rsvd", 62, 2)
};auto fep_hnu_hbm_ddr_hash_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_hbm_ddr_hash),
0x138,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_hbm_ddr_hash", fep_hnu_hbm_ddr_hash_prop);
fld_map_t fep_hnu_ddr_hash {
CREATE_ENTRY("mask0", 0, 32),
CREATE_ENTRY("mask1", 32, 32)
};auto fep_hnu_ddr_hash_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_ddr_hash),
0x140,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_ddr_hash", fep_hnu_ddr_hash_prop);
fld_map_t fep_hnu_addr_trans_hbm_pc_rsvd0_cfg {
CREATE_ENTRY("coh_base", 0, 5),
CREATE_ENTRY("coh_lid", 5, 5),
CREATE_ENTRY("buf_base", 10, 5),
CREATE_ENTRY("buf_lid", 15, 5),
CREATE_ENTRY("rsvd0_gid", 20, 5),
CREATE_ENTRY("rsvd0_lid", 25, 5),
CREATE_ENTRY("pc_gid_min", 30, 5),
CREATE_ENTRY("pc_gid_max", 35, 5),
CREATE_ENTRY("pc_lid0", 40, 5),
CREATE_ENTRY("pc_lid1", 45, 5),
CREATE_ENTRY("pc_lid2", 50, 5),
CREATE_ENTRY("pc_lid3", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto fep_hnu_addr_trans_hbm_pc_rsvd0_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_addr_trans_hbm_pc_rsvd0_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_addr_trans_hbm_pc_rsvd0_cfg", fep_hnu_addr_trans_hbm_pc_rsvd0_cfg_prop);
fld_map_t fep_hnu_addr_trans_nu_mu_cfg {
CREATE_ENTRY("nu_gid_min", 0, 5),
CREATE_ENTRY("nu_gid_max", 5, 5),
CREATE_ENTRY("nu_lid0", 10, 5),
CREATE_ENTRY("nu_lid1", 15, 5),
CREATE_ENTRY("nu_lid2", 20, 5),
CREATE_ENTRY("nu_lid3", 25, 5),
CREATE_ENTRY("mu_gid_min", 30, 5),
CREATE_ENTRY("mu_gid_max", 35, 5),
CREATE_ENTRY("mu_lid0", 40, 5),
CREATE_ENTRY("mu_lid1", 45, 5),
CREATE_ENTRY("mu_lid2", 50, 5),
CREATE_ENTRY("mu_lid3", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto fep_hnu_addr_trans_nu_mu_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_addr_trans_nu_mu_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_addr_trans_nu_mu_cfg", fep_hnu_addr_trans_nu_mu_cfg_prop);
fld_map_t fep_hnu_addr_trans_hu_nvram_ddr_cfg {
CREATE_ENTRY("hu_gid_min", 0, 5),
CREATE_ENTRY("hu_gid_max", 5, 5),
CREATE_ENTRY("hu_lid0", 10, 5),
CREATE_ENTRY("hu_lid1", 15, 5),
CREATE_ENTRY("hu_lid2", 20, 5),
CREATE_ENTRY("hu_lid3", 25, 5),
CREATE_ENTRY("nvram_base", 30, 5),
CREATE_ENTRY("nvram_lid", 35, 5),
CREATE_ENTRY("coh_base", 40, 5),
CREATE_ENTRY("coh_lid", 45, 5),
CREATE_ENTRY("buf_base", 50, 5),
CREATE_ENTRY("buf_lid", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto fep_hnu_addr_trans_hu_nvram_ddr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_addr_trans_hu_nvram_ddr_cfg),
0x158,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_addr_trans_hu_nvram_ddr_cfg", fep_hnu_addr_trans_hu_nvram_ddr_cfg_prop);
fld_map_t fep_hnu_addr_trans_rsvd1_cfg {
CREATE_ENTRY("addr_min", 0, 13),
CREATE_ENTRY("addr_max", 13, 13),
CREATE_ENTRY("gid", 26, 5),
CREATE_ENTRY("lid", 31, 5),
CREATE_ENTRY("__rsvd", 36, 28)
};auto fep_hnu_addr_trans_rsvd1_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_addr_trans_rsvd1_cfg),
0x160,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_addr_trans_rsvd1_cfg", fep_hnu_addr_trans_rsvd1_cfg_prop);
fld_map_t fep_hnu_addr_trans_rsvd2_cfg {
CREATE_ENTRY("addr_min", 0, 13),
CREATE_ENTRY("addr_max", 13, 13),
CREATE_ENTRY("gid", 26, 5),
CREATE_ENTRY("lid", 31, 5),
CREATE_ENTRY("__rsvd", 36, 28)
};auto fep_hnu_addr_trans_rsvd2_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_addr_trans_rsvd2_cfg),
0x168,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_addr_trans_rsvd2_cfg", fep_hnu_addr_trans_rsvd2_cfg_prop);
fld_map_t fep_hnu_addr_trans_default_cfg {
CREATE_ENTRY("gid", 0, 5),
CREATE_ENTRY("lid", 5, 5),
CREATE_ENTRY("__rsvd", 10, 54)
};auto fep_hnu_addr_trans_default_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_addr_trans_default_cfg),
0x170,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_addr_trans_default_cfg", fep_hnu_addr_trans_default_cfg_prop);
fld_map_t fep_hnu_sn_msg_sent_incr_en {
CREATE_ENTRY("erp_vc0_en", 0, 1),
CREATE_ENTRY("erp_vc1_en", 1, 1),
CREATE_ENTRY("erp_vc2_en", 2, 1),
CREATE_ENTRY("erp_vc3_en", 3, 1),
CREATE_ENTRY("etp_vc0_en", 4, 1),
CREATE_ENTRY("etp_vc1_en", 5, 1),
CREATE_ENTRY("etp_vc2_en", 6, 1),
CREATE_ENTRY("etp_vc3_en", 7, 1),
CREATE_ENTRY("nwqm_vc0_en", 8, 1),
CREATE_ENTRY("nwqm_vc1_en", 9, 1),
CREATE_ENTRY("nwqm_vc2_en", 10, 1),
CREATE_ENTRY("nwqm_vc3_en", 11, 1),
CREATE_ENTRY("wro_vc0_en", 12, 1),
CREATE_ENTRY("wro_vc1_en", 13, 1),
CREATE_ENTRY("wro_vc2_en", 14, 1),
CREATE_ENTRY("wro_vc3_en", 15, 1),
CREATE_ENTRY("tgt_vc0_en", 16, 1),
CREATE_ENTRY("tgt_vc1_en", 17, 1),
CREATE_ENTRY("tgt_vc2_en", 18, 1),
CREATE_ENTRY("tgt_vc3_en", 19, 1),
CREATE_ENTRY("hdma_vc0_en", 20, 1),
CREATE_ENTRY("hdma_vc1_en", 21, 1),
CREATE_ENTRY("hdma_vc2_en", 22, 1),
CREATE_ENTRY("hdma_vc3_en", 23, 1),
CREATE_ENTRY("cmn_vc0_en", 24, 1),
CREATE_ENTRY("cmn_vc1_en", 25, 1),
CREATE_ENTRY("cmn_vc2_en", 26, 1),
CREATE_ENTRY("cmn_vc3_en", 27, 1),
CREATE_ENTRY("snx_vc0_en", 28, 1),
CREATE_ENTRY("snx_vc1_en", 29, 1),
CREATE_ENTRY("snx_vc2_en", 30, 1),
CREATE_ENTRY("snx_vc3_en", 31, 1),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fep_hnu_sn_msg_sent_incr_en_prop = csr_prop_t(
std::make_shared<csr_s>(fep_hnu_sn_msg_sent_incr_en),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(fep_hnu_0, "fep_hnu_sn_msg_sent_incr_en", fep_hnu_sn_msg_sent_incr_en_prop);
 // END fep_hnu 
}
{
 // BEGIN nu_fae 
auto nu_fae_0 = nu_rng[0].add_an({"nu_fae"}, 0x14400000, 1, 0x0);
fld_map_t nu_fae_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nu_fae_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fae_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "nu_fae_timeout_thresh_cfg", nu_fae_timeout_thresh_cfg_prop);
fld_map_t nu_fae_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_fae_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fae_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "nu_fae_timedout_sta", nu_fae_timedout_sta_prop);
fld_map_t nu_fae_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_fae_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fae_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "nu_fae_timeout_clr", nu_fae_timeout_clr_prop);
fld_map_t nu_fae_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto nu_fae_features_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fae_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "nu_fae_features", nu_fae_features_prop);
fld_map_t nu_fae_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto nu_fae_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fae_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "nu_fae_spare_pio", nu_fae_spare_pio_prop);
fld_map_t nu_fae_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto nu_fae_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fae_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "nu_fae_scratchpad", nu_fae_scratchpad_prop);
fld_map_t fae_wu_req_que_ncv_th_1 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_1_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_1),
0x90,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_1", fae_wu_req_que_ncv_th_1_prop);
fld_map_t fae_wu_req_que_ncv_th_2 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_2_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_2),
0x98,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_2", fae_wu_req_que_ncv_th_2_prop);
fld_map_t fae_wu_req_que_ncv_th_3 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_3_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_3),
0xA0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_3", fae_wu_req_que_ncv_th_3_prop);
fld_map_t fae_wu_req_que_ncv_th_4 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_4_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_4),
0xA8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_4", fae_wu_req_que_ncv_th_4_prop);
fld_map_t fae_wu_req_que_ncv_th_5 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_5_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_5),
0xB0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_5", fae_wu_req_que_ncv_th_5_prop);
fld_map_t fae_wu_req_que_ncv_th_6 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_6_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_6),
0xB8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_6", fae_wu_req_que_ncv_th_6_prop);
fld_map_t fae_wu_req_que_ncv_th_7 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_7_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_7),
0xC0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_7", fae_wu_req_que_ncv_th_7_prop);
fld_map_t fae_wu_req_que_ncv_th_8 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_8_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_8),
0xC8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_8", fae_wu_req_que_ncv_th_8_prop);
fld_map_t fae_wu_req_que_ncv_th_9 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_9_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_9),
0xD0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_9", fae_wu_req_que_ncv_th_9_prop);
fld_map_t fae_wu_req_que_ncv_th_10 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_10_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_10),
0xD8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_10", fae_wu_req_que_ncv_th_10_prop);
fld_map_t fae_wu_req_que_ncv_th_11 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_11_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_11),
0xE0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_11", fae_wu_req_que_ncv_th_11_prop);
fld_map_t fae_wu_req_que_ncv_th_12 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_12_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_12),
0xE8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_12", fae_wu_req_que_ncv_th_12_prop);
fld_map_t fae_wu_req_que_ncv_th_13 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_13_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_13),
0xF0,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_13", fae_wu_req_que_ncv_th_13_prop);
fld_map_t fae_wu_req_que_ncv_th_14 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_14_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_14),
0xF8,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_14", fae_wu_req_que_ncv_th_14_prop);
fld_map_t fae_wu_req_que_ncv_th_15 {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_wu_req_que_ncv_th_15_prop = csr_prop_t(
std::make_shared<csr_s>(fae_wu_req_que_ncv_th_15),
0x100,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_wu_req_que_ncv_th_15", fae_wu_req_que_ncv_th_15_prop);
fld_map_t fae_dma_xoff_thold {
CREATE_ENTRY("dma_occ_thold", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto fae_dma_xoff_thold_prop = csr_prop_t(
std::make_shared<csr_s>(fae_dma_xoff_thold),
0x120,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_dma_xoff_thold", fae_dma_xoff_thold_prop);
fld_map_t fae_sgid2port_map {
CREATE_ENTRY("sgid0_port", 0, 2),
CREATE_ENTRY("sgid1_port", 2, 2),
CREATE_ENTRY("sgid2_port", 4, 2),
CREATE_ENTRY("sgid3_port", 6, 2),
CREATE_ENTRY("sgid4_port", 8, 2),
CREATE_ENTRY("sgid5_port", 10, 2),
CREATE_ENTRY("sgid6_port", 12, 2),
CREATE_ENTRY("sgid7_port", 14, 2),
CREATE_ENTRY("sgid8_port", 16, 2),
CREATE_ENTRY("sgid9_port", 18, 2),
CREATE_ENTRY("sgid10_port", 20, 2),
CREATE_ENTRY("sgid11_port", 22, 2),
CREATE_ENTRY("sgid12_port", 24, 2),
CREATE_ENTRY("sgid13_port", 26, 2),
CREATE_ENTRY("sgid14_port", 28, 2),
CREATE_ENTRY("sgid15_port", 30, 2),
CREATE_ENTRY("sgid16_port", 32, 2),
CREATE_ENTRY("sgid17_port", 34, 2),
CREATE_ENTRY("sgid18_port", 36, 2),
CREATE_ENTRY("sgid19_port", 38, 2),
CREATE_ENTRY("sgid20_port", 40, 2),
CREATE_ENTRY("sgid21_port", 42, 2),
CREATE_ENTRY("sgid22_port", 44, 2),
CREATE_ENTRY("sgid23_port", 46, 2),
CREATE_ENTRY("sgid24_port", 48, 2),
CREATE_ENTRY("sgid25_port", 50, 2),
CREATE_ENTRY("sgid26_port", 52, 2),
CREATE_ENTRY("sgid27_port", 54, 2),
CREATE_ENTRY("sgid28_port", 56, 2),
CREATE_ENTRY("sgid29_port", 58, 2),
CREATE_ENTRY("sgid30_port", 60, 2),
CREATE_ENTRY("sgid31_port", 62, 2)
};auto fae_sgid2port_map_prop = csr_prop_t(
std::make_shared<csr_s>(fae_sgid2port_map),
0x128,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_sgid2port_map", fae_sgid2port_map_prop);
fld_map_t fae_dsp_cont_wu_src_id {
CREATE_ENTRY("sgid0", 0, 5),
CREATE_ENTRY("sgid1", 5, 5),
CREATE_ENTRY("sgid2", 10, 5),
CREATE_ENTRY("slid", 15, 5),
CREATE_ENTRY("__rsvd", 20, 44)
};auto fae_dsp_cont_wu_src_id_prop = csr_prop_t(
std::make_shared<csr_s>(fae_dsp_cont_wu_src_id),
0x130,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_dsp_cont_wu_src_id", fae_dsp_cont_wu_src_id_prop);
fld_map_t fae_dn_wr_req_src_id {
CREATE_ENTRY("sgid0", 0, 5),
CREATE_ENTRY("sgid1", 5, 5),
CREATE_ENTRY("sgid2", 10, 5),
CREATE_ENTRY("slid", 15, 5),
CREATE_ENTRY("__rsvd", 20, 44)
};auto fae_dn_wr_req_src_id_prop = csr_prop_t(
std::make_shared<csr_s>(fae_dn_wr_req_src_id),
0x138,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_dn_wr_req_src_id", fae_dn_wr_req_src_id_prop);
fld_map_t fae_bm_rd_req_src_dst_id {
CREATE_ENTRY("sgid0", 0, 5),
CREATE_ENTRY("sgid1", 5, 5),
CREATE_ENTRY("sgid2", 10, 5),
CREATE_ENTRY("slid", 15, 5),
CREATE_ENTRY("dgid", 20, 5),
CREATE_ENTRY("dlid", 25, 5),
CREATE_ENTRY("__rsvd", 30, 34)
};auto fae_bm_rd_req_src_dst_id_prop = csr_prop_t(
std::make_shared<csr_s>(fae_bm_rd_req_src_dst_id),
0x140,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_bm_rd_req_src_dst_id", fae_bm_rd_req_src_dst_id_prop);
fld_map_t fae_sram_log_err {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(fae_sram_log_err),
0x148,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_sram_log_err", fae_sram_log_err_prop);
fld_map_t fae_sram_log_syndrome {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto fae_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(fae_sram_log_syndrome),
0x150,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_sram_log_syndrome", fae_sram_log_syndrome_prop);
fld_map_t fae_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto fae_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(fae_sram_log_addr),
0x158,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_sram_log_addr", fae_sram_log_addr_prop);
fld_map_t fae_mem_err_inj_cfg {
CREATE_ENTRY("fae_req_fifo_mem", 0, 1),
CREATE_ENTRY("fae_dma_rob_data_mem", 1, 1),
CREATE_ENTRY("fae_dma_rob_md_mem", 2, 1),
CREATE_ENTRY("fae_dma_frv_dfifo_mem", 3, 1),
CREATE_ENTRY("err_type", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto fae_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fae_mem_err_inj_cfg),
0x160,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_mem_err_inj_cfg", fae_mem_err_inj_cfg_prop);
fld_map_t fae_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fae_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fae_fla_ring_module_id_cfg),
0x168,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_fla_ring_module_id_cfg", fae_fla_ring_module_id_cfg_prop);
fld_map_t fae_fwd_prv_halt {
CREATE_ENTRY("data", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fae_fwd_prv_halt_prop = csr_prop_t(
std::make_shared<csr_s>(fae_fwd_prv_halt),
0x170,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_fwd_prv_halt", fae_fwd_prv_halt_prop);
fld_map_t fae_reset_rdy {
CREATE_ENTRY("data", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fae_reset_rdy_prop = csr_prop_t(
std::make_shared<csr_s>(fae_reset_rdy),
0x178,
CSR_TYPE::REG,
1);
add_csr(nu_fae_0, "fae_reset_rdy", fae_reset_rdy_prop);
 // END nu_fae 
}
{
 // BEGIN nu_mpg_core 
auto nu_mpg_core_0 = nu_rng[0].add_an({"nu_mpg","nu_mpg_core"}, 0x15600000, 1, 0x0);
fld_map_t nu_mpg_core_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nu_mpg_core_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_core_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_core_timeout_thresh_cfg", nu_mpg_core_timeout_thresh_cfg_prop);
fld_map_t nu_mpg_core_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_mpg_core_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_core_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_core_timedout_sta", nu_mpg_core_timedout_sta_prop);
fld_map_t nu_mpg_core_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_mpg_core_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_core_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_core_timeout_clr", nu_mpg_core_timeout_clr_prop);
fld_map_t nu_mpg_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto nu_mpg_features_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_features),
0x90,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_features", nu_mpg_features_prop);
fld_map_t nu_mpg_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto nu_mpg_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_spare_pio),
0x98,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_spare_pio", nu_mpg_spare_pio_prop);
fld_map_t nu_mpg_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto nu_mpg_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_scratchpad),
0xA0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_scratchpad", nu_mpg_scratchpad_prop);
fld_map_t nu_mpg_rx_desc_upd_hw_waddr {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto nu_mpg_rx_desc_upd_hw_waddr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_desc_upd_hw_waddr),
0xA8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_desc_upd_hw_waddr", nu_mpg_rx_desc_upd_hw_waddr_prop);
fld_map_t nu_mpg_rx_desc_upd_sw_raddr {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto nu_mpg_rx_desc_upd_sw_raddr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_desc_upd_sw_raddr),
0xB0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_desc_upd_sw_raddr", nu_mpg_rx_desc_upd_sw_raddr_prop);
fld_map_t nu_mpg_rx_desc_mem_cfg {
CREATE_ENTRY("bkpr_thr", 0, 12),
CREATE_ENTRY("xoff_thr", 12, 12),
CREATE_ENTRY("xon_thr", 24, 12),
CREATE_ENTRY("xoff_en", 36, 1),
CREATE_ENTRY("__rsvd", 37, 27)
};auto nu_mpg_rx_desc_mem_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_desc_mem_cfg),
0xB8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_desc_mem_cfg", nu_mpg_rx_desc_mem_cfg_prop);
fld_map_t nu_mpg_rx_desc_fifo_sta {
CREATE_ENTRY("cnt", 0, 12),
CREATE_ENTRY("__rsvd", 12, 52)
};auto nu_mpg_rx_desc_fifo_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_desc_fifo_sta),
0xC0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_desc_fifo_sta", nu_mpg_rx_desc_fifo_sta_prop);
fld_map_t nu_mpg_rx_data_fifo_cfg {
CREATE_ENTRY("bkpr_thr", 0, 11),
CREATE_ENTRY("xoff_thr", 11, 11),
CREATE_ENTRY("xon_thr", 22, 11),
CREATE_ENTRY("xoff_en", 33, 1),
CREATE_ENTRY("clear_hwm", 34, 1),
CREATE_ENTRY("__rsvd", 35, 29)
};auto nu_mpg_rx_data_fifo_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_data_fifo_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_data_fifo_cfg", nu_mpg_rx_data_fifo_cfg_prop);
fld_map_t nu_mpg_rx_data_fifo_sta {
CREATE_ENTRY("cnt", 0, 11),
CREATE_ENTRY("hwm_val", 11, 11),
CREATE_ENTRY("__rsvd", 22, 42)
};auto nu_mpg_rx_data_fifo_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_data_fifo_sta),
0xD0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_data_fifo_sta", nu_mpg_rx_data_fifo_sta_prop);
fld_map_t nu_mpg_rx_tgb_cfg {
CREATE_ENTRY("max_tags", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto nu_mpg_rx_tgb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_tgb_cfg),
0xD8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_tgb_cfg", nu_mpg_rx_tgb_cfg_prop);
fld_map_t nu_mpg_rx_tgb_sta {
CREATE_ENTRY("num_tags_used", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto nu_mpg_rx_tgb_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_tgb_sta),
0xE0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_tgb_sta", nu_mpg_rx_tgb_sta_prop);
fld_map_t nu_mpg_rx_fsm_cfg {
CREATE_ENTRY("drop_err_pkt", 0, 1),
CREATE_ENTRY("dn_gid", 1, 5),
CREATE_ENTRY("dn_lid", 6, 5),
CREATE_ENTRY("load_hbm_addr", 11, 1),
CREATE_ENTRY("disable_fsm", 12, 1),
CREATE_ENTRY("__rsvd", 13, 51)
};auto nu_mpg_rx_fsm_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_fsm_cfg),
0xE8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_fsm_cfg", nu_mpg_rx_fsm_cfg_prop);
fld_map_t nu_mpg_rx_dn_arb_sta {
CREATE_ENTRY("fep0_credits", 0, 6),
CREATE_ENTRY("fep1_credits", 6, 6),
CREATE_ENTRY("fep2_credits", 12, 6),
CREATE_ENTRY("fifo_cnt", 18, 4),
CREATE_ENTRY("__rsvd", 22, 42)
};auto nu_mpg_rx_dn_arb_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_rx_dn_arb_sta),
0xF0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_rx_dn_arb_sta", nu_mpg_rx_dn_arb_sta_prop);
fld_map_t nu_mpg_tx_desc_upd_hw_raddr {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto nu_mpg_tx_desc_upd_hw_raddr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_desc_upd_hw_raddr),
0xF8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_desc_upd_hw_raddr", nu_mpg_tx_desc_upd_hw_raddr_prop);
fld_map_t nu_mpg_tx_desc_upd_sw_waddr {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto nu_mpg_tx_desc_upd_sw_waddr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_desc_upd_sw_waddr),
0x100,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_desc_upd_sw_waddr", nu_mpg_tx_desc_upd_sw_waddr_prop);
fld_map_t nu_mpg_tx_data_fifo_cfg {
CREATE_ENTRY("bkpr_thr", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto nu_mpg_tx_data_fifo_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_data_fifo_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_data_fifo_cfg", nu_mpg_tx_data_fifo_cfg_prop);
fld_map_t nu_mpg_tx_data_fifo_sta {
CREATE_ENTRY("cnt", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto nu_mpg_tx_data_fifo_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_data_fifo_sta),
0x110,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_data_fifo_sta", nu_mpg_tx_data_fifo_sta_prop);
fld_map_t nu_mpg_tx_tgb_cfg {
CREATE_ENTRY("max_tags", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto nu_mpg_tx_tgb_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_tgb_cfg),
0x118,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_tgb_cfg", nu_mpg_tx_tgb_cfg_prop);
fld_map_t nu_mpg_tx_tgb_sta {
CREATE_ENTRY("num_tags_used", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto nu_mpg_tx_tgb_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_tgb_sta),
0x120,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_tgb_sta", nu_mpg_tx_tgb_sta_prop);
fld_map_t nu_mpg_tx_fsm_cfg {
CREATE_ENTRY("dn_gid", 0, 5),
CREATE_ENTRY("dn_lid", 5, 5),
CREATE_ENTRY("load_hbm_addr", 10, 1),
CREATE_ENTRY("disable_fsm", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto nu_mpg_tx_fsm_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_fsm_cfg),
0x128,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_fsm_cfg", nu_mpg_tx_fsm_cfg_prop);
fld_map_t nu_mpg_hbm_rx_buf_start_addr_cfg {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_mpg_hbm_rx_buf_start_addr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_hbm_rx_buf_start_addr_cfg),
0x130,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_hbm_rx_buf_start_addr_cfg", nu_mpg_hbm_rx_buf_start_addr_cfg_prop);
fld_map_t nu_mpg_hbm_rx_buf_end_addr_cfg {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_mpg_hbm_rx_buf_end_addr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_hbm_rx_buf_end_addr_cfg),
0x138,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_hbm_rx_buf_end_addr_cfg", nu_mpg_hbm_rx_buf_end_addr_cfg_prop);
fld_map_t nu_mpg_hbm_rx_buf_curr_addr_sta {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_mpg_hbm_rx_buf_curr_addr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_hbm_rx_buf_curr_addr_sta),
0x140,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_hbm_rx_buf_curr_addr_sta", nu_mpg_hbm_rx_buf_curr_addr_sta_prop);
fld_map_t nu_mpg_hbm_tx_buf_start_addr_cfg {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_mpg_hbm_tx_buf_start_addr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_hbm_tx_buf_start_addr_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_hbm_tx_buf_start_addr_cfg", nu_mpg_hbm_tx_buf_start_addr_cfg_prop);
fld_map_t nu_mpg_hbm_tx_buf_end_addr_cfg {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_mpg_hbm_tx_buf_end_addr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_hbm_tx_buf_end_addr_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_hbm_tx_buf_end_addr_cfg", nu_mpg_hbm_tx_buf_end_addr_cfg_prop);
fld_map_t nu_mpg_hbm_tx_buf_curr_addr_sta {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_mpg_hbm_tx_buf_curr_addr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_hbm_tx_buf_curr_addr_sta),
0x158,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_hbm_tx_buf_curr_addr_sta", nu_mpg_hbm_tx_buf_curr_addr_sta_prop);
fld_map_t nu_mpg_tx_prd_sta {
CREATE_ENTRY("fpg_credits", 0, 3),
CREATE_ENTRY("__rsvd", 3, 61)
};auto nu_mpg_tx_prd_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_prd_sta),
0x160,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_prd_sta", nu_mpg_tx_prd_sta_prop);
fld_map_t nu_mpg_tx_sn_arb_sta {
CREATE_ENTRY("fep0_credits", 0, 6),
CREATE_ENTRY("fep1_credits", 6, 6),
CREATE_ENTRY("fep2_credits", 12, 6),
CREATE_ENTRY("fifo_cnt", 18, 3),
CREATE_ENTRY("__rsvd", 21, 43)
};auto nu_mpg_tx_sn_arb_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_tx_sn_arb_sta),
0x168,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_tx_sn_arb_sta", nu_mpg_tx_sn_arb_sta_prop);
fld_map_t nu_mpg_fla_slave_id {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nu_mpg_fla_slave_id_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_fla_slave_id),
0x170,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_fla_slave_id", nu_mpg_fla_slave_id_prop);
fld_map_t nu_mpg_sram_err_inj_cfg {
CREATE_ENTRY("tx_desc", 0, 1),
CREATE_ENTRY("tx_data", 1, 1),
CREATE_ENTRY("rx_desc", 2, 1),
CREATE_ENTRY("rx_data", 3, 1),
CREATE_ENTRY("err_type", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto nu_mpg_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_err_inj_cfg),
0x178,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_err_inj_cfg", nu_mpg_sram_err_inj_cfg_prop);
fld_map_t nu_mpg_sram_log_cerr_vec {
CREATE_ENTRY("tx_desc", 0, 1),
CREATE_ENTRY("tx_data", 1, 1),
CREATE_ENTRY("rx_desc", 2, 1),
CREATE_ENTRY("rx_data", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nu_mpg_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_log_cerr_vec),
0x180,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_log_cerr_vec", nu_mpg_sram_log_cerr_vec_prop);
fld_map_t nu_mpg_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_mpg_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_log_cerr_syndrome),
0x188,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_log_cerr_syndrome", nu_mpg_sram_log_cerr_syndrome_prop);
fld_map_t nu_mpg_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_mpg_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_log_cerr_addr),
0x190,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_log_cerr_addr", nu_mpg_sram_log_cerr_addr_prop);
fld_map_t nu_mpg_sram_log_uerr_vec {
CREATE_ENTRY("tx_desc", 0, 1),
CREATE_ENTRY("tx_data", 1, 1),
CREATE_ENTRY("rx_desc", 2, 1),
CREATE_ENTRY("rx_data", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nu_mpg_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_log_uerr_vec),
0x198,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_log_uerr_vec", nu_mpg_sram_log_uerr_vec_prop);
fld_map_t nu_mpg_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_mpg_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_log_uerr_syndrome),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_log_uerr_syndrome", nu_mpg_sram_log_uerr_syndrome_prop);
fld_map_t nu_mpg_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_mpg_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_mpg_sram_log_uerr_addr),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(nu_mpg_core_0, "nu_mpg_sram_log_uerr_addr", nu_mpg_sram_log_uerr_addr_prop);
 // END nu_mpg_core 
}
{
 // BEGIN fla 
auto fla_0 = nu_rng[0].add_an({"fla"}, 0x15800000, 1, 0x0);
fld_map_t fla_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fla_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_timeout_thresh_cfg", fla_timeout_thresh_cfg_prop);
fld_map_t fla_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fla_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_timedout_sta", fla_timedout_sta_prop);
fld_map_t fla_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fla_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fla_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_timeout_clr", fla_timeout_clr_prop);
fld_map_t fla_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto fla_features_prop = csr_prop_t(
std::make_shared<csr_s>(fla_features),
0x90,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_features", fla_features_prop);
fld_map_t fla_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto fla_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(fla_spare_pio),
0x98,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_spare_pio", fla_spare_pio_prop);
fld_map_t fla_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto fla_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(fla_scratchpad),
0xA0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_scratchpad", fla_scratchpad_prop);
fld_map_t fla_mem_init_start_cfg {
CREATE_ENTRY("fld_fla_engine0_cap_mem", 0, 1),
CREATE_ENTRY("fld_fla_engine1_cap_mem", 1, 1),
CREATE_ENTRY("fld_fla_engine2_cap_mem", 2, 1),
CREATE_ENTRY("fld_fla_engine3_cap_mem", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fla_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_mem_init_start_cfg),
0xA8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_mem_init_start_cfg", fla_mem_init_start_cfg_prop);
fld_map_t fla_mem_init_done_sta {
CREATE_ENTRY("fld_fla_engine0_cap_mem", 0, 1),
CREATE_ENTRY("fld_fla_engine1_cap_mem", 1, 1),
CREATE_ENTRY("fld_fla_engine2_cap_mem", 2, 1),
CREATE_ENTRY("fld_fla_engine3_cap_mem", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fla_mem_init_done_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_mem_init_done_sta),
0xB0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_mem_init_done_sta", fla_mem_init_done_sta_prop);
fld_map_t fla_mem_log_err_sta {
CREATE_ENTRY("fld_fla_engine0_cap_mem_cerr", 0, 1),
CREATE_ENTRY("fld_fla_engine1_cap_mem_cerr", 1, 1),
CREATE_ENTRY("fld_fla_engine2_cap_mem_cerr", 2, 1),
CREATE_ENTRY("fld_fla_engine3_cap_mem_cerr", 3, 1),
CREATE_ENTRY("fld_fla_engine0_cap_mem_ucerr", 4, 1),
CREATE_ENTRY("fld_fla_engine1_cap_mem_ucerr", 5, 1),
CREATE_ENTRY("fld_fla_engine2_cap_mem_ucerr", 6, 1),
CREATE_ENTRY("fld_fla_engine3_cap_mem_ucerr", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fla_mem_log_err_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_mem_log_err_sta),
0xB8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_mem_log_err_sta", fla_mem_log_err_sta_prop);
fld_map_t fla_mem_log_syndrome_sta {
CREATE_ENTRY("fld_val", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto fla_mem_log_syndrome_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_mem_log_syndrome_sta),
0xC0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_mem_log_syndrome_sta", fla_mem_log_syndrome_sta_prop);
fld_map_t fla_mem_log_addr_sta {
CREATE_ENTRY("fld_val", 0, 13),
CREATE_ENTRY("__rsvd", 13, 51)
};auto fla_mem_log_addr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_mem_log_addr_sta),
0xC8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_mem_log_addr_sta", fla_mem_log_addr_sta_prop);
fld_map_t fla_mem_err_inj_cfg {
CREATE_ENTRY("fld_fla_engine0_cap_mem", 0, 1),
CREATE_ENTRY("fld_fla_engine1_cap_mem", 1, 1),
CREATE_ENTRY("fld_fla_engine2_cap_mem", 2, 1),
CREATE_ENTRY("fld_fla_engine3_cap_mem", 3, 1),
CREATE_ENTRY("fld_err_type", 4, 1),
CREATE_ENTRY("__rsvd", 5, 59)
};auto fla_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_mem_err_inj_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_mem_err_inj_cfg", fla_mem_err_inj_cfg_prop);
fld_map_t fla_trig_sta {
CREATE_ENTRY("fld_engine0", 0, 1),
CREATE_ENTRY("fld_engine1", 1, 1),
CREATE_ENTRY("fld_engine2", 2, 1),
CREATE_ENTRY("fld_engine3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fla_trig_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_trig_sta),
0xE8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_trig_sta", fla_trig_sta_prop);
fld_map_t fla_cap_done_sta {
CREATE_ENTRY("fld_engine0", 0, 1),
CREATE_ENTRY("fld_engine1", 1, 1),
CREATE_ENTRY("fld_engine2", 2, 1),
CREATE_ENTRY("fld_engine3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto fla_cap_done_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_cap_done_sta),
0xF8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_cap_done_sta", fla_cap_done_sta_prop);
fld_map_t fla_trig_map_cfg {
CREATE_ENTRY("fld_engine0", 0, 4),
CREATE_ENTRY("fld_engine1", 4, 4),
CREATE_ENTRY("fld_engine2", 8, 4),
CREATE_ENTRY("fld_engine3", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_trig_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_trig_map_cfg),
0x100,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_trig_map_cfg", fla_trig_map_cfg_prop);
fld_map_t fla_trig_type_cfg {
CREATE_ENTRY("fld_engine0", 0, 4),
CREATE_ENTRY("fld_engine1", 4, 4),
CREATE_ENTRY("fld_engine2", 8, 4),
CREATE_ENTRY("fld_engine3", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_trig_type_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_trig_type_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_trig_type_cfg", fla_trig_type_cfg_prop);
fld_map_t fla_engine_sample_mode_cfg {
CREATE_ENTRY("fld_engine0", 0, 2),
CREATE_ENTRY("fld_engine1", 2, 2),
CREATE_ENTRY("fld_engine2", 4, 2),
CREATE_ENTRY("fld_engine3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto fla_engine_sample_mode_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine_sample_mode_cfg),
0x110,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine_sample_mode_cfg", fla_engine_sample_mode_cfg_prop);
fld_map_t fla_engine_lane_deskew_cfg {
CREATE_ENTRY("fld_engine0", 0, 8),
CREATE_ENTRY("fld_engine1", 8, 8),
CREATE_ENTRY("fld_engine2", 16, 8),
CREATE_ENTRY("fld_engine3", 24, 8),
CREATE_ENTRY("__rsvd", 32, 32)
};auto fla_engine_lane_deskew_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine_lane_deskew_cfg),
0x118,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine_lane_deskew_cfg", fla_engine_lane_deskew_cfg_prop);
fld_map_t fla_engine_trig_pos_cfg {
CREATE_ENTRY("fld_engine0", 0, 13),
CREATE_ENTRY("fld_engine1", 13, 13),
CREATE_ENTRY("fld_engine2", 26, 13),
CREATE_ENTRY("fld_engine3", 39, 13),
CREATE_ENTRY("__rsvd", 52, 12)
};auto fla_engine_trig_pos_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine_trig_pos_cfg),
0x120,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine_trig_pos_cfg", fla_engine_trig_pos_cfg_prop);
fld_map_t fla_lut_a_sel_cfg {
CREATE_ENTRY("fld_engine0", 0, 16),
CREATE_ENTRY("fld_engine1", 16, 16),
CREATE_ENTRY("fld_engine2", 32, 16),
CREATE_ENTRY("fld_engine3", 48, 16)
};auto fla_lut_a_sel_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_lut_a_sel_cfg),
0x128,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_lut_a_sel_cfg", fla_lut_a_sel_cfg_prop);
fld_map_t fla_lut_a_hit_map_cfg {
CREATE_ENTRY("fld_engine0", 0, 16),
CREATE_ENTRY("fld_engine1", 16, 16),
CREATE_ENTRY("fld_engine2", 32, 16),
CREATE_ENTRY("fld_engine3", 48, 16)
};auto fla_lut_a_hit_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_lut_a_hit_map_cfg),
0x130,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_lut_a_hit_map_cfg", fla_lut_a_hit_map_cfg_prop);
fld_map_t fla_lut_b_sel_cfg {
CREATE_ENTRY("fld_engine0", 0, 16),
CREATE_ENTRY("fld_engine1", 16, 16),
CREATE_ENTRY("fld_engine2", 32, 16),
CREATE_ENTRY("fld_engine3", 48, 16)
};auto fla_lut_b_sel_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_lut_b_sel_cfg),
0x138,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_lut_b_sel_cfg", fla_lut_b_sel_cfg_prop);
fld_map_t fla_lut_b_hit_map_cfg {
CREATE_ENTRY("fld_engine0", 0, 16),
CREATE_ENTRY("fld_engine1", 16, 16),
CREATE_ENTRY("fld_engine2", 32, 16),
CREATE_ENTRY("fld_engine3", 48, 16)
};auto fla_lut_b_hit_map_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_lut_b_hit_map_cfg),
0x140,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_lut_b_hit_map_cfg", fla_lut_b_hit_map_cfg_prop);
fld_map_t fla_engine0_pattern_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine0_pattern_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine0_pattern_a_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine0_pattern_a_cfg", fla_engine0_pattern_a_cfg_prop);
fld_map_t fla_engine0_mask_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine0_mask_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine0_mask_a_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine0_mask_a_cfg", fla_engine0_mask_a_cfg_prop);
fld_map_t fla_engine0_pattern_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine0_pattern_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine0_pattern_b_cfg),
0x158,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine0_pattern_b_cfg", fla_engine0_pattern_b_cfg_prop);
fld_map_t fla_engine0_mask_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine0_mask_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine0_mask_b_cfg),
0x160,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine0_mask_b_cfg", fla_engine0_mask_b_cfg_prop);
fld_map_t fla_engine0_trig_pos_buf_ptr_sta {
CREATE_ENTRY("fld_ptr", 0, 13),
CREATE_ENTRY("__rsvd", 13, 51)
};auto fla_engine0_trig_pos_buf_ptr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine0_trig_pos_buf_ptr_sta),
0x168,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine0_trig_pos_buf_ptr_sta", fla_engine0_trig_pos_buf_ptr_sta_prop);
fld_map_t fla_engine0_cap_cnt_sta {
CREATE_ENTRY("fld_pre_trig_cap_cnt", 0, 14),
CREATE_ENTRY("fld_post_trig_cap_cnt", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fla_engine0_cap_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine0_cap_cnt_sta),
0x170,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine0_cap_cnt_sta", fla_engine0_cap_cnt_sta_prop);
fld_map_t fla_engine1_pattern_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine1_pattern_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine1_pattern_a_cfg),
0x178,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine1_pattern_a_cfg", fla_engine1_pattern_a_cfg_prop);
fld_map_t fla_engine1_mask_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine1_mask_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine1_mask_a_cfg),
0x180,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine1_mask_a_cfg", fla_engine1_mask_a_cfg_prop);
fld_map_t fla_engine1_pattern_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine1_pattern_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine1_pattern_b_cfg),
0x188,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine1_pattern_b_cfg", fla_engine1_pattern_b_cfg_prop);
fld_map_t fla_engine1_mask_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine1_mask_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine1_mask_b_cfg),
0x190,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine1_mask_b_cfg", fla_engine1_mask_b_cfg_prop);
fld_map_t fla_engine1_trig_pos_buf_ptr_sta {
CREATE_ENTRY("fld_ptr", 0, 13),
CREATE_ENTRY("__rsvd", 13, 51)
};auto fla_engine1_trig_pos_buf_ptr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine1_trig_pos_buf_ptr_sta),
0x198,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine1_trig_pos_buf_ptr_sta", fla_engine1_trig_pos_buf_ptr_sta_prop);
fld_map_t fla_engine1_cap_cnt_sta {
CREATE_ENTRY("fld_pre_trig_cap_cnt", 0, 14),
CREATE_ENTRY("fld_post_trig_cap_cnt", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fla_engine1_cap_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine1_cap_cnt_sta),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine1_cap_cnt_sta", fla_engine1_cap_cnt_sta_prop);
fld_map_t fla_engine2_pattern_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine2_pattern_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine2_pattern_a_cfg),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine2_pattern_a_cfg", fla_engine2_pattern_a_cfg_prop);
fld_map_t fla_engine2_mask_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine2_mask_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine2_mask_a_cfg),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine2_mask_a_cfg", fla_engine2_mask_a_cfg_prop);
fld_map_t fla_engine2_pattern_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine2_pattern_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine2_pattern_b_cfg),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine2_pattern_b_cfg", fla_engine2_pattern_b_cfg_prop);
fld_map_t fla_engine2_mask_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine2_mask_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine2_mask_b_cfg),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine2_mask_b_cfg", fla_engine2_mask_b_cfg_prop);
fld_map_t fla_engine2_trig_pos_buf_ptr_sta {
CREATE_ENTRY("fld_ptr", 0, 13),
CREATE_ENTRY("__rsvd", 13, 51)
};auto fla_engine2_trig_pos_buf_ptr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine2_trig_pos_buf_ptr_sta),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine2_trig_pos_buf_ptr_sta", fla_engine2_trig_pos_buf_ptr_sta_prop);
fld_map_t fla_engine2_cap_cnt_sta {
CREATE_ENTRY("fld_pre_trig_cap_cnt", 0, 14),
CREATE_ENTRY("fld_post_trig_cap_cnt", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fla_engine2_cap_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine2_cap_cnt_sta),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine2_cap_cnt_sta", fla_engine2_cap_cnt_sta_prop);
fld_map_t fla_engine3_pattern_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine3_pattern_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine3_pattern_a_cfg),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine3_pattern_a_cfg", fla_engine3_pattern_a_cfg_prop);
fld_map_t fla_engine3_mask_a_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine3_mask_a_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine3_mask_a_cfg),
0x1E0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine3_mask_a_cfg", fla_engine3_mask_a_cfg_prop);
fld_map_t fla_engine3_pattern_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine3_pattern_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine3_pattern_b_cfg),
0x1E8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine3_pattern_b_cfg", fla_engine3_pattern_b_cfg_prop);
fld_map_t fla_engine3_mask_b_cfg {
CREATE_ENTRY("fld_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto fla_engine3_mask_b_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine3_mask_b_cfg),
0x1F0,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine3_mask_b_cfg", fla_engine3_mask_b_cfg_prop);
fld_map_t fla_engine3_trig_pos_buf_ptr_sta {
CREATE_ENTRY("fld_ptr", 0, 13),
CREATE_ENTRY("__rsvd", 13, 51)
};auto fla_engine3_trig_pos_buf_ptr_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine3_trig_pos_buf_ptr_sta),
0x1F8,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine3_trig_pos_buf_ptr_sta", fla_engine3_trig_pos_buf_ptr_sta_prop);
fld_map_t fla_engine3_cap_cnt_sta {
CREATE_ENTRY("fld_pre_trig_cap_cnt", 0, 14),
CREATE_ENTRY("fld_post_trig_cap_cnt", 14, 14),
CREATE_ENTRY("__rsvd", 28, 36)
};auto fla_engine3_cap_cnt_sta_prop = csr_prop_t(
std::make_shared<csr_s>(fla_engine3_cap_cnt_sta),
0x200,
CSR_TYPE::REG,
1);
add_csr(fla_0, "fla_engine3_cap_cnt_sta", fla_engine3_cap_cnt_sta_prop);
 // END fla 
}
{
 // BEGIN nu_nmg 
auto nu_nmg_0 = nu_rng[0].add_an({"nu_nmg"}, 0x15C00000, 1, 0x0);
fld_map_t nu_nmg_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nu_nmg_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_nmg_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nu_nmg_timeout_thresh_cfg", nu_nmg_timeout_thresh_cfg_prop);
fld_map_t nu_nmg_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_nmg_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_nmg_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nu_nmg_timedout_sta", nu_nmg_timedout_sta_prop);
fld_map_t nu_nmg_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_nmg_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_nmg_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nu_nmg_timeout_clr", nu_nmg_timeout_clr_prop);
fld_map_t nu_nmg_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto nu_nmg_features_prop = csr_prop_t(
std::make_shared<csr_s>(nu_nmg_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nu_nmg_features", nu_nmg_features_prop);
fld_map_t nu_nmg_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto nu_nmg_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(nu_nmg_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nu_nmg_spare_pio", nu_nmg_spare_pio_prop);
fld_map_t nu_nmg_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto nu_nmg_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(nu_nmg_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nu_nmg_scratchpad", nu_nmg_scratchpad_prop);
fld_map_t nmg_tdm_sync_cfg {
CREATE_ENTRY("start", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nmg_tdm_sync_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nmg_tdm_sync_cfg),
0xC0,
CSR_TYPE::REG,
1);
add_csr(nu_nmg_0, "nmg_tdm_sync_cfg", nmg_tdm_sync_cfg_prop);
 // END nu_nmg 
}
{
 // BEGIN nu_fnc 
auto nu_fnc_0 = nu_rng[0].add_an({"nu_fnc"}, 0x15C00800, 4, 0x800000);
fld_map_t nu_fnc_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nu_fnc_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_timeout_thresh_cfg", nu_fnc_timeout_thresh_cfg_prop);
fld_map_t nu_fnc_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_fnc_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_timedout_sta", nu_fnc_timedout_sta_prop);
fld_map_t nu_fnc_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_fnc_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_timeout_clr", nu_fnc_timeout_clr_prop);
fld_map_t nu_fnc_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto nu_fnc_features_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_features", nu_fnc_features_prop);
fld_map_t nu_fnc_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto nu_fnc_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_spare_pio", nu_fnc_spare_pio_prop);
fld_map_t nu_fnc_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto nu_fnc_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_scratchpad", nu_fnc_scratchpad_prop);
fld_map_t nu_fnc_cfg {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("ether_type", 8, 16),
CREATE_ENTRY("replay_max_num", 24, 4),
CREATE_ENTRY("trasmit_disable", 28, 4),
CREATE_ENTRY("reset_strm", 32, 4),
CREATE_ENTRY("flush_strm", 36, 4),
CREATE_ENTRY("replay_state_reset", 40, 4),
CREATE_ENTRY("rsvd_1", 44, 2),
CREATE_ENTRY("max_frame_size", 46, 1),
CREATE_ENTRY("rfb_init_start", 47, 1),
CREATE_ENTRY("__rsvd", 48, 16)
};auto nu_fnc_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_cfg", nu_fnc_cfg_prop);
fld_map_t nu_fnc_tdm_cfg {
CREATE_ENTRY("slot3", 0, 2),
CREATE_ENTRY("slot2", 2, 2),
CREATE_ENTRY("slot1", 4, 2),
CREATE_ENTRY("slot0", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nu_fnc_tdm_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_tdm_cfg),
0x88,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_tdm_cfg", nu_fnc_tdm_cfg_prop);
fld_map_t nu_fnc_rfb_mem_sts {
CREATE_ENTRY("rfb_init_done", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nu_fnc_rfb_mem_sts_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_rfb_mem_sts),
0x98,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_rfb_mem_sts", nu_fnc_rfb_mem_sts_prop);
fld_map_t nu_fnc_replay_ctrl {
CREATE_ENTRY("replay_timer", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_fnc_replay_ctrl_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_replay_ctrl),
0xA0,
CSR_TYPE::REG_LST,
1);
add_csr(nu_fnc_0, "nu_fnc_replay_ctrl", nu_fnc_replay_ctrl_prop);
fld_map_t nu_fnc_mq2vc_map {
CREATE_ENTRY("stream", 0, 4),
CREATE_ENTRY("vc", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nu_fnc_mq2vc_map_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_mq2vc_map),
0x320,
CSR_TYPE::REG_LST,
1);
add_csr(nu_fnc_0, "nu_fnc_mq2vc_map", nu_fnc_mq2vc_map_prop);
fld_map_t nu_fnc_strm0_vc2mq_map {
CREATE_ENTRY("vc", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nu_fnc_strm0_vc2mq_map_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_strm0_vc2mq_map),
0x3A0,
CSR_TYPE::REG_LST,
1);
add_csr(nu_fnc_0, "nu_fnc_strm0_vc2mq_map", nu_fnc_strm0_vc2mq_map_prop);
fld_map_t nu_fnc_strm1_vc2mq_map {
CREATE_ENTRY("vc", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nu_fnc_strm1_vc2mq_map_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_strm1_vc2mq_map),
0x420,
CSR_TYPE::REG_LST,
1);
add_csr(nu_fnc_0, "nu_fnc_strm1_vc2mq_map", nu_fnc_strm1_vc2mq_map_prop);
fld_map_t nu_fnc_strm2_vc2mq_map {
CREATE_ENTRY("vc", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nu_fnc_strm2_vc2mq_map_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_strm2_vc2mq_map),
0x4A0,
CSR_TYPE::REG_LST,
1);
add_csr(nu_fnc_0, "nu_fnc_strm2_vc2mq_map", nu_fnc_strm2_vc2mq_map_prop);
fld_map_t nu_fnc_strm3_vc2mq_map {
CREATE_ENTRY("vc", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nu_fnc_strm3_vc2mq_map_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_strm3_vc2mq_map),
0x520,
CSR_TYPE::REG_LST,
1);
add_csr(nu_fnc_0, "nu_fnc_strm3_vc2mq_map", nu_fnc_strm3_vc2mq_map_prop);
fld_map_t nu_fnc_mem_err_inj_cfg {
CREATE_ENTRY("rtry_ctbuf", 0, 1),
CREATE_ENTRY("rtry_cbuf", 1, 1),
CREATE_ENTRY("rtry_dbuf", 2, 1),
CREATE_ENTRY("rfb_hbuf", 3, 1),
CREATE_ENTRY("rfb_lbuf", 4, 1),
CREATE_ENTRY("rx_mbuf", 5, 1),
CREATE_ENTRY("tx_mbuf", 6, 1),
CREATE_ENTRY("err_type", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nu_fnc_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_mem_err_inj_cfg),
0x5A0,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_mem_err_inj_cfg", nu_fnc_mem_err_inj_cfg_prop);
fld_map_t nu_fnc_sram_log_err {
CREATE_ENTRY("val", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto nu_fnc_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_sram_log_err),
0x5A8,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_sram_log_err", nu_fnc_sram_log_err_prop);
fld_map_t nu_fnc_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_fnc_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_sram_log_syndrome),
0x5B0,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_sram_log_syndrome", nu_fnc_sram_log_syndrome_prop);
fld_map_t nu_fnc_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto nu_fnc_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(nu_fnc_sram_log_addr),
0x5B8,
CSR_TYPE::REG,
1);
add_csr(nu_fnc_0, "nu_fnc_sram_log_addr", nu_fnc_sram_log_addr_prop);
 // END nu_fnc 
}
{
 // BEGIN hsu_flink_shim 
auto hsu_flink_shim_0 = nu_rng[0].add_an({"hsu_flink_shim"}, 0x17D00000, 2, 0x800000);
fld_map_t hsu_flink_shim_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto hsu_flink_shim_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_timeout_thresh_cfg", hsu_flink_shim_timeout_thresh_cfg_prop);
fld_map_t hsu_flink_shim_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto hsu_flink_shim_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_timedout_sta", hsu_flink_shim_timedout_sta_prop);
fld_map_t hsu_flink_shim_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto hsu_flink_shim_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_timeout_clr", hsu_flink_shim_timeout_clr_prop);
fld_map_t hsu_flink_shim_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto hsu_flink_shim_features_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_features", hsu_flink_shim_features_prop);
fld_map_t hsu_flink_shim_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto hsu_flink_shim_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_spare_pio", hsu_flink_shim_spare_pio_prop);
fld_map_t hsu_flink_shim_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto hsu_flink_shim_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_scratchpad", hsu_flink_shim_scratchpad_prop);
fld_map_t hsu_flink_shim_csr_gen1 {
CREATE_ENTRY("bif_mode", 0, 2),
CREATE_ENTRY("is_root_port", 2, 4),
CREATE_ENTRY("fnc_flow0", 6, 1),
CREATE_ENTRY("vc_flow0", 7, 4),
CREATE_ENTRY("fnc_flow1", 11, 1),
CREATE_ENTRY("vc_flow1", 12, 4),
CREATE_ENTRY("fnc_flow2", 16, 1),
CREATE_ENTRY("vc_flow2", 17, 4),
CREATE_ENTRY("fnc_flow3", 21, 1),
CREATE_ENTRY("vc_flow3", 22, 4),
CREATE_ENTRY("fnc_flow4", 26, 1),
CREATE_ENTRY("vc_flow4", 27, 4),
CREATE_ENTRY("fnc_flow5", 31, 1),
CREATE_ENTRY("vc_flow5", 32, 4),
CREATE_ENTRY("fnc_flow6", 36, 1),
CREATE_ENTRY("vc_flow6", 37, 4),
CREATE_ENTRY("fnc_flow7", 41, 1),
CREATE_ENTRY("vc_flow7", 42, 4),
CREATE_ENTRY("dis_csr_stall", 46, 1),
CREATE_ENTRY("egr_enable", 47, 1),
CREATE_ENTRY("p_ack_timer", 48, 8),
CREATE_ENTRY("bn_timer", 56, 8)
};auto hsu_flink_shim_csr_gen1_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_csr_gen1),
0x80,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_gen1", hsu_flink_shim_csr_gen1_prop);
fld_map_t hsu_flink_shim_csr_gen2 {
CREATE_ENTRY("bn_brdcst_vc", 0, 32),
CREATE_ENTRY("ack_vc_fnc0_s0", 32, 4),
CREATE_ENTRY("ack_vc_fnc0_s1", 36, 4),
CREATE_ENTRY("ack_vc_fnc0_s2", 40, 4),
CREATE_ENTRY("ack_vc_fnc0_s3", 44, 4),
CREATE_ENTRY("ack_vc_fnc1_s0", 48, 4),
CREATE_ENTRY("ack_vc_fnc1_s1", 52, 4),
CREATE_ENTRY("ack_vc_fnc1_s2", 56, 4),
CREATE_ENTRY("ack_vc_fnc1_s3", 60, 4)
};auto hsu_flink_shim_csr_gen2_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_csr_gen2),
0x88,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_gen2", hsu_flink_shim_csr_gen2_prop);
fld_map_t hsu_flink_shim_csr_gen3 {
CREATE_ENTRY("fnc0_map0", 0, 2),
CREATE_ENTRY("fnc0_map1", 2, 2),
CREATE_ENTRY("fnc0_map2", 4, 2),
CREATE_ENTRY("fnc0_map3", 6, 2),
CREATE_ENTRY("fnc0_map4", 8, 2),
CREATE_ENTRY("fnc0_map5", 10, 2),
CREATE_ENTRY("fnc0_map6", 12, 2),
CREATE_ENTRY("fnc0_map7", 14, 2),
CREATE_ENTRY("fnc0_map8", 16, 2),
CREATE_ENTRY("fnc0_map9", 18, 2),
CREATE_ENTRY("fnc0_map10", 20, 2),
CREATE_ENTRY("fnc0_map11", 22, 2),
CREATE_ENTRY("fnc0_map12", 24, 2),
CREATE_ENTRY("fnc0_map13", 26, 2),
CREATE_ENTRY("fnc0_map14", 28, 2),
CREATE_ENTRY("fnc0_map15", 30, 2),
CREATE_ENTRY("fnc1_map0", 32, 2),
CREATE_ENTRY("fnc1_map1", 34, 2),
CREATE_ENTRY("fnc1_map2", 36, 2),
CREATE_ENTRY("fnc1_map3", 38, 2),
CREATE_ENTRY("fnc1_map4", 40, 2),
CREATE_ENTRY("fnc1_map5", 42, 2),
CREATE_ENTRY("fnc1_map6", 44, 2),
CREATE_ENTRY("fnc1_map7", 46, 2),
CREATE_ENTRY("fnc1_map8", 48, 2),
CREATE_ENTRY("fnc1_map9", 50, 2),
CREATE_ENTRY("fnc1_map10", 52, 2),
CREATE_ENTRY("fnc1_map11", 54, 2),
CREATE_ENTRY("fnc1_map12", 56, 2),
CREATE_ENTRY("fnc1_map13", 58, 2),
CREATE_ENTRY("fnc1_map14", 60, 2),
CREATE_ENTRY("fnc1_map15", 62, 2)
};auto hsu_flink_shim_csr_gen3_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_csr_gen3),
0x90,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_gen3", hsu_flink_shim_csr_gen3_prop);
fld_map_t hsu_flink_shim_csr_gen4 {
CREATE_ENTRY("tgt_tag_partition_mode", 0, 2),
CREATE_ENTRY("bnh_match_val", 2, 15),
CREATE_ENTRY("bnh_mask_val", 17, 15),
CREATE_ENTRY("__rsvd", 32, 32)
};auto hsu_flink_shim_csr_gen4_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_csr_gen4),
0x98,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_gen4", hsu_flink_shim_csr_gen4_prop);
fld_map_t hsu_flink_shim_csr_pf_size_settings_mps {
CREATE_ENTRY("mps_pf0", 0, 3),
CREATE_ENTRY("mps_pf1", 3, 3),
CREATE_ENTRY("mps_pf2", 6, 3),
CREATE_ENTRY("mps_pf3", 9, 3),
CREATE_ENTRY("mps_pf4", 12, 3),
CREATE_ENTRY("mps_pf5", 15, 3),
CREATE_ENTRY("mps_pf6", 18, 3),
CREATE_ENTRY("mps_pf7", 21, 3),
CREATE_ENTRY("mps_pf8", 24, 3),
CREATE_ENTRY("mps_pf9", 27, 3),
CREATE_ENTRY("mps_pf10", 30, 3),
CREATE_ENTRY("mps_pf11", 33, 3),
CREATE_ENTRY("mps_pf12", 36, 3),
CREATE_ENTRY("mps_pf13", 39, 3),
CREATE_ENTRY("mps_pf14", 42, 3),
CREATE_ENTRY("mps_pf15", 45, 3),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_flink_shim_csr_pf_size_settings_mps_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_csr_pf_size_settings_mps),
0xA0,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_pf_size_settings_mps", hsu_flink_shim_csr_pf_size_settings_mps_prop);
fld_map_t hsu_flink_shim_csr_pf_size_settings_mrs {
CREATE_ENTRY("mrs_pf0", 0, 3),
CREATE_ENTRY("mrs_pf1", 3, 3),
CREATE_ENTRY("mrs_pf2", 6, 3),
CREATE_ENTRY("mrs_pf3", 9, 3),
CREATE_ENTRY("mrs_pf4", 12, 3),
CREATE_ENTRY("mrs_pf5", 15, 3),
CREATE_ENTRY("mrs_pf6", 18, 3),
CREATE_ENTRY("mrs_pf7", 21, 3),
CREATE_ENTRY("mrs_pf8", 24, 3),
CREATE_ENTRY("mrs_pf9", 27, 3),
CREATE_ENTRY("mrs_pf10", 30, 3),
CREATE_ENTRY("mrs_pf11", 33, 3),
CREATE_ENTRY("mrs_pf12", 36, 3),
CREATE_ENTRY("mrs_pf13", 39, 3),
CREATE_ENTRY("mrs_pf14", 42, 3),
CREATE_ENTRY("mrs_pf15", 45, 3),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_flink_shim_csr_pf_size_settings_mrs_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_flink_shim_csr_pf_size_settings_mrs),
0xA8,
CSR_TYPE::REG,
1);
add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_pf_size_settings_mrs", hsu_flink_shim_csr_pf_size_settings_mrs_prop);
 // END hsu_flink_shim 
}
{
 // BEGIN hsu_hdma_pcie_framer 
auto hsu_hdma_pcie_framer_0 = nu_rng[0].add_an({"hsu_hdma_pcie_framer"}, 0x18D00000, 2, 0x80000);
fld_map_t hsu_hdma_pcie_framer_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto hsu_hdma_pcie_framer_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_timeout_thresh_cfg", hsu_hdma_pcie_framer_timeout_thresh_cfg_prop);
fld_map_t hsu_hdma_pcie_framer_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto hsu_hdma_pcie_framer_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_timedout_sta", hsu_hdma_pcie_framer_timedout_sta_prop);
fld_map_t hsu_hdma_pcie_framer_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto hsu_hdma_pcie_framer_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_timeout_clr", hsu_hdma_pcie_framer_timeout_clr_prop);
fld_map_t hsu_hdma_pcie_framer_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto hsu_hdma_pcie_framer_features_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_features", hsu_hdma_pcie_framer_features_prop);
fld_map_t hsu_hdma_pcie_framer_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto hsu_hdma_pcie_framer_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_spare_pio", hsu_hdma_pcie_framer_spare_pio_prop);
fld_map_t hsu_hdma_pcie_framer_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto hsu_hdma_pcie_framer_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_scratchpad", hsu_hdma_pcie_framer_scratchpad_prop);
fld_map_t hsu_hdma_pcie_framer_mem_err_inj_cfg {
CREATE_ENTRY("str_mem_sl0", 0, 1),
CREATE_ENTRY("str_mem_sl1", 1, 1),
CREATE_ENTRY("gtr_mem", 2, 1),
CREATE_ENTRY("cmp_mem_sl0", 3, 1),
CREATE_ENTRY("cmp_mem_sl1", 4, 1),
CREATE_ENTRY("iop_mem", 5, 1),
CREATE_ENTRY("cpl_mem", 6, 1),
CREATE_ENTRY("pwp_cpl_mem", 7, 1),
CREATE_ENTRY("pta_cpl_mem", 8, 1),
CREATE_ENTRY("pf_vf_lookup_mem", 9, 1),
CREATE_ENTRY("err_type", 10, 1),
CREATE_ENTRY("__rsvd", 11, 53)
};auto hsu_hdma_pcie_framer_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_mem_err_inj_cfg),
0x90,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_mem_err_inj_cfg", hsu_hdma_pcie_framer_mem_err_inj_cfg_prop);
fld_map_t hsu_hdma_pcie_framer_sram_log_syndrome {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto hsu_hdma_pcie_framer_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_sram_log_syndrome),
0x98,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_sram_log_syndrome", hsu_hdma_pcie_framer_sram_log_syndrome_prop);
fld_map_t hsu_hdma_pcie_framer_sram_log_addr {
CREATE_ENTRY("val", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto hsu_hdma_pcie_framer_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_sram_log_addr),
0xA0,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_sram_log_addr", hsu_hdma_pcie_framer_sram_log_addr_prop);
fld_map_t hsu_hdma_pcie_framer_sram_log_err {
CREATE_ENTRY("val", 0, 20),
CREATE_ENTRY("__rsvd", 20, 44)
};auto hsu_hdma_pcie_framer_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_hdma_pcie_framer_sram_log_err),
0xA8,
CSR_TYPE::REG,
1);
add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_sram_log_err", hsu_hdma_pcie_framer_sram_log_err_prop);
 // END hsu_hdma_pcie_framer 
}
{
 // BEGIN hsu_tgt 
auto hsu_tgt_0 = nu_rng[0].add_an({"hsu_tgt"}, 0x19000000, 2, 0x800000);
fld_map_t hsu_tgt_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto hsu_tgt_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_timeout_thresh_cfg", hsu_tgt_timeout_thresh_cfg_prop);
fld_map_t hsu_tgt_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto hsu_tgt_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_timedout_sta", hsu_tgt_timedout_sta_prop);
fld_map_t hsu_tgt_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto hsu_tgt_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_timeout_clr", hsu_tgt_timeout_clr_prop);
fld_map_t hsu_tgt_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto hsu_tgt_features_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_features", hsu_tgt_features_prop);
fld_map_t hsu_tgt_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto hsu_tgt_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_spare_pio", hsu_tgt_spare_pio_prop);
fld_map_t hsu_tgt_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto hsu_tgt_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_scratchpad", hsu_tgt_scratchpad_prop);
fld_map_t hsu_tgt_csr_at_reg1 {
CREATE_ENTRY("hbm_coh_base", 0, 5),
CREATE_ENTRY("hbm_coh_lid", 5, 5),
CREATE_ENTRY("hbm_buf_base", 10, 5),
CREATE_ENTRY("hbm_buf_lid", 15, 5),
CREATE_ENTRY("rsvd0_gid", 20, 5),
CREATE_ENTRY("rsvd0_lid", 25, 5),
CREATE_ENTRY("pc_gid_min", 30, 5),
CREATE_ENTRY("pc_gid_max", 35, 5),
CREATE_ENTRY("pc_lid0", 40, 5),
CREATE_ENTRY("pc_lid1", 45, 5),
CREATE_ENTRY("pc_lid2", 50, 5),
CREATE_ENTRY("pc_lid3", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto hsu_tgt_csr_at_reg1_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg1),
0x160,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg1", hsu_tgt_csr_at_reg1_prop);
fld_map_t hsu_tgt_csr_at_reg2 {
CREATE_ENTRY("nu_gid_min", 0, 5),
CREATE_ENTRY("nu_gid_max", 5, 5),
CREATE_ENTRY("nu_lid0", 10, 5),
CREATE_ENTRY("nu_lid1", 15, 5),
CREATE_ENTRY("nu_lid2", 20, 5),
CREATE_ENTRY("nu_lid3", 25, 5),
CREATE_ENTRY("mu_gid_min", 30, 5),
CREATE_ENTRY("mu_gid_max", 35, 5),
CREATE_ENTRY("mu_lid0", 40, 5),
CREATE_ENTRY("mu_lid1", 45, 5),
CREATE_ENTRY("mu_lid2", 50, 5),
CREATE_ENTRY("mu_lid3", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto hsu_tgt_csr_at_reg2_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg2),
0x168,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg2", hsu_tgt_csr_at_reg2_prop);
fld_map_t hsu_tgt_csr_at_reg3 {
CREATE_ENTRY("hu_gid_min", 0, 5),
CREATE_ENTRY("hu_gid_max", 5, 5),
CREATE_ENTRY("hu_lid0", 10, 5),
CREATE_ENTRY("hu_lid1", 15, 5),
CREATE_ENTRY("hu_lid2", 20, 5),
CREATE_ENTRY("hu_lid3", 25, 5),
CREATE_ENTRY("nvram_base", 30, 5),
CREATE_ENTRY("nvram_lid", 35, 5),
CREATE_ENTRY("ddr_coh_base", 40, 5),
CREATE_ENTRY("ddr_coh_lid", 45, 5),
CREATE_ENTRY("ddr_buf_base", 50, 5),
CREATE_ENTRY("ddr_buf_lid", 55, 5),
CREATE_ENTRY("__rsvd", 60, 4)
};auto hsu_tgt_csr_at_reg3_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg3),
0x170,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg3", hsu_tgt_csr_at_reg3_prop);
fld_map_t hsu_tgt_csr_at_reg4 {
CREATE_ENTRY("rsvd1_gid", 0, 5),
CREATE_ENTRY("rsvd1_lid", 5, 5),
CREATE_ENTRY("rsvd2_gid", 10, 5),
CREATE_ENTRY("rsvd2_lid", 15, 5),
CREATE_ENTRY("default_gid", 20, 5),
CREATE_ENTRY("default_lid", 25, 5),
CREATE_ENTRY("__rsvd", 30, 34)
};auto hsu_tgt_csr_at_reg4_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg4),
0x178,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg4", hsu_tgt_csr_at_reg4_prop);
fld_map_t hsu_tgt_csr_at_reg5 {
CREATE_ENTRY("hbm_hash_num_shard", 0, 2),
CREATE_ENTRY("hbm_coh_hash_mode", 2, 2),
CREATE_ENTRY("hbm_buf_hash_mode", 4, 2),
CREATE_ENTRY("hbm_hash_stacked_mode", 6, 1),
CREATE_ENTRY("ddr_hash_stacked_mode", 7, 1),
CREATE_ENTRY("ddr_coh_hash_mode", 8, 2),
CREATE_ENTRY("ddr_buf_hash_mode", 10, 2),
CREATE_ENTRY("rsvd1_addr_min", 12, 13),
CREATE_ENTRY("rsvd1_addr_max", 25, 13),
CREATE_ENTRY("rsvd2_addr_min", 38, 13),
CREATE_ENTRY("rsvd2_addr_max", 51, 13)
};auto hsu_tgt_csr_at_reg5_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg5),
0x180,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg5", hsu_tgt_csr_at_reg5_prop);
fld_map_t hsu_tgt_csr_at_reg6 {
CREATE_ENTRY("hbm_hash_mask0", 0, 26),
CREATE_ENTRY("hbm_hash_mask1", 26, 26),
CREATE_ENTRY("__rsvd", 52, 12)
};auto hsu_tgt_csr_at_reg6_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg6),
0x188,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg6", hsu_tgt_csr_at_reg6_prop);
fld_map_t hsu_tgt_csr_at_reg7 {
CREATE_ENTRY("ddr_hash_mask0", 0, 32),
CREATE_ENTRY("ddr_hash_mask1", 32, 32)
};auto hsu_tgt_csr_at_reg7_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_at_reg7),
0x190,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg7", hsu_tgt_csr_at_reg7_prop);
fld_map_t hsu_tgt_csr_mid_addr_0 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_0_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_0),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_0", hsu_tgt_csr_mid_addr_0_prop);
fld_map_t hsu_tgt_csr_mid_addr_1 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_1_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_1),
0x1C8,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_1", hsu_tgt_csr_mid_addr_1_prop);
fld_map_t hsu_tgt_csr_mid_addr_2 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_2_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_2),
0x1D0,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_2", hsu_tgt_csr_mid_addr_2_prop);
fld_map_t hsu_tgt_csr_mid_addr_3 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_3_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_3),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_3", hsu_tgt_csr_mid_addr_3_prop);
fld_map_t hsu_tgt_csr_mid_addr_4 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_4_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_4),
0x1E0,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_4", hsu_tgt_csr_mid_addr_4_prop);
fld_map_t hsu_tgt_csr_mid_addr_5 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_5_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_5),
0x1E8,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_5", hsu_tgt_csr_mid_addr_5_prop);
fld_map_t hsu_tgt_csr_mid_addr_6 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_6_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_6),
0x1F0,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_6", hsu_tgt_csr_mid_addr_6_prop);
fld_map_t hsu_tgt_csr_mid_addr_7 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_7_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_7),
0x1F8,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_7", hsu_tgt_csr_mid_addr_7_prop);
fld_map_t hsu_tgt_csr_mid_addr_8 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_8_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_8),
0x200,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_8", hsu_tgt_csr_mid_addr_8_prop);
fld_map_t hsu_tgt_csr_mid_addr_9 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_9_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_9),
0x208,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_9", hsu_tgt_csr_mid_addr_9_prop);
fld_map_t hsu_tgt_csr_mid_addr_10 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_10_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_10),
0x210,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_10", hsu_tgt_csr_mid_addr_10_prop);
fld_map_t hsu_tgt_csr_mid_addr_11 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_11_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_11),
0x218,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_11", hsu_tgt_csr_mid_addr_11_prop);
fld_map_t hsu_tgt_csr_mid_addr_12 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_12_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_12),
0x220,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_12", hsu_tgt_csr_mid_addr_12_prop);
fld_map_t hsu_tgt_csr_mid_addr_13 {
CREATE_ENTRY("addr", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto hsu_tgt_csr_mid_addr_13_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_mid_addr_13),
0x228,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr_13", hsu_tgt_csr_mid_addr_13_prop);
fld_map_t hsu_tgt_csr_gen2 {
CREATE_ENTRY("mid_drain_en", 0, 14),
CREATE_ENTRY("__rsvd", 14, 50)
};auto hsu_tgt_csr_gen2_prop = csr_prop_t(
std::make_shared<csr_s>(hsu_tgt_csr_gen2),
0x230,
CSR_TYPE::REG,
1);
add_csr(hsu_tgt_0, "hsu_tgt_csr_gen2", hsu_tgt_csr_gen2_prop);
 // END hsu_tgt 
}
nu_rng.add_ring(1, 0x5800000000);
{
 // BEGIN sse 
auto sse_0 = nu_rng[1].add_an({"sse"}, 0x0, 1, 0x0);
fld_map_t sse_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto sse_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(sse_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_timeout_thresh_cfg", sse_timeout_thresh_cfg_prop);
fld_map_t sse_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto sse_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(sse_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_timedout_sta", sse_timedout_sta_prop);
fld_map_t sse_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto sse_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(sse_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_timeout_clr", sse_timeout_clr_prop);
fld_map_t sse_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto sse_features_prop = csr_prop_t(
std::make_shared<csr_s>(sse_features),
0x68,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_features", sse_features_prop);
fld_map_t sse_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto sse_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(sse_spare_pio),
0x70,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_spare_pio", sse_spare_pio_prop);
fld_map_t sse_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto sse_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(sse_scratchpad),
0x78,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_scratchpad", sse_scratchpad_prop);
fld_map_t sse_rng_cfg {
CREATE_ENTRY("mode", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto sse_rng_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(sse_rng_cfg),
0x80,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_rng_cfg", sse_rng_cfg_prop);
fld_map_t sse_fpg_inp_dly {
CREATE_ENTRY("fpg0_dly", 0, 3),
CREATE_ENTRY("fpg1_dly", 3, 3),
CREATE_ENTRY("fpg2_dly", 6, 3),
CREATE_ENTRY("fpg3_dly", 9, 3),
CREATE_ENTRY("fpg4_dly", 12, 3),
CREATE_ENTRY("fpg5_dly", 15, 3),
CREATE_ENTRY("__rsvd", 18, 46)
};auto sse_fpg_inp_dly_prop = csr_prop_t(
std::make_shared<csr_s>(sse_fpg_inp_dly),
0x88,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_fpg_inp_dly", sse_fpg_inp_dly_prop);
fld_map_t sse_get_prv_en {
CREATE_ENTRY("fpg0_prv_en", 0, 1),
CREATE_ENTRY("fpg1_prv_en", 1, 1),
CREATE_ENTRY("fpg2_prv_en", 2, 1),
CREATE_ENTRY("fpg3_prv_en", 3, 1),
CREATE_ENTRY("fpg4_prv_en", 4, 1),
CREATE_ENTRY("fpg5_prv_en", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto sse_get_prv_en_prop = csr_prop_t(
std::make_shared<csr_s>(sse_get_prv_en),
0x90,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_get_prv_en", sse_get_prv_en_prop);
fld_map_t sse_wrr_wt {
CREATE_ENTRY("efp_wt", 0, 4),
CREATE_ENTRY("fae_wt", 4, 4),
CREATE_ENTRY("__rsvd", 8, 56)
};auto sse_wrr_wt_prop = csr_prop_t(
std::make_shared<csr_s>(sse_wrr_wt),
0x98,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_wrr_wt", sse_wrr_wt_prop);
fld_map_t sse_min_dist {
CREATE_ENTRY("efp", 0, 5),
CREATE_ENTRY("fae", 5, 5),
CREATE_ENTRY("__rsvd", 10, 54)
};auto sse_min_dist_prop = csr_prop_t(
std::make_shared<csr_s>(sse_min_dist),
0xA0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_min_dist", sse_min_dist_prop);
fld_map_t sse_sram_log_err {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto sse_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(sse_sram_log_err),
0xA8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_sram_log_err", sse_sram_log_err_prop);
fld_map_t sse_sram_log_syndrome {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto sse_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(sse_sram_log_syndrome),
0xB0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_sram_log_syndrome", sse_sram_log_syndrome_prop);
fld_map_t sse_sram_log_addr {
CREATE_ENTRY("val", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto sse_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(sse_sram_log_addr),
0xB8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_sram_log_addr", sse_sram_log_addr_prop);
fld_map_t sse_mem_err_inj_cfg {
CREATE_ENTRY("sse_mdi_mem", 0, 1),
CREATE_ENTRY("err_type", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto sse_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(sse_mem_err_inj_cfg),
0xC0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_mem_err_inj_cfg", sse_mem_err_inj_cfg_prop);
fld_map_t sse_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto sse_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(sse_fla_ring_module_id_cfg),
0xC8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_fla_ring_module_id_cfg", sse_fla_ring_module_id_cfg_prop);
fld_map_t sse_snpsht_cfg {
CREATE_ENTRY("enable", 0, 1),
CREATE_ENTRY("prv_fld_extr", 1, 56),
CREATE_ENTRY("__rsvd", 57, 7)
};auto sse_snpsht_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_cfg),
0xD0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_cfg", sse_snpsht_cfg_prop);
fld_map_t sse_snpsht_mask_0 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_mask_0_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_mask_0),
0xD8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_mask_0", sse_snpsht_mask_0_prop);
fld_map_t sse_snpsht_mask_1 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_mask_1_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_mask_1),
0xE0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_mask_1", sse_snpsht_mask_1_prop);
fld_map_t sse_snpsht_mask_2 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_mask_2_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_mask_2),
0xE8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_mask_2", sse_snpsht_mask_2_prop);
fld_map_t sse_snpsht_mask_3 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_mask_3_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_mask_3),
0xF0,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_mask_3", sse_snpsht_mask_3_prop);
fld_map_t sse_snpsht_mask_4 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_mask_4_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_mask_4),
0xF8,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_mask_4", sse_snpsht_mask_4_prop);
fld_map_t sse_snpsht_val_0 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_val_0_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_val_0),
0x100,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_val_0", sse_snpsht_val_0_prop);
fld_map_t sse_snpsht_val_1 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_val_1_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_val_1),
0x108,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_val_1", sse_snpsht_val_1_prop);
fld_map_t sse_snpsht_val_2 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_val_2_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_val_2),
0x110,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_val_2", sse_snpsht_val_2_prop);
fld_map_t sse_snpsht_val_3 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_val_3_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_val_3),
0x118,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_val_3", sse_snpsht_val_3_prop);
fld_map_t sse_snpsht_val_4 {
CREATE_ENTRY("val", 0, 64)
};auto sse_snpsht_val_4_prop = csr_prop_t(
std::make_shared<csr_s>(sse_snpsht_val_4),
0x120,
CSR_TYPE::REG,
1);
add_csr(sse_0, "sse_snpsht_val_4", sse_snpsht_val_4_prop);
 // END sse 
}
{
 // BEGIN nhp 
auto nhp_0 = nu_rng[1].add_an({"nhp"}, 0x1C000000, 1, 0x0);
fld_map_t nhp_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_timeout_thresh_cfg", nhp_timeout_thresh_cfg_prop);
fld_map_t nhp_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nhp_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_timedout_sta),
0x8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_timedout_sta", nhp_timedout_sta_prop);
fld_map_t nhp_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nhp_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_timeout_clr", nhp_timeout_clr_prop);
fld_map_t nhp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto nhp_features_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_features),
0x40,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_features", nhp_features_prop);
fld_map_t nhp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto nhp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_spare_pio),
0x48,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_spare_pio", nhp_spare_pio_prop);
fld_map_t nhp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto nhp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_scratchpad),
0x50,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_scratchpad", nhp_scratchpad_prop);
fld_map_t nhp_ofs_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_ofs_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_ofs_cfg),
0x58,
CSR_TYPE::REG_LST,
1);
add_csr(nhp_0, "nhp_ofs_cfg", nhp_ofs_cfg_prop);
fld_map_t nhp_f1_num {
CREATE_ENTRY("val", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto nhp_f1_num_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_f1_num),
0xD8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_f1_num", nhp_f1_num_prop);
fld_map_t lfa_visited_f1_cfg {
CREATE_ENTRY("f1_id_vld", 0, 1),
CREATE_ENTRY("f1_id", 1, 4),
CREATE_ENTRY("__rsvd", 5, 59)
};auto lfa_visited_f1_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(lfa_visited_f1_cfg),
0xE0,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "lfa_visited_f1_cfg", lfa_visited_f1_cfg_prop);
fld_map_t nhp_lvl0_hash_seed {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nhp_lvl0_hash_seed_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl0_hash_seed),
0xE8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl0_hash_seed", nhp_lvl0_hash_seed_prop);
fld_map_t nhp_lvl1_hash_seed {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nhp_lvl1_hash_seed_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl1_hash_seed),
0xF0,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl1_hash_seed", nhp_lvl1_hash_seed_prop);
fld_map_t nhp_lvl0_hash_bypass {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nhp_lvl0_hash_bypass_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl0_hash_bypass),
0xF8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl0_hash_bypass", nhp_lvl0_hash_bypass_prop);
fld_map_t nhp_lvl1_hash_bypass {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nhp_lvl1_hash_bypass_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl1_hash_bypass),
0x100,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl1_hash_bypass", nhp_lvl1_hash_bypass_prop);
fld_map_t nhp_gph_cfg {
CREATE_ENTRY("fcb_send_enable", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nhp_gph_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_gph_cfg),
0x108,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_gph_cfg", nhp_gph_cfg_prop);
fld_map_t nhp_remote_gph_prv_ofs {
CREATE_ENTRY("val", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto nhp_remote_gph_prv_ofs_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_remote_gph_prv_ofs),
0x110,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_remote_gph_prv_ofs", nhp_remote_gph_prv_ofs_prop);
fld_map_t nhp_fcp_spray_min_pktlen {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nhp_fcp_spray_min_pktlen_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_fcp_spray_min_pktlen),
0x118,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_fcp_spray_min_pktlen", nhp_fcp_spray_min_pktlen_prop);
fld_map_t nhp_fcp_spray_pktlen_adj {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nhp_fcp_spray_pktlen_adj_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_fcp_spray_pktlen_adj),
0x120,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_fcp_spray_pktlen_adj", nhp_fcp_spray_pktlen_adj_prop);
fld_map_t nhp_fcp_rand_spray_en {
CREATE_ENTRY("lvl0", 0, 1),
CREATE_ENTRY("lvl1", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_fcp_rand_spray_en_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_fcp_rand_spray_en),
0x128,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_fcp_rand_spray_en", nhp_fcp_rand_spray_en_prop);
fld_map_t nhp_lvl0_fcp_spray_pktlen_lfsr_cfg {
CREATE_ENTRY("shift_cfg", 0, 1),
CREATE_ENTRY("shift_dis", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_lvl0_fcp_spray_pktlen_lfsr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl0_fcp_spray_pktlen_lfsr_cfg),
0x130,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl0_fcp_spray_pktlen_lfsr_cfg", nhp_lvl0_fcp_spray_pktlen_lfsr_cfg_prop);
fld_map_t nhp_lvl1_fcp_spray_pktlen_lfsr_cfg {
CREATE_ENTRY("shift_cfg", 0, 1),
CREATE_ENTRY("shift_dis", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_lvl1_fcp_spray_pktlen_lfsr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl1_fcp_spray_pktlen_lfsr_cfg),
0x138,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl1_fcp_spray_pktlen_lfsr_cfg", nhp_lvl1_fcp_spray_pktlen_lfsr_cfg_prop);
fld_map_t nhp_lvl0_fcp_spray_rrptr_lfsr_cfg {
CREATE_ENTRY("shift_cfg", 0, 1),
CREATE_ENTRY("shift_dis", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_lvl0_fcp_spray_rrptr_lfsr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl0_fcp_spray_rrptr_lfsr_cfg),
0x140,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl0_fcp_spray_rrptr_lfsr_cfg", nhp_lvl0_fcp_spray_rrptr_lfsr_cfg_prop);
fld_map_t nhp_lvl1_fcp_spray_rrptr_lfsr_cfg {
CREATE_ENTRY("shift_cfg", 0, 1),
CREATE_ENTRY("shift_dis", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_lvl1_fcp_spray_rrptr_lfsr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl1_fcp_spray_rrptr_lfsr_cfg),
0x148,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl1_fcp_spray_rrptr_lfsr_cfg", nhp_lvl1_fcp_spray_rrptr_lfsr_cfg_prop);
fld_map_t nhp_lvl0_fcp_spray_randspray_lfsr_cfg {
CREATE_ENTRY("shift_cfg", 0, 1),
CREATE_ENTRY("shift_dis", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_lvl0_fcp_spray_randspray_lfsr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl0_fcp_spray_randspray_lfsr_cfg),
0x150,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl0_fcp_spray_randspray_lfsr_cfg", nhp_lvl0_fcp_spray_randspray_lfsr_cfg_prop);
fld_map_t nhp_lvl1_fcp_spray_randspray_lfsr_cfg {
CREATE_ENTRY("shift_cfg", 0, 1),
CREATE_ENTRY("shift_dis", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto nhp_lvl1_fcp_spray_randspray_lfsr_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lvl1_fcp_spray_randspray_lfsr_cfg),
0x158,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lvl1_fcp_spray_randspray_lfsr_cfg", nhp_lvl1_fcp_spray_randspray_lfsr_cfg_prop);
fld_map_t nhp_fs_ring_cfg {
CREATE_ENTRY("override", 0, 24),
CREATE_ENTRY("status", 24, 24),
CREATE_ENTRY("fs_ring_enable", 48, 1),
CREATE_ENTRY("__rsvd", 49, 15)
};auto nhp_fs_ring_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_fs_ring_cfg),
0x160,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_fs_ring_cfg", nhp_fs_ring_cfg_prop);
fld_map_t nhp_bypass_cfg {
CREATE_ENTRY("bypass_lvl0", 0, 1),
CREATE_ENTRY("bypass_lvl1", 1, 1),
CREATE_ENTRY("bypass_lvl2", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto nhp_bypass_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_bypass_cfg),
0x198,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_bypass_cfg", nhp_bypass_cfg_prop);
fld_map_t nhp_lb_crc_cfg {
CREATE_ENTRY("lvl0_crc16", 0, 16),
CREATE_ENTRY("lvl0_crc4", 16, 4),
CREATE_ENTRY("lvl1_crc16", 20, 16),
CREATE_ENTRY("lvl1_crc4", 36, 4),
CREATE_ENTRY("__rsvd", 40, 24)
};auto nhp_lb_crc_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_lb_crc_cfg),
0x1A0,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_lb_crc_cfg", nhp_lb_crc_cfg_prop);
fld_map_t nhp_sram_log_err {
CREATE_ENTRY("val", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto nhp_sram_log_err_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_sram_log_err),
0x1A8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_sram_log_err", nhp_sram_log_err_prop);
fld_map_t nhp_sram_log_syndrome {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto nhp_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_sram_log_syndrome),
0x1B0,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_sram_log_syndrome", nhp_sram_log_syndrome_prop);
fld_map_t nhp_sram_log_addr {
CREATE_ENTRY("val", 0, 12),
CREATE_ENTRY("__rsvd", 12, 52)
};auto nhp_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_sram_log_addr),
0x1B8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_sram_log_addr", nhp_sram_log_addr_prop);
fld_map_t nhp_mem_err_inj_cfg {
CREATE_ENTRY("nhp_lvl0_mem", 0, 1),
CREATE_ENTRY("nhp_lvl1_mem", 1, 1),
CREATE_ENTRY("nhp_lvl2_mem", 2, 1),
CREATE_ENTRY("nhp_fcp_spray_16_mem", 3, 1),
CREATE_ENTRY("nhp_fcp_spray_8_mem", 4, 1),
CREATE_ENTRY("err_type", 5, 1),
CREATE_ENTRY("__rsvd", 6, 58)
};auto nhp_mem_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_mem_err_inj_cfg),
0x1C0,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_mem_err_inj_cfg", nhp_mem_err_inj_cfg_prop);
fld_map_t nhp_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto nhp_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_fla_ring_module_id_cfg),
0x1D8,
CSR_TYPE::REG,
1);
add_csr(nhp_0, "nhp_fla_ring_module_id_cfg", nhp_fla_ring_module_id_cfg_prop);
fld_map_t nhp_rll_state_override {
CREATE_ENTRY("vld", 0, 1),
CREATE_ENTRY("val", 1, 16),
CREATE_ENTRY("__rsvd", 17, 47)
};auto nhp_rll_state_override_prop = csr_prop_t(
std::make_shared<csr_s>(nhp_rll_state_override),
0x6800,
CSR_TYPE::TBL,
1);
add_csr(nhp_0, "nhp_rll_state_override", nhp_rll_state_override_prop);
 // END nhp 
}
sys_rings["NU"] = nu_rng;
ring_coll_t pc_rng;
pc_rng.add_ring(0, 0x800000000);
pc_rng.add_ring(1, 0x1000000000);
pc_rng.add_ring(2, 0x1800000000);
pc_rng.add_ring(3, 0x2000000000);
pc_rng.add_ring(4, 0x2800000000);
pc_rng.add_ring(5, 0x3000000000);
pc_rng.add_ring(6, 0x3800000000);
pc_rng.add_ring(7, 0x4000000000);
sys_rings["PC"] = pc_rng;
ring_coll_t fiu_rng;
fiu_rng.add_ring(0, 0x0);
sys_rings["FIU"] = fiu_rng;


}    