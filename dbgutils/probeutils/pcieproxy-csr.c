#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#include <FunOS/hw/csr/ccu.h>
#include "pcieproxy.h"
#include "endian.h"

/*
 * Decode a CCU Indirect CSR Access Command.
 */
static void
decode_ccucmd(uint64_t cmd, const char *description)
{
	printf("%s: type=%lld, size64=%lld, ring=%lld, init=%lld, crsv=%lld, tag=%lld, addr=%#llx\n",
	       description,
	       (cmd >> CCU_CMD_TYPE_SHF) & CCU_CMD_TYPE_MSK,
	       (cmd >> CCU_CMD_SIZE_SHF) & CCU_CMD_SIZE_MSK,
	       (cmd >> CCU_CMD_RING_SHF) & CCU_CMD_RING_MSK,
#ifndef CONFIG_CSR_VERSION_2
	       (cmd >> CCU_CMD_INIT_SHF) & CCU_CMD_INIT_MSK,
	       (cmd >> CCU_CMD_CRSV_SHF) & CCU_CMD_CRSV_MSK,
	       (cmd >> CCU_CMD_TAG_SHF) & CCU_CMD_TAG_MSK,
#else
	       0LL, 0LL, 0LL,  /* these fields are not valid for CSRv2 */
#endif
	       (cmd >> CCU_CMD_ADDR_SHF) & CCU_CMD_ADDR_MSK);
}

/*
 * Dump relevant portions of the CCU.
 */
static void
ccu_dump(struct ccu_info_t *ccu_info)
{
	uint64_t *ccu64 = (uint64_t *)ccu_info->mmap;
	uint32_t *ccu32 = (uint32_t *)ccu_info->mmap;
	unsigned int addr;

	/*
	 * The first portion of the mmap contains the CCU Command Register
	 * and CCU_DATA_REG_CNT Scratch Buffer Registers; all uint64_t.
	 */
	decode_ccucmd(be64toh(ccu64[CCU_CMD_REG]), "Cmd Decode");
	for (addr = CCU_DATA(0); addr < CCU_DATA(CCU_DATA_REG_CNT); addr++)
		printf("%4d %#018lx\n",
		       addr * (unsigned int)sizeof(*ccu64),
		       be64toh(ccu64[addr]));

	/*
	 * At the very end of the 4KB mmap() we find a couple of Spinlocks and
	 * an ID register.
	 */
	printf("%4d %#018lx\n",
	       CCU_SPINLOCK0,
	       be64toh(ccu64[CCU_SPINLOCK0/sizeof(*ccu64)]));
	printf("%4d %#018lx\n",
	       CCU_SPINLOCK1,
	       be64toh(ccu64[CCU_SPINLOCK1/sizeof(*ccu64)]));
	printf("%4d         %#010x\n",
	       CCU_ID,
	       be32toh(ccu32[CCU_ID/sizeof(*ccu32)]));
}

/*
 * Read a specified register into a provided buffer using the CCU to issue an
 * Indirect Register Read.
 */
static void
csr_wide_read(struct ccu_info_t *ccu_info,
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

	if (debug) {
		fprintf(stderr, "Initiating CSR Read of addr=%#lx, size=%d\n",
			addr, size);
		decode_ccucmd(cmd, "cmd");
	}

	/*
	 * Issue the CCU Read Command and then copy the CCU Data Buffer into
	 * the caller's buffer.
	 */
	ccu_lock(ccu_info);
	ccu64[CCU_CMD_REG] = htobe64(cmd);
	for (reg_idx = 0; reg_idx < size64; reg_idx++)
		data[reg_idx] = be64toh(ccu64[CCU_DATA(reg_idx)]);
	ccu_unlock(ccu_info);
}

/*
 * Write a specified register from a provided buffer using the CCU to issue an
 * Indirect Register Write.
 */
static void
csr_wide_write(struct ccu_info_t *ccu_info,
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

	if (debug) {
		fprintf(stderr, "Initiating CSR Write of addr=%#lx, size=%d\n",
			addr, size);
			decode_ccucmd(cmd, "cmd");
	}

	/*
	 * Copy the caller's buffer into the CCU Data Buffer and then issue
	 * the CCU Write Command.
	 */
	ccu_lock(ccu_info);
	for (reg_idx = 0; reg_idx < size64; reg_idx++)
		ccu64[CCU_DATA(reg_idx)] = htobe64(data[reg_idx]);
	ccu64[CCU_CMD_REG] = htobe64(cmd);
	ccu_unlock(ccu_info);
}

#ifdef CONFIG_CSR_VERSION_2
#define CCU_OPS_NAME csr2_ops
#else
#define CCU_OPS_NAME csr1_ops
#endif

struct ccu_ops CCU_OPS_NAME = {
	.csr_wide_write = csr_wide_write,
	.csr_wide_read = csr_wide_read,
	.ccu_dump = ccu_dump,
	.decode_ccucmd = decode_ccucmd,
};
