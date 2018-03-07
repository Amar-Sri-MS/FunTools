/*
 *  csr_grp.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <vector>

#include "csr_type.h"
#include "csr_prop.h"


class csr_grp_t {
    public:
        explicit csr_grp_t(const std::shared_ptr<csr_s>& sign,
                const uint64_t& addr,
                const CSR_TYPE& type,
                const uint16_t& n_entries=1,
                const uint8_t& n_inst=1
                );
        csr_prop_t& operator[](const uint8_t& inst);
        void set_an_props(const uint64_t& base_addr,
                const uint8_t& n_an_inst,
                const uint64_t& skip_addr);
        void set_gid(const uint8_t& gid);
        void set_rd_cb(rd_fptr r_fn=nullptr);
        void set_wr_cb(wr_fptr w_fn=nullptr);
        csr_prop_t& get_csr(const uint8_t& gid);

    private:
        std::vector<csr_prop_t> csr_props;
        uint64_t m_base{0};
        uint8_t m_gid{0};
};
