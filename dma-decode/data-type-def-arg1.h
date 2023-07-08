/*******************************************************************************
 * Field descriptions							       *
 ******************************************************************************/
static const struct val_2_desc_s o_opc_desc[] = {
	{0x01, "Operate"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s o_pipe_desc[] = {
	{0x00, "Thread 0 - AES"},
	{0x01, "Thread 1 - AES"},
	{0x02, "Thread 2 - AES"},
	{0x03, "Thread 3 - AES"},
	{0x04, "Thread 4 - SHA"},
	{0x05, "Thread 5 - SHA"},
	{0x06, "Thread 6 - SHA"},
	{0x07, "Thread 7 - SHA"},
	{0x08, "Thread 8 - SHA"},
	{0x09, "Thread 9 - SHA"},
	{0x0a, "Thread 10 - EC"},
	{0x0b, "Thread 11 - CRC (F1 only)"},
	{0x0c, "Thread 12 - CRC"},
	{0x0d, "Thread 13 - CRC"},
	{-1,   "Not found"}
};

/*******************************************************************************
 * Sub-field CRC flags							       *
 ******************************************************************************/
static const struct val_2_desc_s o_crc_f_r0[] = {
	{0x00, "R bit is not set TODO"},
	{0x01, "R bit is set TODO"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s o_crc_f_p[] = {
	{0x00, "Present not set"},
	{0x01, "Present is set"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s o_crc_f_s[] = {
	{0x00, "Seed use default"},
	{0x01, "Seed use provided"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s o_crc_f_r1[] = {
	{0x00, "R bit is not set TODO"},
	{0x01, "R bit is set TODO"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s o_crc_f_c[] = {
	{0x00, "Check/copy not set"},
	{0x01, "Check/copy set"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s o_crc_f_type[] = {
	{0x00, "Copy"},
	{0x01, "TCP/IP"},
	{0x02, "UDP/IP"},
	{0x04, "CRC32"},
	{0x05, "CRC32C"},
	{0x06, "CRC16"},
	{0x07, "CRC64"},
	{-1,   "Not found"}
};

static const struct field_def_s o_crc_flags[] = {
      /* name         shift   width   val_2_desc      calc  sub-fields indexed  jump */
	{"r-bit",	7,	1,	o_crc_f_r0,   NULL,    NULL,	NULL,	NULL},
	{"p-bit",	6,	1,	o_crc_f_p,    NULL,    NULL,	NULL,	NULL},
	{"s-bit",	5,	1,	o_crc_f_s,    NULL,    NULL,	NULL,	NULL},
	{"r-bit",	4,	1,	o_crc_f_r1,   NULL,    NULL,	NULL,	NULL},
	{"c-bit",	3,	1,	o_crc_f_c,    NULL,    NULL,	NULL,	NULL},
	{"type",	0,	3,	o_crc_f_type, NULL,    NULL,	NULL,	NULL},
	{NULL, 		0,	0,	NULL,	      NULL,    NULL,	NULL,	NULL}
};

/*******************************************************************************
 * Flags tables								       *
 ******************************************************************************/
/* Flags table for pipe==undefined or not coded yet
 * Print TODO
 */
static const struct field_def_s o_null_flags[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed  jump */
	{"TODO",      0,     56,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	  NULL,   NULL}
};

/* Flags table for pipe==CRC
 * Print the rest of the CRC fields.
 */
static const struct field_def_s o_crc[] = {
     /* name           shift  width val_2_desc  calc          sub-fields      indexed  jump */
	{"flags",	 48,	8,    NULL,	NULL,		o_crc_flags,	NULL,	NULL},
	{"length",	 32,	16,   NULL,	o_crc_l_calc,	NULL,		NULL,	NULL},
	{"start-offset", 16,	16,   NULL,	o_crc_so_calc,	NULL,		NULL,	NULL},
	{"stop-offset",	 0,	16,   NULL,	o_crc_sto_calc,	NULL,		NULL,	NULL},
	{NULL,		 0,	0,    NULL,	NULL,		NULL,		NULL,	NULL}
};

/* Flags IX table.
 * Jump into the flag table.
 */
static const struct field_def_s o_flag_ix[] = {
     /* name     shift width  val_2_desc   calc   sub-fields  indexed  jump */
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_crc},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_crc},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_crc},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags},
	{"flags",  0,	0,	NULL,	   NULL,    NULL,	NULL,	o_null_flags}
};

/*******************************************************************************
 * Field tables								       *
 *******************************************************************************/
/* Definition of the DMA WU arg1 field.
 * Print the Pipe value.
 * Index into the FLAGS IX table using the pipe value.
 */
const struct field_def_s dma_wu_arg1[] = {
     /* name     shift width  val_2_desc     calc  sub-fields   indexed   jump */
	{"opc",	   62,	2,	o_opc_desc,  NULL,    NULL,	NULL,	   NULL},
	{"pipe",   56,	6,	o_pipe_desc, NULL,    NULL,	NULL,      NULL},
	{"pipe",   56,	6,	NULL,	     NULL,    NULL,	o_flag_ix, NULL},
	{NULL, 	   0,	0,	NULL,	     NULL,    NULL,	NULL,	   NULL}
};
