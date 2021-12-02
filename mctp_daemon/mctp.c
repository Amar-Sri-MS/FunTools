/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fung ible. All rights reserved.
 */
#include <stdio.h>
#include <string.h>

#include "utils.h"
#include "mctp.h"
#include "pldm.h"

/* local variables */
static mctp_stats_t mctp_sts;

/* smbus requires additional byte for slave address */
#define MCTP_HDR_EP_EXTRA(ep)		(((ep)->l2type == MCTP_TRANSPORT_SMBUS) ? 1 : 0)
#define MCTP_HDR_SIZE(ep)		(sizeof(mctp_hdr_stct) + ((ep->flags & MCTP_COMPLETE) ? 1 : 0))
#define MCTP_SUPPORT_TYPE(ep, n)	((ep)->retain->support & (n))

/* mctp set eid command */
static int mctp_cmd_eid_set(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_set_eid_resp_t *rspn = (mctp_set_eid_resp_t *)buf;
	uint8_t eid = hdr->data[1];
	struct mctp_ep_retain_stc *retain;

	if (!ep->retain) 
		return ERR_NO_RETAIN;

	retain = ep->retain;

	if ((eid != 0) && (eid != 0xff)) {
		retain->eid = eid;
		rspn->reason = MCTP_RESP_SUCCESS;
	}
	else {
		rspn->reason = MCTP_RESP_INVAL_DATA;
	}

	rspn->status = 0;
	rspn->eid = retain->eid;
	rspn->pool_size = 0;

	return sizeof(mctp_set_eid_resp_t);
}

/* mctp get eid command */
static int mctp_cmd_eid_get(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_get_eid_resp_t *rspn = (mctp_get_eid_resp_t *)buf;
	struct mctp_ep_retain_stc *retain;

	if (!ep->retain) 
		return ERR_NO_RETAIN;

	retain = ep->retain;

	rspn->reason = MCTP_RESP_SUCCESS;
	rspn->eid = retain->eid;
	rspn->eid_type = 0;
	rspn->data = 0;

	return sizeof(mctp_get_eid_resp_t);
}

/* mctp get udid command */
static int mctp_cmd_uuid_get(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_get_udid_resp_t *rspn = (mctp_get_udid_resp_t *)buf;

	rspn->reason = MCTP_RESP_SUCCESS;
	memcpy(&rspn->udid, ep->retain->uuid, sizeof(ep->retain->uuid));

	return sizeof(mctp_get_udid_resp_t);
}

/* mctp get version command */
static int mctp_cmd_version_get(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_get_version_resp_t *rspn = (mctp_get_version_resp_t *)buf;
	mctp_ver_t *ver = (mctp_ver_t *)rspn->data;
	uint8_t type = hdr->data[0];

	rspn->reason = MCTP_RESP_SUCCESS;
	rspn->ent_cnt = 1;

	switch (type) {
	case MCTP_BASE_PROTOCOL:
		ver->major = MCTP_CTRL_VER_NUM_MAJOR;
		ver->minor = MCTP_CTRL_VER_NUM_MINOR;
		ver->update = MCTP_CTRL_VER_NUM_UPDATE;
		ver->alpha = MCTP_CTRL_VER_NUM_ALPHA;
		break;

	case MCTP_MSG_CONTROL:
		ver->major = MCTP_CTRL_VER_NUM_MAJOR;
		ver->minor = MCTP_CTRL_VER_NUM_MINOR;
		ver->update = MCTP_CTRL_VER_NUM_UPDATE;
		ver->alpha = MCTP_CTRL_VER_NUM_ALPHA;
		break;

#ifdef CONFIG_PLDM_SUPPORT
	case MCTP_MSG_PLDM:
		ver->major = PLDM_VER_NUM_MAJOR;
		ver->minor = PLDM_VER_NUM_MINOR;
		ver->update = PLDM_VER_NUM_UPDATE;
		ver->alpha = PLDM_VER_NUM_ALPHA;
		rspn->ent_cnt++;
		ver = (mctp_ver_t *)ver->data;
		ver->major = PLDM_VER_NUM_MAJOR;
		ver->minor = 0xf0;
		ver->update = PLDM_VER_NUM_UPDATE;
		ver->alpha = PLDM_VER_NUM_ALPHA;	
		break;
#endif

#ifdef CONFIG_NCSI_SUPPORT
	case MCTP_MSG_NCSI:
		if (!NCSI_ENABLED) {
			rspn->reason = MCTP_MSG_TYPE_NOT_SUPPORTED;
			break;
		}
		ver->major = NCSI_VER_NUM_MAJOR;
		ver->minor = NCSI_VER_NUM_MINOR;
		ver->update = NCSI_VER_NUM_UPDATE;
		ver->alpha = NCSI_VER_NUM_ALPHA;
		rspn->ent_cnt++;
		ver = (mctp_ver_t *)ver->data;
		ver->major = NCSI_VER_NUM_MAJOR;
		ver->minor = 0xf0;
		ver->update = NCSI_VER_NUM_UPDATE;
		ver->alpha = NCSI_VER_NUM_ALPHA;
		break;
#endif
	default:
		rspn->reason = MCTP_MSG_TYPE_NOT_SUPPORTED;
	}

	return (sizeof(mctp_get_version_resp_t) + rspn->ent_cnt * sizeof(mctp_ver_t));
}

/* mctp get message command */
static int mctp_cmd_msg_get(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_get_msg_resp_t *rspn = (mctp_get_msg_resp_t *)buf;
	uint8_t *msg = rspn->data;

	*msg++ = MCTP_MSG_CONTROL;

#ifdef CONFIG_NCSI_SUPPORT
	if (MCTP_SUPPORT_TYPE(ep, SUPPORT_NCSI_OVER_MCTP)) {
		*msg++ = MCTP_MSG_NCSI;
	}
#endif

#ifdef CONFIG_PLDM_SUPPORT
	if (MCTP_SUPPORT_TYPE(ep, SUPPORT_PLDM_OVER_MCTP)) {
		*msg++ = MCTP_MSG_PLDM;
	}
#endif

#ifdef CONFIG_MCTP_VDM_PCI_SUPPORT
	if (MCTP_SUPPORT_TYPE(ep, SUPPORT_VDM_OVER_MCTP)) {
		*msg++ = MCTP_MSG_VDM_PCI;
	}
#endif

#ifdef CONFIG_MCTP_VDM_IANA
	if (MCTP_SUPPORT_TYPE(ep, SUPPORT_OEM_OVER_MCTP)) {
		*msg++ = MCTP_MSG_VDM_IANA;
	}
#endif

	rspn->msg_cnt = (uint8_t)(msg - rspn->data);
	rspn->reason = MCTP_RESP_SUCCESS;

	return (sizeof(mctp_get_msg_resp_t) + rspn->msg_cnt);
}

#if defined(CONFIG_HP_DCI_SUPPORT) || defined(CONFIG_HPE_AHS_SUPPORT)
/* mctp Get Vendor Defined Message Support command */
static int mctp_cmd_vdm_get(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_get_vdm_sup_resp_t *rspn = (mctp_get_vdm_sup_resp_t *)buf;
	uint8_t sel = hdr->data[0];

	if (hpe_vdm_get_support(&sel, rspn->data)) {
		rspn->sel = 0xff;
		rspn->code = MCTP_RESP_INVAL_DATA;
	} else {
		rspn->sel = sel;
		rspn->code = MCTP_RESP_SUCCESS;
	}

	return sizeof(mctp_get_vdm_sup_resp_t) + 5;
}
#endif

/* mctp unsupported command */
static int mctp_cmd_unsupported(uint8_t *buf, mctp_ctrl_hdr_t *hdr, mctp_endpoint_stct *ep)
{
	mctp_unsupported_resp_t *rspn = (mctp_unsupported_resp_t *)buf;
	rspn->reason = MCTP_RESP_SUPPORT;

	return sizeof(mctp_unsupported_resp_t);
}

/* mctp controll message handler */
static int mctp_control_handler(mctp_endpoint_stct *ep)
{
	mctp_ctrl_hdr_t *hdr = (mctp_ctrl_hdr_t *)ep->rx_ptr;
	mctp_ctrl_hdr_t *rspn = (mctp_ctrl_hdr_t *)ep->tx_ptr;
	int rc = 0;

	switch (hdr->cmd) {
	case MCTP_CMD_EID_SET:
		rc = mctp_cmd_eid_set(rspn->data, hdr, ep);
		break;

	case MCTP_CMD_EID_GET:
		rc = mctp_cmd_eid_get(rspn->data, hdr, ep);
		break;

	case MCTP_CMD_UUID_GET:
		rc = mctp_cmd_uuid_get(rspn->data, hdr, ep);
		break;

	case MCTP_CMD_VER_GET:
		rc = mctp_cmd_version_get(rspn->data, hdr, ep);
		break;

	case MCTP_CMD_MSG_GET:
		rc = mctp_cmd_msg_get(rspn->data, hdr, ep);
		break;

#if defined(CONFIG_HP_DCI_SUPPORT) || defined(CONFIG_HPE_AHS_SUPPORT)
	case MCTP_CMD_VDM_GET:
		rc = mctp_cmd_vdm_get(rspn->data, hdr, ep);
		break;
#endif

	default:
		rc = mctp_cmd_unsupported(rspn->data, hdr, ep);
	}

	rspn->cmd = hdr->cmd;
	rspn->rq = 0;
	rspn->d_bit = 0;
	rspn->iid = hdr->iid;

	return rc + sizeof(mctp_ctrl_hdr_t);
}

/* place holder for vendor defined messages handler */
static int vdm_pci_handler(uint8_t *buf, int len)
{
	int rc = -1;
	uint16_t vid = ((uint16_t)buf[0] << 8) | buf[1];

	switch (vid) {
#if defined(CONFIG_HP_DCI_SUPPORT) || defined(CONFIG_HPE_AHS_SUPPORT)
	case HP_PCI_VENDOR_ID:
	case HPE_PCI_VENDOR_ID:
		/* The ic bit should get from the mctp layer and passed to the handler, hardcoded 0 for now */
		rc = hpe_vdm_handler(buf, len, pktbuf, 0);
		break;
#endif
	default:
		rc = -1;
	}

	return rc;
}

static int vdm_iana_handler(uint8_t *buf, int len)
{
	return -1;
}

static void mctp_incr_stats(enum mctp_stats_enum sts)
{
	switch (sts) {
	case STOP:
		mctp_sts.stop++;
		return;

	case ABORT:
		mctp_sts.abort++;
		return;

	case ARB_LOST:
		mctp_sts.arb_lost++;
		return;

	case TIMEOUT:
		mctp_sts.timeout++;
		return;

	case BAD_MSG:
		mctp_sts.bad_msg++;
		break;
	}
}

#define CHECK_FOR_SUPPORT(ep, n)						\
	if (!MCTP_SUPPORT_TYPE(ep, n)) {					\
		mctp_err("msg type %02x is not supported\n", ep->msgtype);	\
		return -1;							\
	}
/* Common MCTP packet handler */
static int handle_mctp_pkt(mctp_endpoint_stct *ep)
{
	int rc = -1;

	switch (ep->msgtype) {
	case MCTP_MSG_CONTROL:
		CHECK_FOR_SUPPORT(ep, SUPPORT_MCTP_CNTROL_MSG);
		rc = mctp_control_handler(ep);
		break;

#ifdef CONFIG_PLDM_SUPPORT
	case MCTP_MSG_PLDM:
		CHECK_FOR_SUPPORT(ep, SUPPORT_PLDM_OVER_MCTP);
		rc = pldm_handler(ep->rx_ptr, ep->rx_len, NULL);
		break;
#endif

#ifdef CONFIG_NCSI_SUPPORT
	case MCTP_MSG_NCSI:
		CHECK_FOR_SUPPORT(ep, SUPPORT_NCSI_OVER_MCTP);
		rc = ncsi_handler(ep->rx_ptr, ep->retain->iid);
		break;
#endif

	case MCTP_MSG_VDM_PCI:
		CHECK_FOR_SUPPORT(ep, SUPPORT_VDM_OVER_MCTP);
		rc = vdm_pci_handler(ep->rx_ptr, ep->rx_len);
		break;

	case MCTP_MSG_VDM_IANA:
		CHECK_FOR_SUPPORT(ep, SUPPORT_OEM_OVER_MCTP);
		rc = vdm_iana_handler(ep->rx_ptr, ep->rx_len);
		break;

	default:
		mctp_incr_stats(BAD_MSG);
		mctp_err("unknown msg type %02x\n", ep->msgtype);
		break;
	}

	if (rc > 0) {
		ep->tx_len = (uint32_t )rc;
		mctp_transmit(ep);
		return 0;
	}

	return -1;
}

mctp_stats_t *get_mctp_sts(void)
{
	return &mctp_sts;
}

/* mctp receive routine */
int mctp_recieve(mctp_endpoint_stct *ep)
{
	mctp_hdr_stct *hdr;
	uint8_t *buf = ep->rx_pkt_buf;
	uint8_t len = ep->rx_cnt;
	struct mctp_ep_retain_stc *retain;

	if (!ep->retain) 
		return ERR_NO_RETAIN;

	retain = ep->retain;

	if (len <= sizeof(mctp_hdr_stct)) {
		mctp_err("rx pkt too small, len %u\n", len);
		return ERR_PKT_TOO_SMALL ;
	}

	hdr = (mctp_hdr_stct *)buf;
	buf += sizeof(mctp_hdr_stct);
	len -= sizeof(mctp_hdr_stct);

	if (hdr->dst_eid && (hdr->dst_eid != retain->eid)) {
		mctp_err("dest eid doesn't match\n");
		return ERR_BAD_SEID;
	}

	/* Start new packet, ignore previous incomplete ones */
	if (hdr->som) {
		/* save initial mctp header */
		ep->rx_len = 0;
		ep->ic = hdr->data[0] >> 7;
		ep->msgtype = hdr->data[0] & 0x7f;
		ep->src_eid = hdr->src_eid;

#ifdef CONFIG_CHECK_SEQ_NUM
		/* seq for som must be 0 */
		if (hdr->seq) {
			mctp_err("seq != 0\n");
			return ERR_BAD_SEQ_NUM;
		}
#endif
		ep->rxseq = hdr->seq;
		ep->tag = hdr->tag;
		ep->to = hdr->to;
		buf++;
		len--;
	} else if (((ep->rxseq + 1) & 0x3) != hdr->seq) {
			mctp_err("fragment lost\n");
			return ERR_BAD_SEQ_NUM;
	}

	ep->rxseq = hdr->seq;

	// Concatinate the incoming chunk
	memcpy(&ep->rx_ptr[ep->rx_len], buf, len);
	ep->rx_len += len;

	if (hdr->eom) {
		mctp_sts.rx_pkts++;
		mctp_sts.rx_bytes += ep->rx_len;
		return handle_mctp_pkt(ep);
	}

	return 0;
}

/* mctp transmit routine */
int mctp_transmit(mctp_endpoint_stct *ep)
{
	mctp_hdr_stct *hdr;
	uint8_t *buf;
	uint32_t len;
	struct mctp_ep_retain_stc *retain;

	if (!ep->retain)
		return ERR_NO_RETAIN;

	retain = ep->retain;

	if (ep->tx_len > MCTP_MAX_MESSAGE_DATA || !ep->tx_len) {
		mctp_err("payload exceeds MCTP_MAX_MESSAGE_DATA (%u)\n", ep->tx_len);
		return ERR_LEN;
	}

	if (retain->fragsize < MIN_MCTP_FRAG_SIZE) {
		retain->fragsize = MIN_MCTP_FRAG_SIZE;
	}

	hdr = (mctp_hdr_stct *)ep->tx_pkt_buf;
	buf = hdr->data;

	/* calculate the cunk size of this payload */
	len = ep->tx_len - ep->tx_cnt + MCTP_HDR_SIZE(ep);
	len = (len > retain->fragsize) ? retain->fragsize : len;
	ep->payload = len - MCTP_HDR_SIZE(ep);

	/* set mctp header */
	hdr->hdr_ver = 1;
	hdr->dst_eid = ep->src_eid;
	hdr->src_eid = retain->eid;
	hdr->som = (ep->flags & MCTP_COMPLETE) ? 1 : 0;
	hdr->eom = ((ep->tx_cnt + ep->payload) == ep->tx_len) ? 1 : 0;
	ep->txseq = (hdr->som & !(ep->flags & MCTP_SEQ_ROLL)) ? 0 : ((ep->txseq + 1) & 3);
	hdr->seq = ep->txseq;
	hdr->to = ep->to;
	hdr->tag = ep->tag;

	ep->flags &= ~MCTP_COMPLETE;

	/* per DSP0237 first message should carry msg_type & ic */
	if (hdr->som) {
		*buf++ = ep->msgtype | (ep->ic << 7);
	}

	/* copy payload bytes of data to active buffer */
	memcpy(buf, (void *)&ep->tx_ptr[ep->tx_cnt], ep->payload);

	/* send the data out */
	if (ep->flags & MCTP_IN_FLIGHT)
		return len;

	if (ep->ops->send) {
		return ep->ops->send(len);
	}

	return ERR_NO_TX_HANDLER;
}

int  mctp_init(void)
{
	memset((uint8_t *)&mctp_sts, 0, sizeof(mctp_stats_t));
	
	if (pldm_init())
		return -1;

	return 0;
}
