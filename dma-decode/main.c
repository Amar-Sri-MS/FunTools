#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>
#include <errno.h>
#include <limits.h>

#include "decode.h"
#include "data-type-def.h"

#define MAX_IDENT			80
#define MAX_INPUT_VALUES		2

static void cmdls_calc(char		*ident,
		       const char	*field_name,
		       uint64_t		field_val)
{
	printf("%s%s=%#ld (Size of cmd list in 64-bit words including CWU)\n",
	       ident, field_name, field_val);
}

static void cmdlp_calc(char		*ident,
		       const char	*field_name,
		       uint64_t		field_val)
{
	printf("%s%s=%#016lx (Cmd list address)\n",
	       ident, field_name, field_val);
}

static void a1_l_calc(char		*ident,
		      const char	*field_name,
		      uint64_t		field_val)
{
	printf("%s%s=%#ld (Length of data moved in bytes)\n",
	       ident, field_name, field_val);
}

/* Print the length of the gather command */
static void g_len_calc(char		*ident,
		       const char	*field_name,
		       uint64_t		field_val)
{
	printf("%s%s=%#ld (Length of data to gather in bytes)\n",
	       ident, field_name, field_val);
}

/* Print the length of the scatter command */
static void s_len_calc(char		*ident,
		       const char	*field_name,
		       uint64_t		field_val)
{
	printf("%s%s=%#ld (Length of the scatter buffer in bytes)\n",
	       ident, field_name, field_val);
}

/* Print the the PCIe INFO maximum read size */
static void i_m_rd_sz_calc(char		*ident,
			   const char	*field_name,
			   uint64_t	field_val)
{
	printf("%s%s=%#ld (Maximum read request size in log2)\n",
	       ident, field_name, field_val);
}

/* Print the the PCIe INFO maximum payload size */
static void i_m_pld_calc(char		*ident,
			 const char	*field_name,
			 uint64_t	field_val)
{
	printf("%s%s=%#ld (Maximum payload size in log2)\n",
	       ident, field_name, field_val);
}

/* Print the the PCIe INFO steering tag index */
static void i_ignore_calc(char		*ident,
			  const char	*field_name,
			  uint64_t	field_val)
{
	printf("%s%s=%#ld (Ignored)\n",
	       ident, field_name, field_val);
}

static void o_crc_l_calc(char		*ident,
			 const char	*field_name,
			 uint64_t		field_val)
{
	printf("%s%s=%#ld (Length of total CRC payload in bytes)\n",
	       ident, field_name, field_val);
}

static void o_crc_so_calc(char		*ident,
			  const char	*field_name,
			  uint64_t		field_val)
{
	printf("%s%s=%#ld (Start payload offset to include in the CRC)\n",
	       ident, field_name, field_val);
}

static void o_crc_sto_calc(char		*ident,
			   const char	*field_name,
			   uint64_t		field_val)
{
	printf("%s%s=%#ld (Stop payload offset ito include in the CRC)\n",
	       ident, field_name, field_val);
}

static void usage(char *prog_name)
{
	char	*saveptr;
	char	*token;

#if !defined(__APPLE__)
	/* Remove the path from the command */
	token = strtok_r(prog_name, "/", &saveptr);
	while (token && strlen(saveptr) > 0)
		token = strtok_r(NULL, "/", &saveptr);
#else
	token = prog_name;
#endif

	/*
	 * Two or three arguments are needed:
	 *	1. The register to decode
	 *	2. The register's value(s)
	 */
	printf("Usage: %s <option> <value1>,[value2]\n", token);
	printf("       -a <action>          Decodes the DMA WU action\n");
	printf("       -0 <arg0>            Decodes the DMA WU arg0\n");
	printf("       -1 <arg1>,[arg2]     Decodes the DMA WU arg1\n");
	printf("                            and arg2 if present\n");
	printf("       -c <cmd0>,[cmd1]     Decodes the first DMA command\n");
	printf("                            word and the second one if\n");
	printf("                            present\n");
	printf("\n");
	printf("        Examples:\n");
	printf("                %s -a 0x82f8414000842286\n", token);
	printf("                %s -0 0x010c000009991340\n", token);
	printf("                %s -c 0x010c000009991340,0x0000000040e18000\n",
	       token);
	printf("\n");

	return;
}

/**
 * get_data_def - Find the definition of the requested data to decode
 * @option: Command line option identifying the data to decode.
 *
 * Description:
 * Returns a pointer to data definition if found, NULL otherwise.
 */
static const struct data_type_def_s *get_data_def(char	option)
{
	const struct data_type_def_s	*data_type_def;

	data_type_def = data_type_defs;
	while (data_type_def->option) {
		if (data_type_def->option == option)
			return data_type_def;
		data_type_def++;
	}

	return NULL;
}

/**
 * parse_cmdline - Parse the user provided arguments
 * @argc: Number of arguments
 * @argv: Argument list
 * @option: Updated with the option that identifies the data to decode
 * val: Array of values update with the data to decode
 * val_cnt: Number of elements in val
 *
 * Description:
 * Parses the command line and updates the option and data entered by the user.
 * Returns the number of 64b data values entered or a negative number on error.
 */
static int parse_cmdline(int		argc,
			 char		**argv,
			 char		*option,
			 uint64_t	*val,
			 int		val_cnt)
{
	int	opt;
	char	*endptr;
	char	*token;
	int	rc = -1;
	int	i;

	while ((opt = getopt(argc, argv, "a:0:1:2:c:")) != -1) {
		switch (opt) {
		case 'a':
		case '0':
			errno = 0;
			val[0] = strtoull(optarg, &endptr, 0);
			if ((val[0] == 0 && *endptr != '\0') || errno != 0)	{
				printf("ERROR: Invalid value [%s]\n", optarg);
				break;
			}
			*option = opt;
			rc = 1;
			break;
		case '1':
		case 'c':
			*option = opt;

			i = 0;
			token = strtok(optarg, ",");
			while (token != NULL) {
				errno = 0;
				val[i] = strtoull(token, &endptr, 0);
				if ((val[i] == 0 && *endptr != '\0') ||
					errno != 0)	{
					printf("ERROR: Invalid value [%s]\n",
						   token);
					rc = -1;
					break;
				}
				i++;
				token = strtok(NULL, ",");
			}
			rc = i;
			break;
		case '?':
			usage(argv[0]);
			return -1;
		}
	}

	/* Make sure we got the register and value */
	if (rc < 0) {
		usage(argv[0]);
		return rc;
	}

	return rc;
}

static int get_ident(char	*ident,
		     size_t	len,
		     int	cur_level)
{
	int	i;

	if (cur_level * 4 >= len) {
		printf("ERROR: identation exceeded len=%d level=%d\n",
		       len, cur_level);
		return -EINVAL;
	}

	/* Each level is represented as 4 spaces */
	for (i = 0; i < 4 * cur_level; i++)
		ident[i] = ' ';
	ident[i] = '\0';

	return 0;
}

/**
 * get_field_desc - Get the field description for a given value
 * @val_2_desc: Pointer to list of value/description pairs for a field
 * @val: Value to search for
 *
 * Description:
 * Searches the list of value/description pairs for the given value an
 * returns the text description for it
 */
static const char *get_field_desc(const struct val_2_desc_s	*val_2_desc,
				  uint64_t			val)
{
	while (val_2_desc->val >= 0) {
		if (val_2_desc->val == val)
			return val_2_desc->desc;
		val_2_desc++;
	}
	return val_2_desc->desc;
}

/*
 * decode_data:		Decodes the register fields. Will recurse if a field has
 *			sub-fields.
 *
 *  val0:		First register value.
 *  fields:		Points to the start of fields to decode.
 *  cur_level:		Current identation level. Use to add the correct
 *			identation to the printout.
 */
static void decode_data(uint64_t			val0,
			const struct field_def_s	*fields,
			int				cur_level)
{
	char				ident[MAX_IDENT];
	const struct field_def_s	*field;
	const char			*desc;
	uint64_t			field_val;

	/* Get the current level indentation */
	if (get_ident(ident, MAX_IDENT, cur_level))
		return;

	/* Decode all the fields */
	field = &fields[0];
	while (field->name) {
		field_val = (val0 >> field->shift) & BIT_MASK(field->width);

		/* First decode and print the field */
		if (field->indexed || field->jump) {
			/* Nothing to decode or print. This field is used to
			 * switch tables.
			 */
		} else if (field->sub_fields) {
			/* Print the field to star indenting from */
			printf("%s%s=%#lx\n", ident, field->name, field_val);

			/* Recurse decode the rest of the sub-fields */
			decode_data(field_val, field->sub_fields,
				    cur_level + 1);
		} else if (field->val_2_desc) {
			desc = get_field_desc(field->val_2_desc, field_val);
			printf("%s%s=%#lx (%s)\n",
			       ident, field->name, field_val, desc);
		} else if (field->calc) {
			field->calc(ident, field->name, field_val);
		} else {
			printf("%s%s=%ld (%#lx)\n", ident, field->name,
			       field_val, field_val);
		}

		/* Next, figure out the next field to decode */
		if (field->indexed) {
			/* When indexed is present, the value of the current
			 * field determines the next field to decode.
			 */
			field = &field->indexed[field_val];
		} else if (field->jump) {
			/* When jump is present, jump to the next field to
			 * decode.
			 */
			field = field->jump;
		} else {
			field++;
		}
	}
}

int main(int argc, char **argv)
{
	char				option;
	const struct data_type_def_s	*data_type_def;
	const char			*data_name;
	uint64_t			val[MAX_INPUT_VALUES];
	int				val_cnt;

	val_cnt = parse_cmdline(argc, argv, &option, val, MAX_INPUT_VALUES);
	if (val_cnt < 0)
		return val_cnt;

	data_type_def = get_data_def(option);

	/* Decode the first data value */
	printf("%s=%#018lx\n", data_type_def->name, val[0]);
	decode_data(val[0], data_type_def->fields, 1);

	/* Decode the second data value if present*/
	if (val_cnt > 1) {
		printf("%s=%#018lx\n", data_type_def->name, val[1]);
	}

	return 0;
}
