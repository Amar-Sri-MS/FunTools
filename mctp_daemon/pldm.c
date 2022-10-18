/*
 *      MCTP Daemon - FC pldm implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <stdlib.h>

#include "utils.h"
#include "pldm.h"
#include "pldm_mcd.h"

#ifdef CONFIG_INCLUDE_PLDM_PMC
#include "pldm_pmc.h"
#endif

#ifdef CONFIG_INCLUDE_PLDM_FRU
#include "pldm_fru.h"
#endif

#define MAX_NUMBER_OF_TYPE		3

// local vars
static uint8_t pktbuf[256];
struct pldm_global_stc pldm_vars = { 0 };

struct pldm_type_hdlr_stc {
	uint8_t type;
	pldm_cmd_hdlr_stct *ptr;
};

static struct pldm_type_hdlr_stc pldm_type_hdlrs[MAX_NUMBER_OF_TYPE];
static int hdlr_cnt = 0;

int register_pldm_handler(uint8_t type, pldm_cmd_hdlr_stct *ptr)
{
	if (hdlr_cnt == MAX_NUMBER_OF_TYPE) {
		pldm_err("Cannot register pldm type %u (max. number of handler reached)\n", type);
		return -1;
	}

	pldm_type_hdlrs[hdlr_cnt].type = type;
	pldm_type_hdlrs[hdlr_cnt].ptr = ptr;
	hdlr_cnt++;

	return 0;
}

/* set bit on an array of bit_arr_t */
void set_bit(uint32_t n, bit_arr_t *p)
{
	uint32_t m = (n / ARR_WIDTH);

	p[m] |= (1 << (n % ARR_WIDTH));
}

int pldm_response(pldm_hdr_stct *resp, uint8_t comp_code)
{
	resp->drq_inst = 0;

	/* set complition code */
	resp->data[0] = comp_code;
	return 0;
}

#define HDR_VER		((pldm_hdr->type_ver >> 6) & 0x3)
#define HDR_TYPE	((pldm_hdr->type_ver >> 0) & 0x3f)
#define HDR_DRQ		((pldm_hdr->drq_inst >> 6) & 0x3)
static pldm_cmd_hdlr_stct *search_handler(pldm_hdr_stct *pldm_hdr)
{
        pldm_cmd_hdlr_stct *ptr = NULL;

	for(int i = 0; i < hdlr_cnt; i++) {
		if (pldm_type_hdlrs[i].type == HDR_TYPE) {
			ptr = pldm_type_hdlrs[i].ptr;
			break;
		}
	}

	if (!ptr)
		return NULL;	

        for(; ptr->hdlr ; ptr++) {
                if (ptr->cmd == pldm_hdr->cmd) 
                        return ptr;
        }

        return NULL;
}

int pldm_handler(uint8_t *buf, int len, uint8_t *pbuf)
{
	pldm_hdr_stct *pldm_hdr = (pldm_hdr_stct *)buf;
	pldm_hdr_stct *resp;
	pldm_cmd_hdlr_stct *ptr;
	int rc = 1, ack_pending = (pldm_vars.flags & MCTP_VDM_ASYNC_ACK);

	resp = (!pbuf) ? (pldm_hdr_stct *)pktbuf : (pldm_hdr_stct *)pbuf;

	if (HDR_VER != PLDM_HEADER_VERSION) {
		pldm_err("bad PLDM ver %x\n", HDR_VER);
		pldm_response(resp, PLDM_INVALID_VERSION);
		goto exit;
	}

	if (HDR_DRQ != PLDM_REQ_DATA) {
		if (!(ack_pending)) {
			pldm_err("unsupported req. %x\n", HDR_DRQ);
			pldm_response(resp, PLDM_ERROR);
			goto exit;
		}

		if (pldm_hdr->cmd != PLDM_SUCCESS)
			pldm_err("ack err code = %u\n", pldm_hdr->cmd);

		pldm_vars.flags |= MCTP_VDM_ASYNC_ACK;
		return -1;
	}

	ptr = search_handler(pldm_hdr);
	if (ptr == NULL) {
		pldm_err("handler !found type = %x, cmd = %x\n", HDR_TYPE, pldm_hdr->cmd);
		pldm_response(resp, PLDM_UNSUPPORTED);
		goto exit;
	}

	/* preserve received pldm header */
	memcpy((uint8_t *)resp, (uint8_t *)pldm_hdr, sizeof(pldm_hdr_stct));

	len -= sizeof(pldm_hdr_stct);
	if (!(flags & FLAGS_NO_PLDM_LEN_CHECK)) {
		if (ptr->len != len) {
			pldm_err("invalid length = %x (%x)\n", len, ptr->len);
			pldm_response(resp, PLDM_INVALID_LENGTH);
			goto exit;
		}
	}

	rc = ptr->hdlr(pldm_hdr, resp);
	if (rc < 0) {
		pldm_err("handler rc = %x\n", rc);
		return -1;
	}

exit:
	rc += sizeof(pldm_hdr_stct);

	return rc;
}

int pldm_init(void)
{
	pldm_vars.flags |= MCTP_VDM_ASYNC_ACK;

	if (pldm_mcd_init())
		return -1;

#ifdef CONFIG_INCLUDE_PLDM_PMC
	if (pldm_pmc_init())
		return -1;
#endif

#ifdef CONFIG_INCLUDE_PLDM_FRU
	if (pldm_fru_init())
		return -1;
#endif

	return 0;
}
