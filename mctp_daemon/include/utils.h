/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fung ible. All rights reserved.
 */
#ifndef _INC_UTILS_HDR_
#define _INC_UTILS_HDR_

#include <stdio.h>
#include <stdint.h>
#include <time.h>

#include "fw_version.h"
#include "auto_conf.h"

#define FLAGS_DAEMON_ENABLED    (1 << 0)
#define FLAGS_VERBOSE           (1 << 1)
#define FLAGS_NO_SU_CHECK	(1 << 2)
#define FLAGS_DEBUG		(1 << 3)

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

/* unaligned assignment
 * MIPS architecture does not natively  support unaligned word access
 * e.g. 32bit variable that isn't on 4 bytes alignment (ADD[1:0] = 2'b0) will cause an exception
 * the pldm spec is full with such variables hence a "memcpy" method is required
 * to move data to packed unaligned structured variables
 */
#define ASSIGN32_LE(x, n)                           \
	do {                                                \
		*(((uint8_t *)&(x))+0) = ((n) & 0xff);      \
		*(((uint8_t *)&(x))+1) = (((n)>>8) & 0xff); \
		*(((uint8_t *)&(x))+2) = (((n)>>16) & 0xff);\
		*(((uint8_t *)&(x))+3) = (((n)>>24) & 0xff);\
	} while (0)

#define ALIGN32_BE(x)   (uint32_t)(((*(((uint8_t *)&(x))+0)) << 0)  | \
                                   ((*(((uint8_t *)&(x))+1)) << 8)  | \
                                   ((*(((uint8_t *)&(x))+2)) << 16) | \
                                   ((*(((uint8_t *)&(x))+3)) << 24))

#define ASSIGN16_LE(x, n)                           \
	do {                                                \
		*(((uint8_t *)&(x))+0) = ((n) & 0xff);      \
		*(((uint8_t *)&(x))+1) = (((n)>>8) & 0xff); \
	} while (0)

#define ALIGN16_BE(x)   (uint16_t)(((*(((uint8_t *)&(x))+0)) << 0)  | \
                                   ((*(((uint8_t *)&(x))+1)) << 8))

#define ASSIGN32_BE(x, n)                           \
	do {                                                \
		*(((uint8_t *)&(x))+3) = ((n) & 0xff);      \
		*(((uint8_t *)&(x))+2) = (((n)>>8) & 0xff); \
		*(((uint8_t *)&(x))+1) = (((n)>>16) & 0xff);\
		*(((uint8_t *)&(x))+0) = (((n)>>24) & 0xff);\
	} while (0)

#define ALIGN32_LE(x)   (uint32_t)(((*(((uint8_t *)&(x))+3)) << 0)  | \
                                   ((*(((uint8_t *)&(x))+2)) << 8)  | \
                                   ((*(((uint8_t *)&(x))+1)) << 16) | \
                                   ((*(((uint8_t *)&(x))+0)) << 24))

#define ASSIGN16_BE(x, n)                           \
	do {                                                \
		*(((uint8_t *)&(x))+1) = ((n) & 0xff);      \
		*(((uint8_t *)&(x))+0) = (((n)>>8) & 0xff); \
	} while (0)

#define ALIGN16_LE(x)   (uint16_t)(((*(((uint8_t *)&(x))+1)) << 0)  | \
                                   ((*(((uint8_t *)&(x))+0)) << 8))


struct server_cfg_stc {
	uint16_t sleep;
	uint16_t timeout;
	uint8_t debug;
	char *logfile;
	char *lockfile;
};

extern struct server_cfg_stc cfg;
extern FILE *log_fd;
extern int flags;
extern char *manuallog_file;


void hexdump(uint8_t *addr, int len);
uint32_t crc32(uint8_t  *data_buf, uint32_t byte_cnt, uint32_t crc_in);
void print_version(char *name);
void manual_log(char *str);

#endif /* _INC_UTILS_HDR_ */
