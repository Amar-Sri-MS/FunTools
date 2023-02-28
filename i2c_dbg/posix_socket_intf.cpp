// posix_i2c_intf.cpp
//
// Implementation of i2c_master_read and i2c_master_write simulation
// over a unix socket
// Copyright (c) 2023, Microsoft.
// All Rights Reserved

#include "shared_defs.hpp"

#include <cstdint>
#include <cerrno>
#include <cstring>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>


static int _get_socket(const char *device)
{
	static int s = -1;
	if (s == -1) {
		struct sockaddr_un addr = {};
		addr.sun_family = AF_UNIX;
		s = socket(AF_UNIX, SOCK_STREAM|SOCK_CLOEXEC, 0);
		if (s < 0)
			return s;

		strncpy(addr.sun_path, device, sizeof(addr.sun_path) - 1);
		int r = connect(s, (const struct sockaddr *) &addr,
						sizeof(addr));
		if (r < 0) {
			close(s);
			s = -1;
		}
	}
	return s;
}

extern "C" int i2c_master_read(const char *device, int addr,
		    unsigned char* buff, int buff_len)
{
	int fd = _get_socket(device);
	int ret = -1;
	if (fd > 0) {
		ret = read(fd, buff, buff_len);
	}
	return ret;
}

extern "C" int i2c_master_write(const char *device, int addr,
		     unsigned char* buff, int buff_len)
{
	int fd = _get_socket(device);
	int ret = -1;
	if (fd > 0) {
		ret = write(fd, buff, buff_len);
	}
	return ret;
}
