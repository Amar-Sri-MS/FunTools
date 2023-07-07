/*******************************************************************************
 * Field descriptions							       *
 ******************************************************************************/
static const struct val_2_desc_s gids[] = {
	{0x00, "PC0"},
	{0x01, "PC1"},
	{0x02, "PC2"},
	{0x03, "PC3"},
	{0x04, "PC4"},
	{0x05, "PC5"},
	{0x06, "PC6"},
	{0x07, "PC7"},
	{0x08, "CC"},
	{0x09, "NU0"},
	{0x0a, "NU1"},
	{0x0b, "NU2"},
	{0x0c, "MC0"},
	{0x0d, "MC1"},
	{0x0e, "MC2"},
	{0x0f, "MC3"},
	{0x10, "HU0"},
	{0x11, "HU1"},
	{0x12, "HU2"},
	{0x13, "HU3"},
	{0x14, "HU4"},
	{0x15, "HU5"},
	{0x16, "DDD0"},
	{0x17, "DDD1"},
	{0x18, "SN bridge"},
	{0x19, "RESERVED_25"},
	{0x1a, "RESERVED_26"},
	{0x1b, "RESERVED_27"},
	{0x1c, "RESERVED_28"},
	{0x1d, "RESERVED_29"},
	{0x1e, "RESERVED_30"},
	{0x1f, "UNKNOWN"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s lids[] = {
	{0x00, "Coherent Memory Adapter (CA)"},
	{0x01, "Uncached Memory Adapter (UA)"},
	{0x02, "Buffer Memory Manager (BAM)"},
	{0x03, "DMA Engine (DMA)"},
	{0x04, "RGX for PC, EQM for CC"},
	{0x05, "LE for PC, AMH for CC"},
	{0x06, "ZIP"},
	{0x07, "Work Queue Manager"},
	{0x08, "Core0 VP0"},
	{0x09, "Core0 VP1"},
	{0x0a, "Core0 VP2"},
	{0x0b, "Core0 VP3"},
	{0x0c, "Core1 VP0"},
	{0x0d, "Core1 VP1"},
	{0x0e, "Core1 VP2"},
	{0x0f, "Core1 VP3"},
	{0x10, "Core2 VP0"},
	{0x11, "Core2 VP1"},
	{0x12, "Core2 VP2"},
	{0x13, "Core2 VP3"},
	{0x14, "Core3 VP0"},
	{0x15, "Core3 VP1"},
	{0x16, "Core3 VP2"},
	{0x17, "Core3 VP3"},
	{0x18, "Core4 VP0"},
	{0x19, "Core4 VP1"},
	{0x1a, "Core4 VP2"},
	{0x1b, "Core4 VP3"},
	{0x1c, "Core5 VP0"},
	{0x1d, "Core5 VP1"},
	{0x1e, "Core5 VP2"},
	{0x1f, "Core5 VP3"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s tqs[] = {
	{-1,   "TODO"}
};

static const struct val_2_desc_s rsvd[] = {
	{0x00, "RESERVED"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s bit_24[] = {
	{0x00, "TODO"},
	{0x01, "TODO"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s t_bit[] = {
	{0x00, "TODO"},
	{0x01, "TODO"},
	{-1,   "Not found"}
};

/*******************************************************************************
 * Sub-field sn-header							       *
 ******************************************************************************/
static const struct val_2_desc_s types[] = {
	{0x00, "Block read request"},
	{0x01, "Block read forward"},
	{0x02, "Block write reply"},
	{0x03, "Block write request"},
	{0x04, "BM allocate request"},
	{0x05, "BM allocate response"},
	{0x06, "Buffer free request"},
	{0x07, "RSVD_7"},
	{0x08, "DRAM allocator index update request"},
	{0x09, "WQM memory credit/index request"},
	{0x0a, "WQM memory credit allocate response"},
	{0x0b, "Uncached read request"},
	{0x0c, "Uncached read reply"},
	{0x0d, "EQM event memory allocate request"},
	{0x0e, "Event request"},
	{0x0f, "Event response"},
	{0x10, "32B WU"},
	{0x11, "Work unit non-credit (ex. timer)"},
	{0x12, "RSVD_18"},
	{0x13, "RSVD_19"},
	{0x14, "RSVD_20"},
	{0x15, "Buffer allocate response multiple"},
	{0x16, "Uncached read response"},
	{0x17, "Uncached read request"},
	{0x18, "DRAM allocator index update request 32B"},
	{0x19, "DRAM allocator index update response"},
	{0x1a, "WQM WU memory index allocate response"},
	{0x1b, "WQM WU memory index free request"},
	{0x1c, "EQM event memory page free request"},
	{0x1d, "EQM event memory page allocate response"},
	{0x1e, "64B WU"},
	{0x1f, "INVALID"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s orders[] = {
	{0x00, "Relaxed"},
	{0x01, "Strict"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s vcs[] = {
	{0x00, "Request"},
	{0x01, "Response"},
	{0x02, "WU-Low"},
	{0x03, "WU-High"},
	{-1,   "Not found"}
};

static const struct field_def_s sn_header[] = {
      /* name    shift width val_2_desc calc    sub-fields  indexed    jump */
	{"type",   3,	5,	types,	NULL,	NULL,	    NULL,	NULL},
	{"order",  2,	1,	orders,	NULL,	NULL,	    NULL,	NULL},
	{"vc",	   0,	2,	vcs,	NULL,	NULL,	    NULL,	NULL},
	{NULL, 	   0,	0,	NULL,	NULL,	NULL,	    NULL,	NULL}
};

/*******************************************************************************
 * Field tables								       *
 ******************************************************************************/
static const struct field_def_s src[] = {
      /* name   shift width  val_2_desc calc    sub-fields  indexed    jump */
	{"gid",   5,	5,	gids,	NULL,	NULL,	    NULL,	NULL},
	{"lid",	  0,	5,	lids,	NULL,	NULL,	    NULL,	NULL},
	{NULL, 	  0,	0,	NULL,	NULL,	NULL,	    NULL,	NULL}
};

static const struct field_def_s dst[] = {
      /* name    shift width val_2_desc calc    sub-fields  indexed    jump */
	{"gid",	   15,	5,	gids,	NULL,	NULL,	    NULL,	NULL},
	{"lid",	   10,	5,	lids,	NULL,	NULL,	    NULL,	NULL},
	{"tq",	   2,	8,	tqs,	NULL,	NULL,	    NULL,	NULL},
	{"rsvd",   0,	2,	rsvd,	NULL,	NULL,	    NULL,	NULL},
	{NULL, 	   0,	0,	NULL,	NULL,	NULL,	    NULL,	NULL}
};

/* Definition of the DMA WU action field */
static const struct field_def_s action[] = {
     /* name          shift   width  val_2_desc calc    sub-fields  indexed    jump */
	{"sn_header",	56,	8,	NULL,	NULL,	sn_header,  NULL,	NULL},
	{"src",		46,	10,	NULL,	NULL,	src,	    NULL,	NULL},
	{"dst",		26,	20,	NULL,	NULL,	dst,	    NULL,	NULL},
	{"t-bit",	25,	1,	t_bit,	NULL,	NULL,	    NULL,	NULL},
	{"bit-24",	24,	1,	bit_24,	NULL,	NULL,	    NULL,	NULL},
	{"wuid",	0,	24,	NULL,	NULL,	NULL,	    NULL,	NULL},
	{NULL, 		0,	0,	NULL,	NULL,	NULL,	    NULL,	NULL}
};
