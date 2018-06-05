/*
 *  csr_utils.h
 *
 *  Created by Hariharan Thantry on 2018-02-01
 *
 *  Copyright 2018 Fungible Inc. All rights reserved.
 */
#pragma once
struct string_hash : public std::unary_function<const char*, std::size_t> {
    std::size_t operator()(const char* k) const {
        std::hash<const char*> hasher;
        return hasher(k);
    }
};


