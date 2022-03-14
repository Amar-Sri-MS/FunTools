/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>

#include "utils.h"
#include "mctp.h"
#include "pldm.h"
#include "pldm_fru.h"

extern struct pldm_global_stc pldm_vars;

static struct fru_data_stc fru;

/* pldm get fru meta */
static int pldm_get_fru_meta(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_meta_rsp_stc *rspn = (struct pldm_get_meta_rsp_stc *)resp->data;

	rspn->ver_maj = 0x01;
	rspn->ver_min = 0;
	rspn->set_max_size = 0;
	rspn->fru_length = fru.meta.size;
	rspn->set_records = 0;
	rspn->total_records = fru.meta.records;

	memcpy((char *)rspn->data, (char *)fru.meta.ptr, fru.meta.size);

	return PLDM_PAYLOAD_SIZE + fru.meta.size;
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
	size = MIN(PLDM_TX_BUFFER_SIZE, fru.size - index);
	rspn->next_handler = index + size;
	rspn->flags = (size <= fru.size && index == 0) ? PLDM_GETFRU_RSPN_FLAGS_SINGLE :
		      (size == PLDM_TX_BUFFER_SIZE) ? PLDM_GETFRU_RSPN_FLAGS_MIDDLE : PLDM_GETFRU_RSPN_FLAGS_END;

	memcpy((char *)rspn->data, (char *)&fru.buf[index], size);
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
        return register_pldm_handler(PLDM_FRU_TYPE, pldm_cmds);
}
