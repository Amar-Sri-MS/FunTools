/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/mman.h>
#include <errno.h>

#include "utils.h"
#include "mctp.h"
#include "pldm.h"
#include "pldm_fru.h"

#define MAX_FRU_BUF_SIZE		(2 * 1024)
#define MAX_FRU_RECORDS			5

extern struct pldm_global_stc pldm_vars;

static struct fru_meta_stc fru_meta[MAX_FRU_RECORDS];
static uint8_t fru_buf[MAX_FRU_BUF_SIZE];
static int fru_rcrd_cnt = 0, fru_length = 0, total_records = 0;

/* helper function for parsing the fru data
 * This implementation supports Chassis info/Board area only*/

static int set_chassis_record(uint8_t *ptr, uint8_t **rcrd_ptr)
{
	struct chassis_info_hdr_stc *hdr = (struct chassis_info_hdr_stc *)ptr;
	struct fru_tlv_stc *tlv = (struct fru_tlv_stc *)hdr->data;
	struct fru_data_record_stc *record;
	uint8_t *dest;
	int len = 0;

	if (hdr->version != 1) {
		pldm_err("Bad Chassis Info version, ignoring\n");
		return -1;
	}

	record = fru_meta[fru_rcrd_cnt].record = (struct fru_data_record_stc *)(*rcrd_ptr);
	record->identifier = fru_rcrd_cnt;
	record->type = PLDM_FRU_TYPE_GENERAL_RECORD;
	record->fru_fields = 0;
	record->encoding = PLDM_FRU_ENCODING_ASCII;
	dest = record->data;

	do {
		record->fru_fields++;
		memcpy((char *)dest, (char *)tlv, sizeof(struct fru_tlv_stc) + tlv->len);
		dest += sizeof(struct fru_tlv_stc) + tlv->len;
		len += sizeof(struct fru_tlv_stc) + tlv->len;
		total_records++;

		// check if this is the last tlv
		if (tlv->type == 0x3 && tlv->len == 0x1)
			break;

		if (len >= (8 * hdr->length))
			break;

		tlv = (struct fru_tlv_stc *)&tlv->data[tlv->len];

	} while (1);

	fru_rcrd_cnt++;
	fru_length += (len + sizeof(struct fru_data_record_stc));
	*rcrd_ptr = dest;

	return 0;
}

static int set_board_record(uint8_t *ptr, uint8_t **rcrd_ptr)
{
	struct board_info_hdr_stc *hdr = (struct board_info_hdr_stc *)ptr;
	struct fru_tlv_stc *tlv = (struct fru_tlv_stc *)hdr->data;
	struct fru_data_record_stc *record;
	uint8_t *dest;
	int len = 0;

	if (hdr->version != 1) {
		pldm_err("Bad Board Info version, ignoring\n");
		return -1;
	}

	record = fru_meta[fru_rcrd_cnt].record = (struct fru_data_record_stc *)rcrd_ptr;
	record->identifier = fru_rcrd_cnt;
	record->type = PLDM_FRU_TYPE_GENERAL_RECORD;
	record->fru_fields = 0;
	record->encoding = PLDM_FRU_ENCODING_ASCII;
	dest = record->data;

	do {
		record->fru_fields++;
		memcpy((char *)dest, (char *)tlv, sizeof(struct fru_tlv_stc) + tlv->len);
		dest += sizeof(struct fru_tlv_stc) + tlv->len;
		len += sizeof(struct fru_tlv_stc) + tlv->len;
		total_records++;

		// check if this is the last tlv
		if (tlv->type == 0x3 && tlv->len == 0x1)
			break;

		if (len >= (8 * hdr->length))
			break;

		tlv = (struct fru_tlv_stc *)&tlv->data[tlv->len];

	} while (1);

	fru_rcrd_cnt++;
	fru_length += (len + sizeof(struct fru_data_record_stc));
	*rcrd_ptr = dest;

	return 0;
}

static int parse_fru_file()
{
	struct fru_commom_hdr_stc *hdr;
	uint8_t *ptr = NULL, *rcrd_ptr = &fru_buf[0];
	int rc = -1;
	uint8_t cksum = 0;
        struct stat sbuf;
	int fd;

        if (!(fd = open(cfg.fru_filename, O_RDONLY))) {
                pldm_err("Cannot open fru file %s\n", cfg.fru_filename);
		return -1;
        }

        if (fstat(fd, &sbuf)) {
                pldm_err("Cannot read %s status\n", cfg.fru_filename);
                goto exit;
        }

        ptr = (uint8_t *)mmap(0, sbuf.st_size, PROT_READ, MAP_SHARED, fd, 0);
        if (ptr == (uint8_t *)MAP_FAILED) {
                pldm_err("remap failed (%s)\n", strerror(errno));
                goto exit;
        }

	hdr = (struct fru_commom_hdr_stc *)ptr;

	for(int i = 0; i < 8; i++)
		cksum += ptr[i];

	if (cksum) {
		pldm_err("FRU header checksum failed (%x %x)\n", cksum, ptr[7]);
		goto exit;
	}

	if (hdr->version != 0x01 || hdr->pad) {
		pldm_err("Bad FRU header version/padding (%u %u)\n", hdr->version, hdr->pad);
		goto exit;
	}

	// for now, only chassis info is supported, however - the infrastructure is there
	// to suppoprt up to MAX_FRU_RECORDS records 
	if (hdr->chassis_info_offset) {
		if (set_chassis_record(&ptr[8 * hdr->chassis_info_offset], &rcrd_ptr))
			goto exit;

	}

	if (hdr->board_area_offset) {
		if (set_board_record(&ptr[8 * hdr->board_area_offset], &rcrd_ptr))
			goto exit;
	}


	rc = 0;

exit:
	if (ptr)
		munmap((void *)ptr, sbuf.st_size);

	close(fd);

	return rc;
}

/* pldm get fru meta */
static int pldm_get_fru_meta(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_meta_rsp_stc *rspn = (struct pldm_get_meta_rsp_stc *)resp->data;

	rspn->ver_maj = 0x01;
	rspn->ver_min = 0;
	rspn->set_max_size = 0;
	rspn->fru_length = fru_length;
	rspn->record_sets = fru_rcrd_cnt;
	rspn->total_records = total_records;
	rspn->crc = crc32(fru_buf, fru_length, -1);

	return PLDM_PAYLOAD_SIZE;
}

/* pldm get fru data */
static int pldm_get_fru_data(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_rec_req_hdr_stc *req = (struct pldm_get_rec_req_hdr_stc *)hdr->data;
	struct pldm_get_rec_rsp_stc *rspn = (struct pldm_get_rec_rsp_stc *)resp->data;
	int size;
	uint32_t index;

	index = (req->flags == PLDM_GETFRU_FLAGS_GET_FIRST) ? 0 : pldm2host(req->handler);

	// calculate max. payload
	size = MIN(PLDM_TX_BUFFER_SIZE, fru_length - index);
	rspn->next_handler = index + size;
	rspn->flags = (size <= fru_length && index == 0) ? PLDM_GETFRU_RSPN_FLAGS_SINGLE :
		      (size == PLDM_TX_BUFFER_SIZE) ? PLDM_GETFRU_RSPN_FLAGS_MIDDLE : PLDM_GETFRU_RSPN_FLAGS_END;

	memcpy((char *)rspn->data, (char *)&fru_buf[index], size);
	return PLDM_PAYLOAD_SIZE + size;
}

static pldm_cmd_hdlr_stct pldm_cmds[] = {
	{PLDM_FRU_GET_RECORD_METADATA, 0, pldm_get_fru_meta},
	{PLDM_FRU_GET_RECORD_TABLE, sizeof(struct pldm_get_rec_req_hdr_stc), pldm_get_fru_data},
	PLDM_LAST_CMD,
};

void get_fru_supported_cmds(uint8_t *cmds)
{
	set_bit(PLDM_FRU_GET_RECORD_METADATA, cmds);
	set_bit(PLDM_FRU_GET_RECORD_TABLE, cmds);
}

int pldm_fru_init(void)
{
	if (parse_fru_file()) {
		pldm_err("FRU parsing failed\n");
		return -1;
	}

	log_n_print("Total record sets: %u, table size: %u\n", fru_rcrd_cnt, fru_length);

        return register_pldm_handler(PLDM_FRU_TYPE, pldm_cmds);
}
