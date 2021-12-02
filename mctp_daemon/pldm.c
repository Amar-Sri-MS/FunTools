/*
 *      MCTP Daemon - FC pldm implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>
#include <strings.h>

#include "utils.h"
#include "pldm.h"
#include "pldm_mcd.h"
#include "pldm_pmc.h"

// local vars
static uint8_t pktbuf[256];
struct pldm_global_stc pldm_vars;

static pldm_cmd_hdlr_stct *search_handler(pldm_hdr_stct *hdr)
{
        pldm_cmd_hdlr_stct *ptr= (pldm_cmd_hdlr_stct *)&__pldm_cmds_start;

        for(; ptr != (pldm_cmd_hdlr_stct *)&__pldm_cmds_end; ptr++) {
                if (ptr->type == hdr->type && ptr->cmd == hdr->cmd)
                        return ptr;
        }

        return NULL;
}

/* set bit on an array of bit_arr_t */
void set_bit(uint32_t n, bit_arr_t *p)
{
	uint32_t m = (n / ARR_WIDTH);

	p[m] |= (1 << (n % ARR_WIDTH));
}

int pldm_response(pldm_hdr_stct *resp, uint8_t comp_code)
{
	resp->drq = 0;
	resp->ver = 0;
	resp->rsrvd = 0;

	/* set complition code */
	resp->data[0] = comp_code;
	return 0;
}

int pldm_handler(uint8_t *buf, int len, uint8_t *pbuf)
{
	pldm_hdr_stct *pldm_hdr = (pldm_hdr_stct *)buf;
	pldm_hdr_stct *resp;
	pldm_cmd_hdlr_stct *ptr;
	int rc = 1;

	resp = (!pbuf) ? (pldm_hdr_stct *)pktbuf : (pldm_hdr_stct *)pbuf;

	if (pldm_hdr->ver != PLDM_HEADER_VERSION) {
		pldm_err("bad PLDM ver %x\n", pldm_hdr->ver);
		pldm_response(resp, PLDM_INVALID_VERSION);
		goto exit;
	}

	if (pldm_hdr->drq != PLDM_REQ_DATA) {
		pldm_err("unsupported req. %x\n", pldm_hdr->drq);
		pldm_response(resp, PLDM_ERROR);
		goto exit;
	}

	ptr = search_handler(pldm_hdr);
	if (ptr == NULL) {
		pldm_err("handler !found type = %x, cmd = %x\n", pldm_hdr->type, pldm_hdr->cmd);
		pldm_response(resp, PLDM_UNSUPPORTED);
		goto exit;
	}

	/* preserve received pldm header */
	memcpy((uint8_t *)resp, (uint8_t *)pldm_hdr, sizeof(pldm_hdr_stct));

	len -= sizeof(pldm_hdr_stct);
	if (ptr->len != len) {
		pldm_err("invalid length = %x (%x)\n", len, ptr->len);
		pldm_response(resp, PLDM_INVALID_LENGTH);
		goto exit;
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
	/* initilize global variables for the first time */
	bzero((uint8_t *)&pldm_vars, sizeof(struct pldm_global_stc));

#ifdef CONFIG_INCLUDE_PLDM_PMC
	if (pldm_pmc_init())
		return -1;
#endif

	return 0;
}
