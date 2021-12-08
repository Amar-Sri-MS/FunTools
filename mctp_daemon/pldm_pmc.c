/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>

#include "utils.h"
#include "pldm_pmc.h"
#include "pldm_repo.h"
#include "pdr.h"

#define VALID_SENSOR(id)						\
	do {								\
		int i;							\
		for(i = 0; i < num_of_sensors; i++) {			\
			if (sensor[i].id == id)	{			\
				id = i;					\
				break;					\
			}						\
		}							\
		if (i == num_of_sensors) {				\
			pldm_err("bad sensor id %x\n", id);		\
			pldm_response(resp, INVALID_SENSOR_ID);		\
			return COMP_CODE_ONLY;				\
		}							\
	} while (0)					

#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
static uint32_t pldm_state;
#endif

static uint8_t num_of_sensors;
static struct sensors_info sensor[NUMBER_OF_SENSORS];


/* helper function */
static void set_payload(pldm_hdr_stct *resp, struct pldm_get_pdr_rspn *rspn,
                        uint8_t *src, uint8_t rec, uint8_t flag, uint16_t len, uint32_t next)
{
	uint32_t tmp;

	memcpy(rspn->data, src, len);
	tmp = (rec == (num_of_sensors-1)) ? 0 : rec + 1;
	ASSIGN32_LE(rspn->next_rec, tmp);
	ASSIGN32_LE(rspn->next_data, next);
	rspn->flag = flag;
	ASSIGN16_LE(rspn->count, len);

	pldm_response(resp, PLDM_SUCCESS);
}

/* actual thermal sensor read */
int external_thermal_sensor_rd()
{
	return -1;
}

/* pldm pmc get repo info */
static int pldm_get_repo_info(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_repo_rspn *rspn = (struct pldm_get_repo_rspn *)resp->data;
	uint32_t size = 1023;
	int i;

	rspn->repo_state = AVAILABLE_REPO;

	ASSIGN16_LE(rspn->update_time.utc_offset, (2 * 60));
	ASSIGN32_LE(rspn->update_time.seconds, 0);
	rspn->update_time.minute = 2;
	rspn->update_time.hour = 10;
	rspn->update_time.day = 23;
	rspn->update_time.month = 2;
	ASSIGN16_LE(rspn->update_time.year, 2017);
	
	memcpy((uint8_t *)&rspn->oem_update_time, (uint8_t *)&rspn->update_time,sizeof(struct pldm_timestamp));
	ASSIGN32_LE(rspn->count, num_of_sensors);

	for (i = 0; i < num_of_sensors; i++)
		size += sensor[i].len;

	size &= 0xfffffc00;
	ASSIGN32_LE(rspn->repo_size, size);

	/* FIXME: for now, the numeric pdr is the largest.
	 * if new structure is to be designed, this may need to be changed
	 */
	size = (63 + sizeof(struct numeric_sensor_pdr)) & 0xffffffc0;
	ASSIGN32_LE(rspn->max_pdr_size, size);
	rspn->timeout = 0;

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm get pdr */
static int pldm_get_pdr(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_pdr_req *pldm = (struct pldm_get_pdr_req *)hdr->data;
	struct pldm_get_pdr_rspn *rspn = (struct pldm_get_pdr_rspn *)resp->data;
	struct pldm_common_pdr_hdr *pdrhdr;
	struct numeric_sensor_pdr *pdr;
	uint32_t size;
	uint8_t *ptr;
	uint32_t seq, rec;
	uint16_t cnt, chg;
	int i;

	rec = ALIGN32_BE(pldm->rec_handle);
	seq = ALIGN32_BE(pldm->data_seq);
	cnt = ALIGN16_BE(pldm->req_count);
	chg = ALIGN16_BE(pldm->chan_num);

	if (rec >= num_of_sensors) {
		pldm_err("bad record number %x\n", rec); 
		pldm_response(resp, INVALID_RECORD_HANDLE);
		return COMP_CODE_ONLY;
	}

	for(i = 0; i <num_of_sensors; i++) {
		if (sensor[i].rec == rec) 
			break;
	}

	if (i == num_of_sensors) {
                pldm_err("bad record number %x\n", rec);
                pldm_response(resp, INVALID_RECORD_HANDLE);
                return COMP_CODE_ONLY;
        }

	pdr = (struct numeric_sensor_pdr *)sensor[i].pdr;
	ptr = (uint8_t *)sensor[i].pdr;
	pdrhdr = (struct pldm_common_pdr_hdr *)&pdr->hdr;

	ptr += seq;
	size = MIN(PLDM_TX_BUFFER_SIZE, cnt);

	/* first chunk */
	if (pldm->flag) {
		if (seq) {
			pldm_err("first chunk - bad seq # %x\n", seq);
			pldm_response(resp, INVALID_DATA_TRANSFER_HANDLE);
			return 1;
		}

		if (chg) {
			pldm_err("first chunk - bad chg # %x\n", chg);
			pldm_response(resp, INVALID_RECORD_CHANGE_NUMBER);
			return 1;
		}

		/* first and last chunk? */
		if (sensor[i].len < size) {
			set_payload(resp, rspn, ptr, rec, 5, sensor[rec].len, 0);
			return PLDM_PAYLOAD_SIZE + sensor[rec].len;
		} else {
			set_payload(resp, rspn, ptr, rec, 0, size, size);
			return PLDM_PAYLOAD_SIZE + size;
		}
	}

	/* next chunk */
	if (seq >= sensor[i].len) {
		pldm_err("next chunk - bad seq # %x\n", seq);
		pldm_response(resp, INVALID_DATA_TRANSFER_HANDLE);
		return 1;
	}

	if (chg != pdrhdr->change) {
		pldm_err("next chunk - bad chk # %x\n", chg);
		pldm_response(resp, INVALID_RECORD_CHANGE_NUMBER);
		return 1;
	}

	/* last chunk? */
	if (sensor[i].len < (size + seq)) {
		set_payload(resp, rspn, ptr, rec, 4, (sensor[i].len - seq), (sensor[i].len - seq));
		return PLDM_PAYLOAD_SIZE + (sensor[i].len - seq);
	} else {
		/* middle  */
		set_payload(resp, rspn, ptr, rec, 1, size, (seq + size));
		return PLDM_PAYLOAD_SIZE + size;
	}

	return -1;
}

/* pldm pmc set numeric sensor enable */
static int pldm_set_sensor_en(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_set_num_sens_en_req *pldm = (struct pldm_set_num_sens_en_req *)hdr->data;
	struct pldm_null_rspn_stc *rspn = (struct pldm_null_rspn_stc *)resp->data;
	uint16_t id = ALIGN16_BE(pldm->id);

	VALID_SENSOR(id);
	sensor[id].state = (!pldm->state) ? PLDM_SENSOR_ENABLED : PLDM_SENSOR_DISABLED;
	sensor[id].event = (pldm->event) ? pldm->event : sensor[id].event;

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm pmc get numeric sensor reading */
static int pldm_get_sensor_rd(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_sens_rd_req *pldm = (struct pldm_get_sens_rd_req *)hdr->data;
	struct pldm_get_sens_rd_rspn *rspn = (struct pldm_get_sens_rd_rspn *)resp->data;
	struct numeric_sensor_pdr *pdr;
	uint32_t tmp = 0, warn, critic, fatal;
	uint8_t state;
	uint16_t id = ALIGN16_BE(pldm->id);

	VALID_SENSOR(id);

	if (pldm->rearm && (sensor[id].rearm == PLDM_REARM_DISABLED)) {
		pldm_err("rearm not supported\n");
		pldm_response(resp, REARM_UNAVAILABLE);
		return COMP_CODE_ONLY;
	}

	pdr = (struct numeric_sensor_pdr *)sensor[id].pdr;
	tmp = *((uint32_t *)sensor[id].read);

        if (sensor[id].scale == SCALE_ENABLED) 
		tmp = (sensor[id].op == DIVIDE_TO_SCALE) ? tmp / sensor[id].value : tmp * sensor[id].value;

	ASSIGN32_LE(rspn->data, tmp);

	rspn->data_size = pdr->data_size;

	/* if no temperature read is available - mark the sensor as disabled */
	rspn->state = (tmp == -1) ? PLDM_SENSOR_UNAVAILABLE : PLDM_SENSOR_ENABLED;
	rspn->event_ena = PLDM_EVENTS_STATE_ONLY;

	warn = ALIGN32_BE(pdr->warn_high);
	critic = ALIGN32_BE(pdr->critc_high);
	fatal = ALIGN32_BE(pdr->fatal_high);

	if (tmp == -1)
		state = PLDM_UNKNOWN_STATE;
	else state = (tmp < warn) ? PLDM_NORMAL_STATE : (tmp < critic) ? PLDM_WARNING_STATE : (tmp < fatal) ? PLDM_CRITICAL_STATE : PLDM_FATAL_STATE;

	rspn->c_state = state;

	rspn->p_state = sensor[id].state;
	rspn->e_state = state;

	/* set previous state and record current */
	sensor[id].state = state;

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm get sensor threshold */
static int pldm_get_sensor_th(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_sens_th_req *pldm = (struct pldm_get_sens_th_req *)hdr->data;
	struct pldm_get_sens_th_rspn *rspn = (struct pldm_get_sens_th_rspn *)resp->data;
	struct numeric_sensor_pdr *pdr;
	uint16_t id = ALIGN16_BE(pldm->id);

	VALID_SENSOR(id);
	pdr = (struct numeric_sensor_pdr *)sensor[id].pdr;

	rspn->data_size = pdr->data_size;

	memcpy((uint8_t *)&rspn->warn_high, (uint8_t *)&pdr->warn_high, 4);
	memcpy((uint8_t *)&rspn->crit_high, (uint8_t *)&pdr->critc_high, 4);
	memcpy((uint8_t *)&rspn->fatal_high, (uint8_t *)&pdr->fatal_high, 4);

	memcpy((uint8_t *)&rspn->warn_low, (uint8_t *)&pdr->warn_low, 4);
	memcpy((uint8_t *)&rspn->crit_low, (uint8_t *)&pdr->critc_low, 4);
	memcpy((uint8_t *)&rspn->fatal_low, (uint8_t *)&pdr->fatal_low, 4);

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm get sensor hysteresis */
#define SENSOR_HYSTERESIS_VALUE         5
static int pldm_get_sensor_hy(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_sens_th_req *pldm = (struct pldm_get_sens_th_req *)hdr->data;
	struct pldm_get_sens_hy_rspn *rspn = (struct pldm_get_sens_hy_rspn *)resp->data;
	struct numeric_sensor_pdr *pdr;
	uint16_t id = ALIGN16_BE(pldm->id);

	VALID_SENSOR(id);
	pdr = (struct numeric_sensor_pdr *)sensor[id].pdr;

	rspn->data_size = pdr->data_size;
	memcpy((uint8_t *)&rspn->val, (uint8_t *)&pdr->hysteresis, 4);

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm pmc get state sensor reading */
#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
static int pldm_get_state_rd(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_state_rd_req *pldm = (struct pldm_get_state_rd_req *)hdr->data;
	struct pldm_get_state_rd_rspn *rspn = (struct pldm_get_state_rd_rspn *)resp->data;
	struct state_fields *state = (struct state_fields *)rspn->data;
	struct state_pdr *pdr;
	uint16_t id = ALIGN16_BE(pldm->id);
	int8_t i;

	VALID_SENSOR(id);
	pdr = (struct numeric_sensor_pdr *)sensor[id].pdr;

	rspn->count = pdr->num_of_states;
	for(i=0; i<pdr->num_of_states; i++) {
		state->op_state = i;
		state->prsnt_state = i;
		state->prev_state = i;
		state->event_state = i;
		state = (struct state_fields *)state->data;
	}

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE + pdr->num_of_states*sizeof(struct state_fields);
}
#endif

#define WARNING_TEMP	((NVM_CFG(glob.led_global_settings) & NVM_CFG1_GLOB_MAX_CONT_OPERATING_TEMP_MASK) >> NVM_CFG1_GLOB_MAX_CONT_OPERATING_TEMP_OFFSET)
void update_repo(struct numeric_sensor_pdr *pdr, uint32_t mcot)
{
#ifdef b900
	if (mcot == 0)
		mcot = 100;
#endif
	ASSIGN32_LE(pdr->warn_high, mcot);

	ASSIGN32_LE(pdr->critc_high, (mcot + 10));
	ASSIGN32_LE(pdr->fatal_high, (mcot + 15));
	pdr->support_thold = PLDM_UPPER_WARNING_SUPPORT | PLDM_UPPER_CRITICAL_SUPPORT | PLDM_UPPER_FATAL_SUPPORT;

//	pdr->crc8 = (uint8_t)crc8((uint8_t *)pdr, sizeof(struct numeric_sensor_pdr) - 1);
}

#define ON_BOARD_INLET			0x1
#define ON_BOARD_OUTLET			0x2
#define ON_BOARD_OTHER			0x3

int pldm_pmc_init(void)
{
	num_of_sensors = 0;
	int rc = 0;


	sensor[num_of_sensors].id = ON_BOARD_INLET;
	sensor[num_of_sensors].state = PLDM_SENSOR_ENABLED;
	sensor[num_of_sensors].event = PLDM_EVENT_DISABLED;
	sensor[num_of_sensors].rearm = PLDM_REARM_DISABLED;
	sensor[num_of_sensors].len = sizeof(struct numeric_sensor_pdr);
	sensor[num_of_sensors].scale = SCALE_DISABLED;
	sensor[num_of_sensors].op = MULTIPLY_TO_SCALE;
	sensor[num_of_sensors].value = 2;
	sensor[num_of_sensors].load = 1;
	sensor[num_of_sensors].rec = num_of_sensors;
	sensor[num_of_sensors].pdr = (void *)&thermal_sensor2;
	sensor[num_of_sensors].read = &external_thermal_sensor_rd,

	thermal_sensor2.sens_id = ON_BOARD_INLET;
	if (++num_of_sensors > NUMBER_OF_SENSORS)
		goto exit;

#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
	sensor[num_of_sensors].id = num_of_sensors + 1;
	sensor[num_of_sensors].state = PLDM_SENSOR_ENABLED;
	sensor[num_of_sensors].event = PLDM_EVENT_DISABLED;
	sensor[num_of_sensors].rearm = PLDM_REARM_DISABLED;
	sensor[num_of_sensors].len = sizeof(struct state_pdr);
	sensor[num_of_sensors].load = 1;
	sensor[num_of_sensors].rec = num_of_sensors;
	sensor[num_of_sensors].pdr = (void *)&state_sensor1;
	sensor[num_of_sensors].read = (void *)&pldm_state;

	state_sensor1.sens_id = num_of_sensors + 1;
	if (++num_of_sensors > NUMBER_OF_SENSORS)
		goto exit;
#endif

exit:
	pldm_dbg("pldm pmc init done - num_of_sensors = %u\n", num_of_sensors);
	return rc;
}

pldm_cmd_hdlr_stct pldm_pmc_cmds[] = {
	{PLDM_PMC_SET_NUMERIC_SENSOR_ENABLE, sizeof(struct pldm_set_num_sens_en_req), pldm_set_sensor_en},
	{PLDM_PMC_GET_SENSOR_READING, sizeof(struct pldm_get_sens_rd_req), pldm_get_sensor_rd},
	{PLDM_PMC_GET_SENSOR_THRESHOLDS, sizeof(struct pldm_get_sens_th_req), pldm_get_sensor_th},
	{PLDM_PMC_GET_SENSOR_HYSTERESIS, sizeof(struct pldm_get_sens_th_req), pldm_get_sensor_hy},

#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
	{PLDM_PMC_GET_STATES_SENSOR_READINGS, sizeof(struct pldm_get_state_rd_req), pldm_get_state_rd},
#endif

	{PLDM_PMC_GET_PDR_REPOSITORY_INFO, 0, pldm_get_repo_info},
	{PLDM_PMC_GETPDR, sizeof(struct pldm_get_pdr_req), pldm_get_pdr},
	PLDM_LAST_CMD,
};
