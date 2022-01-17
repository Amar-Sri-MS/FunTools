/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PLDM_PMC_HDR_
#define _INC_PLDM_PMC_HDR_

#include <stdint.h>
#include "pldm.h"

/* real32 - single precision,
 * [31]	   - sign bit
 * [30:23] - exponent
 * [22:0]  - mantissa
 *
 * (exponent = 255 && mantissa != 0) => NaN
 * (exponent = 255 && mantissa == 0 && sign == 1) => -infinity
 * (exponent = 255 && mantissa == 0 && sign == 0) => infinity
 * (0 < exponent < 255) => (-1)**sign * (2**(exponent - 127) * 1.mantissa)
 */

#ifndef BIT
#define BIT(n)				(1 << n)
#endif

#define CONFIG_EXTERNAL_SENSOR_SUPPORT

#define AVAILABLE_REPO			0
#define UPDATE_IN_PROGRESS_REPO		1
#define FAILED_REPO			2

/* pldm sensor state */
#define PLDM_SENSOR_ENABLED		0
#define PLDM_SENSOR_DISABLED		1
#define PLDM_SENSOR_UNAVAILABLE		2
#define PLDM_SENSOR_UNKNOWN		3
#define PLDM_SENSOR_FAILED		4
#define PLDM_SENSOR_INIT		5
#define PLDM_SENSOR_SHUTINGDOWN		6
#define PLDM_SENSOR_IN_TEST		7

/* present sensor state */
#define PLDM_UNKNOWN_STATE		0
#define PLDM_NORMAL_STATE		1
#define PLDM_WARNING_STATE		2
#define PLDM_CRITICAL_STATE		3
#define PLDM_FATAL_STATE		4

/* rearm enable/disable */
#define PLDM_REARM_DISABLED		0
#define PLDM_REARM_ENABLED		1

/* pldm event state */
#define PLDM_EVENT_ENABLED		1
#define PLDM_EVENT_DISABLED		0

#define PLDM_NO_EVENT_GEN		0
#define PLDM_EVENTS_DISABLED		1
#define PLDM_EVENTS_ENABLED		2
#define PLDM_EVENTS_OP_ONLY		3
#define PLDM_EVENTS_STATE_ONLY		4

/* scale constants */
#define SCALE_ENABLED                   1
#define SCALE_DISABLED                  0

#define DIVIDE_TO_SCALE                 1
#define MULTIPLY_TO_SCALE               0

#define NUMBER_OF_SENSORS		6

/* pldm range feilds support */
#define PLDM_FATAL_LOW_SUPPORT		BIT(6)
#define PLDM_FATAL_HIGH_SUPPORT		BIT(5)
#define PLDM_CRITICAL_LOW_SUPPORT	BIT(4)
#define PLDM_CRITICAL_HIGH_SUPPORT	BIT(3)
#define PLDM_NORMAL_MIN_SUPPORT		BIT(2)
#define PLDM_NORMAL_MAX_SUPPORT		BIT(1)
#define PLDM_NOMINAL_VALUE_SUPPORT	BIT(0)

/* pldm threshold support */
#define PLDM_UPPER_WARNING_SUPPORT	BIT(0)
#define PLDM_UPPER_CRITICAL_SUPPORT	BIT(1)
#define PLDM_UPPER_FATAL_SUPPORT	BIT(2)
#define PLDM_LOWER_WARNING_SUPPORT	BIT(3)
#define PLDM_LOWER_CRITICAL_SUPPORT	BIT(4)
#define PLDM_LOWER_FATAL_SUPPORT	BIT(5)

/* chip container id */
#define CHIP_CONTAINER_ID		0x1634

/* pldm pmc configuration */
#define CONFIG_EXPLICIT_REPO_FORMAT
#define CONFIG_DYNAMIC_TEMPERATURE_READ

/* pldm pdr structure per DSP0248 28.1 */
struct pldm_common_pdr_hdr {
	uint32_t handler;
	uint8_t version;
	uint8_t type;
	uint16_t change;
	uint16_t len;
} __attribute__((packed));

/* pldm pdr structure per DSP0248 28.4 */
typedef uint32_t sensordata_t;

struct numeric_sensor_pdr {
	struct pldm_common_pdr_hdr hdr;
	uint16_t hdl_id;
	uint16_t sens_id;            /* statically set per PDR # */
	uint16_t type;              /* statically set to 0x002C */
	uint16_t inst_num;          /* statically set to 0x0001 */
	uint16_t cid;               /* statically set to 0x0000 */
	uint8_t init;               /* statically set to 0x00 */
	uint8_t has_pdr;            /* statically set to 0x00 */
	uint8_t base_unit;          /* statically set to 0x02 */
	int8_t  unit_mod;           /* statically set to 0x00 */
	uint8_t rate;               /* statically set to 0x00 */
	uint8_t base_oem;           /* statically set to 0x00 */
	uint8_t aux_uint;           /* statically set to 0x00 */
	uint8_t aux_mod;            /* statically set to 0x00 */
	uint8_t aux_rate;           /* statically set to 0x00 */
	uint8_t rel;                /* statically set to 0x00 */
	uint8_t aux_hdlr;           /* statically set to 0x00 */
	uint8_t is_linear;          /* statically set to 0x01 */
	uint8_t data_size;          /* statically set to 0x04 */
	int32_t res;                /* statically set to 0x3f800000 */
	int32_t offset;             /* statically set to 0x00000000 */
	uint16_t accuracy;          /* statically set to 0x0000 */
	uint8_t plus_tol;           /* statically set to 0x00 */
	uint8_t minus_tol;          /* statically set to 0x00 */
	sensordata_t hysteresis;    /* statically set to 0x0002 */
	uint8_t support_thold;      /* statically set to 0x07 */
	uint8_t thold_hys;          /* statically set to 0x00 */
	int32_t trans_interval;     /* statically set to 0x00000000 */
	int32_t update_interval;    /* statically set to 0x0000000 */
	sensordata_t max;           /* statically set to TBD */
	sensordata_t min;           /* statically set to TBD */
	uint8_t range;              /* statically set to 0x04 */
	uint8_t range_fileds_support;     /* statically set to 0x7f */
	sensordata_t nominal_val;   /* statically set to TBD - optional support */
	sensordata_t normal_max;    /* statically set to TBD - optional support */
	sensordata_t normal_min;    /* statically set to TBD - optional support */
	sensordata_t warn_high;     /* statically set to TBD */
	sensordata_t warn_low;      /* statically set to TBD */
	sensordata_t critc_high;    /* statically set to TBD - optional support */
	sensordata_t critc_low;     /* statically set to TBD - optional support */
	sensordata_t fatal_high;    /* statically set to TBD - optional support */
	sensordata_t fatal_low;     /* statically set to TBD - optional support */
	uint8_t crc8;
} __attribute__((packed));

/* pldm state header */
struct state_hdr {
	uint16_t id;
	uint8_t size;
} __attribute__((packed));

/* health status structure */
struct health_pdr {
	struct state_hdr hdr;	/* statically set to {0x0001, 0x02} */
	uint8_t states[2];	/* statically set to {0xfe, 0x03} */
} __attribute__((packed));

/* config set status structure */
struct cfg_set_pdr {
	struct state_hdr hdr;	/* statically set to {0x000f, 0x01} */
	uint8_t states[1];	/* statically set to 0x1e */
} __attribute__((packed));

/* config changed status structure */
struct cfg_chg_pdr {
	struct state_hdr hdr;	/* statically set to {0x0010, 0x01} */
	uint8_t states[1];	/* statically set to 0x06 */
} __attribute__((packed));

/* status states structure */
struct states_stc {
	struct health_pdr health;
	struct cfg_set_pdr cfg_set;
	struct cfg_chg_pdr cfg_chg;
} __attribute__((packed));

/* pldm pdr structure per DSP0248.28.6 */
struct state_pdr {
	struct pldm_common_pdr_hdr hdr;
	uint16_t hdl_id;
	uint16_t sens_id;           /* statically set per PDR # */
	uint16_t type;              /* statically set to 0x002C */
	uint16_t inst_num;          /* statically set to 0x0002 */
	uint16_t cid;               /* statically set to 0x0000 */
	uint8_t init;               /* statically set to 0x00 */
	uint8_t has_pdr;            /* statically set to 0x00 */
	uint8_t num_of_states;      /* statically set to 0x03, may need to support more */
	struct states_stc state;
	uint8_t crc8;
} __attribute__((packed));


/* pldm set numeric sensor enable */
#define INVALID_SENSOR_ID       0x80
#define INVALID_SENSOR_STATE    0x81
#define EVENT_NOT_SUPPORTED     0x82
struct pldm_set_num_sens_en_req {
    uint16_t id;
    uint8_t state;
    uint8_t event;
} __attribute__((packed));

/* pldm get sensor read command response per DSP0248 18.2 */
#define REARM_UNAVAILABLE       0x81
struct pldm_get_sens_rd_req {
    uint16_t id;
    uint8_t rearm;
} __attribute__((packed));

struct pldm_get_sens_rd_rspn {
    uint8_t comp_code;
    uint8_t data_size;		/* sensor data set to uint32_t, hence 4 */
    uint8_t state;
    uint8_t event_ena;
    uint8_t c_state;
    uint8_t p_state;
    uint8_t e_state;
    sensordata_t data;
} __attribute__((packed));

/* pldm set_event_receiver struct */
struct pldm_set_event_rcvr_req_stc {
    uint8_t enable;
    uint8_t proto_type;
    uint8_t addr;
} __attribute__((packed));

/* pldm get_event_receiver struct */
struct pldm_get_event_rcvr_rspn_stc {
    uint8_t cmp_code;
    uint8_t proto_type;
    uint8_t addr;
} __attribute__((packed));

/* pldm get sensor thresholds response per DSP0248 18.3 */
struct pldm_get_sens_th_req {
    uint16_t id;
} __attribute__((packed));

struct pldm_get_sens_th_rspn {
    uint8_t comp_code;
    uint8_t data_size;		/* sensor data set to uint32_t, hence 4 */
    sensordata_t warn_high;
    sensordata_t crit_high;
    sensordata_t fatal_high;
    sensordata_t warn_low;
    sensordata_t crit_low;
    sensordata_t fatal_low;
} __attribute__((packed));

/* pldm get sensor hysteresis response per DSP0248 18.6 */
struct pldm_get_sens_hy_rspn {
    uint8_t comp_code;
    uint8_t data_size;          /* sensor data set to uint132_t, hence 4 */
    sensordata_t val;
} __attribute__((packed));

/* pldm get state sensor reading response per DSP0248 20.2 */
struct state_fields {
    uint8_t op_state;
    uint8_t prsnt_state;
    uint8_t prev_state;
    uint8_t event_state;
    uint8_t data[0];
} __attribute__((packed));

struct pldm_get_state_rd_req {
    uint16_t id;
    uint16_t rearm;
} __attribute__((packed));

struct pldm_get_state_rd_rspn {
    uint8_t comp_code;
    uint8_t count;
    uint8_t data[0];
} __attribute__((packed));

/* pldm time stamp 104 format per DSP0240 */
struct pldm_timestamp {
    uint16_t utc_offset;
    uint32_t seconds;
    uint8_t minute;
    uint8_t hour;
    uint8_t day;
    uint8_t month;
    uint16_t year;
    uint8_t utc_time;
} __attribute__((packed));

/* pldm get repo response per DSP0248 26.1 */
#define INVALID_DATA_TRANSFER_HANDLE        0x80
#define INVALID_TRANSFER_OPERATION_FLAG     0x81
#define INVALID_RECORD_HANDLE               0x82
#define INVALID_RECORD_CHANGE_NUMBER        0x83
#define TRANSFER_TIMEOUT                    0x84
#define REPOSITORY_UPDATE_IN_PROGRESS       0x85
struct pldm_get_repo_rspn {
    uint8_t comp_code;
    uint8_t repo_state;
    struct pldm_timestamp update_time;
    struct pldm_timestamp oem_update_time;
    uint32_t count;
    uint32_t repo_size;
    uint32_t max_pdr_size;
    uint8_t timeout;
} __attribute__((packed));

/* pldm get pdr per DSP0248 26.2.1 */
struct pldm_get_pdr_req {
    uint32_t rec_handle;
    uint32_t data_seq;
    uint8_t flag;
    uint16_t req_count;
    uint16_t chan_num;
}  __attribute__((packed));

struct pldm_get_pdr_rspn {
    uint8_t comp_code;
    uint32_t next_rec;
    uint32_t next_data;
    uint8_t flag;
    uint16_t count;
    uint8_t data[0];
} __attribute__((packed));

#define UPPER_WARNING_TH        70
#define UPPER_CRITICAL_TH       85
#define UPPER_FATAL_TH          95
#define LOWER_WARNING_TH        10
#define LOWER_CRITICAL_TH       5
#define LOWER_FATAL_TH          0

struct sensors_info {
	uint32_t len:16, rearm:1, event:3, state:4, id:8;
	uint32_t value:29, load:1, op:1, scale:1;
	uint32_t rec;
	void *pdr;
	int (*read)(void);
};

extern pldm_cmd_hdlr_stct pldm_pmc_cmds[];

int pldm_async_event(uint8_t *buf, int id, int temp);
int pldm_pmc_init(void);

#endif /* _INC_PLDM_PMC_HDR_ */
