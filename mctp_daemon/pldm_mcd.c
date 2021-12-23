/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>
#include <strings.h>

#include "utils.h"
#include "pldm_mcd.h"

extern struct pldm_global_stc pldm_vars;

/* pldm mcd set tid handler */
static int pldm_set_tid(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_set_tid_req_stc *pldm = (struct pldm_set_tid_req_stc *)hdr->data;
	struct pldm_null_rspn_stc *rspn = (struct pldm_null_rspn_stc *)resp->data;

	if (pldm->tid == 0xff) {
		pldm_err("Invalid tid (%x)\n", pldm->tid);
		pldm_response(resp, PLDM_INVALID_DATA);
		return MIN_PLDM_PAYLOAD;
	}

	pldm_vars.tid = pldm->tid;

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm mcd get tid handler */
static int pldm_get_tid(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_tid_rspn_stc *rspn = (struct pldm_get_tid_rspn_stc *)resp->data;

	rspn->tid = pldm_vars.tid;

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm mcd get version handler */
static int pldm_get_ver(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_ver_req_stc *pldm = (struct pldm_get_ver_req_stc *)hdr->data;
	struct pldm_get_ver_rspn_stc *rspn = (struct pldm_get_ver_rspn_stc *)resp->data;
	struct pldm_version_stc *ver = (struct pldm_version_stc *)rspn->data;
	uint32_t crc = 0;
	int n = 1;

	/* support only GetFirstPart */
	if (pldm->flag != 0x01) {
		pldm_err("Invalid flag %x\n", pldm->flag);
		pldm_response(resp, PLDM_INVALID_OP_FLAG);
		return MIN_PLDM_PAYLOAD;
	}

	switch (pldm->type) {
	case PLDM_MCD_TYPE:
		ASSIGN32_LE(ver->ver, PLDM_MCD_VERSION);
		break;

	case PLDM_PMC_TYPE:
		ASSIGN32_LE(ver->ver, PLDM_PMC_VERSION);
		break;

	default:
		pldm_err("Invalid type %x\n", pldm->type);
		pldm_response(resp, PLDM_INVALID_TYPE_REQ);
		return MIN_PLDM_PAYLOAD;
	}

	ASSIGN32_LE(rspn->handle, 0);
	rspn->flag = START_TRANSFER | END_TRANSFER;

	crc = crc32(rspn->data, n*sizeof(uint32_t), 0);
	ASSIGN32_LE(ver->data, crc);

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE + n*sizeof(struct pldm_version_stc) + sizeof(uint32_t);
}

/* pldm mcd get supported types handler */
static int pldm_get_type(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_type_rspn_stc *rspn = (struct pldm_get_type_rspn_stc *)resp->data;

	memset(rspn->type , 0, sizeof(rspn->type));

	/* FIXME: can be optimized to fixed value if room is tight */
	set_bit(PLDM_MCD_TYPE, rspn->type);
	set_bit(PLDM_PMC_TYPE, rspn->type);

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm mcd get supported cmds handler */
static int pldm_get_cmds(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_cmds_req_stc *pldm = (struct pldm_cmds_req_stc *)hdr->data;
	struct pldm_cmds_rspn_stc *rspn = (struct pldm_cmds_rspn_stc *)resp->data;
	uint32_t ver;

	if (pldm->type != PLDM_MCD_TYPE && pldm->type != PLDM_PMC_TYPE) {
		pldm_err("bad pldm type %x\n", pldm->type);
		pldm_response(resp, PLDM_INVALID_TYPE_REQ);
		return COMP_CODE_ONLY;
	}

	ver = ALIGN32_BE(pldm->ver);

	switch (pldm->type) {
	case PLDM_MCD_TYPE:
		if (ver != PLDM_MCD_VERSION) {
			pldm_err("bad pldm version %x %x\n", ver, PLDM_MCD_VERSION);
			pldm_response(resp, PLDM_INVALID_VERSION);
			return COMP_CODE_ONLY;
		}

		/* Note: If additional MCD are added, make sure to add them here as well */
		set_bit(PLDM_MCD_SETTID, rspn->cmds);
		set_bit(PLDM_MCD_GETTID, rspn->cmds);
		set_bit(PLDM_MCD_GET_VERSION, rspn->cmds);
		set_bit(PLDM_MCD_GET_TYPE, rspn->cmds);
		set_bit(PLDM_MCD_GET_CMDS, rspn->cmds);
		break;

	case PLDM_PMC_TYPE:
		if (ver != PLDM_PMC_VERSION) {
			pldm_response(resp, PLDM_INVALID_VERSION);
			return COMP_CODE_ONLY;
		}

		/* Note: If additional PMC are added, make sure to add them here as well */
		set_bit(PLDM_PMC_SET_NUMERIC_SENSOR_ENABLE, rspn->cmds);
		set_bit(PLDM_PMC_GET_SENSOR_READING, rspn->cmds);
		set_bit(PLDM_PMC_GET_SENSOR_THRESHOLDS, rspn->cmds);
		set_bit(PLDM_PMC_GET_SENSOR_HYSTERESIS, rspn->cmds);
#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
		set_bit(PLDM_PMC_GET_STATES_SENSOR_READINGS, rspn->cmds);
#endif
		set_bit(PLDM_PMC_GET_PDR_REPOSITORY_INFO, rspn->cmds);
		set_bit(PLDM_PMC_GETPDR, rspn->cmds);
		break;
	}

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

pldm_cmd_hdlr_stct pldm_mcd_cmds[] = {
	{PLDM_MCD_SETTID, sizeof(struct pldm_set_tid_req_stc), pldm_set_tid},
	{PLDM_MCD_GETTID, 0, pldm_get_tid},
	{PLDM_MCD_GET_VERSION, sizeof(struct pldm_get_ver_req_stc), pldm_get_ver},
	{PLDM_MCD_GET_TYPE, 0, pldm_get_type},
	{PLDM_MCD_GET_CMDS, sizeof(struct pldm_cmds_req_stc), pldm_get_cmds},
	PLDM_LAST_CMD,
};
