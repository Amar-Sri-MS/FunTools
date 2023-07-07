/*******************************************************************************
 * Sub-field info							       *
 ******************************************************************************/
static const struct val_2_desc_s i_ns_desc[] = {
	{0x00, "No Snoop disabled"},
	{0x01, "No Snoop enabled"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s i_ro_desc[] = {
	{0x00, "Relaxed ordering disabled"},
	{0x01, "Relaxed ordering enabled"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s i_at_desc[] = {
	{0x00, "Untranslated"},
	{0x01, "Translated"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s i_pa_desc[] = {
	{0x00, "PASID prefix doesn't exist"},
	{0x01, "PASID prefix exists"},
	{-1,   "Not found"}
};

/* PCIe ST==0 TH==0 table.
 * Print the INFO fieds when ST==0 and TH==0.
 */
static const struct field_def_s pci_i_st0_th0[] = {
      /* name           shift  width  val_2_desc    calc         sub-fields  indexed  jump */
	{"max rd sz",	  29,	 3,	NULL,	    i_m_rd_sz_calc,  NULL,     NULL,   NULL},
	{"max pld",	  27,	 2,	NULL,	    i_m_pld_calc,    NULL,     NULL,   NULL},
	{"R",		  26,	 1,	NULL,	    NULL,	     NULL,     NULL,   NULL},
	{"NS",		  25,	 1,	i_ns_desc,  NULL,	     NULL,     NULL,   NULL},
	{"RO",		  24,	 1,	i_ro_desc,  NULL,	     NULL,     NULL,   NULL},
	{"AT",		  23,	 1,	i_at_desc,  NULL,	     NULL,     NULL,   NULL},
	{"PH",		  21,	 2,	NULL,	    NULL,	     NULL,     NULL,   NULL},
	{"TH",		  20,	 1,	NULL,	    NULL,	     NULL,     NULL,   NULL},
	{"RSVD",	  15,	 5,	NULL,	    NULL,	     NULL,     NULL,   NULL},
	{"steer tag ix",  4,	 11,	NULL,	    i_ignore_calc,   NULL,     NULL,   NULL},
	{"ST",		  3,	 1,	NULL,	    i_ignore_calc,   NULL,     NULL,   NULL},
	{"ST CTR",	  1,	 2,	NULL,	    i_ignore_calc,   NULL,     NULL,   NULL},
	{"PA",		  0,	 1,	i_pa_desc,  NULL,	     NULL,     NULL,   NULL},
	{NULL,		  0,	 0,	NULL,	    NULL,	     NULL,     NULL,   NULL}
};

/* PCIe ST==0 TH==1 table.
 * Print the INFO fieds when ST==0 and TH==1.
 */
static const struct field_def_s pci_i_st0_th1[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed    jump */
	{"TODO",   16,	 40,	NULL,	   NULL,   NULL,    NULL,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,	NULL}
};

/* PCIe ST==1 TH==0 table.
 * Print the INFO fieds when ST==1 and TH==0.
 */
static const struct field_def_s pci_i_st1_th0[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed    jump */
	{"TODO",   16,	 40,	NULL,	   NULL,   NULL,    NULL,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,	NULL}
};

/* PCIe ST==1 TH==1 table.
 * Print the INFO fieds when ST==1 and TH==1.
 */
static const struct field_def_s pci_i_st1_th1[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed    jump */
	{"TODO",   16,	 40,	NULL,	   NULL,   NULL,    NULL,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,	NULL}
};

/* PCIe ST==0 TH IX table.
 * Jump into the INFO table for ST==0 and the TH value.
 */
static const struct field_def_s pci_i_st0_th_ix[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed            jump */
	{"th",	   36,	 1,	NULL,	   NULL,   NULL,    pci_i_st0_th0,	NULL},
	{"th",	   36,	 1,	NULL,	   NULL,   NULL,    pci_i_st0_th1,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,		NULL}
};

/* PCIe ST==1 TH IX table.
 * Jump into the INFO table for ST==1 and the TH value.
 */
static const struct field_def_s pci_i_st1_th_ix[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed            jump */
	{"th",	   36,	 1,	NULL,	   NULL,   NULL,    pci_i_st1_th0,	NULL},
	{"th",	   36,	 1,	NULL,	   NULL,   NULL,    pci_i_st1_th1,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,		NULL}
};

/* PCIe ST==0 IX table.
 * Jump into the INFO table for the TH value.
 */
static const struct field_def_s pci_i_st0[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed            jump */
	{"th",	   36,	 1,	NULL,	   NULL,   NULL,    pci_i_st0_th_ix,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,		NULL}
};

/* PCIe ST==1 IX table.
 * Jump into the INFO table for the TH value.
 */
static const struct field_def_s pci_i_st1[] = {
      /* name    shift width   val_2_desc  calc sub-fields  indexed            jump */
	{"th",	   36,	 1,	NULL,	   NULL,   NULL,    pci_i_st1_th_ix,	NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,		NULL}
};

/* PCIe INFO IX table.
 * Jump into the INFO table for the ST value.
 */
static const struct field_def_s pci_info_ix[] = {
      /* name    shift width   val_2_desc  calc sub-fields indexed    jump */
	{"st",	   19,	 1,	NULL,	   NULL,   NULL,    NULL,    pci_i_st0},
	{"st",	   19,	 1,	NULL,	   NULL,   NULL,    NULL,    pci_i_st1},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,    NULL}
};

/* PCIe info
 * Index into the PCI info table using the ST value.
 */
static const struct field_def_s pci_info[] = {
      /* name    shift width   val_2_desc  calc sub-fields indexed          jump */
	{"st",	   19,	 1,	NULL,	   NULL,   NULL,    pci_info_ix,     NULL},
	{NULL, 	   0,	 0,	NULL,	   NULL,   NULL,    NULL,	     NULL}
};
