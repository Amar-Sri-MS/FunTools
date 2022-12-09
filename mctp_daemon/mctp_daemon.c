/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdint.h> 
#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <syslog.h>
#include <string.h>
#include <getopt.h>
#include<signal.h>

#include "utils.h"
#include "mctp.h"
#include "pldm.h"

extern int main_loop();

FILE *log_fd;
int flags = 0;
char *lock, *log_file;
uint8_t eid = 0;

struct server_cfg_stc cfg = {
	.sleep = 60,
	.timeout = 10,
	.pcie_req_id = 0,
	.lockfile = "/tmp/mctp_daemon.lock",
	.logfile = "/tmp/mctp_daemon.log",
	.fru_filename = NULL,
	.uuid = {0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf},
	.debug = 0,
	.polling = 100,
};

static void segfault_handler()
{
	for(int i = 0; i < NUMBER_OF_EPS; i++)
                if (mctp_ops[i]->exit)
                        mctp_ops[i]->exit();

        remove(lock);
        fclose(log_fd);

        exit(0);
}

#define CHAR2HEX(n)		((n) >='A' && (n) <= 'F') ? ((n) - 0x37) : ((n) >= 'a' && (n) <= 'f') ? ((n) - 0x57) : ((n) >= '0' && ((n) <= '9')) ? ((n) - 0x30) : 0
static void set_uuid(char *uuid)
{
	int len = (strlen(uuid) > 32) ? 32 : strlen(uuid);

	for(int i =0, j = 0; i < len; i+=2, j++) 
		cfg.uuid[j] = (CHAR2HEX(uuid[i]) << 8) + CHAR2HEX(uuid[i+1]);
}

static void usage()
{
	fprintf(stderr, "usage: mctp_daemon [options]\n");
	fprintf(stderr, "\t-a | --async  : Enable Async events\n");
	fprintf(stderr, "\t-b | --daemon : Run in background\n");
	fprintf(stderr, "\t-h | --help   : Print this help\n");
	fprintf(stderr, "\t-l | --log    : Specify logfile\n");
	fprintf(stderr, "\t-n | --nosu   : Run as non-root\n");
	fprintf(stderr, "\t-u | --uuid   : Set UUID\n");
	fprintf(stderr, "\t-v | --verbose: Be verbose\n");
	fprintf(stderr, "\t-D | --debug  : Turn on debug mode\n");
	fprintf(stderr, "\t-E | --eid    : Set termious EID\n");
	fprintf(stderr, "\t-F | --fru    : Set FRU filename\n");
	fprintf(stderr, "\t-L | --lock   : Specify lockfile\n");
	fprintf(stderr, "\t-T | --tid    : Set Async TID\n");
	fprintf(stderr, "\t-V | --version: Print current version\n");

	exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[])
{
	pid_t pid, sid;
	uid_t uid=getuid(), euid=geteuid();
        int c, index = 0, fd2;
	struct sigaction sa;

        struct option long_args[] = {
                {"async",       0, 0, 'a'},
                {"daemon",      1, 0, 'b'},
                {"help",        1, 0, 'h'},
                {"log",         1, 0, 'l'},
		{"nosu",	0, 0, 'n'},
		{"pcie_id",	0, 0, 'p'},
		{"uuid",	1, 0, 'u'},
                {"verbose",     1, 0, 'v'},
		{"debug",	0, 0, 'D'},
		{"eid",		1, 0, 'E'},
		{"fru",		1, 0, 'F'},
		{"nopec",	0, 0, 'I'},
                {"lock",        1, 0, 'L'},
                {"polling",     1, 0, 'P'},
                {"tid",         1, 0, 'T'},
		{"version",	0, 0, 'V'},
		{"nolencheck",	0, 0, 'Z'},
                {0, 0, 0, 0}};

        opterr = 0;
        optind = 1;

	log_file = cfg.logfile;
	lock = cfg.lockfile;

        // install sigfault handler
        memset(&sa, 0, sizeof(struct sigaction));
        sigemptyset(&sa.sa_mask);
        sa.sa_sigaction = segfault_handler;
        sa.sa_flags   = SA_SIGINFO;
        sigaction(SIGSEGV, &sa, NULL);


        while ((c = getopt_long(argc, argv, "abhl:np:u:vDE:F:IL:P:T:VZ", long_args, &index)) != -1) {
		switch (c) {
		case 'a':
			pldm_vars.flags |= MCTP_VDM_ASYNC_ENABLED;
			break;

		case 'h':
			usage();
			break;

		case 'l':
			log_file = optarg;
			break;

		case 'n':
			flags |= FLAGS_NO_SU_CHECK;
			break;

		case 'p':
			cfg.pcie_req_id = (uint16_t)strtol(optarg, NULL, 0);
			break;

		case 'u':
			set_uuid(optarg);
			break;

		case 'L':
			lock = optarg;
			break;

		case 'b':
			flags |= FLAGS_DAEMON_ENABLED;
			break;

		case 'v':
			flags |= FLAGS_VERBOSE;
			break;

		case 'D':
			cfg.debug = 1;
			if (optarg == NULL && argv[optind] != NULL && argv[optind][0] != '-') {
				cfg.debug = (uint8_t)strtol(argv[optind], NULL, 0);
				optind++;
			}
			break;

		case 'E':
			eid = (uint8_t)strtol(optarg, NULL, 0);
			break;

		case 'F':
			cfg.fru_filename = optarg;
			break;

		case 'I':
			flags |= FLAGS_NO_SMBUS_PEC_CHECK;
			break;

		case 'P':
			cfg.polling = (uint8_t)strtol(optarg, NULL, 0);
			break;

		case 'T':
			pldm_vars.async_tid = (uint8_t)strtol(optarg, NULL, 0);
			break;

		case 'V':
			print_version("MCTP Daemon");
			exit(EXIT_SUCCESS);

		case 'Z':
			flags |= FLAGS_NO_PLDM_LEN_CHECK;
			break;

		default:
			fprintf(stderr, "Unknown option %c\n", c);
			exit(EXIT_FAILURE);
		}
	}

	if ((log_fd = fopen(log_file, "a+")) == NULL) {
		fprintf(stderr, "Error - cannot open logfile %s\n", log_file);
		exit(EXIT_FAILURE);
	}

	log("Debug: %s\n", (cfg.debug) ? "Enabled" : "Disabled");

	if (!(flags & FLAGS_NO_SU_CHECK) && (uid != 0 || euid != 0)) {
		log_n_print("Error - not root user\n");
		exit(EXIT_FAILURE);
	}

	if (access(lock, F_OK ) >= 0) {
		log_n_print("MCTP daemon already running\n");
		exit(EXIT_FAILURE);
	} else {
		char pid_str[32];
		
		fd2 = open(lock, O_RDWR | O_CREAT, S_IRUSR | S_IRGRP | S_IROTH);
		if (fd2 < 0) {
			log_n_print("Error - Cannot create lock file\n");
			exit(EXIT_FAILURE);
		}

		snprintf(pid_str, sizeof(pid_str), "%d", getpid());
		write(fd2, pid_str, strlen(pid_str));
	}

	if (flags & FLAGS_DAEMON_ENABLED) {
		pid = fork();
		if (pid < 0) {
			remove(lock);
			exit(EXIT_FAILURE);
		}

		if (pid > 0) {
			char pid_str[32];

			snprintf(pid_str, sizeof(pid_str), "\n%d", pid);
			write(fd2, pid_str, strlen(pid_str));
			exit(EXIT_SUCCESS);
		}

		umask(0);

		sid = setsid();
		if (sid < 0) {
			remove(lock);
			exit(EXIT_FAILURE);
		}

		if ((chdir("/")) < 0) {
			remove(lock);
			exit(EXIT_FAILURE);
		}

		close(STDIN_FILENO);
		close(STDOUT_FILENO);
		close(STDERR_FILENO);
	}

	log("MCTP Daemon started\n");

	main_loop();
	
	remove(lock);
	fclose(log_fd);

	exit(EXIT_SUCCESS);
} 
