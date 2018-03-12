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
    nu_rng.add_ring(1, 0x5800000000);
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
    sys_rings["NU"] = nu_rng;


}