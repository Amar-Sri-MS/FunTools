/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Funible. All rights reserved.
 */
#ifndef _INC_NCSI_PROTO_HDR_
#define _INC_NCSI_PROTO_HDR_

#include <stdint.h>
#include "auto_conf.h"

#define ncsi_err(fmt, arg...)		log_n_print("NCSI: ERROR - "fmt, ##arg)
#define ncsi_dbg(fmt, arg...)		if (cfg.debug & NCSI_DEBUG) printf("%s: "fmt, __func__, ##arg)

#ifndef NULL
#define NULL                    ((void *)0)
#endif

#ifndef BIT
#define BIT(n)                  (1 << (n))
#endif

#ifdef CONFIG_VER_1_1_0_SUPPORT
#define NCSI_VER_NUM_MAJOR              0xf1
#define NCSI_VER_NUM_MINOR              0xf1
#define NCSI_VER_NUM_UPDATE             0xf0
#define NCSI_VER_NUM_ALPHA              0x00
#else
#define NCSI_VER_NUM_MAJOR		0xf1
#define NCSI_VER_NUM_MINOR		0xf0
#define NCSI_VER_NUM_UPDATE		0xf1
#define NCSI_VER_NUM_ALPHA		0x00
#endif /* CONFIG_VER_1_1_0_SUPPORT */

/* ncsi states */
#define NCSI_PKG_RST		    	0
#define NCSI_PKG_DESEL          	1
#define NCSI_PKG_SEL            	3
#define NCSI_CHN_RDY            	7
#define NCSI_PKG_DESEL_RDY      	5

/* interface constants */
#define RMII_IF			        BIT(0)
#define SMBUS_IF		        BIT(1)
#define VDM_IF				BIT(2)
#define ALL_IFS         	    	(RMII_IF | SMBUS_IF | VDM_IF)

/* default package id should come from gpio,
 * since fc cards do not have this feature - set to 1
 */
#define DEFAULT_PACKAGE_ID		1

/* check flags */
#define NO_CHECK                	0
#define CHECK_CHAN              	BIT(0)
#define CHECK_PID               	BIT(1)
#define CHECK_LOWPWR            	BIT(2)
#define CHECK_STAGE0            	BIT(3)
#define CHECK_INIT              	BIT(4)
#define CMD_DISABLED		    	BIT(5)
#define CHECK_LINK		        BIT(6)
#define CHECK_CHAN_1F		    	BIT(7)
#define SPECIAL_MAP	            	BIT(8)

/* check macros */
#define INVALID_CMD(max)	(cmd > max)
#define INVALID_INTRFC(hdlr) 	(!(hdlr->interface & interface))
#define INVALID_CHAN(hdlr)   	((!(hdlr->chk_flag & CHECK_CHAN_1F)) && (ncsi->chan == 0x1f))
#define INIT_REQUIRED(hdlr)  	((hdlr->chk_flag & CHECK_INIT) && (ncsi_state.channel[ncsi->chan].state != NCSI_CHN_RDY))
#define DISABLED_CMD(hdlr)	(hdlr->chk_flag & CMD_DISABLED)
#define NO_LINK(hdlr)	    	((hdlr->chk_flag & CHECK_LINK) && (!(get_link(ncsi->chan))))
#define INVALID_1F(hdlr)	((!(hdlr->chk_flag & CHECK_CHAN_1F)) && (ncsi->chan == 0x1f))
#define CHAN_ISNT_1F		(ncsi->chan != 0x1f)
#define SPECIAL_MAPPING		(hdlr->chk_flag & CHECK_SPECIAL)

/* ncsi command mapping */
#define NCSI_CMD_CLEAR_INIT		0x00
#define NCSI_CMD_PKG_SELECT		0x01
#define NCSI_CMD_PKG_DESELECT		0x02
#define NCSI_CMD_CHAN_ENABLE		0x03
#define NCSI_CMD_CHAN_DISABLE		0x04
#define NCSI_CMD_CHAN_RESET		0x05
#define NCSI_CMD_TX_ENABLE		0x06
#define NCSI_CMD_TX_DISABLE		0x07
#define NCSI_CMD_AEN_ENABLE		0x08
#define NCSI_CMD_LINK_SET		0x09
#define NCSI_CMD_LINK_GET		0x0a
#define NCSI_CMD_VLAN_SET		0x0b
#define NCSI_CMD_VLAN_ENABLE		0x0c
#define NCSI_CMD_VLAN_DISABLE		0x0d
#define NCSI_CMD_MAC_SET		0x0e
#define NCSI_CMD_BCAST_ENABLE		0x10
#define NCSI_CMD_BCAST_DISABLE		0x11
#define NCSI_CMD_MCAST_ENABLE		0x12
#define NCSI_CMD_MCAST_DISABLE		0x13
#define NCSI_CMD_FLOW_CTL		0x14
#define NCSI_CMD_GET_VER		0x15
#define NCSI_CMD_GET_CAP		0x16
#define NCSI_CMD_GET_PARAM		0x17
#define NCSI_CMD_STATS_PKT		0x18
#define NCSI_CMD_STATS_NCSI		0x19
#define NCSI_CMD_STATS_THRU		0x1A
#define NCSI_CMD_OEM			0x50
#define NCSI_CMD_PLDM			0x51
#define NCSI_MAX_CMD                	0x52

/* Response codes */
#define NCSI_RESP_SUCCESS       	0x0000
#define NCSI_RESP_FAIL          	0x0001
#define NCSI_RESP_UNAVAIL		0x0002
#define NCSI_RESP_UNSUPPORT        	0x0003

/* Reason codes */
#define NCSI_REASON_NONE          	0x0000
#define NCSI_REASON_INIT           	0x0001
#define NCSI_REASON_INVAL          	0x0002
#define NCSI_REASON_BUSY_CHAN      	0x0003
#define NCSI_REASON_BUSY_PKG    	0x0004
#define NCSI_REASON_LEN       		0x0005
#define NCSI_REASON_VLAN_0		0x0007
#define NCSI_REASON_MAC_0		0x0008
#define NCSI_REASON_UNSUPPORT     	0x7fff

/* capabilities */
#define NCSI_CAP_HWARB			BIT(0)
#define NCSI_CAP_OS			BIT(1)
#define NCSI_CAP_FLOW_OUT		BIT(2)
#define NCSI_CAP_FLOW_IN		BIT(3)
#define NCSI_CAP_MCAST			BIT(4)
#define HW_ARB_NOT_IMPLEMENTED		BIT(5)

/* set link */
#define SET_LINK_AUTONEG_BIT		BIT(0)
#define SET_LINK_ENA_10MB		BIT(1)
#define SET_LINK_ENA_100MB		BIT(2)
#define SET_LINK_ENA_1G			BIT(3)
#define SET_LINK_ENA_10G		BIT(4)
#define SET_LINK_ENA_HD			BIT(8)
#define SET_LINK_ENA_FD			BIT(9)
#define SET_LINK_ENA_PAUSE		BIT(10)
#define SET_LINK_ENA_ASY_PAUSE		BIT(11)
#define SET_LINK_OEM_VALID		BIT(12)
/* dsp0222 ver1.1.0 specs */
#define SET_LINK_ENA_20G		BIT(5)
#define SET_LINK_ENA_25G		BIT(6)
#define SET_LINK_ENA_40G		BIT(7)
#define SET_LINK_ENA_50G		BIT(13)
#define SET_LINK_ENA_100G		BIT(14)

/* AEN capabilities */
#define NCSI_AEN_LINK			BIT(0)
#define NCSI_AEN_CONFIG			BIT(1)
#define NCSI_AEN_DRV_STATUS		BIT(2)

/* ncsi state valid signature */
#define NCSI_STATE_SIGNATURE		(0x4E435349 + 1)

/* ncsi checksum length */
#define NCSI_CHEKSUM_LEN		4

/* define max. number of supported ports */
#define MAX_NUM_OF_PORTS		1

/* define #of mac/vlan for passthrough */
#define MAX_NCSI_UNICAST		6
#define MAX_NCSI_VLAN			3

/* default package id */
#define NCSI_DEFAULT_PACKAGE_ID		0

/* IANA OEM flags */
#define INIT_DONE               BIT(0)
#define IANA_ENB                BIT(1)

#define NCSI_CMD_RECV		BIT(0)
#define NCSI_CMD_DROP		BIT(1)
#define NCSI_CMD_ERR		BIT(2)
#define NCSI_CMD_CHKSM		BIT(3)
#define NCSI_AEN_CNT		BIT(4)
#define NCSI_RX			BIT(5)
#define NCSI_TX			BIT(6)

/* bc filters */
#define NCSI_BC_FORWARD_ARP	BIT(0)
#define NCSI_BC_FORWARD_DHCPC	BIT(1)
#define NCSI_BC_FORWARD_DHCPS	BIT(2)
#define NCSI_BC_FORWARD_NETBIOS	BIT(3)

/* mc filters */
#define NCSI_MC_IPv6_NEIGH_ADV	BIT(0)
#define NCSI_MC_IPv6_ROUTER_ADV	BIT(1)
#define NCSI_MC_DHCPv6_SERVER	BIT(2)
#define NCSI_MC_DHCPv6_CLIENT	BIT(3)
#define NCSI_MC_IPv6_MLD	BIT(4)
#define NCSI_MC_IPv6_NEIGH_SOL	BIT(5)

/* ncsi statistics */
typedef struct {
	uint32_t recv;
	uint32_t drop;
	uint32_t err;
	uint32_t chksm;
	uint32_t tx;
	uint32_t aen;
} ncsi_statistics_t;

typedef struct {
	uint8_t addr[6];
} mac_addr_stct;

/* configuration status */
#define BCAST_FILTER_ENABLED	BIT(0)
#define CHANNEL_ENABLED		BIT(1)
#define CHANNEL_TX_ENABLED	BIT(2)
#define MCAST_FILTER_ENABLED	BIT(3)

/* channal state */
typedef struct {
	uint8_t state;
	uint8_t vlan_mode:4, stats_rd:1, nw2bmc:1, os2bmc:1;
	uint8_t ucast_ena;
	uint8_t vlan_ena;
	uint32_t link;
	uint32_t config;
	uint8_t bc_filters;
	uint8_t mc_filters;
	mac_addr_stct ucast[MAX_NCSI_UNICAST];
	uint16_t vlan_tag[MAX_NCSI_VLAN];
	uint32_t aen_events;
	uint8_t aen_mcid;
} ncsi_chan_state_t;

/* ncsi state structure */
typedef struct {
	uint32_t signature;
	uint8_t pkgid;
	uint8_t max_ports;
	uint8_t pkg_down:1, pkg_sel:1, chksum_en:1, align_len:1, check_en:1, fc_ena:2, apply_mac:1;
	uint8_t resv; /*alignment*/ 
	ncsi_chan_state_t channel[MAX_NUM_OF_PORTS];
	ncsi_statistics_t stats;
} ncsi_state_t;


/* ncsi header */
typedef struct __attribute__((packed)) {
	uint8_t	 mcid;
	uint8_t	 rev;
	uint8_t	 res1;
	uint8_t	 iid;
	uint8_t	 cmd;
#ifndef ARCH_BIG_ENDIAN
	uint8_t	 chan:5, pkgid:3;
#else
	uint8_t pkgid:3, chan:5;
#endif
	uint16_t len;
	uint32_t res3;
	uint32_t res4;
	uint8_t data[0];
} ncsi_hdr_t;

/* aen packet header */
typedef struct __attribute__((packed)) {
	uint8_t res[3];
	uint8_t type;
	uint8_t data[0];
} aen_hdr_t;

typedef struct __attribute__((packed)) {
	uint32_t status;
	uint32_t oem;
} aen_link_status_t;

typedef struct __attribute__((packed)) {
	uint32_t status;
} aen_driver_status_t;

/* ncsi response header */
typedef struct  __attribute__((packed)) {
	ncsi_hdr_t hdr;
	uint16_t response;
	uint16_t reason;
	uint8_t	 data[0];
} ncsi_resp_t;

typedef struct  __attribute__((packed)) {
	uint8_t	maj;
	uint8_t	min;
	uint8_t	upd;
	uint8_t	alpha1;
	uint8_t	resv[3];
	uint8_t	alpha2;
	uint8_t	fw_name[12];
	uint32_t fw_ver;
	uint16_t did;
	uint16_t vid;
	uint16_t ssid;
	uint16_t svid;
	uint32_t iana;
} ncsi_ver_resp_t;

typedef struct __attribute__((packed)) {
	uint32_t flags;
	uint32_t bcast;
	uint32_t mcast;
	uint32_t buff;
	uint32_t aen;
	uint8_t	 vlan_cnt;
	uint8_t	 mix_cnt;
	uint8_t	 mcast_cnt;
	uint8_t	 ucast_cnt;
	uint8_t	 resv[2];
	uint8_t	 vlan_mode;
	uint8_t	 chan_cnt;
} ncsi_cap_resp_t;

typedef struct __attribute__((packed)) {
	uint8_t	mac_cnt;
	uint8_t rsvd0[2];
	uint8_t	mac_flags;
	uint8_t	vlan_cnt;
	uint8_t	rsvd1;
	uint16_t vlan_flags;
	uint32_t lnk_set;
	uint32_t bcst_set;
	uint32_t cfg_flags;
	uint8_t	vlan_mode;
	uint8_t	flow_ctl;
	uint8_t rsvd2[2];
	uint32_t aen_ctrl;
	uint8_t	data[0];
} ncsi_get_parm_resp_t;

typedef struct __attribute__((packed)) {
	uint32_t cmd_cnt;
	uint32_t cmd_drop;
	uint32_t cmd_err;
	uint32_t cmd_cksum;
	uint32_t rx_pkt;
	uint32_t tx_pkt;
	uint32_t aen_cnt;
} ncsi_stats_ncsi_resp_t;

/* get link status */
#define NCSI_LINK_DOWN		0
#define NCSI_LINK_UP		1

#ifdef CONFIG_VER_1_1_0_SUPPORT
/* DSP0222 v1.1.0 link speed */
#define NCSI_10BASET_HD		(0x01 << 1)
#define NCSI_10BASET_FD		(0x02 << 1)
#define NCSI_100BASETX_HD	(0x03 << 1)
#define NCSI_100BASET4		(0x04 << 1)
#define NCSI_100BASETX_FD	(0x05 << 1)
#define NCSI_1GBASET_HD		(0x06 << 1)
#define NCSI_1GBASET_FD		(0x07 << 1)
#define NCSI_10GBASET		(0x08 << 1)
#define NCSI_20G		(0x09 << 1)
#define NCSI_25G		(0x0a << 1)
#define NCSI_40G		(0x0b << 1)
#define NCSI_50G		(0x0c << 1)
#define NCSI_100G		(0x0d << 1)
#else
#define NCSI_10BASET_HD		(1 << 1)
#define NCSI_10BASET_FD		(2 << 1)
#define NCSI_100BASETX_HD	(3 << 1)
#define NCSI_100BASET4		(4 << 1)
#define NCSI_100BASETX_FD	(5 << 1)
#define NCSI_1GBASET_HD		(6 << 1)
#define NCSI_1GBASET_FD		(7 << 1)
#define NCSI_10GBASET		(8 << 1)
#endif /* CONFIG_VER_1_1_0_SUPPORT */

#define NCSI_AUTONEG_ENA	BIT(5)
#define NCSI_AUTONEG_COMP	BIT(6)
#define NCSI_PAR_DETECT		BIT(7)
#define NCSI_PARTNER_10GFD	BIT(9)
#define NCSI_PARTNER_10GHD	BIT(10)
#define NCSI_PARTNER_100T4	BIT(11)
#define NCSI_PARTNER_100TX_FD	BIT(12)
#define NCSI_PARTNER_100TX_HD	BIT(13)
#define NCSI_PARTNER_10T_FD	BIT(14)
#define NCSI_PARTNER_10T_HD	BIT(15)
#define NCSI_TX_FLOWC_ENA	BIT(16)
#define NCSI_RX_FLOWC_ENA	BIT(17)
#define NCSI_SERDES_LINK_USED	BIT(20)

typedef struct __attribute__((packed)) {
	uint32_t status;
	uint32_t other;
	uint32_t oem;
	uint8_t	 data[0];
} ncsi_get_link_resp_hdr_t;

typedef struct __attribute__((packed)) {
	uint32_t rsvd:24, had:8;
} ncsi_pkg_sel_t;
	
typedef struct __attribute__((packed)) {
	uint8_t rsrvd[3];
	uint8_t mcid;
	uint32_t ctrl;
} ncsi_aen_enable_t;

typedef struct __attribute__((packed)) {
	uint32_t link;
	uint32_t oem;
} ncsi_set_link_t;

typedef struct __attribute__((packed)) {
	uint16_t rsvd0;
	uint16_t id;
	uint16_t rsvd1;
	uint8_t	 index;
	uint8_t	 ena:1, rsvd2:7;
} ncsi_set_vlan_t;

#define NCSI_FILTER_ENABLE		1
#define NCSI_FILTER_DISABLE		0
typedef struct __attribute__((packed)) {
	uint32_t mode:8, rsvd:24;
} enable_vlan_t;

typedef struct __attribute__((packed)) {
	uint8_t	 addr[6];
	uint8_t	 index;
	uint8_t	 ena:1, rsvd:6, type:1;
} ncsi_mac_cmd_t;

#define NCSI_BC_FILTER_ARP		BIT(0)
#define NCSI_BC_FILTER_DHCPC		BIT(1)
#define NCSI_BC_FILTER_DHCPS		BIT(2)
#define NCSI_BC_FILTER_NETBIOS		BIT(3)

#define NCSI_MC_FILTER_IPv6_NEIGH	BIT(0)
#define NCSI_MC_FILTER_IPv6_ROUTE	BIT(1)
#define NCSI_MC_FILTER_DHCPv6		BIT(2)
typedef struct __attribute__((packed)) {
	uint32_t setting;
} ncsi_bcast_ena_t;

typedef struct __attribute__((packed)) {
	uint8_t rsrvd[3];
	uint8_t ena;
} ncsi_flow_control_t;

typedef struct __attribute__ ((packed)) {
	uint64_t clrd;
	uint64_t rx_bytes;
	uint64_t tx_bytes;
	uint64_t rx_upkt;
	uint64_t rx_mpkt;
	uint64_t rx_bpkt;
	uint64_t tx_upkt;
	uint64_t tx_mpkt;
	uint64_t tx_bpkt;
	uint32_t fcs_err;
	uint32_t align_err;
	uint32_t false_crr;
	uint32_t runt_rx;
	uint32_t jbbr_rx;
	uint32_t xon_rx;
	uint32_t xoff_rx;
	uint32_t xon_tx;
	uint32_t xoff_tx;
	uint32_t sngl_clsn;
	uint32_t mult_clsn;
	uint32_t late_clsn;
	uint32_t exsv_clsn;
	uint32_t ctrl_rx;
	uint32_t rx64;
	uint32_t rx127;
	uint32_t rx255;
	uint32_t rx511;
	uint32_t rx1023;
	uint32_t rx1522;
	uint32_t rx9022;
	uint32_t tx64;
	uint32_t tx127;
	uint32_t tx255;
	uint32_t tx511;
	uint32_t tx1023;
	uint32_t tx1522;
	uint32_t tx9022;
	uint64_t valid_rx;
	uint32_t err_runt_rx;
	uint32_t err_jbbr_rx;
} ncsi_stats_resp_t;

typedef struct __attribute__((packed)) {
	uint64_t tx_pkt;
	uint32_t tx_drop;
	uint32_t tx_err;
	uint32_t tx_under;
	uint32_t tx_over;
	uint32_t rx_pkt;
	uint32_t rx_drop;
	uint32_t rx_err;
	uint32_t rx_under;
	uint32_t rx_over;
} ncsi_stats_thru_resp_t;

typedef struct __attribute__((packed)) {
	uint32_t status;
} ncsi_pkg_status_resp_t;

typedef struct __attribute__((packed)) {
        uint32_t iana;
        uint8_t data[0];
} ncsi_oem_t;



typedef void(*ncsi_func)(ncsi_hdr_t *, ncsi_resp_t *);
typedef struct {
	uint8_t cmd;
	uint8_t chk_flag;
	ncsi_func func;
} ncsi_cmd_handler_t;

extern ncsi_cmd_handler_t ncsi_cmds[];

typedef struct {
	uint32_t iana;
	uint32_t flags:16, max:16;
	uint32_t hit;
	void (*init)(void *);
	void (*hdlr)(void *, uint32_t, ncsi_hdr_t *, ncsi_resp_t *);
} ncsi_oem_handler_t;

typedef void(*func_handler)(uint32_t, void *, ncsi_resp_t *);
typedef struct {
	uint32_t iana;
	uint32_t chk_flag:16, interface:8, cmd:8;
	func_handler func;
} oem_cmd_stc_t;

extern ncsi_state_t ncsi_state;
extern ncsi_statistics_t ncsi_stats;

uint32_t checksum(uint8_t *, int, int);
uint32_t get_link_status(uint8_t);
void ncsi_clear_stats(void);
void ncsi_change_state(uint8_t, uint8_t);
void ncsi_incr_stats(uint32_t);
void ncsi_success_response(ncsi_resp_t *, int);
void ncsi_failed_cmd_specific(ncsi_resp_t *, uint8_t, uint16_t);
void ncsi_failed_response(ncsi_resp_t *, uint16_t);
void ncsi_unspprt_response(ncsi_resp_t *, int);
void ncsi_invalid_response(ncsi_resp_t *);
void ncsi_cmd_unsupported(ncsi_hdr_t *, ncsi_resp_t *);
void ncsi_generic_response(ncsi_resp_t *, uint16_t, uint16_t, int);
void ncsi_init_required_response(ncsi_resp_t *);
int ncsi_handler(uint8_t *, int, uint8_t *);
void ncsi_init(void);

#endif /* _INC_NCSI_PROTO_HDR_ */
