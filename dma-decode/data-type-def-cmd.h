/*******************************************************************************
 * Field descriptions							       *
 ******************************************************************************/
/* OPC values */
static const struct val_2_desc_s opc_desc[] = {
	{0x00, "Gather"},
	{0x01, "Operate"},
	{0x02, "Scatter"},
	{0x03, "Complete"},
	{-1,   "Not found"}
};

/*******************************************************************************
 * Field tables								       *
 *******************************************************************************/
/* TGT IX table.
 * Jump into the TGT table.
 */
static const struct field_def_s tgt_ix[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"tgt",	   60,	2,	NULL,	    NULL,    NULL,	NULL,	g_tgt},
	{"tgt",	   60,	2,	NULL,	    NULL,    NULL,	NULL,	NULL},
	{"tgt",	   60,	2,	NULL,	    NULL,    NULL,	NULL,	s_tgt},
	{"tgt",	   60,	2,	NULL,	    NULL,    NULL,	NULL,	NULL},
	{NULL, 	   0,	0,	NULL,	    NULL,    NULL,	NULL,	NULL}
};

/* OPC table.
 * Print the OPC value
 * Index into the TGT IX table using the OPC value
 */
static const struct field_def_s dma_cmd[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed  jump */
	{"opc",	   62,	2,	opc_desc,   NULL,    NULL,	NULL,	NULL},
	{"opc",	   62,	2,	NULL,	    NULL,    NULL,	tgt_ix,	NULL},
	{NULL, 	   0,	0,	NULL,	    NULL,    NULL,	NULL,	NULL}
};
