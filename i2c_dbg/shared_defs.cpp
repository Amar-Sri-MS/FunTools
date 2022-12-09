//
//  shared_defs.cpp
//
//  Copyright (c) 2021 Fungible,Inc.
// All Rights Reserved

#include "shared_defs.hpp"

#include "i2c_chal.hpp"

#include <cstdarg>

static int debug_on;

void debugging_on(int on)
{
	debug_on = on;
}

struct auto_free_cstr
{
	auto_free_cstr(char *d=0) : p{d} {}
	~auto_free_cstr() { free(p); }
	char *p;
};


std::string string_format(const char* format, ...)
{
	auto_free_cstr buff;
	va_list args;
	int n;

        va_start(args, format);
	n = vasprintf(&buff.p, format, args);
	va_end(args);
	if (n < 0)
	{
		throw std::runtime_error("vasprintf error");
	}
	return std::string(buff.p);
}


void hex_dumpv(const unsigned char *bv, size_t len, const char* fmt, va_list args)
{
	fflush(stdout);
	vprintf(fmt, args);
	if (len && bv)
	{
		printf(": ");
		for (int i = 0; i < len; ++i)
		{
			printf("%02x:", bv[i]);
		}
	}
	printf("\n");
	fflush(stdout);
}

void hex_dump(const unsigned char *bv, size_t len, const char* fmt, ...)
{
	if (debug_on)
	{
		va_list args;
		va_start(args, fmt);
		hex_dumpv(bv, len, fmt, args);
		va_end(args);
	}
}

void hex_dump(const byte_vector& bv, const char *fmt, ...)
{
	if (debug_on)
	{
		va_list args;
		va_start(args, fmt);
		hex_dumpv(bv.data(), bv.size(), fmt, args);
		va_end(args);
	}
}

void log(const char *fmt, ...)
{
	if (debug_on)
	{
		va_list args;
		va_start(args, fmt);
		hex_dumpv(NULL, 0, fmt, args);
		va_end(args);
	}
}
