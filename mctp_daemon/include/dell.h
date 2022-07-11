#ifndef _NCSI_DELL_CMD_HDR_
#define _NCSI_DELL_CMD_HDR_

#include <stdint.h>
#include "auto_conf.h"

#define dell_err(fmt,arg...)		log_n_print("DELL: ERROR - "fmt, ##arg)

#ifdef CONFIG_DELL_DEBUG
#define dell_dbg(fmt, arg...)           log_n_print("%s: "fmt, __func__, ##arg)
#else
#define dell_dbg(fmt, arg...)
#endif

/* dell IANA */
#define DELL_IANA			0x02a2

/* dell OEM Section */
#define DELL_CMD_INVENTORY	        0x00
#define DELL_CMD_EXT_CAP	        0x01
#define DELL_CMD_PART_INFO	        0x02
#define DELL_CMD_FCOE_CAP	        0x03
#define DELL_CMD_VLINK		        0x04
#define DELL_CMD_PART_L2STAT		0x05
#define DELL_CMD_PART_FCSTAT		0x06
#define DELL_CMD_ADDR_SET	        0x07
#define DELL_CMD_ADDR_GET	        0x08
#define DELL_CMD_LICENSE_SET		0x09
#define DELL_CMD_LICENSE_GET		0x0a
#define DELL_CMD_PASSTHRU_SET		0x0b
#define DELL_CMD_PASSTHRU_GET		0x0c
#define DELL_CMD_BW_SET		        0x0d
#define DELL_CMD_BW_GET		        0x0e
#define DELL_CMD_MCIP_SET	        0x0f
#define DELL_CMD_TEAM_GET	        0x10
#define DELL_CMD_PORT_ENABLE		0x11
#define DELL_CMD_PORT_DISABLE		0x12
#define DELL_CMD_TEMP_GET	        0x13
#define DELL_CMD_LINKTUNE_SET		0x14
#define DELL_CMD_WOL_ENABLE	        0x15
#define DELL_CMD_WOL_DISABLE		0x16
#define DELL_CMD_GET_FC_STATS		0x17
#define DELL_CMD_GET_FC_LINK		0x18
#define DELL_CMD_GET_HOST_CNTRL		0x19
#define DELL_CMD_GET_PAYLOAD		0x1a
#define DELL_CMD_GET_ISCSI_STS		0x1b
#define DELL_CMD_GET_OS			0x1c
#define DELL_CMD_GET_ISCSI_IPRM		0x1d
#define DELL_CMD_SET_ISCSI_IPRM		0x1e
#define DELL_CMD_GET_ISCSI_TPRM		0x1f
#define DELL_CMD_SET_ISCSI_TPRM		0x20
#define DELL_CMD_GET_FCOE_TPRM		0x21
#define DELL_CMD_SET_FCOE_TPRM		0x22
#define DELL_CMD_COMMIT		        0x23
#define DELL_CMD_COMMIT_STS	        0x24
#define DELL_CMD_GET_LINKTUNE		0x25
#define DELL_CMD_GET_PF_ASSNMT		0x26
#define DELL_CMD_GET_RDMA_STATS         0x27
#define DELL_CMD_GET_LLDP		0x28
#define DELL_CMD_GET_INTERFACE_INFO	0x29
#define DELL_CMD_GET_INTERFACE_SENSOR	0x2a
#define DELL_CMD_SEND_LLDP		0x62
#define DELL_CMD_MAX                    0x62

/* dell response codes */
#define DELL_COMMAND_SUCCESS		0x0000
#define DELL_RESP_NPAR_DISABLED		0x8000
#define DELL_RESP_FUNC_DISABLED		0x8001
#define DELL_RESP_FUNC_NOT_ASSOC	0x8002
#define DELL_RESP_REBOOT_REQD		0x8003
#define DELL_RESP_INVAL_LEN	        0x8004
#define DELL_RESP_UNAVAIL	        0x8005
#define DELL_RESP_UNSUPPORT_ADRS	0x8006
#define DELL_REASON_UNSUP_PT		0x8007
#define DELL_RESP_MAX_PORTS	        0x8008
#define DELL_RESP_RBT_RQRD	        0x8009
#define DELL_UNSUPPORTED_PAYLOAD	0x800a
#define DELL_DRIVER_NOT_LOADED		0x800b
#define DELL_LINK_CMD_FAILED		0x800c
#define DELL_STORAGE_EXCEEDED		0x800d
#define DELL_WRITE_FAILED	        0x800e
#define DELL_WRITE_PENDING	        0x800f
#define DELL_COMMIT_REQD		0x8011
#define DELL_VMAIN_REQD			0x8012
#define DELL_LINK_ERR			0x8013

#define IS_IPv4(x)			is_ipv4((char *)tlv->data, (int)tlv->len, (char *)x)
#define IS_IPv6(x)			is_ipv6((char *)tlv->data, (int)tlv->len, (char *)x)
#define STR2NUM(x)			str2num((char *)tlv->data, ' ', (int)tlv->len, (unsigned char *)x, 10, sizeof(uint32_t))
#define STR2MAC(x)			str2num((char *)tlv->data, ':', (int)tlv->len, (unsigned char *)x, 16, sizeof(uint8_t))
#define STR2TOK(l,s,v)			str2tok((char *)tlv->data, (int)tlv->len, l, s, (char *)v)
#define SET_PID(x)			((x) & 0x3f)
#define GET_PID(x)			((x) & 0x3f)

#define PARTITION(n)			(1 << n)

#define DEFINE_DELL_HDR			ncsi_dell_hdr_t *dhdr = (ncsi_dell_hdr_t *)vptr
#define SET_DELL_HDR			ncsi_dell_hdr_t *dell = (ncsi_dell_hdr_t *)resp->data
#define SET_DELL_NULL_RSPN		ncsi_dell_pid_rsvd_null_respn_t *rspn = (ncsi_dell_pid_rsvd_null_respn_t *)dell->data

#define INVALID_PART(hdlr)	((hdlr->chk_flag & CHECK_PID) && (!valid_mapping(ncsi->chan, pid)) && (!(hdlr->chk_flag & SPECIAL_MAP)))
#define INVALID_PID(hdlr)	((hdlr->chk_flag & CHECK_PID) && (func_disabled(pid) || (pid >= MCP_GLOB_FUNC_MAX)))

#define IPv4_TYPE	1
#define IPv6_TYPE	2
#define STR_TYPE	3
#define NUM_TYPE	4
#define MAC_TYPE	5
#define ENBDIS_TYPE	6
#define IP_TYPE		7
#define WW_TYPE		8

#define SET_TLV(dell_type, prm_type, arg...)			\
	do {							\
		tlv->type = (dell_type);			\
		noftlv++;					\
		len += construct_tlv(&tlv, (prm_type), ##arg);	\
	} while (0)

/* dell inventory constants */
#define DELL_DEVICE_NAME_CONST		0x00
#define DELL_VENDOR_NAME_CONST		0x01

/* dell partition types */
#define DELL_LAN_PART_TYPE		BIT(3)
#define DELL_ISCSI_PART_TYPE		BIT(4)
#define DELL_FCOE_PART_TYPE		BIT(5)
#define DELL_RDMA_PART_TYPE		BIT(6)
#define DELL_FC_PART_TYPE		BIT(7)

/* define dell media type */
#define DELL_MEDIA_TYPE_BASE_T		BIT(0)
#define DELL_MEDIA_TYPE_BASE_KR		BIT(1)
#define DELL_MEDIA_TYPE_BASE_KX		BIT(2)
#define DELL_MEDIA_TYPE_BASE_KX4	BIT(3)
#define DELL_MEDIA_TYPE_SR		BIT(4)
#define DELL_MEDIA_TYPE_SFP		BIT(5)
#define DELL_MEDIA_TYPE_SFP_PLUS	BIT(6)
#define DELL_MEDIA_TYPE_DCA		BIT(7)
#define DELL_MEDIA_TYPE_FC		BIT(8)
#define DELL_MEDIA_BACKPLANE		BIT(9)
#define DELL_MEDIA_SFF_CAGE		BIT(10)

/* dell Payload version numbers */
#define DELL_PAYLOAD_VERSION_1		(1 << 1)
#define DELL_PAYLOAD_VERSION_2		(1 << 2)

#define DELL_PAYLOAD_SIZE	        (sizeof(*rspn) + sizeof(*dell))

/* dell header */
typedef struct __attribute__((packed)) {
	uint32_t oem;
	uint8_t	rev;
	uint8_t	cmd;
	uint8_t	data[0];
} ncsi_dell_hdr_t, ncsi_dell_resp_t;

/* dell null response */
typedef struct  __attribute__((packed)) {
	uint8_t	data[0];
} ncsi_dell_null_respn_t;

/* dell null with pid response */
typedef struct  __attribute__((packed)) {
        uint8_t pid;
        uint8_t data[0];
} ncsi_dell_pid_null_respn_t;

/* dell null with pid and reserved response */
typedef struct __attribute__((packed)) {
	uint8_t	pid;
	uint8_t	rsvd;
	uint8_t	data[0];
} ncsi_dell_pid_rsvd_null_respn_t;

/* dell tlv */
typedef struct __attribute__((packed)) {
	uint8_t	len;
	uint8_t	type;
	uint8_t	data[0];	
} ncsi_dell_tlv;

#define DELL_DEVICE_NAME_TYPE	0
#define DELL_VENDOR_NAME_TYPE	1
/* dell inventory */
typedef struct __attribute__((packed)) {
	uint8_t media[2];
	uint8_t	f_major;
	uint8_t	f_minor;
	uint8_t	f_build;
	uint8_t	f_sub;
	uint8_t	d_major;
	uint8_t	d_minor;
	uint8_t	d_build;
	uint8_t	d_sub;
	uint8_t	data[0];
} ncsi_dell_inventory_t;

/* dell capabilities */
typedef struct __attribute__((packed)) {
	uint8_t	caps[4];
	uint8_t	rsvd;
	uint8_t	dcb_cap;
	uint8_t	nic_part_cap;
	uint8_t	e_switch_cap;
	uint8_t	phy_fns;
	uint8_t	virt_fns;
	uint8_t	data[0];
} ncsi_dell_get_ext_cap_t;

/* dell partition info */
typedef struct __attribute__((packed)) {
	uint8_t	phy_fns_en;
	uint8_t	data[0];
} ncsi_dell_get_part_info_t;

/* dell partition info */
typedef struct __attribute__((packed)) {
	uint8_t pid;
	uint16_t status;
	ncsi_dell_tlv	tlv;
} ncsi_dell_part_info;

/* dell address */
#define DELL_PERM_ADDR		0
#define DELL_FLEX_ADDR		1
typedef struct __attribute__((packed)) {
	uint8_t	pid;
	uint8_t	data[0];
} ncsi_dell_get_addr_hdr_t;

/* dell license */
typedef struct __attribute__((packed)) {
	uint8_t	storage_type;
	uint8_t	rsvd;
	uint8_t	enabled_feature_bitmap[4];
	uint8_t	feature_cap_bitmap[4];
	uint8_t	unique_identifier[4];
	uint8_t	entlmntid_plus_obj[4];
} ncsi_dell_get_license_t;

/* dell virtual link */
typedef struct __attribute__((packed)) {
	uint8_t	pid;
	uint8_t	link;
} ncsi_dell_get_virtual_link_t;

/* dell temperatuer */
typedef struct __attribute__((packed)) {
	uint8_t	max_temp;
	uint8_t	cur_temp;
} ncsi_dell_get_temperature_t;

/* dell get payload version */
typedef struct __attribute__((packed)) {
	uint8_t ver[2];
	uint8_t	rsvd[4];
} ncsi_dell_get_payload_version_t;

/* dell get os driver version */
typedef struct __attribute__((packed)) {
	uint8_t	pid;
	uint8_t	noftlv;
	uint8_t	data[0];
} ncsi_dell_get_os_driver_t;

typedef struct __attribute__((packed)) {
	uint8_t type:7, len_h:1;
	uint8_t len;
	uint8_t data[0];
} lldp_generic_tlv_t;
	
#define NO_PID_CHECK		0
#define PID_CHECK	        1

void dell_failed_response(ncsi_resp_t *, uint16_t, uint16_t);
void dell_reboot_required(ncsi_resp_t *, int);
void dell_commit_required(ncsi_resp_t *, int);
void dell_cmd_unknown(uint32_t, void *, ncsi_resp_t *);
void dell_panding(ncsi_resp_t *, int);

#endif /* _NCSI_DELL_CMD_HDR_	*/
