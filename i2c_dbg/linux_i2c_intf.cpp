// common_i2c_intf.cpp
//
// Implementation of i2c_master_read and i2c_master_write for  Linux like
// Copyright (c) 2022 Fungible,Inc.
// All Rights Reserved

#include "shared_defs.hpp"

#include <cstdint>
#include <cerrno>
#include <cstring>

#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>


static int open_i2c_dev(const char *device_name)
{
	int fd = open(device_name, O_RDWR);

	if (fd < 0)
	{
		log("Error: unable to open dev bus %s", device_name);
		return fd;
	}

	unsigned long funcs;
	if (ioctl(fd, I2C_FUNCS, &funcs) < 0)
	{
		log("Error: Could not get the adapter type: %s",
		     strerror(errno));
		return -1;
	}

	if (!(funcs & I2C_FUNC_I2C))
	{
		log("Error: not an I2C device: %s", device_name);
		return -1;
	}

	return fd;
}

static int i2c_readwrite(const char *device_name, int port, int read,
		  unsigned char* flit_buffer, int len)
{
	int fd = open_i2c_dev(device_name);

	if (fd < 0)
	{
		return -1;
	}

	uint16_t flags = read ? I2C_M_RD : 0;

	struct i2c_msg msg;
	msg.flags = read ? I2C_M_RD : 0;
	msg.addr = port;
	msg.len = len;
	msg.buf = flit_buffer;

	struct i2c_rdwr_ioctl_data rdwr;
	rdwr.msgs = &msg;
	rdwr.nmsgs = 1;

	int nmsgs_sent = ioctl(fd, I2C_RDWR, &rdwr);
	if (nmsgs_sent < 0)
	{
		log("Error: Sending i2c messages: %s",
		    strerror(errno));
		return -1;
	}
        close(fd);

	// return number read/write
	return msg.len;

}

extern "C" int i2c_master_read(const char *device, int port,
		    unsigned char* buff, int buff_len)
{
	return i2c_readwrite(device, port, 1, buff, buff_len);
}

extern "C" int i2c_master_write(const char *device, int port,
		     unsigned char* buff, int buff_len)
{
	return i2c_readwrite(device, port, 0, buff, buff_len);
}
