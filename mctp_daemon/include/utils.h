/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_UTILS_HDR_
#define _INC_UTILS_HDR_

#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <arpa/inet.h>

#include "fw_version.h"
#include "auto_conf.h"

#define FLAGS_DAEMON_ENABLED    	(1 << 0)
#define FLAGS_VERBOSE           	(1 << 1)
#define FLAGS_NO_SU_CHECK		(1 << 2)
#define FLAGS_DEBUG			(1 << 3)
#define FLAGS_NO_SMBUS_PEC_CHECK	(1 << 4)

// define debug bits
#define GENERAL_DEBUG			(1 << 0)
#define EP_DEBUG			(1 << 1)
#define MCTP_DEBUG			(1 << 2)
#define PLDM_DEBUG			(1 << 3)
#define NCSI_DEBUG			(1 << 4)

#define _CONCAT(x, y)   x ## y
#define CONCAT(x, y)    _CONCAT(x, y)

#define SWAP32(x)       (((x) >> 24) | (((x) & 0x0000ff) << 24) | (((x) & 0x00ff00) << 8) | (((x) & 0xff0000) >> 8))
#define SWAP16(x)       ((((x) & 0xff00) >> 8) | (((x) & 0x00ff) << 8))

#define hton32(x)	SWAP32((x))
#define hton16(x)	SWAP16((x))

#define MIN(x, y)	((x) < (y) ? (x) : (y))

#define log(fmt, arg...)                                                                        \
        do {                                                                                    \
                time_t T= time(NULL);                                                           \
                struct  tm tm = *localtime(&T);                                                 \
                fprintf(log_fd, "%02d/%02d/%04d ",tm.tm_mday, tm.tm_mon+1, tm.tm_year+1900);    \
                fprintf(log_fd, "%02d:%02d:%02d ",tm.tm_hour, tm.tm_min, tm.tm_sec);            \
                fprintf(log_fd, fmt, ##arg);                                                    \
		fflush(log_fd);									\
		if (flags & FLAGS_VERBOSE) {							\
			fprintf(stderr, "%02d/%02d/%04d ",tm.tm_mday, tm.tm_mon+1, tm.tm_year+1900);	\
			fprintf(stderr, "%02d:%02d:%02d ",tm.tm_hour, tm.tm_min, tm.tm_sec);            \
			fprintf(stderr, fmt, ##arg);                                                    \
		}											\
        } while (0);

#define log_n_print(fmt, arg...)                                                                \
        do {                                                                                    \
                time_t T= time(NULL);                                                           \
                struct  tm tm = *localtime(&T);                                                 \
                fprintf(log_fd, "%02d/%02d/%04d ",tm.tm_mday, tm.tm_mon+1, tm.tm_year+1900);    \
                fprintf(log_fd, "%02d:%02d:%02d ",tm.tm_hour, tm.tm_min, tm.tm_sec);            \
                fprintf(log_fd, fmt, ##arg);                                                    \
		fflush(log_fd);									\
		fprintf(stderr, fmt, ##arg);                                                    \
        } while (0);


#define log_err(fmt, arg...)                                                                    \
        do {                                                                                    \
                time_t T= time(NULL);                                                           \
                struct  tm tm = *localtime(&T);                                                 \
                fprintf(log_fd, "%02d/%02d/%04d ",tm.tm_mday, tm.tm_mon+1, tm.tm_year+1900);    \
                fprintf(log_fd, "%02d:%02d:%02d ",tm.tm_hour, tm.tm_min, tm.tm_sec);            \
                fprintf(log_fd, "ERROR: "fmt, ##arg);                                           \
		fflush(log_fd);									\
		if (flags & FLAGS_VERBOSE) {							\
			fprintf(stderr, "%02d/%02d/%04d ",tm.tm_mday, tm.tm_mon+1, tm.tm_year+1900);	\
			fprintf(stderr, "%02d:%02d:%02d ",tm.tm_hour, tm.tm_min, tm.tm_sec);            \
			fprintf(stderr, fmt, ##arg);                                                    \
		}											\
        } while (0);

#define print_fifo(fmt, arg...)                         	\
        do {                                            	\
                sprintf(fifo_str, fmt, ##arg);          	\
                write(fifo_fd, fifo_str, strlen(fifo_str)); 	\
        } while (0)


#ifdef ARCH_BIG_ENDIAN
#define pldm2host(n)	n
#define pldm2host_16(n)	n
#define host2pldm(n)	n
#define host2pldm_16(n)	n
#else
#define pldm2host(n)	ntohl(n)
#define pldm2host_16(n)	ntohs(n)
#define host2pldm(n)	htonl(n)
#define host2pldm_16(n)	htons(n)
#endif

struct server_cfg_stc {
	uint16_t sleep;
	uint16_t timeout;
	uint8_t debug;
	char *logfile;
	char *lockfile;
	char *fru_filename;
};

extern struct server_cfg_stc cfg;
extern FILE *log_fd;
extern int flags;
extern char *manuallog_file;


void hexdump(uint8_t *addr, int len);
uint32_t crc32(uint8_t  *data_buf, uint32_t byte_cnt, uint32_t crc_in);
uint8_t crc8(const uint8_t *buf, int len);
void print_version(char *name);

#endif /* _INC_UTILS_HDR_ */
