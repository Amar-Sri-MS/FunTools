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
#include <stdlib.h>

#include "utils.h"
#include "mctp.h"
#include "pldm_pmc.h"
#include "pcie_vdm.h"
#include "smbus.h"

#define PCIE_EP_ID	0
#define SMBUS_EP_ID	1
#define NUMBER_OF_EPS	2

#define DEFAULT_VMD_INTERFACE	PCIE_EP_ID

#define SENSOR_FIFO		"/tmp/mctp_sensors"

static int terminate = 0;

struct mctp_ops_stc *mctp_ops[NUMBER_OF_EPS] = {
	&pcie_vdm_ops,
	&smbus_ops,
};

void sig_handler(int signo)
{
	if (signo == SIGTERM || signo == SIGINT) {
		terminate = 1;
	}
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

static void find_max_fd(int *maxfd)
{
	for(int i = 0; i < NUMBER_OF_EPS; i++)
		if (mctp_ops[i]->get_rx_fifo() > *maxfd)
			*maxfd = mctp_ops[i]->get_rx_fifo();
}	

void temp_event_handler(uint8_t *buf, int len)
{
	if (mctp_ops[DEFAULT_VMD_INTERFACE]->async == NULL)
		return;

	mctp_ops[DEFAULT_VMD_INTERFACE]->async(buf);
}

int main_loop()
{
        int len = 0, rc = -1, rd_len;
        struct timeval timeout;
	int sensor_fifo_fd;
	uint8_t buf[128];

	umask(0);

	// open sensor name fifo
	mkfifo(SENSOR_FIFO, 0666);
	if ((sensor_fifo_fd = open(SENSOR_FIFO, O_RDWR | O_CREAT)) < 0) {
                log_err("cannot open %s\n", SENSOR_FIFO);
                remove(SENSOR_FIFO);
		return -1;
        }

	if (init()) 
		goto exit;
	
        if (signal(SIGTERM , sig_handler) == SIG_ERR) {
                log_err("can't catch SIGTERM\n");
                goto exit;
        }

	if (signal(SIGINT , sig_handler) == SIG_ERR) {
		log_err("can't catch SIGINT\n");
		goto exit;
	}

	// for now, assume only one ep (pcie-vdm)
	while (1) {
		fd_set fds;
		int maxfd = sensor_fifo_fd;

		FD_ZERO(&fds);
		FD_SET(sensor_fifo_fd, &fds);

		for(int i = 0; i < NUMBER_OF_EPS; i++)
			FD_SET(mctp_ops[i]->get_rx_fifo(), &fds);

		timeout.tv_sec = cfg.polling / 1000;
                timeout.tv_usec = cfg.polling % 1000; 

		find_max_fd(&maxfd);
		select(maxfd + 1, &fds, NULL, NULL, &timeout);

		if (terminate) {
			log("Terminated ...\n");
			goto exit;
		}

		if (FD_ISSET(sensor_fifo_fd, &fds)) {
			rd_len = read(sensor_fifo_fd, buf, sizeof(buf));
			if (rd_len > 0)
				temp_event_handler(buf, rd_len);
		}

		for(int i = 0; i < NUMBER_OF_EPS; i++) {
			int fd = mctp_ops[i]->get_rx_fifo();

			if (FD_ISSET(fd, &fds)) {
				rd_len = read(fd, buf, sizeof(buf));

				if (rd_len <= 0)
					continue;

				len += rd_len;
				if (len >= mctp_ops[i]->get_min_payload()) {
					timestamp(" - RCV\n");
					mctp_ops[i]->recv(buf, len);
					len = 0;
				}
			}
		}
	}

exit:

	for(int i = 0; i < NUMBER_OF_EPS; i++)
		if (mctp_ops[i]->exit)
			mctp_ops[i]->exit();

	close(sensor_fifo_fd);
	remove(SENSOR_FIFO);
	
	return rc;
}
