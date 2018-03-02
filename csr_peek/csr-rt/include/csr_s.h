/*
 *  csr_s.h
 *
 *  Created by Hariharan Thantry on 2018-01-27
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

/*
 * Defines a signature class that must be passed in as a 
 * parameter to each container created.
 */
#include <cassert>
#include <functional>
#include <memory>
#include <string>
#include <unordered_map>
#include <tuple>

#include "stdint.h"
#include "csr_utils.h"

/* start off, width */
//typedef std::tuple<uint16_t, uint16_t> fld_off_t;

struct fld_off_t {

    uint16_t fld_off{0};
    uint16_t width{0};
    fld_off_t(const fld_off_t& other) = default;
    fld_off_t& operator=(const fld_off_t& other) = default;
    fld_off_t(const uint16_t& fld, const uint16_t& w);    
    friend std::ostream& operator<<(std::ostream& os, const fld_off_t& obj);

};

typedef std::unordered_map<std::string, fld_off_t, string_hash> fld_map_t;



class csr_s {
    public:
        csr_s(void);
        csr_s(const fld_map_t& fld_map);
        const fld_off_t& operator[](const std::string& fld_name) const;
        csr_s(const csr_s& other);
        csr_s& operator=(const csr_s&);
        uint16_t sz(void) const;
        typedef fld_map_t::iterator iterator;
        typedef fld_map_t::const_iterator const_iterator;
        inline iterator begin() noexcept { return fld_map.begin(); }
        inline iterator end() noexcept { return fld_map.end(); }
        inline const_iterator cbegin() const noexcept { return fld_map.cbegin(); }
        inline const_iterator cend() const noexcept { return fld_map.cend(); }
    private:
        fld_map_t fld_map;
        friend std::ostream& operator<<(std::ostream& os, const csr_s& obj);
};

