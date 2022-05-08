#include <stdio.h>
#include <strings.h>
#include <string.h>

#include "utils.h"
#include "ncsi.h"

// global vars
ncsi_state_t  ncsi_state;
ncsi_statistics_t ncsi_stats;

/* checksum calculator */
uint32_t checksum(uint8_t *buf, int start, int len)
{
	uint32_t cs = 0;
	int i;

	for (i = start; i < (start + len); i += 2) {
		cs += *(uint16_t *)&buf[i];
	}

	return ((~cs) + 1);
}

/* align length to 32bit */
static uint32_t align_to_dw(uint32_t len)
{
	len += (len & 0x3) ? (4 - (len & 0x3)) : 0;
	return len;
}

/* search for standard ncsi command handler */
static ncsi_cmd_handler_t *find_ncsi_cmd(uint8_t cmd)
{
	ncsi_cmd_handler_t *ptr = ncsi_cmds;

	while (ptr->func != NULL) {
		if (ptr->cmd == cmd)
			return ptr;

		ptr++;
	}

	return NULL;
}

/* zero out all ncsi stats */
void ncsi_clear_stats(void)
{
	bzero((uint8_t *)&ncsi_state.stats, sizeof(ncsi_statistics_t));
}

/* ncsi state machine */
void ncsi_change_state(uint8_t ch, uint8_t cmd)
{
	ncsi_chan_state_t *chan = (ncsi_chan_state_t *)&ncsi_state.channel[ch];

	switch (chan->state) {
	case NCSI_PKG_DESEL:
		chan->state = (cmd == NCSI_CMD_CLEAR_INIT) ? NCSI_CHN_RDY : (cmd == NCSI_CMD_PKG_DESELECT) ? NCSI_PKG_DESEL : NCSI_PKG_SEL;
		break;

	case NCSI_PKG_SEL:
		chan->state = (cmd == NCSI_CMD_PKG_DESELECT) ? NCSI_PKG_DESEL : (cmd == NCSI_CMD_CLEAR_INIT) ? NCSI_CHN_RDY : NCSI_PKG_SEL;
		break;

	case NCSI_CHN_RDY:
		chan->state = (cmd == NCSI_CMD_CHAN_RESET) ? NCSI_PKG_SEL : (cmd == NCSI_CMD_PKG_DESELECT) ? NCSI_PKG_DESEL_RDY : NCSI_CHN_RDY;
		break;

	case NCSI_PKG_DESEL_RDY:
		chan->state = (cmd == NCSI_CMD_CHAN_RESET) ? NCSI_PKG_SEL : NCSI_CHN_RDY;
		break;
	}
}

/* ncsi Statistics counters */
void ncsi_incr_stats(uint32_t n)
{
	ncsi_state.stats.recv += (n & NCSI_CMD_RECV) ? 1 : 0;
	ncsi_state.stats.drop += (n & NCSI_CMD_DROP) ? 1 : 0;
	ncsi_state.stats.err  += (n & NCSI_CMD_ERR) ? 1 : 0;
	ncsi_state.stats.chksm += (n & NCSI_CMD_CHKSM) ? 1 : 0;
	ncsi_state.stats.aen += (n & NCSI_AEN_CNT) ? 1 : 0;
	ncsi_state.stats.tx  += (n & NCSI_TX) ? 1 : 0;
}

/* ncsi generic response */
void ncsi_generic_response(ncsi_resp_t *resp, uint16_t response, uint16_t reason, int len)
{
	resp->hdr.len += len;
	resp->response = response;
	resp->reason = reason;
}

/* succesful ncsi response */
void ncsi_success_response(ncsi_resp_t *resp, int len)
{
	ncsi_generic_response(resp, NCSI_RESP_SUCCESS, NCSI_REASON_NONE, len);
}

/* command specific failed reasponse */
void ncsi_failed_cmd_specific(ncsi_resp_t *resp, uint8_t cmd, uint16_t reason)
{
	ncsi_generic_response(resp, NCSI_RESP_FAIL, ((uint16_t)cmd << 8) | reason, 0);
}

/* unsupport ncsi response */
void ncsi_unspprt_response(ncsi_resp_t *resp, int len)
{
	ncsi_generic_response(resp, NCSI_RESP_UNSUPPORT, NCSI_REASON_UNSUPPORT, len);
}

/* failed ncsi response with reason code */
void ncsi_failed_response(ncsi_resp_t *resp, uint16_t reason)
{
	ncsi_generic_response(resp, NCSI_RESP_FAIL, reason, 0);
}

/* invalid ncsi response */
void ncsi_invalid_response(ncsi_resp_t *resp)
{
	ncsi_generic_response(resp, NCSI_RESP_FAIL, NCSI_REASON_INVAL, 0);
}

/* init required ncsi response */
void ncsi_init_required_response(ncsi_resp_t *resp)
{
	ncsi_generic_response(resp, NCSI_RESP_FAIL, NCSI_REASON_INIT, 0);
}

/* ncsi unsupported command response */
void ncsi_cmd_unsupported(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_err("Unsupported cmd 0x%02x\n", ncsi->cmd);

	if (ncsi->chan < ncsi_state.max_ports)
		ncsi_incr_stats(NCSI_CMD_ERR | NCSI_CMD_RECV);

	ncsi_unspprt_response(resp, 0);
}

/* ncsi commands dispatcher */
int ncsi_handler(uint8_t *buf, int len, uint8_t *pbuf)
{
	ncsi_hdr_t *ncsi = (ncsi_hdr_t *)buf;
	ncsi_resp_t *resp = (ncsi_resp_t *)pbuf;
	ncsi_cmd_handler_t *p = NULL;
	uint32_t chksum = 0;
	uint32_t rx_len = 0;
	uint8_t cmd = ncsi->cmd;
	uint32_t pad = 0;
	uint32_t tx_len = 0;

	rx_len = (((*(uint8_t *)&ncsi->len) & 0xf) << 8) + *((uint8_t *)&ncsi->len + 1);
	pad = (rx_len & 0x3) ? (4 - (rx_len & 0x3)) : 0;
	memcpy((uint8_t *)&chksum, (uint8_t *)&buf[sizeof(ncsi_hdr_t) + rx_len + pad], 4);

	memcpy(resp, ncsi, sizeof(ncsi_hdr_t));
	resp->hdr.cmd  = (ncsi->cmd | 0x80);
	resp->hdr.len = 4;

#ifdef CONFIG_NCSI_VALIDATE_CHECKSUM
	/* check checksum */
	if (chksum) {
		if (chksum != checksum(buf, 0, (sizeof(ncsi_hdr_t) + rx_len + pad))) {
			ncsi_incr_stats(NCSI_CMD_CHKSM);
			ncsi_err("Bad checksum [%08x]\n", chksum);
			return -1;
		}
	}
#endif

	/* check package id */
	if (ncsi->pkgid != ncsi_state.pkgid) {
		ncsi_incr_stats(NCSI_CMD_DROP);
		ncsi_err("bad package ID (pkgid = %u)\n", ncsi->pkgid);
		return -1;
	}

	/* check channel */
	if ((ncsi->chan >= ncsi_state.max_ports) && (ncsi->chan != 0x1F)) {
		ncsi_incr_stats(NCSI_CMD_DROP);
		ncsi_err("Unsupported channel %d (cmd = %02x)\n", ncsi->chan, cmd);
#ifdef CONFIG_SEND_INVALID_RESPONSE
		ncsi_invalid_response(resp);
		goto exit;
#else /* timeout */
		return -1;
#endif
	}

	/* check hdr version */
	if (ncsi->rev != 0x01) {
		ncsi_incr_stats(NCSI_CMD_DROP);
		ncsi_err("Unsupported header version %u (cmd = %02x)\n", ncsi->rev, cmd);
		return -1;
	}

	/* When using NC-SI interface, enable TX (not applicable to FC cards) */

	switch (cmd) {
#ifdef CONFIG_ENABLE_NCSI_OEM_CMD
	case NCSI_CMD_OEM:
		ncsi_cmd_oem(ncsi, resp);
		break;
#endif
	default:
		if (INVALID_CMD(NCSI_MAX_CMD)) {
			ncsi_cmd_unsupported(ncsi, resp);
			break;
		}

		/* search the command, null return == not supported */
		if ((p = find_ncsi_cmd(cmd)) == NULL) {
			ncsi_cmd_unsupported(ncsi, resp);
			break;
		}

		/* check if command is enabled */
		if DISABLED_CMD(p) {
			ncsi_cmd_unsupported(ncsi, resp);
			break;
		}

		/* check if chan == 0x1f for specific ncsi commands */
		if INVALID_1F(p) {
			ncsi_incr_stats(NCSI_CMD_DROP);
			return -1;
		}

		/* check if init is required */
		if CHAN_ISNT_1F {
		if INIT_REQUIRED(p)
			{
				ncsi_incr_stats(NCSI_CMD_RECV);
				ncsi_init_required_response(resp);
				break;
			}
		}

		/* everything looks kosher */
		ncsi_state.pkg_sel = (!ncsi_state.pkg_sel) ? 1 : 0;
		ncsi_incr_stats(NCSI_CMD_RECV | NCSI_RX);
		p->func(ncsi, resp);
		break;
	}

#ifdef CONFIG_SEND_INVALID_RESPONSE
exit:
#endif
	/* should we send a response? */
	if (!resp->hdr.len) {
		return -1;
	}

	pad = align_to_dw(resp->hdr.len) - resp->hdr.len;

	/* align payload to dw */
	if (ncsi_state.align_len)
		resp->hdr.len = align_to_dw(resp->hdr.len);

	tx_len = sizeof(ncsi_hdr_t) + align_to_dw(resp->hdr.len);

	/* add padding if required */
	if (pad)
		memset(&pbuf[tx_len - pad], 0, pad);

	resp->hdr.len = resp->hdr.len & 0xfff;
	chksum = (ncsi_state.chksum_en) ? checksum(pbuf, 0, tx_len) : 0;
	memcpy(&pbuf[tx_len], &chksum, sizeof(chksum));
	tx_len += sizeof(chksum);
	ncsi_incr_stats(NCSI_TX);

	return tx_len;
}

/* ncsi init */
void ncsi_init(void)
{
	ncsi_state.pkgid = DEFAULT_PACKAGE_ID;
	ncsi_state.signature = NCSI_STATE_SIGNATURE;

#ifdef CONFIG_ENABLE_NCSI_OEM_CMD
	oem_init();
#endif

	ncsi_dbg("NCSI init done, nofp = %u, pkgid = %u\n", ncsi_state.max_ports, ncsi_state.pkgid);
}
