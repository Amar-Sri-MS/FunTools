/*
 * The PCIe Remote Access mapping in the End Point MMU is 4KB.  All of this
 * should really be in a FunHW or FunOS include file ...
 */
#define CCU_MAP_SIZE		4096

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
/*
 * Decoding the CCU ID register ...
 */
#define CCU_ID_CSRTYPE_SHF	(31)
#define CCU_ID_CSRTYPE_MSK	(0x1)
#define CCU_ID_CSRTYPE_PUT(x)	((x) << CCU_ID_CSRTYPE_SHF)
#define CCU_ID_CSRTYPE_GET(x)	(((x) >> CCU_ID_CSRTYPE_SHF) & CCU_ID_CSRTYPE_MSK)

#define CCU_ID_CHIPID_SHF	(23)
#define CCU_ID_CHIPID_MSK	(0xff)
#define CCU_ID_CHIPID_PUT(x)	((x) << CCU_ID_CHIPID_SHF)
#define CCU_ID_CHIPID_GET(x)	(((x) >> CCU_ID_CHIPID_SHF) & CCU_ID_CHIPID_MSK)

#define CCU_ID_HUT_SHF		(20)
#define CCU_ID_HUT_MSK		(0x1)
#define CCU_ID_HUT_PUT(x)	((x) << CCU_ID_HUT_SHF)
#define CCU_ID_HUT_GET(x)	(((x) >> CCU_ID_HUT_SHF) & CCU_ID_HUT_MSK)

#define CCU_ID_SLICE_SHF	(18)
#define CCU_ID_SLICE_MSK	(0x3)
#define CCU_ID_SLICE_PUT(x)	((x) << CCU_ID_SLICE_SHF)
#define CCU_ID_SLICE_GET(x)	(((x) >> CCU_ID_SLICE_SHF) & CCU_ID_SLICE_MSK)

#define CCU_ID_CID_SHF		(16)
#define CCU_ID_CID_MSK		(0x3)
#define CCU_ID_CID_PUT(x)	((x) << CCU_ID_CID_SHF)
#define CCU_ID_CID_GET(x)	(((x) >> CCU_ID_CID_SHF) & CCU_ID_CID_MSK)

/*
 * Convert bit-length into number of 64-bit units.
 */
#define SIZE64(x)	(((x) + 63) / 64)


/*
 * Client Global Variables and Types.
 */
typedef struct {
	int		fd;
	void		*mmap;
	pid_t		spinlock_token;
	uint64_t	*spinlock;
} ccu_info_t;

extern int debug;

/*
 * =================
 * Endian utilities.
 * =================
 */

/*
 * Swap the endianess of a 64-bit (8-byte) argument and return the result.
 */
static inline uint64_t
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
static inline uint32_t
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
static inline swab16(uint16_t u16)
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

void ccu_lock(ccu_info_t *ccu_info);
void ccu_unlock(ccu_info_t *ccu_info);

struct ccu_ops {
	void (*csr_wide_write)(ccu_info_t *ccu_info,
			uint64_t addr,
			uint64_t *data,
			uint32_t size);
	void (*csr_wide_read)(ccu_info_t *ccu_info,
			uint64_t addr,
			uint64_t *data,
			uint32_t size);
	void (*ccu_dump)(ccu_info_t *ccu_info);
	void (*decode_ccucmd)(uint64_t cmd, const char *description);
};

extern struct ccu_ops csr1_ops;
extern struct ccu_ops csr2_ops;
