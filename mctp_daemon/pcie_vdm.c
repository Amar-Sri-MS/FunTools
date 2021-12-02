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

#include "utils.h"
#include "mctp.h"
#include "pcie_vdm.h"

#define RX_FIFO         	"/tmp/mctp_pcie_rx"
#define TX_FIFO         	"/tmp/mctp_pcie_tx"

#define MAX_PCIE_TX_PKT_SIZE	(MAX_MCTP_PKT_SIZE + sizeof(struct pcie_vdm_hdr_stc))

static uint8_t tx_buf[MCTP_MAX_MESSAGE_DATA];
static uint8_t rx_buf[MCTP_MAX_MESSAGE_DATA];
static uint8_t tx_pkt_buf[MAX_PCIE_TX_PKT_SIZE];
static mctp_endpoint_stct vdm_ep;
static int rx_fifo_fd, tx_fifo_fd;
static struct pcie_vdm_rec_data vdm_data;

static struct mctp_ep_retain_stc vdm_retain = {
	.eid = 1,
	.iid = 0,
	.fragsize = DEFAULT_MCTP_FRAGMENT_SIZE,
	.support = SUPPORT_MCTP_CNTROL_MSG | SUPPORT_PLDM_OVER_MCTP | SUPPORT_VDM_OVER_MCTP | SUPPORT_OEM_OVER_MCTP,
	.uuid = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
		 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f},
	.ep_priv_data = (void *)&vdm_data,
};

static void reset_ep(void)
{
        vdm_ep.rx_cnt = 0;
        vdm_ep.tx_cnt = 0;
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

	reset_ep();

        if ((tx_fifo_fd = open(TX_FIFO, O_RDWR | O_CREAT)) < 0) {
                log_err("cannot open %s for write\n", TX_FIFO);
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

	hdr_data->trgt_id = hdr->trgt_id;
	hdr_data->req_id = hdr->req_id;
	hdr_data->vendor_id = hdr->vendor_id;

	vdm_ep.rx_cnt = len - sizeof(struct pcie_vdm_hdr_stc);
	vdm_ep.rx_pkt_buf = hdr->data;

	hexdump(buf, len);

	return mctp_recieve(&vdm_ep);
}

static void set_pcie_vdm_hdr(int *len)
{
	struct pcie_vdm_hdr_stc *hdr = (struct pcie_vdm_hdr_stc *)tx_pkt_buf;
	struct pcie_vdm_rec_data *hdr_data = (struct pcie_vdm_rec_data *)vdm_ep.retain->ep_priv_data;
	int pad = (4 - (*len & 3)) & 3;

	bzero((uint8_t *)&vdm_ep.tx_pkt_buf[*len], pad);
	bzero((uint8_t *)hdr, sizeof(*hdr));
	*len += pad;

	hdr->fmt = 3;
	hdr->type = (2 << 3) | (PCIE_ROUTE_BY_ID << 0);

	hdr->len = DWORD(*len);
	hdr->msg_code = MCTP_MSG_CODE;
	hdr->vendor_id = MCTP_VENDOR_ID;

	// reply with the origin hdr data
	hdr->trgt_id = hdr_data->req_id;
	hdr->req_id = hdr_data->trgt_id;

	*len += sizeof(struct pcie_vdm_hdr_stc);
}

static int __send(int len)
{

	if (!len) {
		log_err("PCIE_VDM: Error - payload length = 0\n");
		reset_ep();
		return -1;
	}

	vdm_ep.flags |= MCTP_IN_FLIGHT;
	vdm_ep.tx_cnt += vdm_ep.payload;

	set_pcie_vdm_hdr(&len);
#ifdef CONFIG_USE_PCIE_VDM_INERFACE
	write(tx_fifo_fd, tx_pkt_buf, len);
#else
	hexdump(tx_pkt_buf, len);
#endif

	while (vdm_ep.tx_cnt != vdm_ep.tx_len) {
		len = mctp_transmit(&vdm_ep);
		vdm_ep.tx_cnt += vdm_ep.payload;
		
		set_pcie_vdm_hdr(&len);
#ifdef CONFIG_USE_PCIE_VDM_INERFACE
		write(tx_fifo_fd, tx_pkt_buf, len);
#else
		hexdump(tx_pkt_buf, len);
#endif
	}

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

/* PCIE interface handlers*/
struct mctp_ops_stc pcie_vdm_ops = {
        .init = &__init,
        .recv = &__receive,
        .send = &__send,
        .complete = NULL,
        .error = NULL,
	.exit = &__exit,
	.get_rx_fifo = &__get_rx_fifo,
};
