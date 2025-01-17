/*
 *      MCTP Daemon - FC PCIE VDM implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/select.h>
#include <unistd.h>
#include <stdlib.h>

#include "utils.h"
#include "mctp.h"
#include "pcie_vdm.h"
#include "pldm_pmc.h"
#include <errno.h> 

#define RX_FIFO         	"/tmp/mctp_pcie_rx"
#define TX_FIFO         	"/tmp/mctp_pcie_tx"

#define MAX_PCIE_TX_PKT_SIZE	(MAX_MCTP_PKT_SIZE + sizeof(struct pcie_vdm_hdr_stc))

#define SYNC_PCIE_RW_FIFO_FILE "/tmp/.platform/sync_rw_pcie_fifo"

extern uint8_t eid;

static uint8_t tx_buf[MCTP_MAX_MESSAGE_DATA];
static uint8_t rx_buf[MCTP_MAX_MESSAGE_DATA];
static uint8_t tx_pkt_buf[MAX_PCIE_TX_PKT_SIZE];
static mctp_endpoint_stct vdm_ep;
static int rx_fifo_fd, tx_fifo_fd;

static struct pcie_vdm_rec_data vdm_data = {
	.vendor_id = 0,
	.trgt_id = 0,
	.cookie = 0,
	.bus_owner_id = 0,
};

static struct mctp_ep_retain_stc vdm_retain = {
	.eid = 0,
	.iid = 0,
	.fragsize = DEFAULT_MCTP_FRAGMENT_SIZE,
	.support = SUPPORT_MCTP_CNTROL_MSG | SUPPORT_PLDM_OVER_MCTP | SUPPORT_VDM_OVER_MCTP | SUPPORT_OEM_OVER_MCTP | SUPPORT_ASYNC_EVENTS,
	.ep_priv_data = (void *)&vdm_data,
};

static void reset_ep(void)
{
        vdm_ep.rx_cnt = vdm_ep.rx_len = 0;
        vdm_ep.tx_cnt = vdm_ep.tx_len = 0;

	vdm_ep.rxseq = vdm_ep.txseq = 0;

        vdm_ep.flags |= MCTP_COMPLETE;
        vdm_ep.flags &= ~MCTP_IN_FLIGHT;
}

static int __init(void)
{
	bzero((char *)&vdm_ep, sizeof(mctp_endpoint_stct));

        mkfifo(RX_FIFO, 0666);
        mkfifo(TX_FIFO, 0666);

	// full rx/tx payload buffer
	vdm_ep.rx_ptr = rx_buf;
	vdm_ep.tx_ptr = tx_buf;
	vdm_ep.tx_pkt_buf = (uint8_t *)&tx_pkt_buf[sizeof(struct pcie_vdm_hdr_stc)];

	// clear retain section (this should come from non-volatile memory
	vdm_ep.retain = &vdm_retain;
	vdm_ep.ops = &pcie_vdm_ops;

	if (eid)
		vdm_retain.eid = eid;

	reset_ep();

        if ((tx_fifo_fd = open(TX_FIFO, O_RDWR | O_NONBLOCK | O_CREAT)) < 0) {
                log_err("cannot open %s for write, errno: %d\n", TX_FIFO, errno);
                return -1;
        }

        if ((rx_fifo_fd = open(RX_FIFO, O_RDWR | O_NONBLOCK | O_CREAT)) < 0) {
                log_err("cannot open %s for read\n", RX_FIFO);
                return -1;
        }

	return 0;
}

static int __receive(uint8_t *buf, int len)
{
	struct pcie_vdm_hdr_stc *hdr = (struct pcie_vdm_hdr_stc *)buf;
	struct pcie_vdm_rec_data *hdr_data = (struct pcie_vdm_rec_data *)vdm_ep.retain->ep_priv_data;

	hdr_data->cookie = ntoh32(hdr->cookie);
	hdr_data->trgt_id = ntoh16(hdr->req_id);
	hdr_data->vendor_id = ntoh16(hdr->vendor_id);

	vdm_ep.rx_cnt = len - sizeof(struct pcie_vdm_hdr_stc) - (hdr->tag >> 4);
	vdm_ep.rx_pkt_buf = hdr->data;

	if (cfg.debug & EP_DEBUG) 
		hexdump(buf, len);

        if (mctp_recieve(&vdm_ep) < 0) {
                reset_ep();
                return -1;
	}

	return 0;
}

static void set_pcie_vdm_hdr(int *len)
{
	struct pcie_vdm_hdr_stc *hdr = (struct pcie_vdm_hdr_stc *)tx_pkt_buf;
	struct pcie_vdm_rec_data *hdr_data = (struct pcie_vdm_rec_data *)vdm_ep.retain->ep_priv_data;
	int pad = (4 - (*len & 3)) & 3;


	bzero((uint8_t *)&vdm_ep.tx_pkt_buf[*len], pad);
	bzero((uint8_t *)hdr, sizeof(*hdr));
	*len += pad;

	hdr->cookie = hton32(hdr_data->cookie);

	hdr->fmt = 3;
	hdr->type = (2 << 3);
	hdr->type |= (vdm_retain.eid) ? PCIE_ROUTE_BY_ID :  PCIE_ROUTE_TO_RC;

	// count mctp header as pcie_vdm hdr
	hdr->len = hton16((DWORD(*len) - 1));

	hdr->req_id = (cfg.pcie_req_id) ? hton16(cfg.pcie_req_id) : hton16(FUNGIBLE_PCIE_BUS_ID(hdr_data->cookie)  << 8);
	hdr->tag = (pad << 4);
	hdr->msg_code = MCTP_MSG_CODE;
	hdr->vendor_id = hton16(MCTP_VENDOR_ID);

	// reply with the origin hdr data
	hdr->trgt_id = hton16(hdr_data->trgt_id);

	*len += sizeof(struct pcie_vdm_hdr_stc);
}

static int __async(uint8_t *buf)
{
	struct pcie_vdm_rec_data *hdr_data = (struct pcie_vdm_rec_data *)vdm_ep.retain->ep_priv_data;
	uint32_t id;
	int len = 0;
	float temp;

	if (!(vdm_retain.support & SUPPORT_ASYNC_EVENTS)) {
		log_err("%s: async is not supported\n", __func__);
		return -1;
	}

	if (hdr_data == NULL) {
		log_err("%s: no priv data\n", __func__);
		return -1;
	}

	sscanf((const char *)buf, "%u %f", &id, &temp);

	len = pldm_async_event(vdm_ep.tx_ptr, (uint8_t)id, temp);
	if (len < 0) {
		log_err("pldm_async_event with %d\n", len);
		return -1;
	}

	vdm_ep.tx_len = len;
	vdm_ep.tx_cnt = 0;

	if (cfg.debug & EP_DEBUG)
		hexdump(vdm_ep.tx_ptr, vdm_ep.tx_len);

	return mctp_transmit(&vdm_ep);
}


static int __send(int len)
{
	if (!len) {
		log_err("PCIE_VDM: Error - payload length = 0\n");
		reset_ep();
		return -1;
	}
	char syscom[128];
	vdm_ep.flags |= MCTP_IN_FLIGHT;
	vdm_ep.tx_cnt += vdm_ep.payload;

	set_pcie_vdm_hdr(&len);

	if (cfg.debug & EP_DEBUG)
		hexdump(tx_pkt_buf, len);

#ifdef CONFIG_USE_PCIE_VDM_INTERFACE
	write(tx_fifo_fd, tx_pkt_buf, len);
#endif
	// Producer is faster then consumer so creating a bit of Pause
	// till consumer consumes
	snprintf(syscom, sizeof(syscom), "/bin/touch %s", SYNC_PCIE_RW_FIFO_FILE);
	system(syscom);

	while (vdm_ep.tx_cnt != vdm_ep.tx_len) {
		uint32_t counter = 0;
		//Give some time to FIFO reader (CCLinux Glue-layer)
		//as its slower then FIFO writer (mctp_daemon) in
		//extended Packet case alone
		while ((access(SYNC_PCIE_RW_FIFO_FILE, F_OK) == 0) && counter < 10) {
			counter++;
		}

		len = mctp_transmit(&vdm_ep);
		vdm_ep.tx_cnt += vdm_ep.payload;
		
		set_pcie_vdm_hdr(&len);
		if (cfg.debug & EP_DEBUG)
			hexdump(tx_pkt_buf, len);

#ifdef CONFIG_USE_PCIE_VDM_INTERFACE
		write(tx_fifo_fd, tx_pkt_buf, len);
#endif
	}

	//clean-up
	snprintf(syscom, sizeof(syscom), "/bin/rm -f %s", SYNC_PCIE_RW_FIFO_FILE);
	system(syscom);
	reset_ep();
	return 0;
}

static int __exit(void)
{

        close(rx_fifo_fd);
        close(tx_fifo_fd);

        remove(RX_FIFO);
        remove(TX_FIFO);

	return 0;
}

static int __get_rx_fifo(void)
{
	return rx_fifo_fd;
}

static int __get_min_payload(void)
{
	return sizeof(struct pcie_vdm_hdr_stc) + sizeof(mctp_hdr_stct);
}

/* PCIE interface handlers*/
struct mctp_ops_stc pcie_vdm_ops = {
        .init = &__init,
        .recv = &__receive,
	.async = &__async,
        .send = &__send,
        .complete = NULL,
        .error = NULL,
	.exit = &__exit,
	.get_rx_fifo = &__get_rx_fifo,
	.get_min_payload = &__get_min_payload,
};
