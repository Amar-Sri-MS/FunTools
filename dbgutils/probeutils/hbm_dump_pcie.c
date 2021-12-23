/*
 * Tool to dump HBM contents over PCIe using csr peek
 */
#include <stdio.h>
#include <ctype.h>
#include <stdbool.h>
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
#include <syslog.h>
#include <assert.h>
#include <libgen.h>
#include <inttypes.h>

#define MEM_RW_CMD_CSR_ADDR 0x90001900f0ull
#define MEM_RW_STATUS_CSR_ADDR 0x90001900f8ull
#define MEM_RW_DATA_CSR_ADDR 0x9000190100ull
#define MUH_RING_SKIP_ADDR 0x800000000ull
#define MUH_SNA_ANODE_SKIP_ADDR 0x10000ull
#define MUH_SNA_CMD_ADDR_START 0x1000ull

#define MIO_FATAL_INTR_BSET 0xb000000030ull
#define HBM_SIZE_GB         ((uint64_t)8 << 30) // 8GB

/*
 * Server Global Variables.
 */
const char *myname;

/*
 * Client Global Variables and Types.
 */
typedef struct {
	int		fd;
	void		*mmap;
	pid_t		spinlock_token;
	uint64_t	*spinlock;
} ccu_info_t;


/*
 * =================
 * Endian utilities.
 * =================
 */

/*
 * Swap the endianess of a 64-bit (8-byte) argument and return the result.
 */
uint64_t
swab64(uint64_t u64)
{
	return ((((u64 >> 56) & 0xff) <<  0) |
		(((u64 >> 48) & 0xff) <<  8) |
		(((u64 >> 40) & 0xff) << 16) |
		(((u64 >> 32) & 0xff) << 24) |
		(((u64 >> 24) & 0xff) << 32) |
		(((u64 >> 16) & 0xff) << 40) |
		(((u64 >>  8) & 0xff) << 48) |
		(((u64 >>  0) & 0xff) << 56));
}

/*
 * Swap the endianess of a 32-bit (4-byte) argument and return the result.
 */
uint32_t
swab32(uint32_t u32)
{
	return ((((u32 >> 24) & 0xff) <<  0) |
		(((u32 >> 16) & 0xff) <<  8) |
		(((u32 >>  8) & 0xff) << 16) |
		(((u32 >>  0) & 0xff) << 24));
}

/*
 * Swap the endianess of a 16-bit (2-byte) argument and return the result.
 */
uint16_t
swab16(uint16_t u16)
{
	return ((((u16 >> 8) & 0xff) << 0) |
		(((u16 >> 0) & 0xff) << 8));
}

#if __BYTE_ORDER == __BIG_ENDIAN

#define cpu_to_be64(x) ((uint64_t)(x))
#define cpu_to_be32(x) ((uint32_t)(x))
#define cpu_to_be16(x) ((uint16_t)(x))

#define be64_to_cpu(x) ((uint64_t)(x))
#define be32_to_cpu(x) ((uint32_t)(x))
#define be16_to_cpu(x) ((uint16_t)(x))

#define cpu_to_le64(x) swab64(x)
#define cpu_to_le32(x) swab32(x)
#define cpu_to_le16(x) swab16(x)

#define le64_to_cpu(x) swab64(x)
#define le32_to_cpu(x) swab32(x)
#define le16_to_cpu(x) swab16(x)

#elif __BYTE_ORDER == __LITTLE_ENDIAN

#define cpu_to_be64(x) swab64(x)
#define cpu_to_be32(x) swab32(x)
#define cpu_to_be16(x) swab16(x)

#define be64_to_cpu(x) swab64(x)
#define be32_to_cpu(x) swab32(x)
#define be16_to_cpu(x) swab16(x)

#define cpu_to_le64(x) ((uint64_t)(x))
#define cpu_to_le32(x) ((uint32_t)(x))
#define cpu_to_le16(x) ((uint16_t)(x))

#define le64_to_cpu(x) ((uint64_t)(x))
#define le32_to_cpu(x) ((uint32_t)(x))
#define le16_to_cpu(x) ((uint16_t)(x))

#else

#error Unknown Endianess!

#endif


/*
 * =======================================================
 * START: Code extracted from FunOS: hw/csr/ccu.h
 * =======================================================
 */

#define CCU_RING_SHF	(35)
#define CCU_RING_MSK	(0x1f)

// Slave Ring Number (5-bits)

#define CCU_RING_SHF	(35)
#define CCU_RING_MSK	(0x1f)

#define CCU_RING_WIDE	(0)
#define CCU_RING_PUT(n) (1 + (n))	// n = 0..7
#define CCU_RING_CUT	(9)
#define CCU_RING_NUT(n) (10 + (n))	// n = 0..1
#define CCU_RING_HSU(n) (12 + (n))	// n = 0..5
#define CCU_RING_MUH(n) (18 + (n))	// n = 0..1
#define CCU_RING_MUD(n) (20 + (n))	// n = 0..1
#define CCU_RING_MIO(n) (22 + (n))	// n = 0..1

// registers index

#define CCU_CMD_REG		(0)
#define CCU_DATA_REG_CNT	(11)
#define CCU_DATA(n)		(1 + (n))	// n = 0..(CCU_DATA_REG_CNT - 1)
#define CCU_DATA_ADDR(n)	(CCU_DATA(n) * sizeof(uint64_t))
#define CCU_REG_SPACE		(16)
#define CCU_REG_EMUID		(0x78)
#define CCU_REG_ECC_STATUS	(0x78)
#define CCU_WID_MAX		(CCU_DATA_REG_CNT * CCU_REG_WID)

// transaction type

#define CCU_CMD_TYPE_REQ	0
#define CCU_CMD_TYPE_GRANT	1
#define CCU_CMD_TYPE_RD_T       2
#define CCU_CMD_TYPE_WR_T       3
#define CCU_CMD_TYPE_RD_RSP	4
#define CCU_CMD_TYPE_WR_RSP     5

// command init field

#define CCU_CMD_INIT_DIS	0
#define CCU_CMD_INIT_ENB        1       // send init pattern

// command register bit masks - command 24-bits (write)

#define CCU_CMD_TYPE_MSK	(0x0fULL)
#define CCU_CMD_TYPE_SHF	(60)
#define CCU_CMD_SIZE_MSK	(0x3fULL)
#define CCU_CMD_SIZE_SHF	(54)
#define CCU_CMD_RING_MSK	(0x1fULL)
#define CCU_CMD_RING_SHF	(49)
#define CCU_CMD_INIT_MSK	(0x01ULL)
#define CCU_CMD_INIT_SHF        (48)
#define CCU_CMD_CRSV_MSK	(0x03ULL)
#define CCU_CMD_CRSV_SHF	(45)
#define CCU_CMD_TAG_MSK		(0x1fULL)
#define CCU_CMD_TAG_SHF		(40)

// command register bit masks - status 8-bits (read)

#define CCU_CMD_BUSY_MSK        (0x01ULL)		// read only
#define CCU_CMD_BUSY_SHF	(47)			// read only
#define CCU_CMD_SRSV_MSK        (0x03ULL)		// read only
#define CCU_CMD_SRSV_SHF        (44)                    // read only
#define CCU_CMD_CLM_MSK         (0x01ULL)               // read only
#define CCU_CMD_CLM_SHF         (43)			// read only
#define CCU_CMD_RSP_MSK		(0x07ULL)		// read only
#define CCU_CMD_RSP_SHF         (40)			// read only

// command register bit masks - address 40-bits

#define CCU_CMD_ADDR_MSK        (0x0ffffffffffULL)      // 40-bit
#define CCU_CMD_ADDR_SHF        (0)

/*
 * constructing the command register value
 *
 * ty - type - transaction type
 * sz - size - see above
 * rn - ring - wide register access always use ring 0
 * init - initialize the ring - should be 0 for wide reg access
 * tag - destination buffer address (for tracking purpose)
 * adr - address - wide register address (40-bit)
 */
#define CCU_CMD(ty, sz, rn, init, tag, adr)	\
	((((uint64_t)(ty)   & CCU_CMD_TYPE_MSK) << CCU_CMD_TYPE_SHF) | \
	  (((uint64_t)(sz)   & CCU_CMD_SIZE_MSK) << CCU_CMD_SIZE_SHF) | \
	  (((uint64_t)(rn)   & CCU_CMD_RING_MSK) << CCU_CMD_RING_SHF) | \
	  (((uint64_t)(init) & CCU_CMD_INIT_MSK) << CCU_CMD_INIT_SHF) | \
	  (((uint64_t)(tag)  & CCU_CMD_TAG_MSK)	<< CCU_CMD_TAG_SHF) | \
	  (((uint64_t)(adr)  & CCU_CMD_ADDR_MSK) << CCU_CMD_ADDR_SHF))

/*
 * =====================================================
 * END: Code extracted from FunOS: hw/csr/ccu.h
 * =====================================================
 */


/*
 * ==============================================
 * Fundamentals of accesses the CSR Control Unit.
 * ==============================================
 */

/*
 * Registers are read and written via the CCU's Indirect Access commands.
 * Registers have an Address within the Fungible Chip's Address Space, and
 * a Size (in bits).  The Caller provides a Data Buffer of 64-bit words to
 * read register values into or write new register values.
 */

/*
 * The PCIe Remote Access mapping in the End Point MMU is 4KB.  All of this
 * should really be in a FunHW or FunOS include file ...
 */
#define CCU_SIZE		4096

#define CCU_SPINLOCK0		4072
#define CCU_SPINLOCK1		4080
#define CCU_ID			4092

#define CCU_SPINLOCK_ID_SHF	(32)
#define CCU_SPINLOCK_ID_MSK	(0x7fffffffUL)
#define CCU_SPINLOCK_ID_PUT(x)	((uint64_t)(x) << CCU_SPINLOCK_ID_SHF)
#define CCU_SPINLOCK_ID_GET(x)	((uint32_t)(((x) >> CCU_SPINLOCK_ID_SHF) & \
					    CCU_SPINLOCK_ID_MSK))
#define CCU_SPINLOCK_NULL_ID	0x7fffffffUL

#define CCU_SPINLOCK_LOCK_SHF	(63)
#define CCU_SPINLOCK_LOCK_MSK	(0x1UL)
#define CCU_SPINLOCK_LOCK_PUT(x) ((uint64_t)(x) << CCU_SPINLOCK_LOCK_SHF)
#define CCU_SPINLOCK_LOCK_GET(x) ((uint32_t)(((x) >> CCU_SPINLOCK_LOCK_SHF) & \
					     CCU_SPINLOCK_LOCK_MSK))

#define CCU_ID_HUT_SHF		(4)
#define CCU_ID_HUT_MSK		(0x1)
#define CCU_ID_HUT_PUT(x)	((x) << CCU_ID_HUT_SHF)
#define CCU_ID_HUT_GET(x)	(((x) >> CCU_ID_HUT_SHF) & CCU_ID_HUT_MSK)

#define CCU_ID_SLICE_SHF	(2)
#define CCU_ID_SLICE_MSK	(0x3)
#define CCU_ID_SLICE_PUT(x)	((x) << CCU_ID_SLICE_SHF)
#define CCU_ID_SLICE_GET(x)	(((x) >> CCU_ID_SLICE_SHF) & CCU_ID_SLICE_MSK)

#define CCU_ID_CID_SHF		(0)
#define CCU_ID_CID_MSK		(0x3)
#define CCU_ID_CID_PUT(x)	((x) << CCU_ID_CID_SHF)
#define CCU_ID_CID_GET(x)	(((x) >> CCU_ID_CID_SHF) & CCU_ID_CID_MSK)

/*
 * Convert bit-length into number of 64-bit units.
 */
#define SIZE64(x)	(((x) + 63) / 64)


#define  ERROR	0
#define  NOTICE 1
#define  INFO   2
#define  DEBUG  3
#define  TRACE  4

unsigned int dbglvl = NOTICE;

void LOG(unsigned int level, const char *format, ...)
{
	va_list args;

	if (level <= dbglvl) {
		va_start(args, format);
		vfprintf(stderr, format, args);
		va_end(args);
		fprintf(stderr, "\n");
	}
}


/*
 * Decode a CCU Indirect CSR Access Command.
 */
void
decode_ccucmd(uint64_t cmd, const char *description)
{
	LOG(INFO, "%s: type=%lld, size64=%lld, ring=%lld, init=%lld, crsv=%lld, tag=%lld, addr=%#llx",
	       description,
	       (cmd >> CCU_CMD_TYPE_SHF) & CCU_CMD_TYPE_MSK,
	       (cmd >> CCU_CMD_SIZE_SHF) & CCU_CMD_SIZE_MSK,
	       (cmd >> CCU_CMD_RING_SHF) & CCU_CMD_RING_MSK,
	       (cmd >> CCU_CMD_INIT_SHF) & CCU_CMD_INIT_MSK,
	       (cmd >> CCU_CMD_CRSV_SHF) & CCU_CMD_CRSV_MSK,
	       (cmd >> CCU_CMD_TAG_SHF) & CCU_CMD_TAG_MSK,
	       (cmd >> 0) & ((1ULL << 40) - 1));
}

/*
 * Dump relevant portions of the CCU.
 */
void
ccu_dump(ccu_info_t *ccu_info)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint32_t *ccu32 = (uint32_t *)ccu_info->mmap;
	unsigned int addr;

	/*
	 * The first portion of the mmap contains the CCU Command Register
	 * and CCU_DATA_REG_CNT Scratch Buffer Registers; all uint64_t.
	 */
	decode_ccucmd(be64_to_cpu(ccu64[CCU_CMD_REG]), "Cmd Decode");
	for (addr = CCU_CMD_REG; addr < CCU_DATA(CCU_DATA_REG_CNT); addr++)
		LOG(INFO, "%4d %#018lx", addr * (unsigned int)sizeof(*ccu64),
		       be64_to_cpu(ccu64[addr]));

	/*
	 * At the very end of the 4KB mmap() we find a couple of Spinlocks and
	 * an ID register.
	 */
	LOG(INFO, "%4d %#018lx", CCU_SPINLOCK0,
	       be64_to_cpu(ccu64[CCU_SPINLOCK0/sizeof(*ccu64)]));
	LOG(INFO, "%4d %#018lx", CCU_SPINLOCK1,
	       be64_to_cpu(ccu64[CCU_SPINLOCK1/sizeof(*ccu64)]));
	LOG(INFO, "%4d         %#010x",
	       CCU_ID, be32_to_cpu(ccu32[CCU_ID/sizeof(*ccu32)]));
}

/*
 * Dump out the result of a register read via the CCU.
 */
void
ccu_read_dump(ccu_info_t *ccu_info,
	      uint32_t size,
	      const char *name)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint32_t size64 = SIZE64(size);
	int reg_idx;

	LOG(INFO, "dumping CCU Read of %s", name);
	decode_ccucmd(be64_to_cpu(ccu64[CCU_CMD_REG]), "rsp");
	for (reg_idx = 0; reg_idx < size64; reg_idx++)
		   LOG(INFO, "%4d %#018lx",
			  reg_idx * (unsigned int)sizeof(*ccu64),
			  be64_to_cpu(ccu64[CCU_DATA(reg_idx)]));
}

/*
 * Return a pointer to the CCU Spinlock to use for this CCU mapping.
 */
uint64_t *
ccu_spinlock(ccu_info_t *ccu_info)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint64_t null_token = cpu_to_be64(CCU_SPINLOCK_ID_PUT(CCU_SPINLOCK_NULL_ID) |
					  CCU_SPINLOCK_LOCK_PUT(0));
	uint64_t *spinlock;

	/*
	 * Find a valid configured CCU Spinlock.
	 */
	spinlock = &ccu64[CCU_SPINLOCK0 / sizeof(*ccu64)];
	if (*spinlock == null_token) {
		LOG(NOTICE, "Using CCU Spinlock 0");
		return spinlock;
	}

	spinlock = &ccu64[CCU_SPINLOCK1 / sizeof(*ccu64)];
	if (*spinlock == null_token) {
		LOG(NOTICE, "Using CCU Spinlock 1");
		return spinlock;
	}

	/* no valid CCU Spinlock found */
	LOG(ERROR, "No valid configured CCU Spinlock found");
	return NULL;
}

/*
 * Use CCU Spinlock to prevent multiple clients from interfering with echo
 * others' register accesses.
 */
void
ccu_lock(ccu_info_t *ccu_info)
{
	if (ccu_info == NULL)
		return;

	do {
		*ccu_info->spinlock =
			cpu_to_be64(CCU_SPINLOCK_ID_PUT(ccu_info->spinlock_token) |
				    CCU_SPINLOCK_LOCK_PUT(1));
	} while (CCU_SPINLOCK_ID_GET(be64_to_cpu(*ccu_info->spinlock)) !=
		 ccu_info->spinlock_token);
}

void
ccu_unlock(ccu_info_t *ccu_info)
{
	if (ccu_info == NULL)
		return;

	*ccu_info->spinlock =
		cpu_to_be64(CCU_SPINLOCK_ID_PUT(CCU_SPINLOCK_NULL_ID) |
			    CCU_SPINLOCK_LOCK_PUT(0));
}

/*
 * Read a specified register into a provided buffer using the CCU to issue an
 * Indirect Register Read.
 */
void
csr_wide_read(ccu_info_t *ccu_info,
	      uint64_t addr,
	      uint64_t *data,
	      uint32_t size)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint64_t cmd, size64;
	uint32_t ring_sel;
	int reg_idx;

	size64 = SIZE64(size);
	ring_sel = ((addr >> CCU_RING_SHF) & CCU_RING_MSK);
	cmd = CCU_CMD(CCU_CMD_TYPE_RD_T, size64, ring_sel,
			CCU_CMD_INIT_DIS, data, addr);

	LOG(INFO, "Initiating CSR Read of addr=%#lx, size=%d", addr, size);
	decode_ccucmd(cmd, "cmd");

	/*
	 * Issue the CCU Read Command and then copy the CCU Data Buffer into
	 * the caller's buffer.
	 */
	ccu_lock(ccu_info);
	ccu64[CCU_CMD_REG] = cpu_to_be64(cmd);
	for (reg_idx = 0; reg_idx < size64; reg_idx++)
		data[reg_idx] = be64_to_cpu(ccu64[CCU_DATA(reg_idx)]);
	ccu_unlock(ccu_info);
}

/*
 * Read a specified register into a provided buffer.
 */
int
csr_read(ccu_info_t *ccu_info,
	 uint64_t base_addr,
	 uint64_t csr_addr,
	 uint64_t *data,
	 uint32_t size)
{
	uint64_t addr = base_addr + csr_addr;

	csr_wide_read(ccu_info, addr, data, size);
	return 0;
}

/*
 * Write a specified register from a provided buffer using the CCU to issue an
 * Indirect Register Write.
 */
void
csr_wide_write(ccu_info_t *ccu_info,
	       uint64_t addr,
	       uint64_t *data,
	       uint32_t size)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint64_t cmd, size64;
	uint32_t ring_sel;
	int reg_idx;

	size64 = SIZE64(size);
	ring_sel = ((addr >> CCU_RING_SHF) & CCU_RING_MSK);
	cmd = CCU_CMD(CCU_CMD_TYPE_WR_T, size64, ring_sel,
			CCU_CMD_INIT_DIS, data, addr);

	LOG(INFO, "Initiating CSR Write of addr=%#lx, size=%d", addr, size);
	decode_ccucmd(cmd, "cmd");

	/*
	 * Copy the caller's buffer into the CCU Data Buffer and then issue
	 * the CCU Write Command.
	 */
	ccu_lock(ccu_info);
	for (reg_idx = 0; reg_idx < size64; reg_idx++)
		ccu64[CCU_DATA(reg_idx)] = cpu_to_be64(data[reg_idx]);
	ccu64[CCU_CMD_REG] = cpu_to_be64(cmd);
	ccu_unlock(ccu_info);
}

/*
 * Write a specified register from a provided buffer.
 */
int
csr_write(ccu_info_t *ccu_info,
	  uint64_t base_addr,
	  uint64_t csr_addr,
	  uint64_t *data,
	  uint32_t size)
{
	uint64_t addr = base_addr + csr_addr;

	csr_wide_write(ccu_info, addr, data, size);
	return 0;
}


ccu_info_t *pcie_connect(const char *bar)
{

	ccu_info_t *ccu_info =
		(ccu_info_t *)malloc(sizeof(ccu_info_t));

	assert(bar);

	ccu_info->fd = open(bar, O_RDWR);
	if (ccu_info->fd < 0) {
		LOG(ERROR, "Can't open %s: %s", bar, strerror(errno));
		goto error;
	}
	ccu_info->mmap = mmap(NULL, CCU_SIZE,
			     PROT_READ|PROT_WRITE,
			     MAP_SHARED|MAP_LOCKED,
			     ccu_info->fd, 0);
	if (ccu_info->mmap == MAP_FAILED) {
		LOG(ERROR, "Can't mmap %s: %s", bar, strerror(errno));
		close(ccu_info->fd);
		ccu_info->fd = -1;
		ccu_info->mmap = NULL;
		goto error;
	}

	ccu_info->spinlock_token = getpid();
	ccu_info->spinlock = ccu_spinlock(ccu_info);
	if (!ccu_info->spinlock) {
		LOG(ERROR, "Failed to get spinlock!");
		goto error;
	}

	LOG(NOTICE, "PCIE CONNECTION SUCCESSFUL!");

	return ccu_info;

error:
	free(ccu_info);
	return NULL;
}

bool pcie_disconnect(ccu_info_t *ccu_info)
{
	if (ccu_info->mmap) {
		munmap(ccu_info->mmap, CCU_SIZE);
		close(ccu_info->fd);
	}
	free(ccu_info);
	LOG(NOTICE, "PCIE DISCONNECTED!");
}

bool pcie_csr_read(ccu_info_t *ccu_info, uint64_t csr_addr,
		   uint32_t csr_width_words, uint64_t *csr_buff)
{
	uint32_t csr_size = csr_width_words * 64;
	int vidx;

	assert(ccu_info);

	if (!ccu_info->mmap) {
		LOG(ERROR, "Not Connected!");
		return false;
	}

	assert(csr_addr);
	assert(csr_width_words);
	assert(csr_buff);

	if (csr_width_words == 0 || csr_width_words > CCU_DATA_REG_CNT) {
		LOG(ERROR, "Bad CSR Size %u", csr_size);
		return false;
	}

	csr_read(ccu_info, 0, csr_addr, csr_buff, csr_size);

	LOG(INFO, "OKAY READ");
	for (vidx = 0; vidx < csr_width_words; vidx++)
		LOG(INFO, " %#lx", csr_buff[vidx]);

	return true;
}

bool pcie_csr_write(ccu_info_t *ccu_info, uint64_t csr_addr,
		    uint32_t csr_width_words, uint64_t *csr_buff)
{
	uint32_t csr_size = csr_width_words * 64;
	int vidx;

	assert(ccu_info);

	if (!ccu_info->mmap) {
		LOG(ERROR, "Not Connected!");
		return false;
	}

	if (csr_width_words == 0 || csr_width_words > CCU_DATA_REG_CNT) {
		LOG(ERROR, "Bad CSR Size %u", csr_size);
		return false;
	}

	csr_write(ccu_info, 0, csr_addr, csr_buff, csr_size);

	return true;
}

bool freeze_vps_cmd(ccu_info_t *ccu_info)
{
	uint64_t data = 0x1ull << 63;
	bool status = false;

	status = pcie_csr_write(ccu_info, MIO_FATAL_INTR_BSET, 1, &data);

	return status;
}

bool hbm_read_aligned(ccu_info_t *ccu_info, uint64_t start_addr,
		uint32_t num_bytes, uint8_t *read_buf)
{
	bool status;
	uint64_t data[CCU_DATA_REG_CNT] = {0};

	assert(read_buf);
	assert(ccu_info);
	assert(num_bytes);

	if ((num_bytes & 0xFF) != 0) {
		LOG(ERROR, "num_bytes should be multiples of 256");
		return false;
	}

	if ((start_addr & 0xFF) != 0) {
		LOG(ERROR, "start_addr should be 256 byte aligned");
		return false;
	}

	uint64_t cache_line_addr = start_addr >> 6;
	uint32_t num_reads_256bytes = (num_bytes + 255) >> 8;
	uint32_t num_64bit_words = num_reads_256bytes * 32;
	uint32_t num_reads = num_reads_256bytes * 4;
	uint64_t *read_data_words =
		(uint64_t *)malloc(num_64bit_words * sizeof(uint64_t));

	LOG(INFO, "num_reads_256bytes: %u num_reads: %u num_words:%u",
	    num_reads_256bytes, num_reads, num_64bit_words);

	uint64_t cnt = 0;
	while (cnt < (uint64_t)num_reads) {
		uint64_t skip_addr = 0;
		if(cnt & 0x2ull)
			skip_addr = MUH_RING_SKIP_ADDR;
		if (cnt & 0x1ull)
			skip_addr += MUH_SNA_ANODE_SKIP_ADDR;

		uint64_t csr_addr = MEM_RW_CMD_CSR_ADDR;
		csr_addr += skip_addr;
		uint64_t muh_sna_cmd_addr = (cache_line_addr/4) + (cnt/4);
		uint64_t csr_val = muh_sna_cmd_addr << 37;
		csr_val |= 0x1ull << 63; //READ
		data[0] = csr_val;
		status = pcie_csr_write(ccu_info, csr_addr, 1, data);
		if (status == true) {
			LOG(INFO, "Poke:%"PRIu64 " addr: 0x%"PRIx64 " Success!",
			    cnt, muh_sna_cmd_addr);
		} else {
			LOG(ERROR, "CSR Poke failed! Addr: 0x%"PRIx64, csr_addr);
			return false;
		}

		csr_addr = MEM_RW_STATUS_CSR_ADDR;
		csr_addr += skip_addr;
		status = pcie_csr_read(ccu_info, csr_addr, 1, data);
		if (status == true) {
			uint64_t cmd_status_done = data[0];
			cmd_status_done = cmd_status_done >> 63;
			if (cmd_status_done != 1) {
				LOG(ERROR, "Failed cmd status != Done!");
				return false;
			} else {
				LOG(DEBUG, "Data ready!");
			}
		} else {
			LOG(ERROR, "Error! pcie_csr_read csr_addr: 0x%"PRIx64,
			    csr_addr);
			return false;
		}

		for(uint64_t i = 0; i < 8; i++) {
			csr_addr = MEM_RW_DATA_CSR_ADDR + skip_addr;
			csr_addr += i * 8;
			status = pcie_csr_read(ccu_info, csr_addr, 1, &data[i]);
			if (status == true) {
				LOG(DEBUG, "peek word: success!!!");
				LOG(DEBUG, "Read value:0x%"PRIx64, data[0]);
				read_data_words[(cnt * 8) + i] = data[i];
			} else {
				LOG(ERROR, "Error! reading word: %lu", i);
				return false;
			}
		}

		cnt += 1;
	}

	if (cnt == num_reads) {
		LOG(INFO, "Succesfully read %u words!", num_reads * 8);
		for(uint64_t i = 0; i < num_64bit_words; i++) {
			*(uint64_t *)(read_buf + (i * 8)) = htobe64(read_data_words[i]);
			LOG(INFO, "Address: 0x%"PRIx64 " Data: 0x%"PRIx64, (start_addr+(i*8)),
			    read_data_words[i]);
		}

	} else {
		LOG(ERROR, "Read un-successful");
		return false;
	}

	return true;
}

bool hbm_copy_to_file(ccu_info_t *ccu_info, uint64_t start_addr,
		uint64_t size, const char *file_path)
{
        uint64_t start_offset = start_addr & 0xff;
        uint64_t end_offset = (start_offset + size) & 0xFFull;
        end_offset = end_offset ? end_offset : 256;

        start_addr = start_addr & ~0xffull;
        uint64_t read_size = (size + start_offset + 255) & ~0xffull;
        uint64_t read_offset = 0;
	uint64_t wr_start = 0;
	uint64_t wr_end = 0;

	LOG(NOTICE, "Copying HBM data to file: %s"
	    " start_addr: 0x%"PRIx64 " size:0x%"PRIx64,
	    file_path, start_addr, size);

	LOG(INFO, "start_offset:0x%"PRIx64" end_offset:0x%"PRIx64
	    " read_size:0x%"PRIx64, start_offset, end_offset, read_size);

        FILE *f = fopen(file_path, "wb");
	if (f == NULL) {
		LOG(ERROR, "Failed to open file:%s for writing!", file_path);
		return false;
	}

	/* seek to the start address so readers see bytes relative to
	 * HBM base
	 */
	fseek(f, start_addr, SEEK_SET);

        while(read_offset < read_size) {
		uint8_t data[256] = {0};
		bool status = hbm_read_aligned(ccu_info,
				start_addr+read_offset, 256, data);
		if (!status) {
			LOG(ERROR, "Failed to read hbm!");
			fclose(f);
			return false;
		}
		if (read_offset < 256) {
			if (read_size <= 256) {
				wr_start = start_offset;
				wr_end = end_offset;
			} else {
				wr_start = start_offset;
				wr_end = 256;
			}
		} else if ((read_offset+256) >= read_size) {
			wr_start = 0;
			wr_end = end_offset;
		} else {
			wr_start = 0;
			wr_end = 256;
		}
		fwrite(&data[wr_start], 1, wr_end-wr_start , f);
		read_offset += 256;
	}
        fclose(f);

	return true;
}

bool hbm_dump(ccu_info_t *ccu_info, uint64_t start_addr, uint32_t size)
{
        start_addr = start_addr & ~0xffull;
        size = (size + 255) & ~0xffull;
	uint64_t read_offset = 0;

	LOG(NOTICE, "Aligned start_addr: 0x%"PRIx64
	    " size:0x%"PRIx64, start_addr, size);

        while(read_offset < size) {
		uint8_t data[256] = {0};
		bool status = hbm_read_aligned(ccu_info,
				start_addr+read_offset, 256, data);
		if (!status) {
			LOG(ERROR, "Failed to read hbm!");
			return false;
		}

		for (uint32_t i = 0; i < (256/8); i++) {
			printf("Address:0x%016"PRIx64" data:0x%016"PRIx64 "\n",
			       (start_addr + read_offset + (i*8)),
			       (uint64_t)be64toh(*(uint64_t *)(data + (i * 8))));
		}
		read_offset += 256;
	}

	return true;
}

void
usage(void)
{
	fprintf(stderr,
		"usage: %s [-d <debug level>] [-h] -a <start addr> -s <size> -b <bar> -f -o <file>\n"
		"    -h         help/this message\n"
		"    -d         debug level: 0-ERROR, 1-NOTICE, 2-INFO, 3-DEBUG, 4-TRACE\n"
		"    -a         hbm dump starting from address\n"
		"    -s         size of memory to be dumped\n"
		"    -b         pci bar info\n"
		"    -f         freeze vps\n"
		"    -o         output file name\n",
		myname);
}

int
main(int argc, char *const argv[])
{
	int opt;
	uint64_t addr = 0;
	uint64_t size = 0;
	const char *bar = NULL;
	const char *file = NULL;
	bool freeze_vps = false;

	/*
	 * Parse any command line arguments ...
	 */
	myname = strrchr(argv[0], '/');
	if (myname)
		myname++;
	else
		myname = argv[0];
	while ((opt = getopt(argc, argv, "hfd:a:s:b:o:")) != -1) {
		extern char *optarg;
		extern int optind;

		switch (opt) {
		case 'd':
			dbglvl = atoi(optarg);
			LOG(NOTICE, "dbglvl: %u", dbglvl);
			break;
		case 'a':
			addr = strtoull(optarg, NULL, 0);
			LOG(NOTICE, "start addr: 0x%"PRIx64, addr);
			break;

		case 's':
			size = strtoull(optarg, NULL, 0);
			LOG(NOTICE, "size: 0x%"PRIx64, size);
			break;

		case 'h':
			usage();
			exit(EXIT_SUCCESS);

		case 'f':
			freeze_vps = true;
			break;

		case 'b':
			bar = optarg;
			LOG(NOTICE, "bar: %s", bar);
			break;

		case 'o':
			file = optarg;
			LOG(NOTICE, "file: %s", file);
			break;

		default:
			usage();
			exit(EXIT_FAILURE);
			/*NOTREACHED*/
		}
	}

	if (!bar) {
		LOG(ERROR, "Invalid bar info(null)!");
		exit(EXIT_FAILURE);
	}

	if (addr >= HBM_SIZE_GB) {
		LOG(ERROR, "Invalid hbm start address:0x%"PRIx64
		    ". It should be less than 0x%"PRIx64 "!", addr, HBM_SIZE_GB);
		exit(EXIT_FAILURE);
	}

	if (addr + size > HBM_SIZE_GB) {
		LOG(ERROR, "Invalid size:0x%"PRIx64
		    ". Valid memory range: 0x0 - 0x%"PRIx64 "!",
		    size, HBM_SIZE_GB-1);
		exit(EXIT_FAILURE);
	}

	if (file) {
		struct stat sb;
		char dir[1024];
		char *dir_p = dir;

		strncpy(dir_p, file, sizeof(dir));
		dir_p = dirname(dir_p);
		if (stat(dir_p, &sb) == 0 && S_ISDIR(sb.st_mode)) {
			LOG(INFO, "File dir: %s file: %s", dir_p, file);
		} else {
			LOG(ERROR, "Directory: %s does not exist!", dir_p);
			exit(EXIT_FAILURE);
		}
	}

	ccu_info_t *ccu_info = pcie_connect(bar);
	if (!ccu_info) {
		LOG(ERROR, "Failed to connect to BAR!");
		exit(EXIT_FAILURE);
	}

	if (freeze_vps) {
		LOG(NOTICE, "Freezing all VPs!");
		if (!freeze_vps_cmd(ccu_info)) {
			LOG(ERROR, "Failed to send interrupt to freeze VPs!");
			goto end;
		}
	}

	if (file) {
		hbm_copy_to_file(ccu_info, addr, size, file);
	} else {
		hbm_dump(ccu_info, addr, size);
	}

end:
	pcie_disconnect(ccu_info);
	exit(EXIT_SUCCESS);
}
