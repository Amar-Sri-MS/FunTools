/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PLDM_FRU_HDR_
#define _INC_PLDM_FRU_HDR_

#include <stdint.h>

#define PLDM_FRU_VERSION	0xf1f0f100

struct fru_commom_hdr_stc {
	uint8_t version;
	uint8_t int_use_offset;
	uint8_t chassis_info_offset;
	uint8_t board_area_offset;
	uint8_t product_info_offset;
	uint8_t mult_record_offset;
	uint8_t pad;
	uint8_t chksum;
	uint8_t data[0];
} __attribute__((packed));

struct chassis_info_hdr_stc {
	uint8_t version;
	uint8_t length;
	uint8_t type;
	uint8_t data[0];
} __attribute__((packed));

struct board_info_hdr_stc {
	uint8_t version;
	uint8_t length;
	uint8_t language;
	uint8_t time_stamp[3];
	uint8_t data[0];
} __attribute__((packed));

// DSP257 table 5
#define PLDM_FRU_GENERAL_TYPE_CHASSIS		1
#define PLDM_FRU_GENERAL_TYPE_MODEL		2
#define PLDM_FRU_GENERAL_TYPE_PART_NUM		3
#define PLDM_FRU_GENERAL_TYPE_SERIAL_NUM	4
#define PLDM_FRU_GENERAL_TYPE_MANUFACTURER	5
#define PLDM_FRU_GENERAL_TYPE_MANUFACTOR_DATE	6
#define PLDM_FRU_GENERAL_TYPE_VENDOR		7
#define PLDM_FRU_GENERAL_TYPE_NAME		8
#define PLDM_FRU_GENERAL_TYPE_SKU		9
#define PLDM_FRU_GENERAL_TYPE_VERSION		10
#define PLDM_FRU_GENERAL_TYPE_ASSET_TAG		11
#define PLDM_FRU_GENERAL_TYPE_DESCRIPTION	12
#define PLDM_FRU_GENERAL_TYPE_ECL		13
#define PLDM_FRU_GENERAL_TYPE_OTHER		14
#define PLDM_FRU_GENERAL_TYPE_IANA		15

// DSP257 table 6
#define PLDM_FRU_OEM_IANA			1
#define PLDM_FRU_OEM_SPECIFIC			254
struct fru_tlv_stc {
#ifndef ARCH_BIG_ENDIAN
	uint8_t len:6, type:2;
#else
	uint8_t type:2, len:6;
#endif
	uint8_t data[0];
} __attribute__((packed));

// DSP257 table 4
#define PLDM_FRU_TYPE_GENERAL_RECORD		1
#define PLDM_FRU_TYPE_OEM_RECORD		254

// DSP256 table 2
#define PLDM_FRU_ENCODING_ASCII			1
#define PLDM_FRU_ENCODING_UTF8			2
#define PLDM_FRU_ENCODING_UTF16			3
#define PLDM_FRU_ENCODING_UTF16_LE		4
#define PLDM_FRU_ENCODING_UTF16_BE		5
struct fru_data_record_stc {
	uint16_t identifier;
	uint8_t type;
	uint8_t fru_fields;
	uint8_t encoding;
	uint8_t data[0];
} __attribute__((packed));

struct fru_meta_stc {
	struct fru_data_record_stc *record;
};

struct pldm_get_meta_rsp_stc {
	uint8_t cmp_code;
        uint8_t ver_maj;
        uint8_t ver_min;
        uint32_t set_max_size;
        uint32_t fru_length;
        uint16_t record_sets;
        uint16_t total_records;
        uint32_t crc;
} __attribute__((packed));

struct pldm_get_rec_req_hdr_stc {
	uint8_t cmp_code;
        uint32_t handler;
        uint8_t flags;
} __attribute__((packed));

struct pldm_get_rec_rsp_stc {
        uint32_t next_handler;
        uint8_t flags;
        uint8_t data[0];
} __attribute__((packed));

#define PLDM_FRU_GET_RECORD_METADATA    0x01
#define PLDM_FRU_GET_RECORD_TABLE       0x02
#define PLDM_FRU_SET_RECORD_TABLE       0x03
#define PLDM_FRU_GET_RECORD_BT_OPTION   0x04

#define PLDM_GETFRU_FLAGS_GET_FIRST     1
#define PLDM_GETFRU_FLAGS_GET_NEXT      0

#define PLDM_GETFRU_RSPN_FLAGS_START    1
#define PLDM_GETFRU_RSPN_FLAGS_MIDDLE   2
#define PLDM_GETFRU_RSPN_FLAGS_END      4
#define PLDM_GETFRU_RSPN_FLAGS_SINGLE   5

void get_fru_supported_cmds(uint8_t *cmds);
int pldm_fru_init(void);

#endif /* _INC_PLDM_FRU_HDR_ */
