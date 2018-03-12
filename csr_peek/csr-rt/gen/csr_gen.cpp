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
    ring_coll_t hnu_rng;
    hnu_rng.add_ring(0, 0x8000000000);
    hnu_rng.add_ring(1, 0x8800000000);
    sys_rings["HNU"] = hnu_rng;
    ring_coll_t nu_rng;
    nu_rng.add_ring(0, 0x5000000000);
    {
// BEGIN fpg_prs
        auto fpg_prs_0 = nu_rng[0].add_an({"fpg","fpg_prs"}, 0x0, 1, 0x0);
        fld_map_t fpg_prs_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_prs_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_prs_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_prs_0, "fpg_prs_timeout_thresh_cfg", fpg_prs_timeout_thresh_cfg_prop);
        fld_map_t fpg_prs_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_prs_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_prs_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_prs_0, "fpg_prs_timeout_clr", fpg_prs_timeout_clr_prop);
        fld_map_t fpg_prs_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_prs_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_prs_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fpg_prs_0, "fpg_prs_spare_pio", fpg_prs_spare_pio_prop);
        fld_map_t fpg_prs_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_prs_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_prs_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_prs_0, "fpg_prs_scratchpad", fpg_prs_scratchpad_prop);
        fld_map_t prs_mem_err_inj_cfg {
            CREATE_ENTRY("prs_rob_prv_mem", 0, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem0", 1, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem1", 2, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem2", 3, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem3", 4, 1),
            CREATE_ENTRY("err_type", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto prs_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_mem_err_inj_cfg),
                                            0x98,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_prs_0, "prs_mem_err_inj_cfg", prs_mem_err_inj_cfg_prop);
        fld_map_t prs_dsp_dfifo_mem_af_thold {
            CREATE_ENTRY("data", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
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
        };
        auto prs_intf_cfg_prop = csr_prop_t(
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
        };
        auto prs_err_chk_en_prop = csr_prop_t(
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
        };
        auto prs_err_tcode0_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode0),
                                       0xB8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fpg_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
        fld_map_t prs_err_tcode1 {
            CREATE_ENTRY("gp_byte_oor", 0, 7),
            CREATE_ENTRY("action_mem_perr", 7, 7),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto prs_err_tcode1_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode1),
                                       0xC0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fpg_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
        fld_map_t prs_max_lu_cycle_cfg {
            CREATE_ENTRY("use_fixed", 0, 1),
            CREATE_ENTRY("fixed_cnt", 1, 8),
            CREATE_ENTRY("init_cycle_cnt", 9, 6),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
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
        };
        auto prs_stream_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_stream_cfg),
                                       0xD0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fpg_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
        fld_map_t prs_static_ctx_sel {
            CREATE_ENTRY("use_one_ctx", 0, 1),
            CREATE_ENTRY("ctx_num", 1, 2),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto prs_static_ctx_sel_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_static_ctx_sel),
                                           0xD8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
        fld_map_t prs_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
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
        };
        auto prs_tcam_prop = csr_prop_t(
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
        };
        auto prs_seq_mem_prop = csr_prop_t(
                                    std::make_shared<csr_s>(prs_seq_mem),
                                    0x11000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(fpg_prs_0, "prs_seq_mem", prs_seq_mem_prop);
        fld_map_t prs_rob_prv_mem_dhs {
            CREATE_ENTRY("data", 0, 288),
            CREATE_ENTRY("__rsvd", 288, 32)
        };
        auto prs_rob_prv_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_rob_prv_mem_dhs),
                                            0x15000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(fpg_prs_0, "prs_rob_prv_mem_dhs", prs_rob_prv_mem_dhs_prop);
        fld_map_t prs_action_mem_dhs {
            CREATE_ENTRY("data", 0, 112),
            CREATE_ENTRY("__rsvd", 112, 16)
        };
        auto prs_action_mem_dhs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_action_mem_dhs),
                                           0x40000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fpg_prs_0, "prs_action_mem_dhs", prs_action_mem_dhs_prop);
        fld_map_t prs_dsp_dfifo_mem_dhs {
            CREATE_ENTRY("data", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto prs_dsp_dfifo_mem_dhs_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_dsp_dfifo_mem_dhs),
                                              0x140000,
                                              CSR_TYPE::TBL,
                                              2);
        add_csr(fpg_prs_0, "prs_dsp_dfifo_mem_dhs", prs_dsp_dfifo_mem_dhs_prop);
        fld_map_t prs_initial_state {
            CREATE_ENTRY("parser_state", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_initial_state_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_initial_state),
                                          0x540000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_prs_0, "prs_initial_state", prs_initial_state_prop);
        fld_map_t prs_dsp_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_dsp_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_dsp_dbg_probe),
                                          0x541000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_prs_0, "prs_dsp_dbg_probe", prs_dsp_dbg_probe_prop);
        fld_map_t prs_ctx_rob_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_ctx_rob_dbg_probe_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_ctx_rob_dbg_probe),
                                              0x541200,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(fpg_prs_0, "prs_ctx_rob_dbg_probe", prs_ctx_rob_dbg_probe_prop);
        fld_map_t prs_prv_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_prv_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_prv_dbg_probe),
                                          0x541400,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_prs_0, "prs_prv_dbg_probe", prs_prv_dbg_probe_prop);
// END fpg_prs
    }
    {
// BEGIN prw
        auto prw_0 = nu_rng[0].add_an({"fpg","prw"}, 0x800000, 1, 0x0);
        fld_map_t prw_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto prw_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(prw_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(prw_0, "prw_timeout_thresh_cfg", prw_timeout_thresh_cfg_prop);
        fld_map_t prw_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto prw_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(prw_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(prw_0, "prw_timeout_clr", prw_timeout_clr_prop);
        fld_map_t prw_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto prw_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(prw_spare_pio),
                                      0x70,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(prw_0, "prw_spare_pio", prw_spare_pio_prop);
        fld_map_t prw_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto prw_scratchpad_prop = csr_prop_t(
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
        };
        auto prw_holdoff_thr_prop = csr_prop_t(
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
        };
        auto prw_holdoff_timer_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prw_holdoff_timer),
                                          0x88,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(prw_0, "prw_holdoff_timer", prw_holdoff_timer_prop);
        fld_map_t prw_lfa_ethertype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto prw_lfa_ethertype_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prw_lfa_ethertype),
                                          0x90,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(prw_0, "prw_lfa_ethertype", prw_lfa_ethertype_prop);
        fld_map_t prw_vlan_ethertype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto prw_vlan_ethertype_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prw_vlan_ethertype),
                                           0x98,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(prw_0, "prw_vlan_ethertype", prw_vlan_ethertype_prop);
        fld_map_t prw_ignore_psw_spd_flag {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto prw_ignore_psw_spd_flag_prop = csr_prop_t(
                                                std::make_shared<csr_s>(prw_ignore_psw_spd_flag),
                                                0xA0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(prw_0, "prw_ignore_psw_spd_flag", prw_ignore_psw_spd_flag_prop);
        fld_map_t prw_mem_err_inj_cfg {
            CREATE_ENTRY("prw_rdm_even_mem", 0, 1),
            CREATE_ENTRY("prw_rdm_odd_mem", 1, 1),
            CREATE_ENTRY("prw_hcb_mem", 2, 1),
            CREATE_ENTRY("prw_bcb_mem", 3, 1),
            CREATE_ENTRY("prw_nhcb_mem", 4, 1),
            CREATE_ENTRY("err_type", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto prw_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prw_mem_err_inj_cfg),
                                            0xA8,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(prw_0, "prw_mem_err_inj_cfg", prw_mem_err_inj_cfg_prop);
        fld_map_t prw_pkt_capture_control {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("en_capture_with_snapshot_flag", 1, 1),
            CREATE_ENTRY("en_capture_for_ttl_error", 2, 1),
            CREATE_ENTRY("capture_modified_hd", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto prw_pkt_capture_control_prop = csr_prop_t(
                                                std::make_shared<csr_s>(prw_pkt_capture_control),
                                                0xB0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(prw_0, "prw_pkt_capture_control", prw_pkt_capture_control_prop);
        fld_map_t prw_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prw_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(prw_fla_ring_module_id_cfg),
                0xB8,
                CSR_TYPE::REG,
                1);
        add_csr(prw_0, "prw_fla_ring_module_id_cfg", prw_fla_ring_module_id_cfg_prop);
        fld_map_t prw_rdm {
            CREATE_ENTRY("data", 0, 64)
        };
        auto prw_rdm_prop = csr_prop_t(
                                std::make_shared<csr_s>(prw_rdm),
                                0x1000,
                                CSR_TYPE::TBL,
                                1);
        add_csr(prw_0, "prw_rdm", prw_rdm_prop);
// END prw
    }
    {
// BEGIN prw
        auto prw_1 = nu_rng[0].add_an({"epg_rdp","prw"}, 0x14020000, 1, 0x0);
        fld_map_t prw_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto prw_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(prw_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(prw_1, "prw_timeout_thresh_cfg", prw_timeout_thresh_cfg_prop);
        fld_map_t prw_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto prw_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(prw_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(prw_1, "prw_timeout_clr", prw_timeout_clr_prop);
        fld_map_t prw_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto prw_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(prw_spare_pio),
                                      0x70,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(prw_1, "prw_spare_pio", prw_spare_pio_prop);
        fld_map_t prw_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto prw_scratchpad_prop = csr_prop_t(
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
        };
        auto prw_holdoff_thr_prop = csr_prop_t(
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
        };
        auto prw_holdoff_timer_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prw_holdoff_timer),
                                          0x88,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(prw_1, "prw_holdoff_timer", prw_holdoff_timer_prop);
        fld_map_t prw_lfa_ethertype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto prw_lfa_ethertype_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prw_lfa_ethertype),
                                          0x90,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(prw_1, "prw_lfa_ethertype", prw_lfa_ethertype_prop);
        fld_map_t prw_vlan_ethertype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto prw_vlan_ethertype_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prw_vlan_ethertype),
                                           0x98,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(prw_1, "prw_vlan_ethertype", prw_vlan_ethertype_prop);
        fld_map_t prw_ignore_psw_spd_flag {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto prw_ignore_psw_spd_flag_prop = csr_prop_t(
                                                std::make_shared<csr_s>(prw_ignore_psw_spd_flag),
                                                0xA0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(prw_1, "prw_ignore_psw_spd_flag", prw_ignore_psw_spd_flag_prop);
        fld_map_t prw_mem_err_inj_cfg {
            CREATE_ENTRY("prw_rdm_even_mem", 0, 1),
            CREATE_ENTRY("prw_rdm_odd_mem", 1, 1),
            CREATE_ENTRY("prw_hcb_mem", 2, 1),
            CREATE_ENTRY("prw_bcb_mem", 3, 1),
            CREATE_ENTRY("prw_nhcb_mem", 4, 1),
            CREATE_ENTRY("err_type", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto prw_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prw_mem_err_inj_cfg),
                                            0xA8,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(prw_1, "prw_mem_err_inj_cfg", prw_mem_err_inj_cfg_prop);
        fld_map_t prw_pkt_capture_control {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("en_capture_with_snapshot_flag", 1, 1),
            CREATE_ENTRY("en_capture_for_ttl_error", 2, 1),
            CREATE_ENTRY("capture_modified_hd", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto prw_pkt_capture_control_prop = csr_prop_t(
                                                std::make_shared<csr_s>(prw_pkt_capture_control),
                                                0xB0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(prw_1, "prw_pkt_capture_control", prw_pkt_capture_control_prop);
        fld_map_t prw_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prw_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(prw_fla_ring_module_id_cfg),
                0xB8,
                CSR_TYPE::REG,
                1);
        add_csr(prw_1, "prw_fla_ring_module_id_cfg", prw_fla_ring_module_id_cfg_prop);
        fld_map_t prw_rdm {
            CREATE_ENTRY("data", 0, 64)
        };
        auto prw_rdm_prop = csr_prop_t(
                                std::make_shared<csr_s>(prw_rdm),
                                0x1000,
                                CSR_TYPE::TBL,
                                1);
        add_csr(prw_1, "prw_rdm", prw_rdm_prop);
// END prw
    }
    {
// BEGIN fpg_misc
        auto fpg_misc_0 = nu_rng[0].add_an({"fpg","fpg_misc"}, 0x810000, 1, 0x0);
        fld_map_t fpg_misc_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_misc_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_0, "fpg_misc_timeout_thresh_cfg", fpg_misc_timeout_thresh_cfg_prop);
        fld_map_t fpg_misc_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_timeout_clr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_misc_timeout_clr),
                                             0x10,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fpg_misc_0, "fpg_misc_timeout_clr", fpg_misc_timeout_clr_prop);
        fld_map_t fpg_misc_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_misc_spare_pio_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_misc_spare_pio),
                                           0x70,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_misc_0, "fpg_misc_spare_pio", fpg_misc_spare_pio_prop);
        fld_map_t fpg_misc_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_misc_scratchpad_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_misc_scratchpad),
                                            0x78,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_misc_0, "fpg_misc_scratchpad", fpg_misc_scratchpad_prop);
        fld_map_t fpg_misc_stream_speed {
            CREATE_ENTRY("stream_speed", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_misc_stream_speed_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_misc_stream_speed),
                                              0x80,
                                              CSR_TYPE::REG_LST,
                                              4);
        add_csr(fpg_misc_0, "fpg_misc_stream_speed", fpg_misc_stream_speed_prop);
        fld_map_t fpg_misc_get_flit_tdm_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_get_flit_tdm_en_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_get_flit_tdm_en),
                0xA0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_0, "fpg_misc_get_flit_tdm_en", fpg_misc_get_flit_tdm_en_prop);
        fld_map_t fpg_misc_get_flit_tdm_clnd {
            CREATE_ENTRY("stream_num", 0, 2),
            CREATE_ENTRY("vld", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto fpg_misc_get_flit_tdm_clnd_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_get_flit_tdm_clnd),
                0xA8,
                CSR_TYPE::REG_LST,
                4);
        add_csr(fpg_misc_0, "fpg_misc_get_flit_tdm_clnd", fpg_misc_get_flit_tdm_clnd_prop);
        fld_map_t fpg_misc_tx_max_pkt_len {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fpg_misc_tx_max_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_tx_max_pkt_len),
                                                0xC8,
                                                CSR_TYPE::REG_LST,
                                                4);
        add_csr(fpg_misc_0, "fpg_misc_tx_max_pkt_len", fpg_misc_tx_max_pkt_len_prop);
        fld_map_t fpg_misc_tx_min_pkt_len {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_misc_tx_min_pkt_len_prop = csr_prop_t(
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
        };
        auto fpg_misc_tx_ptp_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_misc_tx_ptp_cfg),
                                            0xF0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_misc_0, "fpg_misc_tx_ptp_cfg", fpg_misc_tx_ptp_cfg_prop);
        fld_map_t fpg_misc_mac0_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac0_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac0_peer_delay_cfg),
                    0xF8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_mac0_peer_delay_cfg", fpg_misc_mac0_peer_delay_cfg_prop);
        fld_map_t fpg_misc_mac1_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac1_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac1_peer_delay_cfg),
                    0x100,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_mac1_peer_delay_cfg", fpg_misc_mac1_peer_delay_cfg_prop);
        fld_map_t fpg_misc_mac2_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac2_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac2_peer_delay_cfg),
                    0x108,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_mac2_peer_delay_cfg", fpg_misc_mac2_peer_delay_cfg_prop);
        fld_map_t fpg_misc_mac3_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac3_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac3_peer_delay_cfg),
                    0x110,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_mac3_peer_delay_cfg", fpg_misc_mac3_peer_delay_cfg_prop);
        fld_map_t fpg_misc_tx_pfc_ctrl {
            CREATE_ENTRY("sw_override_en", 0, 16),
            CREATE_ENTRY("sw_override_val", 16, 16),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_misc_tx_pfc_ctrl_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_misc_tx_pfc_ctrl),
                                             0x118,
                                             CSR_TYPE::REG_LST,
                                             4);
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
        };
        auto fpg_misc_tx_failure_bcast_ctrl_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_failure_bcast_ctrl),
                    0x138,
                    CSR_TYPE::REG_LST,
                    4);
        add_csr(fpg_misc_0, "fpg_misc_tx_failure_bcast_ctrl", fpg_misc_tx_failure_bcast_ctrl_prop);
        fld_map_t fpg_misc_tx_fsf_frame_data {
            CREATE_ENTRY("gph_index", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_misc_tx_fsf_frame_data_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_data),
                0x158,
                CSR_TYPE::REG_LST,
                24);
        add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_data", fpg_misc_tx_fsf_frame_data_prop);
        fld_map_t fpg_misc_tx_fsf_xmit_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_tx_fsf_xmit_en_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_tx_fsf_xmit_en),
                                                0x218,
                                                CSR_TYPE::REG_LST,
                                                4);
        add_csr(fpg_misc_0, "fpg_misc_tx_fsf_xmit_en", fpg_misc_tx_fsf_xmit_en_prop);
        fld_map_t fpg_misc_tx_fsf_strm_is_glb_link {
            CREATE_ENTRY("val", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto fpg_misc_tx_fsf_strm_is_glb_link_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fsf_strm_is_glb_link),
                    0x238,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_tx_fsf_strm_is_glb_link", fpg_misc_tx_fsf_strm_is_glb_link_prop);
        fld_map_t fpg_misc_tx_fsf_frame_opcode {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_misc_tx_fsf_frame_opcode_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_opcode),
                    0x240,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_opcode", fpg_misc_tx_fsf_frame_opcode_prop);
        fld_map_t fpg_misc_tx_fsf_frame_dmac {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto fpg_misc_tx_fsf_frame_dmac_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_dmac),
                0x248,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_dmac", fpg_misc_tx_fsf_frame_dmac_prop);
        fld_map_t fpg_misc_tx_fsf_frame_ethertype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_misc_tx_fsf_frame_ethertype_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_ethertype),
                    0x250,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_tx_fsf_frame_ethertype", fpg_misc_tx_fsf_frame_ethertype_prop);
        fld_map_t fpg_misc_tx_fpg_stream_state {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_tx_fpg_stream_state_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fpg_stream_state),
                    0x258,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(fpg_misc_0, "fpg_misc_tx_fpg_stream_state", fpg_misc_tx_fpg_stream_state_prop);
        fld_map_t fpg_misc_psw_tdm_clnd {
            CREATE_ENTRY("stream_num", 0, 2),
            CREATE_ENTRY("vld", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto fpg_misc_psw_tdm_clnd_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_misc_psw_tdm_clnd),
                                              0x318,
                                              CSR_TYPE::REG_LST,
                                              4);
        add_csr(fpg_misc_0, "fpg_misc_psw_tdm_clnd", fpg_misc_psw_tdm_clnd_prop);
        fld_map_t fpg_misc_stream_rate_limit {
            CREATE_ENTRY("credits_per_interval", 0, 13),
            CREATE_ENTRY("interval", 13, 3),
            CREATE_ENTRY("eop_charge", 16, 6),
            CREATE_ENTRY("__rsvd", 22, 42)
        };
        auto fpg_misc_stream_rate_limit_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_stream_rate_limit),
                0x338,
                CSR_TYPE::REG_LST,
                4);
        add_csr(fpg_misc_0, "fpg_misc_stream_rate_limit", fpg_misc_stream_rate_limit_prop);
        fld_map_t fpg_misc_rx_max_pkt_len {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("val", 1, 14),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fpg_misc_rx_max_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_rx_max_pkt_len),
                                                0x358,
                                                CSR_TYPE::REG_LST,
                                                4);
        add_csr(fpg_misc_0, "fpg_misc_rx_max_pkt_len", fpg_misc_rx_max_pkt_len_prop);
        fld_map_t fpg_misc_rx_min_pkt_len {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fpg_misc_rx_min_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_rx_min_pkt_len),
                                                0x378,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_misc_0, "fpg_misc_rx_min_pkt_len", fpg_misc_rx_min_pkt_len_prop);
        fld_map_t fpg_misc_rx_runt_err_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_rx_runt_err_en_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_rx_runt_err_en),
                                                0x380,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_misc_0, "fpg_misc_rx_runt_err_en", fpg_misc_rx_runt_err_en_prop);
        fld_map_t fpg_misc_rx_pfc_ctrl {
            CREATE_ENTRY("sw_override_en", 0, 16),
            CREATE_ENTRY("sw_override_val", 16, 16),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_misc_rx_pfc_ctrl_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_misc_rx_pfc_ctrl),
                                             0x388,
                                             CSR_TYPE::REG_LST,
                                             4);
        add_csr(fpg_misc_0, "fpg_misc_rx_pfc_ctrl", fpg_misc_rx_pfc_ctrl_prop);
        fld_map_t fpg_misc_rx_eop_timeout_cfg {
            CREATE_ENTRY("en", 0, 4),
            CREATE_ENTRY("timeout_val", 4, 16),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto fpg_misc_rx_eop_timeout_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_rx_eop_timeout_cfg),
                0x3A8,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_0, "fpg_misc_rx_eop_timeout_cfg", fpg_misc_rx_eop_timeout_cfg_prop);
        fld_map_t fpg_misc_tx_sch_cfg {
            CREATE_ENTRY("gr_wt_eth", 0, 12),
            CREATE_ENTRY("gr_wt_flink", 12, 12),
            CREATE_ENTRY("gr_per", 24, 4),
            CREATE_ENTRY("dwrr_wt_eth", 28, 4),
            CREATE_ENTRY("dwrr_wt_flink", 32, 4),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fpg_misc_tx_sch_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_misc_tx_sch_cfg),
                                            0x3B0,
                                            CSR_TYPE::REG_LST,
                                            4);
        add_csr(fpg_misc_0, "fpg_misc_tx_sch_cfg", fpg_misc_tx_sch_cfg_prop);
        fld_map_t fpg_misc_rx_flink_etype_cfg {
            CREATE_ENTRY("etype_bypass_en", 0, 1),
            CREATE_ENTRY("val", 1, 16),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto fpg_misc_rx_flink_etype_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_rx_flink_etype_cfg),
                0x3D0,
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
        };
        auto fpg_misc_mem_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_mem_err_inj_cfg),
                0x3D8,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_0, "fpg_misc_mem_err_inj_cfg", fpg_misc_mem_err_inj_cfg_prop);
        fld_map_t fpg_misc_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_misc_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_fla_ring_module_id_cfg),
                    0x3E0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_0, "fpg_misc_fla_ring_module_id_cfg", fpg_misc_fla_ring_module_id_cfg_prop);
// END fpg_misc
    }
    {
// BEGIN fpg_misc
        auto fpg_misc_1 = nu_rng[0].add_an({"nu_mpg","fpg_misc"}, 0x15400000, 1, 0x0);
        fld_map_t fpg_misc_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_misc_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_1, "fpg_misc_timeout_thresh_cfg", fpg_misc_timeout_thresh_cfg_prop);
        fld_map_t fpg_misc_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_timeout_clr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_misc_timeout_clr),
                                             0x10,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fpg_misc_1, "fpg_misc_timeout_clr", fpg_misc_timeout_clr_prop);
        fld_map_t fpg_misc_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_misc_spare_pio_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_misc_spare_pio),
                                           0x70,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_misc_1, "fpg_misc_spare_pio", fpg_misc_spare_pio_prop);
        fld_map_t fpg_misc_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_misc_scratchpad_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_misc_scratchpad),
                                            0x78,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_misc_1, "fpg_misc_scratchpad", fpg_misc_scratchpad_prop);
        fld_map_t fpg_misc_stream_speed {
            CREATE_ENTRY("stream_speed", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_misc_stream_speed_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_misc_stream_speed),
                                              0x80,
                                              CSR_TYPE::REG_LST,
                                              4);
        add_csr(fpg_misc_1, "fpg_misc_stream_speed", fpg_misc_stream_speed_prop);
        fld_map_t fpg_misc_get_flit_tdm_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_get_flit_tdm_en_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_get_flit_tdm_en),
                0xA0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_1, "fpg_misc_get_flit_tdm_en", fpg_misc_get_flit_tdm_en_prop);
        fld_map_t fpg_misc_get_flit_tdm_clnd {
            CREATE_ENTRY("stream_num", 0, 2),
            CREATE_ENTRY("vld", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto fpg_misc_get_flit_tdm_clnd_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_get_flit_tdm_clnd),
                0xA8,
                CSR_TYPE::REG_LST,
                4);
        add_csr(fpg_misc_1, "fpg_misc_get_flit_tdm_clnd", fpg_misc_get_flit_tdm_clnd_prop);
        fld_map_t fpg_misc_tx_max_pkt_len {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fpg_misc_tx_max_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_tx_max_pkt_len),
                                                0xC8,
                                                CSR_TYPE::REG_LST,
                                                4);
        add_csr(fpg_misc_1, "fpg_misc_tx_max_pkt_len", fpg_misc_tx_max_pkt_len_prop);
        fld_map_t fpg_misc_tx_min_pkt_len {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_misc_tx_min_pkt_len_prop = csr_prop_t(
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
        };
        auto fpg_misc_tx_ptp_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_misc_tx_ptp_cfg),
                                            0xF0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_misc_1, "fpg_misc_tx_ptp_cfg", fpg_misc_tx_ptp_cfg_prop);
        fld_map_t fpg_misc_mac0_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac0_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac0_peer_delay_cfg),
                    0xF8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_mac0_peer_delay_cfg", fpg_misc_mac0_peer_delay_cfg_prop);
        fld_map_t fpg_misc_mac1_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac1_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac1_peer_delay_cfg),
                    0x100,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_mac1_peer_delay_cfg", fpg_misc_mac1_peer_delay_cfg_prop);
        fld_map_t fpg_misc_mac2_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac2_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac2_peer_delay_cfg),
                    0x108,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_mac2_peer_delay_cfg", fpg_misc_mac2_peer_delay_cfg_prop);
        fld_map_t fpg_misc_mac3_peer_delay_cfg {
            CREATE_ENTRY("val", 0, 30),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto fpg_misc_mac3_peer_delay_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_mac3_peer_delay_cfg),
                    0x110,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_mac3_peer_delay_cfg", fpg_misc_mac3_peer_delay_cfg_prop);
        fld_map_t fpg_misc_tx_pfc_ctrl {
            CREATE_ENTRY("sw_override_en", 0, 16),
            CREATE_ENTRY("sw_override_val", 16, 16),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_misc_tx_pfc_ctrl_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_misc_tx_pfc_ctrl),
                                             0x118,
                                             CSR_TYPE::REG_LST,
                                             4);
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
        };
        auto fpg_misc_tx_failure_bcast_ctrl_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_failure_bcast_ctrl),
                    0x138,
                    CSR_TYPE::REG_LST,
                    4);
        add_csr(fpg_misc_1, "fpg_misc_tx_failure_bcast_ctrl", fpg_misc_tx_failure_bcast_ctrl_prop);
        fld_map_t fpg_misc_tx_fsf_frame_data {
            CREATE_ENTRY("gph_index", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_misc_tx_fsf_frame_data_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_data),
                0x158,
                CSR_TYPE::REG_LST,
                24);
        add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_data", fpg_misc_tx_fsf_frame_data_prop);
        fld_map_t fpg_misc_tx_fsf_xmit_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_tx_fsf_xmit_en_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_tx_fsf_xmit_en),
                                                0x218,
                                                CSR_TYPE::REG_LST,
                                                4);
        add_csr(fpg_misc_1, "fpg_misc_tx_fsf_xmit_en", fpg_misc_tx_fsf_xmit_en_prop);
        fld_map_t fpg_misc_tx_fsf_strm_is_glb_link {
            CREATE_ENTRY("val", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto fpg_misc_tx_fsf_strm_is_glb_link_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fsf_strm_is_glb_link),
                    0x238,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_tx_fsf_strm_is_glb_link", fpg_misc_tx_fsf_strm_is_glb_link_prop);
        fld_map_t fpg_misc_tx_fsf_frame_opcode {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_misc_tx_fsf_frame_opcode_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_opcode),
                    0x240,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_opcode", fpg_misc_tx_fsf_frame_opcode_prop);
        fld_map_t fpg_misc_tx_fsf_frame_dmac {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto fpg_misc_tx_fsf_frame_dmac_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_dmac),
                0x248,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_dmac", fpg_misc_tx_fsf_frame_dmac_prop);
        fld_map_t fpg_misc_tx_fsf_frame_ethertype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_misc_tx_fsf_frame_ethertype_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fsf_frame_ethertype),
                    0x250,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_tx_fsf_frame_ethertype", fpg_misc_tx_fsf_frame_ethertype_prop);
        fld_map_t fpg_misc_tx_fpg_stream_state {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_tx_fpg_stream_state_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_tx_fpg_stream_state),
                    0x258,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(fpg_misc_1, "fpg_misc_tx_fpg_stream_state", fpg_misc_tx_fpg_stream_state_prop);
        fld_map_t fpg_misc_psw_tdm_clnd {
            CREATE_ENTRY("stream_num", 0, 2),
            CREATE_ENTRY("vld", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto fpg_misc_psw_tdm_clnd_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_misc_psw_tdm_clnd),
                                              0x318,
                                              CSR_TYPE::REG_LST,
                                              4);
        add_csr(fpg_misc_1, "fpg_misc_psw_tdm_clnd", fpg_misc_psw_tdm_clnd_prop);
        fld_map_t fpg_misc_stream_rate_limit {
            CREATE_ENTRY("credits_per_interval", 0, 13),
            CREATE_ENTRY("interval", 13, 3),
            CREATE_ENTRY("eop_charge", 16, 6),
            CREATE_ENTRY("__rsvd", 22, 42)
        };
        auto fpg_misc_stream_rate_limit_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_stream_rate_limit),
                0x338,
                CSR_TYPE::REG_LST,
                4);
        add_csr(fpg_misc_1, "fpg_misc_stream_rate_limit", fpg_misc_stream_rate_limit_prop);
        fld_map_t fpg_misc_rx_max_pkt_len {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("val", 1, 14),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fpg_misc_rx_max_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_rx_max_pkt_len),
                                                0x358,
                                                CSR_TYPE::REG_LST,
                                                4);
        add_csr(fpg_misc_1, "fpg_misc_rx_max_pkt_len", fpg_misc_rx_max_pkt_len_prop);
        fld_map_t fpg_misc_rx_min_pkt_len {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fpg_misc_rx_min_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_rx_min_pkt_len),
                                                0x378,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_misc_1, "fpg_misc_rx_min_pkt_len", fpg_misc_rx_min_pkt_len_prop);
        fld_map_t fpg_misc_rx_runt_err_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_misc_rx_runt_err_en_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_misc_rx_runt_err_en),
                                                0x380,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_misc_1, "fpg_misc_rx_runt_err_en", fpg_misc_rx_runt_err_en_prop);
        fld_map_t fpg_misc_rx_pfc_ctrl {
            CREATE_ENTRY("sw_override_en", 0, 16),
            CREATE_ENTRY("sw_override_val", 16, 16),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_misc_rx_pfc_ctrl_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_misc_rx_pfc_ctrl),
                                             0x388,
                                             CSR_TYPE::REG_LST,
                                             4);
        add_csr(fpg_misc_1, "fpg_misc_rx_pfc_ctrl", fpg_misc_rx_pfc_ctrl_prop);
        fld_map_t fpg_misc_rx_eop_timeout_cfg {
            CREATE_ENTRY("en", 0, 4),
            CREATE_ENTRY("timeout_val", 4, 16),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto fpg_misc_rx_eop_timeout_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_rx_eop_timeout_cfg),
                0x3A8,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_1, "fpg_misc_rx_eop_timeout_cfg", fpg_misc_rx_eop_timeout_cfg_prop);
        fld_map_t fpg_misc_tx_sch_cfg {
            CREATE_ENTRY("gr_wt_eth", 0, 12),
            CREATE_ENTRY("gr_wt_flink", 12, 12),
            CREATE_ENTRY("gr_per", 24, 4),
            CREATE_ENTRY("dwrr_wt_eth", 28, 4),
            CREATE_ENTRY("dwrr_wt_flink", 32, 4),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fpg_misc_tx_sch_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_misc_tx_sch_cfg),
                                            0x3B0,
                                            CSR_TYPE::REG_LST,
                                            4);
        add_csr(fpg_misc_1, "fpg_misc_tx_sch_cfg", fpg_misc_tx_sch_cfg_prop);
        fld_map_t fpg_misc_rx_flink_etype_cfg {
            CREATE_ENTRY("etype_bypass_en", 0, 1),
            CREATE_ENTRY("val", 1, 16),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto fpg_misc_rx_flink_etype_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_rx_flink_etype_cfg),
                0x3D0,
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
        };
        auto fpg_misc_mem_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_misc_mem_err_inj_cfg),
                0x3D8,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_misc_1, "fpg_misc_mem_err_inj_cfg", fpg_misc_mem_err_inj_cfg_prop);
        fld_map_t fpg_misc_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_misc_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_misc_fla_ring_module_id_cfg),
                    0x3E0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_misc_1, "fpg_misc_fla_ring_module_id_cfg", fpg_misc_fla_ring_module_id_cfg_prop);
// END fpg_misc
    }
    {
// BEGIN fpg_sdif
        auto fpg_sdif_0 = nu_rng[0].add_an({"fpg","fpg_sdif"}, 0x812000, 1, 0x0);
        fld_map_t fpg_sdif_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_sdif_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_sdif_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_sdif_0, "fpg_sdif_timeout_thresh_cfg", fpg_sdif_timeout_thresh_cfg_prop);
        fld_map_t fpg_sdif_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_sdif_timeout_clr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_sdif_timeout_clr),
                                             0x10,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fpg_sdif_0, "fpg_sdif_timeout_clr", fpg_sdif_timeout_clr_prop);
        fld_map_t fpg_sdif_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_sdif_spare_pio_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_sdif_spare_pio),
                                           0x70,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_sdif_0, "fpg_sdif_spare_pio", fpg_sdif_spare_pio_prop);
        fld_map_t fpg_sdif_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_sdif_scratchpad_prop = csr_prop_t(
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
        };
        auto fpg_sdif_pcs_tx_clk_ena_msel_prop = csr_prop_t(
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
        };
        auto fpg_sdif_sd_en_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fpg_sdif_sd_en),
                                       0x88,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fpg_sdif_0, "fpg_sdif_sd_en", fpg_sdif_sd_en_prop);
        fld_map_t fpg_sdif_fifo_rst {
            CREATE_ENTRY("tx_ln_rst_n", 0, 4),
            CREATE_ENTRY("rx_ln_rst_n", 4, 4),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_sdif_fifo_rst_prop = csr_prop_t(
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
        };
        auto fpg_sdif_tx_fifo_start_txmit_thr_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_sdif_tx_fifo_start_txmit_thr),
                    0x98,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_sdif_0, "fpg_sdif_tx_fifo_start_txmit_thr", fpg_sdif_tx_fifo_start_txmit_thr_prop);
        fld_map_t fpg_sdif_rx_signal_det {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_sdif_rx_signal_det_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fpg_sdif_rx_signal_det),
                                               0xA0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fpg_sdif_0, "fpg_sdif_rx_signal_det", fpg_sdif_rx_signal_det_prop);
        fld_map_t fpg_sdif_rx_use_energy_det_frm_serdes {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_sdif_rx_use_energy_det_frm_serdes_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_sdif_rx_use_energy_det_frm_serdes),
                    0xA8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_sdif_0, "fpg_sdif_rx_use_energy_det_frm_serdes", fpg_sdif_rx_use_energy_det_frm_serdes_prop);
        fld_map_t fpg_sdif_serdes_mode_is_50g {
            CREATE_ENTRY("sd0_is_50g", 0, 1),
            CREATE_ENTRY("sd2_is_50g", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_sdif_serdes_mode_is_50g_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_sdif_serdes_mode_is_50g),
                0xB8,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_sdif_0, "fpg_sdif_serdes_mode_is_50g", fpg_sdif_serdes_mode_is_50g_prop);
        fld_map_t fpg_sdif_spico_intr_cfg {
            CREATE_ENTRY("ln0_vld", 0, 1),
            CREATE_ENTRY("ln0_code", 1, 16),
            CREATE_ENTRY("ln0_data", 17, 16),
            CREATE_ENTRY("ln1_vld", 33, 1),
            CREATE_ENTRY("ln1_code", 34, 16),
            CREATE_ENTRY("ln1_data", 50, 16),
            CREATE_ENTRY("ln2_vld", 66, 1),
            CREATE_ENTRY("ln2_code", 67, 16),
            CREATE_ENTRY("ln2_data", 83, 16),
            CREATE_ENTRY("ln3_vld", 99, 1),
            CREATE_ENTRY("ln3_code", 100, 16),
            CREATE_ENTRY("ln3_data", 116, 16),
            CREATE_ENTRY("__rsvd", 132, 60)
        };
        auto fpg_sdif_spico_intr_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_sdif_spico_intr_cfg),
                                                0xC0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_sdif_0, "fpg_sdif_spico_intr_cfg", fpg_sdif_spico_intr_cfg_prop);
        fld_map_t fpg_sdif_core_to_cntl {
            CREATE_ENTRY("ln0", 0, 16),
            CREATE_ENTRY("ln1", 16, 16),
            CREATE_ENTRY("ln2", 32, 16),
            CREATE_ENTRY("ln3", 48, 16)
        };
        auto fpg_sdif_core_to_cntl_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_sdif_core_to_cntl),
                                              0x100,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fpg_sdif_0, "fpg_sdif_core_to_cntl", fpg_sdif_core_to_cntl_prop);
        fld_map_t fpg_sdif_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_sdif_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_sdif_fla_ring_module_id_cfg),
                    0x108,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_sdif_0, "fpg_sdif_fla_ring_module_id_cfg", fpg_sdif_fla_ring_module_id_cfg_prop);
// END fpg_sdif
    }
    {
// BEGIN fpg_sdif
        auto fpg_sdif_1 = nu_rng[0].add_an({"nu_mpg","fpg_sdif"}, 0x15402000, 1, 0x0);
        fld_map_t fpg_sdif_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_sdif_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_sdif_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_sdif_1, "fpg_sdif_timeout_thresh_cfg", fpg_sdif_timeout_thresh_cfg_prop);
        fld_map_t fpg_sdif_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_sdif_timeout_clr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fpg_sdif_timeout_clr),
                                             0x10,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fpg_sdif_1, "fpg_sdif_timeout_clr", fpg_sdif_timeout_clr_prop);
        fld_map_t fpg_sdif_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_sdif_spare_pio_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_sdif_spare_pio),
                                           0x70,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_sdif_1, "fpg_sdif_spare_pio", fpg_sdif_spare_pio_prop);
        fld_map_t fpg_sdif_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_sdif_scratchpad_prop = csr_prop_t(
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
        };
        auto fpg_sdif_pcs_tx_clk_ena_msel_prop = csr_prop_t(
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
        };
        auto fpg_sdif_sd_en_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fpg_sdif_sd_en),
                                       0x88,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fpg_sdif_1, "fpg_sdif_sd_en", fpg_sdif_sd_en_prop);
        fld_map_t fpg_sdif_fifo_rst {
            CREATE_ENTRY("tx_ln_rst_n", 0, 4),
            CREATE_ENTRY("rx_ln_rst_n", 4, 4),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_sdif_fifo_rst_prop = csr_prop_t(
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
        };
        auto fpg_sdif_tx_fifo_start_txmit_thr_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_sdif_tx_fifo_start_txmit_thr),
                    0x98,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_sdif_1, "fpg_sdif_tx_fifo_start_txmit_thr", fpg_sdif_tx_fifo_start_txmit_thr_prop);
        fld_map_t fpg_sdif_rx_signal_det {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_sdif_rx_signal_det_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fpg_sdif_rx_signal_det),
                                               0xA0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fpg_sdif_1, "fpg_sdif_rx_signal_det", fpg_sdif_rx_signal_det_prop);
        fld_map_t fpg_sdif_rx_use_energy_det_frm_serdes {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_sdif_rx_use_energy_det_frm_serdes_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_sdif_rx_use_energy_det_frm_serdes),
                    0xA8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_sdif_1, "fpg_sdif_rx_use_energy_det_frm_serdes", fpg_sdif_rx_use_energy_det_frm_serdes_prop);
        fld_map_t fpg_sdif_serdes_mode_is_50g {
            CREATE_ENTRY("sd0_is_50g", 0, 1),
            CREATE_ENTRY("sd2_is_50g", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_sdif_serdes_mode_is_50g_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_sdif_serdes_mode_is_50g),
                0xB8,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_sdif_1, "fpg_sdif_serdes_mode_is_50g", fpg_sdif_serdes_mode_is_50g_prop);
        fld_map_t fpg_sdif_spico_intr_cfg {
            CREATE_ENTRY("ln0_vld", 0, 1),
            CREATE_ENTRY("ln0_code", 1, 16),
            CREATE_ENTRY("ln0_data", 17, 16),
            CREATE_ENTRY("ln1_vld", 33, 1),
            CREATE_ENTRY("ln1_code", 34, 16),
            CREATE_ENTRY("ln1_data", 50, 16),
            CREATE_ENTRY("ln2_vld", 66, 1),
            CREATE_ENTRY("ln2_code", 67, 16),
            CREATE_ENTRY("ln2_data", 83, 16),
            CREATE_ENTRY("ln3_vld", 99, 1),
            CREATE_ENTRY("ln3_code", 100, 16),
            CREATE_ENTRY("ln3_data", 116, 16),
            CREATE_ENTRY("__rsvd", 132, 60)
        };
        auto fpg_sdif_spico_intr_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_sdif_spico_intr_cfg),
                                                0xC0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_sdif_1, "fpg_sdif_spico_intr_cfg", fpg_sdif_spico_intr_cfg_prop);
        fld_map_t fpg_sdif_core_to_cntl {
            CREATE_ENTRY("ln0", 0, 16),
            CREATE_ENTRY("ln1", 16, 16),
            CREATE_ENTRY("ln2", 32, 16),
            CREATE_ENTRY("ln3", 48, 16)
        };
        auto fpg_sdif_core_to_cntl_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_sdif_core_to_cntl),
                                              0x100,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fpg_sdif_1, "fpg_sdif_core_to_cntl", fpg_sdif_core_to_cntl_prop);
        fld_map_t fpg_sdif_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_sdif_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_sdif_fla_ring_module_id_cfg),
                    0x108,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_sdif_1, "fpg_sdif_fla_ring_module_id_cfg", fpg_sdif_fla_ring_module_id_cfg_prop);
// END fpg_sdif
    }
    {
// BEGIN fpg_mpw
        auto fpg_mpw_0 = nu_rng[0].add_an({"fpg","fpg_mpw"}, 0x880000, 1, 0x0);
        fld_map_t fpg_mpw_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_mpw_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_mpw_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_mpw_0, "fpg_mpw_timeout_thresh_cfg", fpg_mpw_timeout_thresh_cfg_prop);
        fld_map_t fpg_mpw_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_mpw_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_mpw_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_mpw_0, "fpg_mpw_timeout_clr", fpg_mpw_timeout_clr_prop);
        fld_map_t fpg_mpw_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_mpw_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_spare_pio),
                                          0x98,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fpg_mpw_0, "fpg_mpw_spare_pio", fpg_mpw_spare_pio_prop);
        fld_map_t fpg_mpw_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_mpw_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_mpw_scratchpad),
                                           0xA0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_mpw_0, "fpg_mpw_scratchpad", fpg_mpw_scratchpad_prop);
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
        };
        auto fpg_mpw_mac_tx_fault_cfg_prop = csr_prop_t(
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
        };
        auto fpg_mpw_mac_lpi_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_mpw_mac_lpi_cfg),
                                            0xE0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_mpw_0, "fpg_mpw_mac_lpi_cfg", fpg_mpw_mac_lpi_cfg_prop);
        fld_map_t fpg_mpw_lpi_tick_cnt_incr_val {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fpg_mpw_lpi_tick_cnt_incr_val_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_mpw_lpi_tick_cnt_incr_val),
                    0xE8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_mpw_0, "fpg_mpw_lpi_tick_cnt_incr_val", fpg_mpw_lpi_tick_cnt_incr_val_prop);
        fld_map_t fpg_mpw_sw_reset {
            CREATE_ENTRY("rst_sd_tx_n", 0, 4),
            CREATE_ENTRY("rst_sd_rx_n", 4, 4),
            CREATE_ENTRY("rst_xpcs_n", 8, 1),
            CREATE_ENTRY("rst_spcs_n", 9, 1),
            CREATE_ENTRY("rst_ref_clk_n", 10, 1),
            CREATE_ENTRY("rst_mac_ref_clk_n", 11, 4),
            CREATE_ENTRY("rst_reg_clk_n", 15, 1),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_sw_reset_prop = csr_prop_t(
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
        };
        auto fpg_mpw_pcs_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fpg_mpw_pcs_cfg),
                                        0x100,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fpg_mpw_0, "fpg_mpw_pcs_cfg", fpg_mpw_pcs_cfg_prop);
        fld_map_t fpg_mpw_tx_rx_loopback_cfg {
            CREATE_ENTRY("en", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_mpw_tx_rx_loopback_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_mpw_tx_rx_loopback_cfg),
                0x110,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_mpw_0, "fpg_mpw_tx_rx_loopback_cfg", fpg_mpw_tx_rx_loopback_cfg_prop);
        fld_map_t fpg_mpw_wct_macro_cfg {
            CREATE_ENTRY("decimal_rollover_en", 0, 1),
            CREATE_ENTRY("base_incr", 1, 26),
            CREATE_ENTRY("base_corr_incr", 27, 26),
            CREATE_ENTRY("override_incr", 53, 26),
            CREATE_ENTRY("base_period", 79, 16),
            CREATE_ENTRY("override_cnt", 95, 16),
            CREATE_ENTRY("override_mode", 111, 1),
            CREATE_ENTRY("sync_pulse_dly_sel", 112, 4),
            CREATE_ENTRY("__rsvd", 116, 12)
        };
        auto fpg_mpw_wct_macro_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_mpw_wct_macro_cfg),
                                              0x118,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fpg_mpw_0, "fpg_mpw_wct_macro_cfg", fpg_mpw_wct_macro_cfg_prop);
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
        };
        auto fpg_mpw_mem_err_inj_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_mpw_mem_err_inj_cfg),
                                                0x128,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_mpw_0, "fpg_mpw_mem_err_inj_cfg", fpg_mpw_mem_err_inj_cfg_prop);
        fld_map_t fpg_mpw_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_mpw_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_mpw_fla_ring_module_id_cfg),
                    0x140,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_mpw_0, "fpg_mpw_fla_ring_module_id_cfg", fpg_mpw_fla_ring_module_id_cfg_prop);
        fld_map_t fpg_mpw_mac0_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac0_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac0_reg),
                                         0x800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_0, "fpg_mpw_mac0_reg", fpg_mpw_mac0_reg_prop);
        fld_map_t fpg_mpw_mac1_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac1_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac1_reg),
                                         0x4800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_0, "fpg_mpw_mac1_reg", fpg_mpw_mac1_reg_prop);
        fld_map_t fpg_mpw_mac2_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac2_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac2_reg),
                                         0x8800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_0, "fpg_mpw_mac2_reg", fpg_mpw_mac2_reg_prop);
        fld_map_t fpg_mpw_mac3_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac3_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac3_reg),
                                         0xC800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_0, "fpg_mpw_mac3_reg", fpg_mpw_mac3_reg_prop);
        fld_map_t fpg_mpw_cpcs00_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_cpcs00_reg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_mpw_cpcs00_reg),
                                           0x12000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fpg_mpw_0, "fpg_mpw_cpcs00_reg", fpg_mpw_cpcs00_reg_prop);
        fld_map_t fpg_mpw_gpcs0_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_gpcs0_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_gpcs0_reg),
                                          0x22000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_0, "fpg_mpw_gpcs0_reg", fpg_mpw_gpcs0_reg_prop);
        fld_map_t fpg_mpw_xpcs0_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs0_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs0_reg),
                                          0x24000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_0, "fpg_mpw_xpcs0_reg", fpg_mpw_xpcs0_reg_prop);
        fld_map_t fpg_mpw_xpcs1_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs1_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs1_reg),
                                          0x34000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_0, "fpg_mpw_xpcs1_reg", fpg_mpw_xpcs1_reg_prop);
        fld_map_t fpg_mpw_xpcs2_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs2_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs2_reg),
                                          0x44000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_0, "fpg_mpw_xpcs2_reg", fpg_mpw_xpcs2_reg_prop);
        fld_map_t fpg_mpw_xpcs3_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs3_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs3_reg),
                                          0x54000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_0, "fpg_mpw_xpcs3_reg", fpg_mpw_xpcs3_reg_prop);
        fld_map_t fpg_mpw_stat_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_stat_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_stat_reg),
                                         0x64000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_0, "fpg_mpw_stat_reg", fpg_mpw_stat_reg_prop);
        fld_map_t fpg_mpw_xpcs_reg91 {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs_reg91_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_mpw_xpcs_reg91),
                                           0x74000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fpg_mpw_0, "fpg_mpw_xpcs_reg91", fpg_mpw_xpcs_reg91_prop);
// END fpg_mpw
    }
    {
// BEGIN fpg_mpw
        auto fpg_mpw_1 = nu_rng[0].add_an({"nu_mpg","fpg_mpw"}, 0x15480000, 1, 0x0);
        fld_map_t fpg_mpw_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fpg_mpw_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_mpw_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_mpw_1, "fpg_mpw_timeout_thresh_cfg", fpg_mpw_timeout_thresh_cfg_prop);
        fld_map_t fpg_mpw_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fpg_mpw_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_mpw_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_mpw_1, "fpg_mpw_timeout_clr", fpg_mpw_timeout_clr_prop);
        fld_map_t fpg_mpw_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_mpw_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_spare_pio),
                                          0x98,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fpg_mpw_1, "fpg_mpw_spare_pio", fpg_mpw_spare_pio_prop);
        fld_map_t fpg_mpw_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fpg_mpw_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_mpw_scratchpad),
                                           0xA0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fpg_mpw_1, "fpg_mpw_scratchpad", fpg_mpw_scratchpad_prop);
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
        };
        auto fpg_mpw_mac_tx_fault_cfg_prop = csr_prop_t(
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
        };
        auto fpg_mpw_mac_lpi_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fpg_mpw_mac_lpi_cfg),
                                            0xE0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fpg_mpw_1, "fpg_mpw_mac_lpi_cfg", fpg_mpw_mac_lpi_cfg_prop);
        fld_map_t fpg_mpw_lpi_tick_cnt_incr_val {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fpg_mpw_lpi_tick_cnt_incr_val_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_mpw_lpi_tick_cnt_incr_val),
                    0xE8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_mpw_1, "fpg_mpw_lpi_tick_cnt_incr_val", fpg_mpw_lpi_tick_cnt_incr_val_prop);
        fld_map_t fpg_mpw_sw_reset {
            CREATE_ENTRY("rst_sd_tx_n", 0, 4),
            CREATE_ENTRY("rst_sd_rx_n", 4, 4),
            CREATE_ENTRY("rst_xpcs_n", 8, 1),
            CREATE_ENTRY("rst_spcs_n", 9, 1),
            CREATE_ENTRY("rst_ref_clk_n", 10, 1),
            CREATE_ENTRY("rst_mac_ref_clk_n", 11, 4),
            CREATE_ENTRY("rst_reg_clk_n", 15, 1),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_sw_reset_prop = csr_prop_t(
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
        };
        auto fpg_mpw_pcs_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fpg_mpw_pcs_cfg),
                                        0x100,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fpg_mpw_1, "fpg_mpw_pcs_cfg", fpg_mpw_pcs_cfg_prop);
        fld_map_t fpg_mpw_tx_rx_loopback_cfg {
            CREATE_ENTRY("en", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fpg_mpw_tx_rx_loopback_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fpg_mpw_tx_rx_loopback_cfg),
                0x110,
                CSR_TYPE::REG,
                1);
        add_csr(fpg_mpw_1, "fpg_mpw_tx_rx_loopback_cfg", fpg_mpw_tx_rx_loopback_cfg_prop);
        fld_map_t fpg_mpw_wct_macro_cfg {
            CREATE_ENTRY("decimal_rollover_en", 0, 1),
            CREATE_ENTRY("base_incr", 1, 26),
            CREATE_ENTRY("base_corr_incr", 27, 26),
            CREATE_ENTRY("override_incr", 53, 26),
            CREATE_ENTRY("base_period", 79, 16),
            CREATE_ENTRY("override_cnt", 95, 16),
            CREATE_ENTRY("override_mode", 111, 1),
            CREATE_ENTRY("sync_pulse_dly_sel", 112, 4),
            CREATE_ENTRY("__rsvd", 116, 12)
        };
        auto fpg_mpw_wct_macro_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fpg_mpw_wct_macro_cfg),
                                              0x118,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fpg_mpw_1, "fpg_mpw_wct_macro_cfg", fpg_mpw_wct_macro_cfg_prop);
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
        };
        auto fpg_mpw_mem_err_inj_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fpg_mpw_mem_err_inj_cfg),
                                                0x128,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fpg_mpw_1, "fpg_mpw_mem_err_inj_cfg", fpg_mpw_mem_err_inj_cfg_prop);
        fld_map_t fpg_mpw_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fpg_mpw_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fpg_mpw_fla_ring_module_id_cfg),
                    0x140,
                    CSR_TYPE::REG,
                    1);
        add_csr(fpg_mpw_1, "fpg_mpw_fla_ring_module_id_cfg", fpg_mpw_fla_ring_module_id_cfg_prop);
        fld_map_t fpg_mpw_mac0_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac0_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac0_reg),
                                         0x800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_1, "fpg_mpw_mac0_reg", fpg_mpw_mac0_reg_prop);
        fld_map_t fpg_mpw_mac1_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac1_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac1_reg),
                                         0x4800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_1, "fpg_mpw_mac1_reg", fpg_mpw_mac1_reg_prop);
        fld_map_t fpg_mpw_mac2_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac2_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac2_reg),
                                         0x8800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_1, "fpg_mpw_mac2_reg", fpg_mpw_mac2_reg_prop);
        fld_map_t fpg_mpw_mac3_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_mac3_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_mac3_reg),
                                         0xC800,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_1, "fpg_mpw_mac3_reg", fpg_mpw_mac3_reg_prop);
        fld_map_t fpg_mpw_cpcs00_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_cpcs00_reg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_mpw_cpcs00_reg),
                                           0x12000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fpg_mpw_1, "fpg_mpw_cpcs00_reg", fpg_mpw_cpcs00_reg_prop);
        fld_map_t fpg_mpw_gpcs0_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_gpcs0_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_gpcs0_reg),
                                          0x22000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_1, "fpg_mpw_gpcs0_reg", fpg_mpw_gpcs0_reg_prop);
        fld_map_t fpg_mpw_xpcs0_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs0_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs0_reg),
                                          0x24000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_1, "fpg_mpw_xpcs0_reg", fpg_mpw_xpcs0_reg_prop);
        fld_map_t fpg_mpw_xpcs1_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs1_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs1_reg),
                                          0x34000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_1, "fpg_mpw_xpcs1_reg", fpg_mpw_xpcs1_reg_prop);
        fld_map_t fpg_mpw_xpcs2_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs2_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs2_reg),
                                          0x44000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_1, "fpg_mpw_xpcs2_reg", fpg_mpw_xpcs2_reg_prop);
        fld_map_t fpg_mpw_xpcs3_reg {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs3_reg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fpg_mpw_xpcs3_reg),
                                          0x54000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fpg_mpw_1, "fpg_mpw_xpcs3_reg", fpg_mpw_xpcs3_reg_prop);
        fld_map_t fpg_mpw_stat_reg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fpg_mpw_stat_reg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fpg_mpw_stat_reg),
                                         0x64000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(fpg_mpw_1, "fpg_mpw_stat_reg", fpg_mpw_stat_reg_prop);
        fld_map_t fpg_mpw_xpcs_reg91 {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fpg_mpw_xpcs_reg91_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fpg_mpw_xpcs_reg91),
                                           0x74000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fpg_mpw_1, "fpg_mpw_xpcs_reg91", fpg_mpw_xpcs_reg91_prop);
// END fpg_mpw
    }
    {
// BEGIN wro
        auto wro_0 = nu_rng[0].add_an({"wro"}, 0x6000000, 1, 0x0);
        fld_map_t wro_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto wro_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(wro_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(wro_0, "wro_timeout_thresh_cfg", wro_timeout_thresh_cfg_prop);
        fld_map_t wro_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto wro_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(wro_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(wro_0, "wro_timeout_clr", wro_timeout_clr_prop);
        fld_map_t wro_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto wro_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(wro_spare_pio),
                                      0xC0,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(wro_0, "wro_spare_pio", wro_spare_pio_prop);
        fld_map_t wro_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto wro_scratchpad_prop = csr_prop_t(
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
        };
        auto wro_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(wro_mem_init_start_cfg),
                                               0xD0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(wro_0, "wro_mem_init_start_cfg", wro_mem_init_start_cfg_prop);
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
        };
        auto wro_mem_err_inj_cfg_prop = csr_prop_t(
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
        };
        auto wro_timer_ctrl_cfg_prop = csr_prop_t(
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
        };
        auto wro_misc_dbg_cfg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(wro_misc_dbg_cfg),
                                         0x108,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(wro_0, "wro_misc_dbg_cfg", wro_misc_dbg_cfg_prop);
        fld_map_t wro_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto wro_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_fla_ring_module_id_cfg),
                0x110,
                CSR_TYPE::REG,
                1);
        add_csr(wro_0, "wro_fla_ring_module_id_cfg", wro_fla_ring_module_id_cfg_prop);
        fld_map_t wro_dbg_gbl_max_oo_sta {
            CREATE_ENTRY("fld_oo_max", 0, 14),
            CREATE_ENTRY("fld_tunnel_id", 14, 14),
            CREATE_ENTRY("__rsvd", 28, 36)
        };
        auto wro_dbg_gbl_max_oo_sta_prop = csr_prop_t(
                                               std::make_shared<csr_s>(wro_dbg_gbl_max_oo_sta),
                                               0x118,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(wro_0, "wro_dbg_gbl_max_oo_sta", wro_dbg_gbl_max_oo_sta_prop);
        fld_map_t wro_dbg_tunnel_max_oo_sta {
            CREATE_ENTRY("fld_oo_max", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto wro_dbg_tunnel_max_oo_sta_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_dbg_tunnel_max_oo_sta),
                0x120,
                CSR_TYPE::REG,
                1);
        add_csr(wro_0, "wro_dbg_tunnel_max_oo_sta", wro_dbg_tunnel_max_oo_sta_prop);
        fld_map_t wro_cuckoo_hash_seed_cfg {
            CREATE_ENTRY("fld_seed_h1", 0, 8),
            CREATE_ENTRY("fld_seed_h2", 8, 8),
            CREATE_ENTRY("fld_seed_h3", 16, 8),
            CREATE_ENTRY("fld_seed_h4", 24, 8),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto wro_cuckoo_hash_seed_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_cuckoo_hash_seed_cfg),
                0x128,
                CSR_TYPE::REG,
                1);
        add_csr(wro_0, "wro_cuckoo_hash_seed_cfg", wro_cuckoo_hash_seed_cfg_prop);
        fld_map_t wro_tunnel_cmd_fifo {
            CREATE_ENTRY("fld_cmd", 0, 2),
            CREATE_ENTRY("fld_tunnel_id", 2, 14),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto wro_tunnel_cmd_fifo_prop = csr_prop_t(
                                            std::make_shared<csr_s>(wro_tunnel_cmd_fifo),
                                            0x140,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(wro_0, "wro_tunnel_cmd_fifo", wro_tunnel_cmd_fifo_prop);
        fld_map_t wro_flush_all_cmd_cfg {
            CREATE_ENTRY("fld_cmd", 0, 1),
            CREATE_ENTRY("fld_pending_status", 1, 1),
            CREATE_ENTRY("fld_done_status", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto wro_flush_all_cmd_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(wro_flush_all_cmd_cfg),
                                              0x148,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(wro_0, "wro_flush_all_cmd_cfg", wro_flush_all_cmd_cfg_prop);
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
        };
        auto wro_wu_msg_map_cfg_prop = csr_prop_t(
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
        };
        auto wro_vp_wu_msg_type_map_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_vp_wu_msg_type_map_cfg),
                0x158,
                CSR_TYPE::REG,
                1);
        add_csr(wro_0, "wro_vp_wu_msg_type_map_cfg", wro_vp_wu_msg_type_map_cfg_prop);
        fld_map_t wro_wu_msg_dgid_map_cfg {
            CREATE_ENTRY("fld_cluster0", 0, 5),
            CREATE_ENTRY("fld_cluster1", 5, 5),
            CREATE_ENTRY("fld_cluster2", 10, 5),
            CREATE_ENTRY("fld_cluster3", 15, 5),
            CREATE_ENTRY("fld_cluster4", 20, 5),
            CREATE_ENTRY("fld_cluster5", 25, 5),
            CREATE_ENTRY("fld_cluster6", 30, 5),
            CREATE_ENTRY("fld_cluster7", 35, 5),
            CREATE_ENTRY("fld_cluster8", 40, 5),
            CREATE_ENTRY("fld_cluster9", 45, 5),
            CREATE_ENTRY("fld_cluster10", 50, 5),
            CREATE_ENTRY("fld_cluster11", 55, 5),
            CREATE_ENTRY("fld_cluster12", 60, 5),
            CREATE_ENTRY("fld_cluster13", 65, 5),
            CREATE_ENTRY("fld_cluster14", 70, 5),
            CREATE_ENTRY("fld_cluster15", 75, 5),
            CREATE_ENTRY("__rsvd", 80, 48)
        };
        auto wro_wu_msg_dgid_map_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(wro_wu_msg_dgid_map_cfg),
                                                0x160,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(wro_0, "wro_wu_msg_dgid_map_cfg", wro_wu_msg_dgid_map_cfg_prop);
        fld_map_t wro_vpp_wu_msg_cfg {
            CREATE_ENTRY("fld_arg0", 0, 16),
            CREATE_ENTRY("fld_arg1", 16, 16),
            CREATE_ENTRY("fld_arg2", 32, 16),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto wro_vpp_wu_msg_cfg_prop = csr_prop_t(
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
        };
        auto wro_le_wu_msg_cfg_prop = csr_prop_t(
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
        };
        auto wro_nu_wu_msg_cfg_prop = csr_prop_t(
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
        };
        auto wro_buffer_address_cfg_prop = csr_prop_t(
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
        };
        auto wro_sn_msg_map_cfg_prop = csr_prop_t(
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
        };
        auto wro_sn_msg_dgid_map_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(wro_sn_msg_dgid_map_cfg),
                                                0x198,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(wro_0, "wro_sn_msg_dgid_map_cfg", wro_sn_msg_dgid_map_cfg_prop);
        fld_map_t wro_dispatch_fifo_crdt_init_cfg {
            CREATE_ENTRY("fld_ini_crdt_val", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto wro_dispatch_fifo_crdt_init_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_dispatch_fifo_crdt_init_cfg),
                    0x1A0,
                    CSR_TYPE::REG,
                    1);
        add_csr(wro_0, "wro_dispatch_fifo_crdt_init_cfg", wro_dispatch_fifo_crdt_init_cfg_prop);
        fld_map_t wro_wun_fl_cfg {
            CREATE_ENTRY("fld_psw_xoff_thresh", 0, 15),
            CREATE_ENTRY("fld_psw_xon_thresh", 15, 15),
            CREATE_ENTRY("fld_fcb_xoff_thresh", 30, 15),
            CREATE_ENTRY("fld_fcb_xon_thresh", 45, 15),
            CREATE_ENTRY("__rsvd", 60, 4)
        };
        auto wro_wun_fl_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(wro_wun_fl_cfg),
                                       0x1A8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(wro_0, "wro_wun_fl_cfg", wro_wun_fl_cfg_prop);
        fld_map_t wro_tunnel_role_cfg {
            CREATE_ENTRY("fld_max_future_seqn_range", 0, 24),
            CREATE_ENTRY("fld_max_past_seqn_range", 24, 24),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto wro_tunnel_role_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(wro_tunnel_role_cfg),
                                            0x1E0,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(wro_0, "wro_tunnel_role_cfg", wro_tunnel_role_cfg_prop);
        fld_map_t wro_sn_if_crdt_cfg {
            CREATE_ENTRY("fld_init_vc0_val", 0, 5),
            CREATE_ENTRY("fld_init_vc1_val", 5, 5),
            CREATE_ENTRY("fld_init_vc2_val", 10, 5),
            CREATE_ENTRY("fld_init_vc3_val", 15, 5),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto wro_sn_if_crdt_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(wro_sn_if_crdt_cfg),
                                           0x2E0,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(wro_0, "wro_sn_if_crdt_cfg", wro_sn_if_crdt_cfg_prop);
        fld_map_t wro_wun_fl_bitallocate_pio_cfg {
            CREATE_ENTRY("fld_data", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto wro_wun_fl_bitallocate_pio_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_wun_fl_bitallocate_pio_cfg),
                    0x8000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_wun_fl_bitallocate_pio_cfg", wro_wun_fl_bitallocate_pio_cfg_prop);
        fld_map_t wro_dbg_probe_dhs {
            CREATE_ENTRY("fld_val", 0, 64)
        };
        auto wro_dbg_probe_dhs_prop = csr_prop_t(
                                          std::make_shared<csr_s>(wro_dbg_probe_dhs),
                                          0x48000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(wro_0, "wro_dbg_probe_dhs", wro_dbg_probe_dhs_prop);
        fld_map_t wro_stats_cntr {
            CREATE_ENTRY("fld_count", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto wro_stats_cntr_prop = csr_prop_t(
                                       std::make_shared<csr_s>(wro_stats_cntr),
                                       0x48200,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(wro_0, "wro_stats_cntr", wro_stats_cntr_prop);
        fld_map_t wro_wun_db_mem_dhs {
            CREATE_ENTRY("fld_drop", 0, 1),
            CREATE_ENTRY("f_trace", 1, 1),
            CREATE_ENTRY("fld_efp_id", 2, 2),
            CREATE_ENTRY("fld_cluster_id", 4, 4),
            CREATE_ENTRY("fld_dlid", 8, 5),
            CREATE_ENTRY("fld_queue_id", 13, 8),
            CREATE_ENTRY("fld_pc_num", 21, 3),
            CREATE_ENTRY("fld_buffer_handle", 24, 13),
            CREATE_ENTRY("fld_sw_opcode", 37, 24),
            CREATE_ENTRY("__rsvd", 61, 3)
        };
        auto wro_wun_db_mem_dhs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(wro_wun_db_mem_dhs),
                                           0x60000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(wro_0, "wro_wun_db_mem_dhs", wro_wun_db_mem_dhs_prop);
        fld_map_t wro_fcb_pkt_ctx_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_qos", 14, 3),
            CREATE_ENTRY("fld_block_num", 17, 16),
            CREATE_ENTRY("__rsvd", 33, 31)
        };
        auto wro_fcb_pkt_ctx_mem_dhs_prop = csr_prop_t(
                                                std::make_shared<csr_s>(wro_fcb_pkt_ctx_mem_dhs),
                                                0x160000,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(wro_0, "wro_fcb_pkt_ctx_mem_dhs", wro_fcb_pkt_ctx_mem_dhs_prop);
        fld_map_t wro_tunnel_ctx_psn_mem_dhs {
            CREATE_ENTRY("fld_ro_state", 0, 2),
            CREATE_ENTRY("fld_flush", 2, 1),
            CREATE_ENTRY("fld_sync", 3, 1),
            CREATE_ENTRY("fld_last_psn", 4, 24),
            CREATE_ENTRY("__rsvd", 28, 36)
        };
        auto wro_tunnel_ctx_psn_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_tunnel_ctx_psn_mem_dhs),
                0x260000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_tunnel_ctx_psn_mem_dhs", wro_tunnel_ctx_psn_mem_dhs_prop);
        fld_map_t wro_tunnel_ctx_pktcnt_mem_dhs {
            CREATE_ENTRY("fld_oo_pkt_cnt", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto wro_tunnel_ctx_pktcnt_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_tunnel_ctx_pktcnt_mem_dhs),
                    0x360000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_tunnel_ctx_pktcnt_mem_dhs", wro_tunnel_ctx_pktcnt_mem_dhs_prop);
        fld_map_t wro_tunnel_cfg_role_tbl_mem_dhs {
            CREATE_ENTRY("fld_entry0_role", 0, 2),
            CREATE_ENTRY("fld_entry0_bypass_ro", 2, 1),
            CREATE_ENTRY("fld_entry1_role", 3, 2),
            CREATE_ENTRY("fld_entry1_bypass_ro", 5, 1),
            CREATE_ENTRY("fld_entry2_role", 6, 2),
            CREATE_ENTRY("fld_entry2_bypass_ro", 8, 1),
            CREATE_ENTRY("fld_entry3_role", 9, 2),
            CREATE_ENTRY("fld_entry3_bypass_ro", 11, 1),
            CREATE_ENTRY("fld_entry4_role", 12, 2),
            CREATE_ENTRY("fld_entry4_bypass_ro", 14, 1),
            CREATE_ENTRY("fld_entry5_role", 15, 2),
            CREATE_ENTRY("fld_entry5_bypass_ro", 17, 1),
            CREATE_ENTRY("fld_entry6_role", 18, 2),
            CREATE_ENTRY("fld_entry6_bypass_ro", 20, 1),
            CREATE_ENTRY("fld_entry7_role", 21, 2),
            CREATE_ENTRY("fld_entry7_bypass_ro", 23, 1),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto wro_tunnel_cfg_role_tbl_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_tunnel_cfg_role_tbl_mem_dhs),
                    0x460000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_tunnel_cfg_role_tbl_mem_dhs", wro_tunnel_cfg_role_tbl_mem_dhs_prop);
        fld_map_t wro_tunnel_seqn_error_event_log_mem_dhs {
            CREATE_ENTRY("fld_seqn_error", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto wro_tunnel_seqn_error_event_log_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_tunnel_seqn_error_event_log_mem_dhs),
                    0x480000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_tunnel_seqn_error_event_log_mem_dhs", wro_tunnel_seqn_error_event_log_mem_dhs_prop);
        fld_map_t wro_tunnel_timeout_event_log_mem_dhs {
            CREATE_ENTRY("fld_timeout_error", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto wro_tunnel_timeout_event_log_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_tunnel_timeout_event_log_mem_dhs),
                    0x488000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_tunnel_timeout_event_log_mem_dhs", wro_tunnel_timeout_event_log_mem_dhs_prop);
        fld_map_t wro_hash_tbl_vldmap_h1_mem_dhs {
            CREATE_ENTRY("fld_set0_vldmap", 0, 4),
            CREATE_ENTRY("fld_set1_vldmap", 4, 4),
            CREATE_ENTRY("fld_set2_vldmap", 8, 4),
            CREATE_ENTRY("fld_set3_vldmap", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto wro_hash_tbl_vldmap_h1_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_hash_tbl_vldmap_h1_mem_dhs),
                    0x490000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_hash_tbl_vldmap_h1_mem_dhs", wro_hash_tbl_vldmap_h1_mem_dhs_prop);
        fld_map_t wro_hash_tbl_vldmap_h2_mem_dhs {
            CREATE_ENTRY("fld_set0_vldmap", 0, 4),
            CREATE_ENTRY("fld_set1_vldmap", 4, 4),
            CREATE_ENTRY("fld_set2_vldmap", 8, 4),
            CREATE_ENTRY("fld_set3_vldmap", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto wro_hash_tbl_vldmap_h2_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_hash_tbl_vldmap_h2_mem_dhs),
                    0x494000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_hash_tbl_vldmap_h2_mem_dhs", wro_hash_tbl_vldmap_h2_mem_dhs_prop);
        fld_map_t wro_hash_tbl_vldmap_h3_mem_dhs {
            CREATE_ENTRY("fld_set0_vldmap", 0, 4),
            CREATE_ENTRY("fld_set1_vldmap", 4, 4),
            CREATE_ENTRY("fld_set2_vldmap", 8, 4),
            CREATE_ENTRY("fld_set3_vldmap", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto wro_hash_tbl_vldmap_h3_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_hash_tbl_vldmap_h3_mem_dhs),
                    0x498000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_hash_tbl_vldmap_h3_mem_dhs", wro_hash_tbl_vldmap_h3_mem_dhs_prop);
        fld_map_t wro_hash_tbl_vldmap_h4_mem_dhs {
            CREATE_ENTRY("fld_set0_vldmap", 0, 4),
            CREATE_ENTRY("fld_set1_vldmap", 4, 4),
            CREATE_ENTRY("fld_set2_vldmap", 8, 4),
            CREATE_ENTRY("fld_set3_vldmap", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto wro_hash_tbl_vldmap_h4_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(wro_hash_tbl_vldmap_h4_mem_dhs),
                    0x49C000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(wro_0, "wro_hash_tbl_vldmap_h4_mem_dhs", wro_hash_tbl_vldmap_h4_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h10_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h10_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h10_mem_dhs),
                0x4A0000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h10_mem_dhs", wro_hash_tbl_h10_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h11_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h11_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h11_mem_dhs),
                0x4B0000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h11_mem_dhs", wro_hash_tbl_h11_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h12_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h12_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h12_mem_dhs),
                0x4C0000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h12_mem_dhs", wro_hash_tbl_h12_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h13_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h13_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h13_mem_dhs),
                0x4D0000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h13_mem_dhs", wro_hash_tbl_h13_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h20_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h20_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h20_mem_dhs),
                0x4E0000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h20_mem_dhs", wro_hash_tbl_h20_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h21_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h21_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h21_mem_dhs),
                0x4F0000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h21_mem_dhs", wro_hash_tbl_h21_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h22_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h22_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h22_mem_dhs),
                0x500000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h22_mem_dhs", wro_hash_tbl_h22_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h23_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h23_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h23_mem_dhs),
                0x510000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h23_mem_dhs", wro_hash_tbl_h23_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h30_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h30_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h30_mem_dhs),
                0x520000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h30_mem_dhs", wro_hash_tbl_h30_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h31_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h31_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h31_mem_dhs),
                0x530000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h31_mem_dhs", wro_hash_tbl_h31_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h32_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h32_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h32_mem_dhs),
                0x540000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h32_mem_dhs", wro_hash_tbl_h32_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h33_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h33_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h33_mem_dhs),
                0x550000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h33_mem_dhs", wro_hash_tbl_h33_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h40_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h40_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h40_mem_dhs),
                0x560000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h40_mem_dhs", wro_hash_tbl_h40_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h41_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h41_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h41_mem_dhs),
                0x570000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h41_mem_dhs", wro_hash_tbl_h41_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h42_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h42_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h42_mem_dhs),
                0x580000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h42_mem_dhs", wro_hash_tbl_h42_mem_dhs_prop);
        fld_map_t wro_hash_tbl_h43_mem_dhs {
            CREATE_ENTRY("fld_tunnel_id", 0, 14),
            CREATE_ENTRY("fld_psn", 14, 24),
            CREATE_ENTRY("fld_rslt", 38, 14),
            CREATE_ENTRY("fld_timestamp", 52, 4),
            CREATE_ENTRY("fld_to_state", 56, 1),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto wro_hash_tbl_h43_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(wro_hash_tbl_h43_mem_dhs),
                0x590000,
                CSR_TYPE::TBL,
                1);
        add_csr(wro_0, "wro_hash_tbl_h43_mem_dhs", wro_hash_tbl_h43_mem_dhs_prop);
// END wro
    }
    {
// BEGIN fcb
        auto fcb_0 = nu_rng[0].add_an({"fcb"}, 0x7000000, 1, 0x0);
        fld_map_t fcb_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fcb_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fcb_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fcb_0, "fcb_timeout_thresh_cfg", fcb_timeout_thresh_cfg_prop);
        fld_map_t fcb_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fcb_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fcb_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fcb_0, "fcb_timeout_clr", fcb_timeout_clr_prop);
        fld_map_t fcb_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fcb_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(fcb_spare_pio),
                                      0x98,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(fcb_0, "fcb_spare_pio", fcb_spare_pio_prop);
        fld_map_t fcb_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fcb_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fcb_scratchpad),
                                       0xA0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fcb_0, "fcb_scratchpad", fcb_scratchpad_prop);
        fld_map_t fcb_wct_macro_cfg {
            CREATE_ENTRY("decimal_rollover_en", 0, 1),
            CREATE_ENTRY("base_incr", 1, 26),
            CREATE_ENTRY("base_corr_incr", 27, 26),
            CREATE_ENTRY("override_incr", 53, 26),
            CREATE_ENTRY("base_period", 79, 16),
            CREATE_ENTRY("override_cnt", 95, 16),
            CREATE_ENTRY("override_mode", 111, 1),
            CREATE_ENTRY("sync_pulse_dly_sel", 112, 4),
            CREATE_ENTRY("__rsvd", 116, 12)
        };
        auto fcb_wct_macro_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fcb_wct_macro_cfg),
                                          0xA8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fcb_0, "fcb_wct_macro_cfg", fcb_wct_macro_cfg_prop);
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
        };
        auto fcb_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fcb_mem_init_start_cfg),
                                               0xB8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fcb_0, "fcb_mem_init_start_cfg", fcb_mem_init_start_cfg_prop);
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
        };
        auto fcb_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fcb_mem_err_inj_cfg),
                                            0xE0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fcb_0, "fcb_mem_err_inj_cfg", fcb_mem_err_inj_cfg_prop);
        fld_map_t fcb_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcb_fla_ring_module_id_cfg_prop = csr_prop_t(
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
            CREATE_ENTRY("fld_ctrl_tx_datarate_adj_enable", 12, 1),
            CREATE_ENTRY("fld_src_flow_wt_override_enable", 13, 1),
            CREATE_ENTRY("fld_src_flow_wt_mantissa", 14, 4),
            CREATE_ENTRY("fld_src_flow_wt_exponent", 18, 4),
            CREATE_ENTRY("fld_scale_dn_override_enable", 22, 1),
            CREATE_ENTRY("fld_pkt_flush_ignore_psw_xoff", 23, 1),
            CREATE_ENTRY("fld_flow_ctrl_cnt_enable", 24, 1),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto fcb_gbl_cfg_prop = csr_prop_t(
                                    std::make_shared<csr_s>(fcb_gbl_cfg),
                                    0xF0,
                                    CSR_TYPE::REG,
                                    1);
        add_csr(fcb_0, "fcb_gbl_cfg", fcb_gbl_cfg_prop);
        fld_map_t fcb_gph_and_mask_cfg {
            CREATE_ENTRY("fld_val", 0, 128)
        };
        auto fcb_gph_and_mask_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fcb_gph_and_mask_cfg),
                                             0xF8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fcb_0, "fcb_gph_and_mask_cfg", fcb_gph_and_mask_cfg_prop);
        fld_map_t fcb_gph_or_mask_cfg {
            CREATE_ENTRY("fld_val", 0, 128)
        };
        auto fcb_gph_or_mask_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fcb_gph_or_mask_cfg),
                                            0x108,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fcb_0, "fcb_gph_or_mask_cfg", fcb_gph_or_mask_cfg_prop);
        fld_map_t fcb_req_sch_qos2grp_map_cfg {
            CREATE_ENTRY("fld_qos0", 0, 3),
            CREATE_ENTRY("fld_qos1", 3, 3),
            CREATE_ENTRY("fld_qos2", 6, 3),
            CREATE_ENTRY("fld_qos3", 9, 3),
            CREATE_ENTRY("fld_qos4", 12, 3),
            CREATE_ENTRY("fld_qos5", 15, 3),
            CREATE_ENTRY("fld_qos6", 18, 3),
            CREATE_ENTRY("fld_qos7", 21, 3),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto fcb_req_sch_qos2grp_map_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_req_sch_qos2grp_map_cfg),
                0x118,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_req_sch_qos2grp_map_cfg", fcb_req_sch_qos2grp_map_cfg_prop);
        fld_map_t fcb_req_sch_grp2str_pri_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcb_req_sch_grp2str_pri_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_req_sch_grp2str_pri_cfg),
                0x120,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_req_sch_grp2str_pri_cfg", fcb_req_sch_grp2str_pri_cfg_prop);
        fld_map_t fcb_req_sch_qos_group_dwrr_wt_cfg {
            CREATE_ENTRY("fld_group0", 0, 7),
            CREATE_ENTRY("fld_group1", 7, 7),
            CREATE_ENTRY("fld_group2", 14, 7),
            CREATE_ENTRY("fld_group3", 21, 7),
            CREATE_ENTRY("fld_group4", 28, 7),
            CREATE_ENTRY("fld_group5", 35, 7),
            CREATE_ENTRY("fld_group6", 42, 7),
            CREATE_ENTRY("fld_group7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_req_sch_qos_group_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_req_sch_qos_group_dwrr_wt_cfg),
                    0x128,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_req_sch_qos_group_dwrr_wt_cfg", fcb_req_sch_qos_group_dwrr_wt_cfg_prop);
        fld_map_t fcb_req_sch_qos_dwrr_wt_cfg {
            CREATE_ENTRY("fld_qos0", 0, 7),
            CREATE_ENTRY("fld_qos1", 7, 7),
            CREATE_ENTRY("fld_qos2", 14, 7),
            CREATE_ENTRY("fld_qos3", 21, 7),
            CREATE_ENTRY("fld_qos4", 28, 7),
            CREATE_ENTRY("fld_qos5", 35, 7),
            CREATE_ENTRY("fld_qos6", 42, 7),
            CREATE_ENTRY("fld_qos7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_req_sch_qos_dwrr_wt_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_req_sch_qos_dwrr_wt_cfg),
                0x130,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_req_sch_qos_dwrr_wt_cfg", fcb_req_sch_qos_dwrr_wt_cfg_prop);
        fld_map_t fcb_req_sch_host_intf_dwrr_wt_cfg {
            CREATE_ENTRY("fld_host_intf0", 0, 7),
            CREATE_ENTRY("fld_host_intf1", 7, 7),
            CREATE_ENTRY("fld_host_intf2", 14, 7),
            CREATE_ENTRY("fld_host_intf3", 21, 7),
            CREATE_ENTRY("fld_host_intf4", 28, 7),
            CREATE_ENTRY("fld_host_intf5", 35, 7),
            CREATE_ENTRY("fld_host_intf6", 42, 7),
            CREATE_ENTRY("fld_host_intf7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_req_sch_host_intf_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_req_sch_host_intf_dwrr_wt_cfg),
                    0x138,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_req_sch_host_intf_dwrr_wt_cfg", fcb_req_sch_host_intf_dwrr_wt_cfg_prop);
        fld_map_t fcb_req_datarate_pacer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
            CREATE_ENTRY("fld_base_leak_rate", 9, 16),
            CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
            CREATE_ENTRY("fld_min_thresh", 40, 15),
            CREATE_ENTRY("__rsvd", 55, 9)
        };
        auto fcb_req_datarate_pacer_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_req_datarate_pacer_cfg),
                0x140,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_req_datarate_pacer_cfg", fcb_req_datarate_pacer_cfg_prop);
        fld_map_t fcb_req_ctlmsg_pacer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_leak_tick_cnt", 1, 12),
            CREATE_ENTRY("fld_base_leak_rate", 13, 12),
            CREATE_ENTRY("fld_admit_lvl_thresh", 25, 24),
            CREATE_ENTRY("fld_update_val", 49, 12),
            CREATE_ENTRY("__rsvd", 61, 3)
        };
        auto fcb_req_ctlmsg_pacer_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_req_ctlmsg_pacer_cfg),
                0x148,
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
        };
        auto fcb_unsol_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_unsol_datarate_pacer_cfg),
                    0x150,
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
        };
        auto fcb_src_gbl_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_gbl_datarate_pacer_cfg),
                    0x158,
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
        };
        auto fcb_src_fcp_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_fcp_datarate_pacer_cfg),
                    0x160,
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
        };
        auto fcb_src_nfcp_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_nfcp_datarate_pacer_cfg),
                    0x168,
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
        };
        auto fcb_src_nfcp_pipe_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_nfcp_pipe_datarate_pacer_cfg),
                    0x170,
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
        };
        auto fcb_src_drop_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_drop_datarate_pacer_cfg),
                    0x178,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_src_drop_datarate_pacer_cfg", fcb_src_drop_datarate_pacer_cfg_prop);
        fld_map_t fcb_tdp_lb_cfg {
            CREATE_ENTRY("fld_pipe_pend_blks_thresh", 0, 16),
            CREATE_ENTRY("fld_fcp_pend_blks_thresh", 16, 16),
            CREATE_ENTRY("fld_nfcp_pend_blks_thresh", 32, 16),
            CREATE_ENTRY("fld_gbl_pend_blks_thresh", 48, 16)
        };
        auto fcb_tdp_lb_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fcb_tdp_lb_cfg),
                                       0x180,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fcb_0, "fcb_tdp_lb_cfg", fcb_tdp_lb_cfg_prop);
        fld_map_t fcb_nfcp_pkt_sch_qos2grp_map_cfg {
            CREATE_ENTRY("fld_qos0", 0, 3),
            CREATE_ENTRY("fld_qos1", 3, 3),
            CREATE_ENTRY("fld_qos2", 6, 3),
            CREATE_ENTRY("fld_qos3", 9, 3),
            CREATE_ENTRY("fld_qos4", 12, 3),
            CREATE_ENTRY("fld_qos5", 15, 3),
            CREATE_ENTRY("fld_qos6", 18, 3),
            CREATE_ENTRY("fld_qos7", 21, 3),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto fcb_nfcp_pkt_sch_qos2grp_map_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_nfcp_pkt_sch_qos2grp_map_cfg),
                    0x1A8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_nfcp_pkt_sch_qos2grp_map_cfg", fcb_nfcp_pkt_sch_qos2grp_map_cfg_prop);
        fld_map_t fcb_nfcp_pkt_sch_grp2str_pri_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcb_nfcp_pkt_sch_grp2str_pri_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_nfcp_pkt_sch_grp2str_pri_cfg),
                    0x1B0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_nfcp_pkt_sch_grp2str_pri_cfg", fcb_nfcp_pkt_sch_grp2str_pri_cfg_prop);
        fld_map_t fcb_nfcp_pkt_sch_qos_group_dwrr_wt_cfg {
            CREATE_ENTRY("fld_group0", 0, 7),
            CREATE_ENTRY("fld_group1", 7, 7),
            CREATE_ENTRY("fld_group2", 14, 7),
            CREATE_ENTRY("fld_group3", 21, 7),
            CREATE_ENTRY("fld_group4", 28, 7),
            CREATE_ENTRY("fld_group5", 35, 7),
            CREATE_ENTRY("fld_group6", 42, 7),
            CREATE_ENTRY("fld_group7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_nfcp_pkt_sch_qos_group_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_nfcp_pkt_sch_qos_group_dwrr_wt_cfg),
                    0x1B8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_nfcp_pkt_sch_qos_group_dwrr_wt_cfg", fcb_nfcp_pkt_sch_qos_group_dwrr_wt_cfg_prop);
        fld_map_t fcb_nfcp_pkt_sch_qos_dwrr_wt_cfg {
            CREATE_ENTRY("fld_qos0", 0, 7),
            CREATE_ENTRY("fld_qos1", 7, 7),
            CREATE_ENTRY("fld_qos2", 14, 7),
            CREATE_ENTRY("fld_qos3", 21, 7),
            CREATE_ENTRY("fld_qos4", 28, 7),
            CREATE_ENTRY("fld_qos5", 35, 7),
            CREATE_ENTRY("fld_qos6", 42, 7),
            CREATE_ENTRY("fld_qos7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_nfcp_pkt_sch_qos_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_nfcp_pkt_sch_qos_dwrr_wt_cfg),
                    0x1C0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_nfcp_pkt_sch_qos_dwrr_wt_cfg", fcb_nfcp_pkt_sch_qos_dwrr_wt_cfg_prop);
        fld_map_t fcb_pkt_sch_nfcp_streams_dwrr_wt_cfg {
            CREATE_ENTRY("fld_stream0", 0, 7),
            CREATE_ENTRY("fld_stream1", 7, 7),
            CREATE_ENTRY("fld_stream2", 14, 7),
            CREATE_ENTRY("fld_stream3", 21, 7),
            CREATE_ENTRY("fld_stream4", 28, 7),
            CREATE_ENTRY("fld_stream5", 35, 7),
            CREATE_ENTRY("fld_stream6", 42, 7),
            CREATE_ENTRY("fld_stream7", 49, 7),
            CREATE_ENTRY("fld_stream8", 56, 7),
            CREATE_ENTRY("fld_stream9", 63, 7),
            CREATE_ENTRY("fld_stream10", 70, 7),
            CREATE_ENTRY("fld_stream11", 77, 7),
            CREATE_ENTRY("fld_stream12", 84, 7),
            CREATE_ENTRY("fld_stream13", 91, 7),
            CREATE_ENTRY("fld_stream14", 98, 7),
            CREATE_ENTRY("fld_stream15", 105, 7),
            CREATE_ENTRY("fld_stream16", 112, 7),
            CREATE_ENTRY("fld_stream17", 119, 7),
            CREATE_ENTRY("fld_stream18", 126, 7),
            CREATE_ENTRY("fld_stream19", 133, 7),
            CREATE_ENTRY("fld_stream20", 140, 7),
            CREATE_ENTRY("fld_stream21", 147, 7),
            CREATE_ENTRY("fld_stream22", 154, 7),
            CREATE_ENTRY("fld_stream23", 161, 7),
            CREATE_ENTRY("__rsvd", 168, 24)
        };
        auto fcb_pkt_sch_nfcp_streams_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_pkt_sch_nfcp_streams_dwrr_wt_cfg),
                    0x1C8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_pkt_sch_nfcp_streams_dwrr_wt_cfg", fcb_pkt_sch_nfcp_streams_dwrr_wt_cfg_prop);
        fld_map_t fcb_pkt_sch_cfg {
            CREATE_ENTRY("fld_fcp_strict_pri", 0, 1),
            CREATE_ENTRY("fld_fcp_dwrr_wt", 1, 7),
            CREATE_ENTRY("fld_nfcp_dwrr_wt", 8, 7),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fcb_pkt_sch_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fcb_pkt_sch_cfg),
                                        0x1E0,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fcb_0, "fcb_pkt_sch_cfg", fcb_pkt_sch_cfg_prop);
        fld_map_t fcb_etp_deq_info_if_crdt_cfg {
            CREATE_ENTRY("fld_pipe0", 0, 6),
            CREATE_ENTRY("fld_pipe1", 6, 6),
            CREATE_ENTRY("fld_pipe2", 12, 6),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto fcb_etp_deq_info_if_crdt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_etp_deq_info_if_crdt_cfg),
                    0x1E8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_etp_deq_info_if_crdt_cfg", fcb_etp_deq_info_if_crdt_cfg_prop);
        fld_map_t fcb_wqm_deq_req_if_crdt_cfg {
            CREATE_ENTRY("fld_pipe0", 0, 4),
            CREATE_ENTRY("fld_pipe1", 4, 4),
            CREATE_ENTRY("fld_pipe2", 8, 4),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto fcb_wqm_deq_req_if_crdt_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_wqm_deq_req_if_crdt_cfg),
                0x1F0,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_wqm_deq_req_if_crdt_cfg", fcb_wqm_deq_req_if_crdt_cfg_prop);
        fld_map_t fcb_src_timer_ctrl_cfg {
            CREATE_ENTRY("fld_timer_enable", 0, 1),
            CREATE_ENTRY("fld_timer_tdm_cnt", 1, 4),
            CREATE_ENTRY("fld_req_timer_tick_cnt", 5, 16),
            CREATE_ENTRY("fld_max_req_retry_cnt", 21, 4),
            CREATE_ENTRY("fld_req_tov_val", 25, 4),
            CREATE_ENTRY("fld_idle_timer_tick_cnt", 29, 16),
            CREATE_ENTRY("fld_idle_tov_val", 45, 4),
            CREATE_ENTRY("__rsvd", 49, 15)
        };
        auto fcb_src_timer_ctrl_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fcb_src_timer_ctrl_cfg),
                                               0x1F8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fcb_0, "fcb_src_timer_ctrl_cfg", fcb_src_timer_ctrl_cfg_prop);
        fld_map_t fcb_src_max_req_retry_symptom {
            CREATE_ENTRY("fld_vld", 0, 1),
            CREATE_ENTRY("fld_wu_qid", 1, 14),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fcb_src_max_req_retry_symptom_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_max_req_retry_symptom),
                    0x208,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_src_max_req_retry_symptom", fcb_src_max_req_retry_symptom_prop);
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
        };
        auto fcb_fcp_ncv_thresh_role_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_fcp_ncv_thresh_role_cfg),
                0x228,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_fcp_ncv_thresh_role_cfg", fcb_fcp_ncv_thresh_role_cfg_prop);
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
        };
        auto fcb_nfcp_ncv_thresh_role_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_nfcp_ncv_thresh_role_cfg),
                    0x238,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_nfcp_ncv_thresh_role_cfg", fcb_nfcp_ncv_thresh_role_cfg_prop);
        fld_map_t fcb_bn_sender_if_crdt_cfg {
            CREATE_ENTRY("fld_val", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto fcb_bn_sender_if_crdt_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_bn_sender_if_crdt_cfg),
                0x240,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_bn_sender_if_crdt_cfg", fcb_bn_sender_if_crdt_cfg_prop);
        fld_map_t fcb_gnt_sch_qos2grp_map_cfg {
            CREATE_ENTRY("fld_qos0", 0, 3),
            CREATE_ENTRY("fld_qos1", 3, 3),
            CREATE_ENTRY("fld_qos2", 6, 3),
            CREATE_ENTRY("fld_qos3", 9, 3),
            CREATE_ENTRY("fld_qos4", 12, 3),
            CREATE_ENTRY("fld_qos5", 15, 3),
            CREATE_ENTRY("fld_qos6", 18, 3),
            CREATE_ENTRY("fld_qos7", 21, 3),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto fcb_gnt_sch_qos2grp_map_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_gnt_sch_qos2grp_map_cfg),
                0x248,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_gnt_sch_qos2grp_map_cfg", fcb_gnt_sch_qos2grp_map_cfg_prop);
        fld_map_t fcb_gnt_sch_grp2str_pri_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcb_gnt_sch_grp2str_pri_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_gnt_sch_grp2str_pri_cfg),
                0x250,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_gnt_sch_grp2str_pri_cfg", fcb_gnt_sch_grp2str_pri_cfg_prop);
        fld_map_t fcb_gnt_sch_qos_group_dwrr_wt_cfg {
            CREATE_ENTRY("fld_group0", 0, 7),
            CREATE_ENTRY("fld_group1", 7, 7),
            CREATE_ENTRY("fld_group2", 14, 7),
            CREATE_ENTRY("fld_group3", 21, 7),
            CREATE_ENTRY("fld_group4", 28, 7),
            CREATE_ENTRY("fld_group5", 35, 7),
            CREATE_ENTRY("fld_group6", 42, 7),
            CREATE_ENTRY("fld_group7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_gnt_sch_qos_group_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_gnt_sch_qos_group_dwrr_wt_cfg),
                    0x258,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_gnt_sch_qos_group_dwrr_wt_cfg", fcb_gnt_sch_qos_group_dwrr_wt_cfg_prop);
        fld_map_t fcb_gnt_sch_qos_dwrr_wt_cfg {
            CREATE_ENTRY("fld_qos0", 0, 7),
            CREATE_ENTRY("fld_qos1", 7, 7),
            CREATE_ENTRY("fld_qos2", 14, 7),
            CREATE_ENTRY("fld_qos3", 21, 7),
            CREATE_ENTRY("fld_qos4", 28, 7),
            CREATE_ENTRY("fld_qos5", 35, 7),
            CREATE_ENTRY("fld_qos6", 42, 7),
            CREATE_ENTRY("fld_qos7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_gnt_sch_qos_dwrr_wt_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_gnt_sch_qos_dwrr_wt_cfg),
                0x260,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_gnt_sch_qos_dwrr_wt_cfg", fcb_gnt_sch_qos_dwrr_wt_cfg_prop);
        fld_map_t fcb_gnt_sch_host_intf_dwrr_wt_cfg {
            CREATE_ENTRY("fld_host_intf0", 0, 7),
            CREATE_ENTRY("fld_host_intf1", 7, 7),
            CREATE_ENTRY("fld_host_intf2", 14, 7),
            CREATE_ENTRY("fld_host_intf3", 21, 7),
            CREATE_ENTRY("fld_host_intf4", 28, 7),
            CREATE_ENTRY("fld_host_intf5", 35, 7),
            CREATE_ENTRY("fld_host_intf6", 42, 7),
            CREATE_ENTRY("fld_host_intf7", 49, 7),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto fcb_gnt_sch_host_intf_dwrr_wt_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_gnt_sch_host_intf_dwrr_wt_cfg),
                    0x268,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_gnt_sch_host_intf_dwrr_wt_cfg", fcb_gnt_sch_host_intf_dwrr_wt_cfg_prop);
        fld_map_t fcb_gnt_datarate_pacer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
            CREATE_ENTRY("fld_base_leak_rate", 9, 16),
            CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
            CREATE_ENTRY("fld_min_thresh", 40, 15),
            CREATE_ENTRY("__rsvd", 55, 9)
        };
        auto fcb_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_gnt_datarate_pacer_cfg),
                0x270,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_gnt_datarate_pacer_cfg", fcb_gnt_datarate_pacer_cfg_prop);
        fld_map_t fcb_gnt_ctlmsg_pacer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_leak_tick_cnt", 1, 12),
            CREATE_ENTRY("fld_base_leak_rate", 13, 12),
            CREATE_ENTRY("fld_admit_lvl_thresh", 25, 24),
            CREATE_ENTRY("fld_update_val", 49, 12),
            CREATE_ENTRY("__rsvd", 61, 3)
        };
        auto fcb_gnt_ctlmsg_pacer_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_gnt_ctlmsg_pacer_cfg),
                0x278,
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
        };
        auto fcb_host_intf0_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf0_gnt_datarate_pacer_cfg),
                    0x280,
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
        };
        auto fcb_host_intf1_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf1_gnt_datarate_pacer_cfg),
                    0x288,
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
        };
        auto fcb_host_intf2_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf2_gnt_datarate_pacer_cfg),
                    0x290,
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
        };
        auto fcb_host_intf3_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf3_gnt_datarate_pacer_cfg),
                    0x298,
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
        };
        auto fcb_host_intf4_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf4_gnt_datarate_pacer_cfg),
                    0x2A0,
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
        };
        auto fcb_host_intf5_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf5_gnt_datarate_pacer_cfg),
                    0x2A8,
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
        };
        auto fcb_host_intf6_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf6_gnt_datarate_pacer_cfg),
                    0x2B0,
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
        };
        auto fcb_host_intf7_gnt_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_host_intf7_gnt_datarate_pacer_cfg),
                    0x2B8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_host_intf7_gnt_datarate_pacer_cfg", fcb_host_intf7_gnt_datarate_pacer_cfg_prop);
        fld_map_t fcb_dst_timer_ctrl_cfg {
            CREATE_ENTRY("fld_timer_enable", 0, 1),
            CREATE_ENTRY("fld_timer_tdm_cnt", 1, 4),
            CREATE_ENTRY("fld_gnt_timer_tick_cnt", 5, 16),
            CREATE_ENTRY("fld_max_gnt_retry_cnt", 21, 4),
            CREATE_ENTRY("fld_gnt_tov_val", 25, 4),
            CREATE_ENTRY("fld_idle_timer_tick_cnt", 29, 16),
            CREATE_ENTRY("fld_idle_tov_val", 45, 4),
            CREATE_ENTRY("__rsvd", 49, 15)
        };
        auto fcb_dst_timer_ctrl_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fcb_dst_timer_ctrl_cfg),
                                               0x2C0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fcb_0, "fcb_dst_timer_ctrl_cfg", fcb_dst_timer_ctrl_cfg_prop);
        fld_map_t fcb_dst_max_gnt_retry_symptom {
            CREATE_ENTRY("fld_vld", 0, 1),
            CREATE_ENTRY("fld_wu_qid", 1, 14),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto fcb_dst_max_gnt_retry_symptom_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_dst_max_gnt_retry_symptom),
                    0x2D0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_dst_max_gnt_retry_symptom", fcb_dst_max_gnt_retry_symptom_prop);
        fld_map_t fcb_dst_gbl_pbof_blks_thresh_cfg {
            CREATE_ENTRY("fld_xon_thresh", 0, 16),
            CREATE_ENTRY("fld_xoff_thresh", 16, 16),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcb_dst_gbl_pbof_blks_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_dst_gbl_pbof_blks_thresh_cfg),
                    0x2D8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fcb_0, "fcb_dst_gbl_pbof_blks_thresh_cfg", fcb_dst_gbl_pbof_blks_thresh_cfg_prop);
        fld_map_t fcb_src_queue_cmd_fifo_dhs {
            CREATE_ENTRY("fld_cmd", 0, 3),
            CREATE_ENTRY("fld_wu_qid", 3, 14),
            CREATE_ENTRY("fld_gph_vld", 17, 1),
            CREATE_ENTRY("fld_gph_vec", 18, 128),
            CREATE_ENTRY("__rsvd", 146, 46)
        };
        auto fcb_src_queue_cmd_fifo_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_src_queue_cmd_fifo_dhs),
                0x2F0,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_src_queue_cmd_fifo_dhs", fcb_src_queue_cmd_fifo_dhs_prop);
        fld_map_t fcb_src_flush_all_cmd_cfg {
            CREATE_ENTRY("fld_cmd", 0, 1),
            CREATE_ENTRY("fld_pending_status", 1, 1),
            CREATE_ENTRY("fld_done_status", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto fcb_src_flush_all_cmd_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_src_flush_all_cmd_cfg),
                0x320,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_src_flush_all_cmd_cfg", fcb_src_flush_all_cmd_cfg_prop);
        fld_map_t fcb_dst_queue_cmd_fifo_dhs {
            CREATE_ENTRY("cmd", 0, 3),
            CREATE_ENTRY("wu_qid", 3, 14),
            CREATE_ENTRY("gph_vld", 17, 1),
            CREATE_ENTRY("gph_vec", 18, 128),
            CREATE_ENTRY("__rsvd", 146, 46)
        };
        auto fcb_dst_queue_cmd_fifo_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_dst_queue_cmd_fifo_dhs),
                0x328,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_dst_queue_cmd_fifo_dhs", fcb_dst_queue_cmd_fifo_dhs_prop);
        fld_map_t fcb_dst_flush_all_cmd_cfg {
            CREATE_ENTRY("fld_cmd", 0, 1),
            CREATE_ENTRY("fld_pending_status", 1, 1),
            CREATE_ENTRY("fld_done_status", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto fcb_dst_flush_all_cmd_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_dst_flush_all_cmd_cfg),
                0x350,
                CSR_TYPE::REG,
                1);
        add_csr(fcb_0, "fcb_dst_flush_all_cmd_cfg", fcb_dst_flush_all_cmd_cfg_prop);
        fld_map_t fcb_src_trace_fifo_cfg {
            CREATE_ENTRY("fld_trace_enable", 0, 1),
            CREATE_ENTRY("fld_opcode_map", 1, 17),
            CREATE_ENTRY("fld_wu_qid", 18, 14),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcb_src_trace_fifo_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fcb_src_trace_fifo_cfg),
                                               0x360,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fcb_0, "fcb_src_trace_fifo_cfg", fcb_src_trace_fifo_cfg_prop);
        fld_map_t fcb_dst_trace_fifo_cfg {
            CREATE_ENTRY("fld_trace_enable", 0, 1),
            CREATE_ENTRY("fld_opcode_map", 1, 11),
            CREATE_ENTRY("fld_wu_qid", 12, 14),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto fcb_dst_trace_fifo_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fcb_dst_trace_fifo_cfg),
                                               0x388,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fcb_0, "fcb_dst_trace_fifo_cfg", fcb_dst_trace_fifo_cfg_prop);
        fld_map_t fcb_src_nfcp_stream_datarate_pacer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_leak_tick_cnt", 1, 8),
            CREATE_ENTRY("fld_base_leak_rate", 9, 16),
            CREATE_ENTRY("fld_admit_lvl_thresh", 25, 15),
            CREATE_ENTRY("fld_min_thresh", 40, 15),
            CREATE_ENTRY("__rsvd", 55, 9)
        };
        auto fcb_src_nfcp_stream_datarate_pacer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_nfcp_stream_datarate_pacer_cfg),
                    0x400,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_src_nfcp_stream_datarate_pacer_cfg", fcb_src_nfcp_stream_datarate_pacer_cfg_prop);
        fld_map_t fcb_src_queue_cfg_tbl {
            CREATE_ENTRY("fld_unsol_en", 0, 1),
            CREATE_ENTRY("fld_max_req_blk_sz", 1, 8),
            CREATE_ENTRY("fld_max_pending_req_win_sz", 9, 16),
            CREATE_ENTRY("fld_max_deq_sz", 25, 8),
            CREATE_ENTRY("fld_max_unsol_deq_sz", 33, 8),
            CREATE_ENTRY("fld_max_unsol_win_sz", 41, 7),
            CREATE_ENTRY("fld_max_gnt_win_sz", 48, 16)
        };
        auto fcb_src_queue_cfg_tbl_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fcb_src_queue_cfg_tbl),
                                              0xC00,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(fcb_0, "fcb_src_queue_cfg_tbl", fcb_src_queue_cfg_tbl_prop);
        fld_map_t fcb_ncv_thresh_tbl {
            CREATE_ENTRY("fld_entry0", 0, 20),
            CREATE_ENTRY("fld_entry1", 20, 20),
            CREATE_ENTRY("fld_entry2", 40, 20),
            CREATE_ENTRY("fld_entry3", 60, 20),
            CREATE_ENTRY("fld_entry4", 80, 20),
            CREATE_ENTRY("fld_entry5", 100, 20),
            CREATE_ENTRY("fld_entry6", 120, 20),
            CREATE_ENTRY("fld_entry7", 140, 20),
            CREATE_ENTRY("fld_entry8", 160, 20),
            CREATE_ENTRY("fld_entry9", 180, 20),
            CREATE_ENTRY("fld_entry10", 200, 20),
            CREATE_ENTRY("fld_entry11", 220, 20),
            CREATE_ENTRY("fld_entry12", 240, 20),
            CREATE_ENTRY("fld_entry13", 260, 20),
            CREATE_ENTRY("fld_entry14", 280, 20),
            CREATE_ENTRY("__rsvd", 300, 20)
        };
        auto fcb_ncv_thresh_tbl_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fcb_ncv_thresh_tbl),
                                           0x1C00,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fcb_0, "fcb_ncv_thresh_tbl", fcb_ncv_thresh_tbl_prop);
        fld_map_t fcb_scale_dn_fact_lkup_tbl {
            CREATE_ENTRY("fld_entry0", 0, 4),
            CREATE_ENTRY("fld_entry1", 4, 4),
            CREATE_ENTRY("fld_entry2", 8, 4),
            CREATE_ENTRY("fld_entry3", 12, 4),
            CREATE_ENTRY("fld_entry4", 16, 4),
            CREATE_ENTRY("fld_entry5", 20, 4),
            CREATE_ENTRY("fld_entry6", 24, 4),
            CREATE_ENTRY("fld_entry7", 28, 4),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcb_scale_dn_fact_lkup_tbl_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_scale_dn_fact_lkup_tbl),
                0xBC00,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_scale_dn_fact_lkup_tbl", fcb_scale_dn_fact_lkup_tbl_prop);
        fld_map_t fcb_dst_queue_cfg_tbl {
            CREATE_ENTRY("fld_max_gnt_blk_sz", 0, 8),
            CREATE_ENTRY("fld_max_pending_gnt_win_sz", 8, 16),
            CREATE_ENTRY("fld_max_req_win_sz", 24, 16),
            CREATE_ENTRY("__rsvd", 40, 24)
        };
        auto fcb_dst_queue_cfg_tbl_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fcb_dst_queue_cfg_tbl),
                                              0xC400,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(fcb_0, "fcb_dst_queue_cfg_tbl", fcb_dst_queue_cfg_tbl_prop);
        fld_map_t fcb_src_pipe_sch_dbg_probe_dhs {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fcb_src_pipe_sch_dbg_probe_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_pipe_sch_dbg_probe_dhs),
                    0xCC00,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_src_pipe_sch_dbg_probe_dhs", fcb_src_pipe_sch_dbg_probe_dhs_prop);
        fld_map_t fcb_src_proc_pipe_dbg_probe_dhs {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fcb_src_proc_pipe_dbg_probe_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_proc_pipe_dbg_probe_dhs),
                    0xCE00,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_src_proc_pipe_dbg_probe_dhs", fcb_src_proc_pipe_dbg_probe_dhs_prop);
        fld_map_t fcb_src_proc_pipe_stats_cntr {
            CREATE_ENTRY("fld_count", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto fcb_src_proc_pipe_stats_cntr_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_proc_pipe_stats_cntr),
                    0xD000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_src_proc_pipe_stats_cntr", fcb_src_proc_pipe_stats_cntr_prop);
        fld_map_t fcb_dst_pipe_sch_dbg_probe_dhs {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fcb_dst_pipe_sch_dbg_probe_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_dst_pipe_sch_dbg_probe_dhs),
                    0xD800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_dst_pipe_sch_dbg_probe_dhs", fcb_dst_pipe_sch_dbg_probe_dhs_prop);
        fld_map_t fcb_dst_proc_pipe_dbg_probe_dhs {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fcb_dst_proc_pipe_dbg_probe_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_dst_proc_pipe_dbg_probe_dhs),
                    0xDA00,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_dst_proc_pipe_dbg_probe_dhs", fcb_dst_proc_pipe_dbg_probe_dhs_prop);
        fld_map_t fcb_dst_proc_pipe_stats_cntr {
            CREATE_ENTRY("fld_count", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto fcb_dst_proc_pipe_stats_cntr_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_dst_proc_pipe_stats_cntr),
                    0xDC00,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_dst_proc_pipe_stats_cntr", fcb_dst_proc_pipe_stats_cntr_prop);
        fld_map_t fcb_src_cfg_role_tbl_mem_dhs {
            CREATE_ENTRY("fld_entry0_spray_config", 0, 2),
            CREATE_ENTRY("fld_entry0_role", 2, 4),
            CREATE_ENTRY("fld_entry0_host_intf", 6, 3),
            CREATE_ENTRY("fld_entry1_spray_config", 9, 2),
            CREATE_ENTRY("fld_entry1_role", 11, 4),
            CREATE_ENTRY("fld_entry1_host_intf", 15, 3),
            CREATE_ENTRY("fld_entry2_spray_config", 18, 2),
            CREATE_ENTRY("fld_entry2_role", 20, 4),
            CREATE_ENTRY("fld_entry2_host_intf", 24, 3),
            CREATE_ENTRY("fld_entry3_spray_config", 27, 2),
            CREATE_ENTRY("fld_entry3_role", 29, 4),
            CREATE_ENTRY("fld_entry3_host_intf", 33, 3),
            CREATE_ENTRY("fld_entry4_spray_config", 36, 2),
            CREATE_ENTRY("fld_entry4_role", 38, 4),
            CREATE_ENTRY("fld_entry4_host_intf", 42, 3),
            CREATE_ENTRY("fld_entry5_spray_config", 45, 2),
            CREATE_ENTRY("fld_entry5_role", 47, 4),
            CREATE_ENTRY("fld_entry5_host_intf", 51, 3),
            CREATE_ENTRY("fld_entry6_spray_config", 54, 2),
            CREATE_ENTRY("fld_entry6_role", 56, 4),
            CREATE_ENTRY("fld_entry6_host_intf", 60, 3),
            CREATE_ENTRY("fld_entry7_spray_config", 63, 2),
            CREATE_ENTRY("fld_entry7_role", 65, 4),
            CREATE_ENTRY("fld_entry7_host_intf", 69, 3),
            CREATE_ENTRY("__rsvd", 72, 56)
        };
        auto fcb_src_cfg_role_tbl_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_cfg_role_tbl_mem_dhs),
                    0x28000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_src_cfg_role_tbl_mem_dhs", fcb_src_cfg_role_tbl_mem_dhs_prop);
        fld_map_t fcb_src_queue_ctx_mem_dhs {
            CREATE_ENTRY("fld_max_win", 0, 1),
            CREATE_ENTRY("fld_unsol", 1, 1),
            CREATE_ENTRY("fld_req_schd", 2, 1),
            CREATE_ENTRY("fld_pkt_schd", 3, 1),
            CREATE_ENTRY("fld_resrvd", 4, 1),
            CREATE_ENTRY("fld_state", 5, 1),
            CREATE_ENTRY("fld_qbn", 6, 24),
            CREATE_ENTRY("fld_rbn", 30, 24),
            CREATE_ENTRY("fld_gbn", 54, 16),
            CREATE_ENTRY("fld_dbn", 70, 24),
            CREATE_ENTRY("fld_ovf_blks", 94, 9),
            CREATE_ENTRY("__rsvd", 103, 25)
        };
        auto fcb_src_queue_ctx_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_src_queue_ctx_mem_dhs),
                0xC0000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_src_queue_ctx_mem_dhs", fcb_src_queue_ctx_mem_dhs_prop);
        fld_map_t fcb_src_flow_wt_tbl_mem_dhs {
            CREATE_ENTRY("fld_mantissa", 0, 4),
            CREATE_ENTRY("fld_exponent", 4, 4),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcb_src_flow_wt_tbl_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_src_flow_wt_tbl_mem_dhs),
                0x4C0000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_src_flow_wt_tbl_mem_dhs", fcb_src_flow_wt_tbl_mem_dhs_prop);
        fld_map_t fcb_scale_dn_fact_tbl_mem_dhs {
            CREATE_ENTRY("entry0", 0, 4),
            CREATE_ENTRY("entry1", 4, 4),
            CREATE_ENTRY("entry2", 8, 4),
            CREATE_ENTRY("entry3", 12, 4),
            CREATE_ENTRY("entry4", 16, 4),
            CREATE_ENTRY("entry5", 20, 4),
            CREATE_ENTRY("entry6", 24, 4),
            CREATE_ENTRY("entry7", 28, 4),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcb_scale_dn_fact_tbl_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_scale_dn_fact_tbl_mem_dhs),
                    0x5C0000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_scale_dn_fact_tbl_mem_dhs", fcb_scale_dn_fact_tbl_mem_dhs_prop);
        fld_map_t fcb_src_timer_mem_dhs {
            CREATE_ENTRY("fld_entry0_state", 0, 2),
            CREATE_ENTRY("fld_entry0_tstmp", 2, 4),
            CREATE_ENTRY("fld_entry0_rtry_cnt", 6, 4),
            CREATE_ENTRY("fld_entry1_state", 10, 2),
            CREATE_ENTRY("fld_entry1_tstmp", 12, 4),
            CREATE_ENTRY("fld_entry1_rtry_cnt", 16, 4),
            CREATE_ENTRY("fld_entry2_state", 20, 2),
            CREATE_ENTRY("fld_entry2_tstmp", 22, 4),
            CREATE_ENTRY("fld_entry2_rtry_cnt", 26, 4),
            CREATE_ENTRY("fld_entry3_state", 30, 2),
            CREATE_ENTRY("fld_entry3_tstmp", 32, 4),
            CREATE_ENTRY("fld_entry3_rtry_cnt", 36, 4),
            CREATE_ENTRY("fld_entry4_state", 40, 2),
            CREATE_ENTRY("fld_entry4_tstmp", 42, 4),
            CREATE_ENTRY("fld_entry4_rtry_cnt", 46, 4),
            CREATE_ENTRY("fld_entry5_state", 50, 2),
            CREATE_ENTRY("fld_entry5_tstmp", 52, 4),
            CREATE_ENTRY("fld_entry5_rtry_cnt", 56, 4),
            CREATE_ENTRY("fld_entry6_state", 60, 2),
            CREATE_ENTRY("fld_entry6_tstmp", 62, 4),
            CREATE_ENTRY("fld_entry6_rtry_cnt", 66, 4),
            CREATE_ENTRY("fld_entry7_state", 70, 2),
            CREATE_ENTRY("fld_entry7_tstmp", 72, 4),
            CREATE_ENTRY("fld_entry7_rtry_cnt", 76, 4),
            CREATE_ENTRY("__rsvd", 80, 48)
        };
        auto fcb_src_timer_mem_dhs_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fcb_src_timer_mem_dhs),
                                              0x5E0000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(fcb_0, "fcb_src_timer_mem_dhs", fcb_src_timer_mem_dhs_prop);
        fld_map_t fcb_src_impairment_tbl_mem_dhs {
            CREATE_ENTRY("fld_entry0", 0, 8),
            CREATE_ENTRY("fld_entry1", 8, 8),
            CREATE_ENTRY("fld_entry2", 16, 8),
            CREATE_ENTRY("fld_entry3", 24, 8),
            CREATE_ENTRY("fld_entry4", 32, 8),
            CREATE_ENTRY("fld_entry5", 40, 8),
            CREATE_ENTRY("fld_entry6", 48, 8),
            CREATE_ENTRY("fld_entry7", 56, 8)
        };
        auto fcb_src_impairment_tbl_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_src_impairment_tbl_mem_dhs),
                    0x660000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_src_impairment_tbl_mem_dhs", fcb_src_impairment_tbl_mem_dhs_prop);
        fld_map_t fcb_req_sch_llist_mem_dhs {
            CREATE_ENTRY("fld_llptr", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fcb_req_sch_llist_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_req_sch_llist_mem_dhs),
                0x680000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_req_sch_llist_mem_dhs", fcb_req_sch_llist_mem_dhs_prop);
        fld_map_t fcb_pkt_sch_llist_mem_dhs {
            CREATE_ENTRY("fld_llptr", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fcb_pkt_sch_llist_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_pkt_sch_llist_mem_dhs),
                0x780000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_pkt_sch_llist_mem_dhs", fcb_pkt_sch_llist_mem_dhs_prop);
        fld_map_t fcb_ncv_seqncer_mem_dhs {
            CREATE_ENTRY("fld_data", 0, 128)
        };
        auto fcb_ncv_seqncer_mem_dhs_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fcb_ncv_seqncer_mem_dhs),
                                                0x880000,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(fcb_0, "fcb_ncv_seqncer_mem_dhs", fcb_ncv_seqncer_mem_dhs_prop);
        fld_map_t fcb_ncv_status_tbl_mem_dhs {
            CREATE_ENTRY("fld_entry0", 0, 4),
            CREATE_ENTRY("fld_entry1", 4, 4),
            CREATE_ENTRY("fld_entry2", 8, 4),
            CREATE_ENTRY("fld_entry3", 12, 4),
            CREATE_ENTRY("fld_entry4", 16, 4),
            CREATE_ENTRY("fld_entry5", 20, 4),
            CREATE_ENTRY("fld_entry6", 24, 4),
            CREATE_ENTRY("fld_entry7", 28, 4),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcb_ncv_status_tbl_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_ncv_status_tbl_mem_dhs),
                0x888000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_ncv_status_tbl_mem_dhs", fcb_ncv_status_tbl_mem_dhs_prop);
        fld_map_t fcb_dst_cfg_role_tbl_mem_dhs {
            CREATE_ENTRY("fld_entry0_enable", 0, 1),
            CREATE_ENTRY("fld_entry0_role", 1, 4),
            CREATE_ENTRY("fld_entry0_host_intf", 5, 3),
            CREATE_ENTRY("fld_entry1_enable", 8, 1),
            CREATE_ENTRY("fld_entry1_role", 9, 4),
            CREATE_ENTRY("fld_entry1_host_intf", 13, 3),
            CREATE_ENTRY("fld_entry2_enable", 16, 1),
            CREATE_ENTRY("fld_entry2_role", 17, 4),
            CREATE_ENTRY("fld_entry2_host_intf", 21, 3),
            CREATE_ENTRY("fld_entry3_enable", 24, 1),
            CREATE_ENTRY("fld_entry3_role", 25, 4),
            CREATE_ENTRY("fld_entry3_host_intf", 29, 3),
            CREATE_ENTRY("fld_entry4_enable", 32, 1),
            CREATE_ENTRY("fld_entry4_role", 33, 4),
            CREATE_ENTRY("fld_entry4_host_intf", 37, 3),
            CREATE_ENTRY("fld_entry5_enable", 40, 1),
            CREATE_ENTRY("fld_entry5_role", 41, 4),
            CREATE_ENTRY("fld_entry5_host_intf", 45, 3),
            CREATE_ENTRY("fld_entry6_enable", 48, 1),
            CREATE_ENTRY("fld_entry6_role", 49, 4),
            CREATE_ENTRY("fld_entry6_host_intf", 53, 3),
            CREATE_ENTRY("fld_entry7_enable", 56, 1),
            CREATE_ENTRY("fld_entry7_role", 57, 4),
            CREATE_ENTRY("fld_entry7_host_intf", 61, 3)
        };
        auto fcb_dst_cfg_role_tbl_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_dst_cfg_role_tbl_mem_dhs),
                    0x8A8000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_dst_cfg_role_tbl_mem_dhs", fcb_dst_cfg_role_tbl_mem_dhs_prop);
        fld_map_t fcb_dst_timer_mem_dhs {
            CREATE_ENTRY("fld_entry0_state", 0, 2),
            CREATE_ENTRY("fld_entry0_tstmp", 2, 4),
            CREATE_ENTRY("fld_entry0_rtry_cnt", 6, 4),
            CREATE_ENTRY("fld_entry1_state", 10, 2),
            CREATE_ENTRY("fld_entry1_tstmp", 12, 4),
            CREATE_ENTRY("fld_entry1_rtry_cnt", 16, 4),
            CREATE_ENTRY("fld_entry2_state", 20, 2),
            CREATE_ENTRY("fld_entry2_tstmp", 22, 4),
            CREATE_ENTRY("fld_entry2_rtry_cnt", 26, 4),
            CREATE_ENTRY("fld_entry3_state", 30, 2),
            CREATE_ENTRY("fld_entry3_tstmp", 32, 4),
            CREATE_ENTRY("fld_entry3_rtry_cnt", 36, 4),
            CREATE_ENTRY("fld_entry4_state", 40, 2),
            CREATE_ENTRY("fld_entry4_tstmp", 42, 4),
            CREATE_ENTRY("fld_entry4_rtry_cnt", 46, 4),
            CREATE_ENTRY("fld_entry5_state", 50, 2),
            CREATE_ENTRY("fld_entry5_tstmp", 52, 4),
            CREATE_ENTRY("fld_entry5_rtry_cnt", 56, 4),
            CREATE_ENTRY("fld_entry6_state", 60, 2),
            CREATE_ENTRY("fld_entry6_tstmp", 62, 4),
            CREATE_ENTRY("fld_entry6_rtry_cnt", 66, 4),
            CREATE_ENTRY("fld_entry7_state", 70, 2),
            CREATE_ENTRY("fld_entry7_tstmp", 72, 4),
            CREATE_ENTRY("fld_entry7_rtry_cnt", 76, 4),
            CREATE_ENTRY("__rsvd", 80, 48)
        };
        auto fcb_dst_timer_mem_dhs_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fcb_dst_timer_mem_dhs),
                                              0x8C8000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(fcb_0, "fcb_dst_timer_mem_dhs", fcb_dst_timer_mem_dhs_prop);
        fld_map_t fcb_dst_queue_ctx_mem_dhs {
            CREATE_ENTRY("fld_max_win", 0, 1),
            CREATE_ENTRY("fld_gnt_schd", 1, 1),
            CREATE_ENTRY("fld_resrvd", 2, 1),
            CREATE_ENTRY("fld_state", 3, 1),
            CREATE_ENTRY("fld_rbn", 4, 16),
            CREATE_ENTRY("fld_gbn", 20, 16),
            CREATE_ENTRY("fld_dbn", 36, 16),
            CREATE_ENTRY("__rsvd", 52, 12)
        };
        auto fcb_dst_queue_ctx_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_dst_queue_ctx_mem_dhs),
                0x960000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_dst_queue_ctx_mem_dhs", fcb_dst_queue_ctx_mem_dhs_prop);
        fld_map_t fcb_gnt_sch_ctx_mem_dhs {
            CREATE_ENTRY("fld_state", 0, 1),
            CREATE_ENTRY("fld_refresh_flag", 1, 1),
            CREATE_ENTRY("fld_reserved", 2, 2),
            CREATE_ENTRY("fld_dwrr_crdt", 4, 18),
            CREATE_ENTRY("fld_refresh_wt", 22, 8),
            CREATE_ENTRY("fld_lat_wt", 30, 8),
            CREATE_ENTRY("__rsvd", 38, 26)
        };
        auto fcb_gnt_sch_ctx_mem_dhs_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fcb_gnt_sch_ctx_mem_dhs),
                                                0xA60000,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(fcb_0, "fcb_gnt_sch_ctx_mem_dhs", fcb_gnt_sch_ctx_mem_dhs_prop);
        fld_map_t fcb_gnt_sch_llist_mem_dhs {
            CREATE_ENTRY("fld_llptr", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto fcb_gnt_sch_llist_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_gnt_sch_llist_mem_dhs),
                0xB60000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_gnt_sch_llist_mem_dhs", fcb_gnt_sch_llist_mem_dhs_prop);
        fld_map_t fcb_dst_flow_wt_tbl_mem_dhs {
            CREATE_ENTRY("fld_entry0mantissa", 0, 4),
            CREATE_ENTRY("fld_entry0exponent", 4, 4),
            CREATE_ENTRY("fld_entry1mantissa", 8, 4),
            CREATE_ENTRY("fld_entry1exponent", 12, 4),
            CREATE_ENTRY("fld_entry2mantissa", 16, 4),
            CREATE_ENTRY("fld_entry2exponent", 20, 4),
            CREATE_ENTRY("fld_entry3mantissa", 24, 4),
            CREATE_ENTRY("fld_entry3exponent", 28, 4),
            CREATE_ENTRY("fld_entry4mantissa", 32, 4),
            CREATE_ENTRY("fld_entry4exponent", 36, 4),
            CREATE_ENTRY("fld_entry5mantissa", 40, 4),
            CREATE_ENTRY("fld_entry5exponent", 44, 4),
            CREATE_ENTRY("fld_entry6mantissa", 48, 4),
            CREATE_ENTRY("fld_entry6exponent", 52, 4),
            CREATE_ENTRY("fld_entry7mantissa", 56, 4),
            CREATE_ENTRY("fld_entry7exponent", 60, 4)
        };
        auto fcb_dst_flow_wt_tbl_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_dst_flow_wt_tbl_mem_dhs),
                0xC60000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_dst_flow_wt_tbl_mem_dhs", fcb_dst_flow_wt_tbl_mem_dhs_prop);
        fld_map_t fcb_impairment_fact_tbl_dhs {
            CREATE_ENTRY("fld_entry0", 0, 8),
            CREATE_ENTRY("fld_entry1", 8, 8),
            CREATE_ENTRY("fld_entry2", 16, 8),
            CREATE_ENTRY("fld_entry3", 24, 8),
            CREATE_ENTRY("fld_entry4", 32, 8),
            CREATE_ENTRY("fld_entry5", 40, 8),
            CREATE_ENTRY("fld_entry6", 48, 8),
            CREATE_ENTRY("fld_entry7", 56, 8)
        };
        auto fcb_impairment_fact_tbl_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_impairment_fact_tbl_dhs),
                0xC80000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_impairment_fact_tbl_dhs", fcb_impairment_fact_tbl_dhs_prop);
        fld_map_t fcb_src_stats_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_packet_cnt", 35, 29)
        };
        auto fcb_src_stats_cntr_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_src_stats_cntr_mem_dhs),
                0xCA0000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_src_stats_cntr_mem_dhs", fcb_src_stats_cntr_mem_dhs_prop);
        fld_map_t fcb_dst_stats_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_packet_cnt", 35, 29)
        };
        auto fcb_dst_stats_cntr_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fcb_dst_stats_cntr_mem_dhs),
                0xDA0000,
                CSR_TYPE::TBL,
                1);
        add_csr(fcb_0, "fcb_dst_stats_cntr_mem_dhs", fcb_dst_stats_cntr_mem_dhs_prop);
        fld_map_t fcb_gnt_sch_deq_updt_corr_mem_dhs {
            CREATE_ENTRY("fld_updt_accum_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcb_gnt_sch_deq_updt_corr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fcb_gnt_sch_deq_updt_corr_mem_dhs),
                    0xEA0000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fcb_0, "fcb_gnt_sch_deq_updt_corr_mem_dhs", fcb_gnt_sch_deq_updt_corr_mem_dhs_prop);
// END fcb
    }
    {
// BEGIN nwqm
        auto nwqm_0 = nu_rng[0].add_an({"nwqm"}, 0x8000000, 1, 0x0);
        fld_map_t nwqm_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nwqm_timeout_thresh_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nwqm_timeout_thresh_cfg),
                                                0x0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(nwqm_0, "nwqm_timeout_thresh_cfg", nwqm_timeout_thresh_cfg_prop);
        fld_map_t nwqm_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nwqm_timeout_clr_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nwqm_timeout_clr),
                                         0x10,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nwqm_0, "nwqm_timeout_clr", nwqm_timeout_clr_prop);
        fld_map_t nwqm_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nwqm_spare_pio_prop = csr_prop_t(
                                       std::make_shared<csr_s>(nwqm_spare_pio),
                                       0x70,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(nwqm_0, "nwqm_spare_pio", nwqm_spare_pio_prop);
        fld_map_t nwqm_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nwqm_scratchpad_prop = csr_prop_t(
                                        std::make_shared<csr_s>(nwqm_scratchpad),
                                        0x78,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(nwqm_0, "nwqm_scratchpad", nwqm_scratchpad_prop);
        fld_map_t nwqm_cfg {
            CREATE_ENTRY("nq_drop_wu_crd_inc_ena", 0, 1),
            CREATE_ENTRY("pbuf_max_qid", 1, 15),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto nwqm_cfg_prop = csr_prop_t(
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
        };
        auto nwqm_pc_to_if_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_pc_to_if_cfg),
                                          0x88,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nwqm_0, "nwqm_pc_to_if_cfg", nwqm_pc_to_if_cfg_prop);
        fld_map_t nwqm_sram_init {
            CREATE_ENTRY("start", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nwqm_sram_init_prop = csr_prop_t(
                                       std::make_shared<csr_s>(nwqm_sram_init),
                                       0x90,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(nwqm_0, "nwqm_sram_init", nwqm_sram_init_prop);
        fld_map_t nwqm_wu_crd_cfg {
            CREATE_ENTRY("alloc_dry_th", 0, 16),
            CREATE_ENTRY("efp_hi_th", 16, 16),
            CREATE_ENTRY("efp_lo_th", 32, 16),
            CREATE_ENTRY("efp_send_th", 48, 16)
        };
        auto nwqm_wu_crd_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(nwqm_wu_crd_cfg),
                                        0xA0,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(nwqm_0, "nwqm_wu_crd_cfg", nwqm_wu_crd_cfg_prop);
        fld_map_t nwqm_wu_index_cfg {
            CREATE_ENTRY("drain_bitalloc", 0, 8),
            CREATE_ENTRY("wm_ena", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto nwqm_wu_index_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_wu_index_cfg),
                                          0xA8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nwqm_0, "nwqm_wu_index_cfg", nwqm_wu_index_cfg_prop);
        fld_map_t nwqm_wu_crd_cnt_ncv_th {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto nwqm_wu_crd_cnt_ncv_th_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nwqm_wu_crd_cnt_ncv_th),
                                               0xB0,
                                               CSR_TYPE::REG,
                                               15);
        add_csr(nwqm_0, "nwqm_wu_crd_cnt_ncv_th", nwqm_wu_crd_cnt_ncv_th_prop);
        fld_map_t nwqm_wu_crd_cnt_min {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto nwqm_wu_crd_cnt_min_prop = csr_prop_t(
                                            std::make_shared<csr_s>(nwqm_wu_crd_cnt_min),
                                            0x130,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(nwqm_0, "nwqm_wu_crd_cnt_min", nwqm_wu_crd_cnt_min_prop);
        fld_map_t nwqm_wu_crd_cnt_adj {
            CREATE_ENTRY("val", 0, 17),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto nwqm_wu_crd_cnt_adj_prop = csr_prop_t(
                                            std::make_shared<csr_s>(nwqm_wu_crd_cnt_adj),
                                            0x138,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(nwqm_0, "nwqm_wu_crd_cnt_adj", nwqm_wu_crd_cnt_adj_prop);
        fld_map_t nwqm_wu_crd_index_pf_misc_cfg {
            CREATE_ENTRY("dgid", 0, 5),
            CREATE_ENTRY("dlid", 5, 5),
            CREATE_ENTRY("crd_alloc_if", 10, 2),
            CREATE_ENTRY("crd_dealloc_if", 12, 2),
            CREATE_ENTRY("index_alloc_if", 14, 2),
            CREATE_ENTRY("index_dealloc_if", 16, 2),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto nwqm_wu_crd_index_pf_misc_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_crd_index_pf_misc_cfg),
                    0x190,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_crd_index_pf_misc_cfg", nwqm_wu_crd_index_pf_misc_cfg_prop);
        fld_map_t nwqm_pbuf_free_cnt_min {
            CREATE_ENTRY("val", 0, 11),
            CREATE_ENTRY("__rsvd", 11, 53)
        };
        auto nwqm_pbuf_free_cnt_min_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nwqm_pbuf_free_cnt_min),
                                               0x1A0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nwqm_0, "nwqm_pbuf_free_cnt_min", nwqm_pbuf_free_cnt_min_prop);
        fld_map_t nwqm_pbuf_free_cnt_adj {
            CREATE_ENTRY("val", 0, 12),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto nwqm_pbuf_free_cnt_adj_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nwqm_pbuf_free_cnt_adj),
                                               0x1A8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nwqm_0, "nwqm_pbuf_free_cnt_adj", nwqm_pbuf_free_cnt_adj_prop);
        fld_map_t nwqm_wu_crd_pf_cfg {
            CREATE_ENTRY("dealloc_th", 0, 10),
            CREATE_ENTRY("avg_th", 10, 10),
            CREATE_ENTRY("alloc_th", 20, 10),
            CREATE_ENTRY("max_alloc_cnt", 30, 10),
            CREATE_ENTRY("dry_wait_timer", 40, 10),
            CREATE_ENTRY("__rsvd", 50, 14)
        };
        auto nwqm_wu_crd_pf_cfg_prop = csr_prop_t(
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
        };
        auto nwqm_wu_index_pf_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nwqm_wu_index_pf_cfg),
                                             0x1B8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nwqm_0, "nwqm_wu_index_pf_cfg", nwqm_wu_index_pf_cfg_prop);
        fld_map_t nwqm_ipf_wu_index_pf_cnt_adj {
            CREATE_ENTRY("val", 0, 12),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto nwqm_ipf_wu_index_pf_cnt_adj_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_ipf_wu_index_pf_cnt_adj),
                    0x1C8,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_ipf_wu_index_pf_cnt_adj", nwqm_ipf_wu_index_pf_cnt_adj_prop);
        fld_map_t nwqm_ipf_wu_index_pf_wr_ptr_adj {
            CREATE_ENTRY("val", 0, 10),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto nwqm_ipf_wu_index_pf_wr_ptr_adj_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_ipf_wu_index_pf_wr_ptr_adj),
                    0x1D0,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_ipf_wu_index_pf_wr_ptr_adj", nwqm_ipf_wu_index_pf_wr_ptr_adj_prop);
        fld_map_t nwqm_ipf_wu_index_pf_rd_ptr_adj {
            CREATE_ENTRY("val", 0, 10),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto nwqm_ipf_wu_index_pf_rd_ptr_adj_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_ipf_wu_index_pf_rd_ptr_adj),
                    0x1D8,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_ipf_wu_index_pf_rd_ptr_adj", nwqm_ipf_wu_index_pf_rd_ptr_adj_prop);
        fld_map_t nwqm_stat_cnt_cfg {
            CREATE_ENTRY("sgid_mask", 0, 5),
            CREATE_ENTRY("sgid_match", 5, 5),
            CREATE_ENTRY("slid_mask", 10, 5),
            CREATE_ENTRY("slid_match", 15, 5),
            CREATE_ENTRY("crd_transaction", 20, 1),
            CREATE_ENTRY("index_transaction", 21, 1),
            CREATE_ENTRY("sni_sop", 22, 1),
            CREATE_ENTRY("sne_sop", 23, 1),
            CREATE_ENTRY("dne_sop", 24, 1),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto nwqm_stat_cnt_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_stat_cnt_cfg),
                                          0x218,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nwqm_0, "nwqm_stat_cnt_cfg", nwqm_stat_cnt_cfg_prop);
        fld_map_t nwqm_sni_stat_cnt_ena {
            CREATE_ENTRY("if2_sn_resp", 0, 1),
            CREATE_ENTRY("if1_sn_resp", 1, 1),
            CREATE_ENTRY("if0_sn_resp", 2, 1),
            CREATE_ENTRY("if2_sn_req", 3, 1),
            CREATE_ENTRY("if1_sn_req", 4, 1),
            CREATE_ENTRY("if0_sn_req", 5, 1),
            CREATE_ENTRY("if2_wu_lo", 6, 1),
            CREATE_ENTRY("if1_wu_lo", 7, 1),
            CREATE_ENTRY("if0_wu_lo", 8, 1),
            CREATE_ENTRY("if2_wu_hi", 9, 1),
            CREATE_ENTRY("if1_wu_hi", 10, 1),
            CREATE_ENTRY("if0_wu_hi", 11, 1),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto nwqm_sni_stat_cnt_ena_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nwqm_sni_stat_cnt_ena),
                                              0x220,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(nwqm_0, "nwqm_sni_stat_cnt_ena", nwqm_sni_stat_cnt_ena_prop);
        fld_map_t nwqm_sni_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_sni_stat_cnt_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_sni_stat_cnt),
                                          0x228,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nwqm_0, "nwqm_sni_stat_cnt", nwqm_sni_stat_cnt_prop);
        fld_map_t nwqm_sne_stat_cnt_ena {
            CREATE_ENTRY("if2_sn_resp", 0, 1),
            CREATE_ENTRY("if1_sn_resp", 1, 1),
            CREATE_ENTRY("if0_sn_resp", 2, 1),
            CREATE_ENTRY("if2_sn_req", 3, 1),
            CREATE_ENTRY("if1_sn_req", 4, 1),
            CREATE_ENTRY("if0_sn_req", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto nwqm_sne_stat_cnt_ena_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nwqm_sne_stat_cnt_ena),
                                              0x230,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(nwqm_0, "nwqm_sne_stat_cnt_ena", nwqm_sne_stat_cnt_ena_prop);
        fld_map_t nwqm_sne_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_sne_stat_cnt_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_sne_stat_cnt),
                                          0x238,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nwqm_0, "nwqm_sne_stat_cnt", nwqm_sne_stat_cnt_prop);
        fld_map_t nwqm_dne_stat_cnt_ena {
            CREATE_ENTRY("if2_wu", 0, 1),
            CREATE_ENTRY("if1_wu", 1, 1),
            CREATE_ENTRY("if0_wu", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto nwqm_dne_stat_cnt_ena_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nwqm_dne_stat_cnt_ena),
                                              0x240,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(nwqm_0, "nwqm_dne_stat_cnt_ena", nwqm_dne_stat_cnt_ena_prop);
        fld_map_t nwqm_dne_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_dne_stat_cnt_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_dne_stat_cnt),
                                          0x248,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nwqm_0, "nwqm_dne_stat_cnt", nwqm_dne_stat_cnt_prop);
        fld_map_t nwqm_misc_0_stat_cnt_ena {
            CREATE_ENTRY("tag_from_etp_if2", 0, 1),
            CREATE_ENTRY("tag_from_etp_if1", 1, 1),
            CREATE_ENTRY("tag_from_etp_if0", 2, 1),
            CREATE_ENTRY("wu_to_etp_if2", 3, 1),
            CREATE_ENTRY("wu_to_etp_if1", 4, 1),
            CREATE_ENTRY("wu_to_etp_if0", 5, 1),
            CREATE_ENTRY("dq_rd_wbuf", 6, 1),
            CREATE_ENTRY("dq_rd_pbuf", 7, 1),
            CREATE_ENTRY("dq_rd_to_sne_if2", 8, 1),
            CREATE_ENTRY("dq_rd_to_sne_if1", 9, 1),
            CREATE_ENTRY("dq_rd_to_sne_if0", 10, 1),
            CREATE_ENTRY("dq_to_fcb", 11, 1),
            CREATE_ENTRY("dq_from_fcb_if2", 12, 1),
            CREATE_ENTRY("dq_from_fcb_if1", 13, 1),
            CREATE_ENTRY("dq_from_fcb_if0", 14, 1),
            CREATE_ENTRY("nq_to_wbuf", 15, 1),
            CREATE_ENTRY("nq_to_pbuf", 16, 1),
            CREATE_ENTRY("nq_to_fcb", 17, 1),
            CREATE_ENTRY("nq_from_sni", 18, 1),
            CREATE_ENTRY("wu_to_fae", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto nwqm_misc_0_stat_cnt_ena_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_misc_0_stat_cnt_ena),
                0x250,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_misc_0_stat_cnt_ena", nwqm_misc_0_stat_cnt_ena_prop);
        fld_map_t nwqm_misc_0_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_misc_0_stat_cnt_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nwqm_misc_0_stat_cnt),
                                             0x258,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nwqm_0, "nwqm_misc_0_stat_cnt", nwqm_misc_0_stat_cnt_prop);
        fld_map_t nwqm_misc_1_stat_cnt_ena {
            CREATE_ENTRY("tag_from_etp_if2", 0, 1),
            CREATE_ENTRY("tag_from_etp_if1", 1, 1),
            CREATE_ENTRY("tag_from_etp_if0", 2, 1),
            CREATE_ENTRY("wu_to_etp_if2", 3, 1),
            CREATE_ENTRY("wu_to_etp_if1", 4, 1),
            CREATE_ENTRY("wu_to_etp_if0", 5, 1),
            CREATE_ENTRY("dq_rd_wbuf", 6, 1),
            CREATE_ENTRY("dq_rd_pbuf", 7, 1),
            CREATE_ENTRY("dq_rd_to_sne_if2", 8, 1),
            CREATE_ENTRY("dq_rd_to_sne_if1", 9, 1),
            CREATE_ENTRY("dq_rd_to_sne_if0", 10, 1),
            CREATE_ENTRY("dq_to_fcb", 11, 1),
            CREATE_ENTRY("dq_from_fcb_if2", 12, 1),
            CREATE_ENTRY("dq_from_fcb_if1", 13, 1),
            CREATE_ENTRY("dq_from_fcb_if0", 14, 1),
            CREATE_ENTRY("nq_to_wbuf", 15, 1),
            CREATE_ENTRY("nq_to_pbuf", 16, 1),
            CREATE_ENTRY("nq_to_fcb", 17, 1),
            CREATE_ENTRY("nq_from_sni", 18, 1),
            CREATE_ENTRY("wu_to_fae", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto nwqm_misc_1_stat_cnt_ena_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_misc_1_stat_cnt_ena),
                0x260,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_misc_1_stat_cnt_ena", nwqm_misc_1_stat_cnt_ena_prop);
        fld_map_t nwqm_misc_1_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_misc_1_stat_cnt_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nwqm_misc_1_stat_cnt),
                                             0x268,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nwqm_0, "nwqm_misc_1_stat_cnt", nwqm_misc_1_stat_cnt_prop);
        fld_map_t nwqm_misc_2_stat_cnt_ena {
            CREATE_ENTRY("tag_from_etp_if2", 0, 1),
            CREATE_ENTRY("tag_from_etp_if1", 1, 1),
            CREATE_ENTRY("tag_from_etp_if0", 2, 1),
            CREATE_ENTRY("wu_to_etp_if2", 3, 1),
            CREATE_ENTRY("wu_to_etp_if1", 4, 1),
            CREATE_ENTRY("wu_to_etp_if0", 5, 1),
            CREATE_ENTRY("dq_rd_wbuf", 6, 1),
            CREATE_ENTRY("dq_rd_pbuf", 7, 1),
            CREATE_ENTRY("dq_rd_to_sne_if2", 8, 1),
            CREATE_ENTRY("dq_rd_to_sne_if1", 9, 1),
            CREATE_ENTRY("dq_rd_to_sne_if0", 10, 1),
            CREATE_ENTRY("dq_to_fcb", 11, 1),
            CREATE_ENTRY("dq_from_fcb_if2", 12, 1),
            CREATE_ENTRY("dq_from_fcb_if1", 13, 1),
            CREATE_ENTRY("dq_from_fcb_if0", 14, 1),
            CREATE_ENTRY("nq_to_wbuf", 15, 1),
            CREATE_ENTRY("nq_to_pbuf", 16, 1),
            CREATE_ENTRY("nq_to_fcb", 17, 1),
            CREATE_ENTRY("nq_from_sni", 18, 1),
            CREATE_ENTRY("wu_to_fae", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto nwqm_misc_2_stat_cnt_ena_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_misc_2_stat_cnt_ena),
                0x270,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_misc_2_stat_cnt_ena", nwqm_misc_2_stat_cnt_ena_prop);
        fld_map_t nwqm_misc_2_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_misc_2_stat_cnt_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nwqm_misc_2_stat_cnt),
                                             0x278,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nwqm_0, "nwqm_misc_2_stat_cnt", nwqm_misc_2_stat_cnt_prop);
        fld_map_t nwqm_misc_3_stat_cnt_ena {
            CREATE_ENTRY("tag_from_etp_if2", 0, 1),
            CREATE_ENTRY("tag_from_etp_if1", 1, 1),
            CREATE_ENTRY("tag_from_etp_if0", 2, 1),
            CREATE_ENTRY("wu_to_etp_if2", 3, 1),
            CREATE_ENTRY("wu_to_etp_if1", 4, 1),
            CREATE_ENTRY("wu_to_etp_if0", 5, 1),
            CREATE_ENTRY("dq_rd_wbuf", 6, 1),
            CREATE_ENTRY("dq_rd_pbuf", 7, 1),
            CREATE_ENTRY("dq_rd_to_sne_if2", 8, 1),
            CREATE_ENTRY("dq_rd_to_sne_if1", 9, 1),
            CREATE_ENTRY("dq_rd_to_sne_if0", 10, 1),
            CREATE_ENTRY("dq_to_fcb", 11, 1),
            CREATE_ENTRY("dq_from_fcb_if2", 12, 1),
            CREATE_ENTRY("dq_from_fcb_if1", 13, 1),
            CREATE_ENTRY("dq_from_fcb_if0", 14, 1),
            CREATE_ENTRY("nq_to_wbuf", 15, 1),
            CREATE_ENTRY("nq_to_pbuf", 16, 1),
            CREATE_ENTRY("nq_to_fcb", 17, 1),
            CREATE_ENTRY("nq_from_sni", 18, 1),
            CREATE_ENTRY("wu_to_fae", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto nwqm_misc_3_stat_cnt_ena_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_misc_3_stat_cnt_ena),
                0x280,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_misc_3_stat_cnt_ena", nwqm_misc_3_stat_cnt_ena_prop);
        fld_map_t nwqm_misc_3_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_misc_3_stat_cnt_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nwqm_misc_3_stat_cnt),
                                             0x288,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nwqm_0, "nwqm_misc_3_stat_cnt", nwqm_misc_3_stat_cnt_prop);
        fld_map_t nwqm_wu_crd_inc_stat_cnt_ena {
            CREATE_ENTRY("nq_drop", 0, 1),
            CREATE_ENTRY("wro", 1, 1),
            CREATE_ENTRY("if2_etp", 2, 1),
            CREATE_ENTRY("if1_etp", 3, 1),
            CREATE_ENTRY("if0_etp", 4, 1),
            CREATE_ENTRY("external", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto nwqm_wu_crd_inc_stat_cnt_ena_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_crd_inc_stat_cnt_ena),
                    0x290,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_crd_inc_stat_cnt_ena", nwqm_wu_crd_inc_stat_cnt_ena_prop);
        fld_map_t nwqm_wu_crd_inc_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_wu_crd_inc_stat_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wu_crd_inc_stat_cnt),
                0x298,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_wu_crd_inc_stat_cnt", nwqm_wu_crd_inc_stat_cnt_prop);
        fld_map_t nwqm_wu_crd_dec_stat_cnt_ena {
            CREATE_ENTRY("efp", 0, 1),
            CREATE_ENTRY("external", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nwqm_wu_crd_dec_stat_cnt_ena_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_crd_dec_stat_cnt_ena),
                    0x2A0,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_crd_dec_stat_cnt_ena", nwqm_wu_crd_dec_stat_cnt_ena_prop);
        fld_map_t nwqm_wu_crd_dec_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_wu_crd_dec_stat_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wu_crd_dec_stat_cnt),
                0x2A8,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_wu_crd_dec_stat_cnt", nwqm_wu_crd_dec_stat_cnt_prop);
        fld_map_t nwqm_wu_crd_alloc_req_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_wu_crd_alloc_req_stat_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_crd_alloc_req_stat_cnt),
                    0x2B0,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_crd_alloc_req_stat_cnt", nwqm_wu_crd_alloc_req_stat_cnt_prop);
        fld_map_t nwqm_wu_index_inc_stat_cnt_ena {
            CREATE_ENTRY("rord", 0, 1),
            CREATE_ENTRY("external", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nwqm_wu_index_inc_stat_cnt_ena_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_index_inc_stat_cnt_ena),
                    0x2B8,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_index_inc_stat_cnt_ena", nwqm_wu_index_inc_stat_cnt_ena_prop);
        fld_map_t nwqm_wu_index_inc_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_wu_index_inc_stat_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wu_index_inc_stat_cnt),
                0x2C0,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_wu_index_inc_stat_cnt", nwqm_wu_index_inc_stat_cnt_prop);
        fld_map_t nwqm_wu_index_dec_stat_cnt_ena {
            CREATE_ENTRY("nq", 0, 1),
            CREATE_ENTRY("external", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nwqm_wu_index_dec_stat_cnt_ena_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_index_dec_stat_cnt_ena),
                    0x2C8,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_index_dec_stat_cnt_ena", nwqm_wu_index_dec_stat_cnt_ena_prop);
        fld_map_t nwqm_wu_index_dec_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_wu_index_dec_stat_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wu_index_dec_stat_cnt),
                0x2D0,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_wu_index_dec_stat_cnt", nwqm_wu_index_dec_stat_cnt_prop);
        fld_map_t nwqm_wu_index_alloc_req_stat_cnt {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nwqm_wu_index_alloc_req_stat_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(nwqm_wu_index_alloc_req_stat_cnt),
                    0x2D8,
                    CSR_TYPE::REG,
                    1);
        add_csr(nwqm_0, "nwqm_wu_index_alloc_req_stat_cnt", nwqm_wu_index_alloc_req_stat_cnt_prop);
        fld_map_t nwqm_wu_index_ptr_err_log {
            CREATE_ENTRY("wu_index_dq_dealloc_null_ptr_err", 0, 1),
            CREATE_ENTRY("wu_index_nq_alloc_null_ptr_err", 1, 1),
            CREATE_ENTRY("wu_index_dealloc_req_null_ptr_err", 2, 1),
            CREATE_ENTRY("wu_index_alloc_resp_null_ptr_err", 3, 1),
            CREATE_ENTRY("wm7_bitalloc_null_ptr_err", 4, 1),
            CREATE_ENTRY("wm6_bitalloc_null_ptr_err", 5, 1),
            CREATE_ENTRY("wm5_bitalloc_null_ptr_err", 6, 1),
            CREATE_ENTRY("wm4_bitalloc_null_ptr_err", 7, 1),
            CREATE_ENTRY("wm3_bitalloc_null_ptr_err", 8, 1),
            CREATE_ENTRY("wm2_bitalloc_null_ptr_err", 9, 1),
            CREATE_ENTRY("wm1_bitalloc_null_ptr_err", 10, 1),
            CREATE_ENTRY("wm0_bitalloc_null_ptr_err", 11, 1),
            CREATE_ENTRY("wm7_bitalloc_dealloc_err", 12, 1),
            CREATE_ENTRY("wm6_bitalloc_dealloc_err", 13, 1),
            CREATE_ENTRY("wm5_bitalloc_dealloc_err", 14, 1),
            CREATE_ENTRY("wm4_bitalloc_dealloc_err", 15, 1),
            CREATE_ENTRY("wm3_bitalloc_dealloc_err", 16, 1),
            CREATE_ENTRY("wm2_bitalloc_dealloc_err", 17, 1),
            CREATE_ENTRY("wm1_bitalloc_dealloc_err", 18, 1),
            CREATE_ENTRY("wm0_bitalloc_dealloc_err", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto nwqm_wu_index_ptr_err_log_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wu_index_ptr_err_log),
                0x300,
                CSR_TYPE::REG,
                1);
        add_csr(nwqm_0, "nwqm_wu_index_ptr_err_log", nwqm_wu_index_ptr_err_log_prop);
        fld_map_t nwqm_fifo_oflow_err_log {
            CREATE_ENTRY("wic_wu_index_alloc_req_fifo_oflow_err", 0, 1),
            CREATE_ENTRY("wic_wu_crd_alloc_req_fifo_oflow_err", 1, 1),
            CREATE_ENTRY("wbuf_wr_ack_fifo_oflow_err", 2, 1),
            CREATE_ENTRY("sni_if2_sn_resp_fifo_oflow_err", 3, 1),
            CREATE_ENTRY("sni_if1_sn_resp_fifo_oflow_err", 4, 1),
            CREATE_ENTRY("sni_if0_sn_resp_fifo_oflow_err", 5, 1),
            CREATE_ENTRY("sni_if2_sn_req_fifo_oflow_err", 6, 1),
            CREATE_ENTRY("sni_if1_sn_req_fifo_oflow_err", 7, 1),
            CREATE_ENTRY("sni_if0_sn_req_fifo_oflow_err", 8, 1),
            CREATE_ENTRY("sni_if2_wu_fifo_oflow_err", 9, 1),
            CREATE_ENTRY("sni_if1_wu_fifo_oflow_err", 10, 1),
            CREATE_ENTRY("sni_if0_wu_fifo_oflow_err", 11, 1),
            CREATE_ENTRY("dq_if2_fcb_req_fifo_oflow_err", 12, 1),
            CREATE_ENTRY("dq_if1_fcb_req_fifo_oflow_err", 13, 1),
            CREATE_ENTRY("dq_if0_fcb_req_fifo_oflow_err", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto nwqm_fifo_oflow_err_log_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nwqm_fifo_oflow_err_log),
                                                0x310,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(nwqm_0, "nwqm_fifo_oflow_err_log", nwqm_fifo_oflow_err_log_prop);
        fld_map_t nwqm_cnt_oflow_err_log {
            CREATE_ENTRY("non_pref_wm_pf_cnt_oflow_err", 0, 1),
            CREATE_ENTRY("wm7_pf_cnt_oflow_err", 1, 1),
            CREATE_ENTRY("wm6_pf_cnt_oflow_err", 2, 1),
            CREATE_ENTRY("wm5_pf_cnt_oflow_err", 3, 1),
            CREATE_ENTRY("wm4_pf_cnt_oflow_err", 4, 1),
            CREATE_ENTRY("wm3_pf_cnt_oflow_err", 5, 1),
            CREATE_ENTRY("wm2_pf_cnt_oflow_err", 6, 1),
            CREATE_ENTRY("wm1_pf_cnt_oflow_err", 7, 1),
            CREATE_ENTRY("wm0_pf_cnt_oflow_err", 8, 1),
            CREATE_ENTRY("wm7_index_free_cnt_oflow_err", 9, 1),
            CREATE_ENTRY("wm6_index_free_cnt_oflow_err", 10, 1),
            CREATE_ENTRY("wm5_index_free_cnt_oflow_err", 11, 1),
            CREATE_ENTRY("wm4_index_free_cnt_oflow_err", 12, 1),
            CREATE_ENTRY("wm3_index_free_cnt_oflow_err", 13, 1),
            CREATE_ENTRY("wm2_index_free_cnt_oflow_err", 14, 1),
            CREATE_ENTRY("wm1_index_free_cnt_oflow_err", 15, 1),
            CREATE_ENTRY("wm0_index_free_cnt_oflow_err", 16, 1),
            CREATE_ENTRY("ipf_num_alloc_req_oflow_err", 17, 1),
            CREATE_ENTRY("ipf_wu_index_pf_cnt_oflow_err", 18, 1),
            CREATE_ENTRY("pbuf_free_cnt_oflow_err", 19, 1),
            CREATE_ENTRY("wu_crd_cnt_oflow_err", 20, 1),
            CREATE_ENTRY("wu_crd_cnt_uflow_err", 21, 1),
            CREATE_ENTRY("ipf_alloc_wu_index_pf_fifo_crd_cnt_oflow_err", 22, 1),
            CREATE_ENTRY("wic_if2_sne_resp_crd_cnt_oflow_err", 23, 1),
            CREATE_ENTRY("wic_if1_sne_resp_crd_cnt_oflow_err", 24, 1),
            CREATE_ENTRY("wic_if0_sne_resp_crd_cnt_oflow_err", 25, 1),
            CREATE_ENTRY("wbuf_dne_2_wr_req_crd_cnt_oflow_err", 26, 1),
            CREATE_ENTRY("wbuf_dne_1_wr_req_crd_cnt_oflow_err", 27, 1),
            CREATE_ENTRY("wbuf_dne_0_wr_req_crd_cnt_oflow_err", 28, 1),
            CREATE_ENTRY("sni_wic_crd_cnt_oflow_err", 29, 1),
            CREATE_ENTRY("sni_wic_if2_vp_req_dealloc_crd_cnt_oflow_err", 30, 1),
            CREATE_ENTRY("sni_wic_if1_vp_req_dealloc_crd_cnt_oflow_err", 31, 1),
            CREATE_ENTRY("sni_wic_if0_vp_req_dealloc_crd_cnt_oflow_err", 32, 1),
            CREATE_ENTRY("sni_wic_vp_req_alloc_crd_cnt_oflow_err", 33, 1),
            CREATE_ENTRY("sni_if2_wic_dealloc_crd_cnt_oflow_err", 34, 1),
            CREATE_ENTRY("sni_if1_wic_dealloc_crd_cnt_oflow_err", 35, 1),
            CREATE_ENTRY("sni_if0_wic_dealloc_crd_cnt_oflow_err", 36, 1),
            CREATE_ENTRY("sni_fae_crd_cnt_oflow_err", 37, 1),
            CREATE_ENTRY("sni_nq_crd_cnt_oflow_err", 38, 1),
            CREATE_ENTRY("sne_if2_sn_req_crd_cnt_oflow_err", 39, 1),
            CREATE_ENTRY("sne_if1_sn_req_crd_cnt_oflow_err", 40, 1),
            CREATE_ENTRY("sne_if0_sn_req_crd_cnt_oflow_err", 41, 1),
            CREATE_ENTRY("sne_if2_sn_resp_crd_cnt_oflow_err", 42, 1),
            CREATE_ENTRY("sne_if1_sn_resp_crd_cnt_oflow_err", 43, 1),
            CREATE_ENTRY("sne_if0_sn_resp_crd_cnt_oflow_err", 44, 1),
            CREATE_ENTRY("rord_wic_dealloc_crd_cnt_oflow_err", 45, 1),
            CREATE_ENTRY("nq_wbuf_crd_cnt_oflow_err", 46, 1),
            CREATE_ENTRY("nq_fcb_crd_cnt_oflow_err", 47, 1),
            CREATE_ENTRY("dq_if2_sne_crd_cnt_oflow_err", 48, 1),
            CREATE_ENTRY("dq_if1_sne_crd_cnt_oflow_err", 49, 1),
            CREATE_ENTRY("dq_if0_sne_crd_cnt_oflow_err", 50, 1),
            CREATE_ENTRY("dq_if2_rord_crd_cnt_oflow_err", 51, 1),
            CREATE_ENTRY("dq_if1_rord_crd_cnt_oflow_err", 52, 1),
            CREATE_ENTRY("dq_if0_rord_crd_cnt_oflow_err", 53, 1),
            CREATE_ENTRY("dq_fcb_deq_resp_crd_cnt_oflow_err", 54, 1),
            CREATE_ENTRY("dne_if2_nwqm_fep_ldn_crd_cnt_oflow_err", 55, 1),
            CREATE_ENTRY("dne_if1_nwqm_fep_ldn_crd_cnt_oflow_err", 56, 1),
            CREATE_ENTRY("dne_if0_nwqm_fep_ldn_crd_cnt_oflow_err", 57, 1),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto nwqm_cnt_oflow_err_log_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nwqm_cnt_oflow_err_log),
                                               0x320,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nwqm_0, "nwqm_cnt_oflow_err_log", nwqm_cnt_oflow_err_log_prop);
        fld_map_t nwqm_sram_err_inj_cfg {
            CREATE_ENTRY("wic_wm7_bitalloc_sram", 0, 1),
            CREATE_ENTRY("wic_wm6_bitalloc_sram", 1, 1),
            CREATE_ENTRY("wic_wm5_bitalloc_sram", 2, 1),
            CREATE_ENTRY("wic_wm4_bitalloc_sram", 3, 1),
            CREATE_ENTRY("wic_wm3_bitalloc_sram", 4, 1),
            CREATE_ENTRY("wic_wm2_bitalloc_sram", 5, 1),
            CREATE_ENTRY("wic_wm1_bitalloc_sram", 6, 1),
            CREATE_ENTRY("wic_wm0_bitalloc_sram", 7, 1),
            CREATE_ENTRY("wic_if2_dealloc_req_data_fifo_sram", 8, 1),
            CREATE_ENTRY("wic_if1_dealloc_req_data_fifo_sram", 9, 1),
            CREATE_ENTRY("wic_if0_dealloc_req_data_fifo_sram", 10, 1),
            CREATE_ENTRY("wic_wu_index_alloc_req_fifo_sram", 11, 1),
            CREATE_ENTRY("wbuf_wbuf_data_sram_lsb", 12, 1),
            CREATE_ENTRY("wbuf_wbuf_data_sram_msb", 13, 1),
            CREATE_ENTRY("sts_pbuf_wu_len_sram", 14, 1),
            CREATE_ENTRY("sts_wm_wu_len_sram", 15, 1),
            CREATE_ENTRY("sts_pbuf_link_sram", 16, 1),
            CREATE_ENTRY("sts_wm_link_sram", 17, 1),
            CREATE_ENTRY("sts_ptr_sram", 18, 1),
            CREATE_ENTRY("sni_if2_wu_data_fifo_sram", 19, 1),
            CREATE_ENTRY("sni_if1_wu_data_fifo_sram", 20, 1),
            CREATE_ENTRY("sni_if0_wu_data_fifo_sram", 21, 1),
            CREATE_ENTRY("pbuf_wu_sram", 22, 1),
            CREATE_ENTRY("ipf_wu_index_pf_sram1", 23, 1),
            CREATE_ENTRY("ipf_wu_index_pf_sram0", 24, 1),
            CREATE_ENTRY("err_type", 25, 1),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto nwqm_sram_err_inj_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nwqm_sram_err_inj_cfg),
                                              0x330,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(nwqm_0, "nwqm_sram_err_inj_cfg", nwqm_sram_err_inj_cfg_prop);
        fld_map_t nwqm_fla_cfg {
            CREATE_ENTRY("fla_module_id", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nwqm_fla_cfg_prop = csr_prop_t(
                                     std::make_shared<csr_s>(nwqm_fla_cfg),
                                     0x350,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(nwqm_0, "nwqm_fla_cfg", nwqm_fla_cfg_prop);
        fld_map_t nwqm_wm_index_free_cnt_min {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto nwqm_wm_index_free_cnt_min_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wm_index_free_cnt_min),
                0x380,
                CSR_TYPE::TBL,
                1);
        add_csr(nwqm_0, "nwqm_wm_index_free_cnt_min", nwqm_wm_index_free_cnt_min_prop);
        fld_map_t nwqm_wm_index_free_cnt_adj {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto nwqm_wm_index_free_cnt_adj_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wm_index_free_cnt_adj),
                0x580,
                CSR_TYPE::TBL,
                1);
        add_csr(nwqm_0, "nwqm_wm_index_free_cnt_adj", nwqm_wm_index_free_cnt_adj_prop);
        fld_map_t nwqm_wic_fl_bitalloc_cfg {
            CREATE_ENTRY("fld_data", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto nwqm_wic_fl_bitalloc_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_wic_fl_bitalloc_cfg),
                0x8000,
                CSR_TYPE::REG_LST,
                8);
        add_csr(nwqm_0, "nwqm_wic_fl_bitalloc_cfg", nwqm_wic_fl_bitalloc_cfg_prop);
        fld_map_t nwqm_pbuf_free_bit_set {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nwqm_pbuf_free_bit_set_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nwqm_pbuf_free_bit_set),
                                               0x208000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(nwqm_0, "nwqm_pbuf_free_bit_set", nwqm_pbuf_free_bit_set_prop);
        fld_map_t nwqm_pbuf_free_bit_clr {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nwqm_pbuf_free_bit_clr_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nwqm_pbuf_free_bit_clr),
                                               0x208400,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(nwqm_0, "nwqm_pbuf_free_bit_clr", nwqm_pbuf_free_bit_clr_prop);
        fld_map_t nwqm_ipf_wu_index_pf_sram {
            CREATE_ENTRY("val", 0, 256)
        };
        auto nwqm_ipf_wu_index_pf_sram_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_ipf_wu_index_pf_sram),
                0x209000,
                CSR_TYPE::TBL,
                1);
        add_csr(nwqm_0, "nwqm_ipf_wu_index_pf_sram", nwqm_ipf_wu_index_pf_sram_prop);
        fld_map_t nwqm_sts_ptr_sram {
            CREATE_ENTRY("val", 0, 68),
            CREATE_ENTRY("__rsvd", 68, 60)
        };
        auto nwqm_sts_ptr_sram_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nwqm_sts_ptr_sram),
                                          0x220000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nwqm_0, "nwqm_sts_ptr_sram", nwqm_sts_ptr_sram_prop);
        fld_map_t nwqm_sts_wm_link_sram {
            CREATE_ENTRY("val", 0, 68),
            CREATE_ENTRY("__rsvd", 68, 60)
        };
        auto nwqm_sts_wm_link_sram_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nwqm_sts_wm_link_sram),
                                              0x440000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(nwqm_0, "nwqm_sts_wm_link_sram", nwqm_sts_wm_link_sram_prop);
        fld_map_t nwqm_sts_pbuf_link_sram {
            CREATE_ENTRY("val", 0, 68),
            CREATE_ENTRY("__rsvd", 68, 60)
        };
        auto nwqm_sts_pbuf_link_sram_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nwqm_sts_pbuf_link_sram),
                                                0x840000,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(nwqm_0, "nwqm_sts_pbuf_link_sram", nwqm_sts_pbuf_link_sram_prop);
        fld_map_t nwqm_sts_wm_wu_len_sram {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto nwqm_sts_wm_wu_len_sram_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nwqm_sts_wm_wu_len_sram),
                                                0x860000,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(nwqm_0, "nwqm_sts_wm_wu_len_sram", nwqm_sts_wm_wu_len_sram_prop);
        fld_map_t nwqm_sts_pbuf_wu_len_sram {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto nwqm_sts_pbuf_wu_len_sram_prop = csr_prop_t(
                std::make_shared<csr_s>(nwqm_sts_pbuf_wu_len_sram),
                0x960000,
                CSR_TYPE::TBL,
                1);
        add_csr(nwqm_0, "nwqm_sts_pbuf_wu_len_sram", nwqm_sts_pbuf_wu_len_sram_prop);
// END nwqm
    }
    {
// BEGIN psw_pwr
        auto psw_pwr_0 = nu_rng[0].add_an({"psw_pwr"}, 0x9000000, 1, 0x0);
        fld_map_t psw_pwr_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_pwr_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_timeout_thresh_cfg", psw_pwr_timeout_thresh_cfg_prop);
        fld_map_t psw_pwr_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_pwr_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_pwr_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_pwr_0, "psw_pwr_timeout_clr", psw_pwr_timeout_clr_prop);
        fld_map_t psw_pwr_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pwr_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_pwr_spare_pio),
                                          0xC0,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_pwr_0, "psw_pwr_spare_pio", psw_pwr_spare_pio_prop);
        fld_map_t psw_pwr_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pwr_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_pwr_scratchpad),
                                           0xC8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_pwr_0, "psw_pwr_scratchpad", psw_pwr_scratchpad_prop);
        fld_map_t psw_pwr_cfg_min_pkt_size {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_pwr_cfg_min_pkt_size_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_cfg_min_pkt_size),
                0xE0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_min_pkt_size", psw_pwr_cfg_min_pkt_size_prop);
        fld_map_t psw_pwr_cfg_min_pkt_size_after_rewrite {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_pwr_cfg_min_pkt_size_after_rewrite_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_min_pkt_size_after_rewrite),
                    0xE8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_min_pkt_size_after_rewrite", psw_pwr_cfg_min_pkt_size_after_rewrite_prop);
        fld_map_t psw_pwr_mem_init_start_cfg {
            CREATE_ENTRY("q_drop_cntr", 0, 1),
            CREATE_ENTRY("q_enq_cntr", 1, 1),
            CREATE_ENTRY("src_pri_enq_cntr", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto psw_pwr_mem_init_start_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_mem_init_start_cfg),
                0xF8,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_mem_init_start_cfg", psw_pwr_mem_init_start_cfg_prop);
        fld_map_t psw_pwr_fla_slave_id {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_pwr_fla_slave_id_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_stream_mem_sel_ifpg_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_stream_mem_sel_ifpg),
                    0x110,
                    CSR_TYPE::REG_LST,
                    6);
        add_csr(psw_pwr_0, "psw_pwr_cfg_stream_mem_sel_ifpg", psw_pwr_cfg_stream_mem_sel_ifpg_prop);
        fld_map_t psw_pwr_cfg_flex_clear_ifpg {
            CREATE_ENTRY("stream0", 0, 1),
            CREATE_ENTRY("stream1", 1, 1),
            CREATE_ENTRY("stream2", 2, 1),
            CREATE_ENTRY("stream3", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_flex_clear_ifpg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_cfg_flex_clear_ifpg),
                0x140,
                CSR_TYPE::REG_LST,
                6);
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
        };
        auto psw_pwr_cfg_back_pressure_ifpg_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_back_pressure_ifpg),
                    0x170,
                    CSR_TYPE::REG_LST,
                    6);
        add_csr(psw_pwr_0, "psw_pwr_cfg_back_pressure_ifpg", psw_pwr_cfg_back_pressure_ifpg_prop);
        fld_map_t psw_pwr_cfg_repl_fifo_th {
            CREATE_ENTRY("headroom", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto psw_pwr_cfg_repl_fifo_th_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_cfg_repl_fifo_th),
                0x1A0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_repl_fifo_th", psw_pwr_cfg_repl_fifo_th_prop);
        fld_map_t psw_pwr_cfg_cfp_hysteresis {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("thresh", 1, 14),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_pwr_cfg_cfp_hysteresis_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_cfg_cfp_hysteresis),
                0x1A8,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_cfp_hysteresis", psw_pwr_cfg_cfp_hysteresis_prop);
        fld_map_t psw_pwr_cfg_egress_mirror_ecn {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_pwr_cfg_egress_mirror_ecn_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_egress_mirror_ecn),
                    0x1B0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_egress_mirror_ecn", psw_pwr_cfg_egress_mirror_ecn_prop);
        fld_map_t psw_pwr_cfg_q_drop_stats {
            CREATE_ENTRY("psw_drop", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_pwr_cfg_q_drop_stats_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_spd_prop = csr_prop_t(
                                        std::make_shared<csr_s>(psw_pwr_cfg_spd),
                                        0x1C0,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_spd", psw_pwr_cfg_spd_prop);
        fld_map_t psw_pwr_cfg_egress_sample_info {
            CREATE_ENTRY("send_to_fpg_en", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_pwr_cfg_egress_sample_info_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_egress_sample_info),
                    0x1C8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_egress_sample_info", psw_pwr_cfg_egress_sample_info_prop);
        fld_map_t psw_pwr_cfg_stream_dis {
            CREATE_ENTRY("fp_stream_dis", 0, 24),
            CREATE_ENTRY("epg_dis", 24, 3),
            CREATE_ENTRY("__rsvd", 27, 37)
        };
        auto psw_pwr_cfg_stream_dis_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_clear_hwm_prop = csr_prop_t(
                                              std::make_shared<csr_s>(psw_pwr_cfg_clear_hwm),
                                              0x1D8,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_clear_hwm", psw_pwr_cfg_clear_hwm_prop);
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
        };
        auto psw_pwr_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_sram_err_inj_cfg),
                0x238,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_sram_err_inj_cfg", psw_pwr_sram_err_inj_cfg_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_cln {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_pwr_cfg_pbuf_arb_cln_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_cln),
                0x270,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_cln", psw_pwr_cfg_pbuf_arb_cln_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_fpg0_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_pbuf_arb_fpg0_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg0_streams_en),
                    0x278,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg0_streams_en", psw_pwr_cfg_pbuf_arb_fpg0_streams_en_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_fpg1_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_pbuf_arb_fpg1_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg1_streams_en),
                    0x280,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg1_streams_en", psw_pwr_cfg_pbuf_arb_fpg1_streams_en_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_fpg2_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_pbuf_arb_fpg2_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg2_streams_en),
                    0x288,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg2_streams_en", psw_pwr_cfg_pbuf_arb_fpg2_streams_en_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_fpg3_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_pbuf_arb_fpg3_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg3_streams_en),
                    0x290,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg3_streams_en", psw_pwr_cfg_pbuf_arb_fpg3_streams_en_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_fpg4_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_pbuf_arb_fpg4_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_fpg4_streams_en),
                    0x298,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_fpg4_streams_en", psw_pwr_cfg_pbuf_arb_fpg4_streams_en_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_fpg5_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_pwr_cfg_pbuf_arb_fpg5_streams_en_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_fpg0_cln_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_fpg1_cln_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_fpg2_cln_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_fpg3_cln_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_fpg4_cln_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_fpg5_cln_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_wrr_weights_prop = csr_prop_t(
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
        };
        auto psw_pwr_cfg_pbuf_arb_min_spacing_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_min_spacing),
                    0x2E0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_min_spacing", psw_pwr_cfg_pbuf_arb_min_spacing_prop);
        fld_map_t psw_pwr_cfg_pbuf_arb_sync_tdm_delay {
            CREATE_ENTRY("cnt", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto psw_pwr_cfg_pbuf_arb_sync_tdm_delay_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_pwr_cfg_pbuf_arb_sync_tdm_delay),
                    0x2E8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_pwr_0, "psw_pwr_cfg_pbuf_arb_sync_tdm_delay", psw_pwr_cfg_pbuf_arb_sync_tdm_delay_prop);
        fld_map_t psw_pwr_stats_cntrs {
            CREATE_ENTRY("cnt", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto psw_pwr_stats_cntrs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_pwr_stats_cntrs),
                                            0x300,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(psw_pwr_0, "psw_pwr_stats_cntrs", psw_pwr_stats_cntrs_prop);
// END psw_pwr
    }
    {
// BEGIN psw_prd
        auto psw_prd_0 = nu_rng[0].add_an({"psw_prd"}, 0x9100000, 1, 0x0);
        fld_map_t psw_prd_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_prd_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prd_0, "psw_prd_timeout_thresh_cfg", psw_prd_timeout_thresh_cfg_prop);
        fld_map_t psw_prd_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_prd_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_prd_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_prd_0, "psw_prd_timeout_clr", psw_prd_timeout_clr_prop);
        fld_map_t psw_prd_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_prd_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_prd_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_prd_0, "psw_prd_spare_pio", psw_prd_spare_pio_prop);
        fld_map_t psw_prd_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_prd_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_prd_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_prd_0, "psw_prd_scratchpad", psw_prd_scratchpad_prop);
        fld_map_t psw_prd_cfg_pb_bytes_adj {
            CREATE_ENTRY("fpg_val", 0, 5),
            CREATE_ENTRY("epg_val", 5, 5),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto psw_prd_cfg_pb_bytes_adj_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_cfg_pb_bytes_adj),
                0x80,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prd_0, "psw_prd_cfg_pb_bytes_adj", psw_prd_cfg_pb_bytes_adj_prop);
        fld_map_t psw_prd_cfg_min_pkt_size {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_prd_cfg_min_pkt_size_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_cfg_min_pkt_size),
                0x88,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prd_0, "psw_prd_cfg_min_pkt_size", psw_prd_cfg_min_pkt_size_prop);
        fld_map_t psw_prd_cfg_mcd_epg_sampled_pkt {
            CREATE_ENTRY("enable", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_prd_cfg_mcd_epg_sampled_pkt_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_edb_credits_efpg_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_edb_credits_efpg),
                    0x98,
                    CSR_TYPE::REG_LST,
                    6);
        add_csr(psw_prd_0, "psw_prd_cfg_edb_credits_efpg", psw_prd_cfg_edb_credits_efpg_prop);
        fld_map_t psw_prd_cfg_stream_drain {
            CREATE_ENTRY("fp_stream_en", 0, 24),
            CREATE_ENTRY("epg_en", 24, 3),
            CREATE_ENTRY("__rsvd", 27, 37)
        };
        auto psw_prd_cfg_stream_drain_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_cfg_stream_drain),
                0xC8,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prd_0, "psw_prd_cfg_stream_drain", psw_prd_cfg_stream_drain_prop);
        fld_map_t psw_prd_cfg_edb_credits_erp {
            CREATE_ENTRY("credit_val", 0, 4),
            CREATE_ENTRY("credit_init", 4, 1),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto psw_prd_cfg_edb_credits_erp_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_cfg_edb_credits_erp),
                0x100,
                CSR_TYPE::REG_LST,
                3);
        add_csr(psw_prd_0, "psw_prd_cfg_edb_credits_erp", psw_prd_cfg_edb_credits_erp_prop);
        fld_map_t psw_prd_cfg_spd {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("dest_stream", 1, 6),
            CREATE_ENTRY("dest_q", 7, 4),
            CREATE_ENTRY("num_scopy_rw_instr", 11, 4),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_prd_cfg_spd_prop = csr_prop_t(
                                        std::make_shared<csr_s>(psw_prd_cfg_spd),
                                        0x138,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(psw_prd_0, "psw_prd_cfg_spd", psw_prd_cfg_spd_prop);
        fld_map_t psw_prd_cfg_spd_scopy_rw_instr_lowerhalf {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_prd_cfg_spd_scopy_rw_instr_lowerhalf_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_spd_scopy_rw_instr_lowerhalf),
                    0x140,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_spd_scopy_rw_instr_lowerhalf", psw_prd_cfg_spd_scopy_rw_instr_lowerhalf_prop);
        fld_map_t psw_prd_cfg_spd_scopy_rw_instr_upperhalf {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_prd_cfg_spd_scopy_rw_instr_upperhalf_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_spd_scopy_rw_instr_upperhalf),
                    0x148,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_spd_scopy_rw_instr_upperhalf", psw_prd_cfg_spd_scopy_rw_instr_upperhalf_prop);
        fld_map_t psw_prd_stats_cfg_deq_cntr {
            CREATE_ENTRY("count_rewrite_bytes", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_prd_stats_cfg_deq_cntr_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_stats_cfg_deq_cntr),
                0x150,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prd_0, "psw_prd_stats_cfg_deq_cntr", psw_prd_stats_cfg_deq_cntr_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_cln {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_prd_cfg_pbuf_arb_cln_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_cln),
                0x160,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_cln", psw_prd_cfg_pbuf_arb_cln_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_fpg0_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prd_cfg_pbuf_arb_fpg0_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg0_streams_en),
                    0x168,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg0_streams_en", psw_prd_cfg_pbuf_arb_fpg0_streams_en_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_fpg1_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prd_cfg_pbuf_arb_fpg1_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg1_streams_en),
                    0x170,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg1_streams_en", psw_prd_cfg_pbuf_arb_fpg1_streams_en_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_fpg2_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prd_cfg_pbuf_arb_fpg2_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg2_streams_en),
                    0x178,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg2_streams_en", psw_prd_cfg_pbuf_arb_fpg2_streams_en_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_fpg3_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prd_cfg_pbuf_arb_fpg3_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg3_streams_en),
                    0x180,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg3_streams_en", psw_prd_cfg_pbuf_arb_fpg3_streams_en_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_fpg4_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prd_cfg_pbuf_arb_fpg4_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_fpg4_streams_en),
                    0x188,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_fpg4_streams_en", psw_prd_cfg_pbuf_arb_fpg4_streams_en_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_fpg5_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prd_cfg_pbuf_arb_fpg5_streams_en_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_fpg0_cln_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_fpg1_cln_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_fpg2_cln_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_fpg3_cln_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_fpg4_cln_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_fpg5_cln_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_wrr_weights_prop = csr_prop_t(
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
        };
        auto psw_prd_cfg_pbuf_arb_min_spacing_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_min_spacing),
                    0x1D0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_min_spacing", psw_prd_cfg_pbuf_arb_min_spacing_prop);
        fld_map_t psw_prd_cfg_pbuf_arb_sync_tdm_delay {
            CREATE_ENTRY("cnt", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto psw_prd_cfg_pbuf_arb_sync_tdm_delay_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prd_cfg_pbuf_arb_sync_tdm_delay),
                    0x1D8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prd_0, "psw_prd_cfg_pbuf_arb_sync_tdm_delay", psw_prd_cfg_pbuf_arb_sync_tdm_delay_prop);
        fld_map_t psw_prd_stats_cntrs {
            CREATE_ENTRY("cnt", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto psw_prd_stats_cntrs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_prd_stats_cntrs),
                                            0x200,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(psw_prd_0, "psw_prd_stats_cntrs", psw_prd_stats_cntrs_prop);
// END psw_prd
    }
    {
// BEGIN psw_sch
        auto psw_sch_0 = nu_rng[0].add_an({"psw_sch"}, 0x9180000, 1, 0x0);
        fld_map_t psw_sch_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_sch_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_sch_0, "psw_sch_timeout_thresh_cfg", psw_sch_timeout_thresh_cfg_prop);
        fld_map_t psw_sch_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_sch_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_sch_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_sch_0, "psw_sch_timeout_clr", psw_sch_timeout_clr_prop);
        fld_map_t psw_sch_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_sch_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_sch_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_sch_0, "psw_sch_spare_pio", psw_sch_spare_pio_prop);
        fld_map_t psw_sch_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_sch_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_sch_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_sch_0, "psw_sch_scratchpad", psw_sch_scratchpad_prop);
        fld_map_t psw_sch_psch_cfg_credits_fp {
            CREATE_ENTRY("credit_val", 0, 3),
            CREATE_ENTRY("credit_init", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_credits_fp_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_psch_cfg_credits_fp),
                0x80,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_fp", psw_sch_psch_cfg_credits_fp_prop);
        fld_map_t psw_sch_psch_cfg_credits_erp {
            CREATE_ENTRY("credit_val", 0, 4),
            CREATE_ENTRY("credit_init", 4, 1),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto psw_sch_psch_cfg_credits_erp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_credits_erp),
                    0x140,
                    CSR_TYPE::REG_LST,
                    3);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_erp", psw_sch_psch_cfg_credits_erp_prop);
        fld_map_t psw_sch_psch_cfg_credits_purge_port {
            CREATE_ENTRY("credit_val", 0, 4),
            CREATE_ENTRY("credit_init", 4, 1),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto psw_sch_psch_cfg_credits_purge_port_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_credits_purge_port),
                    0x158,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_credits_purge_port", psw_sch_psch_cfg_credits_purge_port_prop);
        fld_map_t psw_sch_psch_cfg_select_credits_fp_stream {
            CREATE_ENTRY("fp_num", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto psw_sch_psch_cfg_select_credits_fp_stream_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_select_credits_fp_stream),
                    0x180,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_select_credits_fp_stream", psw_sch_psch_cfg_select_credits_fp_stream_prop);
        fld_map_t psw_sch_psch_cfg_arb_sync_tdm_delay {
            CREATE_ENTRY("cnt", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto psw_sch_psch_cfg_arb_sync_tdm_delay_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_sync_tdm_delay),
                    0x190,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_sync_tdm_delay", psw_sch_psch_cfg_arb_sync_tdm_delay_prop);
        fld_map_t psw_sch_psch_cfg_arb {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_sch_psch_cfg_arb_prop = csr_prop_t(
                                             std::make_shared<csr_s>(psw_sch_psch_cfg_arb),
                                             0x198,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb", psw_sch_psch_cfg_arb_prop);
        fld_map_t psw_sch_psch_cfg_arb_fpg0_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_fpg0_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg0_streams_en),
                    0x1A0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg0_streams_en", psw_sch_psch_cfg_arb_fpg0_streams_en_prop);
        fld_map_t psw_sch_psch_cfg_arb_fpg1_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_fpg1_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg1_streams_en),
                    0x1A8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg1_streams_en", psw_sch_psch_cfg_arb_fpg1_streams_en_prop);
        fld_map_t psw_sch_psch_cfg_arb_fpg2_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_fpg2_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg2_streams_en),
                    0x1B0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg2_streams_en", psw_sch_psch_cfg_arb_fpg2_streams_en_prop);
        fld_map_t psw_sch_psch_cfg_arb_fpg3_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_fpg3_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg3_streams_en),
                    0x1B8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg3_streams_en", psw_sch_psch_cfg_arb_fpg3_streams_en_prop);
        fld_map_t psw_sch_psch_cfg_arb_fpg4_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_fpg4_streams_en_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_fpg4_streams_en),
                    0x1C0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_fpg4_streams_en", psw_sch_psch_cfg_arb_fpg4_streams_en_prop);
        fld_map_t psw_sch_psch_cfg_arb_fpg5_streams_en {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_fpg5_streams_en_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fpg0_cln_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fpg1_cln_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fpg2_cln_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fpg3_cln_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fpg4_cln_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fpg5_cln_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_fp_tdm_slots_mask_prop = csr_prop_t(
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
        };
        auto psw_sch_psch_cfg_arb_min_spacing_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_min_spacing),
                    0x208,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_min_spacing", psw_sch_psch_cfg_arb_min_spacing_prop);
        fld_map_t psw_sch_psch_cfg_arb_gr_period {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_sch_psch_cfg_arb_gr_period_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_period),
                    0x210,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_period", psw_sch_psch_cfg_arb_gr_period_prop);
        fld_map_t psw_sch_psch_cfg_arb_gr_wt_ep_stream {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_psch_cfg_arb_gr_wt_ep_stream_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_psch_cfg_arb_gr_wt_ep_stream),
                    0x218,
                    CSR_TYPE::REG,
                    24);
        add_csr(psw_sch_0, "psw_sch_psch_cfg_arb_gr_wt_ep_stream", psw_sch_psch_cfg_arb_gr_wt_ep_stream_prop);
        fld_map_t psw_sch_qsch_mem_init_start_cfg {
            CREATE_ENTRY("chnl_dwrr_sc", 0, 1),
            CREATE_ENTRY("q_dwrr_sc", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_sch_qsch_mem_init_start_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_mem_init_start_cfg),
                    0x2E0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_qsch_mem_init_start_cfg", psw_sch_qsch_mem_init_start_cfg_prop);
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
        };
        auto psw_sch_qsch_cfg_chnl_q_mapping_fp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_chnl_q_mapping_fp),
                    0x2F0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_chnl_q_mapping_fp", psw_sch_qsch_cfg_chnl_q_mapping_fp_prop);
        fld_map_t psw_sch_qsch_cfg_cr_sp_queues_fp {
            CREATE_ENTRY("vec", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_sch_qsch_cfg_cr_sp_queues_fp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_cr_sp_queues_fp),
                    0x2F8,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_cr_sp_queues_fp", psw_sch_qsch_cfg_cr_sp_queues_fp_prop);
        fld_map_t psw_sch_qsch_cfg_extrabw_sp_queues_fp {
            CREATE_ENTRY("vec", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_sch_qsch_cfg_extrabw_sp_queues_fp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_extrabw_sp_queues_fp),
                    0x3B8,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_extrabw_sp_queues_fp", psw_sch_qsch_cfg_extrabw_sp_queues_fp_prop);
        fld_map_t psw_sch_qsch_cfg_cr_sp_channels_fp {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_qsch_cfg_cr_sp_channels_fp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_cr_sp_channels_fp),
                    0x478,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_cr_sp_channels_fp", psw_sch_qsch_cfg_cr_sp_channels_fp_prop);
        fld_map_t psw_sch_qsch_cfg_extrabw_sp_channels_fp {
            CREATE_ENTRY("vec", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_sch_qsch_cfg_extrabw_sp_channels_fp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_extrabw_sp_channels_fp),
                    0x538,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_extrabw_sp_channels_fp", psw_sch_qsch_cfg_extrabw_sp_channels_fp_prop);
        fld_map_t psw_sch_qsch_cfg_cr_sp_queues_ep {
            CREATE_ENTRY("vec", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_sch_qsch_cfg_cr_sp_queues_ep_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_cr_sp_queues_ep),
                    0x5F8,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_cr_sp_queues_ep", psw_sch_qsch_cfg_cr_sp_queues_ep_prop);
        fld_map_t psw_sch_qsch_cfg_extrabw_sp_queues_ep {
            CREATE_ENTRY("vec", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_sch_qsch_cfg_extrabw_sp_queues_ep_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_extrabw_sp_queues_ep),
                    0x6B8,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_extrabw_sp_queues_ep", psw_sch_qsch_cfg_extrabw_sp_queues_ep_prop);
        fld_map_t psw_sch_qsch_cfg_flush_queues_fp {
            CREATE_ENTRY("vec", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_sch_qsch_cfg_flush_queues_fp_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_flush_queues_fp),
                    0x778,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_flush_queues_fp", psw_sch_qsch_cfg_flush_queues_fp_prop);
        fld_map_t psw_sch_qsch_cfg_flush_queues_ep {
            CREATE_ENTRY("vec", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_sch_qsch_cfg_flush_queues_ep_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_cfg_flush_queues_ep),
                    0x838,
                    CSR_TYPE::REG_LST,
                    24);
        add_csr(psw_sch_0, "psw_sch_qsch_cfg_flush_queues_ep", psw_sch_qsch_cfg_flush_queues_ep_prop);
        fld_map_t psw_sch_orl_cfg_refresh_period {
            CREATE_ENTRY("val", 0, 11),
            CREATE_ENTRY("en", 11, 1),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto psw_sch_orl_cfg_refresh_period_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_cfg_refresh_period),
                    0x8F8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_cfg_refresh_period", psw_sch_orl_cfg_refresh_period_prop);
        fld_map_t psw_sch_orl_cfg_deq_upd {
            CREATE_ENTRY("dis", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_sch_orl_cfg_deq_upd_prop = csr_prop_t(
                                                std::make_shared<csr_s>(psw_sch_orl_cfg_deq_upd),
                                                0x900,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(psw_sch_0, "psw_sch_orl_cfg_deq_upd", psw_sch_orl_cfg_deq_upd_prop);
        fld_map_t psw_sch_pfcrx_q_to_pri_fp {
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
        };
        auto psw_sch_pfcrx_q_to_pri_fp_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_fp),
                0x908,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_fp", psw_sch_pfcrx_q_to_pri_fp_prop);
        fld_map_t psw_sch_pfcrx_q_to_pri_ep {
            CREATE_ENTRY("q0", 0, 3),
            CREATE_ENTRY("q1", 3, 3),
            CREATE_ENTRY("q2", 6, 3),
            CREATE_ENTRY("q3", 9, 3),
            CREATE_ENTRY("q4", 12, 3),
            CREATE_ENTRY("q5", 15, 3),
            CREATE_ENTRY("q6", 18, 3),
            CREATE_ENTRY("q7", 21, 3),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto psw_sch_pfcrx_q_to_pri_ep_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_pfcrx_q_to_pri_ep),
                0x9C8,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_pfcrx_q_to_pri_ep", psw_sch_pfcrx_q_to_pri_ep_prop);
        fld_map_t psw_sch_pfcrx_xoff_set_fp {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_sch_pfcrx_xoff_set_fp_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_fp),
                0xA88,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_fp", psw_sch_pfcrx_xoff_set_fp_prop);
        fld_map_t psw_sch_pfcrx_xoff_reset_fp {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_sch_pfcrx_xoff_reset_fp_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_fp),
                0xB48,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_fp", psw_sch_pfcrx_xoff_reset_fp_prop);
        fld_map_t psw_sch_pfcrx_xoff_set_ep {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_sch_pfcrx_xoff_set_ep_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_pfcrx_xoff_set_ep),
                0xC08,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_set_ep", psw_sch_pfcrx_xoff_set_ep_prop);
        fld_map_t psw_sch_pfcrx_xoff_reset_ep {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto psw_sch_pfcrx_xoff_reset_ep_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_pfcrx_xoff_reset_ep),
                0xCC8,
                CSR_TYPE::REG,
                24);
        add_csr(psw_sch_0, "psw_sch_pfcrx_xoff_reset_ep", psw_sch_pfcrx_xoff_reset_ep_prop);
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
        };
        auto psw_sch_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_sch_sram_err_inj_cfg),
                0xD90,
                CSR_TYPE::REG,
                1);
        add_csr(psw_sch_0, "psw_sch_sram_err_inj_cfg", psw_sch_sram_err_inj_cfg_prop);
        fld_map_t psw_sch_qsch_mem_q_dwrr_weight {
            CREATE_ENTRY("data", 0, 56),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto psw_sch_qsch_mem_q_dwrr_weight_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_mem_q_dwrr_weight),
                    0x1000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_qsch_mem_q_dwrr_weight", psw_sch_qsch_mem_q_dwrr_weight_prop);
        fld_map_t psw_sch_qsch_mem_chnl_dwrr_weight {
            CREATE_ENTRY("data", 0, 28),
            CREATE_ENTRY("__rsvd", 28, 36)
        };
        auto psw_sch_qsch_mem_chnl_dwrr_weight_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_qsch_mem_chnl_dwrr_weight),
                    0x23000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_qsch_mem_chnl_dwrr_weight", psw_sch_qsch_mem_chnl_dwrr_weight_prop);
        fld_map_t psw_sch_orl_fpg_0_to_2_queues_cr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_0_to_2_queues_cr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_0_to_2_queues_cr),
                    0x25800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_0_to_2_queues_cr", psw_sch_orl_fpg_0_to_2_queues_cr_prop);
        fld_map_t psw_sch_orl_fpg_0_to_2_queues_pr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_0_to_2_queues_pr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_0_to_2_queues_pr),
                    0x29800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_0_to_2_queues_pr", psw_sch_orl_fpg_0_to_2_queues_pr_prop);
        fld_map_t psw_sch_orl_fpg_3_to_5_queues_cr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_3_to_5_queues_cr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_3_to_5_queues_cr),
                    0x2D800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_3_to_5_queues_cr", psw_sch_orl_fpg_3_to_5_queues_cr_prop);
        fld_map_t psw_sch_orl_fpg_3_to_5_queues_pr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_3_to_5_queues_pr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_3_to_5_queues_pr),
                    0x31800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_3_to_5_queues_pr", psw_sch_orl_fpg_3_to_5_queues_pr_prop);
        fld_map_t psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_cr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_cr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_cr),
                    0x35800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_cr", psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_cr_prop);
        fld_map_t psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_pr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_pr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_pr),
                    0x39800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_pr", psw_sch_orl_fpg_0_to_2_chnl_ep_0_to_95_queues_pr_prop);
        fld_map_t psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_cr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_cr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_cr),
                    0x3D800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_cr", psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_cr_prop);
        fld_map_t psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_pr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_pr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_pr),
                    0x41800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_pr", psw_sch_orl_fpg_3_to_5_chnl_ep_96_to_191_queues_pr_prop);
        fld_map_t psw_sch_orl_fpg_0_to_2_streams_ep_0_to_11_streams_pr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_0_to_2_streams_ep_0_to_11_streams_pr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_0_to_2_streams_ep_0_to_11_streams_pr),
                    0x45800,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_0_to_2_streams_ep_0_to_11_streams_pr", psw_sch_orl_fpg_0_to_2_streams_ep_0_to_11_streams_pr_prop);
        fld_map_t psw_sch_orl_fpg_3_to_5_streams_ep_12_to_23_streams_pr {
            CREATE_ENTRY("sw_override", 0, 1),
            CREATE_ENTRY("sw_override_val", 1, 1),
            CREATE_ENTRY("refresh_credits", 2, 18),
            CREATE_ENTRY("count", 20, 22),
            CREATE_ENTRY("thresh", 42, 20),
            CREATE_ENTRY("hit", 62, 1),
            CREATE_ENTRY("__rsvd", 63, 1)
        };
        auto psw_sch_orl_fpg_3_to_5_streams_ep_12_to_23_streams_pr_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_sch_orl_fpg_3_to_5_streams_ep_12_to_23_streams_pr),
                    0x46000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_sch_0, "psw_sch_orl_fpg_3_to_5_streams_ep_12_to_23_streams_pr", psw_sch_orl_fpg_3_to_5_streams_ep_12_to_23_streams_pr_prop);
// END psw_sch
    }
    {
// BEGIN psw_prm
        auto psw_prm_0 = nu_rng[0].add_an({"psw_prm"}, 0x9200000, 1, 0x0);
        fld_map_t psw_prm_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_prm_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_timeout_thresh_cfg", psw_prm_timeout_thresh_cfg_prop);
        fld_map_t psw_prm_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_prm_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_prm_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_prm_0, "psw_prm_timeout_clr", psw_prm_timeout_clr_prop);
        fld_map_t psw_prm_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_prm_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_prm_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_prm_0, "psw_prm_spare_pio", psw_prm_spare_pio_prop);
        fld_map_t psw_prm_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_prm_scratchpad_prop = csr_prop_t(
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
        };
        auto psw_prm_mem_init_start_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_mem_init_start_cfg),
                0x80,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_mem_init_start_cfg", psw_prm_mem_init_start_cfg_prop);
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
        };
        auto psw_prm_blk_en_prop = csr_prop_t(
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
        };
        auto psw_prm_cfg_spd_prop = csr_prop_t(
                                        std::make_shared<csr_s>(psw_prm_cfg_spd),
                                        0x98,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(psw_prm_0, "psw_prm_cfg_spd", psw_prm_cfg_spd_prop);
        fld_map_t psw_prm_grm_cfg_sampled_copy_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("clear_hwm", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_prm_grm_cfg_sampled_copy_thresh_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prm_grm_cfg_sampled_copy_thresh),
                    0xA0,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_sampled_copy_thresh", psw_prm_grm_cfg_sampled_copy_thresh_prop);
        fld_map_t psw_prm_grm_cfg_sf_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("xoff_thr", 14, 14),
            CREATE_ENTRY("xon_thr", 28, 14),
            CREATE_ENTRY("clear_hwm", 42, 1),
            CREATE_ENTRY("__rsvd", 43, 21)
        };
        auto psw_prm_grm_cfg_sf_thresh_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_grm_cfg_sf_thresh),
                0xB0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_sf_thresh", psw_prm_grm_cfg_sf_thresh_prop);
        fld_map_t psw_prm_grm_cfg_sx_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("clear_hwm", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_prm_grm_cfg_sx_thresh_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_grm_cfg_sx_thresh),
                0xC0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_sx_thresh", psw_prm_grm_cfg_sx_thresh_prop);
        fld_map_t psw_prm_grm_cfg_dx_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("clear_hwm", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_prm_grm_cfg_dx_thresh_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_grm_cfg_dx_thresh),
                0xD0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_dx_thresh", psw_prm_grm_cfg_dx_thresh_prop);
        fld_map_t psw_prm_grm_cfg_df_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("clear_hwm", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_prm_grm_cfg_df_thresh_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_grm_cfg_df_thresh),
                0xE0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_df_thresh", psw_prm_grm_cfg_df_thresh_prop);
        fld_map_t psw_prm_grm_cfg_fcp_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("xoff_thr", 14, 14),
            CREATE_ENTRY("xon_thr", 28, 14),
            CREATE_ENTRY("clear_hwm", 42, 1),
            CREATE_ENTRY("__rsvd", 43, 21)
        };
        auto psw_prm_grm_cfg_fcp_thresh_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_prm_grm_cfg_fcp_thresh),
                0xF0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_fcp_thresh", psw_prm_grm_cfg_fcp_thresh_prop);
        fld_map_t psw_prm_grm_cfg_nonfcp_thresh {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("xoff_thr", 14, 14),
            CREATE_ENTRY("xon_thr", 28, 14),
            CREATE_ENTRY("clear_hwm", 42, 1),
            CREATE_ENTRY("__rsvd", 43, 21)
        };
        auto psw_prm_grm_cfg_nonfcp_thresh_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prm_grm_cfg_nonfcp_thresh),
                    0x100,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prm_0, "psw_prm_grm_cfg_nonfcp_thresh", psw_prm_grm_cfg_nonfcp_thresh_prop);
        fld_map_t psw_prm_ctm_cfg_cfp_th {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto psw_prm_ctm_cfg_cfp_th_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_prm_ctm_cfg_cfp_th),
                                               0x110,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(psw_prm_0, "psw_prm_ctm_cfg_cfp_th", psw_prm_ctm_cfg_cfp_th_prop);
        fld_map_t psw_prm_ctm_cfg_speed_fp_stream {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_prm_ctm_cfg_speed_fp_stream_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prm_ctm_cfg_speed_fp_stream),
                    0x118,
                    CSR_TYPE::REG,
                    24);
        add_csr(psw_prm_0, "psw_prm_ctm_cfg_speed_fp_stream", psw_prm_ctm_cfg_speed_fp_stream_prop);
        fld_map_t psw_prm_ctm_cfg_ct_disable_dest_fp_streams {
            CREATE_ENTRY("vec", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto psw_prm_ctm_cfg_ct_disable_dest_fp_streams_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_prm_ctm_cfg_ct_disable_dest_fp_streams),
                    0x1D8,
                    CSR_TYPE::REG,
                    1);
        add_csr(psw_prm_0, "psw_prm_ctm_cfg_ct_disable_dest_fp_streams", psw_prm_ctm_cfg_ct_disable_dest_fp_streams_prop);
        fld_map_t psw_prm_stats_cntrs {
            CREATE_ENTRY("cnt", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto psw_prm_stats_cntrs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_prm_stats_cntrs),
                                            0x200,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(psw_prm_0, "psw_prm_stats_cntrs", psw_prm_stats_cntrs_prop);
// END psw_prm
    }
    {
// BEGIN psw_orm
        auto psw_orm_0 = nu_rng[0].add_an({"psw_orm"}, 0x9280000, 1, 0x0);
        fld_map_t psw_orm_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_orm_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_orm_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_orm_0, "psw_orm_timeout_thresh_cfg", psw_orm_timeout_thresh_cfg_prop);
        fld_map_t psw_orm_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_orm_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_orm_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_orm_0, "psw_orm_timeout_clr", psw_orm_timeout_clr_prop);
        fld_map_t psw_orm_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_orm_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_orm_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_orm_0, "psw_orm_spare_pio", psw_orm_spare_pio_prop);
        fld_map_t psw_orm_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_orm_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_orm_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_orm_0, "psw_orm_scratchpad", psw_orm_scratchpad_prop);
        fld_map_t psw_orm_cfg_glb_sh_thr {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("clear_hwm", 15, 1),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto psw_orm_cfg_glb_sh_thr_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_orm_cfg_glb_sh_thr),
                                               0x80,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(psw_orm_0, "psw_orm_cfg_glb_sh_thr", psw_orm_cfg_glb_sh_thr_prop);
        fld_map_t psw_orm_cfg_stats_color_en {
            CREATE_ENTRY("green", 0, 1),
            CREATE_ENTRY("yellow", 1, 1),
            CREATE_ENTRY("red", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto psw_orm_cfg_stats_color_en_prop = csr_prop_t(
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
        };
        auto psw_orm_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_orm_sram_err_inj_cfg),
                0xA8,
                CSR_TYPE::REG,
                1);
        add_csr(psw_orm_0, "psw_orm_sram_err_inj_cfg", psw_orm_sram_err_inj_cfg_prop);
        fld_map_t psw_orm_mem_q_cfg {
            CREATE_ENTRY("min_thr", 0, 15),
            CREATE_ENTRY("static_sh_thr_green", 15, 15),
            CREATE_ENTRY("sh_dynamic_en", 30, 1),
            CREATE_ENTRY("sh_thr_alpha", 31, 4),
            CREATE_ENTRY("sh_thr_offset_yellow", 35, 15),
            CREATE_ENTRY("sh_thr_offset_red", 50, 15),
            CREATE_ENTRY("__rsvd", 65, 63)
        };
        auto psw_orm_mem_q_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_orm_mem_q_cfg),
                                          0x4000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(psw_orm_0, "psw_orm_mem_q_cfg", psw_orm_mem_q_cfg_prop);
        fld_map_t psw_orm_mem_port_cfg {
            CREATE_ENTRY("min_thr", 0, 15),
            CREATE_ENTRY("sh_thr", 15, 15),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto psw_orm_mem_port_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(psw_orm_mem_port_cfg),
                                             0x54000,
                                             CSR_TYPE::TBL,
                                             1);
        add_csr(psw_orm_0, "psw_orm_mem_port_cfg", psw_orm_mem_port_cfg_prop);
        fld_map_t psw_orm_mem_stats_q_peak_cnt {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_orm_mem_stats_q_peak_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_orm_mem_stats_q_peak_cnt),
                    0x66000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_orm_0, "psw_orm_mem_stats_q_peak_cnt", psw_orm_mem_stats_q_peak_cnt_prop);
        fld_map_t psw_orm_mem_stats_port_sh_peak_cnt {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_orm_mem_stats_port_sh_peak_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_orm_mem_stats_port_sh_peak_cnt),
                    0x77000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_orm_0, "psw_orm_mem_stats_port_sh_peak_cnt", psw_orm_mem_stats_port_sh_peak_cnt_prop);
// END psw_orm
    }
    {
// BEGIN psw_irm
        auto psw_irm_0 = nu_rng[0].add_an({"psw_irm"}, 0x9300000, 1, 0x0);
        fld_map_t psw_irm_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_irm_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_irm_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_irm_0, "psw_irm_timeout_thresh_cfg", psw_irm_timeout_thresh_cfg_prop);
        fld_map_t psw_irm_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_irm_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_irm_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_irm_0, "psw_irm_timeout_clr", psw_irm_timeout_clr_prop);
        fld_map_t psw_irm_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_irm_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_irm_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_irm_0, "psw_irm_spare_pio", psw_irm_spare_pio_prop);
        fld_map_t psw_irm_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_irm_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_irm_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_irm_0, "psw_irm_scratchpad", psw_irm_scratchpad_prop);
        fld_map_t psw_irm_cfg_glb_sh_thr {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("clear_hwm", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_irm_cfg_glb_sh_thr_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_irm_cfg_glb_sh_thr),
                                               0x88,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(psw_irm_0, "psw_irm_cfg_glb_sh_thr", psw_irm_cfg_glb_sh_thr_prop);
        fld_map_t psw_irm_cfg_glb_hdrm_thr {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("clear_hwm", 14, 1),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_irm_cfg_glb_hdrm_thr_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_irm_cfg_glb_hdrm_thr),
                0x98,
                CSR_TYPE::REG,
                1);
        add_csr(psw_irm_0, "psw_irm_cfg_glb_hdrm_thr", psw_irm_cfg_glb_hdrm_thr_prop);
        fld_map_t psw_irm_cfg_glb_sh_xon_thr {
            CREATE_ENTRY("val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto psw_irm_cfg_glb_sh_xon_thr_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_irm_cfg_glb_sh_xon_thr),
                0xA0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_irm_0, "psw_irm_cfg_glb_sh_xon_thr", psw_irm_cfg_glb_sh_xon_thr_prop);
        fld_map_t psw_irm_cfg_pri_to_pg_fp {
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
        };
        auto psw_irm_cfg_pri_to_pg_fp_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_fp),
                0xA8,
                CSR_TYPE::REG,
                24);
        add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_fp", psw_irm_cfg_pri_to_pg_fp_prop);
        fld_map_t psw_irm_cfg_pri_to_pg_ep {
            CREATE_ENTRY("pri0", 0, 3),
            CREATE_ENTRY("pri1", 3, 3),
            CREATE_ENTRY("pri2", 6, 3),
            CREATE_ENTRY("pri3", 9, 3),
            CREATE_ENTRY("pri4", 12, 3),
            CREATE_ENTRY("pri5", 15, 3),
            CREATE_ENTRY("pri6", 18, 3),
            CREATE_ENTRY("pri7", 21, 3),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto psw_irm_cfg_pri_to_pg_ep_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_irm_cfg_pri_to_pg_ep),
                0x168,
                CSR_TYPE::REG,
                24);
        add_csr(psw_irm_0, "psw_irm_cfg_pri_to_pg_ep", psw_irm_cfg_pri_to_pg_ep_prop);
        fld_map_t psw_irm_cfg_pfc_en {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_irm_cfg_pfc_en_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_irm_cfg_pfc_en),
                                           0x228,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_irm_0, "psw_irm_cfg_pfc_en", psw_irm_cfg_pfc_en_prop);
        fld_map_t psw_irm_cfg_use_hdrm_after_xoff {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_irm_cfg_use_hdrm_after_xoff_prop = csr_prop_t(
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
        };
        auto psw_irm_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_irm_sram_err_inj_cfg),
                0x238,
                CSR_TYPE::REG,
                1);
        add_csr(psw_irm_0, "psw_irm_sram_err_inj_cfg", psw_irm_sram_err_inj_cfg_prop);
        fld_map_t psw_irm_mem_enq_pg_cfg {
            CREATE_ENTRY("min_thr", 0, 14),
            CREATE_ENTRY("sh_thr", 14, 14),
            CREATE_ENTRY("hdrm_thr", 28, 14),
            CREATE_ENTRY("xoff_en", 42, 1),
            CREATE_ENTRY("__rsvd", 43, 21)
        };
        auto psw_irm_mem_enq_pg_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_irm_mem_enq_pg_cfg),
                                               0xE000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_irm_0, "psw_irm_mem_enq_pg_cfg", psw_irm_mem_enq_pg_cfg_prop);
        fld_map_t psw_irm_mem_deq_pg_cfg {
            CREATE_ENTRY("sh_xon_thr", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto psw_irm_mem_deq_pg_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_irm_mem_deq_pg_cfg),
                                               0x1E000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_irm_0, "psw_irm_mem_deq_pg_cfg", psw_irm_mem_deq_pg_cfg_prop);
        fld_map_t psw_irm_mem_stats_pg_peak_cnt {
            CREATE_ENTRY("total_val", 0, 14),
            CREATE_ENTRY("hdrm_val", 14, 14),
            CREATE_ENTRY("__rsvd", 28, 36)
        };
        auto psw_irm_mem_stats_pg_peak_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(psw_irm_mem_stats_pg_peak_cnt),
                    0x4E000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(psw_irm_0, "psw_irm_mem_stats_pg_peak_cnt", psw_irm_mem_stats_pg_peak_cnt_prop);
// END psw_irm
    }
    {
// BEGIN psw_wred
        auto psw_wred_0 = nu_rng[0].add_an({"psw_wred"}, 0x9380000, 1, 0x0);
        fld_map_t psw_wred_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_wred_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_wred_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_wred_0, "psw_wred_timeout_thresh_cfg", psw_wred_timeout_thresh_cfg_prop);
        fld_map_t psw_wred_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_wred_timeout_clr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(psw_wred_timeout_clr),
                                             0x10,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(psw_wred_0, "psw_wred_timeout_clr", psw_wred_timeout_clr_prop);
        fld_map_t psw_wred_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_wred_spare_pio_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_wred_spare_pio),
                                           0x70,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_wred_0, "psw_wred_spare_pio", psw_wred_spare_pio_prop);
        fld_map_t psw_wred_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_wred_scratchpad_prop = csr_prop_t(
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
        };
        auto psw_wred_cfg_avg_q_prop = csr_prop_t(
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
        };
        auto psw_wred_cfg_ecn_glb_sh_thresh_prop = csr_prop_t(
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
        };
        auto psw_wred_cfg_stats_color_en_prop = csr_prop_t(
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
        };
        auto psw_wred_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_wred_sram_err_inj_cfg),
                0x98,
                CSR_TYPE::REG,
                1);
        add_csr(psw_wred_0, "psw_wred_sram_err_inj_cfg", psw_wred_sram_err_inj_cfg_prop);
        fld_map_t psw_wred_mem_avg_q_cfg {
            CREATE_ENTRY("weight", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto psw_wred_mem_avg_q_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_wred_mem_avg_q_cfg),
                                               0x12000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_wred_0, "psw_wred_mem_avg_q_cfg", psw_wred_mem_avg_q_cfg_prop);
        fld_map_t psw_wred_mem_enq_q_cfg {
            CREATE_ENTRY("wred_en", 0, 1),
            CREATE_ENTRY("ecn_en", 1, 1),
            CREATE_ENTRY("profile", 2, 5),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto psw_wred_mem_enq_q_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_wred_mem_enq_q_cfg),
                                               0x32000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_wred_0, "psw_wred_mem_enq_q_cfg", psw_wred_mem_enq_q_cfg_prop);
        fld_map_t psw_wred_mem_enq_profile {
            CREATE_ENTRY("min_thd", 0, 15),
            CREATE_ENTRY("max_thd", 15, 15),
            CREATE_ENTRY("rate_index", 30, 4),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto psw_wred_mem_enq_profile_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_wred_mem_enq_profile),
                0x42000,
                CSR_TYPE::TBL,
                1);
        add_csr(psw_wred_0, "psw_wred_mem_enq_profile", psw_wred_mem_enq_profile_prop);
        fld_map_t psw_wred_mem_enq_prob {
            CREATE_ENTRY("val", 0, 11),
            CREATE_ENTRY("__rsvd", 11, 53)
        };
        auto psw_wred_mem_enq_prob_prop = csr_prop_t(
                                              std::make_shared<csr_s>(psw_wred_mem_enq_prob),
                                              0x44000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(psw_wred_0, "psw_wred_mem_enq_prob", psw_wred_mem_enq_prob_prop);
        fld_map_t psw_wred_mem_deq_q_cfg {
            CREATE_ENTRY("ecn_en", 0, 1),
            CREATE_ENTRY("profile", 1, 5),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto psw_wred_mem_deq_q_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_wred_mem_deq_q_cfg),
                                               0x46000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_wred_0, "psw_wred_mem_deq_q_cfg", psw_wred_mem_deq_q_cfg_prop);
        fld_map_t psw_wred_mem_deq_profile {
            CREATE_ENTRY("min_thd", 0, 15),
            CREATE_ENTRY("max_thd", 15, 15),
            CREATE_ENTRY("rate_index", 30, 4),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto psw_wred_mem_deq_profile_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_wred_mem_deq_profile),
                0x56000,
                CSR_TYPE::TBL,
                1);
        add_csr(psw_wred_0, "psw_wred_mem_deq_profile", psw_wred_mem_deq_profile_prop);
        fld_map_t psw_wred_mem_deq_prob {
            CREATE_ENTRY("val", 0, 11),
            CREATE_ENTRY("__rsvd", 11, 53)
        };
        auto psw_wred_mem_deq_prob_prop = csr_prop_t(
                                              std::make_shared<csr_s>(psw_wred_mem_deq_prob),
                                              0x58000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(psw_wred_0, "psw_wred_mem_deq_prob", psw_wred_mem_deq_prob_prop);
// END psw_wred
    }
    {
// BEGIN psw_clm
        auto psw_clm_0 = nu_rng[0].add_an({"psw_clm"}, 0x9400000, 1, 0x0);
        fld_map_t psw_clm_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_clm_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_clm_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_clm_0, "psw_clm_timeout_thresh_cfg", psw_clm_timeout_thresh_cfg_prop);
        fld_map_t psw_clm_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_clm_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_clm_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_clm_0, "psw_clm_timeout_clr", psw_clm_timeout_clr_prop);
        fld_map_t psw_clm_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_clm_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_clm_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_clm_0, "psw_clm_spare_pio", psw_clm_spare_pio_prop);
        fld_map_t psw_clm_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_clm_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_clm_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_clm_0, "psw_clm_scratchpad", psw_clm_scratchpad_prop);
        fld_map_t psw_clm_mem_init_start_cfg {
            CREATE_ENTRY("clm_link", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_clm_mem_init_start_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_clm_mem_init_start_cfg),
                0x80,
                CSR_TYPE::REG,
                1);
        add_csr(psw_clm_0, "psw_clm_mem_init_start_cfg", psw_clm_mem_init_start_cfg_prop);
        fld_map_t psw_clm_sram_err_inj_cfg {
            CREATE_ENTRY("pbuf_ucell3", 0, 1),
            CREATE_ENTRY("pbuf_ucell2", 1, 1),
            CREATE_ENTRY("pbuf_ucell1", 2, 1),
            CREATE_ENTRY("pbuf_ucell0", 3, 1),
            CREATE_ENTRY("link", 4, 1),
            CREATE_ENTRY("err_type", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto psw_clm_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_clm_sram_err_inj_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(psw_clm_0, "psw_clm_sram_err_inj_cfg", psw_clm_sram_err_inj_cfg_prop);
        fld_map_t psw_clm_mem_link {
            CREATE_ENTRY("cell_size", 0, 8),
            CREATE_ENTRY("eop", 8, 1),
            CREATE_ENTRY("cell_ptr", 9, 14),
            CREATE_ENTRY("__rsvd", 23, 41)
        };
        auto psw_clm_mem_link_prop = csr_prop_t(
                                         std::make_shared<csr_s>(psw_clm_mem_link),
                                         0x20000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(psw_clm_0, "psw_clm_mem_link", psw_clm_mem_link_prop);
// END psw_clm
    }
    {
// BEGIN psw_pqm
        auto psw_pqm_0 = nu_rng[0].add_an({"psw_pqm"}, 0x9800000, 1, 0x0);
        fld_map_t psw_pqm_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_pqm_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pqm_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pqm_0, "psw_pqm_timeout_thresh_cfg", psw_pqm_timeout_thresh_cfg_prop);
        fld_map_t psw_pqm_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_pqm_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_pqm_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_pqm_0, "psw_pqm_timeout_clr", psw_pqm_timeout_clr_prop);
        fld_map_t psw_pqm_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_pqm_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_pqm_0, "psw_pqm_spare_pio", psw_pqm_spare_pio_prop);
        fld_map_t psw_pqm_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_scratchpad_prop = csr_prop_t(
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
        };
        auto psw_pqm_mem_init_start_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pqm_mem_init_start_cfg),
                0x80,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pqm_0, "psw_pqm_mem_init_start_cfg", psw_pqm_mem_init_start_cfg_prop);
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
        };
        auto psw_pqm_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_pqm_sram_err_inj_cfg),
                0xE0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_pqm_0, "psw_pqm_sram_err_inj_cfg", psw_pqm_sram_err_inj_cfg_prop);
        fld_map_t psw_pqm_mem_pkt_desc {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto psw_pqm_mem_pkt_desc_prop = csr_prop_t(
                                             std::make_shared<csr_s>(psw_pqm_mem_pkt_desc),
                                             0x20000,
                                             CSR_TYPE::TBL,
                                             1);
        add_csr(psw_pqm_0, "psw_pqm_mem_pkt_desc", psw_pqm_mem_pkt_desc_prop);
        fld_map_t psw_pqm_mem_link {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_pqm_mem_link_prop = csr_prop_t(
                                         std::make_shared<csr_s>(psw_pqm_mem_link),
                                         0x140000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(psw_pqm_0, "psw_pqm_mem_link", psw_pqm_mem_link_prop);
        fld_map_t psw_pqm_mem_head_main {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_pqm_mem_head_main_prop = csr_prop_t(
                                              std::make_shared<csr_s>(psw_pqm_mem_head_main),
                                              0x340000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(psw_pqm_0, "psw_pqm_mem_head_main", psw_pqm_mem_head_main_prop);
        fld_map_t psw_pqm_mem_head_shd {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_pqm_mem_head_shd_prop = csr_prop_t(
                                             std::make_shared<csr_s>(psw_pqm_mem_head_shd),
                                             0x350000,
                                             CSR_TYPE::TBL,
                                             1);
        add_csr(psw_pqm_0, "psw_pqm_mem_head_shd", psw_pqm_mem_head_shd_prop);
        fld_map_t psw_pqm_mem_tail_main {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_pqm_mem_tail_main_prop = csr_prop_t(
                                              std::make_shared<csr_s>(psw_pqm_mem_tail_main),
                                              0x360000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(psw_pqm_0, "psw_pqm_mem_tail_main", psw_pqm_mem_tail_main_prop);
        fld_map_t psw_pqm_mem_tail_shd {
            CREATE_ENTRY("val", 0, 15),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto psw_pqm_mem_tail_shd_prop = csr_prop_t(
                                             std::make_shared<csr_s>(psw_pqm_mem_tail_shd),
                                             0x370000,
                                             CSR_TYPE::TBL,
                                             1);
        add_csr(psw_pqm_0, "psw_pqm_mem_tail_shd", psw_pqm_mem_tail_shd_prop);
        fld_map_t psw_pqm_dbg_probe_enq0 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_enq0_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_enq0),
                                               0x400000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq0", psw_pqm_dbg_probe_enq0_prop);
        fld_map_t psw_pqm_dbg_probe_enq1 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_enq1_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_enq1),
                                               0x400200,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq1", psw_pqm_dbg_probe_enq1_prop);
        fld_map_t psw_pqm_dbg_probe_enq2 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_enq2_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_enq2),
                                               0x400400,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq2", psw_pqm_dbg_probe_enq2_prop);
        fld_map_t psw_pqm_dbg_probe_enq3 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_enq3_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_enq3),
                                               0x400600,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_enq3", psw_pqm_dbg_probe_enq3_prop);
        fld_map_t psw_pqm_dbg_probe_deq0 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_deq0_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_deq0),
                                               0x400800,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq0", psw_pqm_dbg_probe_deq0_prop);
        fld_map_t psw_pqm_dbg_probe_deq1 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_deq1_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_deq1),
                                               0x400A00,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq1", psw_pqm_dbg_probe_deq1_prop);
        fld_map_t psw_pqm_dbg_probe_deq2 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_deq2_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_deq2),
                                               0x400C00,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq2", psw_pqm_dbg_probe_deq2_prop);
        fld_map_t psw_pqm_dbg_probe_deq3 {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_pqm_dbg_probe_deq3_prop = csr_prop_t(
                                               std::make_shared<csr_s>(psw_pqm_dbg_probe_deq3),
                                               0x400E00,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(psw_pqm_0, "psw_pqm_dbg_probe_deq3", psw_pqm_dbg_probe_deq3_prop);
        fld_map_t psw_pqm_stats_cntrs {
            CREATE_ENTRY("cnt", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto psw_pqm_stats_cntrs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_pqm_stats_cntrs),
                                            0x401000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(psw_pqm_0, "psw_pqm_stats_cntrs", psw_pqm_stats_cntrs_prop);
// END psw_pqm
    }
    {
// BEGIN psw_cfp
        auto psw_cfp_0 = nu_rng[0].add_an({"psw_cfp"}, 0xA000000, 1, 0x0);
        fld_map_t psw_cfp_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto psw_cfp_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_cfp_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(psw_cfp_0, "psw_cfp_timeout_thresh_cfg", psw_cfp_timeout_thresh_cfg_prop);
        fld_map_t psw_cfp_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_cfp_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(psw_cfp_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(psw_cfp_0, "psw_cfp_timeout_clr", psw_cfp_timeout_clr_prop);
        fld_map_t psw_cfp_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_cfp_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(psw_cfp_spare_pio),
                                          0x98,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(psw_cfp_0, "psw_cfp_spare_pio", psw_cfp_spare_pio_prop);
        fld_map_t psw_cfp_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_cfp_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(psw_cfp_scratchpad),
                                           0xA0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(psw_cfp_0, "psw_cfp_scratchpad", psw_cfp_scratchpad_prop);
        fld_map_t psw_cfp_mem_init_start_cfg {
            CREATE_ENTRY("cct", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_cfp_mem_init_start_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_cfp_mem_init_start_cfg),
                0xA8,
                CSR_TYPE::REG,
                1);
        add_csr(psw_cfp_0, "psw_cfp_mem_init_start_cfg", psw_cfp_mem_init_start_cfg_prop);
        fld_map_t psw_cfp_cfg_clear_hwm {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto psw_cfp_cfg_clear_hwm_prop = csr_prop_t(
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
        };
        auto psw_cfp_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(psw_cfp_sram_err_inj_cfg),
                0xC8,
                CSR_TYPE::REG,
                1);
        add_csr(psw_cfp_0, "psw_cfp_sram_err_inj_cfg", psw_cfp_sram_err_inj_cfg_prop);
        fld_map_t psw_cfp_mem_cct {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_cfp_mem_cct_prop = csr_prop_t(
                                        std::make_shared<csr_s>(psw_cfp_mem_cct),
                                        0x800,
                                        CSR_TYPE::TBL,
                                        1);
        add_csr(psw_cfp_0, "psw_cfp_mem_cct", psw_cfp_mem_cct_prop);
        fld_map_t psw_cfp_bitalloc {
            CREATE_ENTRY("val", 0, 64)
        };
        auto psw_cfp_bitalloc_prop = csr_prop_t(
                                         std::make_shared<csr_s>(psw_cfp_bitalloc),
                                         0x8000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(psw_cfp_0, "psw_cfp_bitalloc", psw_cfp_bitalloc_prop);
// END psw_cfp
    }
    {
// BEGIN etdp
        auto etdp_0 = nu_rng[0].add_an({"etdp"}, 0xA080000, 1, 0x0);
        fld_map_t etdp_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto etdp_timeout_thresh_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(etdp_timeout_thresh_cfg),
                                                0x0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(etdp_0, "etdp_timeout_thresh_cfg", etdp_timeout_thresh_cfg_prop);
        fld_map_t etdp_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto etdp_timeout_clr_prop = csr_prop_t(
                                         std::make_shared<csr_s>(etdp_timeout_clr),
                                         0x10,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etdp_0, "etdp_timeout_clr", etdp_timeout_clr_prop);
        fld_map_t etdp_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto etdp_spare_pio_prop = csr_prop_t(
                                       std::make_shared<csr_s>(etdp_spare_pio),
                                       0x70,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(etdp_0, "etdp_spare_pio", etdp_spare_pio_prop);
        fld_map_t etdp_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto etdp_scratchpad_prop = csr_prop_t(
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
        };
        auto etdp_cfg_prop = csr_prop_t(
                                 std::make_shared<csr_s>(etdp_cfg),
                                 0x80,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(etdp_0, "etdp_cfg", etdp_cfg_prop);
        fld_map_t etdp_fcp_data_blk_sz_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto etdp_fcp_data_blk_sz_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(etdp_fcp_data_blk_sz_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "etdp_fcp_data_blk_sz_cfg", etdp_fcp_data_blk_sz_cfg_prop);
        fld_map_t etdp_pkt_sz_adj {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto etdp_pkt_sz_adj_prop = csr_prop_t(
                                        std::make_shared<csr_s>(etdp_pkt_sz_adj),
                                        0x98,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(etdp_0, "etdp_pkt_sz_adj", etdp_pkt_sz_adj_prop);
        fld_map_t etdp_fpkt_tcp_flags {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto etdp_fpkt_tcp_flags_prop = csr_prop_t(
                                            std::make_shared<csr_s>(etdp_fpkt_tcp_flags),
                                            0xA0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etdp_0, "etdp_fpkt_tcp_flags", etdp_fpkt_tcp_flags_prop);
        fld_map_t etdp_lpkt_tcp_flags {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto etdp_lpkt_tcp_flags_prop = csr_prop_t(
                                            std::make_shared<csr_s>(etdp_lpkt_tcp_flags),
                                            0xA8,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etdp_0, "etdp_lpkt_tcp_flags", etdp_lpkt_tcp_flags_prop);
        fld_map_t etdp_mpkt_tcp_flags {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto etdp_mpkt_tcp_flags_prop = csr_prop_t(
                                            std::make_shared<csr_s>(etdp_mpkt_tcp_flags),
                                            0xB0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etdp_0, "etdp_mpkt_tcp_flags", etdp_mpkt_tcp_flags_prop);
        fld_map_t fcp_cfg {
            CREATE_ENTRY("gph_size", 0, 2),
            CREATE_ENTRY("fcp_qos_count", 2, 2),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fcp_cfg_prop = csr_prop_t(
                                std::make_shared<csr_s>(fcp_cfg),
                                0xB8,
                                CSR_TYPE::REG,
                                1);
        add_csr(etdp_0, "fcp_cfg", fcp_cfg_prop);
        fld_map_t fcp_hdr_dmac {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto fcp_hdr_dmac_prop = csr_prop_t(
                                     std::make_shared<csr_s>(fcp_hdr_dmac),
                                     0xC0,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(etdp_0, "fcp_hdr_dmac", fcp_hdr_dmac_prop);
        fld_map_t fcp_hdr_smac {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto fcp_hdr_smac_prop = csr_prop_t(
                                     std::make_shared<csr_s>(fcp_hdr_smac),
                                     0xC8,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(etdp_0, "fcp_hdr_smac", fcp_hdr_smac_prop);
        fld_map_t fcp_hdr_v4_etype {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcp_hdr_v4_etype_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fcp_hdr_v4_etype),
                                         0xD0,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etdp_0, "fcp_hdr_v4_etype", fcp_hdr_v4_etype_prop);
        fld_map_t fcp_hdr_req_dscp_ecn {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_req_dscp_ecn_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fcp_hdr_req_dscp_ecn),
                                             0xD8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(etdp_0, "fcp_hdr_req_dscp_ecn", fcp_hdr_req_dscp_ecn_prop);
        fld_map_t fcp_hdr_gnt_dscp_ecn {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_gnt_dscp_ecn_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fcp_hdr_gnt_dscp_ecn),
                                             0xE0,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(etdp_0, "fcp_hdr_gnt_dscp_ecn", fcp_hdr_gnt_dscp_ecn_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q0 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q0_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q0),
                0xE8,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q0", fcp_hdr_data_dscp_ecn_q0_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q1 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q1_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q1),
                0xF0,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q1", fcp_hdr_data_dscp_ecn_q1_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q2 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q2_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q2),
                0xF8,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q2", fcp_hdr_data_dscp_ecn_q2_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q3 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q3_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q3),
                0x100,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q3", fcp_hdr_data_dscp_ecn_q3_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q4 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q4_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q4),
                0x108,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q4", fcp_hdr_data_dscp_ecn_q4_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q5 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q5_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q5),
                0x110,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q5", fcp_hdr_data_dscp_ecn_q5_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q6 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q6_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q6),
                0x118,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q6", fcp_hdr_data_dscp_ecn_q6_prop);
        fld_map_t fcp_hdr_data_dscp_ecn_q7 {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_data_dscp_ecn_q7_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_data_dscp_ecn_q7),
                0x120,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_data_dscp_ecn_q7", fcp_hdr_data_dscp_ecn_q7_prop);
        fld_map_t fcp_hdr_ipv4_id {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcp_hdr_ipv4_id_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fcp_hdr_ipv4_id),
                                        0x128,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(etdp_0, "fcp_hdr_ipv4_id", fcp_hdr_ipv4_id_prop);
        fld_map_t fcp_hdr_frag_flags_offset {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcp_hdr_frag_flags_offset_prop = csr_prop_t(
                std::make_shared<csr_s>(fcp_hdr_frag_flags_offset),
                0x130,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "fcp_hdr_frag_flags_offset", fcp_hdr_frag_flags_offset_prop);
        fld_map_t fcp_hdr_ipv4_ttl {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_hdr_ipv4_ttl_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fcp_hdr_ipv4_ttl),
                                         0x138,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etdp_0, "fcp_hdr_ipv4_ttl", fcp_hdr_ipv4_ttl_prop);
        fld_map_t udp_over_ipv4_proto {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto udp_over_ipv4_proto_prop = csr_prop_t(
                                            std::make_shared<csr_s>(udp_over_ipv4_proto),
                                            0x140,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etdp_0, "udp_over_ipv4_proto", udp_over_ipv4_proto_prop);
        fld_map_t fcp_over_ipv4_proto {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fcp_over_ipv4_proto_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fcp_over_ipv4_proto),
                                            0x148,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etdp_0, "fcp_over_ipv4_proto", fcp_over_ipv4_proto_prop);
        fld_map_t fcp_hdr_ipv4_sip {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcp_hdr_ipv4_sip_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fcp_hdr_ipv4_sip),
                                         0x150,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etdp_0, "fcp_hdr_ipv4_sip", fcp_hdr_ipv4_sip_prop);
        fld_map_t fcp_hdr_udp_dport {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcp_hdr_udp_dport_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fcp_hdr_udp_dport),
                                          0x158,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(etdp_0, "fcp_hdr_udp_dport", fcp_hdr_udp_dport_prop);
        fld_map_t fcp_hdr_udp_csum {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcp_hdr_udp_csum_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fcp_hdr_udp_csum),
                                         0x160,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etdp_0, "fcp_hdr_udp_csum", fcp_hdr_udp_csum_prop);
        fld_map_t fcp_hdr_ver {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fcp_hdr_ver_prop = csr_prop_t(
                                    std::make_shared<csr_s>(fcp_hdr_ver),
                                    0x168,
                                    CSR_TYPE::REG,
                                    1);
        add_csr(etdp_0, "fcp_hdr_ver", fcp_hdr_ver_prop);
        fld_map_t fcp_hdr_rsvd {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fcp_hdr_rsvd_prop = csr_prop_t(
                                     std::make_shared<csr_s>(fcp_hdr_rsvd),
                                     0x170,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(etdp_0, "fcp_hdr_rsvd", fcp_hdr_rsvd_prop);
        fld_map_t etdp_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto etdp_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(etdp_fla_ring_module_id_cfg),
                0x178,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "etdp_fla_ring_module_id_cfg", etdp_fla_ring_module_id_cfg_prop);
        fld_map_t etdp_key_lu_63_0 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto etdp_key_lu_63_0_prop = csr_prop_t(
                                         std::make_shared<csr_s>(etdp_key_lu_63_0),
                                         0x0,
                                         CSR_TYPE::REG_LST,
                                         1);
        add_csr(etdp_0, "etdp_key_lu_63_0", etdp_key_lu_63_0_prop);
        fld_map_t etdp_key_lu_127_64 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto etdp_key_lu_127_64_prop = csr_prop_t(
                                           std::make_shared<csr_s>(etdp_key_lu_127_64),
                                           0x0,
                                           CSR_TYPE::REG_LST,
                                           1);
        add_csr(etdp_0, "etdp_key_lu_127_64", etdp_key_lu_127_64_prop);
        fld_map_t etdp_key_lu_191_128 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto etdp_key_lu_191_128_prop = csr_prop_t(
                                            std::make_shared<csr_s>(etdp_key_lu_191_128),
                                            0x0,
                                            CSR_TYPE::REG_LST,
                                            1);
        add_csr(etdp_0, "etdp_key_lu_191_128", etdp_key_lu_191_128_prop);
        fld_map_t etdp_key_lu_255_192 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto etdp_key_lu_255_192_prop = csr_prop_t(
                                            std::make_shared<csr_s>(etdp_key_lu_255_192),
                                            0x0,
                                            CSR_TYPE::REG_LST,
                                            1);
        add_csr(etdp_0, "etdp_key_lu_255_192", etdp_key_lu_255_192_prop);
        fld_map_t etdp_key_len_lu {
            CREATE_ENTRY("key_len", 0, 2),
            CREATE_ENTRY("salt", 2, 16),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto etdp_key_len_lu_prop = csr_prop_t(
                                        std::make_shared<csr_s>(etdp_key_len_lu),
                                        0x3A0,
                                        CSR_TYPE::REG_LST,
                                        17);
        add_csr(etdp_0, "etdp_key_len_lu", etdp_key_len_lu_prop);
        fld_map_t etdp_fcp_stream_map {
            CREATE_ENTRY("fcp_stream", 0, 3),
            CREATE_ENTRY("fcp_present", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto etdp_fcp_stream_map_prop = csr_prop_t(
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
        };
        auto etdp_sram_err_inj_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(etdp_sram_err_inj_cfg),
                                              0x430,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(etdp_0, "etdp_sram_err_inj_cfg", etdp_sram_err_inj_cfg_prop);
        fld_map_t etdp_watchdog_timer_period {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto etdp_watchdog_timer_period_prop = csr_prop_t(
                std::make_shared<csr_s>(etdp_watchdog_timer_period),
                0x488,
                CSR_TYPE::REG,
                1);
        add_csr(etdp_0, "etdp_watchdog_timer_period", etdp_watchdog_timer_period_prop);
        fld_map_t etdp_dbg_probe_pswif_pcnt_dhs {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto etdp_dbg_probe_pswif_pcnt_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(etdp_dbg_probe_pswif_pcnt_dhs),
                    0x4C0,
                    CSR_TYPE::TBL,
                    1);
        add_csr(etdp_0, "etdp_dbg_probe_pswif_pcnt_dhs", etdp_dbg_probe_pswif_pcnt_dhs_prop);
        fld_map_t etdp_dbg_probe_pswif_pbyte_dhs {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto etdp_dbg_probe_pswif_pbyte_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(etdp_dbg_probe_pswif_pbyte_dhs),
                    0x6C0,
                    CSR_TYPE::TBL,
                    1);
        add_csr(etdp_0, "etdp_dbg_probe_pswif_pbyte_dhs", etdp_dbg_probe_pswif_pbyte_dhs_prop);
// END etdp
    }
    {
// BEGIN dma_nu
        auto dma_nu_0 = nu_rng[0].add_an({"dma_nu"}, 0xA380000, 1, 0x0);
        fld_map_t dma_nu_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto dma_nu_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(dma_nu_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(dma_nu_0, "dma_nu_timeout_thresh_cfg", dma_nu_timeout_thresh_cfg_prop);
        fld_map_t dma_nu_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto dma_nu_timeout_clr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(dma_nu_timeout_clr),
                                           0x10,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(dma_nu_0, "dma_nu_timeout_clr", dma_nu_timeout_clr_prop);
        fld_map_t dma_nu_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto dma_nu_spare_pio_prop = csr_prop_t(
                                         std::make_shared<csr_s>(dma_nu_spare_pio),
                                         0x138,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(dma_nu_0, "dma_nu_spare_pio", dma_nu_spare_pio_prop);
        fld_map_t dma_nu_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto dma_nu_scratchpad_prop = csr_prop_t(
                                          std::make_shared<csr_s>(dma_nu_scratchpad),
                                          0x140,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(dma_nu_0, "dma_nu_scratchpad", dma_nu_scratchpad_prop);
        fld_map_t dma_nu_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto dma_nu_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(dma_nu_fla_ring_module_id_cfg),
                    0x148,
                    CSR_TYPE::REG,
                    1);
        add_csr(dma_nu_0, "dma_nu_fla_ring_module_id_cfg", dma_nu_fla_ring_module_id_cfg_prop);
        fld_map_t dma_nu_cfg {
            CREATE_ENTRY("addr_to_ins_en", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto dma_nu_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(dma_nu_cfg),
                                   0x150,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(dma_nu_0, "dma_nu_cfg", dma_nu_cfg_prop);
        fld_map_t dma_nu_f1_rd_tag_cfg {
            CREATE_ENTRY("dph_tag_min", 0, 8),
            CREATE_ENTRY("dph_tag_max", 8, 8),
            CREATE_ENTRY("gtr_tag_min", 16, 9),
            CREATE_ENTRY("gtr_tag_max", 25, 9),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto dma_nu_f1_rd_tag_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(dma_nu_f1_rd_tag_cfg),
                                             0x158,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(dma_nu_0, "dma_nu_f1_rd_tag_cfg", dma_nu_f1_rd_tag_cfg_prop);
        fld_map_t dma_nu_lid_cfg {
            CREATE_ENTRY("min_lid", 0, 5),
            CREATE_ENTRY("max_lid", 5, 5),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto dma_nu_lid_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dma_nu_lid_cfg),
                                       0x160,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dma_nu_0, "dma_nu_lid_cfg", dma_nu_lid_cfg_prop);
        fld_map_t dma_nu_req_limit_cfg {
            CREATE_ENTRY("bm_rd_limit", 0, 9),
            CREATE_ENTRY("hbm_rd_limit", 9, 9),
            CREATE_ENTRY("ddr_rd_limit", 18, 9),
            CREATE_ENTRY("coh_rd_limit", 27, 9),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_req_limit_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(dma_nu_req_limit_cfg),
                                             0x168,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(dma_nu_0, "dma_nu_req_limit_cfg", dma_nu_req_limit_cfg_prop);
        fld_map_t dma_nu_rate_limit_cfg {
            CREATE_ENTRY("bm_rate_limit", 0, 8),
            CREATE_ENTRY("hbm_rate_limit", 8, 8),
            CREATE_ENTRY("ddr_rate_limit", 16, 8),
            CREATE_ENTRY("coh_rate_limit", 24, 8),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto dma_nu_rate_limit_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dma_nu_rate_limit_cfg),
                                              0x170,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(dma_nu_0, "dma_nu_rate_limit_cfg", dma_nu_rate_limit_cfg_prop);
        fld_map_t dma_nu_cmp_cfg {
            CREATE_ENTRY("wu_map_en", 0, 1),
            CREATE_ENTRY("wu_opcodes", 1, 32),
            CREATE_ENTRY("__rsvd", 33, 31)
        };
        auto dma_nu_cmp_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dma_nu_cmp_cfg),
                                       0x178,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dma_nu_0, "dma_nu_cmp_cfg", dma_nu_cmp_cfg_prop);
        fld_map_t dma_nu_alloc_cfg_done {
            CREATE_ENTRY("dph_alloc_done", 0, 1),
            CREATE_ENTRY("gtr_f1_tag_alloc_done", 1, 1),
            CREATE_ENTRY("str_init_tag_trigger", 2, 1),
            CREATE_ENTRY("cmp_init_tag_trigger", 3, 1),
            CREATE_ENTRY("dmi_remote_crd_init_trigger", 4, 1),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto dma_nu_alloc_cfg_done_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dma_nu_alloc_cfg_done),
                                              0x180,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(dma_nu_0, "dma_nu_alloc_cfg_done", dma_nu_alloc_cfg_done_prop);
        fld_map_t dma_nu_dph_cmd_buf_cfg {
            CREATE_ENTRY("min_num", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto dma_nu_dph_cmd_buf_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_dph_cmd_buf_cfg),
                                               0x190,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_dph_cmd_buf_cfg", dma_nu_dph_cmd_buf_cfg_prop);
        fld_map_t dma_nu_stage_buf_alloc {
            CREATE_ENTRY("cmp_buf_size", 0, 10),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto dma_nu_stage_buf_alloc_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_stage_buf_alloc),
                                               0x198,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_stage_buf_alloc", dma_nu_stage_buf_alloc_prop);
        fld_map_t dma_nu_dph_csr_wu_header {
            CREATE_ENTRY("header", 0, 64)
        };
        auto dma_nu_dph_csr_wu_header_prop = csr_prop_t(
                std::make_shared<csr_s>(dma_nu_dph_csr_wu_header),
                0x1A0,
                CSR_TYPE::REG,
                1);
        add_csr(dma_nu_0, "dma_nu_dph_csr_wu_header", dma_nu_dph_csr_wu_header_prop);
        fld_map_t dma_nu_dph_enq_wu_cnt {
            CREATE_ENTRY("cnt", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_dph_enq_wu_cnt_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dma_nu_dph_enq_wu_cnt),
                                              0x1D0,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(dma_nu_0, "dma_nu_dph_enq_wu_cnt", dma_nu_dph_enq_wu_cnt_prop);
        fld_map_t dma_nu_dph_per_thd_wu_cnt {
            CREATE_ENTRY("wu_cnt", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_dph_per_thd_wu_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(dma_nu_dph_per_thd_wu_cnt),
                0x218,
                CSR_TYPE::REG,
                1);
        add_csr(dma_nu_0, "dma_nu_dph_per_thd_wu_cnt", dma_nu_dph_per_thd_wu_cnt_prop);
        fld_map_t dma_nu_gtr_thd_cfg_tab {
            CREATE_ENTRY("tag_prof", 0, 3),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto dma_nu_gtr_thd_cfg_tab_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_gtr_thd_cfg_tab),
                                               0x220,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_gtr_thd_cfg_tab", dma_nu_gtr_thd_cfg_tab_prop);
        fld_map_t dma_nu_gtr_f1_tag_alloc {
            CREATE_ENTRY("min_num", 0, 9),
            CREATE_ENTRY("max_num", 9, 9),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto dma_nu_gtr_f1_tag_alloc_prop = csr_prop_t(
                                                std::make_shared<csr_s>(dma_nu_gtr_f1_tag_alloc),
                                                0x228,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(dma_nu_0, "dma_nu_gtr_f1_tag_alloc", dma_nu_gtr_f1_tag_alloc_prop);
        fld_map_t dma_nu_gtr_f1_tag_prof_thresh {
            CREATE_ENTRY("yellow_thresh", 0, 9),
            CREATE_ENTRY("red_thresh", 9, 9),
            CREATE_ENTRY("green_mask_cycles", 18, 8),
            CREATE_ENTRY("yellow_mask_cycles", 26, 8),
            CREATE_ENTRY("red_mask_cycles", 34, 8),
            CREATE_ENTRY("__rsvd", 42, 22)
        };
        auto dma_nu_gtr_f1_tag_prof_thresh_prop = csr_prop_t(
                    std::make_shared<csr_s>(dma_nu_gtr_f1_tag_prof_thresh),
                    0x230,
                    CSR_TYPE::REG_LST,
                    2);
        add_csr(dma_nu_0, "dma_nu_gtr_f1_tag_prof_thresh", dma_nu_gtr_f1_tag_prof_thresh_prop);
        fld_map_t dma_nu_gtr_opr_credit {
            CREATE_ENTRY("credit", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto dma_nu_gtr_opr_credit_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dma_nu_gtr_opr_credit),
                                              0x240,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(dma_nu_0, "dma_nu_gtr_opr_credit", dma_nu_gtr_opr_credit_prop);
        fld_map_t dma_nu_gtr_per_thd_byte_cnt {
            CREATE_ENTRY("byte_cnt", 0, 44),
            CREATE_ENTRY("__rsvd", 44, 20)
        };
        auto dma_nu_gtr_per_thd_byte_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(dma_nu_gtr_per_thd_byte_cnt),
                0x258,
                CSR_TYPE::REG,
                1);
        add_csr(dma_nu_0, "dma_nu_gtr_per_thd_byte_cnt", dma_nu_gtr_per_thd_byte_cnt_prop);
        fld_map_t dma_nu_cmp_enq_cmd_lst_cnt {
            CREATE_ENTRY("cnt", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_cmp_enq_cmd_lst_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(dma_nu_cmp_enq_cmd_lst_cnt),
                0x270,
                CSR_TYPE::REG,
                1);
        add_csr(dma_nu_0, "dma_nu_cmp_enq_cmd_lst_cnt", dma_nu_cmp_enq_cmd_lst_cnt_prop);
        fld_map_t dma_nu_cmp_wus_sent_cnt {
            CREATE_ENTRY("cnt", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_cmp_wus_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(dma_nu_cmp_wus_sent_cnt),
                                                0x278,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(dma_nu_0, "dma_nu_cmp_wus_sent_cnt", dma_nu_cmp_wus_sent_cnt_prop);
        fld_map_t dma_nu_cmp_err_wus_sent_cnt {
            CREATE_ENTRY("cnt", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto dma_nu_cmp_err_wus_sent_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(dma_nu_cmp_err_wus_sent_cnt),
                0x280,
                CSR_TYPE::REG,
                1);
        add_csr(dma_nu_0, "dma_nu_cmp_err_wus_sent_cnt", dma_nu_cmp_err_wus_sent_cnt_prop);
        fld_map_t dma_nu_dmi_cfg {
            CREATE_ENTRY("rd_opcode", 0, 5),
            CREATE_ENTRY("axm_cache", 5, 4),
            CREATE_ENTRY("axm_prefetch", 9, 1),
            CREATE_ENTRY("remote_etp_vc0_crd", 10, 9),
            CREATE_ENTRY("remote_etp_vc2_crd", 19, 9),
            CREATE_ENTRY("remote_etp_vc3_crd", 28, 9),
            CREATE_ENTRY("remote_hdma_vc0_crd", 37, 9),
            CREATE_ENTRY("remote_hdma_vc2_crd", 46, 9),
            CREATE_ENTRY("remote_hdma_vc3_crd", 55, 9)
        };
        auto dma_nu_dmi_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dma_nu_dmi_cfg),
                                       0x288,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dma_nu_0, "dma_nu_dmi_cfg", dma_nu_dmi_cfg_prop);
        fld_map_t dma_nu_dmi_lsn_sent_cnt {
            CREATE_ENTRY("cnt", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_dmi_lsn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(dma_nu_dmi_lsn_sent_cnt),
                                                0x290,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(dma_nu_0, "dma_nu_dmi_lsn_sent_cnt", dma_nu_dmi_lsn_sent_cnt_prop);
        fld_map_t dma_nu_dmi_ldn_rcvd_cnt {
            CREATE_ENTRY("cnt", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto dma_nu_dmi_ldn_rcvd_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(dma_nu_dmi_ldn_rcvd_cnt),
                                                0x298,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(dma_nu_0, "dma_nu_dmi_ldn_rcvd_cnt", dma_nu_dmi_ldn_rcvd_cnt_prop);
        fld_map_t dma_nu_mem_err_inj_cfg {
            CREATE_ENTRY("dph_wuq_mem", 0, 1),
            CREATE_ENTRY("dph_thd_fifo_mem", 1, 1),
            CREATE_ENTRY("dph_rord_buf0_mem", 2, 1),
            CREATE_ENTRY("dph_rord_buf1_mem", 3, 1),
            CREATE_ENTRY("gtr_cmd_fifo_mem", 4, 1),
            CREATE_ENTRY("gtr_rord_buf0_mem", 5, 1),
            CREATE_ENTRY("gtr_rord_buf1_mem", 6, 1),
            CREATE_ENTRY("gtr_hsu_f1_rord_buf_mem", 7, 1),
            CREATE_ENTRY("gtr_hsu_pcie_rord_buf_mem", 8, 1),
            CREATE_ENTRY("gtr_hsu_pcie_rord_buf_nxtptr_mem", 9, 1),
            CREATE_ENTRY("gtr_hsu_tag_queue_buf_mem", 10, 1),
            CREATE_ENTRY("gtr_hsu_tag_queue_next_ptr0_mem", 11, 1),
            CREATE_ENTRY("gtr_hsu_tag_queue_next_ptr1_mem", 12, 1),
            CREATE_ENTRY("gtr_hsu_tag_queue_next_ptr2_mem", 13, 1),
            CREATE_ENTRY("gtr_hsu_tag_queue_next_ptr3_mem", 14, 1),
            CREATE_ENTRY("str_cmd_mem", 15, 1),
            CREATE_ENTRY("str_next_ptr0_mem", 16, 1),
            CREATE_ENTRY("str_next_ptr1_mem", 17, 1),
            CREATE_ENTRY("str_next_ptr2_mem", 18, 1),
            CREATE_ENTRY("str_next_ptr3_mem", 19, 1),
            CREATE_ENTRY("str_aes_data_fifo_mem", 20, 1),
            CREATE_ENTRY("str_sha_data_fifo_mem", 21, 1),
            CREATE_ENTRY("str_snf_buf_mem", 22, 1),
            CREATE_ENTRY("cmp_cmd_mem", 23, 1),
            CREATE_ENTRY("cmp_next_ptr0_mem", 24, 1),
            CREATE_ENTRY("cmp_next_ptr1_mem", 25, 1),
            CREATE_ENTRY("cmp_next_ptr2_mem", 26, 1),
            CREATE_ENTRY("cmp_next_ptr3_mem", 27, 1),
            CREATE_ENTRY("iop_cmd_mem", 28, 1),
            CREATE_ENTRY("iop_rord_bank0_mem", 29, 1),
            CREATE_ENTRY("iop_rord_bank1_mem", 30, 1),
            CREATE_ENTRY("iop_rord_bank2_mem", 31, 1),
            CREATE_ENTRY("iop_req_bank0_mem", 32, 1),
            CREATE_ENTRY("iop_req_bank1_mem", 33, 1),
            CREATE_ENTRY("err_type", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto dma_nu_mem_err_inj_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_mem_err_inj_cfg),
                                               0x2E0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_mem_err_inj_cfg", dma_nu_mem_err_inj_cfg_prop);
        fld_map_t dma_nu_dph_fla_mux_sel {
            CREATE_ENTRY("sel3", 0, 6),
            CREATE_ENTRY("sel2", 6, 6),
            CREATE_ENTRY("sel1", 12, 6),
            CREATE_ENTRY("sel0", 18, 6),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto dma_nu_dph_fla_mux_sel_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_dph_fla_mux_sel),
                                               0x2E8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_dph_fla_mux_sel", dma_nu_dph_fla_mux_sel_prop);
        fld_map_t dma_nu_gtr_fla_mux_sel {
            CREATE_ENTRY("sel3", 0, 5),
            CREATE_ENTRY("sel2", 5, 5),
            CREATE_ENTRY("sel1", 10, 5),
            CREATE_ENTRY("sel0", 15, 5),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto dma_nu_gtr_fla_mux_sel_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_gtr_fla_mux_sel),
                                               0x2F0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_gtr_fla_mux_sel", dma_nu_gtr_fla_mux_sel_prop);
        fld_map_t dma_nu_cmp_fla_mux_sel {
            CREATE_ENTRY("sel3", 0, 5),
            CREATE_ENTRY("sel2", 5, 5),
            CREATE_ENTRY("sel1", 10, 5),
            CREATE_ENTRY("sel0", 15, 5),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto dma_nu_cmp_fla_mux_sel_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_cmp_fla_mux_sel),
                                               0x2F8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_cmp_fla_mux_sel", dma_nu_cmp_fla_mux_sel_prop);
        fld_map_t dma_nu_dmi_fla_mux_sel {
            CREATE_ENTRY("sel3", 0, 5),
            CREATE_ENTRY("sel2", 5, 5),
            CREATE_ENTRY("sel1", 10, 5),
            CREATE_ENTRY("sel0", 15, 5),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto dma_nu_dmi_fla_mux_sel_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_dmi_fla_mux_sel),
                                               0x300,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_dmi_fla_mux_sel", dma_nu_dmi_fla_mux_sel_prop);
        fld_map_t dma_nu_iop_fla_mux_sel {
            CREATE_ENTRY("sel3", 0, 4),
            CREATE_ENTRY("sel2", 4, 4),
            CREATE_ENTRY("sel1", 8, 4),
            CREATE_ENTRY("sel0", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto dma_nu_iop_fla_mux_sel_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_iop_fla_mux_sel),
                                               0x308,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_iop_fla_mux_sel", dma_nu_iop_fla_mux_sel_prop);
        fld_map_t dma_nu_opr_fla_mux_sel {
            CREATE_ENTRY("sel3", 0, 4),
            CREATE_ENTRY("sel2", 4, 4),
            CREATE_ENTRY("sel1", 8, 4),
            CREATE_ENTRY("sel0", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto dma_nu_opr_fla_mux_sel_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dma_nu_opr_fla_mux_sel),
                                               0x310,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dma_nu_0, "dma_nu_opr_fla_mux_sel", dma_nu_opr_fla_mux_sel_prop);
// END dma_nu
    }
    {
// BEGIN etfp
        auto etfp_0 = nu_rng[0].add_an({"etfp"}, 0xA800000, 1, 0x0);
        fld_map_t etfp_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto etfp_timeout_thresh_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(etfp_timeout_thresh_cfg),
                                                0x0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(etfp_0, "etfp_timeout_thresh_cfg", etfp_timeout_thresh_cfg_prop);
        fld_map_t etfp_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto etfp_timeout_clr_prop = csr_prop_t(
                                         std::make_shared<csr_s>(etfp_timeout_clr),
                                         0x10,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etfp_0, "etfp_timeout_clr", etfp_timeout_clr_prop);
        fld_map_t etfp_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto etfp_spare_pio_prop = csr_prop_t(
                                       std::make_shared<csr_s>(etfp_spare_pio),
                                       0x70,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(etfp_0, "etfp_spare_pio", etfp_spare_pio_prop);
        fld_map_t etfp_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto etfp_scratchpad_prop = csr_prop_t(
                                        std::make_shared<csr_s>(etfp_scratchpad),
                                        0x78,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(etfp_0, "etfp_scratchpad", etfp_scratchpad_prop);
        fld_map_t etfp_cfg {
            CREATE_ENTRY("fcp_sec_seq_num_ctrl", 0, 1),
            CREATE_ENTRY("dis_gseq_num_check", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto etfp_cfg_prop = csr_prop_t(
                                 std::make_shared<csr_s>(etfp_cfg),
                                 0x80,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(etfp_0, "etfp_cfg", etfp_cfg_prop);
        fld_map_t etfp_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto etfp_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(etfp_fla_ring_module_id_cfg),
                0x88,
                CSR_TYPE::REG,
                1);
        add_csr(etfp_0, "etfp_fla_ring_module_id_cfg", etfp_fla_ring_module_id_cfg_prop);
        fld_map_t etfp_wct_macro_cfg {
            CREATE_ENTRY("decimal_rollover_en", 0, 1),
            CREATE_ENTRY("base_incr", 1, 26),
            CREATE_ENTRY("base_corr_incr", 27, 26),
            CREATE_ENTRY("override_incr", 53, 26),
            CREATE_ENTRY("base_period", 79, 16),
            CREATE_ENTRY("override_cnt", 95, 16),
            CREATE_ENTRY("override_mode", 111, 1),
            CREATE_ENTRY("sync_pulse_dly_sel", 112, 4),
            CREATE_ENTRY("__rsvd", 116, 12)
        };
        auto etfp_wct_macro_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(etfp_wct_macro_cfg),
                                           0x90,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(etfp_0, "etfp_wct_macro_cfg", etfp_wct_macro_cfg_prop);
        fld_map_t etfp_sec_seq_num {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto etfp_sec_seq_num_prop = csr_prop_t(
                                         std::make_shared<csr_s>(etfp_sec_seq_num),
                                         0xA0,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(etfp_0, "etfp_sec_seq_num", etfp_sec_seq_num_prop);
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
        };
        auto etfp_sram_err_inj_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(etfp_sram_err_inj_cfg),
                                              0xA8,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(etfp_0, "etfp_sram_err_inj_cfg", etfp_sram_err_inj_cfg_prop);
        fld_map_t fcp_psn_mem {
            CREATE_ENTRY("val", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto fcp_psn_mem_prop = csr_prop_t(
                                    std::make_shared<csr_s>(fcp_psn_mem),
                                    0x20000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(etfp_0, "fcp_psn_mem", fcp_psn_mem_prop);
        fld_map_t fcp_dtunnel_mem {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fcp_dtunnel_mem_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fcp_dtunnel_mem),
                                        0x120000,
                                        CSR_TYPE::TBL,
                                        1);
        add_csr(etfp_0, "fcp_dtunnel_mem", fcp_dtunnel_mem_prop);
        fld_map_t fcp_dip_mem {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fcp_dip_mem_prop = csr_prop_t(
                                    std::make_shared<csr_s>(fcp_dip_mem),
                                    0x220000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(etfp_0, "fcp_dip_mem", fcp_dip_mem_prop);
        fld_map_t fcp_eainfo_mem {
            CREATE_ENTRY("val", 0, 23),
            CREATE_ENTRY("__rsvd", 23, 41)
        };
        auto fcp_eainfo_mem_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fcp_eainfo_mem),
                                       0x320000,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(etfp_0, "fcp_eainfo_mem", fcp_eainfo_mem_prop);
// END etfp
    }
    {
// BEGIN fae_prs
        auto fae_prs_0 = nu_rng[0].add_an({"fae_prs"}, 0xB000000, 1, 0x0);
        fld_map_t fae_prs_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fae_prs_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fae_prs_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fae_prs_0, "fae_prs_timeout_thresh_cfg", fae_prs_timeout_thresh_cfg_prop);
        fld_map_t fae_prs_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fae_prs_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fae_prs_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fae_prs_0, "fae_prs_timeout_clr", fae_prs_timeout_clr_prop);
        fld_map_t fae_prs_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fae_prs_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_prs_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fae_prs_0, "fae_prs_spare_pio", fae_prs_spare_pio_prop);
        fld_map_t fae_prs_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fae_prs_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fae_prs_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fae_prs_0, "fae_prs_scratchpad", fae_prs_scratchpad_prop);
        fld_map_t prs_mem_err_inj_cfg {
            CREATE_ENTRY("prs_rob_prv_mem", 0, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem0", 1, 1),
            CREATE_ENTRY("err_type", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto prs_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_mem_err_inj_cfg),
                                            0x98,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fae_prs_0, "prs_mem_err_inj_cfg", prs_mem_err_inj_cfg_prop);
        fld_map_t prs_dsp_dfifo_mem_af_thold {
            CREATE_ENTRY("data", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
                std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
                0xA0,
                CSR_TYPE::REG,
                1);
        add_csr(fae_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
        fld_map_t prs_intf_cfg {
            CREATE_ENTRY("intf0mode", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto prs_intf_cfg_prop = csr_prop_t(
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
        };
        auto prs_err_chk_en_prop = csr_prop_t(
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
        };
        auto prs_err_tcode0_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode0),
                                       0xB8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fae_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
        fld_map_t prs_err_tcode1 {
            CREATE_ENTRY("gp_byte_oor", 0, 7),
            CREATE_ENTRY("action_mem_perr", 7, 7),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto prs_err_tcode1_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode1),
                                       0xC0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fae_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
        fld_map_t prs_max_lu_cycle_cfg {
            CREATE_ENTRY("use_fixed", 0, 1),
            CREATE_ENTRY("fixed_cnt", 1, 8),
            CREATE_ENTRY("init_cycle_cnt", 9, 6),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
                                             0xC8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fae_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
        fld_map_t prs_stream_cfg {
            CREATE_ENTRY("fixed_stream_en", 0, 1),
            CREATE_ENTRY("intf0_stream", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto prs_stream_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_stream_cfg),
                                       0xD0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fae_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
        fld_map_t prs_static_ctx_sel {
            CREATE_ENTRY("use_one_ctx", 0, 1),
            CREATE_ENTRY("ctx_num", 1, 2),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto prs_static_ctx_sel_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_static_ctx_sel),
                                           0xD8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fae_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
        fld_map_t prs_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
                0xE0,
                CSR_TYPE::REG,
                1);
        add_csr(fae_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
        fld_map_t prs_tcam {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("parser_state", 1, 8),
            CREATE_ENTRY("pattern", 9, 32),
            CREATE_ENTRY("mask", 41, 32),
            CREATE_ENTRY("__rsvd", 73, 55)
        };
        auto prs_tcam_prop = csr_prop_t(
                                 std::make_shared<csr_s>(prs_tcam),
                                 0x1000,
                                 CSR_TYPE::TBL,
                                 1);
        add_csr(fae_prs_0, "prs_tcam", prs_tcam_prop);
        fld_map_t prs_seq_mem {
            CREATE_ENTRY("new_parser_state", 0, 8),
            CREATE_ENTRY("key_src", 8, 2),
            CREATE_ENTRY("pkt_ptr_incr", 10, 4),
            CREATE_ENTRY("set_act_context", 14, 1),
            CREATE_ENTRY("gpr_instr_opcode", 15, 2),
            CREATE_ENTRY("gpr_instr_operand", 17, 12),
            CREATE_ENTRY("__rsvd", 29, 35)
        };
        auto prs_seq_mem_prop = csr_prop_t(
                                    std::make_shared<csr_s>(prs_seq_mem),
                                    0x11000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(fae_prs_0, "prs_seq_mem", prs_seq_mem_prop);
        fld_map_t prs_rob_prv_mem_dhs {
            CREATE_ENTRY("data", 0, 288),
            CREATE_ENTRY("__rsvd", 288, 32)
        };
        auto prs_rob_prv_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_rob_prv_mem_dhs),
                                            0x15000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(fae_prs_0, "prs_rob_prv_mem_dhs", prs_rob_prv_mem_dhs_prop);
        fld_map_t prs_action_mem_dhs {
            CREATE_ENTRY("data", 0, 112),
            CREATE_ENTRY("__rsvd", 112, 16)
        };
        auto prs_action_mem_dhs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_action_mem_dhs),
                                           0x40000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(fae_prs_0, "prs_action_mem_dhs", prs_action_mem_dhs_prop);
        fld_map_t prs_dsp_dfifo_mem_dhs {
            CREATE_ENTRY("data", 0, 263),
            CREATE_ENTRY("__rsvd", 263, 57)
        };
        auto prs_dsp_dfifo_mem_dhs_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_dsp_dfifo_mem_dhs),
                                              0x140000,
                                              CSR_TYPE::TBL,
                                              2);
        add_csr(fae_prs_0, "prs_dsp_dfifo_mem_dhs", prs_dsp_dfifo_mem_dhs_prop);
        fld_map_t prs_initial_state {
            CREATE_ENTRY("parser_state", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_initial_state_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_initial_state),
                                          0x540000,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fae_prs_0, "prs_initial_state", prs_initial_state_prop);
        fld_map_t prs_dsp_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_dsp_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_dsp_dbg_probe),
                                          0x541000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fae_prs_0, "prs_dsp_dbg_probe", prs_dsp_dbg_probe_prop);
        fld_map_t prs_ctx_rob_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_ctx_rob_dbg_probe_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_ctx_rob_dbg_probe),
                                              0x541200,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(fae_prs_0, "prs_ctx_rob_dbg_probe", prs_ctx_rob_dbg_probe_prop);
        fld_map_t prs_prv_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_prv_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_prv_dbg_probe),
                                          0x541400,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(fae_prs_0, "prs_prv_dbg_probe", prs_prv_dbg_probe_prop);
// END fae_prs
    }
    {
// BEGIN etp_prs
        auto etp_prs_0 = nu_rng[0].add_an({"etp_prs"}, 0xB800000, 1, 0x0);
        fld_map_t etp_prs_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto etp_prs_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(etp_prs_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(etp_prs_0, "etp_prs_timeout_thresh_cfg", etp_prs_timeout_thresh_cfg_prop);
        fld_map_t etp_prs_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto etp_prs_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(etp_prs_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etp_prs_0, "etp_prs_timeout_clr", etp_prs_timeout_clr_prop);
        fld_map_t etp_prs_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto etp_prs_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(etp_prs_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(etp_prs_0, "etp_prs_spare_pio", etp_prs_spare_pio_prop);
        fld_map_t etp_prs_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto etp_prs_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(etp_prs_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(etp_prs_0, "etp_prs_scratchpad", etp_prs_scratchpad_prop);
        fld_map_t prs_mem_err_inj_cfg {
            CREATE_ENTRY("prs_rob_prv_mem", 0, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem0", 1, 1),
            CREATE_ENTRY("err_type", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto prs_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_mem_err_inj_cfg),
                                            0x98,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(etp_prs_0, "prs_mem_err_inj_cfg", prs_mem_err_inj_cfg_prop);
        fld_map_t prs_dsp_dfifo_mem_af_thold {
            CREATE_ENTRY("data", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
                std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
                0xA0,
                CSR_TYPE::REG,
                1);
        add_csr(etp_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
        fld_map_t prs_intf_cfg {
            CREATE_ENTRY("intf0mode", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto prs_intf_cfg_prop = csr_prop_t(
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
        };
        auto prs_err_chk_en_prop = csr_prop_t(
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
        };
        auto prs_err_tcode0_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode0),
                                       0xB8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(etp_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
        fld_map_t prs_err_tcode1 {
            CREATE_ENTRY("gp_byte_oor", 0, 7),
            CREATE_ENTRY("action_mem_perr", 7, 7),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto prs_err_tcode1_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode1),
                                       0xC0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(etp_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
        fld_map_t prs_max_lu_cycle_cfg {
            CREATE_ENTRY("use_fixed", 0, 1),
            CREATE_ENTRY("fixed_cnt", 1, 8),
            CREATE_ENTRY("init_cycle_cnt", 9, 6),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
                                             0xC8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(etp_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
        fld_map_t prs_stream_cfg {
            CREATE_ENTRY("fixed_stream_en", 0, 1),
            CREATE_ENTRY("intf0_stream", 1, 5),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto prs_stream_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_stream_cfg),
                                       0xD0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(etp_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
        fld_map_t prs_static_ctx_sel {
            CREATE_ENTRY("use_one_ctx", 0, 1),
            CREATE_ENTRY("ctx_num", 1, 2),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto prs_static_ctx_sel_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_static_ctx_sel),
                                           0xD8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(etp_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
        fld_map_t prs_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
                0xE0,
                CSR_TYPE::REG,
                1);
        add_csr(etp_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
        fld_map_t prs_tcam {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("parser_state", 1, 8),
            CREATE_ENTRY("pattern", 9, 32),
            CREATE_ENTRY("mask", 41, 32),
            CREATE_ENTRY("__rsvd", 73, 55)
        };
        auto prs_tcam_prop = csr_prop_t(
                                 std::make_shared<csr_s>(prs_tcam),
                                 0x1000,
                                 CSR_TYPE::TBL,
                                 1);
        add_csr(etp_prs_0, "prs_tcam", prs_tcam_prop);
        fld_map_t prs_seq_mem {
            CREATE_ENTRY("new_parser_state", 0, 8),
            CREATE_ENTRY("key_src", 8, 2),
            CREATE_ENTRY("pkt_ptr_incr", 10, 4),
            CREATE_ENTRY("set_act_context", 14, 1),
            CREATE_ENTRY("gpr_instr_opcode", 15, 2),
            CREATE_ENTRY("gpr_instr_operand", 17, 12),
            CREATE_ENTRY("__rsvd", 29, 35)
        };
        auto prs_seq_mem_prop = csr_prop_t(
                                    std::make_shared<csr_s>(prs_seq_mem),
                                    0x11000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(etp_prs_0, "prs_seq_mem", prs_seq_mem_prop);
        fld_map_t prs_rob_prv_mem_dhs {
            CREATE_ENTRY("data", 0, 288),
            CREATE_ENTRY("__rsvd", 288, 32)
        };
        auto prs_rob_prv_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_rob_prv_mem_dhs),
                                            0x15000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(etp_prs_0, "prs_rob_prv_mem_dhs", prs_rob_prv_mem_dhs_prop);
        fld_map_t prs_action_mem_dhs {
            CREATE_ENTRY("data", 0, 112),
            CREATE_ENTRY("__rsvd", 112, 16)
        };
        auto prs_action_mem_dhs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_action_mem_dhs),
                                           0x40000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(etp_prs_0, "prs_action_mem_dhs", prs_action_mem_dhs_prop);
        fld_map_t prs_dsp_dfifo_mem_dhs {
            CREATE_ENTRY("data", 0, 263),
            CREATE_ENTRY("__rsvd", 263, 57)
        };
        auto prs_dsp_dfifo_mem_dhs_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_dsp_dfifo_mem_dhs),
                                              0x140000,
                                              CSR_TYPE::TBL,
                                              2);
        add_csr(etp_prs_0, "prs_dsp_dfifo_mem_dhs", prs_dsp_dfifo_mem_dhs_prop);
        fld_map_t prs_initial_state {
            CREATE_ENTRY("parser_state", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_initial_state_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_initial_state),
                                          0x540000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(etp_prs_0, "prs_initial_state", prs_initial_state_prop);
        fld_map_t prs_dsp_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_dsp_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_dsp_dbg_probe),
                                          0x541000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(etp_prs_0, "prs_dsp_dbg_probe", prs_dsp_dbg_probe_prop);
        fld_map_t prs_ctx_rob_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_ctx_rob_dbg_probe_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_ctx_rob_dbg_probe),
                                              0x541200,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(etp_prs_0, "prs_ctx_rob_dbg_probe", prs_ctx_rob_dbg_probe_prop);
        fld_map_t prs_prv_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_prv_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_prv_dbg_probe),
                                          0x541400,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(etp_prs_0, "prs_prv_dbg_probe", prs_prv_dbg_probe_prop);
// END etp_prs
    }
    {
// BEGIN erp_prs
        auto erp_prs_0 = nu_rng[0].add_an({"efp_rfp","erp_prs"}, 0xC000000, 1, 0x0);
        fld_map_t erp_prs_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto erp_prs_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(erp_prs_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(erp_prs_0, "erp_prs_timeout_thresh_cfg", erp_prs_timeout_thresh_cfg_prop);
        fld_map_t erp_prs_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto erp_prs_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(erp_prs_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(erp_prs_0, "erp_prs_timeout_clr", erp_prs_timeout_clr_prop);
        fld_map_t erp_prs_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto erp_prs_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(erp_prs_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(erp_prs_0, "erp_prs_spare_pio", erp_prs_spare_pio_prop);
        fld_map_t erp_prs_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto erp_prs_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(erp_prs_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(erp_prs_0, "erp_prs_scratchpad", erp_prs_scratchpad_prop);
        fld_map_t prs_mem_err_inj_cfg {
            CREATE_ENTRY("prs_rob_prv_mem", 0, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem0", 1, 1),
            CREATE_ENTRY("prs_dsp_fifo_mem1", 2, 1),
            CREATE_ENTRY("err_type", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto prs_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_mem_err_inj_cfg),
                                            0x98,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(erp_prs_0, "prs_mem_err_inj_cfg", prs_mem_err_inj_cfg_prop);
        fld_map_t prs_dsp_dfifo_mem_af_thold {
            CREATE_ENTRY("data", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto prs_dsp_dfifo_mem_af_thold_prop = csr_prop_t(
                std::make_shared<csr_s>(prs_dsp_dfifo_mem_af_thold),
                0xA0,
                CSR_TYPE::REG,
                1);
        add_csr(erp_prs_0, "prs_dsp_dfifo_mem_af_thold", prs_dsp_dfifo_mem_af_thold_prop);
        fld_map_t prs_intf_cfg {
            CREATE_ENTRY("intf0mode", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto prs_intf_cfg_prop = csr_prop_t(
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
        };
        auto prs_err_chk_en_prop = csr_prop_t(
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
        };
        auto prs_err_tcode0_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode0),
                                       0xB8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(erp_prs_0, "prs_err_tcode0", prs_err_tcode0_prop);
        fld_map_t prs_err_tcode1 {
            CREATE_ENTRY("gp_byte_oor", 0, 7),
            CREATE_ENTRY("action_mem_perr", 7, 7),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto prs_err_tcode1_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_err_tcode1),
                                       0xC0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(erp_prs_0, "prs_err_tcode1", prs_err_tcode1_prop);
        fld_map_t prs_max_lu_cycle_cfg {
            CREATE_ENTRY("use_fixed", 0, 1),
            CREATE_ENTRY("fixed_cnt", 1, 8),
            CREATE_ENTRY("init_cycle_cnt", 9, 6),
            CREATE_ENTRY("__rsvd", 15, 49)
        };
        auto prs_max_lu_cycle_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(prs_max_lu_cycle_cfg),
                                             0xC8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(erp_prs_0, "prs_max_lu_cycle_cfg", prs_max_lu_cycle_cfg_prop);
        fld_map_t prs_stream_cfg {
            CREATE_ENTRY("fixed_stream_en", 0, 1),
            CREATE_ENTRY("intf0_stream", 1, 5),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto prs_stream_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(prs_stream_cfg),
                                       0xD0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(erp_prs_0, "prs_stream_cfg", prs_stream_cfg_prop);
        fld_map_t prs_static_ctx_sel {
            CREATE_ENTRY("use_one_ctx", 0, 1),
            CREATE_ENTRY("ctx_num", 1, 3),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto prs_static_ctx_sel_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_static_ctx_sel),
                                           0xD8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(erp_prs_0, "prs_static_ctx_sel", prs_static_ctx_sel_prop);
        fld_map_t prs_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(prs_fla_ring_module_id_cfg),
                0xE0,
                CSR_TYPE::REG,
                1);
        add_csr(erp_prs_0, "prs_fla_ring_module_id_cfg", prs_fla_ring_module_id_cfg_prop);
        fld_map_t prs_tcam {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("parser_state", 1, 8),
            CREATE_ENTRY("pattern", 9, 32),
            CREATE_ENTRY("mask", 41, 32),
            CREATE_ENTRY("__rsvd", 73, 55)
        };
        auto prs_tcam_prop = csr_prop_t(
                                 std::make_shared<csr_s>(prs_tcam),
                                 0x1000,
                                 CSR_TYPE::TBL,
                                 1);
        add_csr(erp_prs_0, "prs_tcam", prs_tcam_prop);
        fld_map_t prs_seq_mem {
            CREATE_ENTRY("new_parser_state", 0, 8),
            CREATE_ENTRY("key_src", 8, 2),
            CREATE_ENTRY("pkt_ptr_incr", 10, 4),
            CREATE_ENTRY("set_act_context", 14, 1),
            CREATE_ENTRY("gpr_instr_opcode", 15, 2),
            CREATE_ENTRY("gpr_instr_operand", 17, 12),
            CREATE_ENTRY("__rsvd", 29, 35)
        };
        auto prs_seq_mem_prop = csr_prop_t(
                                    std::make_shared<csr_s>(prs_seq_mem),
                                    0x11000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(erp_prs_0, "prs_seq_mem", prs_seq_mem_prop);
        fld_map_t prs_rob_prv_mem_dhs {
            CREATE_ENTRY("data", 0, 288),
            CREATE_ENTRY("__rsvd", 288, 32)
        };
        auto prs_rob_prv_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(prs_rob_prv_mem_dhs),
                                            0x15000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(erp_prs_0, "prs_rob_prv_mem_dhs", prs_rob_prv_mem_dhs_prop);
        fld_map_t prs_action_mem_dhs {
            CREATE_ENTRY("data", 0, 112),
            CREATE_ENTRY("__rsvd", 112, 16)
        };
        auto prs_action_mem_dhs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(prs_action_mem_dhs),
                                           0x40000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(erp_prs_0, "prs_action_mem_dhs", prs_action_mem_dhs_prop);
        fld_map_t prs_dsp_dfifo_mem_dhs {
            CREATE_ENTRY("data", 0, 263),
            CREATE_ENTRY("__rsvd", 263, 57)
        };
        auto prs_dsp_dfifo_mem_dhs_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_dsp_dfifo_mem_dhs),
                                              0x140000,
                                              CSR_TYPE::TBL,
                                              2);
        add_csr(erp_prs_0, "prs_dsp_dfifo_mem_dhs", prs_dsp_dfifo_mem_dhs_prop);
        fld_map_t prs_initial_state {
            CREATE_ENTRY("parser_state", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto prs_initial_state_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_initial_state),
                                          0x540000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(erp_prs_0, "prs_initial_state", prs_initial_state_prop);
        fld_map_t prs_dsp_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_dsp_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_dsp_dbg_probe),
                                          0x541000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(erp_prs_0, "prs_dsp_dbg_probe", prs_dsp_dbg_probe_prop);
        fld_map_t prs_ctx_rob_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_ctx_rob_dbg_probe_prop = csr_prop_t(
                                              std::make_shared<csr_s>(prs_ctx_rob_dbg_probe),
                                              0x541200,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(erp_prs_0, "prs_ctx_rob_dbg_probe", prs_ctx_rob_dbg_probe_prop);
        fld_map_t prs_prv_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto prs_prv_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(prs_prv_dbg_probe),
                                          0x541400,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(erp_prs_0, "prs_prv_dbg_probe", prs_prv_dbg_probe_prop);
// END erp_prs
    }
    {
// BEGIN sfg
        auto sfg_0 = nu_rng[0].add_an({"efp_rfp","sfg"}, 0xC800000, 1, 0x0);
        fld_map_t sfg_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto sfg_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(sfg_0, "sfg_timeout_thresh_cfg", sfg_timeout_thresh_cfg_prop);
        fld_map_t sfg_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sfg_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(sfg_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(sfg_0, "sfg_timeout_clr", sfg_timeout_clr_prop);
        fld_map_t sfg_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sfg_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(sfg_spare_pio),
                                      0x98,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(sfg_0, "sfg_spare_pio", sfg_spare_pio_prop);
        fld_map_t sfg_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sfg_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_scratchpad),
                                       0xA0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(sfg_0, "sfg_scratchpad", sfg_scratchpad_prop);
        fld_map_t sfg_mem_init_start_cfg {
            CREATE_ENTRY("fld_rwt_instr_bank0_mem", 0, 1),
            CREATE_ENTRY("fld_rwt_instr_bank1_mem", 1, 1),
            CREATE_ENTRY("fld_eg_qos_tbl_mem", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto sfg_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_mem_init_start_cfg),
                                               0xA8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(sfg_0, "sfg_mem_init_start_cfg", sfg_mem_init_start_cfg_prop);
        fld_map_t sfg_mem_err_inj_cfg {
            CREATE_ENTRY("fld_rwt_instr_bank0_mem", 0, 1),
            CREATE_ENTRY("fld_rwt_instr_bank1_mem", 1, 1),
            CREATE_ENTRY("fld_eg_qos_tbl_mem", 2, 1),
            CREATE_ENTRY("fld_err_type", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto sfg_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(sfg_mem_err_inj_cfg),
                                            0xD0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(sfg_0, "sfg_mem_err_inj_cfg", sfg_mem_err_inj_cfg_prop);
        fld_map_t sfg_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto sfg_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_fla_ring_module_id_cfg),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_fla_ring_module_id_cfg", sfg_fla_ring_module_id_cfg_prop);
        fld_map_t sfg_erp_mode_pol_drop_lkup_cfg {
            CREATE_ENTRY("fld_drop_col_rsvd", 0, 1),
            CREATE_ENTRY("fld_drop_col_red", 1, 1),
            CREATE_ENTRY("fld_drop_col_yellow", 2, 1),
            CREATE_ENTRY("fld_drop_col_green", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto sfg_erp_mode_pol_drop_lkup_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(sfg_erp_mode_pol_drop_lkup_cfg),
                    0xE0,
                    CSR_TYPE::REG,
                    1);
        add_csr(sfg_0, "sfg_erp_mode_pol_drop_lkup_cfg", sfg_erp_mode_pol_drop_lkup_cfg_prop);
        fld_map_t sfg_meter0_color_lkup_cfg {
            CREATE_ENTRY("fld_color", 0, 64)
        };
        auto sfg_meter0_color_lkup_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter0_color_lkup_cfg),
                0xE8,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_meter0_color_lkup_cfg", sfg_meter0_color_lkup_cfg_prop);
        fld_map_t sfg_meter1_color_lkup_cfg {
            CREATE_ENTRY("fld_color", 0, 64)
        };
        auto sfg_meter1_color_lkup_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter1_color_lkup_cfg),
                0xF0,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_meter1_color_lkup_cfg", sfg_meter1_color_lkup_cfg_prop);
        fld_map_t sfg_smpler_pps_timer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_tick_cnt", 1, 20),
            CREATE_ENTRY("__rsvd", 21, 43)
        };
        auto sfg_smpler_pps_timer_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_pps_timer_cfg),
                0xF8,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_smpler_pps_timer_cfg", sfg_smpler_pps_timer_cfg_prop);
        fld_map_t sfg_smpler_lfsr_seed_cfg {
            CREATE_ENTRY("fld_data", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sfg_smpler_lfsr_seed_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_lfsr_seed_cfg),
                0x108,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_smpler_lfsr_seed_cfg", sfg_smpler_lfsr_seed_cfg_prop);
        fld_map_t sfg_frv_flex_byte_sel_cfg {
            CREATE_ENTRY("fld_byte0_type", 0, 1),
            CREATE_ENTRY("fld_byte0_ofs", 1, 7),
            CREATE_ENTRY("fld_byte1_type", 8, 1),
            CREATE_ENTRY("fld_byte1_ofs", 9, 7),
            CREATE_ENTRY("fld_byte2_type", 16, 1),
            CREATE_ENTRY("fld_byte2_ofs", 17, 7),
            CREATE_ENTRY("fld_byte3_type", 24, 1),
            CREATE_ENTRY("fld_byte3_ofs", 25, 7),
            CREATE_ENTRY("fld_byte4_type", 32, 1),
            CREATE_ENTRY("fld_byte4_ofs", 33, 7),
            CREATE_ENTRY("fld_byte5_type", 40, 1),
            CREATE_ENTRY("fld_byte5_ofs", 41, 7),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto sfg_frv_flex_byte_sel_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_frv_flex_byte_sel_cfg),
                0x110,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_frv_flex_byte_sel_cfg", sfg_frv_flex_byte_sel_cfg_prop);
        fld_map_t sfg_meter0_cfg {
            CREATE_ENTRY("data", 0, 64)
        };
        auto sfg_meter0_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_meter0_cfg),
                                       0x120,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(sfg_0, "sfg_meter0_cfg", sfg_meter0_cfg_prop);
        fld_map_t sfg_meter1_cfg {
            CREATE_ENTRY("data", 0, 64)
        };
        auto sfg_meter1_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_meter1_cfg),
                                       0x220,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(sfg_0, "sfg_meter1_cfg", sfg_meter1_cfg_prop);
        fld_map_t sfg_smpler_attr_cfg {
            CREATE_ENTRY("fld_pps_enable", 0, 1),
            CREATE_ENTRY("fld_pps_time_intvl", 1, 20),
            CREATE_ENTRY("fld_pps_crdt_thresh", 21, 7),
            CREATE_ENTRY("fld_smpl_type", 28, 1),
            CREATE_ENTRY("fld_smpl_rate", 29, 10),
            CREATE_ENTRY("fld_smpl_run_size", 39, 4),
            CREATE_ENTRY("__rsvd", 43, 21)
        };
        auto sfg_smpler_attr_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(sfg_smpler_attr_cfg),
                                            0x400,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(sfg_0, "sfg_smpler_attr_cfg", sfg_smpler_attr_cfg_prop);
        fld_map_t sfg_smpler_rwt_instr_cfg {
            CREATE_ENTRY("fld_egr_stream", 0, 6),
            CREATE_ENTRY("fld_egr_que", 6, 4),
            CREATE_ENTRY("fld_first_cell_only", 10, 1),
            CREATE_ENTRY("fld_itype0", 11, 4),
            CREATE_ENTRY("fld_instr0", 15, 20),
            CREATE_ENTRY("fld_itype1", 35, 4),
            CREATE_ENTRY("fld_instr1", 39, 20),
            CREATE_ENTRY("fld_itype2", 59, 4),
            CREATE_ENTRY("fld_instr2", 63, 20),
            CREATE_ENTRY("fld_itype3", 83, 4),
            CREATE_ENTRY("fld_instr3", 87, 20),
            CREATE_ENTRY("__rsvd", 107, 21)
        };
        auto sfg_smpler_rwt_instr_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_rwt_instr_cfg),
                0x1400,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_smpler_rwt_instr_cfg", sfg_smpler_rwt_instr_cfg_prop);
        fld_map_t sfg_smpler_flag_mask_cfg {
            CREATE_ENTRY("fld_mask", 0, 64)
        };
        auto sfg_smpler_flag_mask_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_flag_mask_cfg),
                0x3400,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_smpler_flag_mask_cfg", sfg_smpler_flag_mask_cfg_prop);
        fld_map_t sfg_l2_len_chk_cam_dhs {
            CREATE_ENTRY("fld_vld", 0, 1),
            CREATE_ENTRY("fld_key_flags", 1, 4),
            CREATE_ENTRY("fld_key_template", 5, 16),
            CREATE_ENTRY("fld_msk_flags", 21, 4),
            CREATE_ENTRY("fld_msk_template", 25, 16),
            CREATE_ENTRY("fld_l2_shn", 41, 3),
            CREATE_ENTRY("fld_l3_shn", 44, 3),
            CREATE_ENTRY("__rsvd", 47, 17)
        };
        auto sfg_l2_len_chk_cam_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_l2_len_chk_cam_dhs),
                                               0x3600,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(sfg_0, "sfg_l2_len_chk_cam_dhs", sfg_l2_len_chk_cam_dhs_prop);
        fld_map_t sfg_eg_str_mtu_cfg_tbl {
            CREATE_ENTRY("fld_val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto sfg_eg_str_mtu_cfg_tbl_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_eg_str_mtu_cfg_tbl),
                                               0x3700,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(sfg_0, "sfg_eg_str_mtu_cfg_tbl", sfg_eg_str_mtu_cfg_tbl_prop);
        fld_map_t sfg_stats_cntr {
            CREATE_ENTRY("fld_val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto sfg_stats_cntr_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_stats_cntr),
                                       0x3F00,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(sfg_0, "sfg_stats_cntr", sfg_stats_cntr_prop);
        fld_map_t sfg_smpler_stats_cntrs_dhs {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto sfg_smpler_stats_cntrs_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_stats_cntrs_dhs),
                0x4200,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_smpler_stats_cntrs_dhs", sfg_smpler_stats_cntrs_dhs_prop);
        fld_map_t sfg_snapshot_sym {
            CREATE_ENTRY("fld_val", 0, 64)
        };
        auto sfg_snapshot_sym_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sfg_snapshot_sym),
                                         0x5200,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(sfg_0, "sfg_snapshot_sym", sfg_snapshot_sym_prop);
        fld_map_t sfg_eg_qos_tbl_mem_dhs {
            CREATE_ENTRY("fld_pol_drop", 0, 1),
            CREATE_ENTRY("fld_vlan_qos_ovrt", 1, 1),
            CREATE_ENTRY("fld_vlan_qos", 2, 4),
            CREATE_ENTRY("fld_ip_dscp_ovrt", 6, 1),
            CREATE_ENTRY("fld_ip_dscp", 7, 6),
            CREATE_ENTRY("fld_egr_queue", 13, 4),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto sfg_eg_qos_tbl_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_eg_qos_tbl_mem_dhs),
                                               0x8000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(sfg_0, "sfg_eg_qos_tbl_mem_dhs", sfg_eg_qos_tbl_mem_dhs_prop);
        fld_map_t sfg_rwt_instr_bank0_mem_dhs {
            CREATE_ENTRY("fld_dbl_inst", 0, 1),
            CREATE_ENTRY("fld_itype0", 1, 4),
            CREATE_ENTRY("fld_instr0", 5, 20),
            CREATE_ENTRY("fld_itype1", 25, 4),
            CREATE_ENTRY("fld_instr1", 29, 20),
            CREATE_ENTRY("fld_itype2", 49, 4),
            CREATE_ENTRY("fld_instr2", 53, 20),
            CREATE_ENTRY("fld_itype3", 73, 4),
            CREATE_ENTRY("fld_instr3", 77, 20),
            CREATE_ENTRY("fld_itype4", 97, 4),
            CREATE_ENTRY("fld_instr4", 101, 20),
            CREATE_ENTRY("fld_itype5", 121, 4),
            CREATE_ENTRY("fld_instr5", 125, 20),
            CREATE_ENTRY("__rsvd", 145, 47)
        };
        auto sfg_rwt_instr_bank0_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_rwt_instr_bank0_mem_dhs),
                0x50000,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_rwt_instr_bank0_mem_dhs", sfg_rwt_instr_bank0_mem_dhs_prop);
        fld_map_t sfg_rwt_instr_bank1_mem_dhs {
            CREATE_ENTRY("fld_dbl_inst", 0, 1),
            CREATE_ENTRY("fld_itype0", 1, 4),
            CREATE_ENTRY("fld_instr0", 5, 20),
            CREATE_ENTRY("fld_itype1", 25, 4),
            CREATE_ENTRY("fld_instr1", 29, 20),
            CREATE_ENTRY("fld_itype2", 49, 4),
            CREATE_ENTRY("fld_instr2", 53, 20),
            CREATE_ENTRY("fld_itype3", 73, 4),
            CREATE_ENTRY("fld_instr3", 77, 20),
            CREATE_ENTRY("fld_itype4", 97, 4),
            CREATE_ENTRY("fld_instr4", 101, 20),
            CREATE_ENTRY("fld_itype5", 121, 4),
            CREATE_ENTRY("fld_instr5", 125, 20),
            CREATE_ENTRY("__rsvd", 145, 47)
        };
        auto sfg_rwt_instr_bank1_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_rwt_instr_bank1_mem_dhs),
                0x1D0000,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_rwt_instr_bank1_mem_dhs", sfg_rwt_instr_bank1_mem_dhs_prop);
        fld_map_t sfg_meter0_state_mem_cfg {
            CREATE_ENTRY("fld_0", 0, 2),
            CREATE_ENTRY("fld_1", 2, 2),
            CREATE_ENTRY("fld_2", 4, 2),
            CREATE_ENTRY("fld_3", 6, 2),
            CREATE_ENTRY("fld_4", 8, 2),
            CREATE_ENTRY("fld_5", 10, 2),
            CREATE_ENTRY("fld_6", 12, 2),
            CREATE_ENTRY("fld_7", 14, 2),
            CREATE_ENTRY("fld_8", 16, 2),
            CREATE_ENTRY("fld_9", 18, 2),
            CREATE_ENTRY("fld_10", 20, 2),
            CREATE_ENTRY("fld_11", 22, 2),
            CREATE_ENTRY("fld_12", 24, 2),
            CREATE_ENTRY("fld_13", 26, 2),
            CREATE_ENTRY("fld_14", 28, 2),
            CREATE_ENTRY("fld_15", 30, 2),
            CREATE_ENTRY("fld_16", 32, 2),
            CREATE_ENTRY("fld_17", 34, 2),
            CREATE_ENTRY("fld_18", 36, 2),
            CREATE_ENTRY("fld_19", 38, 2),
            CREATE_ENTRY("fld_20", 40, 2),
            CREATE_ENTRY("fld_21", 42, 2),
            CREATE_ENTRY("fld_22", 44, 2),
            CREATE_ENTRY("fld_23", 46, 2),
            CREATE_ENTRY("fld_24", 48, 2),
            CREATE_ENTRY("fld_25", 50, 2),
            CREATE_ENTRY("fld_26", 52, 2),
            CREATE_ENTRY("fld_27", 54, 2),
            CREATE_ENTRY("fld_28", 56, 2),
            CREATE_ENTRY("fld_29", 58, 2),
            CREATE_ENTRY("fld_30", 60, 2),
            CREATE_ENTRY("fld_31", 62, 2)
        };
        auto sfg_meter0_state_mem_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter0_state_mem_cfg),
                0x350000,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_meter0_state_mem_cfg", sfg_meter0_state_mem_cfg_prop);
        fld_map_t sfg_meter1_state_mem_cfg {
            CREATE_ENTRY("fld_0", 0, 2),
            CREATE_ENTRY("fld_1", 2, 2),
            CREATE_ENTRY("fld_2", 4, 2),
            CREATE_ENTRY("fld_3", 6, 2),
            CREATE_ENTRY("fld_4", 8, 2),
            CREATE_ENTRY("fld_5", 10, 2),
            CREATE_ENTRY("fld_6", 12, 2),
            CREATE_ENTRY("fld_7", 14, 2),
            CREATE_ENTRY("fld_8", 16, 2),
            CREATE_ENTRY("fld_9", 18, 2),
            CREATE_ENTRY("fld_10", 20, 2),
            CREATE_ENTRY("fld_11", 22, 2),
            CREATE_ENTRY("fld_12", 24, 2),
            CREATE_ENTRY("fld_13", 26, 2),
            CREATE_ENTRY("fld_14", 28, 2),
            CREATE_ENTRY("fld_15", 30, 2),
            CREATE_ENTRY("fld_16", 32, 2),
            CREATE_ENTRY("fld_17", 34, 2),
            CREATE_ENTRY("fld_18", 36, 2),
            CREATE_ENTRY("fld_19", 38, 2),
            CREATE_ENTRY("fld_20", 40, 2),
            CREATE_ENTRY("fld_21", 42, 2),
            CREATE_ENTRY("fld_22", 44, 2),
            CREATE_ENTRY("fld_23", 46, 2),
            CREATE_ENTRY("fld_24", 48, 2),
            CREATE_ENTRY("fld_25", 50, 2),
            CREATE_ENTRY("fld_26", 52, 2),
            CREATE_ENTRY("fld_27", 54, 2),
            CREATE_ENTRY("fld_28", 56, 2),
            CREATE_ENTRY("fld_29", 58, 2),
            CREATE_ENTRY("fld_30", 60, 2),
            CREATE_ENTRY("fld_31", 62, 2)
        };
        auto sfg_meter1_state_mem_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter1_state_mem_cfg),
                0x350200,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_meter1_state_mem_cfg", sfg_meter1_state_mem_cfg_prop);
// END sfg
    }
    {
// BEGIN fms
        auto fms_0 = nu_rng[0].add_an({"efp_rfp","fms"}, 0xCC00000, 1, 0x0);
        fld_map_t fms_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fms_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fms_0, "fms_timeout_thresh_cfg", fms_timeout_thresh_cfg_prop);
        fld_map_t fms_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fms_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fms_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fms_0, "fms_timeout_clr", fms_timeout_clr_prop);
        fld_map_t fms_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fms_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(fms_spare_pio),
                                      0x98,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(fms_0, "fms_spare_pio", fms_spare_pio_prop);
        fld_map_t fms_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fms_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fms_scratchpad),
                                       0xA0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fms_0, "fms_scratchpad", fms_scratchpad_prop);
        fld_map_t fms_mem_init_start_cfg {
            CREATE_ENTRY("fld_meter0_ctx_mem", 0, 1),
            CREATE_ENTRY("fld_meter0_cfg_mem", 1, 1),
            CREATE_ENTRY("fld_meter0_green_cntr_mem", 2, 1),
            CREATE_ENTRY("fld_meter0_yellow_cntr_mem", 3, 1),
            CREATE_ENTRY("fld_meter0_red_cntr_mem", 4, 1),
            CREATE_ENTRY("fld_meter1_ctx_mem", 5, 1),
            CREATE_ENTRY("fld_meter1_cfg_mem", 6, 1),
            CREATE_ENTRY("fld_meter1_green_cntr_mem", 7, 1),
            CREATE_ENTRY("fld_meter1_yellow_cntr_mem", 8, 1),
            CREATE_ENTRY("fld_meter1_red_cntr_mem", 9, 1),
            CREATE_ENTRY("fld_bank0_stats_cntr_mem", 10, 1),
            CREATE_ENTRY("fld_bank0_stats_cfg_mem", 11, 1),
            CREATE_ENTRY("fld_bank1_stats_cntr_mem", 12, 1),
            CREATE_ENTRY("fld_bank1_stats_cfg_mem", 13, 1),
            CREATE_ENTRY("fld_bank2_stats_cntr_mem", 14, 1),
            CREATE_ENTRY("fld_bank2_stats_cfg_mem", 15, 1),
            CREATE_ENTRY("fld_bank3_stats_cntr_mem", 16, 1),
            CREATE_ENTRY("fld_bank3_stats_cfg_mem", 17, 1),
            CREATE_ENTRY("fld_psw_eop_info_fifo_mem", 18, 1),
            CREATE_ENTRY("fld_sfg_ctx_mem", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto fms_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_mem_init_start_cfg),
                                               0xA8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fms_0, "fms_mem_init_start_cfg", fms_mem_init_start_cfg_prop);
        fld_map_t fms_mem_err_inj_cfg {
            CREATE_ENTRY("fld_meter0_ctx_mem", 0, 1),
            CREATE_ENTRY("fld_meter0_cfg_mem", 1, 1),
            CREATE_ENTRY("fld_meter0_green_cntr_mem", 2, 1),
            CREATE_ENTRY("fld_meter0_yellow_cntr_mem", 3, 1),
            CREATE_ENTRY("fld_meter0_red_cntr_mem", 4, 1),
            CREATE_ENTRY("fld_meter1_ctx_mem", 5, 1),
            CREATE_ENTRY("fld_meter1_cfg_mem", 6, 1),
            CREATE_ENTRY("fld_meter1_green_cntr_mem", 7, 1),
            CREATE_ENTRY("fld_meter1_yellow_cntr_mem", 8, 1),
            CREATE_ENTRY("fld_meter1_red_cntr_mem", 9, 1),
            CREATE_ENTRY("fld_bank0_stats_cntr_mem", 10, 1),
            CREATE_ENTRY("fld_bank0_stats_cfg_mem", 11, 1),
            CREATE_ENTRY("fld_bank1_stats_cntr_mem", 12, 1),
            CREATE_ENTRY("fld_bank1_stats_cfg_mem", 13, 1),
            CREATE_ENTRY("fld_bank2_stats_cntr_mem", 14, 1),
            CREATE_ENTRY("fld_bank2_stats_cfg_mem", 15, 1),
            CREATE_ENTRY("fld_bank3_stats_cntr_mem", 16, 1),
            CREATE_ENTRY("fld_bank3_stats_cfg_mem", 17, 1),
            CREATE_ENTRY("fld_psw_eop_info_fifo_mem", 18, 1),
            CREATE_ENTRY("fld_sfg_ctx_mem", 19, 1),
            CREATE_ENTRY("fld_err_type", 20, 1),
            CREATE_ENTRY("__rsvd", 21, 43)
        };
        auto fms_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fms_mem_err_inj_cfg),
                                            0xD0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fms_0, "fms_mem_err_inj_cfg", fms_mem_err_inj_cfg_prop);
        fld_map_t fms_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_fla_ring_module_id_cfg),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(fms_0, "fms_fla_ring_module_id_cfg", fms_fla_ring_module_id_cfg_prop);
        fld_map_t fms_timer_ctrl_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_bgnd_updt_enable", 1, 1),
            CREATE_ENTRY("fld_scan_intvl_cnt", 2, 9),
            CREATE_ENTRY("fld_part_timer_cnt", 11, 5),
            CREATE_ENTRY("fld_base_timer_cnt", 16, 5),
            CREATE_ENTRY("fld_max_timestamp_wrap_val", 21, 24),
            CREATE_ENTRY("__rsvd", 45, 19)
        };
        auto fms_timer_ctrl_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fms_timer_ctrl_cfg),
                                           0xE0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fms_0, "fms_timer_ctrl_cfg", fms_timer_ctrl_cfg_prop);
        fld_map_t fms_misc_cfg {
            CREATE_ENTRY("fld_bank0_vld_map", 0, 4),
            CREATE_ENTRY("fld_bank1_vld_map", 4, 4),
            CREATE_ENTRY("fld_bank2_vld_map", 8, 4),
            CREATE_ENTRY("fld_pps_len_val", 12, 14),
            CREATE_ENTRY("fld_meter_adj_val", 26, 14),
            CREATE_ENTRY("fld_stats_adj_val", 40, 14),
            CREATE_ENTRY("__rsvd", 54, 10)
        };
        auto fms_misc_cfg_prop = csr_prop_t(
                                     std::make_shared<csr_s>(fms_misc_cfg),
                                     0xE8,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(fms_0, "fms_misc_cfg", fms_misc_cfg_prop);
        fld_map_t fms_sfg_ctx_mem_dhs {
            CREATE_ENTRY("fld_meter0_idx_vld", 0, 1),
            CREATE_ENTRY("fld_meter0_idx", 1, 8),
            CREATE_ENTRY("fld_meter0_state", 9, 2),
            CREATE_ENTRY("fld_meter1_idx_vld", 11, 1),
            CREATE_ENTRY("fld_meter1_idx", 12, 8),
            CREATE_ENTRY("fld_meter1_state", 20, 2),
            CREATE_ENTRY("fld_bank0_cntr_idx_vld", 22, 1),
            CREATE_ENTRY("fld_bank0_cntr_idx", 23, 9),
            CREATE_ENTRY("fld_bank1_cntr_idx_vld", 32, 1),
            CREATE_ENTRY("fld_bank1_cntr_idx", 33, 9),
            CREATE_ENTRY("fld_bank2_cntr_idx_vld", 42, 1),
            CREATE_ENTRY("fld_bank2_cntr_idx", 43, 9),
            CREATE_ENTRY("fld_bank3_cntr_idx_vld", 52, 1),
            CREATE_ENTRY("fld_bank3_cntr_idx", 53, 9),
            CREATE_ENTRY("fld_l3_plen", 62, 14),
            CREATE_ENTRY("__rsvd", 76, 52)
        };
        auto fms_sfg_ctx_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fms_sfg_ctx_mem_dhs),
                                            0x2000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(fms_0, "fms_sfg_ctx_mem_dhs", fms_sfg_ctx_mem_dhs_prop);
        fld_map_t fms_psw_eop_info_fifo_mem_dhs {
            CREATE_ENTRY("fld_pkt_tag_id", 0, 9),
            CREATE_ENTRY("fld_igr_l2_plen", 9, 14),
            CREATE_ENTRY("fld_egr_l2_plen", 23, 14),
            CREATE_ENTRY("fld_drop", 37, 1),
            CREATE_ENTRY("__rsvd", 38, 26)
        };
        auto fms_psw_eop_info_fifo_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_psw_eop_info_fifo_mem_dhs),
                    0x22000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_psw_eop_info_fifo_mem_dhs", fms_psw_eop_info_fifo_mem_dhs_prop);
        fld_map_t fms_meter0_ctx_mem_dhs {
            CREATE_ENTRY("fld_last_timestamp", 0, 24),
            CREATE_ENTRY("fld_comitd_bkt", 24, 24),
            CREATE_ENTRY("fld_excess_bkt", 48, 24),
            CREATE_ENTRY("__rsvd", 72, 56)
        };
        auto fms_meter0_ctx_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter0_ctx_mem_dhs),
                                               0x2A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter0_ctx_mem_dhs", fms_meter0_ctx_mem_dhs_prop);
        fld_map_t fms_meter0_cfg_mem_dhs {
            CREATE_ENTRY("fld_time_interval", 0, 4),
            CREATE_ENTRY("fld_crd_unit", 4, 4),
            CREATE_ENTRY("fld_comitd_crd_rate", 8, 7),
            CREATE_ENTRY("fld_excess_crd_rate", 15, 7),
            CREATE_ENTRY("fld_comitd_burst_size", 22, 16),
            CREATE_ENTRY("fld_excess_burst_size", 38, 16),
            CREATE_ENTRY("fld_mtr_mode", 54, 1),
            CREATE_ENTRY("fld_len_mode", 55, 1),
            CREATE_ENTRY("fld_rfc_mode", 56, 1),
            CREATE_ENTRY("fld_pps_mode", 57, 1),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto fms_meter0_cfg_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter0_cfg_mem_dhs),
                                               0x3A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter0_cfg_mem_dhs", fms_meter0_cfg_mem_dhs_prop);
        fld_map_t fms_meter0_green_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter0_green_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter0_green_cntr_mem_dhs),
                    0x3E000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter0_green_cntr_mem_dhs", fms_meter0_green_cntr_mem_dhs_prop);
        fld_map_t fms_meter0_yellow_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter0_yellow_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter0_yellow_cntr_mem_dhs),
                    0x42000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter0_yellow_cntr_mem_dhs", fms_meter0_yellow_cntr_mem_dhs_prop);
        fld_map_t fms_meter0_red_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter0_red_cntr_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_meter0_red_cntr_mem_dhs),
                0x46000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_meter0_red_cntr_mem_dhs", fms_meter0_red_cntr_mem_dhs_prop);
        fld_map_t fms_meter1_ctx_mem_dhs {
            CREATE_ENTRY("fld_last_timestamp", 0, 24),
            CREATE_ENTRY("fld_comitd_bkt", 24, 24),
            CREATE_ENTRY("fld_excess_bkt", 48, 24),
            CREATE_ENTRY("__rsvd", 72, 56)
        };
        auto fms_meter1_ctx_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter1_ctx_mem_dhs),
                                               0x4A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter1_ctx_mem_dhs", fms_meter1_ctx_mem_dhs_prop);
        fld_map_t fms_meter1_cfg_mem_dhs {
            CREATE_ENTRY("fld_time_interval", 0, 4),
            CREATE_ENTRY("fld_crd_unit", 4, 4),
            CREATE_ENTRY("fld_comitd_crd_rate", 8, 7),
            CREATE_ENTRY("fld_excess_crd_rate", 15, 7),
            CREATE_ENTRY("fld_comitd_burst_size", 22, 16),
            CREATE_ENTRY("fld_excess_burst_size", 38, 16),
            CREATE_ENTRY("fld_mtr_mode", 54, 1),
            CREATE_ENTRY("fld_len_mode", 55, 1),
            CREATE_ENTRY("fld_rfc_mode", 56, 1),
            CREATE_ENTRY("fld_pps_mode", 57, 1),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto fms_meter1_cfg_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter1_cfg_mem_dhs),
                                               0x5A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter1_cfg_mem_dhs", fms_meter1_cfg_mem_dhs_prop);
        fld_map_t fms_meter1_green_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter1_green_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter1_green_cntr_mem_dhs),
                    0x5E000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter1_green_cntr_mem_dhs", fms_meter1_green_cntr_mem_dhs_prop);
        fld_map_t fms_meter1_yellow_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter1_yellow_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter1_yellow_cntr_mem_dhs),
                    0x62000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter1_yellow_cntr_mem_dhs", fms_meter1_yellow_cntr_mem_dhs_prop);
        fld_map_t fms_meter1_red_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter1_red_cntr_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_meter1_red_cntr_mem_dhs),
                0x66000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_meter1_red_cntr_mem_dhs", fms_meter1_red_cntr_mem_dhs_prop);
        fld_map_t fms_bank0_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank0_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank0_stats_cfg_mem_dhs),
                0x6A000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank0_stats_cfg_mem_dhs", fms_bank0_stats_cfg_mem_dhs_prop);
        fld_map_t fms_bank1_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank1_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank1_stats_cfg_mem_dhs),
                0x6C000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank1_stats_cfg_mem_dhs", fms_bank1_stats_cfg_mem_dhs_prop);
        fld_map_t fms_bank2_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank2_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank2_stats_cfg_mem_dhs),
                0x6E000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank2_stats_cfg_mem_dhs", fms_bank2_stats_cfg_mem_dhs_prop);
        fld_map_t fms_bank3_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank3_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank3_stats_cfg_mem_dhs),
                0x70000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank3_stats_cfg_mem_dhs", fms_bank3_stats_cfg_mem_dhs_prop);
        fld_map_t fms_stats_cntr_mem_dhs {
            CREATE_ENTRY("fld_bank0_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_bank0_pkt_cnt", 35, 29),
            CREATE_ENTRY("fld_bank1_byte_cnt", 64, 35),
            CREATE_ENTRY("fld_bank1_pkt_cnt", 99, 29),
            CREATE_ENTRY("fld_bank2_byte_cnt", 128, 35),
            CREATE_ENTRY("fld_bank2_pkt_cnt", 163, 29),
            CREATE_ENTRY("fld_bank3_byte_cnt", 192, 35),
            CREATE_ENTRY("fld_bank3_pkt_cnt", 227, 29)
        };
        auto fms_stats_cntr_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_stats_cntr_mem_dhs),
                                               0x74000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_stats_cntr_mem_dhs", fms_stats_cntr_mem_dhs_prop);
// END fms
    }
    {
// BEGIN efp_rfp_lcl
        auto efp_rfp_lcl_0 = nu_rng[0].add_an({"efp_rfp","efp_rfp_lcl"}, 0xCE00000, 1, 0x0);
        fld_map_t efp_rfp_lcl_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_lcl_timeout_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(efp_rfp_lcl_timeout_thresh_cfg),
                    0x0,
                    CSR_TYPE::REG,
                    1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timeout_thresh_cfg", efp_rfp_lcl_timeout_thresh_cfg_prop);
        fld_map_t efp_rfp_lcl_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto efp_rfp_lcl_timeout_clr_prop = csr_prop_t(
                                                std::make_shared<csr_s>(efp_rfp_lcl_timeout_clr),
                                                0x10,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_lcl_timeout_clr", efp_rfp_lcl_timeout_clr_prop);
        fld_map_t efp_rfp_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto efp_rfp_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(efp_rfp_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_spare_pio", efp_rfp_spare_pio_prop);
        fld_map_t efp_rfp_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto efp_rfp_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_scratchpad", efp_rfp_scratchpad_prop);
        fld_map_t efp_rfp_parser_offset {
            CREATE_ENTRY("offset", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto efp_rfp_parser_offset_prop = csr_prop_t(
                                              std::make_shared<csr_s>(efp_rfp_parser_offset),
                                              0x80,
                                              CSR_TYPE::REG,
                                              1);
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
        };
        auto efp_rfp_wct_macro_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(efp_rfp_wct_macro_cfg),
                                              0x88,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_wct_macro_cfg", efp_rfp_wct_macro_cfg_prop);
        fld_map_t efp_rfp_trfc_prfl {
            CREATE_ENTRY("efp_rfp_trfc_pri", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto efp_rfp_trfc_prfl_prop = csr_prop_t(
                                          std::make_shared<csr_s>(efp_rfp_trfc_prfl),
                                          0x98,
                                          CSR_TYPE::REG_LST,
                                          64);
        add_csr(efp_rfp_lcl_0, "efp_rfp_trfc_prfl", efp_rfp_trfc_prfl_prop);
        fld_map_t efp_rfp_rsrc_prf_strt {
            CREATE_ENTRY("start_pref", 0, 9),
            CREATE_ENTRY("__rsvd", 9, 55)
        };
        auto efp_rfp_rsrc_prf_strt_prop = csr_prop_t(
                                              std::make_shared<csr_s>(efp_rfp_rsrc_prf_strt),
                                              0x298,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_rsrc_prf_strt", efp_rfp_rsrc_prf_strt_prop);
        fld_map_t efp_rfp_num_bh_prf {
            CREATE_ENTRY("num_bh", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto efp_rfp_num_bh_prf_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_num_bh_prf),
                                           0x2A8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_num_bh_prf", efp_rfp_num_bh_prf_prop);
        fld_map_t efp_rfp_num_au_prf {
            CREATE_ENTRY("num_au", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto efp_rfp_num_au_prf_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_num_au_prf),
                                           0x2B0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_num_au_prf", efp_rfp_num_au_prf_prop);
        fld_map_t efp_rfp_bh_req_thr {
            CREATE_ENTRY("bh_req_thr", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto efp_rfp_bh_req_thr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_bh_req_thr),
                                           0x2B8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_bh_req_thr", efp_rfp_bh_req_thr_prop);
        fld_map_t efp_rfp_au_req_thr {
            CREATE_ENTRY("au_req_thr", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto efp_rfp_au_req_thr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_au_req_thr),
                                           0x2C0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_au_req_thr", efp_rfp_au_req_thr_prop);
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
        };
        auto efp_rfp_pc_cl_opts_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_pc_cl_opts),
                                           0x358,
                                           CSR_TYPE::REG_LST,
                                           9);
        add_csr(efp_rfp_lcl_0, "efp_rfp_pc_cl_opts", efp_rfp_pc_cl_opts_prop);
        fld_map_t efp_rfp_max_bh_allc_rq {
            CREATE_ENTRY("num_bh", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto efp_rfp_max_bh_allc_rq_prop = csr_prop_t(
                                               std::make_shared<csr_s>(efp_rfp_max_bh_allc_rq),
                                               0x3A0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_max_bh_allc_rq", efp_rfp_max_bh_allc_rq_prop);
        fld_map_t efp_rfp_max_au_allc_rq {
            CREATE_ENTRY("num_au", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto efp_rfp_max_au_allc_rq_prop = csr_prop_t(
                                               std::make_shared<csr_s>(efp_rfp_max_au_allc_rq),
                                               0x3A8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_max_au_allc_rq", efp_rfp_max_au_allc_rq_prop);
        fld_map_t efp_rfp_max_pend_allc_req {
            CREATE_ENTRY("max_num", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto efp_rfp_max_pend_allc_req_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_max_pend_allc_req),
                0x3B0,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_max_pend_allc_req", efp_rfp_max_pend_allc_req_prop);
        fld_map_t efp_rfp_clr_map_indv_pool {
            CREATE_ENTRY("clr_map", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_clr_map_indv_pool_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_clr_map_indv_pool),
                0x3B8,
                CSR_TYPE::REG_LST,
                16);
        add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_indv_pool", efp_rfp_clr_map_indv_pool_prop);
        fld_map_t efp_rfp_clr_map_tot_pool {
            CREATE_ENTRY("clr_map", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_clr_map_tot_pool_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_clr_map_tot_pool),
                0x438,
                CSR_TYPE::REG_LST,
                16);
        add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_tot_pool", efp_rfp_clr_map_tot_pool_prop);
        fld_map_t efp_rfp_tot_bmpool_xoff {
            CREATE_ENTRY("psw_sch_node", 0, 24),
            CREATE_ENTRY("psw_xoff_q_vec", 24, 8),
            CREATE_ENTRY("fcb_sch_node", 32, 8),
            CREATE_ENTRY("fcb_xoff_q_vec", 40, 8),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto efp_rfp_tot_bmpool_xoff_prop = csr_prop_t(
                                                std::make_shared<csr_s>(efp_rfp_tot_bmpool_xoff),
                                                0x4B8,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_tot_bmpool_xoff", efp_rfp_tot_bmpool_xoff_prop);
        fld_map_t efp_rfp_wu_thr_xoff {
            CREATE_ENTRY("psw_sch_node", 0, 24),
            CREATE_ENTRY("psw_xoff_q_vec", 24, 8),
            CREATE_ENTRY("fcb_sch_node", 32, 8),
            CREATE_ENTRY("fcb_xoff_q_vec", 40, 8),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto efp_rfp_wu_thr_xoff_prop = csr_prop_t(
                                            std::make_shared<csr_s>(efp_rfp_wu_thr_xoff),
                                            0x4C0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_wu_thr_xoff", efp_rfp_wu_thr_xoff_prop);
        fld_map_t efp_rfp_clr_map_tot_wu_occ {
            CREATE_ENTRY("clr_map", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_clr_map_tot_wu_occ_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_clr_map_tot_wu_occ),
                0x5C8,
                CSR_TYPE::REG_LST,
                16);
        add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_tot_wu_occ", efp_rfp_clr_map_tot_wu_occ_prop);
        fld_map_t efp_rfp_clr_map_nut_wu_occ {
            CREATE_ENTRY("clr_map", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_clr_map_nut_wu_occ_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_clr_map_nut_wu_occ),
                0x648,
                CSR_TYPE::REG_LST,
                16);
        add_csr(efp_rfp_lcl_0, "efp_rfp_clr_map_nut_wu_occ", efp_rfp_clr_map_nut_wu_occ_prop);
        fld_map_t efp_rfp_l4cs_kuc {
            CREATE_ENTRY("en_cs", 0, 1),
            CREATE_ENTRY("l4_type", 1, 1),
            CREATE_ENTRY("skip_zero_cs", 2, 1),
            CREATE_ENTRY("dis_ip_len_chk", 3, 1),
            CREATE_ENTRY("l3_hdr_num", 4, 3),
            CREATE_ENTRY("l4_hdr_num", 7, 3),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto efp_rfp_l4cs_kuc_prop = csr_prop_t(
                                         std::make_shared<csr_s>(efp_rfp_l4cs_kuc),
                                         0x6C8,
                                         CSR_TYPE::REG_LST,
                                         16);
        add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_kuc", efp_rfp_l4cs_kuc_prop);
        fld_map_t efp_rfp_proto_lst {
            CREATE_ENTRY("tcp_proto", 0, 8),
            CREATE_ENTRY("udp_proto", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto efp_rfp_proto_lst_prop = csr_prop_t(
                                          std::make_shared<csr_s>(efp_rfp_proto_lst),
                                          0x748,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_proto_lst", efp_rfp_proto_lst_prop);
        fld_map_t efp_rfp_rad_past_thr {
            CREATE_ENTRY("age_delta", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto efp_rfp_rad_past_thr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_rad_past_thr),
                                             0x750,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_rad_past_thr", efp_rfp_rad_past_thr_prop);
        fld_map_t efp_rfp_rad_futr_thr {
            CREATE_ENTRY("age_delta", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto efp_rfp_rad_futr_thr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_rad_futr_thr),
                                             0x758,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_rad_futr_thr", efp_rfp_rad_futr_thr_prop);
        fld_map_t efp_rfp_rad_enable {
            CREATE_ENTRY("en", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto efp_rfp_rad_enable_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_rad_enable),
                                           0x760,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_rad_enable", efp_rfp_rad_enable_prop);
        fld_map_t efp_rfp_estrm_bmpool_map {
            CREATE_ENTRY("bmpool", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto efp_rfp_estrm_bmpool_map_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_estrm_bmpool_map),
                0x768,
                CSR_TYPE::REG_LST,
                24);
        add_csr(efp_rfp_lcl_0, "efp_rfp_estrm_bmpool_map", efp_rfp_estrm_bmpool_map_prop);
        fld_map_t efp_rfp_fcp_pkt_adj {
            CREATE_ENTRY("fcb_adj_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto efp_rfp_fcp_pkt_adj_prop = csr_prop_t(
                                            std::make_shared<csr_s>(efp_rfp_fcp_pkt_adj),
                                            0x828,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_pkt_adj", efp_rfp_fcp_pkt_adj_prop);
        fld_map_t efp_rfp_fcp_block_sz {
            CREATE_ENTRY("fld_blk_sz", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto efp_rfp_fcp_block_sz_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_fcp_block_sz),
                                             0x830,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_block_sz", efp_rfp_fcp_block_sz_prop);
        fld_map_t efp_rfp_gph_sz {
            CREATE_ENTRY("gph_sz", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_gph_sz_prop = csr_prop_t(
                                       std::make_shared<csr_s>(efp_rfp_gph_sz),
                                       0x838,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_gph_sz", efp_rfp_gph_sz_prop);
        fld_map_t efp_rfp_fcp_qos_slct {
            CREATE_ENTRY("bit_slct", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_fcp_qos_slct_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_fcp_qos_slct),
                                             0x840,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_qos_slct", efp_rfp_fcp_qos_slct_prop);
        fld_map_t efp_rfp_fcp_stream_cfg {
            CREATE_ENTRY("fcp_stream", 0, 3),
            CREATE_ENTRY("fcp_present", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto efp_rfp_fcp_stream_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(efp_rfp_fcp_stream_cfg),
                                               0x848,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_fcp_stream_cfg", efp_rfp_fcp_stream_cfg_prop);
        fld_map_t efp_rfp_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto efp_rfp_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(efp_rfp_fla_ring_module_id_cfg),
                    0x850,
                    CSR_TYPE::REG,
                    1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_fla_ring_module_id_cfg", efp_rfp_fla_ring_module_id_cfg_prop);
        fld_map_t efp_rfp_bm_pool_rid_offset {
            CREATE_ENTRY("offset", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto efp_rfp_bm_pool_rid_offset_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_bm_pool_rid_offset),
                0x858,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_bm_pool_rid_offset", efp_rfp_bm_pool_rid_offset_prop);
        fld_map_t efp_rfp_num_bm_pools {
            CREATE_ENTRY("num_pools", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto efp_rfp_num_bm_pools_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_num_bm_pools),
                                             0x860,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_num_bm_pools", efp_rfp_num_bm_pools_prop);
        fld_map_t efp_rfp_nut_wu_occ_offset {
            CREATE_ENTRY("offset", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto efp_rfp_nut_wu_occ_offset_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_nut_wu_occ_offset),
                0x868,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_nut_wu_occ_offset", efp_rfp_nut_wu_occ_offset_prop);
        fld_map_t efp_rfp_all_wu_occ_offset {
            CREATE_ENTRY("offset", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto efp_rfp_all_wu_occ_offset_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_all_wu_occ_offset),
                0x870,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_all_wu_occ_offset", efp_rfp_all_wu_occ_offset_prop);
        fld_map_t efp_rfp_bm_master_id {
            CREATE_ENTRY("client_id", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto efp_rfp_bm_master_id_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_bm_master_id),
                                             0x878,
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
        };
        auto efp_rfp_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_sram_err_inj_cfg),
                0x880,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_sram_err_inj_cfg", efp_rfp_sram_err_inj_cfg_prop);
        fld_map_t efp_rfp_snapshot_sym {
            CREATE_ENTRY("fld_val", 0, 1),
            CREATE_ENTRY("lb_grp_mem_idx", 1, 11),
            CREATE_ENTRY("rsvd", 12, 52)
        };
        auto efp_rfp_snapshot_sym_prop = csr_prop_t(
                                             std::make_shared<csr_s>(efp_rfp_snapshot_sym),
                                             0x8A8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_snapshot_sym", efp_rfp_snapshot_sym_prop);
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
        };
        auto efp_rfp_err_drop_mask_prop = csr_prop_t(
                                              std::make_shared<csr_s>(efp_rfp_err_drop_mask),
                                              0x8F8,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_err_drop_mask", efp_rfp_err_drop_mask_prop);
        fld_map_t efp_rfp_err_drop_wu_gen {
            CREATE_ENTRY("cluster_id", 0, 4),
            CREATE_ENTRY("dlid", 4, 5),
            CREATE_ENTRY("wu_queue_id", 9, 8),
            CREATE_ENTRY("sw_opcode", 17, 24),
            CREATE_ENTRY("__rsvd", 41, 23)
        };
        auto efp_rfp_err_drop_wu_gen_prop = csr_prop_t(
                                                std::make_shared<csr_s>(efp_rfp_err_drop_wu_gen),
                                                0x900,
                                                CSR_TYPE::REG,
                                                1);
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
        };
        auto efp_rfp_clbp_mem_prop = csr_prop_t(
                                         std::make_shared<csr_s>(efp_rfp_clbp_mem),
                                         0xC00,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_clbp_mem", efp_rfp_clbp_mem_prop);
        fld_map_t efp_rfp_lb_grp_mem {
            CREATE_ENTRY("wu_cluster", 0, 4),
            CREATE_ENTRY("wu_queue", 4, 8),
            CREATE_ENTRY("dlid", 12, 5),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto efp_rfp_lb_grp_mem_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_lb_grp_mem),
                                           0x8000,
                                           CSR_TYPE::TBL,
                                           1);
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
        };
        auto efp_rfp_rewr_inst_prop = csr_prop_t(
                                          std::make_shared<csr_s>(efp_rfp_rewr_inst),
                                          0x28000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_rewr_inst", efp_rfp_rewr_inst_prop);
        fld_map_t efp_rfp_bmpool_node_map {
            CREATE_ENTRY("fcb_psw_slct", 0, 1),
            CREATE_ENTRY("sch_node", 1, 24),
            CREATE_ENTRY("xoff_q_vec", 25, 8),
            CREATE_ENTRY("__rsvd", 33, 31)
        };
        auto efp_rfp_bmpool_node_map_prop = csr_prop_t(
                                                std::make_shared<csr_s>(efp_rfp_bmpool_node_map),
                                                0x34000,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_bmpool_node_map", efp_rfp_bmpool_node_map_prop);
        fld_map_t efp_rfp_l4cs_tcam_key {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("key", 1, 21),
            CREATE_ENTRY("__rsvd", 22, 42)
        };
        auto efp_rfp_l4cs_tcam_key_prop = csr_prop_t(
                                              std::make_shared<csr_s>(efp_rfp_l4cs_tcam_key),
                                              0x35000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_tcam_key", efp_rfp_l4cs_tcam_key_prop);
        fld_map_t efp_rfp_l4cs_tcam_mask {
            CREATE_ENTRY("mask", 0, 21),
            CREATE_ENTRY("__rsvd", 21, 43)
        };
        auto efp_rfp_l4cs_tcam_mask_prop = csr_prop_t(
                                               std::make_shared<csr_s>(efp_rfp_l4cs_tcam_mask),
                                               0x35400,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_l4cs_tcam_mask", efp_rfp_l4cs_tcam_mask_prop);
        fld_map_t efp_rfp_rad_init {
            CREATE_ENTRY("sec_tunnel", 0, 1),
            CREATE_ENTRY("allw_non_sec_pkt", 1, 1),
            CREATE_ENTRY("init_seq_num", 2, 48),
            CREATE_ENTRY("bmpool", 50, 6),
            CREATE_ENTRY("__rsvd", 56, 8)
        };
        auto efp_rfp_rad_init_prop = csr_prop_t(
                                         std::make_shared<csr_s>(efp_rfp_rad_init),
                                         0x40000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(efp_rfp_lcl_0, "efp_rfp_rad_init", efp_rfp_rad_init_prop);
// END efp_rfp_lcl
    }
    {
// BEGIN stg6_ffe
        auto stg6_ffe_0 = nu_rng[0].add_an({"stg6_ffe"}, 0x10000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg6_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg6_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg6_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg6_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg6_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg6_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg6_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg6_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg6_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg6_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg6_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 423),
            CREATE_ENTRY("__rsvd", 423, 25)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg6_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg6_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg6_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg6_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg6_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg6_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg6_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg6_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg6_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg6_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg6_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg6_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg6_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg6_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg6_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg6_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg6_ffe_0, "act_dmem", act_dmem_prop);
// END stg6_ffe
    }
    {
// BEGIN efp_rfp_part1
        auto efp_rfp_part1_0 = nu_rng[0].add_an({"efp_rfp_part1"}, 0x14000000, 1, 0x0);
        fld_map_t efp_rfp_part1_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_part1_timeout_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(efp_rfp_part1_timeout_thresh_cfg),
                    0x0,
                    CSR_TYPE::REG,
                    1);
        add_csr(efp_rfp_part1_0, "efp_rfp_part1_timeout_thresh_cfg", efp_rfp_part1_timeout_thresh_cfg_prop);
        fld_map_t efp_rfp_part1_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto efp_rfp_part1_timeout_clr_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_part1_timeout_clr),
                0x10,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_part1_0, "efp_rfp_part1_timeout_clr", efp_rfp_part1_timeout_clr_prop);
        fld_map_t efp_rfp_part1_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto efp_rfp_part1_spare_pio_prop = csr_prop_t(
                                                std::make_shared<csr_s>(efp_rfp_part1_spare_pio),
                                                0x70,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(efp_rfp_part1_0, "efp_rfp_part1_spare_pio", efp_rfp_part1_spare_pio_prop);
        fld_map_t efp_rfp_part1_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto efp_rfp_part1_scratchpad_prop = csr_prop_t(
                std::make_shared<csr_s>(efp_rfp_part1_scratchpad),
                0x78,
                CSR_TYPE::REG,
                1);
        add_csr(efp_rfp_part1_0, "efp_rfp_part1_scratchpad", efp_rfp_part1_scratchpad_prop);
        fld_map_t efp_rfp_rng_cfg {
            CREATE_ENTRY("mode", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto efp_rfp_rng_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(efp_rfp_rng_cfg),
                                        0x80,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(efp_rfp_part1_0, "efp_rfp_rng_cfg", efp_rfp_rng_cfg_prop);
        fld_map_t efp_rfp_ffe_icount_cfg {
            CREATE_ENTRY("itr_cnt", 0, 3),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto efp_rfp_ffe_icount_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(efp_rfp_ffe_icount_cfg),
                                               0x88,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(efp_rfp_part1_0, "efp_rfp_ffe_icount_cfg", efp_rfp_ffe_icount_cfg_prop);
        fld_map_t efp_rfp_part1_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto efp_rfp_part1_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(efp_rfp_part1_fla_ring_module_id_cfg),
                    0x90,
                    CSR_TYPE::REG,
                    1);
        add_csr(efp_rfp_part1_0, "efp_rfp_part1_fla_ring_module_id_cfg", efp_rfp_part1_fla_ring_module_id_cfg_prop);
        fld_map_t efp_rfp_snpsht_cfg {
            CREATE_ENTRY("enable", 0, 1),
            CREATE_ENTRY("prv_fld_extr", 1, 56),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto efp_rfp_snpsht_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_snpsht_cfg),
                                           0x98,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_cfg", efp_rfp_snpsht_cfg_prop);
        fld_map_t efp_rfp_snpsht_mask {
            CREATE_ENTRY("val", 0, 64)
        };
        auto efp_rfp_snpsht_mask_prop = csr_prop_t(
                                            std::make_shared<csr_s>(efp_rfp_snpsht_mask),
                                            0xA0,
                                            CSR_TYPE::REG,
                                            5);
        add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_mask", efp_rfp_snpsht_mask_prop);
        fld_map_t efp_rfp_snpsht_val {
            CREATE_ENTRY("val", 0, 64)
        };
        auto efp_rfp_snpsht_val_prop = csr_prop_t(
                                           std::make_shared<csr_s>(efp_rfp_snpsht_val),
                                           0xC8,
                                           CSR_TYPE::REG,
                                           5);
        add_csr(efp_rfp_part1_0, "efp_rfp_snpsht_val", efp_rfp_snpsht_val_prop);
        fld_map_t efp_rfp_part1_sram_err_inj_cfg {
            CREATE_ENTRY("efp_rfp_mdi_mem", 0, 1),
            CREATE_ENTRY("err_type", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto efp_rfp_part1_sram_err_inj_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(efp_rfp_part1_sram_err_inj_cfg),
                    0xF0,
                    CSR_TYPE::REG,
                    1);
        add_csr(efp_rfp_part1_0, "efp_rfp_part1_sram_err_inj_cfg", efp_rfp_part1_sram_err_inj_cfg_prop);
        fld_map_t efp_rfp_rng_cam {
            CREATE_ENTRY("data", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto efp_rfp_rng_cam_prop = csr_prop_t(
                                        std::make_shared<csr_s>(efp_rfp_rng_cam),
                                        0x200,
                                        CSR_TYPE::TBL,
                                        1);
        add_csr(efp_rfp_part1_0, "efp_rfp_rng_cam", efp_rfp_rng_cam_prop);
        fld_map_t efp_rfp_mdi_mem_dhs {
            CREATE_ENTRY("data", 0, 400),
            CREATE_ENTRY("__rsvd", 400, 48)
        };
        auto efp_rfp_mdi_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(efp_rfp_mdi_mem_dhs),
                                            0x1800,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(efp_rfp_part1_0, "efp_rfp_mdi_mem_dhs", efp_rfp_mdi_mem_dhs_prop);
// END efp_rfp_part1
    }
    {
// BEGIN epg_rdp_lcl
        auto epg_rdp_lcl_0 = nu_rng[0].add_an({"epg_rdp","epg_rdp_lcl"}, 0x14030000, 1, 0x0);
        fld_map_t epg_rdp_lcl_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto epg_rdp_lcl_timeout_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(epg_rdp_lcl_timeout_thresh_cfg),
                    0x0,
                    CSR_TYPE::REG,
                    1);
        add_csr(epg_rdp_lcl_0, "epg_rdp_lcl_timeout_thresh_cfg", epg_rdp_lcl_timeout_thresh_cfg_prop);
        fld_map_t epg_rdp_lcl_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto epg_rdp_lcl_timeout_clr_prop = csr_prop_t(
                                                std::make_shared<csr_s>(epg_rdp_lcl_timeout_clr),
                                                0x10,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(epg_rdp_lcl_0, "epg_rdp_lcl_timeout_clr", epg_rdp_lcl_timeout_clr_prop);
        fld_map_t epg_rdp_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto epg_rdp_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(epg_rdp_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(epg_rdp_lcl_0, "epg_rdp_spare_pio", epg_rdp_spare_pio_prop);
        fld_map_t epg_rdp_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto epg_rdp_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(epg_rdp_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(epg_rdp_lcl_0, "epg_rdp_scratchpad", epg_rdp_scratchpad_prop);
        fld_map_t parser_offset {
            CREATE_ENTRY("offset", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto parser_offset_prop = csr_prop_t(
                                      std::make_shared<csr_s>(parser_offset),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(epg_rdp_lcl_0, "parser_offset", parser_offset_prop);
        fld_map_t erp_key_lu_63_0 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto erp_key_lu_63_0_prop = csr_prop_t(
                                        std::make_shared<csr_s>(erp_key_lu_63_0),
                                        0x0,
                                        CSR_TYPE::REG_LST,
                                        1);
        add_csr(epg_rdp_lcl_0, "erp_key_lu_63_0", erp_key_lu_63_0_prop);
        fld_map_t erp_key_lu_127_64 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto erp_key_lu_127_64_prop = csr_prop_t(
                                          std::make_shared<csr_s>(erp_key_lu_127_64),
                                          0x0,
                                          CSR_TYPE::REG_LST,
                                          1);
        add_csr(epg_rdp_lcl_0, "erp_key_lu_127_64", erp_key_lu_127_64_prop);
        fld_map_t erp_key_lu_191_128 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto erp_key_lu_191_128_prop = csr_prop_t(
                                           std::make_shared<csr_s>(erp_key_lu_191_128),
                                           0x0,
                                           CSR_TYPE::REG_LST,
                                           1);
        add_csr(epg_rdp_lcl_0, "erp_key_lu_191_128", erp_key_lu_191_128_prop);
        fld_map_t erp_key_lu_255_192 {
            CREATE_ENTRY("key", 0, 64)
        };
        auto erp_key_lu_255_192_prop = csr_prop_t(
                                           std::make_shared<csr_s>(erp_key_lu_255_192),
                                           0x0,
                                           CSR_TYPE::REG_LST,
                                           1);
        add_csr(epg_rdp_lcl_0, "erp_key_lu_255_192", erp_key_lu_255_192_prop);
        fld_map_t erp_key_len_lu {
            CREATE_ENTRY("key_len", 0, 2),
            CREATE_ENTRY("salt", 2, 16),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto erp_key_len_lu_prop = csr_prop_t(
                                       std::make_shared<csr_s>(erp_key_len_lu),
                                       0x2A8,
                                       CSR_TYPE::REG_LST,
                                       17);
        add_csr(epg_rdp_lcl_0, "erp_key_len_lu", erp_key_len_lu_prop);
        fld_map_t erp_prw_cfg_min_pkt_len {
            CREATE_ENTRY("min_pkt_len", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto erp_prw_cfg_min_pkt_len_prop = csr_prop_t(
                                                std::make_shared<csr_s>(erp_prw_cfg_min_pkt_len),
                                                0x330,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(epg_rdp_lcl_0, "erp_prw_cfg_min_pkt_len", erp_prw_cfg_min_pkt_len_prop);
        fld_map_t erp_fcp_stream_map {
            CREATE_ENTRY("fcp_stream", 0, 3),
            CREATE_ENTRY("fcp_present", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto erp_fcp_stream_map_prop = csr_prop_t(
                                           std::make_shared<csr_s>(erp_fcp_stream_map),
                                           0x338,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(epg_rdp_lcl_0, "erp_fcp_stream_map", erp_fcp_stream_map_prop);
        fld_map_t erp_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto erp_fla_ring_module_id_cfg_prop = csr_prop_t(
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
        };
        auto epg_rdp_sram_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(epg_rdp_sram_err_inj_cfg),
                0x348,
                CSR_TYPE::REG,
                1);
        add_csr(epg_rdp_lcl_0, "epg_rdp_sram_err_inj_cfg", epg_rdp_sram_err_inj_cfg_prop);
// END epg_rdp_lcl
    }
    {
// BEGIN fep_nu
        auto fep_nu_0 = nu_rng[0].add_an({"fepw_nu","fep_nu"}, 0x14030400, 1, 0x0);
        fld_map_t fep_nu_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fep_nu_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_timeout_thresh_cfg", fep_nu_timeout_thresh_cfg_prop);
        fld_map_t fep_nu_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fep_nu_timeout_clr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fep_nu_timeout_clr),
                                           0x10,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fep_nu_0, "fep_nu_timeout_clr", fep_nu_timeout_clr_prop);
        fld_map_t fep_nu_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fep_nu_spare_pio_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fep_nu_spare_pio),
                                         0x70,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(fep_nu_0, "fep_nu_spare_pio", fep_nu_spare_pio_prop);
        fld_map_t fep_nu_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fep_nu_scratchpad_prop = csr_prop_t(
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
        };
        auto fep_nu_misc_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_mem_err_inj_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_mem_err_inj_cfg),
                                               0x88,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_mem_err_inj_cfg", fep_nu_mem_err_inj_cfg_prop);
        fld_map_t fep_nu_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_fla_ring_module_id_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_fla_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fep_nu_fla_cfg),
                                       0x98,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fep_nu_0, "fep_nu_fla_cfg", fep_nu_fla_cfg_prop);
        fld_map_t fep_nu_local_id {
            CREATE_ENTRY("erp_local_id", 0, 5),
            CREATE_ENTRY("etp_min_local_id", 5, 5),
            CREATE_ENTRY("nwqm_local_id", 10, 5),
            CREATE_ENTRY("wro_local_id", 15, 5),
            CREATE_ENTRY("fae_local_id", 20, 5),
            CREATE_ENTRY("mpg_local_id", 25, 5),
            CREATE_ENTRY("etp_max_local_id", 30, 5),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto fep_nu_local_id_prop = csr_prop_t(
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
        };
        auto fep_nu_strict_order_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fep_nu_strict_order),
                                            0xB0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fep_nu_0, "fep_nu_strict_order", fep_nu_strict_order_prop);
        fld_map_t fep_nu_erp_snx_cdt_init_val {
            CREATE_ENTRY("erp_vc0_cdt", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_erp_snx_cdt_init_val_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_erp_snx_cdt_init_val),
                0xB8,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_erp_snx_cdt_init_val", fep_nu_erp_snx_cdt_init_val_prop);
        fld_map_t fep_nu_nwqm_snx_cdt_init_val {
            CREATE_ENTRY("nwqm_vc0_cdt", 0, 8),
            CREATE_ENTRY("nwqm_vc1_cdt", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fep_nu_nwqm_snx_cdt_init_val_prop = csr_prop_t(
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
        };
        auto fep_nu_wro_snx_cdt_init_val_prop = csr_prop_t(
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
        };
        auto fep_nu_fae_snx_cdt_init_val_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_fae_snx_cdt_init_val),
                0xD0,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_fae_snx_cdt_init_val", fep_nu_fae_snx_cdt_init_val_prop);
        fld_map_t fep_nu_mpg_snx_cdt_init_val {
            CREATE_ENTRY("mpg_vc0_cdt", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_mpg_snx_cdt_init_val_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_mpg_snx_cdt_init_val),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_mpg_snx_cdt_init_val", fep_nu_mpg_snx_cdt_init_val_prop);
        fld_map_t fep_nu_erp_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_nu_erp_sn_filter_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fep_nu_erp_sn_filter),
                                             0xE0,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fep_nu_0, "fep_nu_erp_sn_filter", fep_nu_erp_sn_filter_prop);
        fld_map_t fep_nu_nwqm_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_nu_nwqm_sn_filter_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fep_nu_nwqm_sn_filter),
                                              0xE8,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fep_nu_0, "fep_nu_nwqm_sn_filter", fep_nu_nwqm_sn_filter_prop);
        fld_map_t fep_nu_fae_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_nu_fae_sn_filter_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fep_nu_fae_sn_filter),
                                             0xF0,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fep_nu_0, "fep_nu_fae_sn_filter", fep_nu_fae_sn_filter_prop);
        fld_map_t fep_nu_mpg_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_nu_mpg_sn_filter_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fep_nu_mpg_sn_filter),
                                             0xF8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fep_nu_0, "fep_nu_mpg_sn_filter", fep_nu_mpg_sn_filter_prop);
        fld_map_t fep_nu_snx_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_nu_snx_sn_filter_prop = csr_prop_t(
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
        };
        auto fep_nu_nwqm_lsn_arb_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_snx_lsn_arb_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_snx_lsn_arb_cfg),
                                               0x110,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_snx_lsn_arb_cfg", fep_nu_snx_lsn_arb_cfg_prop);
        fld_map_t fep_nu_dest_cfg_cmd {
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
        };
        auto fep_nu_dest_cfg_cmd_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fep_nu_dest_cfg_cmd),
                                            0x118,
                                            CSR_TYPE::REG,
                                            4);
        add_csr(fep_nu_0, "fep_nu_dest_cfg_cmd", fep_nu_dest_cfg_cmd_prop);
        fld_map_t fep_nu_hbm_ddr_hash {
            CREATE_ENTRY("ddr_buf_mode", 0, 2),
            CREATE_ENTRY("ddr_coh_mode", 2, 2),
            CREATE_ENTRY("hbm_buf_mode", 4, 2),
            CREATE_ENTRY("hbm_coh_mode", 6, 2),
            CREATE_ENTRY("num_shard_log2", 8, 2),
            CREATE_ENTRY("mask0", 10, 26),
            CREATE_ENTRY("mask1", 36, 26),
            CREATE_ENTRY("__rsvd", 62, 2)
        };
        auto fep_nu_hbm_ddr_hash_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fep_nu_hbm_ddr_hash),
                                            0x138,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fep_nu_0, "fep_nu_hbm_ddr_hash", fep_nu_hbm_ddr_hash_prop);
        fld_map_t fep_nu_ddr_hash {
            CREATE_ENTRY("mask0", 0, 32),
            CREATE_ENTRY("mask1", 32, 32)
        };
        auto fep_nu_ddr_hash_prop = csr_prop_t(
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
        };
        auto fep_nu_addr_trans_hbm_pc_rsvd0_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_addr_trans_nu_mu_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_addr_trans_hu_nvram_ddr_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_addr_trans_rsvd1_cfg_prop = csr_prop_t(
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
        };
        auto fep_nu_addr_trans_rsvd2_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_addr_trans_rsvd2_cfg),
                0x168,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_addr_trans_rsvd2_cfg", fep_nu_addr_trans_rsvd2_cfg_prop);
        fld_map_t fep_nu_addr_trans_default_cfg {
            CREATE_ENTRY("gid", 0, 5),
            CREATE_ENTRY("lid", 5, 5),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto fep_nu_addr_trans_default_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_nu_addr_trans_default_cfg),
                    0x170,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_nu_0, "fep_nu_addr_trans_default_cfg", fep_nu_addr_trans_default_cfg_prop);
        fld_map_t fep_nu_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_sn_sent_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fep_nu_sn_sent_cnt),
                                           0x178,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fep_nu_0, "fep_nu_sn_sent_cnt", fep_nu_sn_sent_cnt_prop);
        fld_map_t fep_nu_sn_rcvd_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_sn_rcvd_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fep_nu_sn_rcvd_cnt),
                                           0x180,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fep_nu_0, "fep_nu_sn_rcvd_cnt", fep_nu_sn_rcvd_cnt_prop);
        fld_map_t fep_nu_lsn_addr_trans_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_lsn_addr_trans_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_nu_lsn_addr_trans_err_cnt),
                    0x188,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_nu_0, "fep_nu_lsn_addr_trans_err_cnt", fep_nu_lsn_addr_trans_err_cnt_prop);
        fld_map_t fep_nu_lsn_unknown_dest_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_lsn_unknown_dest_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_nu_lsn_unknown_dest_err_cnt),
                    0x190,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_nu_0, "fep_nu_lsn_unknown_dest_err_cnt", fep_nu_lsn_unknown_dest_err_cnt_prop);
        fld_map_t fep_nu_lsn_msg_filter_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_lsn_msg_filter_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_nu_lsn_msg_filter_err_cnt),
                    0x198,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_nu_0, "fep_nu_lsn_msg_filter_err_cnt", fep_nu_lsn_msg_filter_err_cnt_prop);
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
        };
        auto fep_nu_sn_msg_sent_incr_en_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_sn_msg_sent_incr_en),
                0x1A0,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_sn_msg_sent_incr_en", fep_nu_sn_msg_sent_incr_en_prop);
        fld_map_t fep_nu_erp_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_erp_sn_sent_cnt_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_erp_sn_sent_cnt),
                                               0x1A8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_erp_sn_sent_cnt", fep_nu_erp_sn_sent_cnt_prop);
        fld_map_t fep_nu_etp_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_etp_sn_sent_cnt_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_etp_sn_sent_cnt),
                                               0x1B0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_etp_sn_sent_cnt", fep_nu_etp_sn_sent_cnt_prop);
        fld_map_t fep_nu_nwqm_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_nwqm_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_nu_nwqm_sn_sent_cnt),
                                                0x1B8,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_nu_0, "fep_nu_nwqm_sn_sent_cnt", fep_nu_nwqm_sn_sent_cnt_prop);
        fld_map_t fep_nu_wro_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_wro_sn_sent_cnt_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_wro_sn_sent_cnt),
                                               0x1C0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_wro_sn_sent_cnt", fep_nu_wro_sn_sent_cnt_prop);
        fld_map_t fep_nu_fae_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_fae_sn_sent_cnt_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_fae_sn_sent_cnt),
                                               0x1C8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_fae_sn_sent_cnt", fep_nu_fae_sn_sent_cnt_prop);
        fld_map_t fep_nu_mpg_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_mpg_sn_sent_cnt_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_mpg_sn_sent_cnt),
                                               0x1D0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_mpg_sn_sent_cnt", fep_nu_mpg_sn_sent_cnt_prop);
        fld_map_t fep_nu_snx_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_snx_sn_sent_cnt_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_nu_snx_sn_sent_cnt),
                                               0x1D8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_nu_0, "fep_nu_snx_sn_sent_cnt", fep_nu_snx_sn_sent_cnt_prop);
        fld_map_t fep_nu_dn_ej_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_dn_ej_cnt_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fep_nu_dn_ej_cnt),
                                         0x1E0,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(fep_nu_0, "fep_nu_dn_ej_cnt", fep_nu_dn_ej_cnt_prop);
        fld_map_t fep_nu_dn_inj_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_nu_dn_inj_cnt_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fep_nu_dn_inj_cnt),
                                          0x1E8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fep_nu_0, "fep_nu_dn_inj_cnt", fep_nu_dn_inj_cnt_prop);
        fld_map_t fep_nu_ldn_addr_trans_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_ldn_addr_trans_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_nu_ldn_addr_trans_err_cnt),
                    0x1F0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_nu_0, "fep_nu_ldn_addr_trans_err_cnt", fep_nu_ldn_addr_trans_err_cnt_prop);
        fld_map_t fep_nu_ldn_unknown_dest_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_ldn_unknown_dest_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_nu_ldn_unknown_dest_err_cnt),
                    0x1F8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_nu_0, "fep_nu_ldn_unknown_dest_err_cnt", fep_nu_ldn_unknown_dest_err_cnt_prop);
        fld_map_t fep_nu_dn_metadata_merr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_dn_metadata_merr_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_dn_metadata_merr_cnt),
                0x200,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_dn_metadata_merr_cnt", fep_nu_dn_metadata_merr_cnt_prop);
        fld_map_t fep_nu_dn_metadata_serr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_dn_metadata_serr_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_nu_dn_metadata_serr_cnt),
                0x208,
                CSR_TYPE::REG,
                1);
        add_csr(fep_nu_0, "fep_nu_dn_metadata_serr_cnt", fep_nu_dn_metadata_serr_cnt_prop);
        fld_map_t fep_nu_dn_data_merr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_dn_data_merr_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_nu_dn_data_merr_cnt),
                                                0x210,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_nu_0, "fep_nu_dn_data_merr_cnt", fep_nu_dn_data_merr_cnt_prop);
        fld_map_t fep_nu_dn_data_serr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_nu_dn_data_serr_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_nu_dn_data_serr_cnt),
                                                0x218,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_nu_0, "fep_nu_dn_data_serr_cnt", fep_nu_dn_data_serr_cnt_prop);
// END fep_nu
    }
    {
// BEGIN dnr
        auto dnr_0 = nu_rng[0].add_an({"fepw_nu","dnr"}, 0x14040000, 1, 0x0);
        fld_map_t dnr_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto dnr_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dnr_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dnr_0, "dnr_timeout_thresh_cfg", dnr_timeout_thresh_cfg_prop);
        fld_map_t dnr_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto dnr_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(dnr_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(dnr_0, "dnr_timeout_clr", dnr_timeout_clr_prop);
        fld_map_t dnr_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto dnr_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(dnr_spare_pio),
                                      0x70,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(dnr_0, "dnr_spare_pio", dnr_spare_pio_prop);
        fld_map_t dnr_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto dnr_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dnr_scratchpad),
                                       0x78,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dnr_0, "dnr_scratchpad", dnr_scratchpad_prop);
        fld_map_t dnr_alt_ej_port {
            CREATE_ENTRY("val", 0, 3),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto dnr_alt_ej_port_prop = csr_prop_t(
                                        std::make_shared<csr_s>(dnr_alt_ej_port),
                                        0x80,
                                        CSR_TYPE::REG_LST,
                                        5);
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
        };
        auto dnr_cong_ctrl_prop = csr_prop_t(
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
        };
        auto dnr_route_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(dnr_route_cfg),
                                      0xB0,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(dnr_0, "dnr_route_cfg", dnr_route_cfg_prop);
        fld_map_t dnr_credit_cfg {
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc0", 0, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc1", 5, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc2", 10, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc3", 15, 5),
            CREATE_ENTRY("ibuf_max_shared_credits", 20, 5),
            CREATE_ENTRY("ebuf_min_rsvd_credits_vc_set0", 25, 7),
            CREATE_ENTRY("ebuf_min_rsvd_credits_vc_set1", 32, 7),
            CREATE_ENTRY("ebuf_max_shared_credits", 39, 7),
            CREATE_ENTRY("ibuf_shared_credits_hysteresis", 46, 5),
            CREATE_ENTRY("ebuf_shared_credits_hysteresis", 51, 7),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto dnr_credit_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dnr_credit_cfg),
                                       0xB8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dnr_0, "dnr_credit_cfg", dnr_credit_cfg_prop);
        fld_map_t dnr_injection_credit_cfg {
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc0", 0, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc1", 5, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc2", 10, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc3", 15, 5),
            CREATE_ENTRY("ibuf_max_shared_credits", 20, 5),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto dnr_injection_credit_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(dnr_injection_credit_cfg),
                0xC0,
                CSR_TYPE::REG,
                1);
        add_csr(dnr_0, "dnr_injection_credit_cfg", dnr_injection_credit_cfg_prop);
        fld_map_t dnr_vc_sel_wt_cfg {
            CREATE_ENTRY("vc0_wt", 0, 2),
            CREATE_ENTRY("vc1_wt", 2, 2),
            CREATE_ENTRY("vc2_wt", 4, 2),
            CREATE_ENTRY("vc3_wt", 6, 2),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto dnr_vc_sel_wt_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(dnr_vc_sel_wt_cfg),
                                          0xC8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(dnr_0, "dnr_vc_sel_wt_cfg", dnr_vc_sel_wt_cfg_prop);
        fld_map_t dnr_default_dgid_cfg {
            CREATE_ENTRY("val", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto dnr_default_dgid_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(dnr_default_dgid_cfg),
                                             0xD0,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(dnr_0, "dnr_default_dgid_cfg", dnr_default_dgid_cfg_prop);
        fld_map_t dnr_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto dnr_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(dnr_fla_ring_module_id_cfg),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(dnr_0, "dnr_fla_ring_module_id_cfg", dnr_fla_ring_module_id_cfg_prop);
        fld_map_t dnr_credit_watchdog_timer_cfg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto dnr_credit_watchdog_timer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(dnr_credit_watchdog_timer_cfg),
                    0xE0,
                    CSR_TYPE::REG,
                    1);
        add_csr(dnr_0, "dnr_credit_watchdog_timer_cfg", dnr_credit_watchdog_timer_cfg_prop);
        fld_map_t dnr_gid_to_coords_map {
            CREATE_ENTRY("coord_x", 0, 3),
            CREATE_ENTRY("coord_y", 3, 3),
            CREATE_ENTRY("use_alt_ej", 6, 1),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto dnr_gid_to_coords_map_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dnr_gid_to_coords_map),
                                              0x2000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(dnr_0, "dnr_gid_to_coords_map", dnr_gid_to_coords_map_prop);
        fld_map_t dnr_wt_table {
            CREATE_ENTRY("wx", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto dnr_wt_table_prop = csr_prop_t(
                                     std::make_shared<csr_s>(dnr_wt_table),
                                     0x12000,
                                     CSR_TYPE::REG_LST,
                                     5);
        add_csr(dnr_0, "dnr_wt_table", dnr_wt_table_prop);
        fld_map_t dnr_injpipe_dbg_probe0 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_injpipe_dbg_probe0_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dnr_injpipe_dbg_probe0),
                                               0x26000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(dnr_0, "dnr_injpipe_dbg_probe0", dnr_injpipe_dbg_probe0_prop);
        fld_map_t dnr_injpipe_dbg_probe1 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_injpipe_dbg_probe1_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dnr_injpipe_dbg_probe1),
                                               0x26200,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(dnr_0, "dnr_injpipe_dbg_probe1", dnr_injpipe_dbg_probe1_prop);
        fld_map_t dnr_ejpipe_dbg_probe0 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ejpipe_dbg_probe0_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dnr_ejpipe_dbg_probe0),
                                              0x26400,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(dnr_0, "dnr_ejpipe_dbg_probe0", dnr_ejpipe_dbg_probe0_prop);
        fld_map_t dnr_ejpipe_dbg_probe1 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ejpipe_dbg_probe1_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dnr_ejpipe_dbg_probe1),
                                              0x26600,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(dnr_0, "dnr_ejpipe_dbg_probe1", dnr_ejpipe_dbg_probe1_prop);
        fld_map_t dnr_ibuf_dbg_probe0 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ibuf_dbg_probe0_prop = csr_prop_t(
                                            std::make_shared<csr_s>(dnr_ibuf_dbg_probe0),
                                            0x26800,
                                            CSR_TYPE::REG_LST,
                                            5);
        add_csr(dnr_0, "dnr_ibuf_dbg_probe0", dnr_ibuf_dbg_probe0_prop);
        fld_map_t dnr_ibuf_dbg_probe1 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ibuf_dbg_probe1_prop = csr_prop_t(
                                            std::make_shared<csr_s>(dnr_ibuf_dbg_probe1),
                                            0x27200,
                                            CSR_TYPE::REG_LST,
                                            5);
        add_csr(dnr_0, "dnr_ibuf_dbg_probe1", dnr_ibuf_dbg_probe1_prop);
// END dnr
    }
    {
// BEGIN dnr
        auto dnr_1 = nu_rng[0].add_an({"fepw_hnu","dnr"}, 0x140C0000, 1, 0x0);
        fld_map_t dnr_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto dnr_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dnr_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(dnr_1, "dnr_timeout_thresh_cfg", dnr_timeout_thresh_cfg_prop);
        fld_map_t dnr_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto dnr_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(dnr_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(dnr_1, "dnr_timeout_clr", dnr_timeout_clr_prop);
        fld_map_t dnr_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto dnr_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(dnr_spare_pio),
                                      0x70,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(dnr_1, "dnr_spare_pio", dnr_spare_pio_prop);
        fld_map_t dnr_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto dnr_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dnr_scratchpad),
                                       0x78,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dnr_1, "dnr_scratchpad", dnr_scratchpad_prop);
        fld_map_t dnr_alt_ej_port {
            CREATE_ENTRY("val", 0, 3),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto dnr_alt_ej_port_prop = csr_prop_t(
                                        std::make_shared<csr_s>(dnr_alt_ej_port),
                                        0x80,
                                        CSR_TYPE::REG_LST,
                                        5);
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
        };
        auto dnr_cong_ctrl_prop = csr_prop_t(
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
        };
        auto dnr_route_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(dnr_route_cfg),
                                      0xB0,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(dnr_1, "dnr_route_cfg", dnr_route_cfg_prop);
        fld_map_t dnr_credit_cfg {
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc0", 0, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc1", 5, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc2", 10, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc3", 15, 5),
            CREATE_ENTRY("ibuf_max_shared_credits", 20, 5),
            CREATE_ENTRY("ebuf_min_rsvd_credits_vc_set0", 25, 7),
            CREATE_ENTRY("ebuf_min_rsvd_credits_vc_set1", 32, 7),
            CREATE_ENTRY("ebuf_max_shared_credits", 39, 7),
            CREATE_ENTRY("ibuf_shared_credits_hysteresis", 46, 5),
            CREATE_ENTRY("ebuf_shared_credits_hysteresis", 51, 7),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto dnr_credit_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(dnr_credit_cfg),
                                       0xB8,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(dnr_1, "dnr_credit_cfg", dnr_credit_cfg_prop);
        fld_map_t dnr_injection_credit_cfg {
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc0", 0, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc1", 5, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc2", 10, 5),
            CREATE_ENTRY("ibuf_min_rsvd_credits_vc3", 15, 5),
            CREATE_ENTRY("ibuf_max_shared_credits", 20, 5),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto dnr_injection_credit_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(dnr_injection_credit_cfg),
                0xC0,
                CSR_TYPE::REG,
                1);
        add_csr(dnr_1, "dnr_injection_credit_cfg", dnr_injection_credit_cfg_prop);
        fld_map_t dnr_vc_sel_wt_cfg {
            CREATE_ENTRY("vc0_wt", 0, 2),
            CREATE_ENTRY("vc1_wt", 2, 2),
            CREATE_ENTRY("vc2_wt", 4, 2),
            CREATE_ENTRY("vc3_wt", 6, 2),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto dnr_vc_sel_wt_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(dnr_vc_sel_wt_cfg),
                                          0xC8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(dnr_1, "dnr_vc_sel_wt_cfg", dnr_vc_sel_wt_cfg_prop);
        fld_map_t dnr_default_dgid_cfg {
            CREATE_ENTRY("val", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto dnr_default_dgid_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(dnr_default_dgid_cfg),
                                             0xD0,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(dnr_1, "dnr_default_dgid_cfg", dnr_default_dgid_cfg_prop);
        fld_map_t dnr_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto dnr_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(dnr_fla_ring_module_id_cfg),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(dnr_1, "dnr_fla_ring_module_id_cfg", dnr_fla_ring_module_id_cfg_prop);
        fld_map_t dnr_credit_watchdog_timer_cfg {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto dnr_credit_watchdog_timer_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(dnr_credit_watchdog_timer_cfg),
                    0xE0,
                    CSR_TYPE::REG,
                    1);
        add_csr(dnr_1, "dnr_credit_watchdog_timer_cfg", dnr_credit_watchdog_timer_cfg_prop);
        fld_map_t dnr_gid_to_coords_map {
            CREATE_ENTRY("coord_x", 0, 3),
            CREATE_ENTRY("coord_y", 3, 3),
            CREATE_ENTRY("use_alt_ej", 6, 1),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto dnr_gid_to_coords_map_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dnr_gid_to_coords_map),
                                              0x2000,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(dnr_1, "dnr_gid_to_coords_map", dnr_gid_to_coords_map_prop);
        fld_map_t dnr_wt_table {
            CREATE_ENTRY("wx", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto dnr_wt_table_prop = csr_prop_t(
                                     std::make_shared<csr_s>(dnr_wt_table),
                                     0x12000,
                                     CSR_TYPE::REG_LST,
                                     5);
        add_csr(dnr_1, "dnr_wt_table", dnr_wt_table_prop);
        fld_map_t dnr_injpipe_dbg_probe0 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_injpipe_dbg_probe0_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dnr_injpipe_dbg_probe0),
                                               0x26000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(dnr_1, "dnr_injpipe_dbg_probe0", dnr_injpipe_dbg_probe0_prop);
        fld_map_t dnr_injpipe_dbg_probe1 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_injpipe_dbg_probe1_prop = csr_prop_t(
                                               std::make_shared<csr_s>(dnr_injpipe_dbg_probe1),
                                               0x26200,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(dnr_1, "dnr_injpipe_dbg_probe1", dnr_injpipe_dbg_probe1_prop);
        fld_map_t dnr_ejpipe_dbg_probe0 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ejpipe_dbg_probe0_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dnr_ejpipe_dbg_probe0),
                                              0x26400,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(dnr_1, "dnr_ejpipe_dbg_probe0", dnr_ejpipe_dbg_probe0_prop);
        fld_map_t dnr_ejpipe_dbg_probe1 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ejpipe_dbg_probe1_prop = csr_prop_t(
                                              std::make_shared<csr_s>(dnr_ejpipe_dbg_probe1),
                                              0x26600,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(dnr_1, "dnr_ejpipe_dbg_probe1", dnr_ejpipe_dbg_probe1_prop);
        fld_map_t dnr_ibuf_dbg_probe0 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ibuf_dbg_probe0_prop = csr_prop_t(
                                            std::make_shared<csr_s>(dnr_ibuf_dbg_probe0),
                                            0x26800,
                                            CSR_TYPE::REG_LST,
                                            5);
        add_csr(dnr_1, "dnr_ibuf_dbg_probe0", dnr_ibuf_dbg_probe0_prop);
        fld_map_t dnr_ibuf_dbg_probe1 {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto dnr_ibuf_dbg_probe1_prop = csr_prop_t(
                                            std::make_shared<csr_s>(dnr_ibuf_dbg_probe1),
                                            0x27200,
                                            CSR_TYPE::REG_LST,
                                            5);
        add_csr(dnr_1, "dnr_ibuf_dbg_probe1", dnr_ibuf_dbg_probe1_prop);
// END dnr
    }
    {
// BEGIN fep_hnu
        auto fep_hnu_0 = nu_rng[0].add_an({"fepw_hnu","fep_hnu"}, 0x14080000, 1, 0x0);
        fld_map_t fep_hnu_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fep_hnu_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_hnu_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(fep_hnu_0, "fep_hnu_timeout_thresh_cfg", fep_hnu_timeout_thresh_cfg_prop);
        fld_map_t fep_hnu_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fep_hnu_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fep_hnu_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fep_hnu_0, "fep_hnu_timeout_clr", fep_hnu_timeout_clr_prop);
        fld_map_t fep_hnu_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fep_hnu_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fep_hnu_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fep_hnu_0, "fep_hnu_spare_pio", fep_hnu_spare_pio_prop);
        fld_map_t fep_hnu_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fep_hnu_scratchpad_prop = csr_prop_t(
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
        };
        auto fep_hnu_misc_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_mem_err_inj_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_mem_err_inj_cfg),
                                                0x88,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_mem_err_inj_cfg", fep_hnu_mem_err_inj_cfg_prop);
        fld_map_t fep_hnu_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_fla_ring_module_id_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_fla_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fep_hnu_fla_cfg),
                                        0x98,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fep_hnu_0, "fep_hnu_fla_cfg", fep_hnu_fla_cfg_prop);
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
        };
        auto fep_hnu_local_id_prop = csr_prop_t(
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
        };
        auto fep_hnu_strict_order_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fep_hnu_strict_order),
                                             0xB0,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fep_hnu_0, "fep_hnu_strict_order", fep_hnu_strict_order_prop);
        fld_map_t fep_hnu_erp_snx_cdt_init_val {
            CREATE_ENTRY("erp_vc0_cdt", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_erp_snx_cdt_init_val_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_erp_snx_cdt_init_val),
                    0xB8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_erp_snx_cdt_init_val", fep_hnu_erp_snx_cdt_init_val_prop);
        fld_map_t fep_hnu_nwqm_snx_cdt_init_val {
            CREATE_ENTRY("nwqm_vc0_cdt", 0, 8),
            CREATE_ENTRY("nwqm_vc1_cdt", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fep_hnu_nwqm_snx_cdt_init_val_prop = csr_prop_t(
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
        };
        auto fep_hnu_wro_snx_cdt_init_val_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_wro_snx_cdt_init_val),
                    0xC8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_wro_snx_cdt_init_val", fep_hnu_wro_snx_cdt_init_val_prop);
        fld_map_t fep_hnu_cmn_snx_cdt_init_val {
            CREATE_ENTRY("cmn_vc0_cdt", 0, 8),
            CREATE_ENTRY("cmn_vc1_cdt", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fep_hnu_cmn_snx_cdt_init_val_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_cmn_snx_cdt_init_val),
                    0xD0,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_cmn_snx_cdt_init_val", fep_hnu_cmn_snx_cdt_init_val_prop);
        fld_map_t fep_hnu_erp_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_hnu_erp_sn_filter_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fep_hnu_erp_sn_filter),
                                              0xD8,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fep_hnu_0, "fep_hnu_erp_sn_filter", fep_hnu_erp_sn_filter_prop);
        fld_map_t fep_hnu_nwqm_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_hnu_nwqm_sn_filter_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_hnu_nwqm_sn_filter),
                                               0xE0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_hnu_0, "fep_hnu_nwqm_sn_filter", fep_hnu_nwqm_sn_filter_prop);
        fld_map_t fep_hnu_hdma_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_hnu_hdma_sn_filter_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fep_hnu_hdma_sn_filter),
                                               0xE8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fep_hnu_0, "fep_hnu_hdma_sn_filter", fep_hnu_hdma_sn_filter_prop);
        fld_map_t fep_hnu_cmn_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_hnu_cmn_sn_filter_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fep_hnu_cmn_sn_filter),
                                              0xF0,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fep_hnu_0, "fep_hnu_cmn_sn_filter", fep_hnu_cmn_sn_filter_prop);
        fld_map_t fep_hnu_snx_sn_filter {
            CREATE_ENTRY("permitted_cmds", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto fep_hnu_snx_sn_filter_prop = csr_prop_t(
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
        };
        auto fep_hnu_nwqm_lsn_arb_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_cmn_lsn_arb_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_snx_lsn_arb_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_snx_lsn_arb_cfg),
                                                0x110,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_snx_lsn_arb_cfg", fep_hnu_snx_lsn_arb_cfg_prop);
        fld_map_t fep_hnu_dest_cfg_cmd {
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
        };
        auto fep_hnu_dest_cfg_cmd_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fep_hnu_dest_cfg_cmd),
                                             0x118,
                                             CSR_TYPE::REG,
                                             4);
        add_csr(fep_hnu_0, "fep_hnu_dest_cfg_cmd", fep_hnu_dest_cfg_cmd_prop);
        fld_map_t fep_hnu_hbm_ddr_hash {
            CREATE_ENTRY("ddr_buf_mode", 0, 2),
            CREATE_ENTRY("ddr_coh_mode", 2, 2),
            CREATE_ENTRY("hbm_buf_mode", 4, 2),
            CREATE_ENTRY("hbm_coh_mode", 6, 2),
            CREATE_ENTRY("num_shard_log2", 8, 2),
            CREATE_ENTRY("mask0", 10, 26),
            CREATE_ENTRY("mask1", 36, 26),
            CREATE_ENTRY("__rsvd", 62, 2)
        };
        auto fep_hnu_hbm_ddr_hash_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fep_hnu_hbm_ddr_hash),
                                             0x138,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(fep_hnu_0, "fep_hnu_hbm_ddr_hash", fep_hnu_hbm_ddr_hash_prop);
        fld_map_t fep_hnu_ddr_hash {
            CREATE_ENTRY("mask0", 0, 32),
            CREATE_ENTRY("mask1", 32, 32)
        };
        auto fep_hnu_ddr_hash_prop = csr_prop_t(
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
        };
        auto fep_hnu_addr_trans_hbm_pc_rsvd0_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_addr_trans_nu_mu_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_addr_trans_hu_nvram_ddr_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_addr_trans_rsvd1_cfg_prop = csr_prop_t(
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
        };
        auto fep_hnu_addr_trans_rsvd2_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_addr_trans_rsvd2_cfg),
                    0x168,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_addr_trans_rsvd2_cfg", fep_hnu_addr_trans_rsvd2_cfg_prop);
        fld_map_t fep_hnu_addr_trans_default_cfg {
            CREATE_ENTRY("gid", 0, 5),
            CREATE_ENTRY("lid", 5, 5),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto fep_hnu_addr_trans_default_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_addr_trans_default_cfg),
                    0x170,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_addr_trans_default_cfg", fep_hnu_addr_trans_default_cfg_prop);
        fld_map_t fep_hnu_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_sn_sent_cnt_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fep_hnu_sn_sent_cnt),
                                            0x178,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fep_hnu_0, "fep_hnu_sn_sent_cnt", fep_hnu_sn_sent_cnt_prop);
        fld_map_t fep_hnu_sn_rcvd_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_sn_rcvd_cnt_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fep_hnu_sn_rcvd_cnt),
                                            0x180,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fep_hnu_0, "fep_hnu_sn_rcvd_cnt", fep_hnu_sn_rcvd_cnt_prop);
        fld_map_t fep_hnu_lsn_addr_trans_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_lsn_addr_trans_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_lsn_addr_trans_err_cnt),
                    0x188,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_lsn_addr_trans_err_cnt", fep_hnu_lsn_addr_trans_err_cnt_prop);
        fld_map_t fep_hnu_lsn_unknown_dest_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_lsn_unknown_dest_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_lsn_unknown_dest_err_cnt),
                    0x190,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_lsn_unknown_dest_err_cnt", fep_hnu_lsn_unknown_dest_err_cnt_prop);
        fld_map_t fep_hnu_lsn_msg_filter_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_lsn_msg_filter_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_lsn_msg_filter_err_cnt),
                    0x198,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_lsn_msg_filter_err_cnt", fep_hnu_lsn_msg_filter_err_cnt_prop);
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
        };
        auto fep_hnu_sn_msg_sent_incr_en_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_hnu_sn_msg_sent_incr_en),
                0x1A0,
                CSR_TYPE::REG,
                1);
        add_csr(fep_hnu_0, "fep_hnu_sn_msg_sent_incr_en", fep_hnu_sn_msg_sent_incr_en_prop);
        fld_map_t fep_hnu_erp_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_erp_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_erp_sn_sent_cnt),
                                                0x1A8,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_erp_sn_sent_cnt", fep_hnu_erp_sn_sent_cnt_prop);
        fld_map_t fep_hnu_etp_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_etp_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_etp_sn_sent_cnt),
                                                0x1B0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_etp_sn_sent_cnt", fep_hnu_etp_sn_sent_cnt_prop);
        fld_map_t fep_hnu_nwqm_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_nwqm_sn_sent_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_hnu_nwqm_sn_sent_cnt),
                0x1B8,
                CSR_TYPE::REG,
                1);
        add_csr(fep_hnu_0, "fep_hnu_nwqm_sn_sent_cnt", fep_hnu_nwqm_sn_sent_cnt_prop);
        fld_map_t fep_hnu_wro_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_wro_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_wro_sn_sent_cnt),
                                                0x1C0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_wro_sn_sent_cnt", fep_hnu_wro_sn_sent_cnt_prop);
        fld_map_t fep_hnu_tgt_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_tgt_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_tgt_sn_sent_cnt),
                                                0x1C8,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_tgt_sn_sent_cnt", fep_hnu_tgt_sn_sent_cnt_prop);
        fld_map_t fep_hnu_hdma_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_hdma_sn_sent_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_hnu_hdma_sn_sent_cnt),
                0x1D0,
                CSR_TYPE::REG,
                1);
        add_csr(fep_hnu_0, "fep_hnu_hdma_sn_sent_cnt", fep_hnu_hdma_sn_sent_cnt_prop);
        fld_map_t fep_hnu_cmn_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_cmn_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_cmn_sn_sent_cnt),
                                                0x1D8,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_cmn_sn_sent_cnt", fep_hnu_cmn_sn_sent_cnt_prop);
        fld_map_t fep_hnu_snx_sn_sent_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_snx_sn_sent_cnt_prop = csr_prop_t(
                                                std::make_shared<csr_s>(fep_hnu_snx_sn_sent_cnt),
                                                0x1E0,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(fep_hnu_0, "fep_hnu_snx_sn_sent_cnt", fep_hnu_snx_sn_sent_cnt_prop);
        fld_map_t fep_hnu_dn_ej_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_dn_ej_cnt_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fep_hnu_dn_ej_cnt),
                                          0x1E8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(fep_hnu_0, "fep_hnu_dn_ej_cnt", fep_hnu_dn_ej_cnt_prop);
        fld_map_t fep_hnu_dn_inj_cnt {
            CREATE_ENTRY("val", 0, 36),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto fep_hnu_dn_inj_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fep_hnu_dn_inj_cnt),
                                           0x1F0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fep_hnu_0, "fep_hnu_dn_inj_cnt", fep_hnu_dn_inj_cnt_prop);
        fld_map_t fep_hnu_ldn_addr_trans_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_ldn_addr_trans_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_ldn_addr_trans_err_cnt),
                    0x1F8,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_ldn_addr_trans_err_cnt", fep_hnu_ldn_addr_trans_err_cnt_prop);
        fld_map_t fep_hnu_ldn_unknown_dest_err_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_ldn_unknown_dest_err_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_ldn_unknown_dest_err_cnt),
                    0x200,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_ldn_unknown_dest_err_cnt", fep_hnu_ldn_unknown_dest_err_cnt_prop);
        fld_map_t fep_hnu_dn_metadata_merr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_dn_metadata_merr_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_dn_metadata_merr_cnt),
                    0x208,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_dn_metadata_merr_cnt", fep_hnu_dn_metadata_merr_cnt_prop);
        fld_map_t fep_hnu_dn_metadata_serr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_dn_metadata_serr_cnt_prop = csr_prop_t(
                    std::make_shared<csr_s>(fep_hnu_dn_metadata_serr_cnt),
                    0x210,
                    CSR_TYPE::REG,
                    1);
        add_csr(fep_hnu_0, "fep_hnu_dn_metadata_serr_cnt", fep_hnu_dn_metadata_serr_cnt_prop);
        fld_map_t fep_hnu_dn_data_merr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_dn_data_merr_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_hnu_dn_data_merr_cnt),
                0x218,
                CSR_TYPE::REG,
                1);
        add_csr(fep_hnu_0, "fep_hnu_dn_data_merr_cnt", fep_hnu_dn_data_merr_cnt_prop);
        fld_map_t fep_hnu_dn_data_serr_cnt {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fep_hnu_dn_data_serr_cnt_prop = csr_prop_t(
                std::make_shared<csr_s>(fep_hnu_dn_data_serr_cnt),
                0x220,
                CSR_TYPE::REG,
                1);
        add_csr(fep_hnu_0, "fep_hnu_dn_data_serr_cnt", fep_hnu_dn_data_serr_cnt_prop);
// END fep_hnu
    }
    {
// BEGIN nu_fae
        auto nu_fae_0 = nu_rng[0].add_an({"nu_fae"}, 0x14400000, 1, 0x0);
        fld_map_t nu_fae_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nu_fae_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(nu_fae_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(nu_fae_0, "nu_fae_timeout_thresh_cfg", nu_fae_timeout_thresh_cfg_prop);
        fld_map_t nu_fae_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nu_fae_timeout_clr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fae_timeout_clr),
                                           0x10,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nu_fae_0, "nu_fae_timeout_clr", nu_fae_timeout_clr_prop);
        fld_map_t nu_fae_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_fae_spare_pio_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nu_fae_spare_pio),
                                         0x70,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nu_fae_0, "nu_fae_spare_pio", nu_fae_spare_pio_prop);
        fld_map_t nu_fae_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_fae_scratchpad_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_fae_scratchpad),
                                          0x78,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_fae_0, "nu_fae_scratchpad", nu_fae_scratchpad_prop);
        fld_map_t nu_fae_wct_macro_cfg {
            CREATE_ENTRY("decimal_rollover_en", 0, 1),
            CREATE_ENTRY("base_incr", 1, 26),
            CREATE_ENTRY("base_corr_incr", 27, 26),
            CREATE_ENTRY("override_incr", 53, 26),
            CREATE_ENTRY("base_period", 79, 16),
            CREATE_ENTRY("override_cnt", 95, 16),
            CREATE_ENTRY("override_mode", 111, 1),
            CREATE_ENTRY("sync_pulse_dly_sel", 112, 4),
            CREATE_ENTRY("__rsvd", 116, 12)
        };
        auto nu_fae_wct_macro_cfg_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nu_fae_wct_macro_cfg),
                                             0x80,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nu_fae_0, "nu_fae_wct_macro_cfg", nu_fae_wct_macro_cfg_prop);
        fld_map_t fae_wu_req_que_ncv_th {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fae_wu_req_que_ncv_th_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fae_wu_req_que_ncv_th),
                                              0x90,
                                              CSR_TYPE::REG,
                                              15);
        add_csr(nu_fae_0, "fae_wu_req_que_ncv_th", fae_wu_req_que_ncv_th_prop);
        fld_map_t fae_fwd_txcrd {
            CREATE_ENTRY("data", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fae_fwd_txcrd_prop = csr_prop_t(
                                      std::make_shared<csr_s>(fae_fwd_txcrd),
                                      0x108,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(nu_fae_0, "fae_fwd_txcrd", fae_fwd_txcrd_prop);
        fld_map_t fae_str_dsp_txcrd {
            CREATE_ENTRY("data", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fae_str_dsp_txcrd_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_str_dsp_txcrd),
                                          0x110,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_fae_0, "fae_str_dsp_txcrd", fae_str_dsp_txcrd_prop);
        fld_map_t fae_str_dma_txcrd {
            CREATE_ENTRY("data", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fae_str_dma_txcrd_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_str_dma_txcrd),
                                          0x118,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_fae_0, "fae_str_dma_txcrd", fae_str_dma_txcrd_prop);
        fld_map_t fae_dma_xoff_thold {
            CREATE_ENTRY("dma_occ_thold", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto fae_dma_xoff_thold_prop = csr_prop_t(
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
        };
        auto fae_sgid2port_map_prop = csr_prop_t(
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
        };
        auto fae_dsp_cont_wu_src_id_prop = csr_prop_t(
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
        };
        auto fae_dn_wr_req_src_id_prop = csr_prop_t(
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
        };
        auto fae_bm_rd_req_src_dst_id_prop = csr_prop_t(
                std::make_shared<csr_s>(fae_bm_rd_req_src_dst_id),
                0x140,
                CSR_TYPE::REG,
                1);
        add_csr(nu_fae_0, "fae_bm_rd_req_src_dst_id", fae_bm_rd_req_src_dst_id_prop);
        fld_map_t fae_mem_err_inj_cfg {
            CREATE_ENTRY("fae_req_fifo_mem", 0, 1),
            CREATE_ENTRY("fae_dma_rob_data_mem", 1, 1),
            CREATE_ENTRY("fae_dma_rob_md_mem", 2, 1),
            CREATE_ENTRY("fae_dma_frv_dfifo_mem", 3, 1),
            CREATE_ENTRY("err_type", 4, 1),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto fae_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fae_mem_err_inj_cfg),
                                            0x160,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(nu_fae_0, "fae_mem_err_inj_cfg", fae_mem_err_inj_cfg_prop);
        fld_map_t fae_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fae_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fae_fla_ring_module_id_cfg),
                0x168,
                CSR_TYPE::REG,
                1);
        add_csr(nu_fae_0, "fae_fla_ring_module_id_cfg", fae_fla_ring_module_id_cfg_prop);
        fld_map_t fae_fwd_prv_halt {
            CREATE_ENTRY("data", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fae_fwd_prv_halt_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fae_fwd_prv_halt),
                                         0x170,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nu_fae_0, "fae_fwd_prv_halt", fae_fwd_prv_halt_prop);
        fld_map_t fae_req_fifo_dhs {
            CREATE_ENTRY("data", 0, 256)
        };
        auto fae_req_fifo_dhs_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fae_req_fifo_dhs),
                                         0x2000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(nu_fae_0, "fae_req_fifo_dhs", fae_req_fifo_dhs_prop);
        fld_map_t fae_dma_rob_data_dhs {
            CREATE_ENTRY("data", 0, 512)
        };
        auto fae_dma_rob_data_dhs_prop = csr_prop_t(
                                             std::make_shared<csr_s>(fae_dma_rob_data_dhs),
                                             0x48000,
                                             CSR_TYPE::TBL,
                                             1);
        add_csr(nu_fae_0, "fae_dma_rob_data_dhs", fae_dma_rob_data_dhs_prop);
        fld_map_t fae_dma_rob_md_dhs {
            CREATE_ENTRY("data", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto fae_dma_rob_md_dhs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fae_dma_rob_md_dhs),
                                           0x248000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(nu_fae_0, "fae_dma_rob_md_dhs", fae_dma_rob_md_dhs_prop);
        fld_map_t fae_frv_dfifo_dhs {
            CREATE_ENTRY("data", 0, 128)
        };
        auto fae_frv_dfifo_dhs_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_frv_dfifo_dhs),
                                          0x24A000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nu_fae_0, "fae_frv_dfifo_dhs", fae_frv_dfifo_dhs_prop);
        fld_map_t fae_sn_txcrd_vc0 {
            CREATE_ENTRY("data", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fae_sn_txcrd_vc0_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fae_sn_txcrd_vc0),
                                         0x26A000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(nu_fae_0, "fae_sn_txcrd_vc0", fae_sn_txcrd_vc0_prop);
        fld_map_t fae_sn_txcrd_vc2 {
            CREATE_ENTRY("data", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fae_sn_txcrd_vc2_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fae_sn_txcrd_vc2),
                                         0x26A100,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(nu_fae_0, "fae_sn_txcrd_vc2", fae_sn_txcrd_vc2_prop);
        fld_map_t fae_dma_sn_tx_txcrd {
            CREATE_ENTRY("data", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fae_dma_sn_tx_txcrd_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fae_dma_sn_tx_txcrd),
                                            0x26A200,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(nu_fae_0, "fae_dma_sn_tx_txcrd", fae_dma_sn_tx_txcrd_prop);
        fld_map_t fae_str_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fae_str_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_str_dbg_probe),
                                          0x26A300,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nu_fae_0, "fae_str_dbg_probe", fae_str_dbg_probe_prop);
        fld_map_t fae_dma_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fae_dma_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_dma_dbg_probe),
                                          0x26A500,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nu_fae_0, "fae_dma_dbg_probe", fae_dma_dbg_probe_prop);
        fld_map_t fae_frv_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fae_frv_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_frv_dbg_probe),
                                          0x26A700,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nu_fae_0, "fae_frv_dbg_probe", fae_frv_dbg_probe_prop);
        fld_map_t fae_sn_tx_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fae_sn_tx_dbg_probe_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fae_sn_tx_dbg_probe),
                                            0x26A900,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(nu_fae_0, "fae_sn_tx_dbg_probe", fae_sn_tx_dbg_probe_prop);
        fld_map_t fae_dsp_dbg_probe {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto fae_dsp_dbg_probe_prop = csr_prop_t(
                                          std::make_shared<csr_s>(fae_dsp_dbg_probe),
                                          0x26AB00,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nu_fae_0, "fae_dsp_dbg_probe", fae_dsp_dbg_probe_prop);
// END nu_fae
    }
    {
// BEGIN nu_mpg_core
        auto nu_mpg_core_0 = nu_rng[0].add_an({"nu_mpg","nu_mpg_core"}, 0x15600000, 1, 0x0);
        fld_map_t nu_mpg_core_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nu_mpg_core_timeout_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nu_mpg_core_timeout_thresh_cfg),
                    0x0,
                    CSR_TYPE::REG,
                    1);
        add_csr(nu_mpg_core_0, "nu_mpg_core_timeout_thresh_cfg", nu_mpg_core_timeout_thresh_cfg_prop);
        fld_map_t nu_mpg_core_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nu_mpg_core_timeout_clr_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nu_mpg_core_timeout_clr),
                                                0x10,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(nu_mpg_core_0, "nu_mpg_core_timeout_clr", nu_mpg_core_timeout_clr_prop);
        fld_map_t nu_mpg_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_mpg_spare_pio_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nu_mpg_spare_pio),
                                         0x98,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nu_mpg_core_0, "nu_mpg_spare_pio", nu_mpg_spare_pio_prop);
        fld_map_t nu_mpg_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_mpg_scratchpad_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_mpg_scratchpad),
                                          0xA0,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_mpg_core_0, "nu_mpg_scratchpad", nu_mpg_scratchpad_prop);
        fld_map_t nu_mpg_rx_desc_upd_sw_raddr {
            CREATE_ENTRY("val", 0, 11),
            CREATE_ENTRY("__rsvd", 11, 53)
        };
        auto nu_mpg_rx_desc_upd_sw_raddr_prop = csr_prop_t(
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
        };
        auto nu_mpg_rx_desc_mem_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nu_mpg_rx_desc_mem_cfg),
                                               0xB8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nu_mpg_core_0, "nu_mpg_rx_desc_mem_cfg", nu_mpg_rx_desc_mem_cfg_prop);
        fld_map_t nu_mpg_rx_data_fifo_cfg {
            CREATE_ENTRY("bkpr_thr", 0, 11),
            CREATE_ENTRY("xoff_thr", 11, 11),
            CREATE_ENTRY("xon_thr", 22, 11),
            CREATE_ENTRY("xoff_en", 33, 1),
            CREATE_ENTRY("clear_hwm", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto nu_mpg_rx_data_fifo_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nu_mpg_rx_data_fifo_cfg),
                                                0xC8,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(nu_mpg_core_0, "nu_mpg_rx_data_fifo_cfg", nu_mpg_rx_data_fifo_cfg_prop);
        fld_map_t nu_mpg_rx_tgb_cfg {
            CREATE_ENTRY("max_tags", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto nu_mpg_rx_tgb_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_mpg_rx_tgb_cfg),
                                          0xD8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_mpg_core_0, "nu_mpg_rx_tgb_cfg", nu_mpg_rx_tgb_cfg_prop);
        fld_map_t nu_mpg_rx_fsm_cfg {
            CREATE_ENTRY("drop_err_pkt", 0, 1),
            CREATE_ENTRY("dn_gid", 1, 5),
            CREATE_ENTRY("dn_lid", 6, 5),
            CREATE_ENTRY("load_hbm_addr", 11, 1),
            CREATE_ENTRY("disable_fsm", 12, 1),
            CREATE_ENTRY("__rsvd", 13, 51)
        };
        auto nu_mpg_rx_fsm_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_mpg_rx_fsm_cfg),
                                          0xE8,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_mpg_core_0, "nu_mpg_rx_fsm_cfg", nu_mpg_rx_fsm_cfg_prop);
        fld_map_t nu_mpg_tx_desc_upd_sw_waddr {
            CREATE_ENTRY("val", 0, 11),
            CREATE_ENTRY("__rsvd", 11, 53)
        };
        auto nu_mpg_tx_desc_upd_sw_waddr_prop = csr_prop_t(
                std::make_shared<csr_s>(nu_mpg_tx_desc_upd_sw_waddr),
                0x100,
                CSR_TYPE::REG,
                1);
        add_csr(nu_mpg_core_0, "nu_mpg_tx_desc_upd_sw_waddr", nu_mpg_tx_desc_upd_sw_waddr_prop);
        fld_map_t nu_mpg_tx_data_fifo_cfg {
            CREATE_ENTRY("bkpr_thr", 0, 11),
            CREATE_ENTRY("__rsvd", 11, 53)
        };
        auto nu_mpg_tx_data_fifo_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nu_mpg_tx_data_fifo_cfg),
                                                0x108,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(nu_mpg_core_0, "nu_mpg_tx_data_fifo_cfg", nu_mpg_tx_data_fifo_cfg_prop);
        fld_map_t nu_mpg_tx_tgb_cfg {
            CREATE_ENTRY("max_tags", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto nu_mpg_tx_tgb_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_mpg_tx_tgb_cfg),
                                          0x118,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_mpg_core_0, "nu_mpg_tx_tgb_cfg", nu_mpg_tx_tgb_cfg_prop);
        fld_map_t nu_mpg_tx_fsm_cfg {
            CREATE_ENTRY("dn_gid", 0, 5),
            CREATE_ENTRY("dn_lid", 5, 5),
            CREATE_ENTRY("load_hbm_addr", 10, 1),
            CREATE_ENTRY("disable_fsm", 11, 1),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto nu_mpg_tx_fsm_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_mpg_tx_fsm_cfg),
                                          0x128,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_mpg_core_0, "nu_mpg_tx_fsm_cfg", nu_mpg_tx_fsm_cfg_prop);
        fld_map_t nu_mpg_hbm_rx_buf_start_addr_cfg {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nu_mpg_hbm_rx_buf_start_addr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nu_mpg_hbm_rx_buf_start_addr_cfg),
                    0x130,
                    CSR_TYPE::REG,
                    1);
        add_csr(nu_mpg_core_0, "nu_mpg_hbm_rx_buf_start_addr_cfg", nu_mpg_hbm_rx_buf_start_addr_cfg_prop);
        fld_map_t nu_mpg_hbm_rx_buf_end_addr_cfg {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nu_mpg_hbm_rx_buf_end_addr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nu_mpg_hbm_rx_buf_end_addr_cfg),
                    0x138,
                    CSR_TYPE::REG,
                    1);
        add_csr(nu_mpg_core_0, "nu_mpg_hbm_rx_buf_end_addr_cfg", nu_mpg_hbm_rx_buf_end_addr_cfg_prop);
        fld_map_t nu_mpg_hbm_tx_buf_start_addr_cfg {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nu_mpg_hbm_tx_buf_start_addr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nu_mpg_hbm_tx_buf_start_addr_cfg),
                    0x148,
                    CSR_TYPE::REG,
                    1);
        add_csr(nu_mpg_core_0, "nu_mpg_hbm_tx_buf_start_addr_cfg", nu_mpg_hbm_tx_buf_start_addr_cfg_prop);
        fld_map_t nu_mpg_hbm_tx_buf_end_addr_cfg {
            CREATE_ENTRY("val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto nu_mpg_hbm_tx_buf_end_addr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nu_mpg_hbm_tx_buf_end_addr_cfg),
                    0x150,
                    CSR_TYPE::REG,
                    1);
        add_csr(nu_mpg_core_0, "nu_mpg_hbm_tx_buf_end_addr_cfg", nu_mpg_hbm_tx_buf_end_addr_cfg_prop);
        fld_map_t nu_mpg_fla_slave_id {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nu_mpg_fla_slave_id_prop = csr_prop_t(
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
        };
        auto nu_mpg_sram_err_inj_cfg_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nu_mpg_sram_err_inj_cfg),
                                                0x178,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(nu_mpg_core_0, "nu_mpg_sram_err_inj_cfg", nu_mpg_sram_err_inj_cfg_prop);
        fld_map_t nu_mpg_tx_desc_mem {
            CREATE_ENTRY("val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto nu_mpg_tx_desc_mem_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_mpg_tx_desc_mem),
                                           0x128000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(nu_mpg_core_0, "nu_mpg_tx_desc_mem", nu_mpg_tx_desc_mem_prop);
        fld_map_t nu_mpg_stats_cntrs {
            CREATE_ENTRY("cnt", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto nu_mpg_stats_cntrs_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_mpg_stats_cntrs),
                                           0x148000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(nu_mpg_core_0, "nu_mpg_stats_cntrs", nu_mpg_stats_cntrs_prop);
// END nu_mpg_core
    }
    {
// BEGIN fla
        auto fla_0 = nu_rng[0].add_an({"fla"}, 0x15800000, 1, 0x0);
        fld_map_t fla_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fla_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_timeout_thresh_cfg", fla_timeout_thresh_cfg_prop);
        fld_map_t fla_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fla_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fla_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fla_0, "fla_timeout_clr", fla_timeout_clr_prop);
        fld_map_t fla_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fla_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(fla_spare_pio),
                                      0x98,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(fla_0, "fla_spare_pio", fla_spare_pio_prop);
        fld_map_t fla_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fla_scratchpad_prop = csr_prop_t(
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
        };
        auto fla_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_mem_init_start_cfg),
                                               0xA8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_mem_init_start_cfg", fla_mem_init_start_cfg_prop);
        fld_map_t fla_mem_err_inj_cfg {
            CREATE_ENTRY("fld_fla_engine0_cap_mem", 0, 1),
            CREATE_ENTRY("fld_fla_engine1_cap_mem", 1, 1),
            CREATE_ENTRY("fld_fla_engine2_cap_mem", 2, 1),
            CREATE_ENTRY("fld_fla_engine3_cap_mem", 3, 1),
            CREATE_ENTRY("fld_err_type", 4, 1),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto fla_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fla_mem_err_inj_cfg),
                                            0xD0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fla_0, "fla_mem_err_inj_cfg", fla_mem_err_inj_cfg_prop);
        fld_map_t fla_cmd_ring_if_dhs {
            CREATE_ENTRY("fld_busSelMap", 0, 4),
            CREATE_ENTRY("fld_module_id", 4, 8),
            CREATE_ENTRY("fld_mux_sel", 12, 8),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto fla_cmd_ring_if_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fla_cmd_ring_if_dhs),
                                            0xD8,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fla_0, "fla_cmd_ring_if_dhs", fla_cmd_ring_if_dhs_prop);
        fld_map_t fla_arm_trig_pls {
            CREATE_ENTRY("fld_engine0", 0, 1),
            CREATE_ENTRY("fld_engine1", 1, 1),
            CREATE_ENTRY("fld_engine2", 2, 1),
            CREATE_ENTRY("fld_engine3", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fla_arm_trig_pls_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fla_arm_trig_pls),
                                         0xE0,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(fla_0, "fla_arm_trig_pls", fla_arm_trig_pls_prop);
        fld_map_t fla_clr_trig_pls {
            CREATE_ENTRY("fld_engine0", 0, 1),
            CREATE_ENTRY("fld_engine1", 1, 1),
            CREATE_ENTRY("fld_engine2", 2, 1),
            CREATE_ENTRY("fld_engine3", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto fla_clr_trig_pls_prop = csr_prop_t(
                                         std::make_shared<csr_s>(fla_clr_trig_pls),
                                         0xF0,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(fla_0, "fla_clr_trig_pls", fla_clr_trig_pls_prop);
        fld_map_t fla_trig_map_cfg {
            CREATE_ENTRY("fld_engine0", 0, 4),
            CREATE_ENTRY("fld_engine1", 4, 4),
            CREATE_ENTRY("fld_engine2", 8, 4),
            CREATE_ENTRY("fld_engine3", 12, 4),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_trig_map_cfg_prop = csr_prop_t(
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
        };
        auto fla_trig_type_cfg_prop = csr_prop_t(
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
        };
        auto fla_engine_sample_mode_cfg_prop = csr_prop_t(
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
        };
        auto fla_engine_lane_deskew_cfg_prop = csr_prop_t(
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
        };
        auto fla_engine_trig_pos_cfg_prop = csr_prop_t(
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
        };
        auto fla_lut_a_sel_cfg_prop = csr_prop_t(
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
        };
        auto fla_lut_a_hit_map_cfg_prop = csr_prop_t(
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
        };
        auto fla_lut_b_sel_cfg_prop = csr_prop_t(
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
        };
        auto fla_lut_b_hit_map_cfg_prop = csr_prop_t(
                                              std::make_shared<csr_s>(fla_lut_b_hit_map_cfg),
                                              0x140,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(fla_0, "fla_lut_b_hit_map_cfg", fla_lut_b_hit_map_cfg_prop);
        fld_map_t fla_engine0_pattern_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine0_pattern_a_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine0_pattern_a_cfg),
                0x148,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine0_pattern_a_cfg", fla_engine0_pattern_a_cfg_prop);
        fld_map_t fla_engine0_mask_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine0_mask_a_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine0_mask_a_cfg),
                                               0x150,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine0_mask_a_cfg", fla_engine0_mask_a_cfg_prop);
        fld_map_t fla_engine0_pattern_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine0_pattern_b_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine0_pattern_b_cfg),
                0x158,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine0_pattern_b_cfg", fla_engine0_pattern_b_cfg_prop);
        fld_map_t fla_engine0_mask_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine0_mask_b_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine0_mask_b_cfg),
                                               0x160,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine0_mask_b_cfg", fla_engine0_mask_b_cfg_prop);
        fld_map_t fla_engine1_pattern_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine1_pattern_a_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine1_pattern_a_cfg),
                0x178,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine1_pattern_a_cfg", fla_engine1_pattern_a_cfg_prop);
        fld_map_t fla_engine1_mask_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine1_mask_a_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine1_mask_a_cfg),
                                               0x180,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine1_mask_a_cfg", fla_engine1_mask_a_cfg_prop);
        fld_map_t fla_engine1_pattern_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine1_pattern_b_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine1_pattern_b_cfg),
                0x188,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine1_pattern_b_cfg", fla_engine1_pattern_b_cfg_prop);
        fld_map_t fla_engine1_mask_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine1_mask_b_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine1_mask_b_cfg),
                                               0x190,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine1_mask_b_cfg", fla_engine1_mask_b_cfg_prop);
        fld_map_t fla_engine2_pattern_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine2_pattern_a_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine2_pattern_a_cfg),
                0x1A8,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine2_pattern_a_cfg", fla_engine2_pattern_a_cfg_prop);
        fld_map_t fla_engine2_mask_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine2_mask_a_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine2_mask_a_cfg),
                                               0x1B0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine2_mask_a_cfg", fla_engine2_mask_a_cfg_prop);
        fld_map_t fla_engine2_pattern_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine2_pattern_b_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine2_pattern_b_cfg),
                0x1B8,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine2_pattern_b_cfg", fla_engine2_pattern_b_cfg_prop);
        fld_map_t fla_engine2_mask_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine2_mask_b_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine2_mask_b_cfg),
                                               0x1C0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine2_mask_b_cfg", fla_engine2_mask_b_cfg_prop);
        fld_map_t fla_engine3_pattern_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine3_pattern_a_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine3_pattern_a_cfg),
                0x1D8,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine3_pattern_a_cfg", fla_engine3_pattern_a_cfg_prop);
        fld_map_t fla_engine3_mask_a_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine3_mask_a_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine3_mask_a_cfg),
                                               0x1E0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine3_mask_a_cfg", fla_engine3_mask_a_cfg_prop);
        fld_map_t fla_engine3_pattern_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine3_pattern_b_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fla_engine3_pattern_b_cfg),
                0x1E8,
                CSR_TYPE::REG,
                1);
        add_csr(fla_0, "fla_engine3_pattern_b_cfg", fla_engine3_pattern_b_cfg_prop);
        fld_map_t fla_engine3_mask_b_cfg {
            CREATE_ENTRY("fld_val", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto fla_engine3_mask_b_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fla_engine3_mask_b_cfg),
                                               0x1F0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fla_0, "fla_engine3_mask_b_cfg", fla_engine3_mask_b_cfg_prop);
// END fla
    }
    {
// BEGIN nu_nmg
        auto nu_nmg_0 = nu_rng[0].add_an({"nu_nmg"}, 0x15C00000, 1, 0x0);
        fld_map_t nu_nmg_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nu_nmg_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(nu_nmg_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(nu_nmg_0, "nu_nmg_timeout_thresh_cfg", nu_nmg_timeout_thresh_cfg_prop);
        fld_map_t nu_nmg_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nu_nmg_timeout_clr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_nmg_timeout_clr),
                                           0x10,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nu_nmg_0, "nu_nmg_timeout_clr", nu_nmg_timeout_clr_prop);
        fld_map_t nu_nmg_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_nmg_spare_pio_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nu_nmg_spare_pio),
                                         0x70,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nu_nmg_0, "nu_nmg_spare_pio", nu_nmg_spare_pio_prop);
        fld_map_t nu_nmg_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_nmg_scratchpad_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nu_nmg_scratchpad),
                                          0x78,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_nmg_0, "nu_nmg_scratchpad", nu_nmg_scratchpad_prop);
        fld_map_t nmg_blk_reset_cfg {
            CREATE_ENTRY("fld_fwd", 0, 1),
            CREATE_ENTRY("fld_fpg0", 1, 1),
            CREATE_ENTRY("fld_fpg0_phy", 2, 4),
            CREATE_ENTRY("fld_fpg1", 6, 1),
            CREATE_ENTRY("fld_fpg1_phy", 7, 4),
            CREATE_ENTRY("fld_fpg2", 11, 1),
            CREATE_ENTRY("fld_fpg2_phy", 12, 4),
            CREATE_ENTRY("fld_fpg3", 16, 1),
            CREATE_ENTRY("fld_fpg3_phy", 17, 4),
            CREATE_ENTRY("fld_fpg4", 21, 1),
            CREATE_ENTRY("fld_fpg4_phy", 22, 4),
            CREATE_ENTRY("fld_fpg5", 26, 1),
            CREATE_ENTRY("fld_fpg5_phy", 27, 4),
            CREATE_ENTRY("fld_mpg", 31, 1),
            CREATE_ENTRY("fld_mpg_phy", 32, 1),
            CREATE_ENTRY("fld_epg0", 33, 1),
            CREATE_ENTRY("fld_epg1", 34, 1),
            CREATE_ENTRY("fld_epg2", 35, 1),
            CREATE_ENTRY("fld_efp_tx", 36, 1),
            CREATE_ENTRY("fld_efp_rx", 37, 1),
            CREATE_ENTRY("fld_psw", 38, 1),
            CREATE_ENTRY("fld_wqm", 39, 1),
            CREATE_ENTRY("fld_fcb", 40, 1),
            CREATE_ENTRY("fld_wro", 41, 1),
            CREATE_ENTRY("fld_fae", 42, 1),
            CREATE_ENTRY("fld_hue0", 43, 1),
            CREATE_ENTRY("fld_hue1", 44, 1),
            CREATE_ENTRY("fld_sbus_master", 45, 1),
            CREATE_ENTRY("__rsvd", 46, 18)
        };
        auto nmg_blk_reset_cfg_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nmg_blk_reset_cfg),
                                          0x80,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(nu_nmg_0, "nmg_blk_reset_cfg", nmg_blk_reset_cfg_prop);
        fld_map_t nmg_clk_enable_cfg {
            CREATE_ENTRY("fld_ffe0", 0, 1),
            CREATE_ENTRY("fld_ffe1", 1, 1),
            CREATE_ENTRY("fld_ffe2", 2, 1),
            CREATE_ENTRY("fld_ffe3", 3, 1),
            CREATE_ENTRY("fld_ffe4", 4, 1),
            CREATE_ENTRY("fld_ffe5", 5, 1),
            CREATE_ENTRY("fld_nhp", 6, 1),
            CREATE_ENTRY("fld_sfg", 7, 1),
            CREATE_ENTRY("fld_fms", 8, 1),
            CREATE_ENTRY("fld_sse", 9, 1),
            CREATE_ENTRY("fld_fae_fae", 10, 1),
            CREATE_ENTRY("fld_fae_prs", 11, 1),
            CREATE_ENTRY("fld_fpg0_fpg_mpw", 12, 1),
            CREATE_ENTRY("fld_fpg0_fpg_sdif", 13, 1),
            CREATE_ENTRY("fld_fpg0_prw", 14, 1),
            CREATE_ENTRY("fld_fpg0_prs", 15, 1),
            CREATE_ENTRY("fld_fpg0_fpg_misc", 16, 1),
            CREATE_ENTRY("fld_fpg1_fpg_mpw", 17, 1),
            CREATE_ENTRY("fld_fpg1_fpg_sdif", 18, 1),
            CREATE_ENTRY("fld_fpg1_prw", 19, 1),
            CREATE_ENTRY("fld_fpg1_prs", 20, 1),
            CREATE_ENTRY("fld_fpg1_fpg_misc", 21, 1),
            CREATE_ENTRY("fld_fpg2_fpg_mpw", 22, 1),
            CREATE_ENTRY("fld_fpg2_fpg_sdif", 23, 1),
            CREATE_ENTRY("fld_fpg2_prw", 24, 1),
            CREATE_ENTRY("fld_fpg2_prs", 25, 1),
            CREATE_ENTRY("fld_fpg2_fpg_misc", 26, 1),
            CREATE_ENTRY("fld_fpg3_fpg_mpw", 27, 1),
            CREATE_ENTRY("fld_fpg3_fpg_sdif", 28, 1),
            CREATE_ENTRY("fld_fpg3_prw", 29, 1),
            CREATE_ENTRY("fld_fpg3_prs", 30, 1),
            CREATE_ENTRY("fld_fpg3_fpg_misc", 31, 1),
            CREATE_ENTRY("fld_fpg4_fpg_mpw", 32, 1),
            CREATE_ENTRY("fld_fpg4_fpg_sdif", 33, 1),
            CREATE_ENTRY("fld_fpg4_prw", 34, 1),
            CREATE_ENTRY("fld_fpg4_prs", 35, 1),
            CREATE_ENTRY("fld_fpg4_fpg_misc", 36, 1),
            CREATE_ENTRY("fld_fpg5_fpg_mpw", 37, 1),
            CREATE_ENTRY("fld_fpg5_fpg_sdif", 38, 1),
            CREATE_ENTRY("fld_fpg5_prw", 39, 1),
            CREATE_ENTRY("fld_fpg5_prs", 40, 1),
            CREATE_ENTRY("fld_fpg5_fpg_misc", 41, 1),
            CREATE_ENTRY("fld_mpg_fpg_mpw", 42, 1),
            CREATE_ENTRY("fld_mpg_fpg_sdif", 43, 1),
            CREATE_ENTRY("fld_mpg_fpg_misc", 44, 1),
            CREATE_ENTRY("fld_mpg_core", 45, 1),
            CREATE_ENTRY("fld_epg0_rdp_prw", 46, 1),
            CREATE_ENTRY("fld_epg0_rdp", 47, 1),
            CREATE_ENTRY("fld_epg0_tdp", 48, 1),
            CREATE_ENTRY("fld_epg0_fep", 49, 1),
            CREATE_ENTRY("fld_epg1_rdp_prw", 50, 1),
            CREATE_ENTRY("fld_epg1_rdp", 51, 1),
            CREATE_ENTRY("fld_epg1_tdp", 52, 1),
            CREATE_ENTRY("fld_epg1_fep", 53, 1),
            CREATE_ENTRY("fld_epg2_rdp_prw", 54, 1),
            CREATE_ENTRY("fld_epg2_rdp", 55, 1),
            CREATE_ENTRY("fld_epg2_tdp", 56, 1),
            CREATE_ENTRY("fld_epg2_fep", 57, 1),
            CREATE_ENTRY("fld_efp_tx_rfp", 58, 1),
            CREATE_ENTRY("fld_efp_tx_rfp_ffe", 59, 1),
            CREATE_ENTRY("fld_efp_tx_tfp", 60, 1),
            CREATE_ENTRY("fld_efp_tx_tfp_prs", 61, 1),
            CREATE_ENTRY("fld_efp_rx_rfp", 62, 1),
            CREATE_ENTRY("fld_efp_rx_rfp_prs", 63, 1),
            CREATE_ENTRY("fld_efp_rx_rfp_sfg", 64, 1),
            CREATE_ENTRY("fld_efp_rx_rfp_fms", 65, 1),
            CREATE_ENTRY("fld_psw", 66, 1),
            CREATE_ENTRY("fld_wqm", 67, 1),
            CREATE_ENTRY("fld_fcb", 68, 1),
            CREATE_ENTRY("fld_wro", 69, 1),
            CREATE_ENTRY("fld_fla", 70, 1),
            CREATE_ENTRY("fld_hue0_fnc0", 71, 1),
            CREATE_ENTRY("fld_hue0_fnc1", 72, 1),
            CREATE_ENTRY("fld_hue0_htd_tgt", 73, 1),
            CREATE_ENTRY("fld_hue0_htd_dma", 74, 1),
            CREATE_ENTRY("fld_hue1_fnc0", 75, 1),
            CREATE_ENTRY("fld_hue1_fnc1", 76, 1),
            CREATE_ENTRY("fld_hue1_htd_tgt", 77, 1),
            CREATE_ENTRY("fld_hue1_htd_dma", 78, 1),
            CREATE_ENTRY("__rsvd", 79, 49)
        };
        auto nmg_clk_enable_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nmg_clk_enable_cfg),
                                           0x88,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nu_nmg_0, "nmg_clk_enable_cfg", nmg_clk_enable_cfg_prop);
        fld_map_t nmg_blk_init_start_cfg {
            CREATE_ENTRY("fld_ffe0", 0, 1),
            CREATE_ENTRY("fld_ffe1", 1, 1),
            CREATE_ENTRY("fld_ffe2", 2, 1),
            CREATE_ENTRY("fld_ffe3", 3, 1),
            CREATE_ENTRY("fld_ffe4", 4, 1),
            CREATE_ENTRY("fld_ffe5", 5, 1),
            CREATE_ENTRY("fld_nhp", 6, 1),
            CREATE_ENTRY("fld_sfg", 7, 1),
            CREATE_ENTRY("fld_fms", 8, 1),
            CREATE_ENTRY("fld_sse", 9, 1),
            CREATE_ENTRY("fld_fae_fae", 10, 1),
            CREATE_ENTRY("fld_fae_prs", 11, 1),
            CREATE_ENTRY("fld_fpg0_fpg_mpw", 12, 1),
            CREATE_ENTRY("fld_fpg0_fpg_sdif", 13, 1),
            CREATE_ENTRY("fld_fpg0_prw", 14, 1),
            CREATE_ENTRY("fld_fpg0_prs", 15, 1),
            CREATE_ENTRY("fld_fpg0_fpg_misc", 16, 1),
            CREATE_ENTRY("fld_fpg1_fpg_mpw", 17, 1),
            CREATE_ENTRY("fld_fpg1_fpg_sdif", 18, 1),
            CREATE_ENTRY("fld_fpg1_prw", 19, 1),
            CREATE_ENTRY("fld_fpg1_prs", 20, 1),
            CREATE_ENTRY("fld_fpg1_fpg_misc", 21, 1),
            CREATE_ENTRY("fld_fpg2_fpg_mpw", 22, 1),
            CREATE_ENTRY("fld_fpg2_fpg_sdif", 23, 1),
            CREATE_ENTRY("fld_fpg2_prw", 24, 1),
            CREATE_ENTRY("fld_fpg2_prs", 25, 1),
            CREATE_ENTRY("fld_fpg2_fpg_misc", 26, 1),
            CREATE_ENTRY("fld_fpg3_fpg_mpw", 27, 1),
            CREATE_ENTRY("fld_fpg3_fpg_sdif", 28, 1),
            CREATE_ENTRY("fld_fpg3_prw", 29, 1),
            CREATE_ENTRY("fld_fpg3_prs", 30, 1),
            CREATE_ENTRY("fld_fpg3_fpg_misc", 31, 1),
            CREATE_ENTRY("fld_fpg4_fpg_mpw", 32, 1),
            CREATE_ENTRY("fld_fpg4_fpg_sdif", 33, 1),
            CREATE_ENTRY("fld_fpg4_prw", 34, 1),
            CREATE_ENTRY("fld_fpg4_prs", 35, 1),
            CREATE_ENTRY("fld_fpg4_fpg_misc", 36, 1),
            CREATE_ENTRY("fld_fpg5_fpg_mpw", 37, 1),
            CREATE_ENTRY("fld_fpg5_fpg_sdif", 38, 1),
            CREATE_ENTRY("fld_fpg5_prw", 39, 1),
            CREATE_ENTRY("fld_fpg5_prs", 40, 1),
            CREATE_ENTRY("fld_fpg5_fpg_misc", 41, 1),
            CREATE_ENTRY("fld_mpg_fpg_mpw", 42, 1),
            CREATE_ENTRY("fld_mpg_fpg_sdif", 43, 1),
            CREATE_ENTRY("fld_mpg_fpg_misc", 44, 1),
            CREATE_ENTRY("fld_mpg_core", 45, 1),
            CREATE_ENTRY("fld_epg0_rdp_prw", 46, 1),
            CREATE_ENTRY("fld_epg0_rdp", 47, 1),
            CREATE_ENTRY("fld_epg0_tdp", 48, 1),
            CREATE_ENTRY("fld_epg0_fep", 49, 1),
            CREATE_ENTRY("fld_epg1_rdp_prw", 50, 1),
            CREATE_ENTRY("fld_epg1_rdp", 51, 1),
            CREATE_ENTRY("fld_epg1_tdp", 52, 1),
            CREATE_ENTRY("fld_epg1_fep", 53, 1),
            CREATE_ENTRY("fld_epg2_rdp_prw", 54, 1),
            CREATE_ENTRY("fld_epg2_rdp", 55, 1),
            CREATE_ENTRY("fld_epg2_tdp", 56, 1),
            CREATE_ENTRY("fld_epg2_fep", 57, 1),
            CREATE_ENTRY("fld_efp_tx_rfp", 58, 1),
            CREATE_ENTRY("fld_efp_tx_rfp_ffe", 59, 1),
            CREATE_ENTRY("fld_efp_tx_tfp", 60, 1),
            CREATE_ENTRY("fld_efp_tx_tfp_prs", 61, 1),
            CREATE_ENTRY("fld_efp_rx_rfp", 62, 1),
            CREATE_ENTRY("fld_efp_rx_rfp_prs", 63, 1),
            CREATE_ENTRY("fld_efp_rx_rfp_sfg", 64, 1),
            CREATE_ENTRY("fld_efp_rx_rfp_fms", 65, 1),
            CREATE_ENTRY("fld_psw", 66, 1),
            CREATE_ENTRY("fld_wqm", 67, 1),
            CREATE_ENTRY("fld_fcb", 68, 1),
            CREATE_ENTRY("fld_wro", 69, 1),
            CREATE_ENTRY("fld_fla", 70, 1),
            CREATE_ENTRY("fld_hue0_fnc0", 71, 1),
            CREATE_ENTRY("fld_hue0_fnc1", 72, 1),
            CREATE_ENTRY("fld_hue0_htd_tgt", 73, 1),
            CREATE_ENTRY("fld_hue0_htd_dma", 74, 1),
            CREATE_ENTRY("fld_hue1_fnc0", 75, 1),
            CREATE_ENTRY("fld_hue1_fnc1", 76, 1),
            CREATE_ENTRY("fld_hue1_htd_tgt", 77, 1),
            CREATE_ENTRY("fld_hue1_htd_dma", 78, 1),
            CREATE_ENTRY("__rsvd", 79, 49)
        };
        auto nmg_blk_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nmg_blk_init_start_cfg),
                                               0x98,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nu_nmg_0, "nmg_blk_init_start_cfg", nmg_blk_init_start_cfg_prop);
        fld_map_t nmg_sbus_cfg {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nmg_sbus_cfg_prop = csr_prop_t(
                                     std::make_shared<csr_s>(nmg_sbus_cfg),
                                     0xB8,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(nu_nmg_0, "nmg_sbus_cfg", nmg_sbus_cfg_prop);
        fld_map_t nmg_tdm_sync_cfg {
            CREATE_ENTRY("start", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nmg_tdm_sync_cfg_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nmg_tdm_sync_cfg),
                                         0xC0,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nu_nmg_0, "nmg_tdm_sync_cfg", nmg_tdm_sync_cfg_prop);
// END nu_nmg
    }
    {
// BEGIN nu_fnc
        auto nu_fnc_0 = nu_rng[0].add_an({"nu_fnc"}, 0x15C00800, 1, 0x0);
        fld_map_t nu_fnc_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nu_fnc_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(nu_fnc_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(nu_fnc_0, "nu_fnc_timeout_thresh_cfg", nu_fnc_timeout_thresh_cfg_prop);
        fld_map_t nu_fnc_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nu_fnc_timeout_clr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_timeout_clr),
                                           0x10,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nu_fnc_0, "nu_fnc_timeout_clr", nu_fnc_timeout_clr_prop);
        fld_map_t nu_fnc_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_fnc_spare_pio_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nu_fnc_spare_pio),
                                         0x70,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(nu_fnc_0, "nu_fnc_spare_pio", nu_fnc_spare_pio_prop);
        fld_map_t nu_fnc_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nu_fnc_scratchpad_prop = csr_prop_t(
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
            CREATE_ENTRY("rsvd_1", 44, 3),
            CREATE_ENTRY("max_frame_size", 47, 1),
            CREATE_ENTRY("rfb_init_start", 48, 1),
            CREATE_ENTRY("__rsvd", 49, 15)
        };
        auto nu_fnc_cfg_prop = csr_prop_t(
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
        };
        auto nu_fnc_tdm_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(nu_fnc_tdm_cfg),
                                       0x88,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(nu_fnc_0, "nu_fnc_tdm_cfg", nu_fnc_tdm_cfg_prop);
        fld_map_t nu_fnc_replay_ctrl {
            CREATE_ENTRY("replay_timer", 0, 16),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto nu_fnc_replay_ctrl_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_replay_ctrl),
                                           0x98,
                                           CSR_TYPE::REG_LST,
                                           4);
        add_csr(nu_fnc_0, "nu_fnc_replay_ctrl", nu_fnc_replay_ctrl_prop);
        fld_map_t nu_fnc_tx_mbuf_ptr {
            CREATE_ENTRY("end_addr", 0, 9),
            CREATE_ENTRY("start_addr", 9, 9),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto nu_fnc_tx_mbuf_ptr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_tx_mbuf_ptr),
                                           0xB8,
                                           CSR_TYPE::REG_LST,
                                           16);
        add_csr(nu_fnc_0, "nu_fnc_tx_mbuf_ptr", nu_fnc_tx_mbuf_ptr_prop);
        fld_map_t nu_fnc_rx_mbuf_ptr {
            CREATE_ENTRY("end_addr", 0, 12),
            CREATE_ENTRY("start_addr", 12, 12),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nu_fnc_rx_mbuf_ptr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_rx_mbuf_ptr),
                                           0x138,
                                           CSR_TYPE::REG_LST,
                                           16);
        add_csr(nu_fnc_0, "nu_fnc_rx_mbuf_ptr", nu_fnc_rx_mbuf_ptr_prop);
        fld_map_t nu_fnc_rtry_dbuf_ptr {
            CREATE_ENTRY("end_addr", 0, 11),
            CREATE_ENTRY("start_addr", 11, 11),
            CREATE_ENTRY("__rsvd", 22, 42)
        };
        auto nu_fnc_rtry_dbuf_ptr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nu_fnc_rtry_dbuf_ptr),
                                             0x1B8,
                                             CSR_TYPE::REG_LST,
                                             4);
        add_csr(nu_fnc_0, "nu_fnc_rtry_dbuf_ptr", nu_fnc_rtry_dbuf_ptr_prop);
        fld_map_t nu_fnc_rtry_cbuf_ptr {
            CREATE_ENTRY("end_addr", 0, 9),
            CREATE_ENTRY("start_addr", 9, 9),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto nu_fnc_rtry_cbuf_ptr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nu_fnc_rtry_cbuf_ptr),
                                             0x1D8,
                                             CSR_TYPE::REG_LST,
                                             4);
        add_csr(nu_fnc_0, "nu_fnc_rtry_cbuf_ptr", nu_fnc_rtry_cbuf_ptr_prop);
        fld_map_t nu_fnc_rfb_buf_ptr {
            CREATE_ENTRY("end_addr", 0, 9),
            CREATE_ENTRY("start_addr", 9, 9),
            CREATE_ENTRY("__rsvd", 18, 46)
        };
        auto nu_fnc_rfb_buf_ptr_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_rfb_buf_ptr),
                                           0x1F8,
                                           CSR_TYPE::REG_LST,
                                           4);
        add_csr(nu_fnc_0, "nu_fnc_rfb_buf_ptr", nu_fnc_rfb_buf_ptr_prop);
        fld_map_t nu_fnc_tx_link_crd {
            CREATE_ENTRY("crd_cnt", 0, 12),
            CREATE_ENTRY("crd_seq", 12, 12),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nu_fnc_tx_link_crd_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_tx_link_crd),
                                           0x218,
                                           CSR_TYPE::REG_LST,
                                           16);
        add_csr(nu_fnc_0, "nu_fnc_tx_link_crd", nu_fnc_tx_link_crd_prop);
        fld_map_t nu_fnc_rx_link_crd {
            CREATE_ENTRY("crd_seq", 0, 12),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto nu_fnc_rx_link_crd_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nu_fnc_rx_link_crd),
                                           0x298,
                                           CSR_TYPE::REG_LST,
                                           16);
        add_csr(nu_fnc_0, "nu_fnc_rx_link_crd", nu_fnc_rx_link_crd_prop);
        fld_map_t nu_fnc_mq2vc_map {
            CREATE_ENTRY("stream", 0, 4),
            CREATE_ENTRY("vc", 4, 4),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nu_fnc_mq2vc_map_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nu_fnc_mq2vc_map),
                                         0x318,
                                         CSR_TYPE::REG_LST,
                                         16);
        add_csr(nu_fnc_0, "nu_fnc_mq2vc_map", nu_fnc_mq2vc_map_prop);
        fld_map_t nu_fnc_strm0_vc2mq_map {
            CREATE_ENTRY("vc", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto nu_fnc_strm0_vc2mq_map_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nu_fnc_strm0_vc2mq_map),
                                               0x398,
                                               CSR_TYPE::REG_LST,
                                               16);
        add_csr(nu_fnc_0, "nu_fnc_strm0_vc2mq_map", nu_fnc_strm0_vc2mq_map_prop);
        fld_map_t nu_fnc_strm1_vc2mq_map {
            CREATE_ENTRY("vc", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto nu_fnc_strm1_vc2mq_map_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nu_fnc_strm1_vc2mq_map),
                                               0x418,
                                               CSR_TYPE::REG_LST,
                                               16);
        add_csr(nu_fnc_0, "nu_fnc_strm1_vc2mq_map", nu_fnc_strm1_vc2mq_map_prop);
        fld_map_t nu_fnc_strm2_vc2mq_map {
            CREATE_ENTRY("vc", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto nu_fnc_strm2_vc2mq_map_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nu_fnc_strm2_vc2mq_map),
                                               0x498,
                                               CSR_TYPE::REG_LST,
                                               16);
        add_csr(nu_fnc_0, "nu_fnc_strm2_vc2mq_map", nu_fnc_strm2_vc2mq_map_prop);
        fld_map_t nu_fnc_strm3_vc2mq_map {
            CREATE_ENTRY("vc", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto nu_fnc_strm3_vc2mq_map_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nu_fnc_strm3_vc2mq_map),
                                               0x518,
                                               CSR_TYPE::REG_LST,
                                               16);
        add_csr(nu_fnc_0, "nu_fnc_strm3_vc2mq_map", nu_fnc_strm3_vc2mq_map_prop);
// END nu_fnc
    }
    {
// BEGIN hsu_flink_shim
        auto hsu_flink_shim_0 = nu_rng[0].add_an({"hsu_flink_shim"}, 0x17D00000, 1, 0x0);
        fld_map_t hsu_flink_shim_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto hsu_flink_shim_timeout_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_flink_shim_timeout_thresh_cfg),
                    0x0,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_timeout_thresh_cfg", hsu_flink_shim_timeout_thresh_cfg_prop);
        fld_map_t hsu_flink_shim_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hsu_flink_shim_timeout_clr_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_flink_shim_timeout_clr),
                0x10,
                CSR_TYPE::REG,
                1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_timeout_clr", hsu_flink_shim_timeout_clr_prop);
        fld_map_t hsu_flink_shim_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto hsu_flink_shim_spare_pio_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_flink_shim_spare_pio),
                0x70,
                CSR_TYPE::REG,
                1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_spare_pio", hsu_flink_shim_spare_pio_prop);
        fld_map_t hsu_flink_shim_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto hsu_flink_shim_scratchpad_prop = csr_prop_t(
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
        };
        auto hsu_flink_shim_csr_gen1_prop = csr_prop_t(
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
        };
        auto hsu_flink_shim_csr_gen2_prop = csr_prop_t(
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
        };
        auto hsu_flink_shim_csr_gen3_prop = csr_prop_t(
                                                std::make_shared<csr_s>(hsu_flink_shim_csr_gen3),
                                                0x90,
                                                CSR_TYPE::REG,
                                                1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_gen3", hsu_flink_shim_csr_gen3_prop);
        fld_map_t hsu_flink_shim_csr_gen4 {
            CREATE_ENTRY("bnh_match_val", 0, 15),
            CREATE_ENTRY("bnh_mask_val", 15, 15),
            CREATE_ENTRY("__rsvd", 30, 34)
        };
        auto hsu_flink_shim_csr_gen4_prop = csr_prop_t(
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
        };
        auto hsu_flink_shim_csr_pf_size_settings_mps_prop = csr_prop_t(
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
        };
        auto hsu_flink_shim_csr_pf_size_settings_mrs_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_flink_shim_csr_pf_size_settings_mrs),
                    0xA8,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_pf_size_settings_mrs", hsu_flink_shim_csr_pf_size_settings_mrs_prop);
        fld_map_t hsu_flink_shim_csr_fla_ring_module_id_cfg {
            CREATE_ENTRY("module_id", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto hsu_flink_shim_csr_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_flink_shim_csr_fla_ring_module_id_cfg),
                    0xB0,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_fla_ring_module_id_cfg", hsu_flink_shim_csr_fla_ring_module_id_cfg_prop);
        fld_map_t hsu_flink_shim_csr_mem_err_inj_cfg {
            CREATE_ENTRY("iram", 0, 1),
            CREATE_ENTRY("eram_ctrl", 1, 1),
            CREATE_ENTRY("eram_data", 2, 1),
            CREATE_ENTRY("err_type", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto hsu_flink_shim_csr_mem_err_inj_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_flink_shim_csr_mem_err_inj_cfg),
                    0xB8,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_mem_err_inj_cfg", hsu_flink_shim_csr_mem_err_inj_cfg_prop);
        fld_map_t hsu_flink_shim_csr_mem_init_cmd {
            CREATE_ENTRY("mem_init_cmd", 0, 3),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto hsu_flink_shim_csr_mem_init_cmd_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_flink_shim_csr_mem_init_cmd),
                    0xC0,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_flink_shim_0, "hsu_flink_shim_csr_mem_init_cmd", hsu_flink_shim_csr_mem_init_cmd_prop);
// END hsu_flink_shim
    }
    {
// BEGIN hsu_hdma_pcie_framer
        auto hsu_hdma_pcie_framer_0 = nu_rng[0].add_an({"hsu_hdma_pcie_framer"}, 0x18D00000, 1, 0x0);
        fld_map_t hsu_hdma_pcie_framer_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto hsu_hdma_pcie_framer_timeout_thresh_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_timeout_thresh_cfg),
                    0x0,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_timeout_thresh_cfg", hsu_hdma_pcie_framer_timeout_thresh_cfg_prop);
        fld_map_t hsu_hdma_pcie_framer_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hsu_hdma_pcie_framer_timeout_clr_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_timeout_clr),
                    0x10,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_timeout_clr", hsu_hdma_pcie_framer_timeout_clr_prop);
        fld_map_t hsu_hdma_pcie_framer_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto hsu_hdma_pcie_framer_spare_pio_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_spare_pio),
                    0x70,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_spare_pio", hsu_hdma_pcie_framer_spare_pio_prop);
        fld_map_t hsu_hdma_pcie_framer_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto hsu_hdma_pcie_framer_scratchpad_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_scratchpad),
                    0x78,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_scratchpad", hsu_hdma_pcie_framer_scratchpad_prop);
        fld_map_t hsu_hdma_pcie_framer_icsr_tag_cfg {
            CREATE_ENTRY("cfg", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hsu_hdma_pcie_framer_icsr_tag_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_icsr_tag_cfg),
                    0x80,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_icsr_tag_cfg", hsu_hdma_pcie_framer_icsr_tag_cfg_prop);
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
        };
        auto hsu_hdma_pcie_framer_mem_err_inj_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_mem_err_inj_cfg),
                    0x88,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_mem_err_inj_cfg", hsu_hdma_pcie_framer_mem_err_inj_cfg_prop);
        fld_map_t hsu_hdma_pcie_framer_icsr_wdata {
            CREATE_ENTRY("data", 0, 64)
        };
        auto hsu_hdma_pcie_framer_icsr_wdata_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_icsr_wdata),
                    0xC0,
                    CSR_TYPE::TBL,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_icsr_wdata", hsu_hdma_pcie_framer_icsr_wdata_prop);
        fld_map_t hsu_hdma_pcie_framer_icsr_addr {
            CREATE_ENTRY("data", 0, 64)
        };
        auto hsu_hdma_pcie_framer_icsr_addr_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_icsr_addr),
                    0x2C0,
                    CSR_TYPE::TBL,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_icsr_addr", hsu_hdma_pcie_framer_icsr_addr_prop);
        fld_map_t hsu_hdma_pcie_framer_icsr_cmd {
            CREATE_ENTRY("typ", 0, 3),
            CREATE_ENTRY("first_dw_be", 3, 4),
            CREATE_ENTRY("last_dw_be", 7, 4),
            CREATE_ENTRY("trigger", 11, 1),
            CREATE_ENTRY("done", 12, 1),
            CREATE_ENTRY("cpl_st", 13, 3),
            CREATE_ENTRY("ep", 16, 1),
            CREATE_ENTRY("rsvd", 17, 47)
        };
        auto hsu_hdma_pcie_framer_icsr_cmd_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_icsr_cmd),
                    0x3C0,
                    CSR_TYPE::TBL,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_icsr_cmd", hsu_hdma_pcie_framer_icsr_cmd_prop);
        fld_map_t hsu_hdma_pcie_framer_vf_partition_lut {
            CREATE_ENTRY("vf_base", 0, 8),
            CREATE_ENTRY("num_vf", 8, 9),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto hsu_hdma_pcie_framer_vf_partition_lut_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_vf_partition_lut),
                    0x500,
                    CSR_TYPE::TBL,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_vf_partition_lut", hsu_hdma_pcie_framer_vf_partition_lut_prop);
        fld_map_t hsu_hdma_pcie_framer_pf_vf_lookup {
            CREATE_ENTRY("pf_id", 0, 3),
            CREATE_ENTRY("vf_id", 3, 9),
            CREATE_ENTRY("__rsvd", 12, 52)
        };
        auto hsu_hdma_pcie_framer_pf_vf_lookup_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_pf_vf_lookup),
                    0x1000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_pf_vf_lookup", hsu_hdma_pcie_framer_pf_vf_lookup_prop);
        fld_map_t hsu_hdma_pcie_framer_str_ack_mode {
            CREATE_ENTRY("mode_bits", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto hsu_hdma_pcie_framer_str_ack_mode_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_hdma_pcie_framer_str_ack_mode),
                    0x9000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(hsu_hdma_pcie_framer_0, "hsu_hdma_pcie_framer_str_ack_mode", hsu_hdma_pcie_framer_str_ack_mode_prop);
// END hsu_hdma_pcie_framer
    }
    {
// BEGIN hsu_tgt
        auto hsu_tgt_0 = nu_rng[0].add_an({"hsu_tgt"}, 0x19000000, 1, 0x0);
        fld_map_t hsu_tgt_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto hsu_tgt_timeout_thresh_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_tgt_timeout_thresh_cfg),
                0x0,
                CSR_TYPE::REG,
                1);
        add_csr(hsu_tgt_0, "hsu_tgt_timeout_thresh_cfg", hsu_tgt_timeout_thresh_cfg_prop);
        fld_map_t hsu_tgt_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hsu_tgt_timeout_clr_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_timeout_clr),
                                            0x10,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(hsu_tgt_0, "hsu_tgt_timeout_clr", hsu_tgt_timeout_clr_prop);
        fld_map_t hsu_tgt_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto hsu_tgt_spare_pio_prop = csr_prop_t(
                                          std::make_shared<csr_s>(hsu_tgt_spare_pio),
                                          0x70,
                                          CSR_TYPE::REG,
                                          1);
        add_csr(hsu_tgt_0, "hsu_tgt_spare_pio", hsu_tgt_spare_pio_prop);
        fld_map_t hsu_tgt_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto hsu_tgt_scratchpad_prop = csr_prop_t(
                                           std::make_shared<csr_s>(hsu_tgt_scratchpad),
                                           0x78,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(hsu_tgt_0, "hsu_tgt_scratchpad", hsu_tgt_scratchpad_prop);
        fld_map_t hsu_tgt_csr_gen1 {
            CREATE_ENTRY("dis_csr_stall", 0, 1),
            CREATE_ENTRY("evt_en", 1, 1),
            CREATE_ENTRY("unused1", 2, 62)
        };
        auto hsu_tgt_csr_gen1_prop = csr_prop_t(
                                         std::make_shared<csr_s>(hsu_tgt_csr_gen1),
                                         0x80,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_gen1", hsu_tgt_csr_gen1_prop);
        fld_map_t hsu_tgt_csr_cred_init_snx {
            CREATE_ENTRY("cred_init_snx", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto hsu_tgt_csr_cred_init_snx_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_tgt_csr_cred_init_snx),
                0x88,
                CSR_TYPE::REG,
                1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_cred_init_snx", hsu_tgt_csr_cred_init_snx_prop);
        fld_map_t hsu_tgt_csr_err_log {
            CREATE_ENTRY("err_log", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto hsu_tgt_csr_err_log_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_err_log),
                                            0x90,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_err_log", hsu_tgt_csr_err_log_prop);
        fld_map_t hsu_tgt_csr_mem_init_cmd {
            CREATE_ENTRY("mem_init_cmd", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto hsu_tgt_csr_mem_init_cmd_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_tgt_csr_mem_init_cmd),
                0x98,
                CSR_TYPE::REG,
                1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_mem_init_cmd", hsu_tgt_csr_mem_init_cmd_prop);
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
        };
        auto hsu_tgt_csr_at_reg1_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg1),
                                            0x150,
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
        };
        auto hsu_tgt_csr_at_reg2_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg2),
                                            0x158,
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
        };
        auto hsu_tgt_csr_at_reg3_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg3),
                                            0x160,
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
        };
        auto hsu_tgt_csr_at_reg4_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg4),
                                            0x168,
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
        };
        auto hsu_tgt_csr_at_reg5_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg5),
                                            0x170,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg5", hsu_tgt_csr_at_reg5_prop);
        fld_map_t hsu_tgt_csr_at_reg6 {
            CREATE_ENTRY("hbm_hash_mask0", 0, 26),
            CREATE_ENTRY("hbm_hash_mask1", 26, 26),
            CREATE_ENTRY("__rsvd", 52, 12)
        };
        auto hsu_tgt_csr_at_reg6_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg6),
                                            0x178,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg6", hsu_tgt_csr_at_reg6_prop);
        fld_map_t hsu_tgt_csr_at_reg7 {
            CREATE_ENTRY("ddr_hash_mask0", 0, 32),
            CREATE_ENTRY("ddr_hash_mask1", 32, 32)
        };
        auto hsu_tgt_csr_at_reg7_prop = csr_prop_t(
                                            std::make_shared<csr_s>(hsu_tgt_csr_at_reg7),
                                            0x180,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_at_reg7", hsu_tgt_csr_at_reg7_prop);
        fld_map_t hsu_tgt_csr_fla_ring_module_id_cfg {
            CREATE_ENTRY("module_id", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto hsu_tgt_csr_fla_ring_module_id_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(hsu_tgt_csr_fla_ring_module_id_cfg),
                    0x188,
                    CSR_TYPE::REG,
                    1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_fla_ring_module_id_cfg", hsu_tgt_csr_fla_ring_module_id_cfg_prop);
        fld_map_t hsu_tgt_csr_mem_err_inj_cfg {
            CREATE_ENTRY("ptag", 0, 1),
            CREATE_ENTRY("llst", 1, 1),
            CREATE_ENTRY("ftag", 2, 1),
            CREATE_ENTRY("rbuf_lo", 3, 1),
            CREATE_ENTRY("rbuf_hi", 4, 1),
            CREATE_ENTRY("iramc", 5, 1),
            CREATE_ENTRY("iramd_lo", 6, 1),
            CREATE_ENTRY("iramd_hi", 7, 1),
            CREATE_ENTRY("err_type", 8, 1),
            CREATE_ENTRY("__rsvd", 9, 55)
        };
        auto hsu_tgt_csr_mem_err_inj_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_tgt_csr_mem_err_inj_cfg),
                0x190,
                CSR_TYPE::REG,
                1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_mem_err_inj_cfg", hsu_tgt_csr_mem_err_inj_cfg_prop);
        fld_map_t hsu_tgt_csr_mid_addr {
            CREATE_ENTRY("addr", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto hsu_tgt_csr_mid_addr_prop = csr_prop_t(
                                             std::make_shared<csr_s>(hsu_tgt_csr_mid_addr),
                                             0x1B0,
                                             CSR_TYPE::REG,
                                             14);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_mid_addr", hsu_tgt_csr_mid_addr_prop);
        fld_map_t hsu_tgt_csr_gen2 {
            CREATE_ENTRY("mid_drain_en", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto hsu_tgt_csr_gen2_prop = csr_prop_t(
                                         std::make_shared<csr_s>(hsu_tgt_csr_gen2),
                                         0x220,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_gen2", hsu_tgt_csr_gen2_prop);
        fld_map_t hsu_tgt_csr_mem_tgt_stats {
            CREATE_ENTRY("cnt", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto hsu_tgt_csr_mem_tgt_stats_prop = csr_prop_t(
                std::make_shared<csr_s>(hsu_tgt_csr_mem_tgt_stats),
                0x2C0000,
                CSR_TYPE::TBL,
                1);
        add_csr(hsu_tgt_0, "hsu_tgt_csr_mem_tgt_stats", hsu_tgt_csr_mem_tgt_stats_prop);
// END hsu_tgt
    }
    nu_rng.add_ring(1, 0x5800000000);
    {
// BEGIN sse
        auto sse_0 = nu_rng[1].add_an({"sse"}, 0x0, 1, 0x0);
        fld_map_t sse_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto sse_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sse_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(sse_0, "sse_timeout_thresh_cfg", sse_timeout_thresh_cfg_prop);
        fld_map_t sse_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sse_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(sse_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(sse_0, "sse_timeout_clr", sse_timeout_clr_prop);
        fld_map_t sse_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sse_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(sse_spare_pio),
                                      0x70,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(sse_0, "sse_spare_pio", sse_spare_pio_prop);
        fld_map_t sse_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sse_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sse_scratchpad),
                                       0x78,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(sse_0, "sse_scratchpad", sse_scratchpad_prop);
        fld_map_t sse_rng_cfg {
            CREATE_ENTRY("mode", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sse_rng_cfg_prop = csr_prop_t(
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
        };
        auto sse_fpg_inp_dly_prop = csr_prop_t(
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
        };
        auto sse_get_prv_en_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sse_get_prv_en),
                                       0x90,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(sse_0, "sse_get_prv_en", sse_get_prv_en_prop);
        fld_map_t sse_wrr_wt {
            CREATE_ENTRY("efp_wt", 0, 4),
            CREATE_ENTRY("fae_wt", 4, 4),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto sse_wrr_wt_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sse_wrr_wt),
                                   0x98,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(sse_0, "sse_wrr_wt", sse_wrr_wt_prop);
        fld_map_t sse_min_dist {
            CREATE_ENTRY("efp", 0, 5),
            CREATE_ENTRY("fae", 5, 5),
            CREATE_ENTRY("__rsvd", 10, 54)
        };
        auto sse_min_dist_prop = csr_prop_t(
                                     std::make_shared<csr_s>(sse_min_dist),
                                     0xA0,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(sse_0, "sse_min_dist", sse_min_dist_prop);
        fld_map_t sse_mem_err_inj_cfg {
            CREATE_ENTRY("sse_mdi_mem", 0, 1),
            CREATE_ENTRY("err_type", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto sse_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(sse_mem_err_inj_cfg),
                                            0xC0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(sse_0, "sse_mem_err_inj_cfg", sse_mem_err_inj_cfg_prop);
        fld_map_t sse_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto sse_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sse_fla_ring_module_id_cfg),
                0xC8,
                CSR_TYPE::REG,
                1);
        add_csr(sse_0, "sse_fla_ring_module_id_cfg", sse_fla_ring_module_id_cfg_prop);
        fld_map_t sse_snpsht_cfg {
            CREATE_ENTRY("enable", 0, 1),
            CREATE_ENTRY("prv_fld_extr", 1, 56),
            CREATE_ENTRY("__rsvd", 57, 7)
        };
        auto sse_snpsht_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sse_snpsht_cfg),
                                       0xD0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(sse_0, "sse_snpsht_cfg", sse_snpsht_cfg_prop);
        fld_map_t sse_snpsht_mask {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sse_snpsht_mask_prop = csr_prop_t(
                                        std::make_shared<csr_s>(sse_snpsht_mask),
                                        0xD8,
                                        CSR_TYPE::REG,
                                        5);
        add_csr(sse_0, "sse_snpsht_mask", sse_snpsht_mask_prop);
        fld_map_t sse_snpsht_val {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sse_snpsht_val_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sse_snpsht_val),
                                       0x100,
                                       CSR_TYPE::REG,
                                       5);
        add_csr(sse_0, "sse_snpsht_val", sse_snpsht_val_prop);
        fld_map_t sse_rng_cam {
            CREATE_ENTRY("operation", 0, 2),
            CREATE_ENTRY("port_type", 2, 2),
            CREATE_ENTRY("val_low", 4, 16),
            CREATE_ENTRY("val_hi", 20, 16),
            CREATE_ENTRY("__rsvd", 36, 28)
        };
        auto sse_rng_cam_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sse_rng_cam),
                                    0x200,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(sse_0, "sse_rng_cam", sse_rng_cam_prop);
        fld_map_t sse_mdi_mem_dhs {
            CREATE_ENTRY("data", 0, 400),
            CREATE_ENTRY("__rsvd", 400, 48)
        };
        auto sse_mdi_mem_dhs_prop = csr_prop_t(
                                        std::make_shared<csr_s>(sse_mdi_mem_dhs),
                                        0x2000,
                                        CSR_TYPE::TBL,
                                        1);
        add_csr(sse_0, "sse_mdi_mem_dhs", sse_mdi_mem_dhs_prop);
        fld_map_t sse_dbg_probe0_cnt {
            CREATE_ENTRY("fld_val", 0, 64)
        };
        auto sse_dbg_probe0_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(sse_dbg_probe0_cnt),
                                           0x3A000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(sse_0, "sse_dbg_probe0_cnt", sse_dbg_probe0_cnt_prop);
        fld_map_t sse_dbg_probe1_cnt {
            CREATE_ENTRY("fld_val", 0, 64)
        };
        auto sse_dbg_probe1_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(sse_dbg_probe1_cnt),
                                           0x3A200,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(sse_0, "sse_dbg_probe1_cnt", sse_dbg_probe1_cnt_prop);
// END sse
    }
    {
// BEGIN stg0_ffe
        auto stg0_ffe_0 = nu_rng[1].add_an({"stg0_ffe"}, 0x4000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg0_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg0_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg0_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg0_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg0_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg0_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg0_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg0_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg0_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg0_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg0_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 199),
            CREATE_ENTRY("__rsvd", 199, 57)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg0_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg0_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg0_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 88),
            CREATE_ENTRY("result", 88, 20),
            CREATE_ENTRY("__rsvd", 108, 20)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg0_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg0_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 88),
            CREATE_ENTRY("result", 88, 20),
            CREATE_ENTRY("__rsvd", 108, 20)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg0_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg0_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg0_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg0_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg0_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg0_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg0_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg0_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg0_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg0_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg0_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg0_ffe_0, "act_dmem", act_dmem_prop);
// END stg0_ffe
    }
    {
// BEGIN stg1_ffe
        auto stg1_ffe_0 = nu_rng[1].add_an({"stg1_ffe"}, 0x8000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg1_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg1_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg1_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg1_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg1_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg1_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg1_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg1_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg1_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg1_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg1_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 199),
            CREATE_ENTRY("__rsvd", 199, 57)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg1_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg1_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg1_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 88),
            CREATE_ENTRY("result", 88, 20),
            CREATE_ENTRY("__rsvd", 108, 20)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg1_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg1_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 88),
            CREATE_ENTRY("result", 88, 20),
            CREATE_ENTRY("__rsvd", 108, 20)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg1_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg1_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg1_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg1_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg1_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg1_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg1_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg1_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg1_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg1_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg1_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg1_ffe_0, "act_dmem", act_dmem_prop);
// END stg1_ffe
    }
    {
// BEGIN stg2_ffe
        auto stg2_ffe_0 = nu_rng[1].add_an({"stg2_ffe"}, 0xC000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg2_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg2_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg2_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg2_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg2_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg2_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg2_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg2_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg2_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg2_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg2_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 423),
            CREATE_ENTRY("__rsvd", 423, 25)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg2_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg2_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg2_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg2_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg2_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg2_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg2_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg2_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg2_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg2_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg2_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg2_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg2_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg2_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg2_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg2_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg2_ffe_0, "act_dmem", act_dmem_prop);
// END stg2_ffe
    }
    {
// BEGIN stg3_ffe
        auto stg3_ffe_0 = nu_rng[1].add_an({"stg3_ffe"}, 0x10000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg3_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg3_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg3_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg3_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg3_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg3_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg3_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg3_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg3_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg3_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg3_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 199),
            CREATE_ENTRY("__rsvd", 199, 57)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg3_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg3_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg3_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 88),
            CREATE_ENTRY("result", 88, 20),
            CREATE_ENTRY("__rsvd", 108, 20)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg3_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg3_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 88),
            CREATE_ENTRY("result", 88, 20),
            CREATE_ENTRY("__rsvd", 108, 20)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg3_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg3_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg3_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg3_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg3_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg3_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg3_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 88),
            CREATE_ENTRY("__rsvd", 88, 40)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg3_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg3_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg3_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg3_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg3_ffe_0, "act_dmem", act_dmem_prop);
// END stg3_ffe
    }
    {
// BEGIN stg4_ffe
        auto stg4_ffe_0 = nu_rng[1].add_an({"stg4_ffe"}, 0x14000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg4_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg4_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg4_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg4_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg4_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg4_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg4_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg4_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg4_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg4_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg4_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 423),
            CREATE_ENTRY("__rsvd", 423, 25)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg4_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg4_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg4_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg4_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg4_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg4_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg4_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg4_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg4_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg4_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg4_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg4_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg4_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg4_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg4_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg4_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg4_ffe_0, "act_dmem", act_dmem_prop);
// END stg4_ffe
    }
    {
// BEGIN stg5_ffe
        auto stg5_ffe_0 = nu_rng[1].add_an({"stg5_ffe"}, 0x18000000, 1, 0x0);
        fld_map_t ffe_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto ffe_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(ffe_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(stg5_ffe_0, "ffe_timeout_thresh_cfg", ffe_timeout_thresh_cfg_prop);
        fld_map_t ffe_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto ffe_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(ffe_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(stg5_ffe_0, "ffe_timeout_clr", ffe_timeout_clr_prop);
        fld_map_t ffe_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(ffe_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg5_ffe_0, "ffe_spare_pio", ffe_spare_pio_prop);
        fld_map_t ffe_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto ffe_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(ffe_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(stg5_ffe_0, "ffe_scratchpad", ffe_scratchpad_prop);
        fld_map_t static_cfg {
            CREATE_ENTRY("stage_bypass", 0, 2),
            CREATE_ENTRY("lg_tbl_bnk_asgn", 2, 2),
            CREATE_ENTRY("lg_tcam_bnk_asgn", 4, 2),
            CREATE_ENTRY("sm_tcam_bnk_asgn", 6, 2),
            CREATE_ENTRY("bypass_id", 8, 3),
            CREATE_ENTRY("l1_hash_as_dit", 11, 1),
            CREATE_ENTRY("l2_hash_as_dit", 12, 1),
            CREATE_ENTRY("log_tbl_32_en", 13, 1),
            CREATE_ENTRY("smac_logical_tbl_id", 14, 4),
            CREATE_ENTRY("logical_port_oset", 18, 7),
            CREATE_ENTRY("__rsvd", 25, 39)
        };
        auto static_cfg_prop = csr_prop_t(
                                   std::make_shared<csr_s>(static_cfg),
                                   0x58,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(stg5_ffe_0, "static_cfg", static_cfg_prop);
        fld_map_t ffe_sram_err_inj {
            CREATE_ENTRY("val", 0, 34),
            CREATE_ENTRY("__rsvd", 34, 30)
        };
        auto ffe_sram_err_inj_prop = csr_prop_t(
                                         std::make_shared<csr_s>(ffe_sram_err_inj),
                                         0x60,
                                         CSR_TYPE::REG,
                                         1);
        add_csr(stg5_ffe_0, "ffe_sram_err_inj", ffe_sram_err_inj_prop);
        fld_map_t tcam_ctl {
            CREATE_ENTRY("lt_par_chk_en", 0, 1),
            CREATE_ENTRY("st_par_chk_en", 1, 1),
            CREATE_ENTRY("lt_vbe_ctl", 2, 32),
            CREATE_ENTRY("st_vbe_ctl", 34, 1),
            CREATE_ENTRY("__rsvd", 35, 29)
        };
        auto tcam_ctl_prop = csr_prop_t(
                                 std::make_shared<csr_s>(tcam_ctl),
                                 0x78,
                                 CSR_TYPE::REG,
                                 1);
        add_csr(stg5_ffe_0, "tcam_ctl", tcam_ctl_prop);
        fld_map_t hash_seed_cfg {
            CREATE_ENTRY("seed_h1", 0, 8),
            CREATE_ENTRY("seed_h2", 8, 8),
            CREATE_ENTRY("__rsvd", 16, 48)
        };
        auto hash_seed_cfg_prop = csr_prop_t(
                                      std::make_shared<csr_s>(hash_seed_cfg),
                                      0x80,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(stg5_ffe_0, "hash_seed_cfg", hash_seed_cfg_prop);
        fld_map_t ffe_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto ffe_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(ffe_fla_ring_module_id_cfg),
                0x90,
                CSR_TYPE::REG,
                1);
        add_csr(stg5_ffe_0, "ffe_fla_ring_module_id_cfg", ffe_fla_ring_module_id_cfg_prop);
        fld_map_t tmp_tcam_m_key {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_m_key_prop = csr_prop_t(
                                       std::make_shared<csr_s>(tmp_tcam_m_key),
                                       0x4400,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(stg5_ffe_0, "tmp_tcam_m_key", tmp_tcam_m_key_prop);
        fld_map_t tmp_tcam_mask {
            CREATE_ENTRY("value", 0, 26),
            CREATE_ENTRY("__rsvd", 26, 38)
        };
        auto tmp_tcam_mask_prop = csr_prop_t(
                                      std::make_shared<csr_s>(tmp_tcam_mask),
                                      0x5400,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg5_ffe_0, "tmp_tcam_mask", tmp_tcam_mask_prop);
        fld_map_t key_ucode_mem {
            CREATE_ENTRY("entry", 0, 423),
            CREATE_ENTRY("__rsvd", 423, 25)
        };
        auto key_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(key_ucode_mem),
                                      0x18000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg5_ffe_0, "key_ucode_mem", key_ucode_mem_prop);
        fld_map_t lt_attributes_mem {
            CREATE_ENTRY("entry", 0, 39),
            CREATE_ENTRY("__rsvd", 39, 25)
        };
        auto lt_attributes_mem_prop = csr_prop_t(
                                          std::make_shared<csr_s>(lt_attributes_mem),
                                          0x58000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(stg5_ffe_0, "lt_attributes_mem", lt_attributes_mem_prop);
        fld_map_t hash_mem_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto hash_mem_vld_prop = csr_prop_t(
                                     std::make_shared<csr_s>(hash_mem_vld),
                                     0x5A000,
                                     CSR_TYPE::TBL,
                                     8);
        add_csr(stg5_ffe_0, "hash_mem_vld", hash_mem_vld_prop);
        fld_map_t hash_mem {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto hash_mem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(hash_mem),
                                 0xE0000,
                                 CSR_TYPE::TBL,
                                 8);
        add_csr(stg5_ffe_0, "hash_mem", hash_mem_prop);
        fld_map_t stash_table_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto stash_table_vld_prop = csr_prop_t(
                                        std::make_shared<csr_s>(stash_table_vld),
                                        0x8E0000,
                                        CSR_TYPE::TBL,
                                        4);
        add_csr(stg5_ffe_0, "stash_table_vld", stash_table_vld_prop);
        fld_map_t stash_table {
            CREATE_ENTRY("key", 0, 200),
            CREATE_ENTRY("result", 200, 20),
            CREATE_ENTRY("__rsvd", 220, 36)
        };
        auto stash_table_prop = csr_prop_t(
                                    std::make_shared<csr_s>(stash_table),
                                    0x920000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg5_ffe_0, "stash_table", stash_table_prop);
        fld_map_t lg_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto lg_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(lg_tcam_vld),
                                    0x928000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg5_ffe_0, "lg_tcam_vld", lg_tcam_vld_prop);
        fld_map_t lg_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_x),
                                  0xA40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg5_ffe_0, "lg_tcam_x", lg_tcam_x_prop);
        fld_map_t lg_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto lg_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(lg_tcam_y),
                                  0x1A40000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg5_ffe_0, "lg_tcam_y", lg_tcam_y_prop);
        fld_map_t lg_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto lg_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(lg_tcam_at_index),
                                         0x2A40000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg5_ffe_0, "lg_tcam_at_index", lg_tcam_at_index_prop);
        fld_map_t sm_tcam_vld {
            CREATE_ENTRY("value", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sm_tcam_vld_prop = csr_prop_t(
                                    std::make_shared<csr_s>(sm_tcam_vld),
                                    0x2B40000,
                                    CSR_TYPE::TBL,
                                    4);
        add_csr(stg5_ffe_0, "sm_tcam_vld", sm_tcam_vld_prop);
        fld_map_t sm_tcam_x {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_x_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_x),
                                  0x2B48000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg5_ffe_0, "sm_tcam_x", sm_tcam_x_prop);
        fld_map_t sm_tcam_y {
            CREATE_ENTRY("data", 0, 200),
            CREATE_ENTRY("__rsvd", 200, 56)
        };
        auto sm_tcam_y_prop = csr_prop_t(
                                  std::make_shared<csr_s>(sm_tcam_y),
                                  0x2BC8000,
                                  CSR_TYPE::TBL,
                                  4);
        add_csr(stg5_ffe_0, "sm_tcam_y", sm_tcam_y_prop);
        fld_map_t sm_tcam_at_index {
            CREATE_ENTRY("result", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_tcam_at_index_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sm_tcam_at_index),
                                         0x2C48000,
                                         CSR_TYPE::TBL,
                                         4);
        add_csr(stg5_ffe_0, "sm_tcam_at_index", sm_tcam_at_index_prop);
        fld_map_t sm_dit_mem {
            CREATE_ENTRY("ap_addr", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sm_dit_mem_prop = csr_prop_t(
                                   std::make_shared<csr_s>(sm_dit_mem),
                                   0x2C50000,
                                   CSR_TYPE::TBL,
                                   2);
        add_csr(stg5_ffe_0, "sm_dit_mem", sm_dit_mem_prop);
        fld_map_t act_ucode_mem {
            CREATE_ENTRY("entry_0", 0, 29),
            CREATE_ENTRY("entry_1", 29, 29),
            CREATE_ENTRY("entry_2", 58, 29),
            CREATE_ENTRY("entry_3", 87, 29),
            CREATE_ENTRY("entry_4", 116, 29),
            CREATE_ENTRY("entry_5", 145, 29),
            CREATE_ENTRY("flag_entry_0", 174, 7),
            CREATE_ENTRY("flag_entry_1", 181, 7),
            CREATE_ENTRY("flag_entry_2", 188, 7),
            CREATE_ENTRY("flag_entry_3", 195, 7),
            CREATE_ENTRY("__rsvd", 202, 54)
        };
        auto act_ucode_mem_prop = csr_prop_t(
                                      std::make_shared<csr_s>(act_ucode_mem),
                                      0x2C70000,
                                      CSR_TYPE::TBL,
                                      1);
        add_csr(stg5_ffe_0, "act_ucode_mem", act_ucode_mem_prop);
        fld_map_t act_dmem {
            CREATE_ENTRY("data", 0, 64)
        };
        auto act_dmem_prop = csr_prop_t(
                                 std::make_shared<csr_s>(act_dmem),
                                 0x2C80000,
                                 CSR_TYPE::TBL,
                                 6);
        add_csr(stg5_ffe_0, "act_dmem", act_dmem_prop);
// END stg5_ffe
    }
    {
// BEGIN nhp
        auto nhp_0 = nu_rng[1].add_an({"nhp"}, 0x1C000000, 1, 0x0);
        fld_map_t nhp_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nhp_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nhp_0, "nhp_timeout_thresh_cfg", nhp_timeout_thresh_cfg_prop);
        fld_map_t nhp_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nhp_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(nhp_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(nhp_0, "nhp_timeout_clr", nhp_timeout_clr_prop);
        fld_map_t nhp_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nhp_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(nhp_spare_pio),
                                      0x48,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(nhp_0, "nhp_spare_pio", nhp_spare_pio_prop);
        fld_map_t nhp_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto nhp_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(nhp_scratchpad),
                                       0x50,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(nhp_0, "nhp_scratchpad", nhp_scratchpad_prop);
        fld_map_t nhp_ofs_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_ofs_cfg_prop = csr_prop_t(
                                    std::make_shared<csr_s>(nhp_ofs_cfg),
                                    0x58,
                                    CSR_TYPE::REG_LST,
                                    16);
        add_csr(nhp_0, "nhp_ofs_cfg", nhp_ofs_cfg_prop);
        fld_map_t nhp_f1_num {
            CREATE_ENTRY("val", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto nhp_f1_num_prop = csr_prop_t(
                                   std::make_shared<csr_s>(nhp_f1_num),
                                   0xD8,
                                   CSR_TYPE::REG,
                                   1);
        add_csr(nhp_0, "nhp_f1_num", nhp_f1_num_prop);
        fld_map_t lfa_visited_f1_cfg {
            CREATE_ENTRY("f1_id_vld", 0, 1),
            CREATE_ENTRY("f1_id", 1, 4),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto lfa_visited_f1_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(lfa_visited_f1_cfg),
                                           0xE0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nhp_0, "lfa_visited_f1_cfg", lfa_visited_f1_cfg_prop);
        fld_map_t nhp_lvl0_hash_seed {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nhp_lvl0_hash_seed_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nhp_lvl0_hash_seed),
                                           0xE8,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nhp_0, "nhp_lvl0_hash_seed", nhp_lvl0_hash_seed_prop);
        fld_map_t nhp_lvl1_hash_seed {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nhp_lvl1_hash_seed_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nhp_lvl1_hash_seed),
                                           0xF0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(nhp_0, "nhp_lvl1_hash_seed", nhp_lvl1_hash_seed_prop);
        fld_map_t nhp_lvl0_hash_bypass {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nhp_lvl0_hash_bypass_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nhp_lvl0_hash_bypass),
                                             0xF8,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nhp_0, "nhp_lvl0_hash_bypass", nhp_lvl0_hash_bypass_prop);
        fld_map_t nhp_lvl1_hash_bypass {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nhp_lvl1_hash_bypass_prop = csr_prop_t(
                                             std::make_shared<csr_s>(nhp_lvl1_hash_bypass),
                                             0x100,
                                             CSR_TYPE::REG,
                                             1);
        add_csr(nhp_0, "nhp_lvl1_hash_bypass", nhp_lvl1_hash_bypass_prop);
        fld_map_t nhp_gph_cfg {
            CREATE_ENTRY("fcb_send_enable", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nhp_gph_cfg_prop = csr_prop_t(
                                    std::make_shared<csr_s>(nhp_gph_cfg),
                                    0x108,
                                    CSR_TYPE::REG,
                                    1);
        add_csr(nhp_0, "nhp_gph_cfg", nhp_gph_cfg_prop);
        fld_map_t nhp_remote_gph_prv_ofs {
            CREATE_ENTRY("val", 0, 7),
            CREATE_ENTRY("__rsvd", 7, 57)
        };
        auto nhp_remote_gph_prv_ofs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nhp_remote_gph_prv_ofs),
                                               0x110,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(nhp_0, "nhp_remote_gph_prv_ofs", nhp_remote_gph_prv_ofs_prop);
        fld_map_t nhp_fcp_spray_pktlen_adj {
            CREATE_ENTRY("val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nhp_fcp_spray_pktlen_adj_prop = csr_prop_t(
                std::make_shared<csr_s>(nhp_fcp_spray_pktlen_adj),
                0x118,
                CSR_TYPE::REG,
                1);
        add_csr(nhp_0, "nhp_fcp_spray_pktlen_adj", nhp_fcp_spray_pktlen_adj_prop);
        fld_map_t nhp_fcp_rand_spray_en {
            CREATE_ENTRY("lvl0", 0, 1),
            CREATE_ENTRY("lvl1", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_fcp_rand_spray_en_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nhp_fcp_rand_spray_en),
                                              0x120,
                                              CSR_TYPE::REG,
                                              1);
        add_csr(nhp_0, "nhp_fcp_rand_spray_en", nhp_fcp_rand_spray_en_prop);
        fld_map_t nhp_lvl0_fcp_spray_pktlen_lfsr_cfg {
            CREATE_ENTRY("shift_cfg", 0, 1),
            CREATE_ENTRY("shift_dis", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_lvl0_fcp_spray_pktlen_lfsr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl0_fcp_spray_pktlen_lfsr_cfg),
                    0x128,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl0_fcp_spray_pktlen_lfsr_cfg", nhp_lvl0_fcp_spray_pktlen_lfsr_cfg_prop);
        fld_map_t nhp_lvl1_fcp_spray_pktlen_lfsr_cfg {
            CREATE_ENTRY("shift_cfg", 0, 1),
            CREATE_ENTRY("shift_dis", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_lvl1_fcp_spray_pktlen_lfsr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl1_fcp_spray_pktlen_lfsr_cfg),
                    0x130,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl1_fcp_spray_pktlen_lfsr_cfg", nhp_lvl1_fcp_spray_pktlen_lfsr_cfg_prop);
        fld_map_t nhp_lvl0_fcp_spray_rrptr_lfsr_cfg {
            CREATE_ENTRY("shift_cfg", 0, 1),
            CREATE_ENTRY("shift_dis", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_lvl0_fcp_spray_rrptr_lfsr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl0_fcp_spray_rrptr_lfsr_cfg),
                    0x138,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl0_fcp_spray_rrptr_lfsr_cfg", nhp_lvl0_fcp_spray_rrptr_lfsr_cfg_prop);
        fld_map_t nhp_lvl1_fcp_spray_rrptr_lfsr_cfg {
            CREATE_ENTRY("shift_cfg", 0, 1),
            CREATE_ENTRY("shift_dis", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_lvl1_fcp_spray_rrptr_lfsr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl1_fcp_spray_rrptr_lfsr_cfg),
                    0x140,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl1_fcp_spray_rrptr_lfsr_cfg", nhp_lvl1_fcp_spray_rrptr_lfsr_cfg_prop);
        fld_map_t nhp_lvl0_fcp_spray_randspray_lfsr_cfg {
            CREATE_ENTRY("shift_cfg", 0, 1),
            CREATE_ENTRY("shift_dis", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_lvl0_fcp_spray_randspray_lfsr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl0_fcp_spray_randspray_lfsr_cfg),
                    0x148,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl0_fcp_spray_randspray_lfsr_cfg", nhp_lvl0_fcp_spray_randspray_lfsr_cfg_prop);
        fld_map_t nhp_lvl1_fcp_spray_randspray_lfsr_cfg {
            CREATE_ENTRY("shift_cfg", 0, 1),
            CREATE_ENTRY("shift_dis", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_lvl1_fcp_spray_randspray_lfsr_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl1_fcp_spray_randspray_lfsr_cfg),
                    0x150,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl1_fcp_spray_randspray_lfsr_cfg", nhp_lvl1_fcp_spray_randspray_lfsr_cfg_prop);
        fld_map_t nhp_fs_ring_cfg {
            CREATE_ENTRY("override", 0, 24),
            CREATE_ENTRY("status", 24, 24),
            CREATE_ENTRY("fs_ring_enable", 48, 1),
            CREATE_ENTRY("__rsvd", 49, 15)
        };
        auto nhp_fs_ring_cfg_prop = csr_prop_t(
                                        std::make_shared<csr_s>(nhp_fs_ring_cfg),
                                        0x158,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(nhp_0, "nhp_fs_ring_cfg", nhp_fs_ring_cfg_prop);
        fld_map_t nhp_lvl0_pktlen_lfsr_seed_cfg {
            CREATE_ENTRY("data", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nhp_lvl0_pktlen_lfsr_seed_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl0_pktlen_lfsr_seed_cfg),
                    0x160,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl0_pktlen_lfsr_seed_cfg", nhp_lvl0_pktlen_lfsr_seed_cfg_prop);
        fld_map_t nhp_lvl1_pktlen_lfsr_seed_cfg {
            CREATE_ENTRY("data", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nhp_lvl1_pktlen_lfsr_seed_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl1_pktlen_lfsr_seed_cfg),
                    0x168,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl1_pktlen_lfsr_seed_cfg", nhp_lvl1_pktlen_lfsr_seed_cfg_prop);
        fld_map_t nhp_lvl0_rrptr_lfsr_seed_cfg {
            CREATE_ENTRY("data", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nhp_lvl0_rrptr_lfsr_seed_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl0_rrptr_lfsr_seed_cfg),
                    0x170,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl0_rrptr_lfsr_seed_cfg", nhp_lvl0_rrptr_lfsr_seed_cfg_prop);
        fld_map_t nhp_lvl1_rrptr_lfsr_seed_cfg {
            CREATE_ENTRY("data", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nhp_lvl1_rrptr_lfsr_seed_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl1_rrptr_lfsr_seed_cfg),
                    0x178,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl1_rrptr_lfsr_seed_cfg", nhp_lvl1_rrptr_lfsr_seed_cfg_prop);
        fld_map_t nhp_lvl0_randspray_lfsr_seed_cfg {
            CREATE_ENTRY("data", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nhp_lvl0_randspray_lfsr_seed_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl0_randspray_lfsr_seed_cfg),
                    0x180,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl0_randspray_lfsr_seed_cfg", nhp_lvl0_randspray_lfsr_seed_cfg_prop);
        fld_map_t nhp_lvl1_randspray_lfsr_seed_cfg {
            CREATE_ENTRY("data", 0, 24),
            CREATE_ENTRY("__rsvd", 24, 40)
        };
        auto nhp_lvl1_randspray_lfsr_seed_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(nhp_lvl1_randspray_lfsr_seed_cfg),
                    0x188,
                    CSR_TYPE::REG,
                    1);
        add_csr(nhp_0, "nhp_lvl1_randspray_lfsr_seed_cfg", nhp_lvl1_randspray_lfsr_seed_cfg_prop);
        fld_map_t nhp_bypass_cfg {
            CREATE_ENTRY("bypass_lvl0", 0, 1),
            CREATE_ENTRY("bypass_lvl1", 1, 1),
            CREATE_ENTRY("bypass_lvl2", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto nhp_bypass_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(nhp_bypass_cfg),
                                       0x190,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(nhp_0, "nhp_bypass_cfg", nhp_bypass_cfg_prop);
        fld_map_t nhp_lb_crc_cfg {
            CREATE_ENTRY("lvl0_crc16", 0, 16),
            CREATE_ENTRY("lvl0_crc4", 16, 4),
            CREATE_ENTRY("lvl1_crc16", 20, 16),
            CREATE_ENTRY("lvl1_crc4", 36, 4),
            CREATE_ENTRY("__rsvd", 40, 24)
        };
        auto nhp_lb_crc_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(nhp_lb_crc_cfg),
                                       0x198,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(nhp_0, "nhp_lb_crc_cfg", nhp_lb_crc_cfg_prop);
        fld_map_t nhp_mem_err_inj_cfg {
            CREATE_ENTRY("nhp_lvl0_mem", 0, 1),
            CREATE_ENTRY("nhp_lvl1_mem", 1, 1),
            CREATE_ENTRY("nhp_lvl2_mem", 2, 1),
            CREATE_ENTRY("nhp_fcp_spray_16_mem", 3, 1),
            CREATE_ENTRY("nhp_fcp_spray_8_mem", 4, 1),
            CREATE_ENTRY("err_type", 5, 1),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto nhp_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(nhp_mem_err_inj_cfg),
                                            0x1B8,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(nhp_0, "nhp_mem_err_inj_cfg", nhp_mem_err_inj_cfg_prop);
        fld_map_t nhp_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nhp_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(nhp_fla_ring_module_id_cfg),
                0x1D0,
                CSR_TYPE::REG,
                1);
        add_csr(nhp_0, "nhp_fla_ring_module_id_cfg", nhp_fla_ring_module_id_cfg_prop);
        fld_map_t nhp_local_gph_map_table {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("idx", 1, 7),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto nhp_local_gph_map_table_prop = csr_prop_t(
                                                std::make_shared<csr_s>(nhp_local_gph_map_table),
                                                0x400,
                                                CSR_TYPE::TBL,
                                                1);
        add_csr(nhp_0, "nhp_local_gph_map_table", nhp_local_gph_map_table_prop);
        fld_map_t nhp_gph_stream_map_table {
            CREATE_ENTRY("data", 0, 66),
            CREATE_ENTRY("__rsvd", 66, 62)
        };
        auto nhp_gph_stream_map_table_prop = csr_prop_t(
                std::make_shared<csr_s>(nhp_gph_stream_map_table),
                0x2400,
                CSR_TYPE::TBL,
                1);
        add_csr(nhp_0, "nhp_gph_stream_map_table", nhp_gph_stream_map_table_prop);
        fld_map_t nhp_gph_ls {
            CREATE_ENTRY("write_all", 0, 1),
            CREATE_ENTRY("status", 1, 1),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto nhp_gph_ls_prop = csr_prop_t(
                                   std::make_shared<csr_s>(nhp_gph_ls),
                                   0x4400,
                                   CSR_TYPE::TBL,
                                   1);
        add_csr(nhp_0, "nhp_gph_ls", nhp_gph_ls_prop);
        fld_map_t nhp_rll_stream_map_table {
            CREATE_ENTRY("stream", 0, 6),
            CREATE_ENTRY("__rsvd", 6, 58)
        };
        auto nhp_rll_stream_map_table_prop = csr_prop_t(
                std::make_shared<csr_s>(nhp_rll_stream_map_table),
                0x6400,
                CSR_TYPE::TBL,
                1);
        add_csr(nhp_0, "nhp_rll_stream_map_table", nhp_rll_stream_map_table_prop);
        fld_map_t nhp_rll_state_override {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("val", 1, 16),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto nhp_rll_state_override_prop = csr_prop_t(
                                               std::make_shared<csr_s>(nhp_rll_state_override),
                                               0x6800,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(nhp_0, "nhp_rll_state_override", nhp_rll_state_override_prop);
        fld_map_t nhp_lvl0_mem {
            CREATE_ENTRY("data", 0, 101),
            CREATE_ENTRY("__rsvd", 101, 27)
        };
        auto nhp_lvl0_mem_prop = csr_prop_t(
                                     std::make_shared<csr_s>(nhp_lvl0_mem),
                                     0x10000,
                                     CSR_TYPE::TBL,
                                     1);
        add_csr(nhp_0, "nhp_lvl0_mem", nhp_lvl0_mem_prop);
        fld_map_t nhp_lvl1_mem {
            CREATE_ENTRY("data", 0, 61),
            CREATE_ENTRY("__rsvd", 61, 3)
        };
        auto nhp_lvl1_mem_prop = csr_prop_t(
                                     std::make_shared<csr_s>(nhp_lvl1_mem),
                                     0x110000,
                                     CSR_TYPE::TBL,
                                     1);
        add_csr(nhp_0, "nhp_lvl1_mem", nhp_lvl1_mem_prop);
        fld_map_t nhp_lvl2_mem {
            CREATE_ENTRY("data", 0, 61),
            CREATE_ENTRY("__rsvd", 61, 3)
        };
        auto nhp_lvl2_mem_prop = csr_prop_t(
                                     std::make_shared<csr_s>(nhp_lvl2_mem),
                                     0x150000,
                                     CSR_TYPE::TBL,
                                     1);
        add_csr(nhp_0, "nhp_lvl2_mem", nhp_lvl2_mem_prop);
        fld_map_t nhp_lb_tcam_lvl0 {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("key", 1, 18),
            CREATE_ENTRY("mask", 19, 18),
            CREATE_ENTRY("__rsvd", 37, 27)
        };
        auto nhp_lb_tcam_lvl0_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nhp_lb_tcam_lvl0),
                                         0x190000,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(nhp_0, "nhp_lb_tcam_lvl0", nhp_lb_tcam_lvl0_prop);
        fld_map_t nhp_lb_tcam_lvl1 {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("key", 1, 18),
            CREATE_ENTRY("mask", 19, 18),
            CREATE_ENTRY("__rsvd", 37, 27)
        };
        auto nhp_lb_tcam_lvl1_prop = csr_prop_t(
                                         std::make_shared<csr_s>(nhp_lb_tcam_lvl1),
                                         0x190400,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(nhp_0, "nhp_lb_tcam_lvl1", nhp_lb_tcam_lvl1_prop);
        fld_map_t nhp_lb_key_instr_lvl0 {
            CREATE_ENTRY("inst", 0, 66),
            CREATE_ENTRY("__rsvd", 66, 62)
        };
        auto nhp_lb_key_instr_lvl0_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nhp_lb_key_instr_lvl0),
                                              0x190800,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(nhp_0, "nhp_lb_key_instr_lvl0", nhp_lb_key_instr_lvl0_prop);
        fld_map_t nhp_lb_key_instr_lvl1 {
            CREATE_ENTRY("inst", 0, 66),
            CREATE_ENTRY("__rsvd", 66, 62)
        };
        auto nhp_lb_key_instr_lvl1_prop = csr_prop_t(
                                              std::make_shared<csr_s>(nhp_lb_key_instr_lvl1),
                                              0x191800,
                                              CSR_TYPE::TBL,
                                              1);
        add_csr(nhp_0, "nhp_lb_key_instr_lvl1", nhp_lb_key_instr_lvl1_prop);
        fld_map_t nhp_fcp_wght {
            CREATE_ENTRY("val", 0, 183),
            CREATE_ENTRY("__rsvd", 183, 9)
        };
        auto nhp_fcp_wght_prop = csr_prop_t(
                                     std::make_shared<csr_s>(nhp_fcp_wght),
                                     0x194000,
                                     CSR_TYPE::TBL,
                                     2);
        add_csr(nhp_0, "nhp_fcp_wght", nhp_fcp_wght_prop);
        fld_map_t nhp_rw_tcam {
            CREATE_ENTRY("vld", 0, 1),
            CREATE_ENTRY("key", 1, 24),
            CREATE_ENTRY("mask", 25, 24),
            CREATE_ENTRY("__rsvd", 49, 15)
        };
        auto nhp_rw_tcam_prop = csr_prop_t(
                                    std::make_shared<csr_s>(nhp_rw_tcam),
                                    0x214000,
                                    CSR_TYPE::TBL,
                                    1);
        add_csr(nhp_0, "nhp_rw_tcam", nhp_rw_tcam_prop);
        fld_map_t nhp_rw_tcam_ofs {
            CREATE_ENTRY("value", 0, 4),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto nhp_rw_tcam_ofs_prop = csr_prop_t(
                                        std::make_shared<csr_s>(nhp_rw_tcam_ofs),
                                        0x215000,
                                        CSR_TYPE::TBL,
                                        1);
        add_csr(nhp_0, "nhp_rw_tcam_ofs", nhp_rw_tcam_ofs_prop);
        fld_map_t nhp_stream_fs_num {
            CREATE_ENTRY("data", 0, 5),
            CREATE_ENTRY("__rsvd", 5, 59)
        };
        auto nhp_stream_fs_num_prop = csr_prop_t(
                                          std::make_shared<csr_s>(nhp_stream_fs_num),
                                          0x216000,
                                          CSR_TYPE::TBL,
                                          1);
        add_csr(nhp_0, "nhp_stream_fs_num", nhp_stream_fs_num_prop);
        fld_map_t nhp_lcl_link_status {
            CREATE_ENTRY("data", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto nhp_lcl_link_status_prop = csr_prop_t(
                                            std::make_shared<csr_s>(nhp_lcl_link_status),
                                            0x216800,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(nhp_0, "nhp_lcl_link_status", nhp_lcl_link_status_prop);
        fld_map_t nhp_dbg_probe0_cnt {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto nhp_dbg_probe0_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nhp_dbg_probe0_cnt),
                                           0x217000,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(nhp_0, "nhp_dbg_probe0_cnt", nhp_dbg_probe0_cnt_prop);
        fld_map_t nhp_dbg_probe1_cnt {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto nhp_dbg_probe1_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nhp_dbg_probe1_cnt),
                                           0x217200,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(nhp_0, "nhp_dbg_probe1_cnt", nhp_dbg_probe1_cnt_prop);
        fld_map_t nhp_dbg_probe2_cnt {
            CREATE_ENTRY("fld_count", 0, 64)
        };
        auto nhp_dbg_probe2_cnt_prop = csr_prop_t(
                                           std::make_shared<csr_s>(nhp_dbg_probe2_cnt),
                                           0x217400,
                                           CSR_TYPE::TBL,
                                           1);
        add_csr(nhp_0, "nhp_dbg_probe2_cnt", nhp_dbg_probe2_cnt_prop);
// END nhp
    }
    {
// BEGIN fms
        auto fms_0 = nu_rng[1].add_an({"fms"}, 0x1C400000, 1, 0x0);
        fld_map_t fms_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto fms_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fms_0, "fms_timeout_thresh_cfg", fms_timeout_thresh_cfg_prop);
        fld_map_t fms_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto fms_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(fms_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(fms_0, "fms_timeout_clr", fms_timeout_clr_prop);
        fld_map_t fms_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fms_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(fms_spare_pio),
                                      0x98,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(fms_0, "fms_spare_pio", fms_spare_pio_prop);
        fld_map_t fms_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto fms_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(fms_scratchpad),
                                       0xA0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(fms_0, "fms_scratchpad", fms_scratchpad_prop);
        fld_map_t fms_mem_init_start_cfg {
            CREATE_ENTRY("fld_meter0_ctx_mem", 0, 1),
            CREATE_ENTRY("fld_meter0_cfg_mem", 1, 1),
            CREATE_ENTRY("fld_meter0_green_cntr_mem", 2, 1),
            CREATE_ENTRY("fld_meter0_yellow_cntr_mem", 3, 1),
            CREATE_ENTRY("fld_meter0_red_cntr_mem", 4, 1),
            CREATE_ENTRY("fld_meter1_ctx_mem", 5, 1),
            CREATE_ENTRY("fld_meter1_cfg_mem", 6, 1),
            CREATE_ENTRY("fld_meter1_green_cntr_mem", 7, 1),
            CREATE_ENTRY("fld_meter1_yellow_cntr_mem", 8, 1),
            CREATE_ENTRY("fld_meter1_red_cntr_mem", 9, 1),
            CREATE_ENTRY("fld_bank0_stats_cntr_mem", 10, 1),
            CREATE_ENTRY("fld_bank0_stats_cfg_mem", 11, 1),
            CREATE_ENTRY("fld_bank1_stats_cntr_mem", 12, 1),
            CREATE_ENTRY("fld_bank1_stats_cfg_mem", 13, 1),
            CREATE_ENTRY("fld_bank2_stats_cntr_mem", 14, 1),
            CREATE_ENTRY("fld_bank2_stats_cfg_mem", 15, 1),
            CREATE_ENTRY("fld_bank3_stats_cntr_mem", 16, 1),
            CREATE_ENTRY("fld_bank3_stats_cfg_mem", 17, 1),
            CREATE_ENTRY("fld_psw_eop_info_fifo_mem", 18, 1),
            CREATE_ENTRY("fld_sfg_ctx_mem", 19, 1),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto fms_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_mem_init_start_cfg),
                                               0xA8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(fms_0, "fms_mem_init_start_cfg", fms_mem_init_start_cfg_prop);
        fld_map_t fms_mem_err_inj_cfg {
            CREATE_ENTRY("fld_meter0_ctx_mem", 0, 1),
            CREATE_ENTRY("fld_meter0_cfg_mem", 1, 1),
            CREATE_ENTRY("fld_meter0_green_cntr_mem", 2, 1),
            CREATE_ENTRY("fld_meter0_yellow_cntr_mem", 3, 1),
            CREATE_ENTRY("fld_meter0_red_cntr_mem", 4, 1),
            CREATE_ENTRY("fld_meter1_ctx_mem", 5, 1),
            CREATE_ENTRY("fld_meter1_cfg_mem", 6, 1),
            CREATE_ENTRY("fld_meter1_green_cntr_mem", 7, 1),
            CREATE_ENTRY("fld_meter1_yellow_cntr_mem", 8, 1),
            CREATE_ENTRY("fld_meter1_red_cntr_mem", 9, 1),
            CREATE_ENTRY("fld_bank0_stats_cntr_mem", 10, 1),
            CREATE_ENTRY("fld_bank0_stats_cfg_mem", 11, 1),
            CREATE_ENTRY("fld_bank1_stats_cntr_mem", 12, 1),
            CREATE_ENTRY("fld_bank1_stats_cfg_mem", 13, 1),
            CREATE_ENTRY("fld_bank2_stats_cntr_mem", 14, 1),
            CREATE_ENTRY("fld_bank2_stats_cfg_mem", 15, 1),
            CREATE_ENTRY("fld_bank3_stats_cntr_mem", 16, 1),
            CREATE_ENTRY("fld_bank3_stats_cfg_mem", 17, 1),
            CREATE_ENTRY("fld_psw_eop_info_fifo_mem", 18, 1),
            CREATE_ENTRY("fld_sfg_ctx_mem", 19, 1),
            CREATE_ENTRY("fld_err_type", 20, 1),
            CREATE_ENTRY("__rsvd", 21, 43)
        };
        auto fms_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fms_mem_err_inj_cfg),
                                            0xD0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(fms_0, "fms_mem_err_inj_cfg", fms_mem_err_inj_cfg_prop);
        fld_map_t fms_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_fla_ring_module_id_cfg),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(fms_0, "fms_fla_ring_module_id_cfg", fms_fla_ring_module_id_cfg_prop);
        fld_map_t fms_timer_ctrl_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_bgnd_updt_enable", 1, 1),
            CREATE_ENTRY("fld_scan_intvl_cnt", 2, 9),
            CREATE_ENTRY("fld_part_timer_cnt", 11, 5),
            CREATE_ENTRY("fld_base_timer_cnt", 16, 5),
            CREATE_ENTRY("fld_max_timestamp_wrap_val", 21, 24),
            CREATE_ENTRY("__rsvd", 45, 19)
        };
        auto fms_timer_ctrl_cfg_prop = csr_prop_t(
                                           std::make_shared<csr_s>(fms_timer_ctrl_cfg),
                                           0xE0,
                                           CSR_TYPE::REG,
                                           1);
        add_csr(fms_0, "fms_timer_ctrl_cfg", fms_timer_ctrl_cfg_prop);
        fld_map_t fms_misc_cfg {
            CREATE_ENTRY("fld_bank0_vld_map", 0, 4),
            CREATE_ENTRY("fld_bank1_vld_map", 4, 4),
            CREATE_ENTRY("fld_bank2_vld_map", 8, 4),
            CREATE_ENTRY("fld_pps_len_val", 12, 14),
            CREATE_ENTRY("fld_meter_adj_val", 26, 14),
            CREATE_ENTRY("fld_stats_adj_val", 40, 14),
            CREATE_ENTRY("__rsvd", 54, 10)
        };
        auto fms_misc_cfg_prop = csr_prop_t(
                                     std::make_shared<csr_s>(fms_misc_cfg),
                                     0xE8,
                                     CSR_TYPE::REG,
                                     1);
        add_csr(fms_0, "fms_misc_cfg", fms_misc_cfg_prop);
        fld_map_t fms_sfg_ctx_mem_dhs {
            CREATE_ENTRY("fld_meter0_idx_vld", 0, 1),
            CREATE_ENTRY("fld_meter0_idx", 1, 8),
            CREATE_ENTRY("fld_meter0_state", 9, 2),
            CREATE_ENTRY("fld_meter1_idx_vld", 11, 1),
            CREATE_ENTRY("fld_meter1_idx", 12, 8),
            CREATE_ENTRY("fld_meter1_state", 20, 2),
            CREATE_ENTRY("fld_bank0_cntr_idx_vld", 22, 1),
            CREATE_ENTRY("fld_bank0_cntr_idx", 23, 9),
            CREATE_ENTRY("fld_bank1_cntr_idx_vld", 32, 1),
            CREATE_ENTRY("fld_bank1_cntr_idx", 33, 9),
            CREATE_ENTRY("fld_bank2_cntr_idx_vld", 42, 1),
            CREATE_ENTRY("fld_bank2_cntr_idx", 43, 9),
            CREATE_ENTRY("fld_bank3_cntr_idx_vld", 52, 1),
            CREATE_ENTRY("fld_bank3_cntr_idx", 53, 9),
            CREATE_ENTRY("fld_l3_plen", 62, 14),
            CREATE_ENTRY("__rsvd", 76, 52)
        };
        auto fms_sfg_ctx_mem_dhs_prop = csr_prop_t(
                                            std::make_shared<csr_s>(fms_sfg_ctx_mem_dhs),
                                            0x2000,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(fms_0, "fms_sfg_ctx_mem_dhs", fms_sfg_ctx_mem_dhs_prop);
        fld_map_t fms_psw_eop_info_fifo_mem_dhs {
            CREATE_ENTRY("fld_pkt_tag_id", 0, 9),
            CREATE_ENTRY("fld_igr_l2_plen", 9, 14),
            CREATE_ENTRY("fld_egr_l2_plen", 23, 14),
            CREATE_ENTRY("fld_drop", 37, 1),
            CREATE_ENTRY("__rsvd", 38, 26)
        };
        auto fms_psw_eop_info_fifo_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_psw_eop_info_fifo_mem_dhs),
                    0x22000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_psw_eop_info_fifo_mem_dhs", fms_psw_eop_info_fifo_mem_dhs_prop);
        fld_map_t fms_meter0_ctx_mem_dhs {
            CREATE_ENTRY("fld_last_timestamp", 0, 24),
            CREATE_ENTRY("fld_comitd_bkt", 24, 24),
            CREATE_ENTRY("fld_excess_bkt", 48, 24),
            CREATE_ENTRY("__rsvd", 72, 56)
        };
        auto fms_meter0_ctx_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter0_ctx_mem_dhs),
                                               0x2A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter0_ctx_mem_dhs", fms_meter0_ctx_mem_dhs_prop);
        fld_map_t fms_meter0_cfg_mem_dhs {
            CREATE_ENTRY("fld_time_interval", 0, 4),
            CREATE_ENTRY("fld_crd_unit", 4, 4),
            CREATE_ENTRY("fld_comitd_crd_rate", 8, 7),
            CREATE_ENTRY("fld_excess_crd_rate", 15, 7),
            CREATE_ENTRY("fld_comitd_burst_size", 22, 16),
            CREATE_ENTRY("fld_excess_burst_size", 38, 16),
            CREATE_ENTRY("fld_mtr_mode", 54, 1),
            CREATE_ENTRY("fld_len_mode", 55, 1),
            CREATE_ENTRY("fld_rfc_mode", 56, 1),
            CREATE_ENTRY("fld_pps_mode", 57, 1),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto fms_meter0_cfg_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter0_cfg_mem_dhs),
                                               0x3A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter0_cfg_mem_dhs", fms_meter0_cfg_mem_dhs_prop);
        fld_map_t fms_meter0_green_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter0_green_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter0_green_cntr_mem_dhs),
                    0x3E000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter0_green_cntr_mem_dhs", fms_meter0_green_cntr_mem_dhs_prop);
        fld_map_t fms_meter0_yellow_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter0_yellow_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter0_yellow_cntr_mem_dhs),
                    0x42000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter0_yellow_cntr_mem_dhs", fms_meter0_yellow_cntr_mem_dhs_prop);
        fld_map_t fms_meter0_red_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter0_red_cntr_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_meter0_red_cntr_mem_dhs),
                0x46000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_meter0_red_cntr_mem_dhs", fms_meter0_red_cntr_mem_dhs_prop);
        fld_map_t fms_meter1_ctx_mem_dhs {
            CREATE_ENTRY("fld_last_timestamp", 0, 24),
            CREATE_ENTRY("fld_comitd_bkt", 24, 24),
            CREATE_ENTRY("fld_excess_bkt", 48, 24),
            CREATE_ENTRY("__rsvd", 72, 56)
        };
        auto fms_meter1_ctx_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter1_ctx_mem_dhs),
                                               0x4A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter1_ctx_mem_dhs", fms_meter1_ctx_mem_dhs_prop);
        fld_map_t fms_meter1_cfg_mem_dhs {
            CREATE_ENTRY("fld_time_interval", 0, 4),
            CREATE_ENTRY("fld_crd_unit", 4, 4),
            CREATE_ENTRY("fld_comitd_crd_rate", 8, 7),
            CREATE_ENTRY("fld_excess_crd_rate", 15, 7),
            CREATE_ENTRY("fld_comitd_burst_size", 22, 16),
            CREATE_ENTRY("fld_excess_burst_size", 38, 16),
            CREATE_ENTRY("fld_mtr_mode", 54, 1),
            CREATE_ENTRY("fld_len_mode", 55, 1),
            CREATE_ENTRY("fld_rfc_mode", 56, 1),
            CREATE_ENTRY("fld_pps_mode", 57, 1),
            CREATE_ENTRY("__rsvd", 58, 6)
        };
        auto fms_meter1_cfg_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_meter1_cfg_mem_dhs),
                                               0x5A000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_meter1_cfg_mem_dhs", fms_meter1_cfg_mem_dhs_prop);
        fld_map_t fms_meter1_green_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter1_green_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter1_green_cntr_mem_dhs),
                    0x5E000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter1_green_cntr_mem_dhs", fms_meter1_green_cntr_mem_dhs_prop);
        fld_map_t fms_meter1_yellow_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter1_yellow_cntr_mem_dhs_prop = csr_prop_t(
                    std::make_shared<csr_s>(fms_meter1_yellow_cntr_mem_dhs),
                    0x62000,
                    CSR_TYPE::TBL,
                    1);
        add_csr(fms_0, "fms_meter1_yellow_cntr_mem_dhs", fms_meter1_yellow_cntr_mem_dhs_prop);
        fld_map_t fms_meter1_red_cntr_mem_dhs {
            CREATE_ENTRY("fld_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_pkt_cnt", 35, 29)
        };
        auto fms_meter1_red_cntr_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_meter1_red_cntr_mem_dhs),
                0x66000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_meter1_red_cntr_mem_dhs", fms_meter1_red_cntr_mem_dhs_prop);
        fld_map_t fms_bank0_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank0_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank0_stats_cfg_mem_dhs),
                0x6A000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank0_stats_cfg_mem_dhs", fms_bank0_stats_cfg_mem_dhs_prop);
        fld_map_t fms_bank1_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank1_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank1_stats_cfg_mem_dhs),
                0x6C000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank1_stats_cfg_mem_dhs", fms_bank1_stats_cfg_mem_dhs_prop);
        fld_map_t fms_bank2_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank2_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank2_stats_cfg_mem_dhs),
                0x6E000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank2_stats_cfg_mem_dhs", fms_bank2_stats_cfg_mem_dhs_prop);
        fld_map_t fms_bank3_stats_cfg_mem_dhs {
            CREATE_ENTRY("fld_entry0_cntr_mode", 0, 1),
            CREATE_ENTRY("fld_entry0_len_mode", 1, 1),
            CREATE_ENTRY("fld_entry1_cntr_mode", 2, 1),
            CREATE_ENTRY("fld_entry1_len_mode", 3, 1),
            CREATE_ENTRY("fld_entry2_cntr_mode", 4, 1),
            CREATE_ENTRY("fld_entry2_len_mode", 5, 1),
            CREATE_ENTRY("fld_entry3_cntr_mode", 6, 1),
            CREATE_ENTRY("fld_entry3_len_mode", 7, 1),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto fms_bank3_stats_cfg_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(fms_bank3_stats_cfg_mem_dhs),
                0x70000,
                CSR_TYPE::TBL,
                1);
        add_csr(fms_0, "fms_bank3_stats_cfg_mem_dhs", fms_bank3_stats_cfg_mem_dhs_prop);
        fld_map_t fms_stats_cntr_mem_dhs {
            CREATE_ENTRY("fld_bank0_byte_cnt", 0, 35),
            CREATE_ENTRY("fld_bank0_pkt_cnt", 35, 29),
            CREATE_ENTRY("fld_bank1_byte_cnt", 64, 35),
            CREATE_ENTRY("fld_bank1_pkt_cnt", 99, 29),
            CREATE_ENTRY("fld_bank2_byte_cnt", 128, 35),
            CREATE_ENTRY("fld_bank2_pkt_cnt", 163, 29),
            CREATE_ENTRY("fld_bank3_byte_cnt", 192, 35),
            CREATE_ENTRY("fld_bank3_pkt_cnt", 227, 29)
        };
        auto fms_stats_cntr_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(fms_stats_cntr_mem_dhs),
                                               0x74000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(fms_0, "fms_stats_cntr_mem_dhs", fms_stats_cntr_mem_dhs_prop);
// END fms
    }
    {
// BEGIN sfg
        auto sfg_0 = nu_rng[1].add_an({"sfg"}, 0x1C800000, 1, 0x0);
        fld_map_t sfg_timeout_thresh_cfg {
            CREATE_ENTRY("val", 0, 2),
            CREATE_ENTRY("__rsvd", 2, 62)
        };
        auto sfg_timeout_thresh_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_timeout_thresh_cfg),
                                               0x0,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(sfg_0, "sfg_timeout_thresh_cfg", sfg_timeout_thresh_cfg_prop);
        fld_map_t sfg_timeout_clr {
            CREATE_ENTRY("val", 0, 1),
            CREATE_ENTRY("__rsvd", 1, 63)
        };
        auto sfg_timeout_clr_prop = csr_prop_t(
                                        std::make_shared<csr_s>(sfg_timeout_clr),
                                        0x10,
                                        CSR_TYPE::REG,
                                        1);
        add_csr(sfg_0, "sfg_timeout_clr", sfg_timeout_clr_prop);
        fld_map_t sfg_spare_pio {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sfg_spare_pio_prop = csr_prop_t(
                                      std::make_shared<csr_s>(sfg_spare_pio),
                                      0x98,
                                      CSR_TYPE::REG,
                                      1);
        add_csr(sfg_0, "sfg_spare_pio", sfg_spare_pio_prop);
        fld_map_t sfg_scratchpad {
            CREATE_ENTRY("val", 0, 64)
        };
        auto sfg_scratchpad_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_scratchpad),
                                       0xA0,
                                       CSR_TYPE::REG,
                                       1);
        add_csr(sfg_0, "sfg_scratchpad", sfg_scratchpad_prop);
        fld_map_t sfg_mem_init_start_cfg {
            CREATE_ENTRY("fld_rwt_instr_bank0_mem", 0, 1),
            CREATE_ENTRY("fld_rwt_instr_bank1_mem", 1, 1),
            CREATE_ENTRY("fld_eg_qos_tbl_mem", 2, 1),
            CREATE_ENTRY("__rsvd", 3, 61)
        };
        auto sfg_mem_init_start_cfg_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_mem_init_start_cfg),
                                               0xA8,
                                               CSR_TYPE::REG,
                                               1);
        add_csr(sfg_0, "sfg_mem_init_start_cfg", sfg_mem_init_start_cfg_prop);
        fld_map_t sfg_mem_err_inj_cfg {
            CREATE_ENTRY("fld_rwt_instr_bank0_mem", 0, 1),
            CREATE_ENTRY("fld_rwt_instr_bank1_mem", 1, 1),
            CREATE_ENTRY("fld_eg_qos_tbl_mem", 2, 1),
            CREATE_ENTRY("fld_err_type", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto sfg_mem_err_inj_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(sfg_mem_err_inj_cfg),
                                            0xD0,
                                            CSR_TYPE::REG,
                                            1);
        add_csr(sfg_0, "sfg_mem_err_inj_cfg", sfg_mem_err_inj_cfg_prop);
        fld_map_t sfg_fla_ring_module_id_cfg {
            CREATE_ENTRY("fld_val", 0, 8),
            CREATE_ENTRY("__rsvd", 8, 56)
        };
        auto sfg_fla_ring_module_id_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_fla_ring_module_id_cfg),
                0xD8,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_fla_ring_module_id_cfg", sfg_fla_ring_module_id_cfg_prop);
        fld_map_t sfg_erp_mode_pol_drop_lkup_cfg {
            CREATE_ENTRY("fld_drop_col_rsvd", 0, 1),
            CREATE_ENTRY("fld_drop_col_red", 1, 1),
            CREATE_ENTRY("fld_drop_col_yellow", 2, 1),
            CREATE_ENTRY("fld_drop_col_green", 3, 1),
            CREATE_ENTRY("__rsvd", 4, 60)
        };
        auto sfg_erp_mode_pol_drop_lkup_cfg_prop = csr_prop_t(
                    std::make_shared<csr_s>(sfg_erp_mode_pol_drop_lkup_cfg),
                    0xE0,
                    CSR_TYPE::REG,
                    1);
        add_csr(sfg_0, "sfg_erp_mode_pol_drop_lkup_cfg", sfg_erp_mode_pol_drop_lkup_cfg_prop);
        fld_map_t sfg_meter0_color_lkup_cfg {
            CREATE_ENTRY("fld_color", 0, 64)
        };
        auto sfg_meter0_color_lkup_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter0_color_lkup_cfg),
                0xE8,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_meter0_color_lkup_cfg", sfg_meter0_color_lkup_cfg_prop);
        fld_map_t sfg_meter1_color_lkup_cfg {
            CREATE_ENTRY("fld_color", 0, 64)
        };
        auto sfg_meter1_color_lkup_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter1_color_lkup_cfg),
                0xF0,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_meter1_color_lkup_cfg", sfg_meter1_color_lkup_cfg_prop);
        fld_map_t sfg_smpler_pps_timer_cfg {
            CREATE_ENTRY("fld_enable", 0, 1),
            CREATE_ENTRY("fld_tick_cnt", 1, 20),
            CREATE_ENTRY("__rsvd", 21, 43)
        };
        auto sfg_smpler_pps_timer_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_pps_timer_cfg),
                0xF8,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_smpler_pps_timer_cfg", sfg_smpler_pps_timer_cfg_prop);
        fld_map_t sfg_smpler_lfsr_seed_cfg {
            CREATE_ENTRY("fld_data", 0, 20),
            CREATE_ENTRY("__rsvd", 20, 44)
        };
        auto sfg_smpler_lfsr_seed_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_lfsr_seed_cfg),
                0x108,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_smpler_lfsr_seed_cfg", sfg_smpler_lfsr_seed_cfg_prop);
        fld_map_t sfg_frv_flex_byte_sel_cfg {
            CREATE_ENTRY("fld_byte0_type", 0, 1),
            CREATE_ENTRY("fld_byte0_ofs", 1, 7),
            CREATE_ENTRY("fld_byte1_type", 8, 1),
            CREATE_ENTRY("fld_byte1_ofs", 9, 7),
            CREATE_ENTRY("fld_byte2_type", 16, 1),
            CREATE_ENTRY("fld_byte2_ofs", 17, 7),
            CREATE_ENTRY("fld_byte3_type", 24, 1),
            CREATE_ENTRY("fld_byte3_ofs", 25, 7),
            CREATE_ENTRY("fld_byte4_type", 32, 1),
            CREATE_ENTRY("fld_byte4_ofs", 33, 7),
            CREATE_ENTRY("fld_byte5_type", 40, 1),
            CREATE_ENTRY("fld_byte5_ofs", 41, 7),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto sfg_frv_flex_byte_sel_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_frv_flex_byte_sel_cfg),
                0x110,
                CSR_TYPE::REG,
                1);
        add_csr(sfg_0, "sfg_frv_flex_byte_sel_cfg", sfg_frv_flex_byte_sel_cfg_prop);
        fld_map_t sfg_meter0_cfg {
            CREATE_ENTRY("data", 0, 64)
        };
        auto sfg_meter0_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_meter0_cfg),
                                       0x120,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(sfg_0, "sfg_meter0_cfg", sfg_meter0_cfg_prop);
        fld_map_t sfg_meter1_cfg {
            CREATE_ENTRY("data", 0, 64)
        };
        auto sfg_meter1_cfg_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_meter1_cfg),
                                       0x220,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(sfg_0, "sfg_meter1_cfg", sfg_meter1_cfg_prop);
        fld_map_t sfg_smpler_attr_cfg {
            CREATE_ENTRY("fld_pps_enable", 0, 1),
            CREATE_ENTRY("fld_pps_time_intvl", 1, 20),
            CREATE_ENTRY("fld_pps_crdt_thresh", 21, 7),
            CREATE_ENTRY("fld_smpl_type", 28, 1),
            CREATE_ENTRY("fld_smpl_rate", 29, 10),
            CREATE_ENTRY("fld_smpl_run_size", 39, 4),
            CREATE_ENTRY("__rsvd", 43, 21)
        };
        auto sfg_smpler_attr_cfg_prop = csr_prop_t(
                                            std::make_shared<csr_s>(sfg_smpler_attr_cfg),
                                            0x400,
                                            CSR_TYPE::TBL,
                                            1);
        add_csr(sfg_0, "sfg_smpler_attr_cfg", sfg_smpler_attr_cfg_prop);
        fld_map_t sfg_smpler_rwt_instr_cfg {
            CREATE_ENTRY("fld_egr_stream", 0, 6),
            CREATE_ENTRY("fld_egr_que", 6, 4),
            CREATE_ENTRY("fld_first_cell_only", 10, 1),
            CREATE_ENTRY("fld_itype0", 11, 4),
            CREATE_ENTRY("fld_instr0", 15, 20),
            CREATE_ENTRY("fld_itype1", 35, 4),
            CREATE_ENTRY("fld_instr1", 39, 20),
            CREATE_ENTRY("fld_itype2", 59, 4),
            CREATE_ENTRY("fld_instr2", 63, 20),
            CREATE_ENTRY("fld_itype3", 83, 4),
            CREATE_ENTRY("fld_instr3", 87, 20),
            CREATE_ENTRY("__rsvd", 107, 21)
        };
        auto sfg_smpler_rwt_instr_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_rwt_instr_cfg),
                0x1400,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_smpler_rwt_instr_cfg", sfg_smpler_rwt_instr_cfg_prop);
        fld_map_t sfg_smpler_flag_mask_cfg {
            CREATE_ENTRY("fld_mask", 0, 64)
        };
        auto sfg_smpler_flag_mask_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_flag_mask_cfg),
                0x3400,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_smpler_flag_mask_cfg", sfg_smpler_flag_mask_cfg_prop);
        fld_map_t sfg_l2_len_chk_cam_dhs {
            CREATE_ENTRY("fld_vld", 0, 1),
            CREATE_ENTRY("fld_key_flags", 1, 4),
            CREATE_ENTRY("fld_key_template", 5, 16),
            CREATE_ENTRY("fld_msk_flags", 21, 4),
            CREATE_ENTRY("fld_msk_template", 25, 16),
            CREATE_ENTRY("fld_l2_shn", 41, 3),
            CREATE_ENTRY("fld_l3_shn", 44, 3),
            CREATE_ENTRY("__rsvd", 47, 17)
        };
        auto sfg_l2_len_chk_cam_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_l2_len_chk_cam_dhs),
                                               0x3600,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(sfg_0, "sfg_l2_len_chk_cam_dhs", sfg_l2_len_chk_cam_dhs_prop);
        fld_map_t sfg_eg_str_mtu_cfg_tbl {
            CREATE_ENTRY("fld_val", 0, 14),
            CREATE_ENTRY("__rsvd", 14, 50)
        };
        auto sfg_eg_str_mtu_cfg_tbl_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_eg_str_mtu_cfg_tbl),
                                               0x3700,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(sfg_0, "sfg_eg_str_mtu_cfg_tbl", sfg_eg_str_mtu_cfg_tbl_prop);
        fld_map_t sfg_stats_cntr {
            CREATE_ENTRY("fld_val", 0, 48),
            CREATE_ENTRY("__rsvd", 48, 16)
        };
        auto sfg_stats_cntr_prop = csr_prop_t(
                                       std::make_shared<csr_s>(sfg_stats_cntr),
                                       0x3F00,
                                       CSR_TYPE::TBL,
                                       1);
        add_csr(sfg_0, "sfg_stats_cntr", sfg_stats_cntr_prop);
        fld_map_t sfg_smpler_stats_cntrs_dhs {
            CREATE_ENTRY("val", 0, 32),
            CREATE_ENTRY("__rsvd", 32, 32)
        };
        auto sfg_smpler_stats_cntrs_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_smpler_stats_cntrs_dhs),
                0x4200,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_smpler_stats_cntrs_dhs", sfg_smpler_stats_cntrs_dhs_prop);
        fld_map_t sfg_snapshot_sym {
            CREATE_ENTRY("fld_val", 0, 64)
        };
        auto sfg_snapshot_sym_prop = csr_prop_t(
                                         std::make_shared<csr_s>(sfg_snapshot_sym),
                                         0x5200,
                                         CSR_TYPE::TBL,
                                         1);
        add_csr(sfg_0, "sfg_snapshot_sym", sfg_snapshot_sym_prop);
        fld_map_t sfg_eg_qos_tbl_mem_dhs {
            CREATE_ENTRY("fld_pol_drop", 0, 1),
            CREATE_ENTRY("fld_vlan_qos_ovrt", 1, 1),
            CREATE_ENTRY("fld_vlan_qos", 2, 4),
            CREATE_ENTRY("fld_ip_dscp_ovrt", 6, 1),
            CREATE_ENTRY("fld_ip_dscp", 7, 6),
            CREATE_ENTRY("fld_egr_queue", 13, 4),
            CREATE_ENTRY("__rsvd", 17, 47)
        };
        auto sfg_eg_qos_tbl_mem_dhs_prop = csr_prop_t(
                                               std::make_shared<csr_s>(sfg_eg_qos_tbl_mem_dhs),
                                               0x8000,
                                               CSR_TYPE::TBL,
                                               1);
        add_csr(sfg_0, "sfg_eg_qos_tbl_mem_dhs", sfg_eg_qos_tbl_mem_dhs_prop);
        fld_map_t sfg_rwt_instr_bank0_mem_dhs {
            CREATE_ENTRY("fld_dbl_inst", 0, 1),
            CREATE_ENTRY("fld_itype0", 1, 4),
            CREATE_ENTRY("fld_instr0", 5, 20),
            CREATE_ENTRY("fld_itype1", 25, 4),
            CREATE_ENTRY("fld_instr1", 29, 20),
            CREATE_ENTRY("fld_itype2", 49, 4),
            CREATE_ENTRY("fld_instr2", 53, 20),
            CREATE_ENTRY("fld_itype3", 73, 4),
            CREATE_ENTRY("fld_instr3", 77, 20),
            CREATE_ENTRY("fld_itype4", 97, 4),
            CREATE_ENTRY("fld_instr4", 101, 20),
            CREATE_ENTRY("fld_itype5", 121, 4),
            CREATE_ENTRY("fld_instr5", 125, 20),
            CREATE_ENTRY("__rsvd", 145, 47)
        };
        auto sfg_rwt_instr_bank0_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_rwt_instr_bank0_mem_dhs),
                0x50000,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_rwt_instr_bank0_mem_dhs", sfg_rwt_instr_bank0_mem_dhs_prop);
        fld_map_t sfg_rwt_instr_bank1_mem_dhs {
            CREATE_ENTRY("fld_dbl_inst", 0, 1),
            CREATE_ENTRY("fld_itype0", 1, 4),
            CREATE_ENTRY("fld_instr0", 5, 20),
            CREATE_ENTRY("fld_itype1", 25, 4),
            CREATE_ENTRY("fld_instr1", 29, 20),
            CREATE_ENTRY("fld_itype2", 49, 4),
            CREATE_ENTRY("fld_instr2", 53, 20),
            CREATE_ENTRY("fld_itype3", 73, 4),
            CREATE_ENTRY("fld_instr3", 77, 20),
            CREATE_ENTRY("fld_itype4", 97, 4),
            CREATE_ENTRY("fld_instr4", 101, 20),
            CREATE_ENTRY("fld_itype5", 121, 4),
            CREATE_ENTRY("fld_instr5", 125, 20),
            CREATE_ENTRY("__rsvd", 145, 47)
        };
        auto sfg_rwt_instr_bank1_mem_dhs_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_rwt_instr_bank1_mem_dhs),
                0x1D0000,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_rwt_instr_bank1_mem_dhs", sfg_rwt_instr_bank1_mem_dhs_prop);
        fld_map_t sfg_meter0_state_mem_cfg {
            CREATE_ENTRY("fld_0", 0, 2),
            CREATE_ENTRY("fld_1", 2, 2),
            CREATE_ENTRY("fld_2", 4, 2),
            CREATE_ENTRY("fld_3", 6, 2),
            CREATE_ENTRY("fld_4", 8, 2),
            CREATE_ENTRY("fld_5", 10, 2),
            CREATE_ENTRY("fld_6", 12, 2),
            CREATE_ENTRY("fld_7", 14, 2),
            CREATE_ENTRY("fld_8", 16, 2),
            CREATE_ENTRY("fld_9", 18, 2),
            CREATE_ENTRY("fld_10", 20, 2),
            CREATE_ENTRY("fld_11", 22, 2),
            CREATE_ENTRY("fld_12", 24, 2),
            CREATE_ENTRY("fld_13", 26, 2),
            CREATE_ENTRY("fld_14", 28, 2),
            CREATE_ENTRY("fld_15", 30, 2),
            CREATE_ENTRY("fld_16", 32, 2),
            CREATE_ENTRY("fld_17", 34, 2),
            CREATE_ENTRY("fld_18", 36, 2),
            CREATE_ENTRY("fld_19", 38, 2),
            CREATE_ENTRY("fld_20", 40, 2),
            CREATE_ENTRY("fld_21", 42, 2),
            CREATE_ENTRY("fld_22", 44, 2),
            CREATE_ENTRY("fld_23", 46, 2),
            CREATE_ENTRY("fld_24", 48, 2),
            CREATE_ENTRY("fld_25", 50, 2),
            CREATE_ENTRY("fld_26", 52, 2),
            CREATE_ENTRY("fld_27", 54, 2),
            CREATE_ENTRY("fld_28", 56, 2),
            CREATE_ENTRY("fld_29", 58, 2),
            CREATE_ENTRY("fld_30", 60, 2),
            CREATE_ENTRY("fld_31", 62, 2)
        };
        auto sfg_meter0_state_mem_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter0_state_mem_cfg),
                0x350000,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_meter0_state_mem_cfg", sfg_meter0_state_mem_cfg_prop);
        fld_map_t sfg_meter1_state_mem_cfg {
            CREATE_ENTRY("fld_0", 0, 2),
            CREATE_ENTRY("fld_1", 2, 2),
            CREATE_ENTRY("fld_2", 4, 2),
            CREATE_ENTRY("fld_3", 6, 2),
            CREATE_ENTRY("fld_4", 8, 2),
            CREATE_ENTRY("fld_5", 10, 2),
            CREATE_ENTRY("fld_6", 12, 2),
            CREATE_ENTRY("fld_7", 14, 2),
            CREATE_ENTRY("fld_8", 16, 2),
            CREATE_ENTRY("fld_9", 18, 2),
            CREATE_ENTRY("fld_10", 20, 2),
            CREATE_ENTRY("fld_11", 22, 2),
            CREATE_ENTRY("fld_12", 24, 2),
            CREATE_ENTRY("fld_13", 26, 2),
            CREATE_ENTRY("fld_14", 28, 2),
            CREATE_ENTRY("fld_15", 30, 2),
            CREATE_ENTRY("fld_16", 32, 2),
            CREATE_ENTRY("fld_17", 34, 2),
            CREATE_ENTRY("fld_18", 36, 2),
            CREATE_ENTRY("fld_19", 38, 2),
            CREATE_ENTRY("fld_20", 40, 2),
            CREATE_ENTRY("fld_21", 42, 2),
            CREATE_ENTRY("fld_22", 44, 2),
            CREATE_ENTRY("fld_23", 46, 2),
            CREATE_ENTRY("fld_24", 48, 2),
            CREATE_ENTRY("fld_25", 50, 2),
            CREATE_ENTRY("fld_26", 52, 2),
            CREATE_ENTRY("fld_27", 54, 2),
            CREATE_ENTRY("fld_28", 56, 2),
            CREATE_ENTRY("fld_29", 58, 2),
            CREATE_ENTRY("fld_30", 60, 2),
            CREATE_ENTRY("fld_31", 62, 2)
        };
        auto sfg_meter1_state_mem_cfg_prop = csr_prop_t(
                std::make_shared<csr_s>(sfg_meter1_state_mem_cfg),
                0x350200,
                CSR_TYPE::TBL,
                1);
        add_csr(sfg_0, "sfg_meter1_state_mem_cfg", sfg_meter1_state_mem_cfg_prop);
// END sfg
    }
    sys_rings["NU"] = nu_rng;


}
