/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PLDM_HDR_
#define _INC_PLDM_HDR_

#include <stdint.h>
#include "auto_conf.h"

#define pldm_err(fmt, arg...)          log_n_print("pldm error: "fmt, ##arg)

#ifdef CONFIG_PLDM_DEBUG
#define pldm_dbg(fmt, arg...)          log_n_print("%s: "fmt, __func__, ##arg)
#else
#define pldm_dbg(fmt, arg...)
#endif

#ifndef NULL
#define NULL                    ((void *)0)
#endif

#ifndef BIT
#define BIT(n)			(1 << (n))
#endif


#define PLDM_VER_CRC32          0xedb88320

/* mctp pldm version */
#define PLDM_VER_NUM_MAJOR		0xf1
#define PLDM_VER_NUM_MINOR		0xf1
#define PLDM_VER_NUM_UPDATE		0xf0
#define PLDM_VER_NUM_ALPHA		0x00

#define PLDM_HEADER_VERSION     	0
#define PLDM_REQ_DATA           	2

#define MAX_NUM_OF_STATES       	8
#define PLDM_TX_BUFFER_SIZE     	256
#define PLDM_PAYLOAD_OFFSET	    	(4 + 5)

/* pldm error codes */
#define PLDM_SUCCESS                    0x00
#define PLDM_ERROR                      0x01
#define PLDM_INVALID_DATA               0x02
#define PLDM_INVALID_LENGTH             0x03
#define PLDM_BUSY                       0x04
#define PLDM_UNSUPPORTED                0x05
#define PLDM_INVALID_TYPE               0x20
#define PLDM_INVALID_DATA_HANDLE        0x80
#define PLDM_INVALID_OP_FLAG            0x81
#define PLDM_INVALID_TYPE_REQ           0x83
#define PLDM_INVALID_VERSION            0x84

/* pldm types */
#define PLDM_MCD_TYPE           	0x00
#define PLDM_SMBIOS_TYPE        	0x01
#define PLDM_PMC_TYPE           	0x02
#define PLDM_BCC_TYPE           	0x03
#define PLDM_FRU_TYPE           	0x04
#define PLDM_OEM_TYPE           	0x3f

/* pldm Messaging Control and Discovery Commands */
#define PLDM_MCD_SETTID         	0x01
#define PLDM_MCD_GETTID         	0x02
#define PLDM_MCD_GET_VERSION    	0x03
#define PLDM_MCD_GET_TYPE       	0x04
#define PLDM_MCD_GET_CMDS       	0x05

/* pldm Platform Monitoring and Control Commands */
/* Terminus and Event Commands */
#define PLDM_PMC_GET_TERMINUS_UID	0x03
#define PLDM_PMC_SET_EVENT_RECEIVER	0x04
#define PLDM_PMC_GET_EVENT_RECEIVER	0x05
#define PLDM_PMC_PLATFORM_EVENT_MSG	0x0A

/* Numeric Sensor Commands */
#define PLDM_PMC_SET_NUMERIC_SENSOR_ENABLE      0x10
#define PLDM_PMC_GET_SENSOR_READING             0x11
#define PLDM_PMC_GET_SENSOR_THRESHOLDS          0x12
#define PLDM_PMC_SET_SENSOR_THRESHOLDS          0x13
#define PLDM_PMC_RESTORE_SENSOR_THRESHOLDS      0x14
#define PLDM_PMC_GET_SENSOR_HYSTERESIS          0x15
#define PLDM_PMC_SET_SENSOR_HYSTERESIS          0x16
#define PLDM_PMC_INIT_NUMERIC_SENSOR            0x17

/* State Sensor Commands */
#define PLDM_PMC_SET_STATES_SENSOR_ENABLES      0x20
#define PLDM_PMC_GET_STATES_SENSOR_READINGS     0x21
#define PLDM_PMC_INIT_STATE_SENSOR              0x22

/* pldm PDR Repository Commands */
#define PLDM_PMC_GET_PDR_REPOSITORY_INFO        0x50
#define PLDM_PMC_GETPDR                         0x51

/* pldm flags */
#define START_TRANSFER                          1
#define MIDDLE_TRANSFER                         2
#define END_TRANSFER                            4

#define MIN_PLDM_PAYLOAD                        1
#define COMP_CODE_ONLY                          MIN_PLDM_PAYLOAD

#define PLDM_TYPE_MCD_HDLR(cmd, len, hdlr)      {PLDM_MCD_TYPE, cmd, len, &hdlr}
#define PLDM_TYPE_PMC_HDLR(cmd, len, hdlr)      {PLDM_PMC_TYPE, cmd, len, hdlr}

/* used by set bit on multibyte bitstream */
typedef uint8_t         bit_arr_t;
#define BIT_SIZE        256
#define ARR_WIDTH       (8 * sizeof(bit_arr_t))
#define ARR_SIZE        (BIT_SIZE/ARR_WIDTH)

#define PLDM_PAYLOAD_SIZE       (sizeof(*rspn))

/* pldm static and global variables */
struct pldm_states_stc {
        uint8_t pres;
        uint8_t prev;
        uint8_t evnt;
};

#define MCTP_VDM_ASYNC_ENABLED		BIT(0)
#define MCTP_VDM_ASYNC_ACK		BIT(1)
struct pldm_global_stc {
    uint32_t temp;
    uint32_t sen_en;
    struct pldm_states_stc state[4];
    uint8_t tid;
    uint8_t async_tid;
    uint8_t flags;
};

/* pldm receive header */
typedef struct __attribute__((packed)) {
	uint8_t inst_id: 5, rsrvd: 1, drq: 2;
	uint8_t type: 6, ver: 2;
	uint8_t cmd;
	uint8_t data[0];
} pldm_hdr_stct;

/* pldm null response struct */
struct pldm_null_rspn_stc {
	uint8_t cmp_code;
} __attribute__((packed));

/* pldm handler structure */
typedef struct {
	uint8_t cmd;
	uint16_t len;
	int (*hdlr)(pldm_hdr_stct *hdr, pldm_hdr_stct *resp);
} pldm_cmd_hdlr_stct;

#define PLDM_LAST_CMD		{-1, -1, NULL}

extern struct pldm_global_stc pldm_vars;

void pldm_handle_async_event(int id, float temp);
void set_bit(uint32_t, bit_arr_t *);
int pldm_response(pldm_hdr_stct *, uint8_t);
int pldm_handler(uint8_t *, int, uint8_t *);
int pldm_init(void);

#endif /* _INC_PLDM_HDR_ */
