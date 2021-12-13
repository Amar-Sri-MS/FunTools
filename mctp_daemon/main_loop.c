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
#include <signal.h>

#include "utils.h"
#include "mctp.h"
#include "pcie_vdm.h"
#include "smbus.h"

#define PCIE_EP_ID	0
#define SMBUS_EP_ID	1
#define NUMBER_OF_EPS	2

static int terminate = 0;
static struct mctp_ops_stc *mctp_ops[NUMBER_OF_EPS] = {
	&pcie_vdm_ops,
	&smbus_ops,
};

void sig_handler(int signo)
{
	if (signo == SIGTERM || signo == SIGINT)
		terminate = 1;
}

static int init_ep()
{
	for(int i = 0; i < NUMBER_OF_EPS; i++) {
		if (mctp_ops[i]->init)
			if (mctp_ops[i]->init())
				return -1;
	}

	return 0;
}

static int init(void)
{

	if (init_ep()) {
		log_err("ep init failed\n");
		return -1;
	}

	if (mctp_init()) {
		log_err("mctp init failed\n");
		return -1;
	}

	return 0;
}

int main_loop()
{
        int len = 0, rc = -1, rd_len;
        struct timeval timeout;
        fd_set read_fds;
	int rx_fifo_fd;
	uint8_t buf[128];

	umask(0);

	if (init()) {
		return -1;
	}

        if (signal(SIGTERM , sig_handler) == SIG_ERR) {
                log_err("can't catch SIGTERM\n");
                goto exit;
        }

	if (signal(SIGINT , sig_handler) == SIG_ERR) {
		log_err("can't catch SIGINT\n");
		return -1;
	}

	rx_fifo_fd = mctp_ops[PCIE_EP_ID]->get_rx_fifo();

	// for now, assume only one ep (pcie-vdm)
	while (1) {
		FD_ZERO(&read_fds);
		FD_SET(rx_fifo_fd, &read_fds);
		timeout.tv_sec = cfg.sleep;
		timeout.tv_usec = 0;

		if (terminate) {
			log("Terminated ...\n");
			goto exit;
		}

                if ((select(rx_fifo_fd + 1, &read_fds, NULL, NULL, &timeout)) != 1) 
                        continue;

		rd_len = read(rx_fifo_fd, buf, sizeof(buf));

		if (rd_len <= 0)
			continue;

		len += rd_len;
		if (len >= mctp_ops[PCIE_EP_ID]->get_min_payload()) {
			mctp_ops[PCIE_EP_ID]->recv(buf, len);
			len = 0;
		}
        }

exit:

	for(int i = 0; i < NUMBER_OF_EPS; i++)
		if (mctp_ops[i]->exit)
			mctp_ops[i]->exit();
	return rc;
}
