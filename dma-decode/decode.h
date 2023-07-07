#ifndef _DECODE_H_
#define _DECODE_H_

#include <stdint.h>

/* Bit masks */
#define BIT_MASK(bit)		((1ull << (bit)) - 1)

#define ARRAY_SIZE(a)		(sizeof(a) / sizeof((a)[0]))

/**
 * val_2_desc_s - Value/definition pair for a field
 * @value: Single valid value the field can take
 * @desc: Text describing the field value
 *
 * Description:
 * This structure is used to maintain a list of all the values and
 * descriptions a field can take.
 */
struct val_2_desc_s {
	int	val;
	char	*desc;
};

/**
 * field_def_s - Describes a data field.
 * @name: Field name.
 * @shift: Field bit start position.
 * @width: Width of the fields in bits
 * @val_2_desc: List of value/description pairs.
 * @calc: Function to calculate/decode/process the field value.
 * @sub_fields: If not NULL, field must be further decoded.
 * @indexed: Jump into another table by index
 * @jump: Jump into another table
 */
struct field_def_s {
	const char			*name;
	int				shift;
	int				width;
	const struct val_2_desc_s	*val_2_desc;
	void 				(*calc)(char		*ident,
						const char	*field_name,
						uint64_t	field_val);
	const struct field_def_s	*sub_fields;
	const struct field_def_s	*indexed;
	const struct field_def_s	*jump;
};

/**
 * data_type_def_s - Defines one top level type of data to decode
 * @option: Command line option that identifies the type of data
 * @name: Name of the type of data
 * @fields: Pointer to the field table that make up the data
 *
 * Description:
 * This structure is used to maintain a list of all the data types that can be
 * decoded.
 */
struct data_type_def_s {
	char				option;
	char				*name;
	const struct field_def_s	*fields;
};

static void cmdls_calc(char *ident, const char *field_name, uint64_t field_val);
static void cmdlp_calc(char *ident, const char *field_name, uint64_t field_val);
static void a1_l_calc(char *ident, const char *field_name, uint64_t field_val);
static void g_len_calc(char *ident, const char *field_name, uint64_t field_val);
static void s_len_calc(char *ident, const char *field_name, uint64_t field_val);
static void o_crc_l_calc(char *ident, const char *field_name, uint64_t field_val);
static void o_crc_so_calc(char *ident, const char *field_name, uint64_t field_val);
static void o_crc_sto_calc(char *ident, const char *field_name, uint64_t field_val);
static void i_m_rd_sz_calc(char *ident, const char *field_name, uint64_t field_val);
static void i_m_pld_calc(char *ident, const char *field_name, uint64_t field_val);
static void i_ignore_calc(char *ident, const char *field_name, uint64_t field_val);

#endif /* _DECODE_H_ */
