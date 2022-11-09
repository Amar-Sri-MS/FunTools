//
//  shared_defs.hpp
//
//  Copyright (c) 2022 Fungible,Inc.
// All Rights Reserved

#ifndef shared_defs_hpp
#define shared_defs_hpp

#include <stdexcept>
#include <string>
#include <vector>
#include <memory>

/* shared definitions */
typedef std::vector<unsigned char> byte_vector;

class i2c_error : public std::runtime_error {

public:
	i2c_error(const std::string& err): runtime_error(err) {}
};


/* utilities */
std::string string_format(const char* format, ...);


void hex_dumpv(const unsigned char *bv, size_t len, const char* fmt, va_list args);
void hex_dump(const unsigned char *bv, size_t len, const char* fmt, ...);
void hex_dump(const byte_vector& bv, const char *fmt, ...);
void log(const char *fmt, ...);

#endif /* shared_defs_hpp */
