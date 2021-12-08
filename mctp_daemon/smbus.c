/*
 *      MCTP Daemon - FC mctp slave implementation
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
#include "smbus.h"

#define RX_FIFO         	"/tmp/mctp_smbus_rx"
#define TX_FIFO         	"/tmp/mctp_smbus_tx"
#define MAX_SMBUS_TX_PKT_SIZE	(MAX_MCTP_PKT_SIZE + sizeof(struct smbus_hdr_stc))

static uint8_t tx_buf[MCTP_MAX_MESSAGE_DATA];
static uint8_t rx_buf[MCTP_MAX_MESSAGE_DATA];
static uint8_t tx_pkt_buf[MAX_SMBUS_TX_PKT_SIZE];

static uint8_t src_addr;

static struct mctp_ep_retain_stc smbus_retain = {
	.eid = 1,
	.iid = 0,
	.fragsize = DEFAULT_MCTP_FRAGMENT_SIZE,
	.support = SUPPORT_MCTP_CNTROL_MSG | SUPPORT_PLDM_OVER_MCTP | SUPPORT_VDM_OVER_MCTP | SUPPORT_OEM_OVER_MCTP,
	.uuid = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
		 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f},
};

static mctp_endpoint_stct smbus_ep;
static int rx_fifo_fd, tx_fifo_fd;

static void reset_ep(void)
{
        vdm_ep.rx_cnt = vdm_ep.rx_len = 0;
        vdm_ep.tx_cnt = vdm_ep.tx_len = 0;

        vdm_ep.rxseq = vdm_ep.txseq = 0;

        smbus_ep.flags |= MCTP_COMPLETE;
        smbus_ep.flags &= ~MCTP_IN_FLIGHT;
}

static int __init(void)
{
	bzero((char *)&smbus_ep, sizeof(mctp_endpoint_stct));

        mkfifo(RX_FIFO, 0666);
        mkfifo(TX_FIFO, 0666);

	// full rx/tx payload buffer
	smbus_ep.rx_ptr = rx_buf;
	smbus_ep.tx_ptr = tx_buf;
	smbus_ep.tx_pkt_buf = (uint8_t *)&tx_pkt_buf[sizeof(struct smbus_hdr_stc)];

	// clear retain section (this should come from non-volatile memory
	smbus_ep.retain = &smbus_retain;
	smbus_ep.ops = &smbus_ops;

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
	smbus_ep.rx_cnt = len;
	smbus_ep.rx_pkt_buf = buf;

	hexdump(buf, len);

        if (mctp_recieve(&vdm_ep) < 0) {
                reset_ep();
                return -1;
        }
}

static void set_smbus_hdr(int *len)
{
	struct smbus_hdr_stc *hdr = (struct smbus_hdr_stc *)tx_pkt_buf;

	bzero((uint8_t *)hdr, sizeof(*hdr));

	hdr->dst_addr = src_addr;
	hdr->type = 0x0f;
	hdr->len = *len;
	hdr->rdwr = 1;
	hdr->src_addr = SMBUS_SLAVE_ADDR;

	len += sizeof(struct smbus_hdr_stc);
}

static int __send(int len)
{

	if (!len) {
		log_err("SMBUS: Error - payload length = 0\n");
		reset_ep();
		return -1;
	}

	smbus_ep.flags |= MCTP_IN_FLIGHT;
	smbus_ep.tx_cnt += smbus_ep.payload;

	set_smbus_hdr(&len);
#ifdef CONFIG_USE_SMBUS_INTERFACE
	write(tx_fifo_fd, tx_pkt_buf, len);
#else
	hexdump(tx_pkt_buf, len);
#endif


	while (smbus_ep.tx_cnt != smbus_ep.tx_len) {
		len = mctp_transmit(&smbus_ep);
		smbus_ep.tx_cnt += smbus_ep.payload;

		set_smbus_hdr(&len);
#ifdef CONFIG_USE_SMBUS_INTERFACE
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
struct mctp_ops_stc smbus_ops = {
        .init = &__init,
        .recv = &__receive,
        .send = &__send,
        .complete = NULL,
        .error = NULL,
	.exit = &__exit,
	.get_rx_fifo = &__get_rx_fifo,
};
