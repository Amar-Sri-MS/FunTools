//
//  i2c_chal.hpp
//
//  Copyright (c) 2021 Fungible,Inc.
// All Rights Reserved

#ifndef i2c_chal_hpp
#define i2c_chal_hpp

#include <cstdint>

#ifdef __cplusplus
extern "C"
{
#endif

void debugging_on(int on);

void set_device(int chip_instance, const char *device);
const char *get_device(int chip_instance);


const unsigned char *i2c_dbg_chal_cmd(uint32_t command,
				      int chip_instance,
				      const unsigned char *data,
				      int data_len,
				      int reply_delay_usec,
				      int *result_len);

int i2c_dbg_write_flash(int chip_instance, int offset,
			const unsigned char *data, int data_length);

const unsigned char *i2c_dbg_read_flash(int chip_instance, int offset,
					int data_length);

#ifdef __cplusplus
}
#endif


#endif /* i2c_chal_hpp */
