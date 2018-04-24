ring_coll_t nu_rng;
nu_rng.add_ring(0, 0x5000000000);
{
 // BEGIN psw_pwr 
auto psw_pwr_0 = nu_rng[0].add_an({"psw_pwr"}, 0x9000000, 1, 0x0);
fld_map_t psw_pwr_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_pwr_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_timeout_thresh_cfg),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_timeout_thresh_cfg", psw_pwr_timeout_thresh_cfg_prop);
fld_map_t psw_pwr_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_timedout_sta),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_timedout_sta", psw_pwr_timedout_sta_prop);
fld_map_t psw_pwr_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_timeout_clr),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_timeout_clr", psw_pwr_timeout_clr_prop);
fld_map_t psw_pwr_fatal_intr_cause {
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
};auto psw_pwr_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_intr_cause", psw_pwr_fatal_intr_cause_prop);
fld_map_t psw_pwr_fatal_intr_stat {
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
};auto psw_pwr_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_intr_stat", psw_pwr_fatal_intr_stat_prop);
fld_map_t psw_pwr_fatal_intr_mask {
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
};auto psw_pwr_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_intr_mask", psw_pwr_fatal_intr_mask_prop);
fld_map_t psw_pwr_fatal_intr_bset {
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
};auto psw_pwr_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_intr_bset", psw_pwr_fatal_intr_bset_prop);
fld_map_t psw_pwr_fatal_intr_bclr {
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
};auto psw_pwr_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_intr_bclr", psw_pwr_fatal_intr_bclr_prop);
fld_map_t psw_pwr_fatal_misc_intr_cause {
CREATE_ENTRY("unexpected_frv_rcvd", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_fatal_misc_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_misc_intr_cause),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_misc_intr_cause", psw_pwr_fatal_misc_intr_cause_prop);
fld_map_t psw_pwr_fatal_misc_intr_stat {
CREATE_ENTRY("unexpected_frv_rcvd", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_fatal_misc_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_misc_intr_stat),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_misc_intr_stat", psw_pwr_fatal_misc_intr_stat_prop);
fld_map_t psw_pwr_fatal_misc_intr_mask {
CREATE_ENTRY("unexpected_frv_rcvd", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_fatal_misc_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_misc_intr_mask),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_misc_intr_mask", psw_pwr_fatal_misc_intr_mask_prop);
fld_map_t psw_pwr_fatal_misc_intr_bset {
CREATE_ENTRY("unexpected_frv_rcvd", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_fatal_misc_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_misc_intr_bset),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_misc_intr_bset", psw_pwr_fatal_misc_intr_bset_prop);
fld_map_t psw_pwr_fatal_misc_intr_bclr {
CREATE_ENTRY("unexpected_frv_rcvd", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_fatal_misc_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fatal_misc_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fatal_misc_intr_bclr", psw_pwr_fatal_misc_intr_bclr_prop);
fld_map_t psw_pwr_non_fatal_intr_cause {
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
};auto psw_pwr_non_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_intr_cause", psw_pwr_non_fatal_intr_cause_prop);
fld_map_t psw_pwr_non_fatal_intr_stat {
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
};auto psw_pwr_non_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_intr_stat", psw_pwr_non_fatal_intr_stat_prop);
fld_map_t psw_pwr_non_fatal_intr_mask {
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
};auto psw_pwr_non_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_intr_mask", psw_pwr_non_fatal_intr_mask_prop);
fld_map_t psw_pwr_non_fatal_intr_bset {
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
};auto psw_pwr_non_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_intr_bset", psw_pwr_non_fatal_intr_bset_prop);
fld_map_t psw_pwr_non_fatal_intr_bclr {
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
};auto psw_pwr_non_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_intr_bclr", psw_pwr_non_fatal_intr_bclr_prop);
fld_map_t psw_pwr_non_fatal_misc_intr_cause {
CREATE_ENTRY("cfp_pkt_drop", 0, 1),
CREATE_ENTRY("main_pkt_drop", 1, 1),
CREATE_ENTRY("frv_error", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_non_fatal_misc_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_misc_intr_cause),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_misc_intr_cause", psw_pwr_non_fatal_misc_intr_cause_prop);
fld_map_t psw_pwr_non_fatal_misc_intr_stat {
CREATE_ENTRY("cfp_pkt_drop", 0, 1),
CREATE_ENTRY("main_pkt_drop", 1, 1),
CREATE_ENTRY("frv_error", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_non_fatal_misc_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_misc_intr_stat),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_misc_intr_stat", psw_pwr_non_fatal_misc_intr_stat_prop);
fld_map_t psw_pwr_non_fatal_misc_intr_mask {
CREATE_ENTRY("cfp_pkt_drop", 0, 1),
CREATE_ENTRY("main_pkt_drop", 1, 1),
CREATE_ENTRY("frv_error", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_non_fatal_misc_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_misc_intr_mask),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_misc_intr_mask", psw_pwr_non_fatal_misc_intr_mask_prop);
fld_map_t psw_pwr_non_fatal_misc_intr_bset {
CREATE_ENTRY("cfp_pkt_drop", 0, 1),
CREATE_ENTRY("main_pkt_drop", 1, 1),
CREATE_ENTRY("frv_error", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_non_fatal_misc_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_misc_intr_bset),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_misc_intr_bset", psw_pwr_non_fatal_misc_intr_bset_prop);
fld_map_t psw_pwr_non_fatal_misc_intr_bclr {
CREATE_ENTRY("cfp_pkt_drop", 0, 1),
CREATE_ENTRY("main_pkt_drop", 1, 1),
CREATE_ENTRY("frv_error", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_non_fatal_misc_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_non_fatal_misc_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_non_fatal_misc_intr_bclr", psw_pwr_non_fatal_misc_intr_bclr_prop);
fld_map_t psw_pwr_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_pwr_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_features),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_features", psw_pwr_features_prop);
fld_map_t psw_pwr_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_pwr_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_spare_pio),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_spare_pio", psw_pwr_spare_pio_prop);
fld_map_t psw_pwr_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_pwr_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_scratchpad),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_fatal_interrupt_status", psw_fatal_interrupt_status_prop);
fld_map_t psw_pwr_cfg_min_pkt_size {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_min_pkt_size_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_min_pkt_size),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_min_pkt_size", psw_pwr_cfg_min_pkt_size_prop);
fld_map_t psw_pwr_cfg_min_pkt_size_after_rewrite {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_min_pkt_size_after_rewrite_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_min_pkt_size_after_rewrite),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_sta_unexpected_frv_rcvd_error", psw_pwr_sta_unexpected_frv_rcvd_error_prop);
fld_map_t psw_pwr_mem_init_start_cfg {
CREATE_ENTRY("q_drop_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("src_pri_enq_cntr", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_mem_init_start_cfg),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_mem_init_start_cfg", psw_pwr_mem_init_start_cfg_prop);
fld_map_t psw_pwr_mem_init_done_status {
CREATE_ENTRY("q_drop_cntr", 0, 1),
CREATE_ENTRY("q_enq_cntr", 1, 1),
CREATE_ENTRY("src_pri_enq_cntr", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_pwr_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_mem_init_done_status),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_mem_init_done_status", psw_pwr_mem_init_done_status_prop);
fld_map_t psw_pwr_fla_slave_id {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_fla_slave_id_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_fla_slave_id),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_fla_slave_id", psw_pwr_fla_slave_id_prop);
fld_map_t psw_pwr_cfg_stream_mem_sel_ifpg {
CREATE_ENTRY("section0", 0, 2),
CREATE_ENTRY("section1", 2, 2),
CREATE_ENTRY("section2", 4, 2),
CREATE_ENTRY("section3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_stream_mem_sel_ifpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_stream_mem_sel_ifpg),
CSR_TYPE::REG_LST,
add_csr(psw_pwr_0, "psw_pwr_cfg_stream_mem_sel_ifpg", psw_pwr_cfg_stream_mem_sel_ifpg_prop);
fld_map_t psw_pwr_cfg_flex_clear_ifpg {
CREATE_ENTRY("stream0", 0, 1),
CREATE_ENTRY("stream1", 1, 1),
CREATE_ENTRY("stream2", 2, 1),
CREATE_ENTRY("stream3", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_flex_clear_ifpg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_flex_clear_ifpg),
CSR_TYPE::REG_LST,
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
CSR_TYPE::REG_LST,
add_csr(psw_pwr_0, "psw_pwr_cfg_back_pressure_ifpg", psw_pwr_cfg_back_pressure_ifpg_prop);
fld_map_t psw_pwr_cfg_repl_fifo_th {
CREATE_ENTRY("headroom", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto psw_pwr_cfg_repl_fifo_th_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_repl_fifo_th),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_repl_fifo_th", psw_pwr_cfg_repl_fifo_th_prop);
fld_map_t psw_pwr_cfg_cfp_hysteresis {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("thresh", 1, 14),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pwr_cfg_cfp_hysteresis_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_cfp_hysteresis),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_cfp_hysteresis", psw_pwr_cfg_cfp_hysteresis_prop);
fld_map_t psw_pwr_cfg_egress_mirror_ecn {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_egress_mirror_ecn_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_egress_mirror_ecn),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_egress_mirror_ecn", psw_pwr_cfg_egress_mirror_ecn_prop);
fld_map_t psw_pwr_cfg_q_drop_stats {
CREATE_ENTRY("psw_drop", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_q_drop_stats_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_q_drop_stats),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_spd", psw_pwr_cfg_spd_prop);
fld_map_t psw_pwr_cfg_egress_sample_info {
CREATE_ENTRY("send_to_fpg_en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_egress_sample_info_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_egress_sample_info),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_egress_sample_info", psw_pwr_cfg_egress_sample_info_prop);
fld_map_t psw_pwr_cfg_stream_dis {
CREATE_ENTRY("fp_stream_dis", 0, 24),
CREATE_ENTRY("epg_dis", 24, 3),
CREATE_ENTRY("__rsvd", 27, 37)
};auto psw_pwr_cfg_stream_dis_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_stream_dis),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
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
CSR_TYPE::REG_LST,
add_csr(psw_pwr_0, "psw_pwr_fpg_stream_mem_cnt", psw_pwr_fpg_stream_mem_cnt_prop);
fld_map_t psw_pwr_epg_stream_mem_cnt {
CREATE_ENTRY("curr_val", 0, 8),
CREATE_ENTRY("hwm_val", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_epg_stream_mem_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_epg_stream_mem_cnt),
CSR_TYPE::REG_LST,
add_csr(psw_pwr_0, "psw_pwr_epg_stream_mem_cnt", psw_pwr_epg_stream_mem_cnt_prop);
fld_map_t psw_pwr_repl_fifo_cnt {
CREATE_ENTRY("curr_val", 0, 8),
CREATE_ENTRY("hwm_val", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_repl_fifo_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_repl_fifo_cnt),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_repl_fifo_cnt", psw_pwr_repl_fifo_cnt_prop);
fld_map_t psw_pwr_cpr_cnt {
CREATE_ENTRY("cfp_prefetch_fifo", 0, 4),
CREATE_ENTRY("drop_cell_fifo", 4, 5),
CREATE_ENTRY("__rsvd", 9, 55)
};auto psw_pwr_cpr_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cpr_cnt),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_sram_log_cerr_vec", psw_pwr_sram_log_cerr_vec_prop);
fld_map_t psw_pwr_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_cerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_sram_log_cerr_syndrome", psw_pwr_sram_log_cerr_syndrome_prop);
fld_map_t psw_pwr_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_cerr_addr),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_sram_log_uerr_vec", psw_pwr_sram_log_uerr_vec_prop);
fld_map_t psw_pwr_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_uerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_sram_log_uerr_syndrome", psw_pwr_sram_log_uerr_syndrome_prop);
fld_map_t psw_pwr_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_sram_log_uerr_addr),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_sram_log_uerr_addr", psw_pwr_sram_log_uerr_addr_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_cln {
CREATE_ENTRY("vld", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pwr_cfg_pbuf_arb_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_cln", psw_pwr_cfg_pbuf_arb_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg0_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg0_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg0_streams_en),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg0_streams_en", psw_pwr_cfg_pbuf_arb_fpg0_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg1_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg1_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg1_streams_en),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg1_streams_en", psw_pwr_cfg_pbuf_arb_fpg1_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg2_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg2_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg2_streams_en),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg2_streams_en", psw_pwr_cfg_pbuf_arb_fpg2_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg3_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg3_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg3_streams_en),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg3_streams_en", psw_pwr_cfg_pbuf_arb_fpg3_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg4_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg4_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg4_streams_en),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg4_streams_en", psw_pwr_cfg_pbuf_arb_fpg4_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg5_streams_en {
CREATE_ENTRY("vec", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto psw_pwr_cfg_pbuf_arb_fpg5_streams_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg5_streams_en),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg5_streams_en", psw_pwr_cfg_pbuf_arb_fpg5_streams_en_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg0_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg0_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg0_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg0_cln", psw_pwr_cfg_pbuf_arb_fpg0_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg1_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg1_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg1_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg1_cln", psw_pwr_cfg_pbuf_arb_fpg1_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg2_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg2_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg2_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg2_cln", psw_pwr_cfg_pbuf_arb_fpg2_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg3_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg3_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg3_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg3_cln", psw_pwr_cfg_pbuf_arb_fpg3_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg4_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg4_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg4_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg4_cln", psw_pwr_cfg_pbuf_arb_fpg4_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_fpg5_cln {
CREATE_ENTRY("entry0", 0, 2),
CREATE_ENTRY("entry1", 2, 2),
CREATE_ENTRY("entry2", 4, 2),
CREATE_ENTRY("entry3", 6, 2),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pwr_cfg_pbuf_arb_fpg5_cln_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg5_cln),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg5_cln", psw_pwr_cfg_pbuf_arb_fpg5_cln_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_wrr_weights {
CREATE_ENTRY("epg0", 0, 4),
CREATE_ENTRY("epg1", 4, 4),
CREATE_ENTRY("epg2", 8, 4),
CREATE_ENTRY("spl_port", 12, 4),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pwr_cfg_pbuf_arb_wrr_weights_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_wrr_weights),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_wrr_weights", psw_pwr_cfg_pbuf_arb_wrr_weights_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_min_spacing {
CREATE_ENTRY("epg", 0, 5),
CREATE_ENTRY("spl_port", 5, 5),
CREATE_ENTRY("null_slot", 10, 16),
CREATE_ENTRY("__rsvd", 26, 38)
};auto psw_pwr_cfg_pbuf_arb_min_spacing_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_min_spacing),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_min_spacing", psw_pwr_cfg_pbuf_arb_min_spacing_prop);
fld_map_t psw_pwr_cfg_pbuf_arb_sync_tdm_delay {
CREATE_ENTRY("cnt", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto psw_pwr_cfg_pbuf_arb_sync_tdm_delay_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_sync_tdm_delay),
CSR_TYPE::REG,
add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_sync_tdm_delay", psw_pwr_cfg_pbuf_arb_sync_tdm_delay_prop);
fld_map_t psw_pwr_stats_cntrs {
CREATE_ENTRY("cnt", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto psw_pwr_stats_cntrs_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_stats_cntrs),
CSR_TYPE::TBL,
add_csr(psw_pwr_0, "psw_pwr_stats_cntrs", psw_pwr_stats_cntrs_prop);
fld_map_t psw_pwr_q_drop_cntr {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto psw_pwr_q_drop_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_q_drop_cntr),
CSR_TYPE::TBL,
add_csr(psw_pwr_0, "psw_pwr_q_drop_cntr", psw_pwr_q_drop_cntr_prop);
fld_map_t psw_pwr_q_enq_cntr {
CREATE_ENTRY("pkt_cnt", 0, 30),
CREATE_ENTRY("bytes_cnt", 30, 36),
CREATE_ENTRY("__rsvd", 66, 62)
};auto psw_pwr_q_enq_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_q_enq_cntr),
CSR_TYPE::TBL,
add_csr(psw_pwr_0, "psw_pwr_q_enq_cntr", psw_pwr_q_enq_cntr_prop);
fld_map_t psw_pwr_src_pri_enq_cntr {
CREATE_ENTRY("pkt_cnt", 0, 30),
CREATE_ENTRY("bytes_cnt", 30, 36),
CREATE_ENTRY("__rsvd", 66, 62)
};auto psw_pwr_src_pri_enq_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pwr_src_pri_enq_cntr),
CSR_TYPE::TBL,
add_csr(psw_pwr_0, "psw_pwr_src_pri_enq_cntr", psw_pwr_src_pri_enq_cntr_prop);
 // END psw_pwr 
}
{
 // BEGIN psw_orm 
auto psw_orm_0 = nu_rng[0].add_an({"psw_orm"}, 0x9280000, 1, 0x0);
fld_map_t psw_orm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_orm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_timeout_thresh_cfg),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_timeout_thresh_cfg", psw_orm_timeout_thresh_cfg_prop);
fld_map_t psw_orm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_orm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_timedout_sta),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_timedout_sta", psw_orm_timedout_sta_prop);
fld_map_t psw_orm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_orm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_timeout_clr),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_timeout_clr", psw_orm_timeout_clr_prop);
fld_map_t psw_orm_fatal_intr_cause {
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
};auto psw_orm_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_fatal_intr_cause", psw_orm_fatal_intr_cause_prop);
fld_map_t psw_orm_fatal_intr_stat {
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
};auto psw_orm_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_fatal_intr_stat", psw_orm_fatal_intr_stat_prop);
fld_map_t psw_orm_fatal_intr_mask {
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
};auto psw_orm_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_fatal_intr_mask", psw_orm_fatal_intr_mask_prop);
fld_map_t psw_orm_fatal_intr_bset {
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
};auto psw_orm_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_fatal_intr_bset", psw_orm_fatal_intr_bset_prop);
fld_map_t psw_orm_fatal_intr_bclr {
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
};auto psw_orm_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_fatal_intr_bclr", psw_orm_fatal_intr_bclr_prop);
fld_map_t psw_orm_non_fatal_intr_cause {
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
};auto psw_orm_non_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_non_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_non_fatal_intr_cause", psw_orm_non_fatal_intr_cause_prop);
fld_map_t psw_orm_non_fatal_intr_stat {
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
};auto psw_orm_non_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_non_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_non_fatal_intr_stat", psw_orm_non_fatal_intr_stat_prop);
fld_map_t psw_orm_non_fatal_intr_mask {
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
};auto psw_orm_non_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_non_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_non_fatal_intr_mask", psw_orm_non_fatal_intr_mask_prop);
fld_map_t psw_orm_non_fatal_intr_bset {
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
};auto psw_orm_non_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_non_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_non_fatal_intr_bset", psw_orm_non_fatal_intr_bset_prop);
fld_map_t psw_orm_non_fatal_intr_bclr {
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
};auto psw_orm_non_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_non_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_non_fatal_intr_bclr", psw_orm_non_fatal_intr_bclr_prop);
fld_map_t psw_orm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_orm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_features),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_features", psw_orm_features_prop);
fld_map_t psw_orm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_orm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_spare_pio),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_spare_pio", psw_orm_spare_pio_prop);
fld_map_t psw_orm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_orm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_scratchpad),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_scratchpad", psw_orm_scratchpad_prop);
fld_map_t psw_orm_cfg_glb_sh_thr {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("clear_hwm", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_cfg_glb_sh_thr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_cfg_glb_sh_thr),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_cfg_glb_sh_thr", psw_orm_cfg_glb_sh_thr_prop);
fld_map_t psw_orm_glb_sh_cnt {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_glb_sh_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_glb_sh_cnt),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_glb_sh_cnt", psw_orm_glb_sh_cnt_prop);
fld_map_t psw_orm_glb_sh_cnt_hwm {
CREATE_ENTRY("hwm_val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_glb_sh_cnt_hwm_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_glb_sh_cnt_hwm),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_glb_sh_cnt_hwm", psw_orm_glb_sh_cnt_hwm_prop);
fld_map_t psw_orm_glb_sh_pending_cnt {
CREATE_ENTRY("val", 0, 11),
CREATE_ENTRY("__rsvd", 11, 53)
};auto psw_orm_glb_sh_pending_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_glb_sh_pending_cnt),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_glb_sh_pending_cnt", psw_orm_glb_sh_pending_cnt_prop);
fld_map_t psw_orm_cfg_stats_color_en {
CREATE_ENTRY("green", 0, 1),
CREATE_ENTRY("yellow", 1, 1),
CREATE_ENTRY("red", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_orm_cfg_stats_color_en_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_cfg_stats_color_en),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_sram_log_cerr_vec", psw_orm_sram_log_cerr_vec_prop);
fld_map_t psw_orm_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_cerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_sram_log_cerr_syndrome", psw_orm_sram_log_cerr_syndrome_prop);
fld_map_t psw_orm_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_cerr_addr),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_sram_log_uerr_vec", psw_orm_sram_log_uerr_vec_prop);
fld_map_t psw_orm_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_uerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_sram_log_uerr_syndrome", psw_orm_sram_log_uerr_syndrome_prop);
fld_map_t psw_orm_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_orm_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_sram_log_uerr_addr),
CSR_TYPE::REG,
add_csr(psw_orm_0, "psw_orm_sram_log_uerr_addr", psw_orm_sram_log_uerr_addr_prop);
fld_map_t psw_orm_mem_q_cfg {
CREATE_ENTRY("min_thr", 0, 15),
CREATE_ENTRY("static_sh_thr_green", 15, 15),
CREATE_ENTRY("sh_dynamic_en", 30, 1),
CREATE_ENTRY("sh_thr_alpha", 31, 4),
CREATE_ENTRY("sh_thr_offset_yellow", 35, 15),
CREATE_ENTRY("sh_thr_offset_red", 50, 15),
CREATE_ENTRY("__rsvd", 65, 63)
};auto psw_orm_mem_q_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_q_cfg),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_q_cfg", psw_orm_mem_q_cfg_prop);
fld_map_t psw_orm_mem_q_cnt {
CREATE_ENTRY("min_cnt", 0, 15),
CREATE_ENTRY("port_min_cnt", 15, 15),
CREATE_ENTRY("sh_cnt", 30, 15),
CREATE_ENTRY("pending_cnt", 45, 11),
CREATE_ENTRY("__rsvd", 56, 8)
};auto psw_orm_mem_q_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_q_cnt),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_q_cnt", psw_orm_mem_q_cnt_prop);
fld_map_t psw_orm_mem_port_cfg {
CREATE_ENTRY("min_thr", 0, 15),
CREATE_ENTRY("sh_thr", 15, 15),
CREATE_ENTRY("__rsvd", 30, 34)
};auto psw_orm_mem_port_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_port_cfg),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_port_cfg", psw_orm_mem_port_cfg_prop);
fld_map_t psw_orm_mem_port_cnt {
CREATE_ENTRY("min_cnt", 0, 15),
CREATE_ENTRY("sh_cnt", 15, 15),
CREATE_ENTRY("pending_cnt", 30, 11),
CREATE_ENTRY("__rsvd", 41, 23)
};auto psw_orm_mem_port_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_port_cnt),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_port_cnt", psw_orm_mem_port_cnt_prop);
fld_map_t psw_orm_mem_stats_q_drop_cnt {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto psw_orm_mem_stats_q_drop_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_stats_q_drop_cnt),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_stats_q_drop_cnt", psw_orm_mem_stats_q_drop_cnt_prop);
fld_map_t psw_orm_mem_stats_q_peak_cnt {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_mem_stats_q_peak_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_stats_q_peak_cnt),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_stats_q_peak_cnt", psw_orm_mem_stats_q_peak_cnt_prop);
fld_map_t psw_orm_mem_stats_port_sh_drop_cnt {
CREATE_ENTRY("val", 0, 30),
CREATE_ENTRY("__rsvd", 30, 34)
};auto psw_orm_mem_stats_port_sh_drop_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_stats_port_sh_drop_cnt),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_stats_port_sh_drop_cnt", psw_orm_mem_stats_port_sh_drop_cnt_prop);
fld_map_t psw_orm_mem_stats_port_sh_peak_cnt {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_orm_mem_stats_port_sh_peak_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_orm_mem_stats_port_sh_peak_cnt),
CSR_TYPE::TBL,
add_csr(psw_orm_0, "psw_orm_mem_stats_port_sh_peak_cnt", psw_orm_mem_stats_port_sh_peak_cnt_prop);
 // END psw_orm 
}
{
 // BEGIN psw_pqm 
auto psw_pqm_0 = nu_rng[0].add_an({"psw_pqm"}, 0x9800000, 1, 0x0);
fld_map_t psw_pqm_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_pqm_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_timeout_thresh_cfg),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_timeout_thresh_cfg", psw_pqm_timeout_thresh_cfg_prop);
fld_map_t psw_pqm_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pqm_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_timedout_sta),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_timedout_sta", psw_pqm_timedout_sta_prop);
fld_map_t psw_pqm_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pqm_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_timeout_clr),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_timeout_clr", psw_pqm_timeout_clr_prop);
fld_map_t psw_pqm_fatal_intr_cause {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_fatal_intr_cause", psw_pqm_fatal_intr_cause_prop);
fld_map_t psw_pqm_fatal_intr_stat {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_fatal_intr_stat", psw_pqm_fatal_intr_stat_prop);
fld_map_t psw_pqm_fatal_intr_mask {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_fatal_intr_mask", psw_pqm_fatal_intr_mask_prop);
fld_map_t psw_pqm_fatal_intr_bset {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_fatal_intr_bset", psw_pqm_fatal_intr_bset_prop);
fld_map_t psw_pqm_fatal_intr_bclr {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_fatal_intr_bclr", psw_pqm_fatal_intr_bclr_prop);
fld_map_t psw_pqm_non_fatal_intr_cause {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_non_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_non_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_non_fatal_intr_cause", psw_pqm_non_fatal_intr_cause_prop);
fld_map_t psw_pqm_non_fatal_intr_stat {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_non_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_non_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_non_fatal_intr_stat", psw_pqm_non_fatal_intr_stat_prop);
fld_map_t psw_pqm_non_fatal_intr_mask {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_non_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_non_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_non_fatal_intr_mask", psw_pqm_non_fatal_intr_mask_prop);
fld_map_t psw_pqm_non_fatal_intr_bset {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_non_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_non_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_non_fatal_intr_bset", psw_pqm_non_fatal_intr_bset_prop);
fld_map_t psw_pqm_non_fatal_intr_bclr {
CREATE_ENTRY("stats_pg_deq_cntr", 0, 1),
CREATE_ENTRY("stats_q_deq_cntr", 1, 1),
CREATE_ENTRY("tail_shd", 2, 1),
CREATE_ENTRY("tail_main", 3, 1),
CREATE_ENTRY("head_shd", 4, 1),
CREATE_ENTRY("head_main", 5, 1),
CREATE_ENTRY("pkt_desc", 6, 1),
CREATE_ENTRY("link", 7, 1),
CREATE_ENTRY("__rsvd", 8, 56)
};auto psw_pqm_non_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_non_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_non_fatal_intr_bclr", psw_pqm_non_fatal_intr_bclr_prop);
fld_map_t psw_pqm_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_pqm_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_features),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_features", psw_pqm_features_prop);
fld_map_t psw_pqm_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_spare_pio),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_spare_pio", psw_pqm_spare_pio_prop);
fld_map_t psw_pqm_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_scratchpad),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_mem_init_done_status", psw_pqm_mem_init_done_status_prop);
fld_map_t psw_pqm_sta_q_empty_fpg0 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_fpg0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_fpg0),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_fpg0", psw_pqm_sta_q_empty_fpg0_prop);
fld_map_t psw_pqm_sta_q_empty_fpg1 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_fpg1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_fpg1),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_fpg1", psw_pqm_sta_q_empty_fpg1_prop);
fld_map_t psw_pqm_sta_q_empty_fpg2 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_fpg2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_fpg2),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_fpg2", psw_pqm_sta_q_empty_fpg2_prop);
fld_map_t psw_pqm_sta_q_empty_fpg3 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_fpg3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_fpg3),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_fpg3", psw_pqm_sta_q_empty_fpg3_prop);
fld_map_t psw_pqm_sta_q_empty_fpg4 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_fpg4_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_fpg4),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_fpg4", psw_pqm_sta_q_empty_fpg4_prop);
fld_map_t psw_pqm_sta_q_empty_fpg5 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_fpg5_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_fpg5),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_fpg5", psw_pqm_sta_q_empty_fpg5_prop);
fld_map_t psw_pqm_sta_q_empty_epg0 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_epg0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_epg0),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_epg0", psw_pqm_sta_q_empty_epg0_prop);
fld_map_t psw_pqm_sta_q_empty_epg1 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_epg1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_epg1),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_epg1", psw_pqm_sta_q_empty_epg1_prop);
fld_map_t psw_pqm_sta_q_empty_epg2 {
CREATE_ENTRY("vec", 0, 64)
};auto psw_pqm_sta_q_empty_epg2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_epg2),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_epg2", psw_pqm_sta_q_empty_epg2_prop);
fld_map_t psw_pqm_sta_q_empty_purge_port {
CREATE_ENTRY("vec", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_pqm_sta_q_empty_purge_port_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sta_q_empty_purge_port),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sta_q_empty_purge_port", psw_pqm_sta_q_empty_purge_port_prop);
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
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sram_log_cerr_vec", psw_pqm_sram_log_cerr_vec_prop);
fld_map_t psw_pqm_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_cerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sram_log_cerr_syndrome", psw_pqm_sram_log_cerr_syndrome_prop);
fld_map_t psw_pqm_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_cerr_addr),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sram_log_uerr_vec", psw_pqm_sram_log_uerr_vec_prop);
fld_map_t psw_pqm_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_uerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sram_log_uerr_syndrome", psw_pqm_sram_log_uerr_syndrome_prop);
fld_map_t psw_pqm_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_pqm_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_sram_log_uerr_addr),
CSR_TYPE::REG,
add_csr(psw_pqm_0, "psw_pqm_sram_log_uerr_addr", psw_pqm_sram_log_uerr_addr_prop);
fld_map_t psw_pqm_mem_pkt_desc {
CREATE_ENTRY("val", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto psw_pqm_mem_pkt_desc_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_pkt_desc),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_mem_pkt_desc", psw_pqm_mem_pkt_desc_prop);
fld_map_t psw_pqm_mem_link {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pqm_mem_link_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_link),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_mem_link", psw_pqm_mem_link_prop);
fld_map_t psw_pqm_mem_head_main {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pqm_mem_head_main_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_head_main),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_mem_head_main", psw_pqm_mem_head_main_prop);
fld_map_t psw_pqm_mem_head_shd {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pqm_mem_head_shd_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_head_shd),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_mem_head_shd", psw_pqm_mem_head_shd_prop);
fld_map_t psw_pqm_mem_tail_main {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pqm_mem_tail_main_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_tail_main),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_mem_tail_main", psw_pqm_mem_tail_main_prop);
fld_map_t psw_pqm_mem_tail_shd {
CREATE_ENTRY("val", 0, 15),
CREATE_ENTRY("__rsvd", 15, 49)
};auto psw_pqm_mem_tail_shd_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_mem_tail_shd),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_mem_tail_shd", psw_pqm_mem_tail_shd_prop);
fld_map_t psw_pqm_stats_q_deq_cntr {
CREATE_ENTRY("pkt_cnt", 0, 30),
CREATE_ENTRY("bytes_cnt", 30, 36),
CREATE_ENTRY("__rsvd", 66, 62)
};auto psw_pqm_stats_q_deq_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_stats_q_deq_cntr),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_stats_q_deq_cntr", psw_pqm_stats_q_deq_cntr_prop);
fld_map_t psw_pqm_stats_pg_deq_cntr {
CREATE_ENTRY("pkt_cnt", 0, 30),
CREATE_ENTRY("bytes_cnt", 30, 36),
CREATE_ENTRY("__rsvd", 66, 62)
};auto psw_pqm_stats_pg_deq_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_stats_pg_deq_cntr),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_stats_pg_deq_cntr", psw_pqm_stats_pg_deq_cntr_prop);
fld_map_t psw_pqm_dbg_probe_enq0 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_enq0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_enq0),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq0", psw_pqm_dbg_probe_enq0_prop);
fld_map_t psw_pqm_dbg_probe_enq1 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_enq1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_enq1),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq1", psw_pqm_dbg_probe_enq1_prop);
fld_map_t psw_pqm_dbg_probe_enq2 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_enq2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_enq2),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq2", psw_pqm_dbg_probe_enq2_prop);
fld_map_t psw_pqm_dbg_probe_enq3 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_enq3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_enq3),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq3", psw_pqm_dbg_probe_enq3_prop);
fld_map_t psw_pqm_dbg_probe_deq0 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_deq0_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_deq0),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq0", psw_pqm_dbg_probe_deq0_prop);
fld_map_t psw_pqm_dbg_probe_deq1 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_deq1_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_deq1),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq1", psw_pqm_dbg_probe_deq1_prop);
fld_map_t psw_pqm_dbg_probe_deq2 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_deq2_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_deq2),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq2", psw_pqm_dbg_probe_deq2_prop);
fld_map_t psw_pqm_dbg_probe_deq3 {
CREATE_ENTRY("val", 0, 64)
};auto psw_pqm_dbg_probe_deq3_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_dbg_probe_deq3),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq3", psw_pqm_dbg_probe_deq3_prop);
fld_map_t psw_pqm_stats_cntrs {
CREATE_ENTRY("cnt", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto psw_pqm_stats_cntrs_prop = csr_prop_t(
std::make_shared<csr_s>(psw_pqm_stats_cntrs),
CSR_TYPE::TBL,
add_csr(psw_pqm_0, "psw_pqm_stats_cntrs", psw_pqm_stats_cntrs_prop);
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
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_timeout_thresh_cfg", psw_cfp_timeout_thresh_cfg_prop);
fld_map_t psw_cfp_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_timedout_sta),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_timedout_sta", psw_cfp_timedout_sta_prop);
fld_map_t psw_cfp_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_timeout_clr),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_timeout_clr", psw_cfp_timeout_clr_prop);
fld_map_t psw_cfp_fatal_intr_cause {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_intr_cause", psw_cfp_fatal_intr_cause_prop);
fld_map_t psw_cfp_fatal_intr_stat {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_intr_stat", psw_cfp_fatal_intr_stat_prop);
fld_map_t psw_cfp_fatal_intr_mask {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_intr_mask", psw_cfp_fatal_intr_mask_prop);
fld_map_t psw_cfp_fatal_intr_bset {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_intr_bset", psw_cfp_fatal_intr_bset_prop);
fld_map_t psw_cfp_fatal_intr_bclr {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_intr_bclr", psw_cfp_fatal_intr_bclr_prop);
fld_map_t psw_cfp_fatal_misc_intr_cause {
CREATE_ENTRY("fld_dealloc_err", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_fatal_misc_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_misc_intr_cause),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_misc_intr_cause", psw_cfp_fatal_misc_intr_cause_prop);
fld_map_t psw_cfp_fatal_misc_intr_stat {
CREATE_ENTRY("fld_dealloc_err", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_fatal_misc_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_misc_intr_stat),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_misc_intr_stat", psw_cfp_fatal_misc_intr_stat_prop);
fld_map_t psw_cfp_fatal_misc_intr_mask {
CREATE_ENTRY("fld_dealloc_err", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_fatal_misc_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_misc_intr_mask),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_misc_intr_mask", psw_cfp_fatal_misc_intr_mask_prop);
fld_map_t psw_cfp_fatal_misc_intr_bset {
CREATE_ENTRY("fld_dealloc_err", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_fatal_misc_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_misc_intr_bset),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_misc_intr_bset", psw_cfp_fatal_misc_intr_bset_prop);
fld_map_t psw_cfp_fatal_misc_intr_bclr {
CREATE_ENTRY("fld_dealloc_err", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_fatal_misc_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_fatal_misc_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_fatal_misc_intr_bclr", psw_cfp_fatal_misc_intr_bclr_prop);
fld_map_t psw_cfp_non_fatal_intr_cause {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_non_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_non_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_non_fatal_intr_cause", psw_cfp_non_fatal_intr_cause_prop);
fld_map_t psw_cfp_non_fatal_intr_stat {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_non_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_non_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_non_fatal_intr_stat", psw_cfp_non_fatal_intr_stat_prop);
fld_map_t psw_cfp_non_fatal_intr_mask {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_non_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_non_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_non_fatal_intr_mask", psw_cfp_non_fatal_intr_mask_prop);
fld_map_t psw_cfp_non_fatal_intr_bset {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_non_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_non_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_non_fatal_intr_bset", psw_cfp_non_fatal_intr_bset_prop);
fld_map_t psw_cfp_non_fatal_intr_bclr {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_non_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_non_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_non_fatal_intr_bclr", psw_cfp_non_fatal_intr_bclr_prop);
fld_map_t psw_cfp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto psw_cfp_features_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_features),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_features", psw_cfp_features_prop);
fld_map_t psw_cfp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto psw_cfp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_spare_pio),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_spare_pio", psw_cfp_spare_pio_prop);
fld_map_t psw_cfp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto psw_cfp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_scratchpad),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_scratchpad", psw_cfp_scratchpad_prop);
fld_map_t psw_cfp_mem_init_start_cfg {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_mem_init_start_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_mem_init_start_cfg),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_mem_init_start_cfg", psw_cfp_mem_init_start_cfg_prop);
fld_map_t psw_cfp_mem_init_done_status {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_mem_init_done_status_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_mem_init_done_status),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_mem_init_done_status", psw_cfp_mem_init_done_status_prop);
fld_map_t psw_cfp_cnt {
CREATE_ENTRY("curr_val", 0, 15),
CREATE_ENTRY("hwm_val", 15, 15),
CREATE_ENTRY("__rsvd", 30, 34)
};auto psw_cfp_cnt_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_cnt),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_cnt", psw_cfp_cnt_prop);
fld_map_t psw_cfp_cfg_clear_hwm {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto psw_cfp_cfg_clear_hwm_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_cfg_clear_hwm),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_cfg_clear_hwm", psw_cfp_cfg_clear_hwm_prop);
fld_map_t psw_cfp_sram_err_inj_cfg {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("err_type", 2, 1),
CREATE_ENTRY("__rsvd", 3, 61)
};auto psw_cfp_sram_err_inj_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_err_inj_cfg),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_err_inj_cfg", psw_cfp_sram_err_inj_cfg_prop);
fld_map_t psw_cfp_sram_log_cerr_vec {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_sram_log_cerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_cerr_vec),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_log_cerr_vec", psw_cfp_sram_log_cerr_vec_prop);
fld_map_t psw_cfp_sram_log_cerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_cerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_cerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_log_cerr_syndrome", psw_cfp_sram_log_cerr_syndrome_prop);
fld_map_t psw_cfp_sram_log_cerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_cerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_cerr_addr),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_log_cerr_addr", psw_cfp_sram_log_cerr_addr_prop);
fld_map_t psw_cfp_sram_log_uerr_vec {
CREATE_ENTRY("cct", 0, 1),
CREATE_ENTRY("bitalloc", 1, 1),
CREATE_ENTRY("__rsvd", 2, 62)
};auto psw_cfp_sram_log_uerr_vec_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_uerr_vec),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_log_uerr_vec", psw_cfp_sram_log_uerr_vec_prop);
fld_map_t psw_cfp_sram_log_uerr_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_uerr_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_uerr_syndrome),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_log_uerr_syndrome", psw_cfp_sram_log_uerr_syndrome_prop);
fld_map_t psw_cfp_sram_log_uerr_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto psw_cfp_sram_log_uerr_addr_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_sram_log_uerr_addr),
CSR_TYPE::REG,
add_csr(psw_cfp_0, "psw_cfp_sram_log_uerr_addr", psw_cfp_sram_log_uerr_addr_prop);
fld_map_t psw_cfp_mem_cct {
CREATE_ENTRY("val", 0, 64)
};auto psw_cfp_mem_cct_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_mem_cct),
CSR_TYPE::TBL,
add_csr(psw_cfp_0, "psw_cfp_mem_cct", psw_cfp_mem_cct_prop);
fld_map_t psw_cfp_bitalloc {
CREATE_ENTRY("val", 0, 64)
};auto psw_cfp_bitalloc_prop = csr_prop_t(
std::make_shared<csr_s>(psw_cfp_bitalloc),
CSR_TYPE::TBL,
add_csr(psw_cfp_0, "psw_cfp_bitalloc", psw_cfp_bitalloc_prop);
 // END psw_cfp 
}
{
 // BEGIN efp_rfp_lcl 
auto efp_rfp_lcl_0 = nu_rng[0].add_an({"efp_rfp","efp_rfp_lcl"}, 0xCE00000, 1, 0x0);
fld_map_t efp_rfp_lcl_timeout_thresh_cfg {
CREATE_ENTRY("val", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_lcl_timeout_thresh_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_timeout_thresh_cfg),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timeout_thresh_cfg", efp_rfp_lcl_timeout_thresh_cfg_prop);
fld_map_t efp_rfp_lcl_timedout_sta {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_lcl_timedout_sta_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_timedout_sta),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timedout_sta", efp_rfp_lcl_timedout_sta_prop);
fld_map_t efp_rfp_lcl_timeout_clr {
CREATE_ENTRY("val", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_lcl_timeout_clr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_timeout_clr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timeout_clr", efp_rfp_lcl_timeout_clr_prop);
fld_map_t efp_rfp_lcl_fatal_intr_cause {
CREATE_ENTRY("efp_rfp_rad_mem_ucerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_ucerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_ucerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_ucerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_ucerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_ucerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_ucerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_ucerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_ucerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_ucerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_ucerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_ucerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack0_wdog", 12, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack1_wdog", 13, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack2_wdog", 14, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc0_wdog", 15, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc1_wdog", 16, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc2_wdog", 17, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc3_wdog", 18, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc4_wdog", 19, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc5_wdog", 20, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc6_wdog", 21, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc7_wdog", 22, 1),
CREATE_ENTRY("efp_rfp_mhg_single_flit", 23, 1),
CREATE_ENTRY("efp_rfp_mhg_gt256", 24, 1),
CREATE_ENTRY("__rsvd", 25, 39)
};auto efp_rfp_lcl_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_fatal_intr_cause", efp_rfp_lcl_fatal_intr_cause_prop);
fld_map_t efp_rfp_lcl_fatal_intr_stat {
CREATE_ENTRY("efp_rfp_rad_mem_ucerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_ucerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_ucerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_ucerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_ucerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_ucerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_ucerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_ucerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_ucerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_ucerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_ucerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_ucerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack0_wdog", 12, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack1_wdog", 13, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack2_wdog", 14, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc0_wdog", 15, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc1_wdog", 16, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc2_wdog", 17, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc3_wdog", 18, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc4_wdog", 19, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc5_wdog", 20, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc6_wdog", 21, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc7_wdog", 22, 1),
CREATE_ENTRY("efp_rfp_mhg_single_flit", 23, 1),
CREATE_ENTRY("efp_rfp_mhg_gt256", 24, 1),
CREATE_ENTRY("__rsvd", 25, 39)
};auto efp_rfp_lcl_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_fatal_intr_stat", efp_rfp_lcl_fatal_intr_stat_prop);
fld_map_t efp_rfp_lcl_fatal_intr_mask {
CREATE_ENTRY("efp_rfp_rad_mem_ucerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_ucerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_ucerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_ucerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_ucerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_ucerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_ucerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_ucerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_ucerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_ucerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_ucerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_ucerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack0_wdog", 12, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack1_wdog", 13, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack2_wdog", 14, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc0_wdog", 15, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc1_wdog", 16, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc2_wdog", 17, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc3_wdog", 18, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc4_wdog", 19, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc5_wdog", 20, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc6_wdog", 21, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc7_wdog", 22, 1),
CREATE_ENTRY("efp_rfp_mhg_single_flit", 23, 1),
CREATE_ENTRY("efp_rfp_mhg_gt256", 24, 1),
CREATE_ENTRY("__rsvd", 25, 39)
};auto efp_rfp_lcl_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_fatal_intr_mask", efp_rfp_lcl_fatal_intr_mask_prop);
fld_map_t efp_rfp_lcl_fatal_intr_bset {
CREATE_ENTRY("efp_rfp_rad_mem_ucerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_ucerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_ucerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_ucerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_ucerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_ucerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_ucerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_ucerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_ucerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_ucerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_ucerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_ucerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack0_wdog", 12, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack1_wdog", 13, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack2_wdog", 14, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc0_wdog", 15, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc1_wdog", 16, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc2_wdog", 17, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc3_wdog", 18, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc4_wdog", 19, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc5_wdog", 20, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc6_wdog", 21, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc7_wdog", 22, 1),
CREATE_ENTRY("efp_rfp_mhg_single_flit", 23, 1),
CREATE_ENTRY("efp_rfp_mhg_gt256", 24, 1),
CREATE_ENTRY("__rsvd", 25, 39)
};auto efp_rfp_lcl_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_fatal_intr_bset", efp_rfp_lcl_fatal_intr_bset_prop);
fld_map_t efp_rfp_lcl_fatal_intr_bclr {
CREATE_ENTRY("efp_rfp_rad_mem_ucerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_ucerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_ucerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_ucerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_ucerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_ucerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_ucerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_ucerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_ucerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_ucerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_ucerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_ucerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack0_wdog", 12, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack1_wdog", 13, 1),
CREATE_ENTRY("efp_rfp_last_wr_ack2_wdog", 14, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc0_wdog", 15, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc1_wdog", 16, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc2_wdog", 17, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc3_wdog", 18, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc4_wdog", 19, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc5_wdog", 20, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc6_wdog", 21, 1),
CREATE_ENTRY("efp_rfp_alloc_resp_pc7_wdog", 22, 1),
CREATE_ENTRY("efp_rfp_mhg_single_flit", 23, 1),
CREATE_ENTRY("efp_rfp_mhg_gt256", 24, 1),
CREATE_ENTRY("__rsvd", 25, 39)
};auto efp_rfp_lcl_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_fatal_intr_bclr", efp_rfp_lcl_fatal_intr_bclr_prop);
fld_map_t efp_rfp_lcl_non_fatal_intr_cause {
CREATE_ENTRY("efp_rfp_rad_mem_cerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_cerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_cerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_cerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_cerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_cerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_cerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_cerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_cerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_cerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_cerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_cerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem_perr_intr", 12, 1),
CREATE_ENTRY("efp_rfp_clbp_mem_perr_intr", 13, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem_perr_intr", 14, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem_perr_intr", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_lcl_non_fatal_intr_cause_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_non_fatal_intr_cause),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_non_fatal_intr_cause", efp_rfp_lcl_non_fatal_intr_cause_prop);
fld_map_t efp_rfp_lcl_non_fatal_intr_stat {
CREATE_ENTRY("efp_rfp_rad_mem_cerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_cerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_cerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_cerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_cerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_cerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_cerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_cerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_cerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_cerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_cerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_cerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem_perr_intr", 12, 1),
CREATE_ENTRY("efp_rfp_clbp_mem_perr_intr", 13, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem_perr_intr", 14, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem_perr_intr", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_lcl_non_fatal_intr_stat_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_non_fatal_intr_stat),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_non_fatal_intr_stat", efp_rfp_lcl_non_fatal_intr_stat_prop);
fld_map_t efp_rfp_lcl_non_fatal_intr_mask {
CREATE_ENTRY("efp_rfp_rad_mem_cerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_cerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_cerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_cerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_cerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_cerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_cerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_cerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_cerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_cerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_cerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_cerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem_perr_intr", 12, 1),
CREATE_ENTRY("efp_rfp_clbp_mem_perr_intr", 13, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem_perr_intr", 14, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem_perr_intr", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_lcl_non_fatal_intr_mask_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_non_fatal_intr_mask),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_non_fatal_intr_mask", efp_rfp_lcl_non_fatal_intr_mask_prop);
fld_map_t efp_rfp_lcl_non_fatal_intr_bset {
CREATE_ENTRY("efp_rfp_rad_mem_cerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_cerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_cerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_cerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_cerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_cerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_cerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_cerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_cerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_cerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_cerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_cerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem_perr_intr", 12, 1),
CREATE_ENTRY("efp_rfp_clbp_mem_perr_intr", 13, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem_perr_intr", 14, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem_perr_intr", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_lcl_non_fatal_intr_bset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_non_fatal_intr_bset),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_non_fatal_intr_bset", efp_rfp_lcl_non_fatal_intr_bset_prop);
fld_map_t efp_rfp_lcl_non_fatal_intr_bclr {
CREATE_ENTRY("efp_rfp_rad_mem_cerr_intr", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0_cerr_intr", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1_cerr_intr", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2_cerr_intr", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0_cerr_intr", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1_cerr_intr", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf_cerr_intr", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf_cerr_intr", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf_cerr_intr", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf_cerr_intr", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data_cerr_intr", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq_cerr_intr", 11, 1),
CREATE_ENTRY("efp_rfp_rewr_inst_mem_perr_intr", 12, 1),
CREATE_ENTRY("efp_rfp_clbp_mem_perr_intr", 13, 1),
CREATE_ENTRY("efp_rfp_lb_grp_mem_perr_intr", 14, 1),
CREATE_ENTRY("efp_rfp_bmpool_nd_map_mem_perr_intr", 15, 1),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_lcl_non_fatal_intr_bclr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lcl_non_fatal_intr_bclr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_non_fatal_intr_bclr", efp_rfp_lcl_non_fatal_intr_bclr_prop);
fld_map_t efp_rfp_features {
CREATE_ENTRY("module_id", 0, 8),
CREATE_ENTRY("version", 8, 8),
CREATE_ENTRY("features", 16, 16),
CREATE_ENTRY("Reserved", 32, 32)
};auto efp_rfp_features_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_features),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_features", efp_rfp_features_prop);
fld_map_t efp_rfp_spare_pio {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_spare_pio_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_spare_pio),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_spare_pio", efp_rfp_spare_pio_prop);
fld_map_t efp_rfp_scratchpad {
CREATE_ENTRY("val", 0, 64)
};auto efp_rfp_scratchpad_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_scratchpad),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_scratchpad", efp_rfp_scratchpad_prop);
fld_map_t efp_rfp_parser_offset {
CREATE_ENTRY("offset", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_parser_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_parser_offset),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_parser_offset", efp_rfp_parser_offset_prop);
fld_map_t efp_rfp_wct_macro_cfg {
CREATE_ENTRY("decimal_rollover_en", 0, 1),
CREATE_ENTRY("base_incr", 1, 26),
CREATE_ENTRY("base_corr_incr", 27, 26),
CREATE_ENTRY("override_incr", 53, 26),
CREATE_ENTRY("base_period", 79, 16),
CREATE_ENTRY("override_cnt", 95, 16),
CREATE_ENTRY("override_mode", 111, 1),
CREATE_ENTRY("sync_pulse_dly_sel", 112, 4),
CREATE_ENTRY("__rsvd", 116, 12)
};auto efp_rfp_wct_macro_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_wct_macro_cfg),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_wct_macro_cfg", efp_rfp_wct_macro_cfg_prop);
fld_map_t efp_rfp_trfc_prfl {
CREATE_ENTRY("efp_rfp_trfc_pri", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_trfc_prfl_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_trfc_prfl),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_trfc_prfl", efp_rfp_trfc_prfl_prop);
fld_map_t efp_rfp_rsrc_prf_strt {
CREATE_ENTRY("start_pref", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto efp_rfp_rsrc_prf_strt_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rsrc_prf_strt),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prf_strt", efp_rfp_rsrc_prf_strt_prop);
fld_map_t efp_rfp_rsrc_prf_done {
CREATE_ENTRY("pref_done", 0, 9),
CREATE_ENTRY("__rsvd", 9, 55)
};auto efp_rfp_rsrc_prf_done_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rsrc_prf_done),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prf_done", efp_rfp_rsrc_prf_done_prop);
fld_map_t efp_rfp_num_bh_prf {
CREATE_ENTRY("num_bh", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_num_bh_prf_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_num_bh_prf),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_num_bh_prf", efp_rfp_num_bh_prf_prop);
fld_map_t efp_rfp_num_au_prf {
CREATE_ENTRY("num_au", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto efp_rfp_num_au_prf_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_num_au_prf),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_num_au_prf", efp_rfp_num_au_prf_prop);
fld_map_t efp_rfp_bh_req_thr {
CREATE_ENTRY("bh_req_thr", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_bh_req_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bh_req_thr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_bh_req_thr", efp_rfp_bh_req_thr_prop);
fld_map_t efp_rfp_au_req_thr {
CREATE_ENTRY("au_req_thr", 0, 7),
CREATE_ENTRY("__rsvd", 7, 57)
};auto efp_rfp_au_req_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_au_req_thr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_au_req_thr", efp_rfp_au_req_thr_prop);
fld_map_t efp_rfp_au_cntr {
CREATE_ENTRY("num_au_pref", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_au_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_au_cntr),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_au_cntr", efp_rfp_au_cntr_prop);
fld_map_t efp_rfp_bh_sts {
CREATE_ENTRY("num_bh_pref", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_bh_sts_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bh_sts),
CSR_TYPE::REG_LST,
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
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_pc_cl_opts", efp_rfp_pc_cl_opts_prop);
fld_map_t efp_rfp_max_bh_allc_rq {
CREATE_ENTRY("num_bh", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_max_bh_allc_rq_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_max_bh_allc_rq),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_max_bh_allc_rq", efp_rfp_max_bh_allc_rq_prop);
fld_map_t efp_rfp_max_au_allc_rq {
CREATE_ENTRY("num_au", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_max_au_allc_rq_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_max_au_allc_rq),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_max_au_allc_rq", efp_rfp_max_au_allc_rq_prop);
fld_map_t efp_rfp_max_pend_allc_req {
CREATE_ENTRY("max_num", 0, 4),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_max_pend_allc_req_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_max_pend_allc_req),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_max_pend_allc_req", efp_rfp_max_pend_allc_req_prop);
fld_map_t efp_rfp_rsrc_prefetch_pool {
CREATE_ENTRY("pool", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_rsrc_prefetch_pool_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rsrc_prefetch_pool),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prefetch_pool", efp_rfp_rsrc_prefetch_pool_prop);
fld_map_t efp_rfp_clr_map_indv_pool {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_indv_pool_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_indv_pool),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_indv_pool", efp_rfp_clr_map_indv_pool_prop);
fld_map_t efp_rfp_clr_map_tot_pool {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_tot_pool_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_tot_pool),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_tot_pool", efp_rfp_clr_map_tot_pool_prop);
fld_map_t efp_rfp_tot_bmpool_xoff {
CREATE_ENTRY("psw_sch_node", 0, 24),
CREATE_ENTRY("psw_xoff_q_vec", 24, 8),
CREATE_ENTRY("fcb_sch_node", 32, 8),
CREATE_ENTRY("fcb_xoff_q_vec", 40, 8),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_tot_bmpool_xoff_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_tot_bmpool_xoff),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_tot_bmpool_xoff", efp_rfp_tot_bmpool_xoff_prop);
fld_map_t efp_rfp_wu_thr_xoff {
CREATE_ENTRY("psw_sch_node", 0, 24),
CREATE_ENTRY("psw_xoff_q_vec", 24, 8),
CREATE_ENTRY("fcb_sch_node", 32, 8),
CREATE_ENTRY("fcb_xoff_q_vec", 40, 8),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_wu_thr_xoff_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_wu_thr_xoff),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_wu_thr_xoff", efp_rfp_wu_thr_xoff_prop);
fld_map_t efp_rfp_psw_nd_st {
CREATE_ENTRY("node_state", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_psw_nd_st_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_psw_nd_st),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_psw_nd_st", efp_rfp_psw_nd_st_prop);
fld_map_t efp_rfp_fcb_nd_st {
CREATE_ENTRY("node_state", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_fcb_nd_st_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcb_nd_st),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_fcb_nd_st", efp_rfp_fcb_nd_st_prop);
fld_map_t efp_rfp_clr_map_tot_wu_occ {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_tot_wu_occ_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_tot_wu_occ),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_tot_wu_occ", efp_rfp_clr_map_tot_wu_occ_prop);
fld_map_t efp_rfp_clr_map_nut_wu_occ {
CREATE_ENTRY("clr_map", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_clr_map_nut_wu_occ_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clr_map_nut_wu_occ),
CSR_TYPE::REG_LST,
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
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_kuc", efp_rfp_l4cs_kuc_prop);
fld_map_t efp_rfp_proto_lst {
CREATE_ENTRY("tcp_proto", 0, 8),
CREATE_ENTRY("udp_proto", 8, 8),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_proto_lst_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_proto_lst),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_proto_lst", efp_rfp_proto_lst_prop);
fld_map_t efp_rfp_rad_past_thr {
CREATE_ENTRY("age_delta", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_rad_past_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_past_thr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_past_thr", efp_rfp_rad_past_thr_prop);
fld_map_t efp_rfp_rad_futr_thr {
CREATE_ENTRY("age_delta", 0, 48),
CREATE_ENTRY("__rsvd", 48, 16)
};auto efp_rfp_rad_futr_thr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_futr_thr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_futr_thr", efp_rfp_rad_futr_thr_prop);
fld_map_t efp_rfp_rad_enable {
CREATE_ENTRY("en", 0, 1),
CREATE_ENTRY("__rsvd", 1, 63)
};auto efp_rfp_rad_enable_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_enable),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_enable", efp_rfp_rad_enable_prop);
fld_map_t efp_rfp_estrm_bmpool_map {
CREATE_ENTRY("bmpool", 0, 6),
CREATE_ENTRY("__rsvd", 6, 58)
};auto efp_rfp_estrm_bmpool_map_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_estrm_bmpool_map),
CSR_TYPE::REG_LST,
add_csr(efp_rfp_lcl_0, "efp_rfp_estrm_bmpool_map", efp_rfp_estrm_bmpool_map_prop);
fld_map_t efp_rfp_fcp_pkt_adj {
CREATE_ENTRY("fcb_adj_val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_fcp_pkt_adj_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_pkt_adj),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_pkt_adj", efp_rfp_fcp_pkt_adj_prop);
fld_map_t efp_rfp_fcp_block_sz {
CREATE_ENTRY("fld_blk_sz", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto efp_rfp_fcp_block_sz_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_block_sz),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_block_sz", efp_rfp_fcp_block_sz_prop);
fld_map_t efp_rfp_gph_sz {
CREATE_ENTRY("gph_sz", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_gph_sz_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_gph_sz),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_gph_sz", efp_rfp_gph_sz_prop);
fld_map_t efp_rfp_fcp_qos_slct {
CREATE_ENTRY("bit_slct", 0, 2),
CREATE_ENTRY("__rsvd", 2, 62)
};auto efp_rfp_fcp_qos_slct_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_qos_slct),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_qos_slct", efp_rfp_fcp_qos_slct_prop);
fld_map_t efp_rfp_fcp_stream_cfg {
CREATE_ENTRY("fcp_stream", 0, 3),
CREATE_ENTRY("fcp_present", 3, 1),
CREATE_ENTRY("__rsvd", 4, 60)
};auto efp_rfp_fcp_stream_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fcp_stream_cfg),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_stream_cfg", efp_rfp_fcp_stream_cfg_prop);
fld_map_t efp_rfp_fla_ring_module_id_cfg {
CREATE_ENTRY("fld_val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_fla_ring_module_id_cfg_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_fla_ring_module_id_cfg),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_fla_ring_module_id_cfg", efp_rfp_fla_ring_module_id_cfg_prop);
fld_map_t efp_rfp_bm_pool_rid_offset {
CREATE_ENTRY("offset", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_bm_pool_rid_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bm_pool_rid_offset),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_bm_pool_rid_offset", efp_rfp_bm_pool_rid_offset_prop);
fld_map_t efp_rfp_num_bm_pools {
CREATE_ENTRY("num_pools", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_num_bm_pools_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_num_bm_pools),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_num_bm_pools", efp_rfp_num_bm_pools_prop);
fld_map_t efp_rfp_nut_wu_occ_offset {
CREATE_ENTRY("offset", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_nut_wu_occ_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_nut_wu_occ_offset),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_nut_wu_occ_offset", efp_rfp_nut_wu_occ_offset_prop);
fld_map_t efp_rfp_all_wu_occ_offset {
CREATE_ENTRY("offset", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_all_wu_occ_offset_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_all_wu_occ_offset),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_all_wu_occ_offset", efp_rfp_all_wu_occ_offset_prop);
fld_map_t efp_rfp_bm_master_id {
CREATE_ENTRY("client_id", 0, 5),
CREATE_ENTRY("__rsvd", 5, 59)
};auto efp_rfp_bm_master_id_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bm_master_id),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_cerr_log_vec", efp_rfp_sram_cerr_log_vec_prop);
fld_map_t efp_rfp_sram_ucerr_log_vec {
CREATE_ENTRY("efp_rfp_rad_mem", 0, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst0", 1, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst1", 2, 1),
CREATE_ENTRY("efp_rfp_hdr_bf_inst2", 3, 1),
CREATE_ENTRY("efp_rfp_mhg_buf0", 4, 1),
CREATE_ENTRY("efp_rfp_mhg_buf1", 5, 1),
CREATE_ENTRY("efp_rfp_l4cs_hdr_buf", 6, 1),
CREATE_ENTRY("efp_rfp_rsrc_buf", 7, 1),
CREATE_ENTRY("efp_rfp_misc_buf", 8, 1),
CREATE_ENTRY("efp_rfp_pre_mhg_buf", 9, 1),
CREATE_ENTRY("efp_rfp_tag_data", 10, 1),
CREATE_ENTRY("efp_rfp_fcpea_seq", 11, 1),
CREATE_ENTRY("__rsvd", 12, 52)
};auto efp_rfp_sram_ucerr_log_vec_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_ucerr_log_vec),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_ucerr_log_vec", efp_rfp_sram_ucerr_log_vec_prop);
fld_map_t efp_rfp_sram_log_syndrome {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_sram_log_syndrome_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_log_syndrome),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_log_syndrome", efp_rfp_sram_log_syndrome_prop);
fld_map_t efp_rfp_sram_log_addr {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_sram_log_addr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_sram_log_addr),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_sram_log_addr", efp_rfp_sram_log_addr_prop);
fld_map_t efp_rfp_snapshot_sym {
CREATE_ENTRY("fld_val", 0, 1),
CREATE_ENTRY("lb_grp_mem_idx", 1, 11),
CREATE_ENTRY("rsvd", 12, 52)
};auto efp_rfp_snapshot_sym_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_snapshot_sym),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_snapshot_sym", efp_rfp_snapshot_sym_prop);
fld_map_t efp_rfp_flow_control_sta {
CREATE_ENTRY("fld_fcb_flow_ctrl", 0, 1),
CREATE_ENTRY("fld_wro_flow_ctrl", 1, 1),
CREATE_ENTRY("fld_wqm_flow_ctrl", 2, 1),
CREATE_ENTRY("fld_prs_flow_ctrl", 3, 1),
CREATE_ENTRY("fld_dn_bm_tag_flow_ctrl", 4, 1),
CREATE_ENTRY("fld_sn_bm_tag_flow_ctrl", 5, 1),
CREATE_ENTRY("fld_rdp0_flow_ctrl", 6, 1),
CREATE_ENTRY("fld_rdp1_flow_ctrl", 7, 1),
CREATE_ENTRY("fld_rdp2_flow_ctrl", 8, 1),
CREATE_ENTRY("__rsvd", 9, 55)
};auto efp_rfp_flow_control_sta_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_flow_control_sta),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_flow_control_sta", efp_rfp_flow_control_sta_prop);
fld_map_t efp_rfp_mhg_eot {
CREATE_ENTRY("val", 0, 32),
CREATE_ENTRY("__rsvd", 32, 32)
};auto efp_rfp_mhg_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_mhg_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_mhg_eot", efp_rfp_mhg_eot_prop);
fld_map_t efp_rfp_lsn_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_lsn_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lsn_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_lsn_eot", efp_rfp_lsn_eot_prop);
fld_map_t efp_rfp_cs_pipe0_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_cs_pipe0_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_cs_pipe0_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_cs_pipe0_eot", efp_rfp_cs_pipe0_eot_prop);
fld_map_t efp_rfp_cs_pipe1_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_cs_pipe1_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_cs_pipe1_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_cs_pipe1_eot", efp_rfp_cs_pipe1_eot_prop);
fld_map_t efp_rfp_misc_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_misc_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_misc_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_misc_eot", efp_rfp_misc_eot_prop);
fld_map_t efp_rfp_prs_wrapper_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_prs_wrapper_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_prs_wrapper_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_prs_wrapper_eot", efp_rfp_prs_wrapper_eot_prop);
fld_map_t efp_rfp_upd_if_eot {
CREATE_ENTRY("val", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_upd_if_eot_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_upd_if_eot),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_upd_if_eot", efp_rfp_upd_if_eot_prop);
fld_map_t efp_rfp_watchdog_timer_period {
CREATE_ENTRY("val", 0, 16),
CREATE_ENTRY("__rsvd", 16, 48)
};auto efp_rfp_watchdog_timer_period_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_watchdog_timer_period),
CSR_TYPE::REG,
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
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_err_drop_mask", efp_rfp_err_drop_mask_prop);
fld_map_t efp_rfp_err_drop_wu_gen {
CREATE_ENTRY("cluster_id", 0, 4),
CREATE_ENTRY("dlid", 4, 5),
CREATE_ENTRY("wu_queue_id", 9, 8),
CREATE_ENTRY("sw_opcode", 17, 24),
CREATE_ENTRY("__rsvd", 41, 23)
};auto efp_rfp_err_drop_wu_gen_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_err_drop_wu_gen),
CSR_TYPE::REG,
add_csr(efp_rfp_lcl_0, "efp_rfp_err_drop_wu_gen", efp_rfp_err_drop_wu_gen_prop);
fld_map_t efp_rfp_clbp_mem {
CREATE_ENTRY("gen_b0_offset", 0, 8),
CREATE_ENTRY("gen_b1_offset", 8, 8),
CREATE_ENTRY("gen_b2_offset", 16, 8),
CREATE_ENTRY("gen_b3_offset", 24, 8),
CREATE_ENTRY("fld_swp_en_2b", 32, 1),
CREATE_ENTRY("fld_0_ctrl_2b", 33, 8),
CREATE_ENTRY("fld_1_ctrl_2b", 41, 8),
CREATE_ENTRY("fld_swp_en_16b", 49, 1),
CREATE_ENTRY("fld_0_offset_16b", 50, 8),
CREATE_ENTRY("fld_1_offset_16b", 58, 8),
CREATE_ENTRY("fld_0_size_16b", 66, 4),
CREATE_ENTRY("fld_1_size_16b", 70, 4),
CREATE_ENTRY("grp_mem_base_addr", 74, 11),
CREATE_ENTRY("group_size", 85, 4),
CREATE_ENTRY("traffic_profile", 89, 2),
CREATE_ENTRY("sw_opcode", 91, 24),
CREATE_ENTRY("__rsvd", 115, 13)
};auto efp_rfp_clbp_mem_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_clbp_mem),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_clbp_mem", efp_rfp_clbp_mem_prop);
fld_map_t efp_rfp_lb_grp_mem {
CREATE_ENTRY("wu_cluster", 0, 4),
CREATE_ENTRY("wu_queue", 4, 8),
CREATE_ENTRY("dlid", 12, 5),
CREATE_ENTRY("__rsvd", 17, 47)
};auto efp_rfp_lb_grp_mem_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_lb_grp_mem),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_lb_grp_mem", efp_rfp_lb_grp_mem_prop);
fld_map_t efp_rfp_rewr_inst {
CREATE_ENTRY("rem_hdr", 0, 1),
CREATE_ENTRY("add_hdr", 1, 2),
CREATE_ENTRY("hdr_num", 3, 3),
CREATE_ENTRY("add2_null_bytes", 6, 1),
CREATE_ENTRY("null_byte_hdr_num", 7, 3),
CREATE_ENTRY("hdr_byte0", 10, 8),
CREATE_ENTRY("gen_byt0_off", 18, 8),
CREATE_ENTRY("gen_byt1_off", 26, 8),
CREATE_ENTRY("gen_byt2_off", 34, 8),
CREATE_ENTRY("gen_byt3_off", 42, 8),
CREATE_ENTRY("gen_byt4_off", 50, 8),
CREATE_ENTRY("gen_byt5_off", 58, 8),
CREATE_ENTRY("gen_byt6_off", 66, 8),
CREATE_ENTRY("gen_byt7_off", 74, 8),
CREATE_ENTRY("gen_byt8_off", 82, 8),
CREATE_ENTRY("gen_byt9_off", 90, 8),
CREATE_ENTRY("fld_swp_en_2b", 98, 1),
CREATE_ENTRY("fld_0_ctrl_2b", 99, 8),
CREATE_ENTRY("fld_1_ctrl_2b", 107, 8),
CREATE_ENTRY("fld_swp_en_16b", 115, 1),
CREATE_ENTRY("fld_0_offset_16b", 116, 8),
CREATE_ENTRY("fld_1_offset_16b", 124, 8),
CREATE_ENTRY("fld_0_size_16b", 132, 4),
CREATE_ENTRY("fld_1_size_16b", 136, 4),
CREATE_ENTRY("__rsvd", 140, 52)
};auto efp_rfp_rewr_inst_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rewr_inst),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_rewr_inst", efp_rfp_rewr_inst_prop);
fld_map_t efp_rfp_bmpool_node_map {
CREATE_ENTRY("fcb_psw_slct", 0, 1),
CREATE_ENTRY("sch_node", 1, 24),
CREATE_ENTRY("xoff_q_vec", 25, 8),
CREATE_ENTRY("__rsvd", 33, 31)
};auto efp_rfp_bmpool_node_map_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_bmpool_node_map),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_bmpool_node_map", efp_rfp_bmpool_node_map_prop);
fld_map_t efp_rfp_l4cs_tcam_key {
CREATE_ENTRY("vld", 0, 1),
CREATE_ENTRY("key", 1, 21),
CREATE_ENTRY("__rsvd", 22, 42)
};auto efp_rfp_l4cs_tcam_key_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_l4cs_tcam_key),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_tcam_key", efp_rfp_l4cs_tcam_key_prop);
fld_map_t efp_rfp_l4cs_tcam_mask {
CREATE_ENTRY("mask", 0, 21),
CREATE_ENTRY("__rsvd", 21, 43)
};auto efp_rfp_l4cs_tcam_mask_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_l4cs_tcam_mask),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_tcam_mask", efp_rfp_l4cs_tcam_mask_prop);
fld_map_t efp_rfp_rad_init {
CREATE_ENTRY("sec_tunnel", 0, 1),
CREATE_ENTRY("allw_non_sec_pkt", 1, 1),
CREATE_ENTRY("init_seq_num", 2, 48),
CREATE_ENTRY("bmpool", 50, 6),
CREATE_ENTRY("__rsvd", 56, 8)
};auto efp_rfp_rad_init_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_rad_init),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_rad_init", efp_rfp_rad_init_prop);
fld_map_t efp_rfp_intf_stats_cntr {
CREATE_ENTRY("fld_count", 0, 36),
CREATE_ENTRY("__rsvd", 36, 28)
};auto efp_rfp_intf_stats_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_intf_stats_cntr),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_intf_stats_cntr", efp_rfp_intf_stats_cntr_prop);
fld_map_t efp_rfp_err_cntr {
CREATE_ENTRY("fld_count", 0, 8),
CREATE_ENTRY("__rsvd", 8, 56)
};auto efp_rfp_err_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_err_cntr),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_err_cntr", efp_rfp_err_cntr_prop);
fld_map_t efp_rfp_pkt_type_cntr {
CREATE_ENTRY("fld_count", 0, 36),
CREATE_ENTRY("__rsvd", 36, 28)
};auto efp_rfp_pkt_type_cntr_prop = csr_prop_t(
std::make_shared<csr_s>(efp_rfp_pkt_type_cntr),
CSR_TYPE::TBL,
add_csr(efp_rfp_lcl_0, "efp_rfp_pkt_type_cntr", efp_rfp_pkt_type_cntr_prop);
 // END efp_rfp_lcl 
}
sys_rings["NU"] = nu_rng;
