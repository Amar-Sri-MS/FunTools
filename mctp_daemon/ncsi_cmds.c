#include <string.h>

#include "utils.h"
#include "ncsi.h"

static char fw_name[] = "Fungible FC50";

/* clear/init */
static void ncsi_clear_init(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_change_state(ncsi->chan, ncsi->cmd);

	ncsi_clear_stats();

	ncsi_success_response(resp, 0);
	ncsi_dbg("ncsi_clear_init on ch %d \n", ncsi->chan);
}

/* package select */
static void ncsi_pkg_select(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	int i;

	ncsi_state.pkg_sel = 1;

	for (i = 0; i < ncsi_state.max_ports; i++)
		ncsi_change_state(i, NCSI_CMD_PKG_SELECT);

	ncsi_success_response(resp, 0);
}

/* package deselect command handler */
static void ncsi_pkg_deselect(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	int i;

	ncsi_state.pkg_sel = 0;

	for (i = 0; i < ncsi_state.max_ports; i++)
		ncsi_change_state(i, NCSI_CMD_PKG_DESELECT);

	ncsi_success_response(resp, 0);
}

/* chan enable command handler */
static void ncsi_chan_enable(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	uint8_t ch = (uint8_t)ncsi->chan;
	ncsi_chan_state_t *chan = (ncsi_chan_state_t *)&ncsi_state.channel[ch];

	chan->config |= CHANNEL_ENABLED;
	ncsi_success_response(resp, 0);
}

/* disable channel command handler */
static void ncsi_chan_disable(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	uint8_t ch = (uint8_t)ncsi->chan;
	ncsi_chan_state_t *chan = (ncsi_chan_state_t *)&ncsi_state.channel[ch];
	uint8_t ald = ncsi->data[0] & 1;

	chan->config &= ~CHANNEL_ENABLED;

	if (ald) {
		/* TODO: Disable link */
	}

	ncsi_success_response(resp, 0);
}

/* reset channel command handler */
static void ncsi_reset_chan(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	uint8_t ch = (uint8_t)ncsi->chan;

	ncsi_change_state(ch, ncsi->cmd);
	ncsi_success_response(resp, 0);
}

/* get link command handler */
static void ncsi_get_link(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_get_link_resp_hdr_t *rspn = (ncsi_get_link_resp_hdr_t *)resp->data;
#ifdef CONFIG_NCSI_GET_LINK_STATUS_SUPPORT
	uint8_t ch = (uint8_t)ncsi->chan;
	uint32_t status = get_link_status(ch);
#else
	uint32_t status = 0;
#endif

	rspn->status = status;
	rspn->other = 0;
	rspn->oem = 0;

	ncsi_success_response(resp, sizeof(*rspn));
}

#define DEVICE_ID		0x1bab
#define SUB_DEVICE_ID		0x0000
#define VENDOR_ID		0x1bab
#define SUB_VENDOR_ID		0x0000
/* get version command handler */
static void ncsi_get_ver(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_ver_resp_t *rspn = (ncsi_ver_resp_t *)resp->data;

	memset((uint8_t *)rspn, 0, sizeof(ncsi_ver_resp_t));

	rspn->maj = NCSI_VER_NUM_MAJOR;
	rspn->min = NCSI_VER_NUM_MINOR;
	rspn->upd = NCSI_VER_NUM_UPDATE;

	memcpy(rspn->fw_name, fw_name, (strlen(fw_name) > 12) ? 12 : strlen(fw_name));

	// TODO: Add real fw version and iana
	rspn->fw_ver = -1;
	rspn->iana = -1;

        rspn->did = DEVICE_ID;
        rspn->ssid = SUB_DEVICE_ID;

        rspn->vid = VENDOR_ID;
        rspn->svid = SUB_VENDOR_ID;

	ncsi_success_response(resp, sizeof(*rspn));
}

/* get capabilities command handler */
static void ncsi_get_cap(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_cap_resp_t *rspn = (ncsi_cap_resp_t *)resp->data;

	memset((uint8_t *)rspn, 0, sizeof(ncsi_cap_resp_t));
	rspn->buff = 128;
	rspn->flags = NCSI_CAP_OS;
	rspn->chan_cnt = ncsi_state.max_ports;

	ncsi_success_response(resp, sizeof(*rspn));
}

/* get parameter command handler */
static void ncsi_get_param(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	uint8_t ch = (uint8_t)ncsi->chan;
	ncsi_chan_state_t *chan = (ncsi_chan_state_t *)&ncsi_state.channel[ch];
	ncsi_get_parm_resp_t *rspn = (ncsi_get_parm_resp_t *)resp->data;
	uint8_t *ptr = rspn->data;

	memset((uint8_t *)rspn, 0, sizeof(ncsi_get_parm_resp_t));
	rspn->vlan_mode = chan->vlan_mode;

	rspn->lnk_set = chan->link;
	rspn->bcst_set = chan->bc_filters;
	rspn->cfg_flags = chan->config;

	/* fc isn't supported */
	rspn->flow_ctl = ncsi_state.fc_ena;

/* Only if we have pass-through (RMII or SGMII), isn't valid for FC cards */
#ifdef CONFIG_NCSI_ENABLED_SIDEBAND
	if (!SIDEBAND_DISABLED) {
		int i;

		rspn->aen_ctrl = NCSI_AEN_LINK;
		rspn->mac_cnt = MAX_NCSI_UNICAST;
		rspn->mac_flags = chan->ucast_ena;

		rspn->vlan_cnt = MAX_NCSI_VLAN;
		rspn->vlan_flags[1] = chan->vlan_ena;

		for (i = 0; i < MAX_NCSI_UNICAST; i++) {
			memcpy(ptr, chan->ucast[i].addr, 6);
			ptr += 6;
		}

		for (i = 0; i < MAX_NCSI_VLAN; i++) {
			*ptr++ = (chan->vlan_tag[i] >> 8) & 0xff;
			*ptr++ = chan->vlan_tag[i] & 0xff;
		}
	}
#endif

	ncsi_success_response(resp, sizeof(*rspn) + (ptr - rspn->data));
}

/* Get ncsi statistics */
static void ncsi_get_stats(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_stats_ncsi_resp_t *rspn = (ncsi_stats_ncsi_resp_t *)resp->data;

	memset((uint8_t *)rspn, 0xff, sizeof(ncsi_stats_ncsi_resp_t));

	rspn->rx_pkt = ncsi_state.stats.recv +  ncsi_state.stats.drop + ncsi_state.stats.chksm;
	rspn->tx_pkt = ncsi_state.stats.tx;
	rspn->cmd_cnt = ncsi_state.stats.recv;
	rspn->cmd_drop = ncsi_state.stats.drop;
	rspn->cmd_err = ncsi_state.stats.err;
	rspn->cmd_cksum = ncsi_state.stats.chksm;
	rspn->aen_cnt = ncsi_state.stats.aen;

	ncsi_clear_stats();
	ncsi_success_response(resp, sizeof(*rspn));
}

/* aen enable command handler */
static void ncsi_aen_enable(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_aen_enable_t *aen = (ncsi_aen_enable_t *)ncsi->data;
	uint8_t chan = (uint8_t)ncsi->chan;

	ncsi_state.channel[chan].aen_mcid = aen->mcid;
	ncsi_state.channel[chan].aen_events = aen->ctrl;

	ncsi_success_response(resp, 0);
}

#ifdef CONFIG_PLDM_OVER_NCSI_SUPPORT
static void ncsi_pldm(ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
        int rc = 0;

        rc = pldm_handler(ncsi->data, ncsi->len, resp->data);
        if (rc < 0) {
                ncsi_failed_response(resp, 0);
                return;
        }

        ncsi_success_response(resp, rc);
}
#endif

#define REGISTER_NCSI_CMD(_cmd, _handler, _ifs, _checks)	{.cmd = _cmd, .chk_flag = _checks, .func = &_handler}
ncsi_cmd_handler_t ncsi_cmds[] = {
	/* register mandatory standard ncsi cmds */
	REGISTER_NCSI_CMD(NCSI_CMD_CHAN_RESET, ncsi_reset_chan, ALL_IFS, NO_CHECK),
	REGISTER_NCSI_CMD(NCSI_CMD_CHAN_DISABLE, ncsi_chan_disable, ALL_IFS, CHECK_INIT),
	REGISTER_NCSI_CMD(NCSI_CMD_CHAN_ENABLE, ncsi_chan_enable, ALL_IFS, CHECK_INIT),
	REGISTER_NCSI_CMD(NCSI_CMD_PKG_DESELECT, ncsi_pkg_deselect, ALL_IFS, CHECK_CHAN_1F),
	REGISTER_NCSI_CMD(NCSI_CMD_PKG_SELECT, ncsi_pkg_select, ALL_IFS, CHECK_CHAN_1F),
	REGISTER_NCSI_CMD(NCSI_CMD_CLEAR_INIT, ncsi_clear_init, ALL_IFS, NO_CHECK),
	REGISTER_NCSI_CMD(NCSI_CMD_STATS_NCSI, ncsi_get_stats, ALL_IFS, CHECK_INIT),
	REGISTER_NCSI_CMD(NCSI_CMD_GET_PARAM, ncsi_get_param, ALL_IFS, CHECK_INIT),
	REGISTER_NCSI_CMD(NCSI_CMD_GET_CAP, ncsi_get_cap, ALL_IFS, CHECK_INIT),
	REGISTER_NCSI_CMD(NCSI_CMD_GET_VER, ncsi_get_ver, ALL_IFS, CHECK_INIT),
	REGISTER_NCSI_CMD(NCSI_CMD_LINK_GET, ncsi_get_link, ALL_IFS, CHECK_INIT),

	/* register ncsi aen handler */
	REGISTER_NCSI_CMD(NCSI_CMD_AEN_ENABLE, ncsi_aen_enable, RMII_IF, CHECK_INIT),
};
