// i2c_chal.cpp
//
//  Copyright (c) 2021 Fungible,Inc.
// All Rights Reserved

#include "i2c_chal.hpp"
#include "shared_defs.hpp"

#include <cassert>
#include <cstring>
#include <cstdint>
#include <ctime>
#include <cstdio>
#include <cstdarg>
#include <cerrno>
#include <endian.h>

/*
  cross compiling on Ubuntu 20.04 should work.
   However, Ubunut 22.04 uses a later GLIBC and cross-compiling
   will not work on the default build system
*/

#if defined(MAX_GLIBC_MINOR) && __GLIBC_MINOR__ > MAX_GLIBC_MINOR
#error Compiler using too new a version of GLIBC: will not run on target
#error Please build on another host
#endif

#if RASPBERRY
#define CHIP_DEVICE_0 "/dev/i2c-1"
#define CHIP_DEVICE_1 "/dev/i2c-1"
#else
#define CHIP_DEVICE_0 "/dev/i2c3"
#define CHIP_DEVICE_1 "/dev/i2c5"
#endif

using std::min;

#define  CHAL_HEADER_SIZE (4)
#define  MAX_FLIT_SIZE  (64)

void socket_reset(void);

std::string m_devices_for_chip[2] = { CHIP_DEVICE_0, CHIP_DEVICE_1};

void set_device(int chip_instance, const char *device)
{
	m_devices_for_chip[chip_instance? 1:0] = device;
#ifdef USE_POSIX_SOCKET
	socket_reset();
#endif
}

const char *get_device(int chip_instance)
{
	return m_devices_for_chip[chip_instance? 1 : 0].c_str();
}


// ***** i2c functions -- implemented in libi2c.so for FS1600
extern "C" {
int i2c_master_read(const char *device, int addr,
		    unsigned char* buff, int buff_len);
int i2c_master_write(const char *device, int addr,
		     unsigned char* buff, int buff_len);
}


static int i2c_read(int chip_instance, unsigned char* flit_buffer, int len)
{
	log("Reading %d bytes\n", len);

	int read_bytes = i2c_master_read(get_device(chip_instance),
					 0x70, flit_buffer, len);
	if (read_bytes <= 0) {
		throw i2c_error(string_format("Error %d (reading %d bytes)",
					      read_bytes, len));
	}
	hex_dump(flit_buffer, read_bytes, "read %d bytes", read_bytes);
	return read_bytes;
}

static void i2c_write(int chip_instance, unsigned char *buff, int len)
{
	hex_dump(buff, len, "Writing %d bytes", len);

	int wrote_bytes = i2c_master_write(get_device(chip_instance),
					   0x70, buff, len);
	if (wrote_bytes < 0) {
		throw i2c_error(string_format("Error %d (writing %d bytes)",
					      wrote_bytes, len));
	}
	log("Wrote %d bytes\n", wrote_bytes);
}

static int i2c_dbg_chal_read_flit(int chip_instance,
				  unsigned char *flit_data,
				  unsigned char len)
{
	assert(len <= MAX_FLIT_SIZE);
	++len;

	unsigned char cmd_byte = (0x40 | len);

	i2c_write(chip_instance, &cmd_byte, 1);

	int read_bytes = i2c_read(chip_instance, flit_data, len);

	unsigned char status_byte = flit_data[0];
	if (status_byte >> 7) {
		std::string err_msg = string_format("Command Execution Error: 0x%02x",
						    status_byte);
		if ((status_byte >> 6) == 0x3) {
			err_msg += " *** invalid shim action state ***";
		}

		throw i2c_error(err_msg);
	}
	flit_data[0] &= 0x7F; /* length prefix */
	return read_bytes;
}


static int i2c_dbg_chal_peek_read_len(int chip_instance)
{
	unsigned char flit_data[MAX_FLIT_SIZE+1];

	i2c_dbg_chal_read_flit(chip_instance, flit_data, 0);
	return flit_data[0];
}


static byte_vector i2c_dbg_chal_read(int chip_instance, int num_bytes)
{
	log("chal_read: read %d bytes (0x%08x)\n", num_bytes, num_bytes);

	byte_vector data;
	int read = 0;
	int try_count = 0;

	unsigned char flit_data[MAX_FLIT_SIZE+1];

	while (read < num_bytes) {
		int flit_size = num_bytes - read;

#ifdef USE_POSIX_SOCKET
		/*
		 * When using a socket, we must properly indicate number
		 * of bytes requested in the read cmd byte. If the requested number
		 * is 64 or 65, then the actual number is lost due to overlapping
		 * with the command bit. This number is probably ignored by real
		 * HW, but then data is clocked out on i2c master's clock, but
		 * with a socket interface we have no simple way of telling the device
		 * how many bytes to return, so ensure that a valid number is
		 * always requested
		 */
#define FLIT_SIZE_ADJUST (4)
#else
#define FLIT_SIZE_ADJUST (0)
#endif

		if (flit_size >= MAX_FLIT_SIZE) {
			flit_size = MAX_FLIT_SIZE - FLIT_SIZE_ADJUST;
		}

		int flit_read = i2c_dbg_chal_read_flit(chip_instance,
						       flit_data,
						       flit_size);
		if (flit_read > 1) {
			try_count = 0;
			read += flit_read-1;
			data.insert(data.end(),
				    flit_data + 1,
				    flit_data + flit_read);

		} else {
			if (++try_count > 10) {
				throw i2c_error(string_format("Timeout reading %d bytes after %d bytes read",
							      num_bytes, read));
			}
		}
	}
	hex_dump(data, "Successfully received %d bytes!", data.size());
	return data;
}


static bool i2c_dbg_chal_fifo_flush(int chip_instance)
{
	log("Flushing the FIFO\n");

	int flushed = 0;
	while (!flushed) {
		try {
			int len = i2c_dbg_chal_peek_read_len(chip_instance);
			if (len > 0) {
				i2c_dbg_chal_read(chip_instance, len);
			} else if (len == 0) {
				flushed = 1;
			}
		}
		catch (...) {
			return false;
		}
	}
	log("Flushed the FIFO\n");
	return true;
}


static byte_vector i2c_dbg_chal_cmd_header_read(int chip_instance)
{
	log("Read command status header\n");
	int len = i2c_dbg_chal_peek_read_len(chip_instance);
	if (len < 4 || len > MAX_FLIT_SIZE) {
		throw i2c_error(string_format("Unable to read header: got %d (not in 4-64 range)",
					      len));
	}
	return i2c_dbg_chal_read(chip_instance, CHAL_HEADER_SIZE);
}

byte_vector i2c_dbg_chal_cmd(uint32_t command, int chip_instance,
			     const void *data, int data_len,
			     int reply_delay_usec)
{

	/* Flush */
	i2c_dbg_chal_fifo_flush(chip_instance);

	log("challenge cmd: 0x%08x\n", command);
	hex_dump((const unsigned char *) data, data_len, "challenge data:");
	/* Send command */
	uint32_t cmd_buffer[3];
	uint8_t *to_send = ((uint8_t *) cmd_buffer) + 3;
	int to_send_len = (int) sizeof(cmd_buffer) - 3;
	uint32_t size = data_len + 4 + 4;

	*to_send = 0xC8;
	cmd_buffer[1] = htole32(size);
	cmd_buffer[2] = htole32(command);

	hex_dump(to_send, to_send_len, "Send dbg chal cmd");

	i2c_write(chip_instance, to_send, to_send_len);

	unsigned char flit_data[MAX_FLIT_SIZE+1];

	int sent = 0;
	while (sent < data_len) {

		int flit_size = data_len - sent;

		if (flit_size > MAX_FLIT_SIZE) {
			flit_size = MAX_FLIT_SIZE;
		}
		flit_data[0] = 0x80 + (flit_size & 0x3F);
		memcpy(flit_data+1, ((uint8_t *)data) + sent, flit_size);
		i2c_write(chip_instance, flit_data, flit_size+1);
		sent += flit_size;
	}

	log("Send %d bytes\n", data_len);

	/* Wait for reply */
	if (reply_delay_usec) {
		struct timespec reqt;
		reqt.tv_sec = 0;
		reqt.tv_nsec = reply_delay_usec * 1000;
		nanosleep(&reqt, NULL);
	}

	/* Read reply */

	byte_vector header = i2c_dbg_chal_cmd_header_read(chip_instance);
	if (header.size() != CHAL_HEADER_SIZE) {
		throw i2c_error(string_format("Command 0x%08X reply: invalid challenge header length: %d",
					      command, header.size()));
	}
	hex_dump(header, "header");
	/* header is little endian and length is encoded in 2 first byte */
	int reply_length = header[0] + (header[1] << 8) - CHAL_HEADER_SIZE;

	if (reply_length > 0) {
		byte_vector rdata = i2c_dbg_chal_read(chip_instance,
						      reply_length);
		header.insert(header.end(), rdata.begin(), rdata.end());
	}
	return header;
}


const unsigned char *i2c_dbg_chal_cmd(uint32_t command,
				      int chip_instance,
				      const unsigned char *data,
				      int data_len,
				      int reply_delay_usec,
				      int *result_len)
{
	static byte_vector reply;
	*result_len = 0;
	const unsigned char *ret = 0;
	try
	{
		reply = i2c_dbg_chal_cmd(command, chip_instance,
					 data, data_len, reply_delay_usec);
		*result_len = (int) reply.size();
		ret = reply.data();
	}
	catch (std::runtime_error& rex)
	{
		printf("Error %s\n", rex.what());
	}
	catch (...)
	{
		printf("Unknown exception\n");
	}
	return ret;
}


//******* challenge function sppecialization
enum
{
	FLASH_ERASE_SECTION = 0xFC000000,
	FLASH_WRITE_BUFF_SIZE =  0xFC010000 | 0x00001000,
	FLASH_WRITE_ADD_DATA =   0xFC010000 | 0x00002000,
	FLASH_WRITE_CLEAR_DATA = 0xFC010000 | 0x00003000,
	FLASH_WRITE_FLUSH_DATA = 0xFC010000 | 0x00004000,

	FLASH_READ_BUFF_SIZE =   0xFC020000 | 0x00001000,
	FLASH_READ_DATA =        0xFC020000 | 0x00002000, // FLASH_READ | CMD_BUFFER_DATA

	QSPI_PAGE_SIZE = 0x100,
	QSPI_SECTOR_SIZE = 0x10000,
	FLASH_SIZE = 0x1000000,    // 16 MB
};

class challenge_error : public std::runtime_error {
public:
	challenge_error(const std::string& err, int err_code):
		runtime_error(err), _err_code(err_code) {}

	int err_code(void) { return _err_code; }
private:
	int _err_code;
};

void check_challenge_error(const byte_vector &challenge_response,
			   uint32_t command)
{
	static std::string err_code_str[] =
	{
		"OK",
		"Invalid Command",
		"Authorization Error",
		"Invalid Signature",
		"Bus Error",
		"Reserved",
		"Crypto Error",
		"Invalid Parameter"
	};

	unsigned char err_code = challenge_response[2];
	if (err_code > 0)
	{
		std::string prefix = string_format("Command 0x%08x:", command);

		if (err_code < sizeof(err_code_str)/sizeof(err_code_str[0]))
		{
			throw challenge_error(prefix + err_code_str[err_code],
					      err_code);
		}

		throw challenge_error(prefix + string_format("Error code: %d\n",
							     err_code),
				      err_code);
	}
}

byte_vector i2c_dbg_chal_cmd_int(uint32_t command,
					  int chip_instance,
					  const void *data = NULL,
					  int data_len = 0,
					  int reply_delay_usec = 0)
{
	byte_vector reply = i2c_dbg_chal_cmd(command, chip_instance,
						    data, data_len,
						    reply_delay_usec);
	check_challenge_error(reply, command);

	return reply;
}


void get_write_buffer_size(int chip_instance,
			   uint32_t *page_size,
			   uint32_t *wr_buffer_size)
{
	byte_vector reply = i2c_dbg_chal_cmd_int(FLASH_WRITE_BUFF_SIZE,
						 chip_instance);
	uint32_t *data32 = (uint32_t *) reply.data();

	*page_size = le32toh(data32[1]);
	*wr_buffer_size = le32toh(data32[2]);
}

void i2c_dbg_write_flash_aux(int chip_instance, uint32_t offset,
			     const unsigned char *data, uint32_t data_length)
{
	uint32_t page_size, write_buffer_size, buffer_load_size;
	/* at most 256 bytes (QSPI_PAGE_SIZE) can be written at once */
	static uint32_t add_data_params[2 +
					((QSPI_PAGE_SIZE+sizeof(uint32_t)-1)/
					 sizeof(uint32_t))];
	uint8_t *dest = (uint8_t *) (add_data_params + 2);

	get_write_buffer_size(chip_instance, &page_size, &write_buffer_size);

	buffer_load_size = min(page_size, write_buffer_size);

	/* clear the write buffer only at start -- done automatically after
	 * a write operation afterwards
	 */
	i2c_dbg_chal_cmd_int(FLASH_WRITE_CLEAR_DATA, chip_instance);

	while (data_length)
	{
		uint32_t page_data_size;

		/* page_data_size <= page_size and <= data_length*/
		page_data_size = min(page_size, data_length);

		uint32_t offset_in_page = 0;

		while (offset_in_page < page_data_size)
		{
			/* load_size <= page_data_size so <= data_length */
			uint32_t load_size = min(buffer_load_size,
						 page_data_size);

			add_data_params[0] = htole32(offset_in_page);
			add_data_params[1] = htole32(load_size);

			/* add data to buffer */
			memcpy(dest, data, load_size);
			data += load_size;
			data_length -= load_size;

			i2c_dbg_chal_cmd_int(FLASH_WRITE_ADD_DATA,
					     chip_instance,
					     add_data_params,
					     2 * sizeof(uint32_t) + load_size,
					     1);
			offset_in_page += load_size;
		}

		// buffer data is loaded -- write it to flash
		uint32_t cmd_params = htole32(offset);
		i2c_dbg_chal_cmd_int(FLASH_WRITE_FLUSH_DATA,
				     chip_instance,
				     &cmd_params,
				     sizeof(cmd_params),
				     1);
		offset += page_size;
	}
}


int i2c_dbg_write_flash(int chip_instance, int offset,
			const unsigned char *data, int data_length)
{
	int ret = EIO;
	try
	{
		i2c_dbg_write_flash_aux(chip_instance, offset,
					data, data_length);
		ret = 0;
	}
	catch (challenge_error& cex)
	{
		ret = cex.err_code();
		printf("Challenge error: %s\n", cex.what());
	}
	catch (std::runtime_error& rex)
	{
		printf("Error %s\n", rex.what());
	}
	catch (...)
	{
		printf("Unknown exception\n");
	}
	return ret;
}

void i2c_dbg_read_flash_aux(int chip_instance, uint32_t addr,
			    unsigned char *data, uint32_t size)
{
	uint32_t read_params[2];
	uint32_t num_read = 0;
	byte_vector reply;
	while (num_read < size)
	{
		/* read QSPI_PAGE_SIZE at a time */
		uint32_t to_read = min((uint32_t) QSPI_PAGE_SIZE,
				       size - num_read);
		read_params[0] = htole32(addr);
		read_params[1] = htole32(to_read);
		reply = i2c_dbg_chal_cmd_int(FLASH_READ_DATA,
						 chip_instance,
						 &read_params,
						 sizeof(read_params));
		memcpy(data + num_read, reply.data()+sizeof(uint32_t), to_read);
		num_read += to_read;
		addr += to_read;
	}
}



const unsigned char *i2c_dbg_read_flash_ex(int chip_instance, int offset,
					   int data_len, int *err_code)
{
	static byte_vector reply;
	unsigned char *read_bytes = 0;
	*err_code = EIO;
	try
	{
		reply.resize(data_len);
		i2c_dbg_read_flash_aux(chip_instance, offset,
				       reply.data(), data_len);
		read_bytes = reply.data();
		*err_code = 0;
	}
	catch (challenge_error& cex)
	{
		*err_code = cex.err_code();
		printf("Challenge error: %s\n", cex.what());
	}
	catch (std::runtime_error& rex)
	{
		printf("Error %s\n", rex.what());
	}
	catch (...)
	{
		printf("Unknown exception\n");
	}
	return read_bytes;
}

const unsigned char *i2c_dbg_read_flash(int chip_instance, int offset,
					int data_len)
{
	int err_code;
	return i2c_dbg_read_flash_ex(chip_instance,
				     offset,
				     data_len,
				     &err_code);
}
