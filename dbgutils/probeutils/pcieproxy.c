/*
 * Small Socket Server to allow a remote Client to read and write Fungible
 * Chip Control/Status Registers (CSRs).  We use an mmap() of a PCIe End Point
 * BAR into which the FunOS has mapped a CSR Control Unit (CCU) via its End
 * Point Memory Management Unit (EMMU).  THis allows us to perform "Remote
 * Indirect CSR Accesses".
 *
 * Currently, the CCU is mapped into BAR2/3 of a selected Physical Function
 * when certain Boot Arguments are present for FunOS:
 *
 *     "--csr_remote_access"
 *         Use a default: Socketed Board, HU Slice 0, HU Controller 0, PF 1.
 *
 *    "csr_remote_access_controller={controller}"
 *        Where "{controller}" is a 3-byte encoded value 0x{RI}{CI}{PF}:
 *        HSU RING (0..3), CID, PF.
 *
 * The server provides a single-threaded service with four ASCII Commands:
 *
 *   CONNECT <PCIe BAR in SysFS>
 *     -- mmap() the specified PCIe Base Address Register.  Typical names
 *     -- look like /sys/bus/pci/devices/0000:03:00.1/resource2 ...
 *     -- Response is "OKAY CONNECT <PCIe BAR in SysFS" or an Error Message.
 *
 *   DISCONNECT
 *     -- munmap() the PCIe BAR.
 *     -- Response is "OKAY DISCONNECT" or an Error Message.
 *
 *   CHIPINFO
 *     -- Returns "OKAY CHIPINFO <CSR> <Chip>", where "<CSR>" is "CSR1" or
 *     -- "CSR2" and "<Chip>" is "F1", "S1", "F1.1", etc.
 *
 *   READ <Register Address> <Register Size (in bits)>
 *     -- Returns "OKAY READ" and a sequence of 64-bit hexadecimal values
 *     -- representing the register value, or an error message.
 *
 *   WRITE <Register Address> <Register Size (in bits)> <64-bit Values> ...
 *     -- Writes a register with the provided values.  There must be
 *     -- (<Register Size> + 63)/64 <Values>.
 *     -- Response is "OKAY WRITE" or an Error Message.
 *
 *   DUMPCCU
 *     -- Dump the Control Status Register Control Unit.  Note, at least
 *     -- one READ or WRITE command should be done first to cause the
 *     -- CCU to get initialized, including the ECC Memory backing the CCU
 *     -- Indirect Register File.  We do not check for this however because
 *     -- this is purely for debugging.
 *
 *   The <Register Address>, <Register Size>, and WRITE <Values> may be in
 *   any numeric format.
 *
 * ... and yes, I know you wished this were written in Python but getting it
 * to do bit-specific things like Endianess, uint64_t addressing, etc. is
 * annoying.  Deal with the pain ...
 */
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <stdarg.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <syslog.h>

#include "hw/csr/ccu.h"
#include "endian.h"
#include "pcieproxy.h"

#define PCIEPROXY_API __attribute__((visibility("default")))

#include "libpcieproxy.h"

/*
 * CCU Server TCP Port.
 */
#define CCU_SERVER_TCP_PORT	44445

/*
 * Server Global Variables.
 */
const char *myname;
int debug = 0;
int port = CCU_SERVER_TCP_PORT;
static struct ccu_ops *ccu;

/*
 * The CCU ID CSR Type field (bit 31) defines whether we're dealing with a
 * CSR1 Chip (F1) or a CSR2 Chip (S1 and later).  The CCU ID Chip ID field
 * ([30:21]) can be used to determine which Chip we're talking to.
 */
#define CSRTYPE_CHIPID(_csrtype, _chipid) \
				(((_csrtype) << 16) | (_chipid))

#define CSR1_F1			CSRTYPE_CHIPID(1, 0)

#define CSR2_S1			CSRTYPE_CHIPID(2, 0)
#define CSR2_F1D1		CSRTYPE_CHIPID(2, 1)

/*
 * Convert bit-length into number of 64-bit units.
 */
#define SIZE64(x)	(((x) + 63) / 64)


uint32_t
ccu_read_id(struct ccu_info_t *ccu_info)
{
	uint32_t *ccu32 = (uint32_t *)ccu_info->mmap;;

	return be32toh(ccu32[CCU_ID/sizeof(*ccu32)]);
}

/*
 * Return a pointer to the CCU Spinlock to use for this CCU mapping.
 */
uint64_t *
ccu_spinlock(struct ccu_info_t *ccu_info)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint64_t null_token = htobe64(CCU_SPINLOCK_ID_PUT(CCU_SPINLOCK_NULL_ID) |
					  CCU_SPINLOCK_LOCK_PUT(0));
	uint64_t *spinlock;

	/*
	 * Find a valid configured CCU Spinlock.
	 */
	spinlock = &ccu64[CCU_SPINLOCK0 / sizeof(*ccu64)];
	if (*spinlock == null_token) {
		if (debug)
			fprintf(stderr, "Using CCU Spinlock 0\n");
		return spinlock;
	}

	spinlock = &ccu64[CCU_SPINLOCK1 / sizeof(*ccu64)];
	if (*spinlock == null_token) {
		if (debug)
			fprintf(stderr, "Using CCU Spinlock 1\n");
		return spinlock;
	}

	/* no valid CCU Spinlock found */
	if (debug)
		fprintf(stderr, "No valid configured CCU Spinlock found\n");
	return NULL;
}

/*
 * Use CCU Spinlock to prevent multiple clients from interfering with echo
 * others' register accesses.
 */
void
ccu_lock(struct ccu_info_t *ccu_info)
{
	if (ccu_info == NULL)
		return;

	do {
		*ccu_info->spinlock =
			htobe64(CCU_SPINLOCK_ID_PUT(ccu_info->spinlock_token) |
				    CCU_SPINLOCK_LOCK_PUT(1));
	} while (CCU_SPINLOCK_ID_GET(be64toh(*ccu_info->spinlock)) !=
		 ccu_info->spinlock_token);
}

void
ccu_unlock(struct ccu_info_t *ccu_info)
{
	if (ccu_info == NULL)
		return;

	*ccu_info->spinlock =
		htobe64(CCU_SPINLOCK_ID_PUT(CCU_SPINLOCK_NULL_ID) |
			    CCU_SPINLOCK_LOCK_PUT(0));
}

/*
 * Read a specified register into a provided buffer.
 */
int
pcie_csr_read(struct ccu_info_t *ccu_info,
	 uint64_t base_addr,
	 uint64_t csr_addr,
	 uint64_t *data,
	 uint32_t size)
{
	uint64_t addr = base_addr + csr_addr;

	ccu->csr_wide_read(ccu_info, addr, data, size);
	return 0;
}

/*
 * Write a specified register from a provided buffer.
 */
int
pcie_csr_write(struct ccu_info_t *ccu_info,
	  uint64_t base_addr,
	  uint64_t csr_addr,
	  uint64_t *data,
	  uint32_t size)
{
	uint64_t addr = base_addr + csr_addr;

	ccu->csr_wide_write(ccu_info, addr, data, size);
	return 0;
}

#ifdef BUILD_LIBRARY
struct ccu_info_t *pcie_csr_init(const char *name, uint64_t offset)
{
	struct ccu_info_t *ccu_info = calloc(1, sizeof(*ccu_info));

	ccu_info->fd = open(name, O_RDWR);
	if (ccu_info->fd < 0) {
		fprintf(stderr, "Can't open %s: %s\n", name, strerror(errno));
		goto err;
	}

	ccu_info->mmap = mmap(NULL, CCU_MAP_SIZE,
					PROT_READ|PROT_WRITE,
					MAP_SHARED|MAP_LOCKED,
					ccu_info->fd, offset);
	if (ccu_info->mmap == MAP_FAILED) {
		fprintf(stderr, "Can't mmap %s: %s\n",
				name, strerror(errno));
		goto err_fd;
	}

	ccu_info->spinlock_token = getpid();
	ccu_info->spinlock = ccu_spinlock(ccu_info);
	uint32_t ccu_id = ccu_read_id(ccu_info);
	ccu = CCU_ID_CSRTYPE_GET(ccu_id) == 0 ?
		&csr1_ops : &csr2_ops;

	return ccu_info;
err_fd:
	close(ccu_info->fd);
err:
	free(ccu_info);
	return NULL;
}

void pcie_csr_close(struct ccu_info_t *ccu_info)
{
	if (!ccu_info)
		return;

	if (ccu_info->mmap)
		munmap(ccu_info->mmap, CCU_MAP_SIZE);

	if (ccu_info->fd >= 0)
		close(ccu_info->fd);

	free(ccu_info);
}

void pcie_csr_enable_debug(bool enable)
{
	debug = enable;
}
#endif

#ifdef BUILD_SERVER

/*
 * ============
 * Main Server.
 * ============
 */

/*
 * This is the part that would be easier in Python ...
 */

#define MAX_COMMAND_WORDS	(CCU_DATA_REG_CNT + 2)	/* WRITE addr ... */
#define MAX_COMMAND_WORD_LENGTH	(2 + 64/4 + 1)		/* 0x...\0 */
#define MAX_COMMAND_LINE	(MAX_COMMAND_WORDS * MAX_COMMAND_WORD_LENGTH)

#define MAX_RESPONSE_WORDS	(CCU_DATA_REG_CNT + 1)	/* OKAY value ... */
#define MAX_RESPONSE_WORD_LENGTH MAX_COMMAND_WORD_LENGTH
#define MAX_RESPONSE_LINE	(MAX_RESPONSE_WORDS * MAX_RESPONSE_WORD_LENGTH)

void
response(int fd, int priority, const char *format, ...)
{
	va_list args;

	if (priority > 0) {
		va_start(args, format);
		vsyslog(priority, format, args);
		va_end(args);
	}

	if (fd > 0) {
		va_start(args, format);
		vdprintf(fd, format, args);
		va_end(args);
	}

	if (debug) {
		va_start(args, format);
		vfprintf(stderr, format, args);
		va_end(args);
	}
}

int
server(int client_fd)
{
	struct ccu_info_t ccu_info;
	int err = 0;

	ccu_info.fd = -1;
	ccu_info.mmap = NULL;

	while (1) {
		char command[MAX_COMMAND_LINE];
		char *argv[MAX_COMMAND_WORDS];
		char *cp;
		int cc, argc;
		int inword;

		/*
		 * Grab a command from the socket and parse it into
		 * non-whitespace words.
		 */
		cc = read(client_fd, command, sizeof command);
		if (cc <= 0) {
			err = errno;
			response(-1, LOG_ERR,
				 "Unable to read from socket: %s\n",
				 strerror(errno));
			break;
		}
		if (cc >= MAX_COMMAND_LINE-1) {
			response(client_fd, LOG_DEBUG,
				 "Command line too long\n");
			continue;
		}
		command[cc] = '\0';

		cp = command;
		argc = 0;
		inword = 0;
		while (*cp) {
			if (isspace(*cp)) {
				if (inword) {
					*cp = '\0';
					argc++;
					inword = 0;
				}
			} else if (!inword) {
				argv[argc] = cp;
				inword = 1;
			}
			cp++;
		}
		if (inword) {
			argc++;
			inword = 0;
		}

		/*
		 * Blank commands aren't accepted.
		 */
		if (argc <= 0) {
			response(client_fd, LOG_DEBUG,
				 "Bad [blank] command line\n");
			continue;
		}

		/*
		 * See what the remote user wants ...
		 */
		if (strcmp(argv[0], "CONNECT") == 0) {
			unsigned long long offset = 0;
			/*
			 * CONNECT <PCIe BAR in SysFS>
			 */

			if (ccu_info.mmap) {
				response(client_fd, LOG_DEBUG,
					 "Already connected!\n");
				continue;
			}

			if (argc < 2 || argc > 3) {
				response(client_fd, LOG_DEBUG,
					 "Usage: CONNECT <BAR> <offset>\n");
				continue;
			}

			ccu_info.fd = open(argv[1], O_RDWR);
			if (ccu_info.fd < 0) {
				response(client_fd, LOG_DEBUG,
					 "Can't open %s: %s\n",
					 argv[1], strerror(errno));
				continue;
			}

			if (argc == 3) {
				offset = strtoull(argv[2], NULL, 0);
			}

			ccu_info.mmap = mmap(NULL, CCU_MAP_SIZE,
					     PROT_READ|PROT_WRITE,
					     MAP_SHARED|MAP_LOCKED,
					     ccu_info.fd, offset);
			if (ccu_info.mmap == MAP_FAILED) {
				response(client_fd, LOG_DEBUG,
					 "Can't mmap %s: %s\n",
					 argv[1], strerror(errno));
				close(ccu_info.fd);
				ccu_info.fd = -1;
				ccu_info.mmap = NULL;
				continue;
			}

			ccu_info.spinlock_token = getpid();
			ccu_info.spinlock = ccu_spinlock(&ccu_info);
			uint32_t ccu_id = ccu_read_id(&ccu_info);
			ccu = CCU_ID_CSRTYPE_GET(ccu_id) == 0 ?
				&csr1_ops : &csr2_ops;

			response(client_fd, LOG_DEBUG, "OKAY CONNECT %s\n",
				 argv[1]);
			continue;
		}

		if (strcmp(argv[0], "DISCONNECT") == 0) {
			/*
			 * DISCONNECT (ignore any extra arguments)
			 */

			response(client_fd, LOG_DEBUG, "OKAY DISCONNECT\n");
			break;
		}

		if (strcmp(argv[0], "CHIPINFO") == 0) {
			/*
			 * CHIPINFO (ignore any extra arguments)
			 */
			uint32_t ccu_id;
			unsigned int csrtype, chipid;
			const char *chip;

			if (!ccu_info.mmap) {
				response(client_fd, LOG_DEBUG,
					 "Not Connected!\n");
				continue;
			}

			/*
			 * Read and decode the CCU ID.
			 */
			ccu_id = ccu_read_id(&ccu_info);
			csrtype = CCU_ID_CSRTYPE_GET(ccu_id) == 0 ? 1 : 2;
			chipid = CCU_ID_CHIPID_GET(ccu_id);

			switch (CSRTYPE_CHIPID(csrtype, chipid)) {
			case CSR1_F1:
				chip = "F1";
				break;

			case CSR2_S1:
				chip = "S1";
				break;

			case CSR2_F1D1:
				chip = "F1.1";
				break;

			default:
				response(client_fd, LOG_DEBUG,
					 "CSR%d bad Chip ID %u\n",
					 csrtype, chipid);
				continue;
			}

			response(client_fd, LOG_DEBUG,
				 "OKAY CHIPINFO CSR%u %s\n",
				 csrtype, chip);
			continue;
		}

		if (strcmp(argv[0], "READ") == 0) {
			/*
			 * READ <Register Address> <Register Size (in bits)>
			 */

			uint64_t csr_addr;
			uint32_t csr_size, size64;
			uint64_t csr_buf[CCU_DATA_REG_CNT];
			int vidx;
			char response_msg[MAX_RESPONSE_LINE];
			FILE *response_fp;

			if (!ccu_info.mmap) {
				response(client_fd, LOG_DEBUG,
					 "Not Connected!\n");
				continue;
			}

			if (argc != 3) {
				response(client_fd, LOG_DEBUG,
					 "Read command takes 2 arguments\n");
				continue;
			}

			csr_addr = strtoull(argv[1], NULL, 0);
			csr_size = strtoul(argv[2], NULL, 0);
			size64 = SIZE64(csr_size);
			if (size64 == 0 || size64 > CCU_DATA_REG_CNT) {
				response(client_fd, LOG_DEBUG,
					 "Bad CSR Size %u\n", csr_size);
				continue;
			}

			pcie_csr_read(&ccu_info, 0, csr_addr, csr_buf, csr_size);

			response_fp = fmemopen(response_msg,
					       sizeof response_msg,
					       "w");
			if (response_fp == NULL) {
				response(client_fd, LOG_DEBUG,
					 "Unable to create response buffer\n");
				continue;
			}

			fputs("OKAY READ", response_fp);
			for (vidx = 0; vidx < size64; vidx++)
				fprintf(response_fp, " %#lx", csr_buf[vidx]);
			fputc('\n', response_fp);
			fclose(response_fp);

			response(client_fd, LOG_DEBUG, response_msg);
			continue;
		}

		if (strcmp(argv[0], "WRITE") == 0) {
			/*
			 * WRITE <Register Address> <Register Size (in bits)>
			 *     <64-bit Values> ...
			 */

			uint64_t csr_addr;
			uint32_t csr_size, size64;
			uint64_t csr_buf[CCU_DATA_REG_CNT];
			int nvalues, vidx;

			if (!ccu_info.mmap) {
				response(client_fd, LOG_DEBUG,
					 "Not Connected!\n");
				continue;
			}

			nvalues = argc - 3;
			if (nvalues <= 0) {
				response(client_fd, LOG_DEBUG,
					 "Write command needs values\n");
				continue;
			}

			csr_addr = strtoull(argv[1], NULL, 0);
			csr_size = strtoul(argv[2], NULL, 0);
			size64 = SIZE64(csr_size);
			if (nvalues != size64) {
				response(client_fd, LOG_DEBUG,
					 "Need %u value%s\n", size64,
					 size64 == 1 ? "" : "s");
				continue;
			}
			if (size64 == 0 || size64 > CCU_DATA_REG_CNT) {
				response(client_fd, LOG_DEBUG,
					 "Bad CSR Size %u\n", csr_size);
				continue;
			}
			for (vidx = 0; vidx < size64; vidx++)
				csr_buf[vidx] = strtoull(argv[vidx+3],
							 NULL, 0);

			pcie_csr_write(&ccu_info, 0, csr_addr, csr_buf, csr_size);
			response(client_fd, LOG_DEBUG, "OKAY WRITE\n");
			continue;
		}

		if (strcmp(argv[0], "DUMPCCU") == 0) {
			/*
			 * DUMPCCU (ignore any extra arguments)
			 */

			if (!ccu_info.mmap) {
				response(client_fd, LOG_DEBUG,
					 "Not Connected!\n");
				continue;
			}

			ccu->ccu_dump(&ccu_info);
			response(client_fd, LOG_DEBUG, "OKAY DUMPCCU\n");
			continue;
		}

		response(client_fd, LOG_DEBUG, "Bad command: %s\n", argv[0]);
		continue;
	}

	if (ccu_info.mmap) {
		munmap(ccu_info.mmap, CCU_MAP_SIZE);
		close(ccu_info.fd);
	}

	return err;
}

/*
 * =============
 * Main Program.
 * =============
 */

void
debuglog(int priority, const char *format, ...)
{
	va_list args;

	if (priority > 0) {
		va_start(args, format);
		vsyslog(priority, format, args);
		va_end(args);
	}

	if (debug) {
		va_start(args, format);
		vfprintf(stderr, format, args);
		va_end(args);
	}
}

void
usage(void)
{
	fprintf(stderr,
		"usage: %s [-d] [-h] [-p <TCP Server Port>\n"
		"    -d         debug/don't daemonize\n"
		"    -h         help/this message\n"
		"    -p <port>  specify different TCP Server Port\n",
		myname);
}

/*
 * Main program which forms Server for truly remote access to Control/Status
 * registers.
 */
int
main(int argc, char *const argv[])
{
	int server_fd, client_fd;
	struct sockaddr_in server_inaddr;
	int opt, sock_opt;

	/*
	 * Parse any command line arguments ...
	 */
	myname = strrchr(argv[0], '/');
	if (myname)
		myname++;
	else
		myname = argv[0];
	while ((opt = getopt(argc, argv, "dhp:")) != -1) {
		extern char *optarg;
		extern int optind;

		switch (opt) {
		case 'd':
			debug = 1;
			break;

		case 'h':
			usage();
			exit(EXIT_SUCCESS);
			/*NOTREACHED*/

		case 'p':
			port = atoi(optarg);
			break;

		default:
			usage();
			exit(EXIT_FAILURE);
			/*NOTREACHED*/
		}
	}

	/*
	 * Create Server Socket, bind our special TCP Port number to it,
	 * and become a Daemon (if desired).
	 */
	server_fd = socket(AF_INET, SOCK_STREAM, 0);
	if (server_fd < 0) {
		fprintf(stderr, "%s: unable to open Server Socket: %s\n",
			myname, strerror(errno));
		exit(EXIT_FAILURE);
		/*NOTREACHED*/
	}

	sock_opt = 1;
	if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &sock_opt,
		       sizeof(sock_opt)) < 0) {
		fprintf(stderr, "%s: Can't reuse socket address: %s\n",
			myname, strerror(errno));
		exit(EXIT_FAILURE);
		/*NOTREACHED*/
	}

	memset(&server_inaddr, 0, sizeof server_inaddr);
	server_inaddr.sin_family = AF_INET;
	server_inaddr.sin_port = htobe16(CCU_SERVER_TCP_PORT);
	server_inaddr.sin_addr.s_addr = htobe32(INADDR_ANY);
	if (bind(server_fd, (struct sockaddr *)&server_inaddr,
		 sizeof server_inaddr) != 0) {
		fprintf(stderr, "%s: unable to bind address to Server Socket: %s\n",
			myname, strerror(errno));
		exit(EXIT_FAILURE);
		/*NOTREACHED*/
	}

	if (listen(server_fd, 5) < 0) {
		fprintf(stderr, "%s: unable to listen on Server Socket: %s\n",
			myname, strerror(errno));
	}

	/*
	 * If we're going to become a Daemon, this will be our last
	 * contact with the TTY ...
	 */
	if (!debug) {
		pid_t daemon = fork();

		if (daemon < 0) {
			fprintf(stderr, "%s: unable to daemonize: %s\n",
				myname, strerror(errno));
			exit(EXIT_FAILURE);
			/*NOT_REACHED*/
		}
		if (daemon) {
			exit(EXIT_SUCCESS);
			/*NOTREACHED*/
		}

		fclose(stdin);
		fclose(stdout);
		fclose(stderr);
	}

	/*
	 * Main server accept loop.
	 */
	openlog(myname, 0, LOG_USER);

	while (1) {
		int client_fd, err;
		struct sockaddr_in client_inaddr;
		socklen_t client_addrlen;
		pid_t client_pid;

		/*
		 * Accept new incoming connection request.
		 */
		client_addrlen = sizeof client_inaddr;
		client_fd = accept(server_fd,
				   (struct sockaddr *)&client_inaddr,
				   &client_addrlen);
		if (client_fd < 0) {
			debuglog(LOG_ERR, "Can't accept incoming connection: %s\n",
				 strerror(errno));
			close(server_fd);
			exit(EXIT_FAILURE);
			/*NOTREACHED*/
		}

		/*
		 * Fork child process to handle the incoming request.
		 */
		client_pid = fork();
		if (client_pid < 0) {
			debuglog(LOG_ERR, "Can't fork client server process: %s\n",
				 strerror(errno));
			shutdown(client_fd, SHUT_RDWR);
			close(client_fd);
			continue;
		}
		if (client_pid) {
			debuglog(LOG_DEBUG, "Forked client server for client %s:%d\n",
				 inet_ntoa(client_inaddr.sin_addr),
				 be16toh(client_inaddr.sin_port));
			continue;
		}

		/*
		 * And in the child process, we process the request.
		 */
		err = server(client_fd);
		if (err)
			debuglog(LOG_ERR, "Server for client %s:%d returned error: %s\n",
				 inet_ntoa(client_inaddr.sin_addr),
				 be16toh(client_inaddr.sin_port),
				 strerror(errno));
		else
			debuglog(LOG_DEBUG, "Server for client %s:%d completed successfully\n",
				 inet_ntoa(client_inaddr.sin_addr),
				 be16toh(client_inaddr.sin_port));

		shutdown(client_fd, SHUT_RDWR);
		close(client_fd);
	}

	close(server_fd);
	closelog();
	exit(EXIT_SUCCESS);
	/*NOTREACHED*/
}

#endif  /* BUILD_SERVER */
