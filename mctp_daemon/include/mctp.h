/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PCIE_HDR_
#define _INC_PCIE_HDR_

#include <stdint.h>
#include "auto_conf.h"

#define mctp_err(fmt, arg...)          log_n_print("MCTP: ERROR - "fmt, ##arg)

#ifdef CONFIG_MCTP_DEBUG
#define mctp_dbg(fmt, arg...)          printf("%s: "fmt,__func__, ##arg)
#else
#define mctp_dbg(fmt, arg...)
#endif

#define MAX_MCTP_PKT_SIZE	(64 + 4)

#define MCTP_CMD_EID_SET	0x01
#define MCTP_CMD_EID_GET	0x02
#define MCTP_CMD_UUID_GET	0x03
#define MCTP_CMD_VER_GET	0x04
#define MCTP_CMD_MSG_GET	0x05
#define MCTP_CMD_VDM_GET	0x06
#define MCTP_CMD_EID_RESOLVE	0x07
#define MCTP_CMD_EID_ALLOC	0x08
#define MCTP_CMD_ROUTE_UPDATE	0x09
#define MCTP_CMD_ROUTE_GET	0x0a
#define MCTP_CMD_PRE_EP_DISC	0x0b
#define MCTP_CMD_EP_DISC	0x0c
#define MCTP_CMD_NOTIFY_DISC	0x0d
#define MCTP_CMD_HOP_GET	0x0f

#define MCTP_RESP_SUCCESS	0x00
#define MCTP_RESP_ERROR		0x01
#define MCTP_RESP_INVAL_DATA	0x02
#define MCTP_RESP_INVAL_LEN	0x03
#define MCTP_RESP_BUSY		0x04
#define MCTP_RESP_SUPPORT	0x05

#define MCTP_MSG_CONTROL	0x00
#define MCTP_MSG_PLDM		0x01
#define MCTP_MSG_NCSI		0x02
#define MCTP_MSG_VDM_PCI	0x7e
#define MCTP_MSG_VDM_IANA	0x7f
#define MCTP_BASE_PROTOCOL	0xff

#define MCTP_VID_FMT_PCI	(0x00)
#define MCTP_VID_FMT_IANA	(0x01)

#define MCTP_EID_NULL		0
#define MCTP_EID_BROADCAST	0xff

#define MAX_MCTP_MESSAGE_SIZE   256
#define MIN_MCTP_FRAG_SIZE      5
#define MCTP_COMMAND_CODE       0x0f

#define MCTP_OPCODE_WRITE	1

typedef struct __attribute__((packed)) {
	uint8_t	hdr_ver;
	uint8_t	dst_eid;
	uint8_t	src_eid;
	uint8_t	tag:3, to:1, seq:2, eom:1, som:1;
	uint8_t	data[0];
} mctp_hdr_stct;

typedef struct __attribute__((packed)) {
	uint8_t	iid:5, rsvd:1, d_bit:1, rq:1;
	uint8_t	cmd;
	uint8_t	data[0];
} mctp_ctrl_hdr_t;

typedef struct __attribute__((packed)) {
	uint16_t pci_vid;
	uint8_t	data[0];
} mctp_pci_vid_hdr_t;

typedef struct {
	uint8_t reason;
} mctp_unsupported_resp_t;

typedef struct {
	uint8_t reason;
	uint8_t status;
	uint8_t eid;
	uint8_t pool_size;
} mctp_set_eid_resp_t;

typedef struct {
	uint8_t reason;
	uint8_t eid;
	uint8_t eid_type;
	uint8_t data;
} mctp_get_eid_resp_t;

typedef struct {
	uint8_t reason;
	uint8_t udid[16];
} mctp_get_udid_resp_t;

#define MCTP_MSG_TYPE_NOT_SUPPORTED	0x80

/* mctp base/control protocol version */
#define MCTP_CTRL_VER_NUM_MAJOR		0xf1
#define MCTP_CTRL_VER_NUM_MINOR		0xf2
#define MCTP_CTRL_VER_NUM_UPDATE	0xf0
#define MCTP_CTRL_VER_NUM_ALPHA		0x00

typedef struct __attribute__((packed)) {
	uint8_t reason;
	uint8_t ent_cnt;
	uint8_t data[0];
} mctp_get_version_resp_t;

typedef struct __attribute__((packed)) {
	uint8_t major;
	uint8_t minor;
	uint8_t update;
	uint8_t alpha;
	uint8_t data[0];
} mctp_ver_t;

typedef struct __attribute__((packed)) {
	uint8_t reason;
	uint8_t msg_cnt;
	uint8_t data[0];
} mctp_get_msg_resp_t;

typedef struct __attribute__((__packed__)) {
	uint8_t code;
	uint8_t sel;
	uint8_t data[0];
} mctp_get_vdm_sup_resp_t;

/* Minimum payload size for response to mctp requests */
#define MCTP_CTL_MIN_RSP	(2)

#define MCTP_MTU_SIZE			64
#define MCTP_SMB_FRAG_SIZE              124
#define MCTP_PCIE_FRAG_SIZE		68
#define MCTP_MAX_MESSAGE_DATA   	2048
#define MCTP_MAX_BUFFER_SIZE		256

#define MCTP_TRANSPORT_SMBUS    	1
#define MCTP_TRANSPORT_PCIE_VDM		2

#ifndef BIT
#define BIT(x)				(1 << x)
#endif

/* mctp endpoint supported media */
#define SUPPORT_NCSI_OVER_MCTP		BIT(0)
#define SUPPORT_PLDM_OVER_MCTP		BIT(1)
#define SUPPORT_VDM_OVER_MCTP		BIT(2)
#define SUPPORT_OEM_OVER_MCTP		BIT(3)
#define SUPPORT_MCTP_CNTROL_MSG		BIT(4)
#define SUPPORT_ASYNC_EVENTS		BIT(5)

/* mctp endpoint flags */
#define MCTP_SEQ_ROLL			BIT(0)
#define MCTP_COMPLETE			BIT(1)
#define MCTP_EP_ACTIVE			BIT(2)
#define MCTP_EP_INIT_DONE		BIT(3)
#define MCTP_IN_FLIGHT                  BIT(4)

/* mctp error codes */
#define ERR_NO_TX_HANDLER               -1
#define ERR_NO_RX_HANDLER               -2
#define ERR_LEN                         -3
#define ERR_PKT_TOO_SMALL               -4
#define ERR_BAD_SEQ_NUM                 -5
#define ERR_INIT	                -6
#define ERR_BAD_SEID			-7
#define ERR_BAD_DEID			-8
#define ERR_NO_RETAIN			-9
#define ERR_BUFFER_OVERFLOW		-10

struct mctp_ops_stc {
	int (*init)(void);
	int (*recv)(uint8_t *, int);
	int (*async)(uint8_t *);
	int (*send)(int);
	int (*complete)(void);
	int (*error)(void);
	int (*exit)(void);
	int (*get_rx_fifo)(void);
	int (*get_min_payload)(void);
};

#define DEFAULT_MCTP_FRAGMENT_SIZE		68
struct mctp_ep_retain_stc {
	uint32_t eid:8, iid:8, fragsize:8, support:8;
	uint8_t uuid[16];
	void *ep_priv_data;
};

typedef struct mctp_endpoint_stc {
	uint8_t src_eid;
	uint8_t msgtype:7, ic:1;
	uint8_t rxseq:2, txseq:2, tag:3, to:1;

	uint8_t flags;				// ep state flags
	uint32_t payload;			// the payload portion length of outgoing fragment

	uint32_t tx_len:16, tx_cnt:16;		// tx_len = total payload length, tx_cnt = fragment length
	uint8_t	*tx_ptr;			// pointer to a complete payload
	uint8_t *tx_pkt_buf;			// pointer to fragment buffer

	uint32_t rx_len:16, rx_cnt:16;		// rx_len = total received payload length, rx_cnt = fragment length
	uint8_t	*rx_ptr;			// pointer to complete received payload
	uint8_t *rx_pkt_buf;			// pointer to received fragment

	struct mctp_ep_retain_stc *retain;
	struct mctp_ops_stc *ops;
} mctp_endpoint_stct;


enum mctp_stats_enum {
	STOP,
	ABORT,
	ARB_LOST,
	TIMEOUT,
	BAD_MSG
};

/* MCTP statistics */
typedef struct {
	uint32_t rx_pkts;
	uint32_t rx_bytes;
	uint32_t tx_pkts;
	uint32_t tx_bytes;
	uint32_t abort;
	uint32_t timeout;
	uint32_t arb_lost;
	uint32_t stop;
	uint32_t bad_msg;
} mctp_stats_t;

#define PCIE_EP_ID      0
#define SMBUS_EP_ID     1
#define NUMBER_OF_EPS   2
extern struct mctp_ops_stc *mctp_ops[NUMBER_OF_EPS];

mctp_stats_t *get_mctp_sts(void);
int mctp_recieve(mctp_endpoint_stct *);
int mctp_transmit(mctp_endpoint_stct *);
int mctp_init(void);

#endif /* _INC_PCIE_HDR_ */
