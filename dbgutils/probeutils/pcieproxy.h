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
