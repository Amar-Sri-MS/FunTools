/*******************************************************************************
 * Sub-field flags							       *
 ******************************************************************************/
static const struct val_2_desc_s ow[] = {
	{0x0, "Ordered write not set"},
	{0x1, "Ordered write set"},
	{-1,  "Not found"}
};

static const struct val_2_desc_s or[] = {
	{0x0, "Ordered read not set"},
	{0x1, "Ordered read set"},
	{-1,  "Not found"}
};

static const struct val_2_desc_s ins[] = {
	{0x0, "Cmd list in coherent memory (CM)"},
	{0x1, "Cmd list in buffer memory (BM)"},
	{0x2, "Cmd list in HBM"},
	{0x3, "Cmd list in DDR"},
	{-1,  "Not found"}
};

static const struct val_2_desc_s f_bit[] = {
	{0x0, "Don't set BM_RD_REQ"},
	{0x1, "Set BM_RD_REQ after last cmd list read"},
	{-1,  "Not found"}
};

static const struct val_2_desc_s r_bit[] = {
	{0x0, "Relaxed ordering not set "},
	{0x1, "Relaxed ordering set "},
	{-1,  "Not found"}
};

static const struct val_2_desc_s s_bit[] = {
	{0x0, "Strict ordering not set "},
	{0x1, "Strict ordering set "},
	{-1,  "Not found"}
};

static const struct val_2_desc_s c_bit[] = {
	{0x0, "CWU not on cmd list"},
	{0x1, "CWU at start of cmd list"},
	{-1,  "Not found"}
};

static const struct field_def_s dma_a0_f[] = {
      /* name    shift width val_2_desc calc    sub-fields  indexed    jump */
	{"ow",	   7,	1,	ow,	NULL,	NULL,	    NULL,	NULL},
	{"or",	   6,	1,	or,	NULL,	NULL,	    NULL,	NULL},
	{"ins",	   4,	2,	ins,	NULL,	NULL,	    NULL,	NULL},
	{"f-bit",  3,	1,	f_bit,	NULL,	NULL,	    NULL,	NULL},
	{"r-bit",  2,	1,	r_bit,	NULL,	NULL,	    NULL,	NULL},
	{"s-bit",  1,	1,	s_bit,	NULL,	NULL,	    NULL,	NULL},
	{"c-bit",  0,	1,	c_bit,	NULL,	NULL,	    NULL,	NULL},
	{NULL, 	   0,	0,	NULL,	NULL,	NULL,	    NULL,	NULL}
};

/*******************************************************************************
 * Field tables								       *
 ******************************************************************************/
/* Definition of the DMA WU arg0 field */
static const struct field_def_s dma_wu_arg0[] = {
     /* name             shift width val_2_desc calc            sub-fields  indexed    jump */
	{"flags",	   56,	8,	NULL,	NULL,		dma_a0_f,   NULL,	NULL},
	{"cmd_list_size",  48,	8,	NULL,	cmdls_calc,	NULL, 	    NULL,	NULL},
	{"cmd_list_ptr",   0,	48,	NULL,	cmdlp_calc,	NULL, 	    NULL,	NULL},
	{NULL, 		   0,	0,	NULL,	NULL,		NULL,	    NULL,	NULL}
};
