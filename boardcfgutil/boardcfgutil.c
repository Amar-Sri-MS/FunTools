/*
 *  boardcfgutil.c
 *
 *  Created by Nag Ponugoti on 2023-09-06.
 *  Inherited from Charles Gray's commit 0dbb7d8fd
 *  Copyright © 2023 Microsoft. All rights reserved.
 *
 *  Utility to derive board config json from multiple layers of configs like global, chip and board.
 */

#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <limits.h>     // for PATH_MAX
#include <ctype.h>	// for isprint()
#include <stdio.h>	// for fprintf()
#include <unistd.h>	// for STDOUT_FILENO
#include <stdlib.h>	// for free()
#include <getopt.h>	// for getopt_long()
#include <fcntl.h>	// for open()
#include <string.h>	// for strcmp()
#include <sys/stat.h>   // for fstat()
#include <inttypes.h>
#include <stdint.h>

#ifndef __linux__
/* get the nice linux macros on other platforms */
#include <platform/mips64/include/endian.h> // this could be in a better location...
#endif

#include <FunSDK/config/include/boot_config.h>

// We must define PLATFORM_POSIX to get fun_json_write_to_fd() and other fun_malloc related posix utitilies
#define PLATFORM_POSIX 1

/* Don't move these includes above PLATFORM_POSIX macro definition */
#include <FunOS/utils/threaded/fun_malloc_threaded.h>
#include <FunOS/utils/threaded/fun_config_json_utils.h>

#define NOMODE      (0)
#define TEXT        (1)
#define BINARY      (2)
#define TEXTONELINE (3)

#define DBG_LOG_ENABLE 0

#if DBG_LOG_ENABLE
#define log(...)                 do { fprintf (stdout, __VA_ARGS__); fflush(stdout); } while (0)
#define BCFG_JSON_LOG(fmt, js)   do { fun_json_printf(fmt, js); } while(0)
#else /* DBG_LOG_ENABLE */
#define log(...)                 do { } while (0)
#define BCFG_JSON_LOG(...)       do { } while (0)
#endif /* DBG_LOG_ENABLE */

#define eprintf(...)             do { fprintf (stderr, __VA_ARGS__); fflush(stderr); } while (0)
#define die(...)                 do { fprintf (stderr, __VA_ARGS__); fflush(stderr); exit(1); } while (0)


static int _verbose = 0;

/** utility **/
static void oom(void)
{
	eprintf("out of memory\n");
	exit(-1);
}

static uint32_t _board_cfg_data_start_offset(void)
{
	return offsetof(struct board_cfg, data);
}

#define TABS "\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
MAYBE_UNUSED static const char *_tabs(uint32_t depth)
{
	return &TABS[strlen(TABS)-depth];
}

/** value conversion **/
#define FLAG_MAX (63)
struct valtab {
	const char *str;
	uint64_t val;
};

static struct valtab _pcie_cfg_flag_tab[] = {
	{"SRIS_ENABLED", PCIE_CNTLR_FLAGS_SRIS_ENABLE },

        /* must be last */
        {NULL, 0}
};

static struct valtab _bif_valtab[] = {
	{"BIF_ONE_16", 0},
	{"BIF_TWO_8",  1},
	{"BIF_FOUR_4", 2},
	{"BIF_HYBRID", 3},

	/* must be last */
	{NULL, 0}
};

static struct valtab _porttype_valtab[] = {
	{"EP",   PCIE_PORT_TYPE_EP},
	{"RC",   PCIE_PORT_TYPE_RC},
	{"UPSW", PCIE_PORT_TYPE_UPSW},
	{"DNSW", PCIE_PORT_TYPE_DNSW},

	/* must be last */
	{NULL, 0}
};

static struct valtab _cfgtype_valtab[] = {
	{ "PCIE",   BOARD_CFG_PCIE },
	{ "PLL",   BOARD_CFG_PLL },
	{ "DDR", BOARD_CFG_DDR },

	/* must be last */
	{NULL, 0}
};

static struct valtab _gen_valtab[] = {
	{"GEN1", 0},
	{"GEN2", 1},
	{"GEN3", 2},
	{"GEN4", 3},
	{"GEN5", 4},

	/* must be last */
	{NULL, 0}
};

static struct valtab _width_valtab[] = {
	{"x1",  0},
	{"x2",  1},
	{"x4",  2},
	{"x8",  3},
	{"x16", 4},
	{"x32", 5},

	/* must be last */
	{NULL, 0}
};

static bool __str2val(struct valtab *tab, const char *str, uint64_t *val)
{
	int i = 0;

	while (tab[i].str != NULL) {
		if(strcmp(str, tab[i].str) == 0) {
			/* found the flag */
			*val = tab[i].val;
			return true;
		}

		/* next */
		i++;
	}

	return false;
}

static const char *__val2str(struct valtab *tab, uint64_t val)
{
	int i = 0;

	while (tab[i].str != NULL) {
		if(tab[i].val == val) {
			/* found the value */
			return tab[i].str;
		}

		/* next */
		i++;
	}

	return "<unknown>";
}

bool _cfg_valid(struct board_cfg *cfg)
{
	assert(cfg != NULL);

	if (cfg->magic != htole64(BOARD_CFG_MAGIC))
		return false;

	if ((cfg->version <= 0) || (cfg->version > htole32(BOARD_CFG_VERSION)))
		return false;

	/* magic and version OK */
	return true;
}

bool _pcie_cfg_valid(struct board_cfg_pcie *cfg)
{
	assert(cfg != NULL);

	if (cfg->header.magic != htole64(BOARD_CFG_PCIE_MAGIC))
		return false;

	if ((cfg->header.version <= 0) || (cfg->header.version > htole32(BOARD_PCIE_CFG_VERSION)))
		return false;

	/* magic and version OK */
	return true;
}

bool _pll_cfg_valid(struct board_cfg_pll *cfg)
{
	assert(cfg != NULL);

	if (cfg->header.magic != htole64(BOARD_CFG_PLL_MAGIC))
		return false;

	if ((cfg->header.version <= 0) || (cfg->header.version > htole32(BOARD_PLL_CFG_VERSION)))
		return false;

	/* magic and version OK */
	return true;
}

bool _ddr_cfg_valid(struct board_cfg_ddr *cfg)
{
	assert(cfg != NULL);

	if (cfg->header.magic != htole64(BOARD_CFG_DDR_MAGIC))
		return false;

	if ((cfg->header.version <= 0) || (cfg->header.version > htole32(BOARD_DDR_CFG_VERSION)))
		return false;

	/* magic and version OK */
	return true;
}

static void _magic2printable(char str[sizeof(uint64_t)+1], uint64_t magic)
{
	int i;

	/* copy the bytes as-is */
	memcpy(str, &magic, sizeof(uint64_t));
	str[sizeof(uint64_t)] = '\0';

	/* replace anything unprintable like hexdump -C */
	for (i = 0; i < sizeof(uint64_t); i++) {
		if (!isprint(str[i]))
			str[i] = '.';
	}
}

/** config pretty-printer **/
static void __pretty_print_flags(struct valtab *tab, uint64_t flags)
{
	uint64_t remflags = flags;
	bool sep = false;
	bool not = false;
	int i = 0;

	while (tab[i].str != NULL) {
		not = true;
		if((flags & tab[i].val) == tab[i].val) {
			/* found the flag */
			not = false;
			remflags ^= tab[i].val;
		}

		/* print the flag */
		printf("%s%s%s",
		       sep ? " | " : "",
		       not ? "~" : "",
		       tab[i].str);

		/* next */
		sep = true;
		i++;
	}

	if (remflags != 0) {
		printf("  (unknown flags: 0x%" PRIx64 ")", remflags);
	}
}

static void pretty_print_pcie_cfg_flags(uint64_t flags)
{
	__pretty_print_flags(_pcie_cfg_flag_tab, flags);
}

static void _pretty_print_board_cfg_header(uint32_t depth, struct board_cfg_header *header)
{
	assert(header);

	char magic_str[sizeof(uint64_t)+1];

	printf("%scfg type: %s [%u]\n", _tabs(depth),
		__val2str(_cfgtype_valtab, le16toh(header->cfg_type)), le16toh(header->cfg_type));
	printf("%sversion: %u\n",   _tabs(depth), le32toh(header->version));
	printf("%ssize: %u\n",   _tabs(depth), le32toh(header->size_bytes));
	_magic2printable(magic_str, header->magic);
	printf("%smagic: %s [0x%" PRIx64 "]\n", _tabs(depth), magic_str, le64toh(header->magic));

}

static void _pretty_print_board_pcie_cfg(uint32_t depth, struct board_cfg_pcie *cfg)
{
	_pretty_print_board_cfg_header(depth, &cfg->header);
	printf("%shsu_id: %u\n",   _tabs(depth), cfg->link_cfg.hsu_id);
	printf("%scntlr_id: %u\n", _tabs(depth), cfg->link_cfg.cntlr_id);
	printf("%sbif: %s [%u]\n", _tabs(depth),
			__val2str(_bif_valtab, cfg->link_cfg.bif), cfg->link_cfg.bif);
	printf("%spcie_gen: %s [%u]\n", _tabs(depth),
		__val2str(_gen_valtab, cfg->link_cfg.pcie_gen), cfg->link_cfg.pcie_gen);
	printf("%spcie_width: %s [%u]\n", _tabs(depth),
	       __val2str(_width_valtab, cfg->link_cfg.pcie_width),
	       cfg->link_cfg.pcie_width);
	printf("%sport_type: %s [%u]\n", _tabs(depth),
	       __val2str(_porttype_valtab, cfg->link_cfg.port_type),
	       cfg->link_cfg.port_type);
	printf("%spcie cfg flags: 0x%" PRIx64 " = ", _tabs(depth), le64toh(cfg->link_cfg.flags));
	pretty_print_pcie_cfg_flags(be64toh(cfg->link_cfg.flags));
	printf("%sperst_gpio: %u\n", _tabs(depth), cfg->perst_gpio);
	printf("%sclock_switch_gpio: %u\n", _tabs(depth), cfg->clock_switch_gpio);
	printf("\n\n");
}

static void _pretty_print_board_pll_cfg(uint32_t depth, struct board_cfg_pll *cfg)
{
	_pretty_print_board_cfg_header(depth, &cfg->header);
	printf("%ssoc_freq_MHz: %u\n",   _tabs(depth), le16toh(cfg->soc_freq_MHz));
	printf("%spc_freq_MHz: %u\n",   _tabs(depth), le16toh(cfg->pc_freq_MHz));
	printf("\n\n");
}

static void _pretty_print_board_ddr_cfg(uint32_t depth, struct board_cfg_ddr *cfg)
{
	_pretty_print_board_cfg_header(depth, &cfg->header);
	uint8_t num_channels = cfg->num_channels;

	printf("%snum_channels: %u\n",   _tabs(depth), num_channels);

	printf("%sddr_sizes_GB: [ ", _tabs(depth));
	for (uint8_t i = 0; i < num_channels; i++) {
		printf("%d ", le16toh(cfg->ddr_size_GB[i]));
	}
	printf("]\n\n");
}

static void _pretty_print_cfg(uint32_t depth, struct board_cfg *cfg)
{
	char mstr[sizeof(uint64_t) + 1];

	assert(cfg != NULL);

	/* magic */
	_magic2printable(mstr, cfg->magic);
	printf("%smagic  : 0x%" PRIx64" [%s]\n",
	       _tabs(depth), le64toh(cfg->magic), mstr);

	/* version */
	printf("%sversion: %u\n", _tabs(depth), le32toh(cfg->version));

	/* *description */
	printf("%sdescription: %s\n", _tabs(depth), cfg->descr);

	/* num_cfg_entries & size_bytes */
	uint8_t num_cfg_entries = cfg->num_cfg_entries;
	printf("%snum_cfg_entries: %u\n", _tabs(depth), num_cfg_entries);

	uint32_t board_cfg_size = le32toh(cfg->size_bytes);
	printf("%ssize_bytes: %u (total: %u)\n",
	       _tabs(depth), board_cfg_size,
	       board_cfg_size + _board_cfg_data_start_offset());

	/* validity check */
	printf("%sconfig blob is%s valid\n",
	       _tabs(depth), _cfg_valid(cfg) ? "" : " NOT");

	/* print all cfg entries */
	printf("\n");

	void *cfg_ptr = &cfg->data;

	for (uint8_t i = 0; i < num_cfg_entries; i++) {
		struct board_cfg_header *header = cfg_ptr;
		uint16_t cfg_type = le16toh(header->cfg_type);
		uint32_t size_bytes = le32toh(header->size_bytes);

		switch (cfg_type) {
		case BOARD_CFG_PCIE:
			_pretty_print_board_pcie_cfg(depth + 1, cfg_ptr);
			break;
		case BOARD_CFG_PLL:
			_pretty_print_board_pll_cfg(depth + 1, cfg_ptr);
			break;
		case BOARD_CFG_DDR:
			_pretty_print_board_ddr_cfg(depth + 1, cfg_ptr);
			break;
		default:
			eprintf("Invalid cfg type: %u\n", cfg_type);
		}

		cfg_ptr += size_bytes;
	}

	log("cfg->size_bytes: %u cfg_ptr: %p cfg->data: %p\n",
	    board_cfg_size, cfg_ptr, cfg->data);
	assert(board_cfg_size == (cfg_ptr - (void *)(cfg->data)));
}


/* Board cfg need to be generated only for sub profiles which have the config that needs to applied in the sbpfirmware */
static bool _valid_bootstrap_subprofile(const char *sub_prof, char *chip)
{
	/* subprofiles with bootstrap board config for S'class chips */
	const char *bootstrap_sub_profs_s[] = { "hu_profile", "ddr_profile", "pll_profile" };

	/* subprofiles with bootstrap board config for F'class chips */
	const char *bootstrap_sub_profs_f[] = { "pll_profile" };
	const char **bootstrap_sub_profs = NULL;
	size_t num_sub_profs = 0;

	if (!strncmp(chip, "s1", 2) || !strncmp(chip, "s2", 2)) {
		bootstrap_sub_profs = bootstrap_sub_profs_s;
		num_sub_profs = ARRAY_SIZE(bootstrap_sub_profs_s);
	} else if (!strncmp(chip, "f1", 2) || !strncmp(chip, "f2", 2)) {
		bootstrap_sub_profs = bootstrap_sub_profs_f;
		num_sub_profs = ARRAY_SIZE(bootstrap_sub_profs_f);
	} else
		die("Invalid chip name(%s)!\n", chip);

	for (uint16_t i = 0; i < num_sub_profs; i++) {
		if (!strcmp(bootstrap_sub_profs[i], sub_prof)) {
			return true;
		}
	}

	return false;
}

static bool _chip_name_from_sku_json(const struct fun_json *sku_json, char *chip_name)
{
	const char *chip;
	if (!fun_json_lookup_string(sku_json, "PlatformInfo/chip", &chip)) {
		eprintf("missing PlatformInfo/chip dict!\n");
		return false;
	}

	strcpy(chip_name, chip);

	return true;
}

static bool _chip_name_for_sku(struct fun_json *input_json,
			       const char *sku_name, char *chip_name)
{
	const struct fun_json *skus = fun_json_lookup(input_json, "skus");

	if (!fun_json_is_dict(skus)) {
		eprintf("failed to find skus table in input json\n");
		return false;
	}

	const struct fun_json *sku_json = fun_json_lookup(skus, sku_name);

	if (!fun_json_is_dict(sku_json)) {
		eprintf("failed to find sku(%s) json\n", sku_name);
		return false;
	}

	return _chip_name_from_sku_json(sku_json, chip_name);
}

static const struct fun_json *_board_layer_for_sku(const struct fun_json *input_json,
						   const char *sku_name)
{
	const struct fun_json *skus = fun_json_lookup(input_json, "skus");

	if (!fun_json_is_dict(skus)) {
		eprintf("failed to find skus table in input json\n");
		return false;
	}

	const struct fun_json *sku_json = fun_json_lookup(skus, sku_name);

	if (!fun_json_is_dict(sku_json)) {
		eprintf("failed to find sku(%s) json\n", sku_name);
		return false;
	}

	return fun_json_lookup(sku_json, "PlatformInfo/board_layer");
}


#define BOARD_CFG_HSU_ENABLE_MASK ((0x1ULL << BOARD_CFG_HSU_COUNT_MAX) - 1)

static bool hostunits_enable_bmap_get(const struct fun_json *host_intf_cfg_json,
				      uint64_t *hu_en_bmap)
{
	*hu_en_bmap = 0;

	/* just extract the one value */
	if (!fun_json_lookup_uint64(host_intf_cfg_json, "HostUnits/hu_en", hu_en_bmap)) {
		eprintf("Failed to find the hu_en config\n");
		return false;
	}

	/* set any rings as appropriate */
	*hu_en_bmap &= BOARD_CFG_HSU_ENABLE_MASK;

	return true;
}

static const bool hostunits_json_get(const struct fun_json *host_intf_json,
				     const struct fun_json **hostunits_json)
{
	/* process the host unit */
	*hostunits_json = fun_json_lookup(host_intf_json, "HostUnit");

	if (!(*hostunits_json)) {
		eprintf("Can't find HostUnit dictionary\n");
		return false;
	}

	if (!fun_json_is_dict(*hostunits_json)) {
		eprintf("HostUnit: not a dictionary\n");
		return false;
	}

	return true;
}

static const bool hu_json_get(const struct fun_json *hostunits_json,
			      char *key, struct fun_json **hu_json)
{
	/* process the host unit */
	*hu_json = fun_json_lookup(hostunits_json, key);

	if (!*hu_json) {
		eprintf("WARN %s: can't find dictionary\n", key);
		return false;
	}

	if (!fun_json_is_dict(*hu_json)) {
		eprintf("WARN %s: not a dictionary\n", key);
		return false;
	}

	return true;
}

static const bool hu_cntlr_json_get(const struct fun_json *host_intf_json,
				    uint8_t hsu_id, uint8_t cntlr_id,
				    const struct fun_json **cntlr_json)
{
	/* process the host unit */
	const struct fun_json *hu_cntlrs_json;

	hu_cntlrs_json = fun_json_lookup(host_intf_json, "HostUnitController");

	if (!(hu_cntlrs_json)) {
		eprintf("WARN hu_cntlrs_json: can't find dictionary\n");
		return false;
	}

	if (!fun_json_is_dict(hu_cntlrs_json)) {
		eprintf("WARN hu_cntlrs_json: not a dictionary\n");
		*cntlr_json = NULL;
		return true;
	}

	char key[64];
	snprintf(key, ARRAY_SIZE(key), "hu_%d/ctl_%d", hsu_id, cntlr_id);

	*cntlr_json = fun_json_lookup(hu_cntlrs_json, key);

	if (!(*cntlr_json)) {
		eprintf("WARN cntlr_json(%s): does not exist\n", key);
		return false;
	}

	return true;
}

static const bool hu_cntlr_enable_bmap(const struct fun_json *hostunit_json,
				       uint64_t *hu_cntlr_enable)
{
	int64_t en = 0;

        if (!fun_json_lookup_int64(hostunit_json, "ctl_en", &en)) {
                eprintf("bad ctl_en\n");
		return false;
	}

	*hu_cntlr_enable = en;
	return true;
}


/* Parse host unit json config */
static bool parse_hu_cfg(struct fun_json *hu_json, struct pcie_link_cfg *pcie_link_cfg)
{
	const char *bif_mode = NULL;
	uint64_t bif = 0;

        /* get the bif and en bits */
        if (!fun_json_lookup_string(hu_json, "bif_mode", &bif_mode)) {
                eprintf("bad bif mode\n");
                return false;
        }

        if (!__str2val(_bif_valtab, bif_mode, &bif)) {
                eprintf("bad bif value\n");
                return false;
        }

	pcie_link_cfg->bif = (uint8_t)bif;

	return true;
}

/* Checks if the the controller is host pcie endpoint */
static bool hu_cntlr_host_bios_visible(const struct fun_json *cntlr_json)
{
	assert(cntlr_json);

	bool host_bios_visible = false;

	if(!fun_json_lookup_bool(cntlr_json, "host_bios_visible", &host_bios_visible))
		return false;

	return host_bios_visible;
}


/* Parse pcie endpoint gpio json config */
static bool parse_hu_cntlr_gpio_cfg(const struct fun_json *cntlr_json,
				    uint8_t port_type,
				    struct board_cfg_pcie *pcie_cfg)
{
	uint8_t gpio_id = UINT8_MAX;
	const struct fun_json *perst_json = fun_json_lookup(cntlr_json, "perst");

	if (!perst_json) {
		if (port_type == PCIE_PORT_TYPE_EP) {
			eprintf("missing perst config for the hu contlr in ep mode\n");
			return false;
		}
	} else {
		if (!fun_json_is_dict(perst_json)) {
			eprintf("invalid perst config(expected to be a dict)\n");
			return false;
		}

		const char *str = NULL;

		if (!fun_json_lookup_string(perst_json, "type", &str)) {
			eprintf("missing perst type information\n");
			return false;
		}

		if (strcmp(str, "GPIO")) {
			eprintf("invalid perst mapping(should be GPIO)\n");
			return false;
		}

		if (!fun_json_lookup_uint8(perst_json, "id", &gpio_id)) {
			eprintf("missing gpio config\n");
			return false;
		}
	}
	pcie_cfg->perst_gpio = gpio_id;

	if (!fun_json_lookup_uint8(cntlr_json, "clock_switch_gpio", &gpio_id)) {
		gpio_id = UINT8_MAX;
	}
	pcie_cfg->clock_switch_gpio = gpio_id;

        return true;
}

/* Parse controller json config */
static bool parse_hu_cntlr_cfg(const struct fun_json *cntlr_json,
			       struct pcie_link_cfg *pcie_link_cfg)
{
        const char *str = NULL;
        uint64_t u64 = 0, en = 0;
        uint8_t port_type;

        /* embed port type */
        if (fun_json_lookup_string(cntlr_json, "mode", &str)) {
                if (strcmp(str, "EP") == 0)
                        port_type = PCIE_PORT_TYPE_EP;
                else if (strcmp(str, "RC") == 0)
                        port_type = PCIE_PORT_TYPE_RC;
                else if (strcmp(str, "UPSW") == 0)
                        port_type = PCIE_PORT_TYPE_UPSW;
                else if (strcmp(str, "DNSW") == 0)
                        port_type = PCIE_PORT_TYPE_DNSW;
                else {
                        eprintf("ERROR: (%u:%u) unknown 'mode'=%s\n",
                                pcie_link_cfg->hsu_id, pcie_link_cfg->cntlr_id, str);
			return false;
		}
                pcie_link_cfg->port_type =  port_type;
        } else {
		eprintf("WARNING: (%u:%u) Controller 'mode' not found!\n",
			pcie_link_cfg->hsu_id, pcie_link_cfg->cntlr_id);
		return false;
        }

        /* check for sris on/off */
	assert(!pcie_link_cfg->flags);
        if (fun_json_lookup_string(cntlr_json, "sris", &str)) {
                en = PCIE_CNTLR_FLAGS_SRIS_ENABLE;
                en = htole64(en);
                if (strcmp(str, "ON") == 0) {
                        pcie_link_cfg->flags |= en;
                }
        }

        /* pcie_gen */
        if (!fun_json_lookup_string(cntlr_json, "pcie_gen", &str))
                return false;

        if (!__str2val(_gen_valtab, str, &u64)) {
                eprintf("bad pcie_gen value\n");
                return false;
        }
        pcie_link_cfg->pcie_gen = (uint8_t)u64;

        /* pcie_width */
        if (!fun_json_lookup_string(cntlr_json, "pcie_width", &str))
                return false;

        if (!__str2val(_width_valtab, str, &u64)) {
                eprintf("bad pcie_width value\n");
                return false;
        }
        pcie_link_cfg->pcie_width = (uint8_t)u64;

        return true;
}

static uint32_t board_cfg_size(struct board_cfg *cfg)
{
	return _board_cfg_data_start_offset() + le32toh(cfg->size_bytes);
}


static bool _board_cfg_alloc(struct board_cfg **board_cfg_p,
			     void *cfg_data, uint32_t cfg_size)
{
	assert(board_cfg_p);
	assert(cfg_size);

	struct board_cfg *board_cfg = *board_cfg_p;
	uint8_t num_cfg_entries = board_cfg->num_cfg_entries;

	if(num_cfg_entries >= BOARD_CFG_MAX_ENTRIES) {
		eprintf("Too many cfg entries: %u\n", num_cfg_entries);
		return false;
	}

	uint32_t cfg_data_offset = _board_cfg_data_start_offset();
	uint32_t cur_size = board_cfg_size(board_cfg);
	uint32_t new_size = cur_size + cfg_size;
	log("cur_size: %u new_size:%u\n", cur_size, new_size);

	if(new_size > BOARD_CFG_MAX_SIZE_BYTES) {
		eprintf("Exceeded total board config size(%uB)\n", new_size);
		return false;
	}

	board_cfg = (struct board_cfg  *)realloc(board_cfg, new_size);
	if (!board_cfg) {
		eprintf("Failed to allocate config size(%u)\n", new_size);
		return false;
	}

	memcpy((void *)board_cfg + cur_size, cfg_data, cfg_size);
	num_cfg_entries++;

	board_cfg->size_bytes = htole32(new_size - cfg_data_offset);
	board_cfg->num_cfg_entries = num_cfg_entries;

	log("pcie new_size: %u num_cfg_entries: %u board_cfg:%p start: %p\n",
	    new_size, num_cfg_entries, board_cfg, (void *)board_cfg + cur_size);

	*board_cfg_p = board_cfg;
	return true;
}

static bool board_cfg_add_pcie_link_cfg(
		struct board_cfg **board_cfg_p,
		struct board_cfg_pcie *pcie_cfg)
{
	assert(board_cfg_p);
	assert(pcie_cfg);

	if(!(_board_cfg_alloc(board_cfg_p, pcie_cfg, sizeof(*pcie_cfg)))) {
		eprintf("Failed to allocate pcie cfg entry!");
		return false;
	}

	return true;
}

static bool board_cfg_add_ddr_channel_cfg(struct board_cfg **board_cfg_p,
					  struct board_cfg_ddr *ddr_cfg)
{
	assert(board_cfg_p);
	assert(ddr_cfg);

	if(!(_board_cfg_alloc(board_cfg_p, ddr_cfg, sizeof(*ddr_cfg)))) {
		eprintf("Failed to allocate ddr cfg entry!");
		return false;
	}

	return true;
}

static bool board_cfg_add_pll_cfg(struct board_cfg **board_cfg_p,
				  struct board_cfg_pll *pll_cfg)
{
	assert(board_cfg_p);
	assert(pll_cfg);

	if(!(_board_cfg_alloc(board_cfg_p, pll_cfg, sizeof(*pll_cfg)))) {
		eprintf("Failed to allocate pll cfg entry!");
		return false;
	}

	return true;
}

static void _fill_cfg_header(uint32_t type, uint64_t magic,
			     uint32_t size, uint32_t version,
			     OUT struct board_cfg_header *header)
{
	assert(header);

	header->cfg_type = htole16(type);
	header->magic = htole64(magic);
	header->size_bytes = htole32(size);
	header->version = htole32(version);
}

/* parse host unit interface(pcie) config and generate board config blob */
static bool host_intf_cfg_json_parse(const struct fun_json *host_intf_cfg_json,
				     struct board_cfg **board_cfg)
{
	assert(host_intf_cfg_json);
	assert(board_cfg);

	uint64_t hu_en_bmap = 0;

	if (!hostunits_enable_bmap_get(host_intf_cfg_json, &hu_en_bmap))
		return false;

	const struct fun_json * hostunits_json = NULL;

	if(!hostunits_json_get(host_intf_cfg_json, &hostunits_json))
		return false;

	log("hu_en_bmap: 0x%" PRIx64 "\n", hu_en_bmap);

	for (uint8_t hsu_id = 0; hu_en_bmap >> hsu_id; hsu_id++) {
		if (!((hu_en_bmap >> hsu_id) & 0x1))
			continue;

		char hu_key[32];
		struct fun_json *hu_json = NULL;

		snprintf(hu_key, ARRAY_SIZE(hu_key), "hu_%d", hsu_id);
		if(!hu_json_get(hostunits_json, hu_key, &hu_json))
			continue;

		uint64_t cntlr_enable_bmp = 0;

		if (!hu_cntlr_enable_bmap(hu_json, &cntlr_enable_bmp))
			continue;

		if (!cntlr_enable_bmp)
			continue;

		struct board_cfg_pcie board_cfg_pcie = { 0 };
		struct pcie_link_cfg *pcie_link_cfg = &board_cfg_pcie.link_cfg;

		_fill_cfg_header(BOARD_CFG_PCIE, BOARD_CFG_PCIE_MAGIC,
				 sizeof(board_cfg_pcie),
				 BOARD_PCIE_CFG_VERSION,
				 &board_cfg_pcie.header);

		pcie_link_cfg->hsu_id = hsu_id;
		if (!parse_hu_cfg(hu_json, pcie_link_cfg))
			return false;

		/* Loop through all the controller that are enabled */
		for (uint8_t cid = 0; cntlr_enable_bmp >> cid; cid++) {
			if (!((cntlr_enable_bmp >> cid) & 0x1))
				continue;

			pcie_link_cfg->cntlr_id = cid;

			const struct fun_json *cntlr_json = NULL;

			/* Get the controller cfg json */
			if (!hu_cntlr_json_get(host_intf_cfg_json,
					       hsu_id, cid, &cntlr_json)) {
				return false;
			}

			if (!cntlr_json) {
				continue;
			}

			/* *if the the controller is not host pcie endpoint, no need to generate the config blob */
			if (!hu_cntlr_host_bios_visible(cntlr_json))
				continue;

			 pcie_link_cfg->flags = 0;

			if (!parse_hu_cntlr_cfg(cntlr_json, pcie_link_cfg))
				return false;

			if(!parse_hu_cntlr_gpio_cfg(cntlr_json,
						    pcie_link_cfg->port_type,
						    &board_cfg_pcie))
				return false;

			/* add the pcie cfg to board config blob */
			if (!board_cfg_add_pcie_link_cfg(board_cfg, &board_cfg_pcie))
				return false;
		}
	}

	return true;
}

/* parse ddr config and generate board config blob */
static bool ddr_cfg_parse(const struct fun_json *ddr_cfg_json,
			  struct board_cfg **board_cfg)
{
	assert(ddr_cfg_json);
	assert(board_cfg);

	uint8_t num_channels = 0;

	if (!fun_json_lookup_uint8(ddr_cfg_json, "num_channels", &num_channels)) {
		return false;
	}

	struct board_cfg_ddr ddr_cfg = { 0 };

	_fill_cfg_header(BOARD_CFG_DDR, BOARD_CFG_DDR_MAGIC,
			 sizeof(ddr_cfg),
			 BOARD_DDR_CFG_VERSION,
			 &ddr_cfg.header);
	ddr_cfg.num_channels = num_channels;

	const struct fun_json *channel_sizes = NULL;

	channel_sizes = fun_json_lookup(ddr_cfg_json, "sizes_GB");

	if (!channel_sizes) {
		eprintf("Missing channel sizes dict\n");
		return false;
	}

	if (!fun_json_is_array(channel_sizes)) {
		eprintf("ddr channel sizes expected to be an array!\n");
		return false;
	}

	if (num_channels != fun_json_array_count(channel_sizes)) {
		   eprintf("invalid array! %d != %u\n", num_channels,
			   fun_json_array_count(channel_sizes));
		   return false;
	}


	for (uint8_t i = 0; i < num_channels; i++) {
		uint16_t ddr_size = 0;
		const struct fun_json *json = fun_json_array_at(channel_sizes, i);

		if (!fun_json_fill_uint16(json, &ddr_size)) {
			eprintf("ddr channel size error!\n");
			return false;
		}

		ddr_cfg.ddr_size_GB[i] = htole16(ddr_size);
		log("ddr_size_GB[%u]: %u=%u\n", i, ddr_cfg.ddr_size_GB[i], ddr_size);
	}

	if (!board_cfg_add_ddr_channel_cfg(board_cfg, &ddr_cfg))
		return false;

	return true;
}

/* parse pll config and generate board config blob */
static bool pll_cfg_parse(const struct fun_json *pll_cfg_json,
			  struct board_cfg **board_cfg)
{
	assert(pll_cfg_json);
	assert(board_cfg);

	uint16_t soc_freq = 0;
	uint16_t pc_freq = 0;

	if (!fun_json_lookup_uint16(pll_cfg_json, "soc_freq_MHz", &soc_freq)) {
		eprintf("soc_freq config is missing\n");
		return false;
	}

	if (!fun_json_lookup_uint16(pll_cfg_json, "pc_freq_MHz", &pc_freq)) {
		eprintf("pc_freq config is missing\n");
		return false;
	}

	struct board_cfg_pll pll_cfg = { 0 };

	_fill_cfg_header(BOARD_CFG_PLL, BOARD_CFG_PLL_MAGIC,
			 sizeof(pll_cfg),
			 BOARD_PLL_CFG_VERSION,
			 &pll_cfg.header);

	pll_cfg.soc_freq_MHz = htole16(soc_freq);
	pll_cfg.pc_freq_MHz = htole16(pc_freq);


	if (!board_cfg_add_pll_cfg(board_cfg, &pll_cfg))
		return false;

	return true;
}

static bool _is_posix_sku(const char *sku_name)
{
	return strstr(sku_name, "posix");
}

static bool _is_emu_sku(const char *sku_name)
{
	return strstr(sku_name, "qemu") || strstr(sku_name, "emu_");
}

static bool _is_posix_or_emu_sku(const char *sku_name)
{
	return _is_posix_sku(sku_name) || _is_emu_sku(sku_name);
}

static bool _json_to_board_cfg(const struct fun_json *input_json,
		     const char *sku_name,
		     const char *prof_name,
		     struct board_cfg **board_cfg)
{
	assert(board_cfg);
	assert(sku_name != NULL);
	assert(prof_name!= NULL);

	const struct fun_json *skus = fun_json_lookup(input_json, "skus");

	if (!fun_json_is_dict(skus)) {
		eprintf("failed to find skus table in input json\n");
		return false;
	}

	const struct fun_json *sku_json = fun_json_lookup(skus, sku_name);

	if (!sku_json) {
		eprintf("failed to find the json for %s\n", sku_name);
		return false;
	}

	/* clear the config with junk so we don't  */
	memset(*board_cfg, 0, sizeof(struct board_cfg));

	/* check the input is at least semi-valid */
	if (!fun_json_is_dict(sku_json))
		return false;

	(*board_cfg)->magic = htole64(BOARD_CFG_MAGIC);
	(*board_cfg)->version = htole32(BOARD_CFG_VERSION);
	snprintf((*board_cfg)->descr, ARRAY_SIZE((*board_cfg)->descr), "%s-%s",
		 sku_name, prof_name);

	char chip[8] = {};

	if(!_chip_name_from_sku_json(sku_json, chip)) {
		eprintf("ERROR: Failed to get chip name from the sku_json\n");
		return false;
	}

	bool is_silicon_board = !_is_posix_or_emu_sku(sku_name);

	if (!is_silicon_board && !_board_layer_for_sku(input_json, sku_name)) {
		log("Skipping qemu sku_name: %s prof_name: %s\n", sku_name, sku_name);
		return true;
	}

	if (_valid_bootstrap_subprofile("hu_profile", chip)) {
		const struct fun_json * host_intf_json;

		host_intf_json  = fun_json_lookup(sku_json, "HuInterface");

		if (!host_intf_json) {
			eprintf("WARN: HuInterface is missing!");
			return is_silicon_board ? false : true;
		}

		if (!host_intf_cfg_json_parse(host_intf_json, board_cfg)) {
			return false;
		}
	}

	if (_valid_bootstrap_subprofile("ddr_profile", chip)) {
		const struct fun_json *ddr_cfg_json = fun_json_lookup(sku_json, "ddr");

		if (!ddr_cfg_json) {
			eprintf("WARN: ddr cfg is missing!\n");
			return is_silicon_board ? false : true;
		}

		if (!ddr_cfg_parse(ddr_cfg_json, board_cfg))
			return false;
	}

	if (_valid_bootstrap_subprofile("pll_profile", chip)) {
		const struct fun_json *pll_cfg_json = fun_json_lookup(sku_json, "pll");

		/* though f1d1, s1 and s2 have pll config, does not mean that other chips/boards will need this */
		if (!pll_cfg_json) {
			return true;
		}

		if (!pll_cfg_parse(pll_cfg_json, board_cfg))
			return false;
	}

	return true;
}

#define FNAME_MAX_LEN 128

static char *_profile_file_name(const char *sku_name, char *chip_name,  const char *prof_name, char *fname)
{
	int n;

	if (_is_posix_or_emu_sku(sku_name)) {
		n = snprintf(fname, FNAME_MAX_LEN, "board_cfg_%s_%s", sku_name, prof_name) < 0;
	} else {
		/* chip_name is inserted into profile file name to be consistant with per-sku eepr names used in upgrade scripts */
		n = snprintf(fname, FNAME_MAX_LEN, "board_cfg_%s_%s_%s", chip_name, sku_name, prof_name) < 0;
	}

	if ((n < 0) || (n > FNAME_MAX_LEN - 1))
		return NULL;

	return fname;
}

/** config file reading and writing **/
static void _write_cfg_to_file(const char *outdir, const char *fname,
			       struct board_cfg *cfg)
{
	int fd;
	ssize_t n;
	char fpath[PATH_MAX+1];

	assert(outdir != NULL);
	assert(cfg != NULL);

	n = snprintf(fpath, sizeof(fpath), "%s/%s", outdir, fname) < 0;
	if ((n < 0) || (n > sizeof(fpath)))
		die("path name error");

	remove(fpath);
	fd = open(fpath, O_WRONLY|O_CREAT, 0644);
	if (fd < 0) {
		perror("open");
		exit(1);
	}

	uint32_t cfg_size = board_cfg_size(cfg);
	log("board_cfg_size: %u\n", cfg_size);

	n = write(fd, cfg, cfg_size);
	if (n != cfg_size)
		die("truncated write");

	ssize_t remaining = BOARD_CFG_MAX_SIZE_BYTES - cfg_size;
	uint8_t *padding = (uint8_t *)calloc(remaining, sizeof(uint8_t));

	n = write(fd, padding, remaining);
	if (n != remaining) {
		die("failed to write padding bytes to the file!");
	}

	free(padding);
	close(fd);
	log("\twritten to file %s\n", fpath);
}

static void _handle_bin_input(const char *binfile)
{
	int fd = -1;
	ssize_t n = 0;
	struct stat sbuf;

	assert(binfile != NULL);

	/* this makes no sense without verbosity>0 */
	_verbose++;

	/* open, read and dump the file */
	fd = open(binfile, O_RDONLY);
	if (fd < 0) {
		perror("open");
		exit(1);
	}

	log("input binfile: %s:\n", binfile);

	if (fstat(fd, &sbuf) != 0) {
		perror("fstat");
		exit(1);
	}

	struct board_cfg *cfg = (struct board_cfg *)malloc(sbuf.st_size);

	n = read(fd, cfg, sbuf.st_size);
	if (n < sbuf.st_size)
		die("Failed to read all the expected bytes(%zd != %" PRIu64 ")!\n", n, sbuf.st_size);
	close(fd);

	if (sbuf.st_size != BOARD_CFG_MAX_SIZE_BYTES) {
		eprintf("WARNING: file is incorrect size (%" PRIu64 "!= %u)\n",
			sbuf.st_size, BOARD_CFG_MAX_SIZE_BYTES);

	}

	uint32_t cfg_size = board_cfg_size(cfg);

	if (cfg_size > BOARD_CFG_MAX_SIZE_BYTES)
		die("Invalid(too big) cfg size: %u\n", cfg_size);

	/* dump it */
	if (_verbose > 0) {
		printf("Encoded board config:\n");
		_pretty_print_cfg(1, cfg);
	}

	/* return to previous value */
	_verbose--;
	free(cfg);
}


/** json reading **/
static char *_read_input_file(int fd, size_t *outsize)
{
	char *buffer;
	char *pp;
	ssize_t n;
	size_t alloc_size, size = 0;

	alloc_size = 8 * (1024 * 1024);
	buffer = calloc(1, alloc_size);
	if (buffer == NULL)
		oom();
	pp = buffer;

	while ((n = read(fd, pp, alloc_size - size)) > 0) {
		/* total json so far + just read */
		size += n;

		/* if it's full, up the buffer */
		if (size == alloc_size) {
			alloc_size *= 2;
			buffer = realloc(buffer, alloc_size);
			if (buffer == NULL)
				oom();
		}

		/* next read pointer = buffer + existing json */
		pp = buffer + size;
	}

	if (n < 0) {
		perror("read");
		exit(1);
	}

	if (outsize)
		*outsize = size;
	return buffer;
}

static struct fun_json *_read_json(int fd)
{
	struct fun_json *input_json = NULL;
	char *buf;
	size_t size = 0;
	bool parsed_all;

	buf = _read_input_file(fd, &size);
	assert(buf);

	input_json = fun_json_create_from_text_with_status(buf, &parsed_all);

	log("parsed_all: %d size: %zd strlen(buf): %zd\n", parsed_all, size, strlen(buf));
	if (!parsed_all || size != strlen(buf)) {
		fun_json_release(input_json);
		input_json = fun_json_create_error("JSON terminated earlier than the end of file", fun_json_no_copy_no_own);
	}

	free(buf);
	return input_json;
}

static struct fun_json *_read_bjson(int fd)
{
	struct fun_json *input_json = NULL;
	char *buf;
	size_t size;

	buf = _read_input_file(fd, &size);
	assert(buf);

	input_json = fun_json_create_from_binary((uint8_t*)buf, size);

	free(buf);
	return input_json;
}


static struct fun_json *read_input_file(int inmode, const char *infile)
{
	int infd;

	/* open input file */
	if (strcmp(infile, "-") == 0) {
		if (inmode == BINARY)
			die("not reading binary from stdin\n");
		infd = STDIN_FILENO;
	} else {
		infd = open(infile, O_RDONLY);
		if (infd < 0) {
			perror("open input");
			exit(1);
		}
	}

	/* read in some json */
	struct fun_json *input_json = NULL;
	if (inmode == TEXT)
		input_json = _read_json(infd);
	else
		input_json = _read_bjson(infd);

	if (fun_json_is_error_message(input_json)) {
		const char *message;

		fun_json_fill_error_message(input_json, &message);
		return NULL;
	}

	return input_json;
}

static struct fun_json *board_cfg_profiles = NULL;

static void _write_board_prof_list(const char *outdir)
{
	if (!outdir)
		return;

	char fpath[PATH_MAX+1];
	int n = snprintf(fpath, sizeof(fpath), "%s/%s", outdir, "board_cfg_profile_list.json") < 0;
	if ((n < 0) || (n > sizeof(fpath)))
		die("path name error\n");

	remove(fpath);
	int fd = open(fpath, O_WRONLY|O_CREAT, 0644);

	if (fd < 0) {
		perror("open");
		exit(1);
	}

	if (!board_cfg_profiles)
		board_cfg_profiles = fun_json_create_empty_dict();

	char *ouput = fun_json_to_text(board_cfg_profiles);
	size_t output_size = strlen(ouput);

	log("output(%zd): %s\n", strlen(ouput), ouput);

	n = write(fd, ouput, output_size);
	if (n != output_size) {
		perror("truncated write");
		exit(1);
	}
	close(fd);

	fun_free_string(ouput);
	fun_json_release(board_cfg_profiles);
}

static bool _handle_json_input_per_prof(struct fun_json *input_json,
					const char *sku_name,
					const char *prof_name,
					const char *outdir)
{
	/* Override default config with the profile config */
	fun_boot_config_for_profile(sku_name, prof_name, NULL, input_json);
	//BCFG_JSON_LOG("input_json: %s\n", input_json);

	struct board_cfg *board_cfg = calloc(1, sizeof(*board_cfg));

	log("found sku %s\n", sku_name);
	bool b = _json_to_board_cfg(input_json, sku_name, prof_name, &board_cfg);
	if (!b) {
		eprintf("\tFailed to parse sku correctly, ignoring\n");
		return false;
	}

	/* dump it */
	if (_verbose > 0) {
		printf("Encoded board config:\n");
		_pretty_print_cfg(1, board_cfg);
	}

	log("generating final blob for profile: %s\n", prof_name);

	char fname_buf[FNAME_MAX_LEN];
	char chip_name[8];

	if (!_chip_name_for_sku(input_json, sku_name, chip_name))
		die("failed to get chip name for the sku: %s\n", sku_name);

	const char *out_fname = _profile_file_name(sku_name, chip_name, prof_name, fname_buf);

	/* write to a path if it exists */
	if (outdir != NULL) {
		_write_cfg_to_file(outdir, out_fname, board_cfg);
	}

	if (!board_cfg_profiles) {
		board_cfg_profiles = fun_json_create_empty_dict();
	}

	char image_type[FNAME_MAX_LEN] = {};
	const char *keys[] = { "chip", "sku", "prof_name", "image_type", "filename" };
	snprintf(image_type, FNAME_MAX_LEN, "board_cfg_%s_%s", sku_name, prof_name);
	const char *values[] = { chip_name, sku_name, prof_name, image_type, out_fname };
	struct fun_json *pjson = fun_json_create_dict_from_strings(ARRAY_SIZE(keys), keys, fun_json_no_copy_no_own, values, fun_json_copy);


	if (!fun_json_dict_add(board_cfg_profiles, out_fname, fun_json_copy, pjson, false))
		die("Failed to add dict to board cfg profiles list\n");

	log("generating final blob for profile: %s\n", prof_name);
	free(board_cfg);

	return true;
}

static bool _board_prof_list_get(struct fun_json *input_json, const char *sku_name,
				 struct fun_json **prof_list)
{
	const struct fun_json *profiles = fun_json_lookup(input_json, "profiles_config/profiles");

	if (!profiles) {
		eprintf("missing profiles json\n");
		return false;
	}

	*prof_list = fun_json_dict_sorted_keys_as_array(profiles);
	return true;
}

static bool _is_applicable_board_profile(struct fun_json *input_json, const char *sku_name, const char *prof_name)
{
	struct fun_json *subsel_list = NULL;
	struct fun_ptr_and_size subprofile_list;
	const char **sub_prof_name_p = NULL;
	const char *cfg_name = NULL;
	const char *board_name = NULL;
	const struct fun_json *subprofiles = NULL;
	const struct fun_json *board = NULL;
	const struct fun_json *board_layer = NULL;

	if (_is_posix_sku(sku_name)) {
		log("Skipping posix sku_name: %s prof_name: %s\n", sku_name, prof_name);
		return false;
	}

	/* default profile is always applicable */
	if (!strcmp(prof_name, "default"))
		return true;

	/* Get the dict of sub profiles and profile cfg mapped to it */
	subprofile_list  = fun_boot_config_sorted_subprofile_list(prof_name, input_json, NULL, &subsel_list);

	/* get the master list of subprofiles */
	subprofiles = fun_json_lookup(input_json, "profiles_config/subprofiles");
	assert(fun_json_is_dict(subprofiles));

	/* extract chip & board */
	bool ret = false;
	char chip_name[8];

	/* Get the chip name of the sku */
	if(!_chip_name_for_sku(input_json, sku_name, chip_name)) {
		return false;
	}

	/* Get the board layer for the sku */
	board_layer = _board_layer_for_sku(input_json, sku_name);
	if (!board_layer) {
		log("NOTE: json config has no board name(sku: %s prof: %s)\n",
		    sku_name, prof_name);
		ret = false;
		goto end;
	}

	/* iterate over all the selected subprofile keys */
	sub_prof_name_p = (const char **)subprofile_list.ptr;
	BCFG_JSON_LOG("subsel list: %s\n", subsel_list);
	while (*sub_prof_name_p != NULL) {
		/* pre-increment sub_prof_name_p so we can use continue */
		const char *sub_prof_name = *sub_prof_name_p;

		sub_prof_name_p++; /* for the next iteration */

		if (!_valid_bootstrap_subprofile(sub_prof_name, chip_name))
			continue;


		/* Get the config mapped to subprofile at the board layer */
		if (!fun_json_lookup_string(subsel_list, sub_prof_name, &cfg_name))
			die("lost subprofile key %s\n", sub_prof_name);
		log("[fun_config_json] tweaking with subprofile %s=%s\n", sub_prof_name, cfg_name);

		/*
		 * if board_layer is an array, then we iterate over all
		 * array items. If it is a string, then array_count == 0
		 * and we only check the string value directly
		 */
		fun_json_index_t numitems = fun_json_array_count(board_layer);
		for (fun_json_index_t index = 0; index < numitems + 1; index++) {
			bool ok = false;
			if (index < numitems)
				ok = fun_json_fill_string(
					fun_json_array_at(board_layer, index),
					&board_name);
			else
				ok = fun_json_fill_string(board_layer, &board_name);

			if (!ok)
				continue;

			/* apply from the board list */
			log("check path %s/board/%s/%s\n", sub_prof_name, board_name, cfg_name);
			board = fun_json_lookup_multi(subprofiles, sub_prof_name,
						      "board", board_name, cfg_name);
			if (board) {
				BCFG_JSON_LOG("board override exists: %s\n", board);
				ret = true;
				goto end;
			} else {
				log("path %s/board/%s/%s does not exists!\n", sub_prof_name, board_name, cfg_name);
			}
		}
	}

end:
	fun_json_release(subsel_list);
	fun_free_ptr_and_size_threaded(subprofile_list);

	return ret;
}

static void _handle_json_input(int inmode, const char *infile,
			       const char *outdir, const char *sku_name,
			       const char *prof_name)
{
	/* read the input json file */
	struct fun_json *input_json = read_input_file(inmode, infile);

	if (!input_json)
		die("failed to read the JSON from input file\n");

	/* lookup SKUs */
	const struct fun_json *skus = fun_json_lookup(input_json, "skus");

	if (!fun_json_is_dict(skus))
		die("failed to find skus table in input json\n");

	/* generate the board config for every sku and profile combination */
	uint64_t iter = fun_json_dict_iterator(skus);
	const char *key = NULL;
	const struct fun_json *sku_json = NULL;

	while (fun_json_dict_iterate(skus, &iter, &key, &sku_json)) {
		if (!strcmp("unknown_sku", key))
			continue;

		/* if the sku_name is passed, only interested in that sku */
		if (sku_name && strcmp(sku_name, key))
			continue;

		struct fun_json *prof_list = NULL;

		if (prof_name) {
			/* If profile name is passed, only interestred that */
			const char *profiles[] = { prof_name };
			prof_list = fun_json_create_array_from_strings(profiles, fun_json_no_copy_no_own, 1);
			if (!prof_list)
				die("failed to allocate memory for array\n");
		} else {
			/* Get the profile list for the sku */
			if (!_board_prof_list_get(input_json, key, &prof_list))
				die("failed to get the profile list for sku: %s\n", key);
		}

		/* Check every profile if it is applicable to board layer of the sku */
		for_each_index_in_json_array(j, prof_list) {
			struct fun_json *item = fun_json_array_at(prof_list, j);
			const char *prof_name = fun_json_to_string(item, prof_name);

			log("working on sku: %s profile: %s\n", key, prof_name);

			struct fun_json *input_json = read_input_file(inmode, infile);
			if (!input_json)
				die("Failed to read the infile\n");

			/* check if the profile applicable at board layer of the sku */
			if (!_is_applicable_board_profile(input_json, key, prof_name)) {
				log("Profile: %s is not applicable for the sku: %s\n", prof_name, key);
				fun_json_release(input_json);
				continue;
			}

			/* Generate the board cfg for the sku/profile */
			if (!_handle_json_input_per_prof(input_json, key, prof_name, outdir))
				die("failed to parse prof cfg json!\n");

			log("Done with sku: %s profile: %s\n", key, prof_name);
			fun_json_release(input_json);
			input_json = NULL;
			log("Done with sku: %s profile: %s\n", key, prof_name);
		}
		log("finished processing sku: %s\n\n\n", key);
		fun_json_release(prof_list);
	}

	/* write list of all the board configs generated */
	_write_board_prof_list(outdir);
	fun_json_release(input_json);
}

static int
_setmode(int curmode, int newmode)
{
	if (curmode != NOMODE)
		die("can only specify one input or output file\n");

	return newmode;
}

static void
_usage(const char *fname)
{
	fprintf(stderr, "usage: %s -i <input.json> [-o <outdir>] [-s <sku>] [-p <profile>] [-v[v]]\n",
		fname);
	fprintf(stderr, "usage: %s -I <input.bjson> [-o <outdir>] [-s <sku>] [-p <profile>] [-v[v]]\n",
		fname);
	fprintf(stderr, "usage: %s -d <input.bin> [-v]\n",
		fname);
	fprintf(stderr, "    options\n");
	fprintf(stderr, "        -i <file>      input <file> as text json\n");
	fprintf(stderr, "        -I <file>      input <file> as binary json\n");
	fprintf(stderr, "        -p <profile>   override profile name\n");
	fprintf(stderr, "        -d <file>      pretty print  <file> from raw pcicfg.bin format\n");
	fprintf(stderr, "        -o <dir>       output files to <dir>\n");
	fprintf(stderr, "        -s <sku_name>  filter input to <sku_name> only\n");
	fprintf(stderr, "        -v[v]          verbose/very verbose\n");

	exit(1);
}

int
main(int argc, char *argv[])
{
	int r = 0;
	int c;

	int inmode = NOMODE;
	char *infile = NULL;
	char *outdir = NULL;
	char *binfile = NULL;
	char *prof_name = NULL;
	char *sku_name = NULL;

	while (1) {
		static struct option long_options[] = {
			{"in",      required_argument, 0,  'i' },
			{"out",     required_argument, 0,  'o' },
			{"inb",     required_argument, 0,  'I' },
			{"outb",    required_argument, 0,  'O' },
			{"sku",     required_argument, 0,  's' },
			{"profile", required_argument, 0,  'p' },
			{"dump",    required_argument, 0,  'd' },
			{NULL,      no_argument,       0,  'v' },
		};


		c = getopt_long(argc, argv, "i:o:l:I:O:vs:p:d:",
				long_options, NULL);
		if (c == -1)
			break;

		switch (c) {
		case 'i':
			inmode = _setmode(inmode, TEXT);
			infile = optarg;
			break;
		case 'o':
			outdir = optarg;
			break;
		case 'I':
			inmode = _setmode(inmode, BINARY);
			infile = optarg;
			break;
		case 'p':

			prof_name = optarg;
			break;
		case 'd':
			binfile = optarg;
			break;
		case 'v':
			_verbose++;
			break;
		case 's':
			sku_name = optarg;
			_verbose++;
			break;
		case '?':
		default:
			_usage(argv[0]);
		}
	}

	if ((infile == NULL) && (binfile == NULL))
		_usage(argv[0]);

	if (infile != NULL) {
		_handle_json_input(inmode, infile, outdir, sku_name, prof_name);
	}

	if (binfile != NULL) {
		_handle_bin_input(binfile);
	}

	return r;
}

