#include <stdio.h>
#include <strings.h>
#include <string.h>

#include "utils.h"
#include "ncsi.h"
#include "dell.h"

/* dell failed response */
void dell_failed_response(ncsi_resp_t *resp, uint16_t response, uint16_t reason)
{
	ncsi_dell_hdr_t *dell = (ncsi_dell_hdr_t *)resp->data;
	ncsi_dell_null_respn_t *rspn = (ncsi_dell_null_respn_t *)dell->data;

	resp->hdr.len += DELL_PAYLOAD_SIZE;
	resp->response = response;
	resp->reason = reason;
}

/* dell reboot required response */
void dell_reboot_required(ncsi_resp_t *resp, int len)
{
	ncsi_dell_hdr_t *dell = (ncsi_dell_hdr_t *)resp->data;
	ncsi_dell_null_respn_t *rspn = (ncsi_dell_null_respn_t *)dell->data;

	resp->hdr.len += DELL_PAYLOAD_SIZE;
	resp->response = NCSI_RESP_SUCCESS;
	resp->reason = DELL_RESP_RBT_RQRD;
}

/* dell panding response */
void dell_panding(ncsi_resp_t *resp, int len)
{
	ncsi_generic_response(resp, NCSI_RESP_SUCCESS, DELL_WRITE_PENDING, len);
}

/* dell panding response */
void dell_commit_required(ncsi_resp_t *resp, int len)
{
	ncsi_generic_response(resp, NCSI_RESP_SUCCESS, DELL_COMMIT_REQD, len);
}

/* dell Unknown */
void dell_cmd_unknown(uint32_t ch, void *vptr, ncsi_resp_t *resp)
{
	ncsi_dell_hdr_t *dell = (ncsi_dell_hdr_t *)resp->data;
	ncsi_dell_null_respn_t *rspn = (ncsi_dell_null_respn_t *)dell->data;

	//dell_err("Unsupported command %02x\n", dhdr->cmd);
	ncsi_unspprt_response(resp, DELL_PAYLOAD_SIZE);
}

/* map function to channel */
int valid_mapping(uint8_t ch, uint8_t fn)
{
	int i;

	i = (ncsi_state.max_ports - 1);
	return ((ch & i) == (fn & i)) ? 1 : 0;
}

/* set DELL header */
static void set_dell_hdr(ncsi_resp_t *resp, uint8_t cmd, uint8_t rev)
{
	ncsi_dell_hdr_t *dell = (ncsi_dell_hdr_t *)resp->data;
	dell->oem = DELL_IANA;
	dell->rev = rev;
	dell->cmd = cmd;
}

static oem_cmd_stc_t *get_dell_cmd(uint8_t cmd)
{
	return NULL;
}

/* NC-SI DELL OEM dispatcher */
static void dell_cmd_handler(void *hdlr, uint32_t interface, ncsi_hdr_t *ncsi, ncsi_resp_t *resp)
{
	ncsi_dell_hdr_t *dell = (ncsi_dell_hdr_t *)ncsi->data;
#ifdef CONFIG_DELL_CHECK_PID
	uint8_t pid = GET_PID(dell->data[0]);
#endif
	uint8_t cmd = dell->cmd;
	oem_cmd_stc_t *p = NULL;
        ncsi_oem_handler_t *oem = (ncsi_oem_handler_t *)hdlr;
	
	set_dell_hdr(resp, dell->cmd, dell->rev);
	oem->hit++;

	/* check version, currently supported versions are 1 & 2 */
	if (dell->rev != 2) {
		dell_err("version not supported %u\n", dell->rev);
		dell_failed_response(resp, NCSI_RESP_FAIL, DELL_UNSUPPORTED_PAYLOAD);
		return;
	}

	/* check the command is within the defined range */
	if INVALID_CMD(oem->max) {
		dell_err("command exceeds max commands (%x)\n", cmd);
		ncsi_incr_stats(NCSI_CMD_ERR | NCSI_RX);
		dell_failed_response(resp, NCSI_RESP_UNSUPPORT, NCSI_REASON_UNSUPPORT);
		return;
	}

	/* check if command supported */
	if ((p = get_dell_cmd(cmd)) == NULL) {
		dell_err("command %x not found\n", cmd);
		ncsi_incr_stats(NCSI_CMD_ERR | NCSI_RX);
		dell_failed_response(resp, NCSI_RESP_UNSUPPORT, NCSI_REASON_UNSUPPORT);
		return;
	}

	/* check if the request interface is allowed to run the command */
#ifdef CONFIG_DELL_CHECK_INTERFACE
	if (INVALID_INTRFC(p) || DISABLED_CMD(p)) {
		dell_err("interface not allowed\n");
		ncsi_incr_stats(NCSI_CMD_ERR | NCSI_RX);
		dell_failed_response(resp, NCSI_RESP_UNSUPPORT, NCSI_REASON_UNSUPPORT);
		return;
	}
#endif
	ncsi_incr_stats(NCSI_CMD_RECV | NCSI_RX);

#ifdef CONFIG_DELL_CHECK_PID
	/* check PID does not exceed max. pids */
	if INVALID_PID(p) {
		dell_err("func exceeds max. func (%u)\n", pid);
		dell_failed_response(resp, NCSI_RESP_FAIL, DELL_RESP_FUNC_NOT_ASSOC);
		return;
	}
#endif

#ifdef CONFIG_DELL_CHECK_INVALID_PARTITION
	/* check pid/chid for correct mapping */
	if INVALID_PART(p) {
		dell_err("func %u not associated with ch %u\n", pid, ncsi->chan);
		dell_failed_response(resp, NCSI_RESP_FAIL, DELL_RESP_FUNC_NOT_ASSOC);
		return;
	}
#endif
	/* everything looks kosher */
	p->func(ncsi->chan, dell, resp);
}

ncsi_oem_handler_t dell_oem = {
	.iana	= DELL_IANA,
	.flags	= IANA_ENB,
	.max 	= DELL_CMD_MAX,
	.hit	= 0,
	.init	= NULL,
	.hdlr	= &dell_cmd_handler,
};
