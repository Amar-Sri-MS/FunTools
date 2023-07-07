/*******************************************************************************
 * Field descriptions							       *
 ******************************************************************************/
/* TGT when OPC==GATHER */
static const struct val_2_desc_s g_tgt_desc[] = {
	{0x00, "DPU memory"},
	{0x01, "PCIe"},
	{0x02, "Immediate"},
	{0x03, "Generate"},
	{-1,   "Not found"}
};

/* INS when TGT==DPU memory */
static const struct val_2_desc_s g_d_ins_desc[] = {
	{0x00, "Coherent memory"},
	{0x01, "BM"},
	{0x02, "HBM (F1), OCM (S1)"},
	{0x03, "DDR"},
	{-1,   "Not found"}
};

/* INS when TGT==PCIe */
static const struct val_2_desc_s g_p_ins_desc[] = {
	{0x00, "Wire (Remote PCIe memory)"},
	{0x01, "RMMU, LOCAL (S2)"},
	{0x02, "RSVD"},
	{0x03, "RSVD"},
	{-1,   "Not found"}
};

/* INS when TGT==IMMEDIATE */
static const struct val_2_desc_s g_i_ins_desc[] = {
	{0x00, "RSVD, Normal (S2)"},
	{0x01, "RSVD, CNTR (S2)"},
	{0x02, "RSVD"},
	{0x03, "RSVD, NULL (S2)"},
	{-1,   "Not found"}
};

/* TYPE when TGT==DPU memory && TGT==PCIe*/
static const struct val_2_desc_s g_def_type_desc[] = {
	{0x00, "Normal (Single Address)"},
	{0x01, "Stride (Not supported by HUDMA and NUDMA)"},
	{0x02, "Normal+EOP (Single Address + EOP)"},
	{0x03, "Stride+EOP (Not supported by HUDMA and NUDMA)"},
	{-1,   "Not found"}
};

/* TYPE when TGT==IMMEDIATE */
static const struct val_2_desc_s g_i_type_desc[] = {
	{0x00, "Data"},
	{0x01, "Meta"},
	{0x02, "Data+EOP"},
	{0x03, "RSVD"},
	{-1,   "Not found"}
};

/* TYPE when TGT==GENERATED */
static const struct val_2_desc_s g_g_type_desc[] = {
	{0x00, "Data"},
	{0x01, "RSVD"},
	{0x02, "RSVD, Data+EOP (S2)"},
	{0x03, "Data+EOP, RSVD (S2)"},
	{-1,   "Not found"}
};

/*******************************************************************************
 * Sub-field BM-flags							       *
 ******************************************************************************/
static const struct val_2_desc_s g_bm_s_bit[] = {
	{0x00, "Status success"},
	{0x01, "Status fail"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_b_bit[] = {
	{0x00, "No Barrier"},
	{0x01, "Barrier"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_p_bit[] = {
	{0x00, "Not Partial"},
	{0x01, "Partial"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_l_bit[] = {
	{0x00, "Not Last"},
	{0x01, "Last"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_i_bit[] = {
	{0x00, "No ID"},
	{0x01, "ID"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_m_bit[] = {
	{0x00, "No Multiple"},
	{0x01, "Multiple"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_f_bit[] = {
	{0x00, "Don't free"},
	{0x01, "Free after read"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s g_bm_x_bit[] = {
	{0x00, "Not Expandable"},
	{0x01, "Expandable"},
	{-1,   "Not found"}
};

/* BM flags */
static const struct field_def_s g_bm_flags[] = {
      /* name    shift width   val_2_desc    calc sub-fields indexed    jump */
	{"S-bit",  7,	 1,	g_bm_s_bit,  NULL,   NULL,    NULL,	NULL},
	{"B-bit",  6,	 1,	g_bm_b_bit,  NULL,   NULL,    NULL,	NULL},
	{"P-bit",  5,	 1,	g_bm_p_bit,  NULL,   NULL,    NULL,	NULL},
	{"L-bit",  4,	 1,	g_bm_l_bit,  NULL,   NULL,    NULL,	NULL},
	{"I-bit",  3,	 1,	g_bm_i_bit,  NULL,   NULL,    NULL,	NULL},
	{"M-bit",  2,	 1,	g_bm_m_bit,  NULL,   NULL,    NULL,	NULL},
	{"F-bit",  1,	 1,	g_bm_f_bit,  NULL,   NULL,    NULL,	NULL},
	{"X-bit",  0,	 1,	g_bm_x_bit,  NULL,   NULL,    NULL,	NULL},
	{NULL, 	   0,	 0,	NULL,	     NULL,   NULL,    NULL,	NULL}
};

/*******************************************************************************
 * TYPE tables (plus the rest of the fields)				       *
 ******************************************************************************/
/* TYPE table when TGT==DPU memory
 * Print the TYPE value.
 * Print the rest of the fields
 */
static const struct field_def_s g_dpu_type[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields   indexed  jump */
	{"type",      56,    2,	   g_def_type_desc, NULL,	NULL,	    NULL,   NULL},
	{"rsvd",      24,    32,   NULL,	    NULL,	NULL,	    NULL,   NULL},
	{"bm-flags",  16,    8,	   NULL,	    NULL,	g_bm_flags, NULL,   NULL},
	{"length",    0,     16,   NULL,	    g_len_calc, NULL,	    NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	    NULL,   NULL}
};

/* TYPE table when TGT==PCIe
 * Print the TYPE value.
 * Print the rest of the fields
 */
static const struct field_def_s g_pci_type[] = {
     /* name        shift  width   val_2_desc        calc   sub-fields indexed  jump */
	{"type",      56,    2,	   g_def_type_desc,  NULL,    NULL,	 NULL,   NULL},
	{"RSVD",      48,    8,	   NULL,	     NULL,    NULL,	 NULL,	 NULL},
	{"info",      16,    32,   NULL,	     NULL,    pci_info,	 NULL,	 NULL},
	{"length",    0,     16,   NULL,	     NULL,    NULL,	 NULL,	 NULL},
	{NULL,        0,     0,	   NULL,	     NULL,    NULL,	 NULL,   NULL}
};

/* TYPE table when TGT==IMMEDIATE && TYPE==DATA
 * Print the rest of the fields
 */
static const struct field_def_s g_imm_r_data[] = {
     /* name        shift  width  val_2_desc    calc  sub-fields indexed  jump */
	{"length",    48,    8,	   NULL,	NULL,   NULL,     NULL,	   NULL},
	{"offset",    40,    8,	   NULL,	NULL,   NULL,     NULL,	   NULL},
	{"skip+data", 0,     40,   NULL,	NULL,   NULL,     NULL,	   NULL},
	{NULL,        0,     0,	   NULL,	NULL,   NULL,     NULL,	   NULL}
};

/* TYPE table when TGT==IMMEDIATE && TYPE==META
 * Print the rest of the fields
 */
static const struct field_def_s g_imm_r_meta[] = {
     /* name        shift  width  val_2_desc    calc  sub-fields indexed  jump */
	{"f1_f1",     55,    1,	   NULL,	NULL,	NULL,	  NULL,   NULL},
	{"rsvd",      53,    2,	   NULL,	NULL,	NULL,	  NULL,   NULL},
	{"ufid",      44,    9,	   NULL,	NULL,	NULL,	  NULL,   NULL},
	{"pf",	      41,    3,	   NULL,	NULL,	NULL,	  NULL,   NULL},
	{"vf",	      32,    9,	   NULL,	NULL,	NULL,	  NULL,   NULL},
	{"pasid",     0,     32,   NULL,	NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	NULL,   NULL,     NULL,	  NULL}
};

/* TGT==IMMEDIATE rest of the fields IX table.
 * Jump into the TGT==IMMEDIATE rest of the fields table.
 */
static const struct field_def_s g_imm_r_ix[] = {
     /* name     shift  width  val_2_desc  calc  sub-fields  indexed jump */
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_imm_r_data},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_imm_r_meta},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_imm_r_data},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_imm_r_meta},
	{NULL,     0,     0,	   NULL,   NULL,   NULL,     NULL,   NULL}
};

/* TYPE table when TGT==IMMEDIATE
 * Print the TYPE value.
 * Index into the rest of the fields table using the type value.
 */
static const struct field_def_s g_imm_type[] = {
     /* name        shift  width   val_2_desc       calc  sub-fields indexed  jump */
	{"type",      56,    2,	   g_i_type_desc,   NULL,   NULL,     NULL,	   NULL},
	{"type",      56,    2,	   NULL,	    NULL,   NULL,     g_imm_r_ix,  NULL},

};

/* TYPE table when TGT==GENERATED
 * Print the TYPE value.
 * Print the rest of the fields
 */
static const struct field_def_s g_gen_type[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed  jump */
	{"type",      56,    2,	   g_g_type_desc,   NULL,	NULL,	  NULL,   NULL},
	{"TODO",      0,     56,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	  NULL,   NULL}
};

/* TYPE IX table.
 * Jump into the TYPE table.
 */
static const struct field_def_s g_type_ix[] = {
     /* name     shift  width  val_2_desc  calc  sub-fields  indexed jump */
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_dpu_type},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_pci_type},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_imm_type},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   g_gen_type},
	{NULL,     0,     0,	   NULL,   NULL,   NULL,     NULL,   NULL}
};

/*******************************************************************************
 * INS tables								       *
 ******************************************************************************/
/* INS for TGT==DPU memory
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s g_dpu_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    g_d_ins_desc, NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    g_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS for TGT==PCIe
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s g_pci_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    g_p_ins_desc, NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    g_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS for TGT==IMMEDIATE
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s g_imm_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    g_i_ins_desc, NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    g_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS for TGT==GENERATED
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s g_gen_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    NULL,	    NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    g_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS IX table.
 * Jump into the INS table.
 */
static const struct field_def_s g_ins_ix[] = {
     /* name     shift width  val_2_desc   calc  sub-fields   indexed  jump */
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	g_dpu_ins},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	g_pci_ins},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	g_imm_ins},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	g_gen_ins},
	{NULL, 	   0,	0,	NULL,	   NULL,    NULL,	NULL,	NULL}
};

/*******************************************************************************
 * TGT tables								       *
 ******************************************************************************/
/* Print the TGT value.
 * Index into the INS IX table using the TGT value.
 */
static const struct field_def_s g_tgt[] = {
     /* name     shift width  val_2_desc    calc  sub-fields    indexed   jump */
	{"tgt",	   60,	2,	g_tgt_desc, NULL,    NULL,	NULL,      NULL},
	{"tgt",	   60,	2,	NULL,	    NULL,    NULL,	g_ins_ix,  NULL},
	{NULL, 	   0,	0,	NULL,	    NULL,    NULL,	NULL,	   NULL}
};
