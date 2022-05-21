/*
 *  pcicfgutil.c
 *
 *  Created by Charles Gray on 2020-10-21.
 *  Copyright © 2020 Fungible. All rights reserved.
 */

/* utility to convert json config to SBP hw_hsu_api_link_config blobs.
 * specs for the entirety of this logic is from this jira:
 *    http://jira/browse/SWOS-11291
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

// We must define PLATFORM_POSIX to get fun_json_write_to_fd()
#define PLATFORM_POSIX 1
#include <FunOS/utils/threaded/fun_json.h>

#define NOMODE      (0)
#define TEXT        (1)
#define BINARY      (2)
#define TEXTONELINE (3)

#define eprintf(...) fprintf (stderr, __VA_ARGS__)
#define die(...) do { fprintf (stderr, __VA_ARGS__); exit(1); } while (0)

static int _verbose = 0;

/** utility **/
static void oom(void)
{
	printf("out of memory\n");
	exit(-1);
}

#define TABS "\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
static const char *_tabs(uint32_t depth)
{
	return &TABS[strlen(TABS)-depth];
}

/** value conversion **/
#define FLAG_MAX (63)
struct valtab {
	const char *str;
	uint64_t val;
};

/* global flags */
static struct valtab _global_flagtab[] = {
	{"NO_PHYS", HW_HSU_API_LINK_CONFIG_FLAGS_NO_PHYS},

	/* must be last */
	{NULL, 0}
};

static struct valtab _ring_flagtab[] = {
	{"ENABLED", HW_HSU_API_LINK_CONFIG_RING_FLAGS_RING_ENABLED},

	/* must be last */
	{NULL, 0}
};

static struct valtab _cid_flagtab[] = {
	{"CID_ENABLED", HW_HSU_API_LINK_CONFIG_CID_FLAGS_CID_ENABLED},
	{"LINK_ENABLED", HW_HSU_API_LINK_CONFIG_CID_FLAGS_LINK_ENABLE},
	{"SRIS_ENABLED", HW_HSU_API_LINK_CONFIG_CID_FLAGS_SRIS_ENABLE},

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

static struct valtab _gen_valtab[] = {
	{"GEN1", 0},
	{"GEN2", 1},
	{"GEN3", 2},
	{"GEN4", 3},
	{"GEN5", 4},
	{"DEFAULT", HW_HSU_API_LINK_CONFIG_PCIE_GEN_DEFAULT},

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
	{"DEFAULT", HW_HSU_API_LINK_CONFIG_PCIE_WIDTH_DEFAULT},

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

/* flags are expected to be in host endian already */
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

static void _pretty_print_flags(uint64_t flags)
{
	__pretty_print_flags(_global_flagtab, flags);
}

static void _pretty_print_cid_flags(uint64_t flags)
{
	/*
	 * Deal with multi-bit fields first.  If this turns into a "thing",
	 * then we can fix this more generally, but Port Type was a field we
	 * never wanted in the (struct hw_hsu_api_link_config) and were
	 * finally forced to take in because we have to set the RX Credits on
	 * a per-Port Type basis before the Link is brought up.
	 */
	unsigned int porttype =
		HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_GET(flags);
	printf("PORT_TYPE=%u ", porttype);
	flags &= ~HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_MASK;

	__pretty_print_flags(_cid_flagtab, flags);
}

static void _pretty_print_ring_flags(uint64_t flags)
{
	__pretty_print_flags(_ring_flagtab, flags);
}

/** config pretty-printer **/

void _pretty_print_cid(uint32_t depth, struct hw_hsu_cid_config *cid)
{
	if ((_verbose < 2)
	    && ((be64toh(cid->cid_flags) & HW_HSU_API_LINK_CONFIG_CID_FLAGS_CID_ENABLED) == 0)) {
		printf("%s<disabled>\n", _tabs(depth));
		return;
	}

	/* flags */
	printf("%scid_flags: 0x%" PRIx64 " = ",
	       _tabs(depth), be64toh(cid->cid_flags));
	_pretty_print_cid_flags(be64toh(cid->cid_flags));
	printf("\n");

	/* pci values */
	printf("%spcie_gen: %s [%u]\n", _tabs(depth),
	       __val2str(_gen_valtab, be32toh(cid->pcie_gen)),
	       be32toh(cid->pcie_gen));
	printf("%spcie_width: %s [%u]\n", _tabs(depth),
	       __val2str(_width_valtab, be32toh(cid->pcie_width)),
	       be32toh(cid->pcie_width));
}

void _pretty_print_ring(uint32_t depth, struct hw_hsu_ring_config *ring)
{
	uint32_t cid = 0;

	if ((_verbose < 2)
	    && ((be64toh(ring->ring_flags) & HW_HSU_API_LINK_CONFIG_RING_FLAGS_RING_ENABLED) == 0)) {
		printf("%s<disabled>\n", _tabs(depth));
		return;
	}
	
	printf("%sbif: %s [%u]\n", _tabs(depth),
	       __val2str(_bif_valtab, be32toh(ring->bif)),
	       be32toh(ring->bif));

	/* flags */
	printf("%sring_flags: 0x%" PRIx64 " = ",
	       _tabs(depth), be64toh(ring->ring_flags));
	_pretty_print_ring_flags(be64toh(ring->ring_flags));
	printf("\n");
	

	for (cid = 0; cid < HW_HSU_API_LINK_CONFIG_V0_MAX_CIDS; cid++) {
		printf("%scid_config[%d]:\n", _tabs(depth), cid);
		_pretty_print_cid(depth+1, &ring->cid_config[cid]);
	}
}


bool _cfg_valid(struct hw_hsu_api_link_config *cfg)
{
	assert(cfg != NULL);

	if (cfg->magic != htobe64(HW_HSU_API_LINK_CONFIG_MAGIC))
		return false;

	if (cfg->version != htobe32(HW_HSU_API_LINK_CONFIG_VERSION_V0))
		return false;

	/* magic and version OK */
	return true;
}

void _magic2printable(char str[sizeof(uint64_t)+1], uint64_t magic)
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

void _pretty_print_cfg(uint32_t depth, struct hw_hsu_api_link_config *cfg)
{
	int ring = 0;
	char mstr[sizeof(uint64_t)+1];

	assert(cfg != NULL);

	/* magic */
	_magic2printable(mstr, cfg->magic);
	printf("%smagic  : 0x%" PRIx64" [%s]\n",
	       _tabs(depth), be64toh(cfg->magic), mstr);

	/* version */
	printf("%sversion: %d [unsigned=%u]\n",
	       _tabs(depth), be32toh(cfg->version), be32toh(cfg->version));

	/* validity check */
	printf("%sconfig blob is%s valid\n",
	       _tabs(depth), _cfg_valid(cfg) ? "" : " NOT");
	
	/* IDs */
	printf("\n");
	printf("%ssku_id    : %u\n", _tabs(depth), be32toh(cfg->sku_id));
	printf("%sid        : %u\n", _tabs(depth), be32toh(cfg->id));
	printf("%sid_version: %u\n", _tabs(depth), be32toh(cfg->id_version));

	/* flags */
	printf("\n");
	printf("%sflags     : 0x%" PRIx64" = ",
	       _tabs(depth), be64toh(cfg->flags));
	_pretty_print_flags(be64toh(cfg->flags));
	printf("\n");

	/* recurse into the rings */
	printf("\n");
	for (ring = 0; ring < HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS; ring++) {
		printf("%sring_config[%d]:\n", _tabs(depth), ring);
		_pretty_print_ring(depth+1, &cfg->ring_config[ring]);
	}
}


/** json -> config conversion **/
static uint64_t _sku2flags(const struct fun_json *sku)
{
	uint64_t flags = 0;
	bool no_phys = false;

	assert(fun_json_is_dict(sku));
	
	/* check for no_phys */
	no_phys = fun_json_lookup_bool_default(sku, "no_phys", false);

	if (no_phys)
		flags |= HW_HSU_API_LINK_CONFIG_FLAGS_NO_PHYS;
	
	/* host order*/
	return flags;
}

static uint32_t _args_as_ring(const struct fun_json *chu)
{
	int64_t value = 0;
	
	assert(fun_json_is_dict(chu));

	if (!fun_json_lookup_int64(chu, "_args/0", &value)) {
		printf("lookup fail\n");
		return HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS;
	}

	if (value > HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS) {
		value = HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS;
	}

	return value;
}

static bool _args_as_ring_pair(const struct fun_json *chu,
			       uint32_t *ring, uint32_t *cid)
{
	int64_t value = 0;

	assert(fun_json_is_dict(chu));
	assert(ring != NULL);
	assert(cid != NULL);

	if (!fun_json_lookup_int64(chu, "_args/0", &value)) {
		return false;
	}

	if (value >= HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS) {
		return false;
	}

	*ring = value;

	if (!fun_json_lookup_int64(chu, "_args/1", &value)) {
		return false;
	}

	if (value >= HW_HSU_API_LINK_CONFIG_V0_MAX_CIDS) {
		return false;
	}

	*cid = value;
	
	return true;
}

static bool _parse_hostunits(struct hw_hsu_api_link_config *cfg,
			     const struct fun_json *sku)
{
	int64_t hu_en = 0;
	uint64_t en = 0;
	int i = 0;

	/* just extract the one value */
	if (!fun_json_lookup_int64(sku,
				   "HuInterface/HostUnits/hu_en", &hu_en)) {
		return false;
	}

	/* set any rings as appropriate */
	en = htobe64(HW_HSU_API_LINK_CONFIG_RING_FLAGS_RING_ENABLED);

	for (i = 0; i < HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS; i++) {
		if ((hu_en & (1ULL<<i)) == 0)
			continue;
		cfg->ring_config[i].ring_flags |= en;
	}
	
	return true;
}

static bool _parse_hostunit(struct hw_hsu_api_link_config *cfg,
			    const struct fun_json *sku)
{
	const struct fun_json *hu = NULL, *chu = NULL;
	fun_json_index_t i = 0, count = 0;
	uint32_t ring = 0, cid = 0;
	int64_t ctl_en = 0;
	uint64_t en = 0, bif = 0;
	const char *bif_mode = NULL;
	
	
	assert(fun_json_is_dict(sku));
	
	hu = fun_json_lookup(sku, "HuInterface/HostUnit");
	if (!fun_json_is_array(hu)) {
		eprintf("failed to find HostUnit table\n");
		return false;
	}

	/* iterate over each item */
	count = fun_json_array_count(hu);
	for (i = 0; i < count; i++) {
		/* lookup the item */
		chu = fun_json_array_at(hu, i);
		if (!fun_json_is_dict(chu)) {
			eprintf("invalid HostUnit array\n");
			return false;
		}

		/* extract the ring from _args array */
		ring = _args_as_ring(chu);
		if (ring >= HW_HSU_API_LINK_CONFIG_V0_MAX_RINGS) {
			/* most likely posix */
			continue;			
		}

		/* get the bif and en bits */
		if (!fun_json_lookup_string(chu, "bif_mode", &bif_mode)) {
			eprintf("bad bif mode\n");
			return false;
		}

		if (!__str2val(_bif_valtab, bif_mode, &bif)) {
			eprintf("bad bif value\n");
			return false;
		}
		
		if (!fun_json_lookup_int64(chu, "ctl_en", &ctl_en)) {
			eprintf("bad ctl_en\n");
			return false;
		}

		/* now we've extracted something from the json, we can 
		 * patch up the cfg
		 */
		cfg->ring_config[ring].bif = htobe32(bif);

		en = htobe64(HW_HSU_API_LINK_CONFIG_RING_FLAGS_RING_ENABLED);
		for (cid = 0; cid < HW_HSU_API_LINK_CONFIG_V0_MAX_CIDS; cid++) {
			if ((ctl_en & (1ULL << cid)) == 0)
				continue;
			cfg->ring_config[ring].cid_config[cid].cid_flags |= en;
		}
	}
	
	return true;
}

static bool _parse_hostunitcontroller(struct hw_hsu_api_link_config *cfg,
				      const struct fun_json *sku)
{
	const struct fun_json *huc = NULL, *chu = NULL;
	fun_json_index_t i = 0, count = 0;
	uint32_t ring = 0, cid = 0, pcie_gen = 0, pcie_width = 0;
	bool r = false;
	const char *str = NULL;
	uint64_t u64 = 0, en = 0;
	struct hw_hsu_cid_config *pcid = NULL;
	
	assert(fun_json_is_dict(sku));
	
	huc = fun_json_lookup(sku, "HuInterface/HostUnitController");
	if (!fun_json_is_array(huc)) {
		eprintf("failed to find HostUnitController table\n");
		return false;
	}

	/* iterate over each item */
	count = fun_json_array_count(huc);
	for (i = 0; i < count; i++) {
		/* lookup the item */
		chu = fun_json_array_at(huc, i);
		if (!fun_json_is_dict(chu)) {
			eprintf("invalid HostUnitController array\n");
			return false;
		}

		/* extract the ring from _args array */
		r = _args_as_ring_pair(chu, &ring, &cid);
		if (!r) {
			/* most likely posix, ignore it */
			continue;		
		}

		/* take a direct pointer */
		pcid = &cfg->ring_config[ring].cid_config[cid];
		
		/* embed Port Type */
		if (fun_json_lookup_string(chu, "mode", &str)) {
			unsigned int porttype = 0;
			if (strcmp(str, "EP") == 0)
				porttype = HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_EP;
			else if (strcmp(str, "RC") == 0)
				porttype = HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_RC;
			else if (strcmp(str, "UPSW") == 0)
				porttype = HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_UPSW;
			else if (strcmp(str, "DNSW") == 0)
				porttype = HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_DNSW;
			else
				fprintf(stderr, "ERROR: (%u:%u) unknown 'mode'=%s",
				       ring, cid, str);
			pcid->cid_flags |=
				htobe64(HW_HSU_API_LINK_CONFIG_CID_FLAGS_PORTTYPE_PUT(porttype));
		} else
			fprintf(stderr,
				"WARNING: (%u:%u) Controller 'mode' not found!",
				ring, cid);

		/* check for link on/off */
		if (fun_json_lookup_string(chu, "link", &str)) {
			en = HW_HSU_API_LINK_CONFIG_CID_FLAGS_LINK_ENABLE;
			en = htobe64(en);
			if (strcmp(str, "ON") == 0) {
				pcid->cid_flags |= en;
			}
		}

		/* check for sris on/off */
		if (fun_json_lookup_string(chu, "sris", &str)) {
			en = HW_HSU_API_LINK_CONFIG_CID_FLAGS_SRIS_ENABLE;
			en = htobe64(en);
			if (strcmp(str, "ON") == 0) {
				pcid->cid_flags |= en;
			}
		}
		
		/* pcie_gen */
		pcie_gen = HW_HSU_API_LINK_CONFIG_PCIE_GEN_DEFAULT;
		if (fun_json_lookup_string(chu, "pcie_gen", &str)) {
			if (!__str2val(_gen_valtab, str, &u64)) {
				eprintf("bad pcie_gen value\n");
				return false;
			}
			pcie_gen = u64;
		}
		pcid->pcie_gen = htobe32(pcie_gen);

		/* pcie_width */
		pcie_width = HW_HSU_API_LINK_CONFIG_PCIE_WIDTH_DEFAULT;
		if (fun_json_lookup_string(chu, "pcie_width", &str)) {
			if (!__str2val(_width_valtab, str, &u64)) {
				eprintf("bad pcie_width value\n");
				return false;
			}
			pcie_width = u64;
		}
		pcid->pcie_width = htobe32(pcie_width);		
	}

	return true;
}

static bool _parse_boardinit(struct hw_hsu_api_link_config *cfg,
			    const struct fun_json *sku)
{
	const struct fun_json *board = NULL;

	assert(fun_json_is_dict(sku));

	memset(&cfg->board_config, 0xff, sizeof(cfg->board_config));

	board = fun_json_lookup(sku, "HuInterface/BoardInit");
	if (!fun_json_is_dict(board)) {
		/* no board init, it's optional so it's ok */
		return true;
	}

	/* Currently our chips have a maximum of 16 gpios (0..15) */
	if (!fun_json_lookup_uint8_default(board, "gpio", &cfg->board_config.gpio_id, 0xff) ||
		(cfg->board_config.gpio_id > 15)) {
		eprintf("Invalid BoardInit/gpio value\n");
		return false;
	}

	if (!fun_json_lookup_uint8_default(board, "pre-link-init", &cfg->board_config.gpio_pre_init_val, 0xff) ||
		(cfg->board_config.gpio_pre_init_val > 1)) {
		eprintf("Invalid BoardInit/pre-link-init value\n");
		return false;
	}

	if (!fun_json_lookup_uint8_default(board, "post-link-init", &cfg->board_config.gpio_post_init_val, 0xff) ||
		(cfg->board_config.gpio_post_init_val > 1)) {
		eprintf("Invalid BoardInit/post-link-init value\n");
		return false;
	}

	return true;
}

static bool _sku2cfg(struct hw_hsu_api_link_config *cfg,
		     const struct fun_json *sku)
{
	assert(cfg != NULL);
	assert(sku != NULL);

	/* clear the config with junk so we don't  */
	memset(cfg, 0, sizeof(*cfg));
	
	/* check the input is at least semi-valid */
	if (!fun_json_is_dict(sku))
		return false;	

	/* boilerplate */
	cfg->magic = htobe64(HW_HSU_API_LINK_CONFIG_MAGIC);
	cfg->version = htobe32(HW_HSU_API_LINK_CONFIG_VERSION_V1);

	/* this is redundant since it's implicit at install time. keep
	 * it zero
	 */
	cfg->sku_id = htobe32(0);
	
	/* nominally zero */
	cfg->id = htobe32(0);
	cfg->id_version = htobe32(0);

	/* scrape flags from the json */
	cfg->flags = htobe64(_sku2flags(sku));

	/* process the host units (hu_en) */
	if (!_parse_hostunits(cfg, sku))
		return false;

	/* process the host unit */
	if (!_parse_hostunit(cfg, sku))
		return false;

	/* process the host unit controller */
	if (!_parse_hostunitcontroller(cfg, sku))
		return false;

	if (!_parse_boardinit(cfg, sku))
		return false;

	return true;
}

/** config file reading and writing **/
static void _write_cfg_to_file(const char *outdir, const char *sku,
			       struct hw_hsu_api_link_config *cfg)
{
	int fd;
	ssize_t n;
	char fname[PATH_MAX+1];
	
	assert(outdir != NULL);
	assert(sku != NULL);
	assert(cfg != NULL);

	n = snprintf(fname, sizeof(fname), "%s/pcicfg-%s.bin", outdir, sku) < 0;
	if ((n < 0) || (n > sizeof(fname)))
		die("path name error");

	fd = open(fname, O_WRONLY|O_CREAT, 0644);
	if (fd < 0) {
		perror("open");
		exit(1);
	}

	n = write(fd, cfg, sizeof(*cfg));
	if (n != sizeof(*cfg))
		die("truncated write");
	close(fd);
	
	printf("\twritten to file %s\n", fname);
}

static void _handle_bin_input(const char *binfile)
{
	int fd = -1;
	ssize_t n = 0;
	struct hw_hsu_api_link_config cfg;
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

	printf("%s:\n", binfile);

	if (fstat(fd, &sbuf) != 0) {
		perror("fstat");
		exit(1);
	}

	if (sbuf.st_size != sizeof(cfg)) {
		eprintf("WARNING: file is incorrect size (%zu != %zu)\n",
			(size_t) sbuf.st_size, sizeof(cfg));
	}
	
	n = read(fd, &cfg, sizeof(cfg));
	if (n < sizeof(cfg))
		die("short read");
	close(fd);

	_pretty_print_cfg(1, &cfg);
	
	/* return to previous value */
	_verbose--;
}


/** json reading **/
static char *_read_input_file(int fd, size_t *outsize)
{
	char *buffer;
	char *pp;
	ssize_t n;
	size_t alloc_size, size = 0;

	alloc_size = (1024 * 1024);
	buffer = malloc(alloc_size);
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
	struct fun_json *input = NULL;
	char *buf;
	size_t size = 0;
	bool parsed_all;

	buf = _read_input_file(fd, &size);
	assert(buf);
	
	input = fun_json_create_from_text_with_status(buf, &parsed_all);

	if (!parsed_all || size != strlen(buf)) {
		fun_json_release(input);
		input = fun_json_create_error("JSON terminated earlier than the end of file", fun_json_no_copy_no_own);
	}

	free(buf);
	return input;
}

static struct fun_json *_read_bjson(int fd)
{
	struct fun_json *input = NULL;
	char *buf;
	size_t size;

	buf = _read_input_file(fd, &size);
	assert(buf);
	
	input = fun_json_create_from_binary((uint8_t*)buf, size);

	free(buf);
	return input;
}
	

static void _handle_json_input(int inmode, const char *infile,
			       const char *outdir, const char *sku_filter)
{
	/* iterate over the SKUs */
	const struct fun_json *skus = NULL, *sku = NULL;
	const char *key = NULL;
	uint64_t iter;
	struct hw_hsu_api_link_config cfg;
	bool b;
	int infd;

	/* open input file */
	if (strcmp(infile, "-") == 0) {
		if (inmode == BINARY) {
			fprintf(stderr, "not reading binary from stdin\n");
			exit(1);
		}
		infd = STDIN_FILENO;
	} else {
		infd = open(infile, O_RDONLY);
		if (infd < 0) {
			perror("open input");
			exit(1);
		}
	}

	/* read in some json */
	struct fun_json *input = NULL;
	if (inmode == TEXT)
		input = _read_json(infd);
	else
		input = _read_bjson(infd);

	if (!input) {
		fprintf(stderr, "failed to read a JSON\n");
		exit(1);
	}

	if (fun_json_is_error_message(input)) {
		const char *message;
		fun_json_fill_error_message(input, &message);
		fprintf(stderr, "%s\n", message);
		exit(1);
	}

	/* 1) lookup SKUs */
	skus = fun_json_lookup(input, "skus");
	if (!fun_json_is_dict(skus)) {
		fprintf(stderr, "failed to find skus table in input json\n");
		exit(1);
	}
	
	/* 2) iterate over SKUs */
	iter = fun_json_dict_iterator(skus);

	while (fun_json_dict_iterate(skus, &iter, &key, &sku)) {
		if ((sku_filter != NULL)
		    && (strcmp(sku_filter, key) != 0)) {
			printf("igoring sku %s\n", key);
			continue;
		}
		printf("found sku %s\n", key);
		b = _sku2cfg(&cfg, sku);

		if (!b) {
			eprintf("\tFailed to parse sku correctly, ignoring\n");
			continue;
		}

		/* dump it */
		if (_verbose > 0) {
			printf("\tEncoded SKU config:\n");
			_pretty_print_cfg(1, &cfg);
		}

		/* write to a path if it exists */
		if (outdir != NULL) {
			_write_cfg_to_file(outdir, key, &cfg);
		}
	}

	fun_json_release(input);
}

static int
_setmode(int curmode, int newmode)
{
	if (curmode != NOMODE) {
		fprintf(stderr, "can only specify one input or output file\n");
		exit(1);
	}

	return newmode;
}

static void
_usage(const char *fname)
{
	fprintf(stderr, "usage: %s -i <input.json> [-o <outdir>] [-s <sku>] [-v[v]]\n",
		fname);
	fprintf(stderr, "usage: %s -I <input.bjson> [-o <outdir>] [-s <sku>] [-v[v]]\n",
		fname);
	fprintf(stderr, "usage: %s -p <input.bin> [-v]\n",
		fname);
	fprintf(stderr, "    options\n");
	fprintf(stderr, "        -i <file>      input <file> as text json\n");
	fprintf(stderr, "        -I <file>      input <file> as binary json\n");
	fprintf(stderr, "        -p <file>      pretty print  <file> from raw pcicfg.bin format\n");
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
	char *sku_filter = NULL;
	
	while (1) {
		static struct option long_options[] = {
			{"in",    required_argument, 0,  'i' },
			{"out",   required_argument, 0,  'o' },
			{"inb",   required_argument, 0,  'I' },
			{"outb",  required_argument, 0,  'O' },
			{"sku",   required_argument, 0,  's' },
			{"print", required_argument, 0,  'p' },
			{NULL,    no_argument,       0,  'v' },
		};

		
		c = getopt_long(argc, argv, "i:o:l:I:O:vs:p:",
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
			binfile = optarg;
			break;
		case 'v':
			_verbose++;
			break;
		case 's':
			sku_filter = optarg;
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
		_handle_json_input(inmode, infile, outdir, sku_filter);
		
	}
	
	if (binfile != NULL) {
		_handle_bin_input(binfile);	
	}
	
	return r;
}

