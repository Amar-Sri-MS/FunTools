/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include "utils.h"
#include "mctp.h"
#include "pldm_pmc.h"
#include "pldm_repo.h"
#include "pdr.h"

#define PLDM_SENSOR_EVENT_CLASS		0
#define PLDM_EFFECTOR_EVENT_CLASS	1

#define PLDM_NUMERIC_SENSOR_STATE	3

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

extern struct pldm_global_stc pldm_vars;

static uint8_t num_of_sensors;
static uint8_t no_ack_cnt = 0;
static struct sensors_info sensor[NUMBER_OF_SENSORS];

struct pldm_msg_hdr_stc {
	uint8_t version;
	uint8_t tid;
	uint8_t class;
	uint8_t data[0];
} __attribute__((packed));

struct pldm_numeric_sensor_event_stc {
	uint16_t id;
	uint8_t class;
	uint8_t state;
	uint8_t prv_state;
	uint8_t data_size;
	uint8_t data[0];
} __attribute__((packed));


struct numeric_sensor_pdr *get_sensor_pdr(int id)
{
	for (int i = 0; i < num_of_sensors; i++) {
		if (sensor[i].id == id)
			return (struct numeric_sensor_pdr *)&sensor[i].pdr;
	}

	return NULL;
}

#define MAX_NO_ACK_COUNT		5
int pldm_async_event(uint8_t *buf, int id, int temp)
{
	struct numeric_sensor_pdr *pdr;
	struct pldm_msg_hdr_stc *hdr = (struct pldm_msg_hdr_stc *)buf;
	struct pldm_numeric_sensor_event_stc *msg = (struct pldm_numeric_sensor_event_stc *)hdr->data;
	uint8_t state;

	if (pldm_vars.async_tid == 0) {
		log_err("no async_tid defined\n");
		return -1;
	}

	if (!(pldm_vars.flags & MCTP_VDM_ASYNC_ENABLED)) {
		log_err("async disabled\n");
		return -1;
	}

	if (!(pldm_vars.flags & MCTP_VDM_ASYNC_ACK)) {
		if (++no_ack_cnt != MAX_NO_ACK_COUNT) {
			log_err("no ack received\n");
			return -1;
		}
		no_ack_cnt = 0;
	}

	if ((pdr = get_sensor_pdr(id)) == NULL) {
		log_err("failed to retrieve sensor %u info\n", id);
		return -1;
	}

	hdr->version = 0x01;
	hdr->tid = pldm_vars.async_tid;
	hdr->class = PLDM_SENSOR_EVENT_CLASS;

	msg->id = host2pldm_16(id);
	msg->class = PLDM_NUMERIC_SENSOR_STATE;

        if (sensor[id].scale == SCALE_ENABLED) 
		temp = (sensor[id].op == DIVIDE_TO_SCALE) ? temp / sensor[id].value : temp * sensor[id].value;

	msg->data_size = pdr->data_size;
	*(int *)(msg->data) = host2pldm(temp);

	if (temp == -1)
		state = PLDM_UNKNOWN_STATE;
	else state = (temp < pdr->warn_high) ? PLDM_NORMAL_STATE : (temp < pdr->critc_high) ? PLDM_WARNING_STATE : (temp < pdr->fatal_high) ? PLDM_CRITICAL_STATE : PLDM_FATAL_STATE;

	/* set previous state and record current */
	msg->state = state;
	msg->prv_state = sensor[id].state;
	sensor[id].state = state;

	pldm_vars.flags &= ~MCTP_VDM_ASYNC_ACK;

	return sizeof(struct pldm_msg_hdr_stc) + sizeof(struct pldm_numeric_sensor_event_stc) + pdr->data_size;
}

/* helper function */
static void set_payload(pldm_hdr_stct *resp, struct pldm_get_pdr_rspn *rspn,
                        uint8_t *src, uint8_t rec, uint8_t flag, uint16_t len, uint32_t next)
{
	uint32_t tmp;

	memcpy(rspn->data, src, len);
	tmp = (rec == (num_of_sensors-1)) ? 0 : rec + 1;
	rspn->next_rec = host2pldm(tmp);
	rspn->next_data = host2pldm(next);
	rspn->flag = flag;
	rspn->count = host2pldm_16(len);

	pldm_response(resp, PLDM_SUCCESS);
}

/* actual thermal sensor read */
int32_t external_thermal_sensor_rd()
{
	return -1;
}

/* pldm mcd set event reciver tid handler */
static int pldm_set_rcvr_tid(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
        struct pldm_set_event_rcvr_req_stc *pldm = (struct pldm_set_event_rcvr_req_stc *)hdr->data;
        struct pldm_null_rspn_stc *rspn = (struct pldm_null_rspn_stc *)resp->data;

        if (pldm->proto_type != TRANSPORT_TYPE_MCTP) {
                pldm_err("Invalid protocol type %x\n", pldm->proto_type);
                pldm_response(resp, PLDM_INVALID_DATA);
                return MIN_PLDM_PAYLOAD;
        }

        pldm_vars.async_tid = (pldm->enable) ? pldm->addr : 0;

        pldm_response(resp, PLDM_SUCCESS);
        return PLDM_PAYLOAD_SIZE;
}

/* pldm mcd get event reciver tid handler */
static int pldm_get_rcvr_tid(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
        struct pldm_get_event_rcvr_rspn_stc *rspn = (struct pldm_get_event_rcvr_rspn_stc *)resp->data;

	rspn->proto_type = TRANSPORT_TYPE_MCTP;
        rspn->addr = pldm_vars.async_tid;

        pldm_response(resp, PLDM_SUCCESS);
        return PLDM_PAYLOAD_SIZE;
}

/* pldm pmc get repo info */
static int pldm_get_repo_info(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_repo_rspn *rspn = (struct pldm_get_repo_rspn *)resp->data;
	uint32_t size = 1023;
	int i;

	rspn->repo_state = AVAILABLE_REPO;

	rspn->update_time.utc_offset = host2pldm_16(2 * 60);
	rspn->update_time.seconds = REPO_BUILD_SEC;
	rspn->update_time.minute = REPO_BUILD_MIN;
	rspn->update_time.hour = REPO_BUILD_HOUR;
	rspn->update_time.day = REPO_BUILD_DAY;
	rspn->update_time.month = REPO_BUILD_MONTH;
	rspn->update_time.year = host2pldm_16(REPO_BUILD_YEAR);
	
	memcpy((uint8_t *)&rspn->oem_update_time, (uint8_t *)&rspn->update_time,sizeof(struct pldm_timestamp));
	rspn->count = host2pldm(num_of_sensors);

	for (i = 0; i < num_of_sensors; i++)
		size += sensor[i].len;

	rspn->repo_size = host2pldm(size);

	/* FIXME: for now, the numeric pdr is the largest.
	 * if new structure is to be designed, this may need to be changed
	 */
	size = (63 + sizeof(struct numeric_sensor_pdr));
	rspn->max_pdr_size = host2pldm(size);

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

	rec = pldm2host(pldm->rec_handle);
	seq = pldm2host(pldm->data_seq);
	cnt = pldm2host_16(pldm->req_count);
	chg = pldm2host_16(pldm->chan_num);

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
	uint16_t id = pldm2host_16(pldm->id);

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
	int8_t tmp = 0, warn, critic, fatal;
	uint8_t state;
	uint16_t id = pldm2host_16(pldm->id);

	VALID_SENSOR(id);

	if (pldm->rearm && (sensor[id].rearm == PLDM_REARM_DISABLED)) {
		pldm_err("rearm not supported\n");
		pldm_response(resp, REARM_UNAVAILABLE);
		return COMP_CODE_ONLY;
	}

	pdr = (struct numeric_sensor_pdr *)sensor[id].pdr;
	tmp = *((int8_t *)sensor[id].read);
	//Real implementation would be done later.
	//Currently using hardcoded value to satisfy testing need.
	//FYI: Currently this feature and product has been frozen
	tmp=0x2c;

        if (sensor[id].scale == SCALE_ENABLED) 
		tmp = (sensor[id].op == DIVIDE_TO_SCALE) ? tmp / sensor[id].value : tmp * sensor[id].value;

	rspn->data = tmp;
	
	rspn->data_size = pdr->data_size;

	/* if no temperature read is available - mark the sensor as disabled */
	rspn->state = (tmp == -1) ? PLDM_SENSOR_UNAVAILABLE : sensor[id].state;
	rspn->event_ena = PLDM_EVENTS_STATE_ONLY;

	warn = pdr->warn_high;
	critic = pdr->critc_high;
	fatal = pdr->fatal_high;

	//As per DSP0248 Spec
	if (sensor[id].state != PLDM_SENSOR_ENABLED) {
		rspn->c_state = PLDM_UNKNOWN_STATE;
		rspn->p_state = PLDM_UNKNOWN_STATE;
		rspn->e_state = PLDM_UNKNOWN_STATE;
	} else {
		if (tmp == -1)
			state = PLDM_UNKNOWN_STATE;
		else state = (tmp < warn) ? PLDM_NORMAL_STATE : (tmp < critic) ? PLDM_WARNING_STATE : (tmp < fatal) ? PLDM_CRITICAL_STATE : PLDM_FATAL_STATE;

		rspn->p_state = rspn->c_state;
		rspn->c_state = state;
		rspn->e_state = state;
	}

	pldm_response(resp, PLDM_SUCCESS);
	return PLDM_PAYLOAD_SIZE;
}

/* pldm get sensor threshold */
static int pldm_get_sensor_th(pldm_hdr_stct *hdr, pldm_hdr_stct *resp)
{
	struct pldm_get_sens_th_req *pldm = (struct pldm_get_sens_th_req *)hdr->data;
	struct pldm_get_sens_th_rspn *rspn = (struct pldm_get_sens_th_rspn *)resp->data;
	struct numeric_sensor_pdr *pdr;
	uint16_t id = pldm2host_16(pldm->id);

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
	uint16_t id = pldm2host_16(pldm->id);

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
	uint16_t id = pldm2host_16(pldm->id);
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

void update_repo(struct numeric_sensor_pdr *pdr, uint32_t mcot)
{
	pdr->warn_high = host2pldm(mcot);

	pdr->critc_high = host2pldm((mcot + 10));
	pdr->fatal_high = host2pldm((mcot + 15));
	pdr->support_thold = PLDM_UPPER_WARNING_SUPPORT | PLDM_UPPER_CRITICAL_SUPPORT | PLDM_UPPER_FATAL_SUPPORT;

//	pdr->crc8 = (uint8_t)crc8((uint8_t *)pdr, sizeof(struct numeric_sensor_pdr) - 1);
}

static pldm_cmd_hdlr_stct pldm_pmc_cmds[] = {
	{PLDM_PMC_SET_NUMERIC_SENSOR_ENABLE, sizeof(struct pldm_set_num_sens_en_req), pldm_set_sensor_en},
	{PLDM_PMC_GET_SENSOR_READING, sizeof(struct pldm_get_sens_rd_req), pldm_get_sensor_rd},
	{PLDM_PMC_GET_SENSOR_THRESHOLDS, sizeof(struct pldm_get_sens_th_req), pldm_get_sensor_th},
	{PLDM_PMC_GET_SENSOR_HYSTERESIS, sizeof(struct pldm_get_sens_th_req), pldm_get_sensor_hy},
#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
	{PLDM_PMC_GET_STATES_SENSOR_READINGS, sizeof(struct pldm_get_state_rd_req), pldm_get_state_rd},
#endif
	{PLDM_PMC_GET_PDR_REPOSITORY_INFO, 0, pldm_get_repo_info},
	{PLDM_PMC_GETPDR, sizeof(struct pldm_get_pdr_req), pldm_get_pdr},
        {PLDM_PMC_SET_EVENT_RECEIVER, sizeof(struct pldm_set_event_rcvr_req_stc), pldm_set_rcvr_tid},
        {PLDM_PMC_GET_EVENT_RECEIVER, 0, pldm_get_rcvr_tid},
	PLDM_LAST_CMD,
};

void get_pmc_supported_cmds(uint8_t *cmds)
{
	set_bit(PLDM_PMC_SET_NUMERIC_SENSOR_ENABLE, cmds);
	set_bit(PLDM_PMC_GET_SENSOR_READING, cmds);
	set_bit(PLDM_PMC_GET_SENSOR_THRESHOLDS, cmds);
	set_bit(PLDM_PMC_GET_SENSOR_HYSTERESIS, cmds);
#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
	set_bit(PLDM_PMC_GET_STATES_SENSOR_READINGS, cmds);
#endif
	set_bit(PLDM_PMC_GET_PDR_REPOSITORY_INFO, cmds);
	set_bit(PLDM_PMC_GETPDR, cmds);
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
	sensor[num_of_sensors].pdr = (void *)&thermal_sensor1;
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

	rc = register_pldm_handler(PLDM_PMC_TYPE, pldm_pmc_cmds);

exit:
	pldm_dbg("pldm pmc init done - num_of_sensors = %u\n", num_of_sensors);
	return rc;
}

