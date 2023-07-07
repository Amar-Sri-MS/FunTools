/*******************************************************************************
 * Field descriptions							       *
 ******************************************************************************/
/* TGT when OPC==GATHER */
static const struct val_2_desc_s s_tgt_desc[] = {
	{0x00, "DPU memory"},
	{0x01, "PCIe"},
	{0x02, "CTRL"},
	{0x03, "NULL, Local (S2)"},
	{-1,   "Not found"}
};

/* INS when TGT==DPU memory */
static const struct val_2_desc_s s_d_ins_desc[] = {
	{0x00, "Coherent memory"},
	{0x01, "BM"},
	{0x02, "HBM (F1), OCM (S1)"},
	{0x03, "DDR"},
	{-1,   "Not found"}
};

/* INS when TGT==PCIe */
static const struct val_2_desc_s s_p_ins_desc[] = {
	{0x00, "Wire (Remote PCIe memory)"},
	{0x01, "RMMU, LOCAL (S2)"},
	{0x02, "RSVD, NULL (S2)"},
	{0x03, "INTR (Interrupt request"},
	{-1,   "Not found"}
};

/* TYPE when TGT==DPU memory && TGT==PCIe */
static const struct val_2_desc_s s_def_type_desc[] = {
	{0x00, "Normal (Single Address)"},
	{0x01, "Stride (Not supported for PCIe)"},
	{0x02, "Normal+EOP (Single Address + EOP)"},
	{0x03, "Stride+EOP (Not supported for PCIe)"},
	{-1,   "Not found"}
};

/* TYPE when TGT==CTRL */
static const struct val_2_desc_s s_ctr_type_desc[] = {
	{0x00, "RSVD"},
	{0x01, "META"},
	{0x02, "RSVD"},
	{0x03, "RSVD"},
	{-1,   "Not found"}
};

/* TYPE when TGT==NULL/Local */
static const struct val_2_desc_s s_null_type_desc[] = {
	{0x00, "DELETE"},
	{0x01, "RSVD, FORWARD (S2)"},
	{0x02, "RSVD, DELETE+EOP (S2)"},
	{0x03, "DELETE+EOP, FORWARD+EOP (S2)"},
	{-1,   "Not found"}
};

/*******************************************************************************
 * Sub-field flags							       *
 ******************************************************************************/
static const struct val_2_desc_s s_e_bit[] = {
	{0x00, "No PWR-E (No forced partial write on last block"},
	{0x01, "PWR-E (Forced partial write on last block"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s s_b_bit[] = {
	{0x00, "No PWR-E (No forced partial write on firt block"},
	{0x01, "PWR-E (Forced partial write on first block"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s s_a_bit[] = {
	{0x00, "No Append (Don't zero fill last block"},
	{0x01, "Append (Zero fill last block"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s s_p_bit[] = {
	{0x00, "No Prepend (Don't zero fill first block"},
	{0x01, "Prepend (Zero fill first block"},
	{-1,   "Not found"}
};

/* Scatter command flags */
static const struct field_def_s s_flags[] = {
      /* name    shift width   val_2_desc   calc sub-fields indexed    jump */
	{"E-bit",  7,	 1,	s_e_bit,    NULL,   NULL,    NULL,	NULL},
	{"B-bit",  6,	 1,	s_b_bit,    NULL,   NULL,    NULL,	NULL},
	{"A-bit",  5,	 1,	s_a_bit,    NULL,   NULL,    NULL,	NULL},
	{"P-bit",  4,	 1,	s_p_bit,    NULL,   NULL,    NULL,	NULL},
	{"RSVD",   0,	 4,	NULL,	    NULL,   NULL,    NULL,	NULL},
	{NULL, 	   0,	 0,	NULL,	    NULL,   NULL,    NULL,	NULL}
};

/*******************************************************************************
 * Sub-field PCIe flags							       *
 ******************************************************************************/
static const struct val_2_desc_s s_p_s_bit[] = {
	{0x00, "RSVD, v-Switch disabled (S2)"},
	{0x01, "RSVD, v-Switch enabled (S2)"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s s_p_r_bit[] = {
	{0x00, "RSVD"},
	{0x01, "RSVD"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s s_p_a_bit[] = {
	{0x00, "No Append (Don't zero fill last block"},
	{0x01, "Append (Zero fill last block"},
	{-1,   "Not found"}
};

static const struct val_2_desc_s s_p_p_bit[] = {
	{0x00, "No Prepend (Don't zero fill first block"},
	{0x01, "Prepend (Zero fill first block"},
	{-1,   "Not found"}
};

/* PCIe flags for INS==Wire */
static const struct field_def_s s_p_w_flags[] = {
      /* name            shift width   val_2_desc   calc sub-fields indexed    jump */
	{"S-bit",	   7,	 1,	s_p_s_bit,  NULL,   NULL,    NULL,	NULL},
	{"R-bit",	   6,	 1,	s_p_r_bit,  NULL,   NULL,    NULL,	NULL},
	{"A-bit",	   5,	 1,	s_p_a_bit,  NULL,   NULL,    NULL,	NULL},
	{"P-bit",	   4,	 1,	s_p_p_bit,  NULL,   NULL,    NULL,	NULL},
	{"R-bit",	   3,	 1,	s_p_r_bit,  NULL,   NULL,    NULL,	NULL},
	{"RSVD, TC (S2)",  0,	 3,	NULL,	    NULL,   NULL,    NULL,	NULL},
	{NULL,		   0,	 0,	NULL,	    NULL,   NULL,    NULL,	NULL}
};

/*******************************************************************************
 * TYPE tables								       *
 ******************************************************************************/
/* TYPE table when TGT==DPU memory
 * Print the TYPE value.
 * Print the rest of the fields
 */
static const struct field_def_s s_dpu_type[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields   indexed  jump */
	{"type",      56,    2,	   s_def_type_desc, NULL,	NULL,	    NULL,   NULL},
	{"flags",     48,    8,	   NULL,	    NULL,	s_flags,    NULL,   NULL},
	{"rsvd",      16,    32,   NULL,	    NULL,	NULL,	    NULL,   NULL},
	{"length",    0,     16,   NULL,	    s_len_calc, NULL,	    NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	    NULL,   NULL}
};

/* TGT==PCIe and INS==Wire
 * Print the rest of the fields
 */
static const struct field_def_s s_pci_wire[] = {
     /* name         shift  width  val_2_desc   calc  sub-fields    indexed  jump */
	{"pci flags",  48,    8,   NULL,	NULL,	s_p_w_flags,  NULL,   NULL},
	{"info",       16,    32,  NULL,	NULL,   pci_info,     NULL,   NULL},
	{"length",     0,     16,  NULL,	NULL,   NULL,	      NULL,   NULL},
	{NULL,	       0,     0,   NULL,	NULL,	NULL,	      NULL,   NULL}
};

/* TGT==PCIe and INS==RMMU
 * Print the rest of the fields
 */
static const struct field_def_s s_pci_rmmu[] = {
     /* name        shift  width   val_2_desc   calc   sub-fields  indexed     jump */
	{"RSVD",      48,    8,	   NULL,	NULL,	NULL,	     NULL,	NULL},
	{"info",      16,    32,   NULL,	NULL,   pci_info,    NULL,	NULL},
	{"length",    0,     16,   NULL,	NULL,   NULL,	     NULL,	NULL},
	{NULL,        0,     0,	   NULL,	NULL,   NULL,	     NULL,	NULL}
};

/* TGT==PCIe and INS==RSVD
 * Print the rest of the fields
 */
static const struct field_def_s s_pci_rsvd[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed  jump */
	{"TODO",      0,     56,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	  NULL,   NULL}
};

/* TGT==PCIe and INS==INTR
 * Print the rest of the fields
 */
static const struct field_def_s s_pci_intr[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed  jump */
	{"TODO",      0,     56,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	  NULL,   NULL}
};

/* PCI IX table.
 * Jump into the PCIe INS table.
 */
static const struct field_def_s s_pci_ix[] = {
     /* name     shift width  val_2_desc   calc  sub-fields  indexed  jump */
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_pci_wire},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_pci_rmmu},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_pci_rsvd},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_pci_intr},
	{NULL, 	   0,	0,	NULL,	   NULL,    NULL,	NULL,	NULL}
};

/* TYPE table when TGT==PCIe
 * Print the TYPE value.
 * Index into the PCI table using the INS value.
 */
static const struct field_def_s s_pci_type[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed   jump */
	{"type",      56,    2,	   s_def_type_desc, NULL,	NULL,	NULL,	   NULL},
	{"ins",	      58,    2,	   NULL,	    NULL,	NULL,	s_pci_ix,  NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	NULL,	   NULL}
};

/* TYPE table when TGT==CTRL
 * Print the TYPE value.
 * Print the rest of the fields
 */
static const struct field_def_s s_ctr_type[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed  jump */
	{"type",      56,    2,	   s_ctr_type_desc, NULL,	NULL,	  NULL,   NULL},
	{"f1_f1",     55,    1,	   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{"rsvd",      53,    2,	   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{"ufid",      44,    9,	   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{"pf",	      41,    3,	   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{"vf",	      32,    9,	   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{"pasid",     0,     32,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	  NULL,   NULL}
};

/* TYPE table when TGT==NULL/Local
 * Print the TYPE value.
 * Print the rest of the fields
 */
static const struct field_def_s s_null_type[] = {
     /* name        shift  width   val_2_desc       calc     sub-fields indexed  jump */
	{"type",      56,    2,	   s_null_type_desc, NULL,	NULL,	  NULL,   NULL},
	{"RSVD",      16,    40,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{"length",    0,     16,   NULL,	    NULL,	NULL,	  NULL,   NULL},
	{NULL,        0,     0,	   NULL,	    NULL,	NULL,	  NULL,   NULL}
};

/* TYPE IX table.
 * Jump into the TYPE table.
 */
static const struct field_def_s s_type_ix[] = {
     /* name     shift  width  val_2_desc  calc  sub-fields  indexed jump */
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   s_dpu_type},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   s_pci_type},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   s_ctr_type},
	{"type",   56,    2,	   NULL,   NULL,   NULL,     NULL,   s_null_type},
	{NULL,     0,     0,	   NULL,   NULL,   NULL,     NULL,   NULL}
};

/*******************************************************************************
 * INS tables								       *
 ******************************************************************************/
/* INS for TGT==DPU memory
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s s_dpu_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    s_d_ins_desc, NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    s_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS for TGT==PCIe
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s s_pci_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    s_p_ins_desc, NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    s_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS for TGT==CTRL
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s s_ctr_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    NULL,	    NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    s_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS for TGT==NULL/Local
 * Print the INS value.
 * Index into the TYPE IX table using the TGT value.
 */
static const struct field_def_s s_nul_ins[] = {
     /* name     shift width  val_2_desc    calc  sub-fields  indexed   jump */
	{"ins",	   58,	2,    NULL,	    NULL,    NULL,    NULL,	 NULL},
	{"tgt",	   60,	2,    NULL,	    NULL,    NULL,    s_type_ix, NULL},
	{NULL, 	   0,	0,    NULL,	    NULL,    NULL,    NULL,	 NULL}
};

/* INS IX table.
 * Jump into the INS table.
 */
static const struct field_def_s s_ins_ix[] = {
     /* name     shift width  val_2_desc   calc  sub-fields  indexed  jump */
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_dpu_ins},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_pci_ins},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_ctr_ins},
	{"ins",	   58,	2,	NULL,	   NULL,    NULL,	NULL,	s_nul_ins},
	{NULL, 	   0,	0,	NULL,	   NULL,    NULL,	NULL,	NULL}
};

/*******************************************************************************
 * TGT tables								       *
 ******************************************************************************/
/* Print the TGT value.
 * Index into the INS IX table using the TGT value.
 */
static const struct field_def_s s_tgt[] = {
     /* name     shift width  val_2_desc    calc  sub-fields    indexed   jump */
	{"tgt",	   60,	2,	s_tgt_desc, NULL,    NULL,	NULL,      NULL},
	{"tgt",	   60,	2,	NULL,	    NULL,    NULL,	s_ins_ix,  NULL},
	{NULL, 	   0,	0,	NULL,	    NULL,    NULL,	NULL,	   NULL}
};
