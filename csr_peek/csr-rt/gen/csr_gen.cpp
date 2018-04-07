ring_coll_t nu_rng;
nu_rng.add_ring(0, 0x5000000000);
{
 // BEGIN fpg_prs 
auto fpg_prs_0 = nu_rng[0].add_an({"fpg","fpg_prs"}, 0x0, 1, 0x0);
fld_map_t fpg_prs_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto fpg_prs_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_timeout_thresh_cfg),
0x0,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_timeout_thresh_cfg", fpg_prs_timeout_thresh_cfg_prop);
fld_map_t fpg_prs_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto fpg_prs_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(fpg_prs_timeout_clr),
0x10,
CSR_TYPE::REG,
1);
add_csr(fpg_prs_0, "fpg_prs_timeout_clr", fpg_prs_timeout_clr_prop);
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
fld_map_t prs_tcam {
CREATE_ENTRY("vld", 0, 1),
CREATE_ENTRY("parser_state", 1, 8),
CREATE_ENTRY("pattern", 9, 32),
CREATE_ENTRY("mask", 41, 32),
CREATE_ENTRY("__rsvd", 73, 55)
};auto prs_tcam_prop = csr_prop_t(
std::make_shared<csr_s>(prs_tcam),
0x1000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_tcam", prs_tcam_prop);
fld_map_t prs_seq_mem {
CREATE_ENTRY("new_parser_state", 0, 8),
CREATE_ENTRY("key_src", 8, 2),
CREATE_ENTRY("pkt_ptr_incr", 10, 4),
CREATE_ENTRY("set_act_context", 14, 1),
CREATE_ENTRY("gpr_instr_opcode", 15, 2),
CREATE_ENTRY("gpr_instr_operand", 17, 12),
CREATE_ENTRY("__rsvd", 29, 35)
};auto prs_seq_mem_prop = csr_prop_t(
std::make_shared<csr_s>(prs_seq_mem),
0x11000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_seq_mem", prs_seq_mem_prop);
fld_map_t prs_rob_prv_mem_dhs {
CREATE_ENTRY("data", 0, 288),
CREATE_ENTRY("__rsvd", 288, 32)
};auto prs_rob_prv_mem_dhs_prop = csr_prop_t(
std::make_shared<csr_s>(prs_rob_prv_mem_dhs),
0x15000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_rob_prv_mem_dhs", prs_rob_prv_mem_dhs_prop);
fld_map_t prs_action_mem_dhs {
CREATE_ENTRY("data", 0, 112),
CREATE_ENTRY("__rsvd", 112, 16)
};auto prs_action_mem_dhs_prop = csr_prop_t(
std::make_shared<csr_s>(prs_action_mem_dhs),
0x40000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_action_mem_dhs", prs_action_mem_dhs_prop);
fld_map_t prs_dsp_dfifo_mem_dhs {
CREATE_ENTRY("data", 0, 36),
CREATE_ENTRY("__rsvd", 36, 28)
};auto prs_dsp_dfifo_mem_dhs_prop = csr_prop_t(
std::make_shared<csr_s>(prs_dsp_dfifo_mem_dhs),
0x140000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_dsp_dfifo_mem_dhs", prs_dsp_dfifo_mem_dhs_prop);
fld_map_t prs_initial_state {
CREATE_ENTRY("parser_state", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto prs_initial_state_prop = csr_prop_t(
std::make_shared<csr_s>(prs_initial_state),
0x540000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_initial_state", prs_initial_state_prop);
fld_map_t prs_dsp_dbg_probe {
CREATE_ENTRY("fld_count", 0, 64)
};auto prs_dsp_dbg_probe_prop = csr_prop_t(
std::make_shared<csr_s>(prs_dsp_dbg_probe),
0x541000,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_dsp_dbg_probe", prs_dsp_dbg_probe_prop);
fld_map_t prs_ctx_rob_dbg_probe {
CREATE_ENTRY("fld_count", 0, 64)
};auto prs_ctx_rob_dbg_probe_prop = csr_prop_t(
std::make_shared<csr_s>(prs_ctx_rob_dbg_probe),
0x541200,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_ctx_rob_dbg_probe", prs_ctx_rob_dbg_probe_prop);
fld_map_t prs_prv_dbg_probe {
CREATE_ENTRY("fld_count", 0, 64)
};auto prs_prv_dbg_probe_prop = csr_prop_t(
std::make_shared<csr_s>(prs_prv_dbg_probe),
0x541400,
CSR_TYPE::TBL,
1);
add_csr(fpg_prs_0, "prs_prv_dbg_probe", prs_prv_dbg_probe_prop);
 // END fpg_prs 
}
sys_rings["NU"] = nu_rng;
