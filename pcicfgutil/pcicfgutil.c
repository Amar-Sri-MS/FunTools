/*
 *  pcicfgutil.c
 *
 *  Created by Charles Gray on 2020-10-21.
 *  Copyright © 2020 Fungible. All rights reserved.
 */

/* utility to convert json config to SBP hw_hsu_api_link_config blobs */

#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <ctype.h>	// for fprintf()
#include <stdio.h>	// for fprintf()
#include <unistd.h>	// for STDOUT_FILENO
#include <stdlib.h>	// for free()
#include <getopt.h>	// for getopt_long()
#include <fcntl.h>	// for open()
#include <string.h>	// for strcmp()

#include <platform/mips64/include/endian.h> // this could be in a better location...

#include <FunSDK/config/include/boot_config.h>

// We must define PLATFORM_POSIX to get fun_json_write_to_fd()
#define PLATFORM_POSIX 1
#include <FunSDK/utils/threaded/fun_json.h>

#define NOMODE      (0)
#define TEXT        (1)
#define BINARY      (2)
#define TEXTONELINE (3)

#define eprintf(...) fprintf (stderr, __VA_ARGS__)
#define die(...) do { fprintf (stderr, __VA_ARGS__); exit(1); } while (0)

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
struct flagtab {
	const char *str;
	uint64_t flag;
};

/* global flags */
static struct flagtab _global_flagtab[] = {
	{"NO_PHYS", HW_HSU_API_LINK_CONFIG_FLAGS_NO_PHYS},

	/* must be last */
	{NULL, 0}
};

static struct flagtab _ring_flagtab[] = {
	{"ENABLED", HW_HSU_API_LINK_CONFIG_RING_FLAGS_RING_ENABLED},

	/* must be last */
	{NULL, 0}
};

static struct flagtab _cid_flagtab[] = {
	{"CID_ENABLED", HW_HSU_API_LINK_CONFIG_CID_FLAGS_CID_ENABLED},
	{"LINK_ENABLED", HW_HSU_API_LINK_CONFIG_CID_FLAGS_LINK_ENABLE},
	{"SRIS_ENABLED", HW_HSU_API_LINK_CONFIG_CID_FLAGS_SRIS_ENABLE},

	/* must be last */
	{NULL, 0}
};

static uint64_t __str2flag(struct flagtab *tab, const char *str)
{
	int i = 0;

	while (tab[i].str != NULL) {
		if(strcmp(str, tab[i].str) == 0) {
			/* found the flag */
			return tab[i].flag;
		}

		/* next */
		i++;
	}
	
	die("unknown flag: %s\n", str);
}

static uint64_t _str2flag(const char *str)
{
	return __str2flag(_global_flagtab, str);
}

static void __pretty_print_flags(struct flagtab *tab, uint64_t flags)
{
	uint64_t remflags = flags;
	bool sep = false;
	bool not = false;
	int i = 0;

	while (tab[i].str != NULL) {
		not = true;
		if((flags & tab[i].flag) == tab[i].flag) {
			/* found the flag */
			not = false;
			remflags ^= tab[i].flag;
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
	__pretty_print_flags(_cid_flagtab, flags);
}

static void _pretty_print_ring_flags(uint64_t flags)
{
	__pretty_print_flags(_ring_flagtab, flags);
}

/** config pretty-printer **/

void _pretty_print_cid(uint32_t depth, struct hw_hsu_cid_config *cid)
{
	/* flags */
	printf("%scid_flags: 0x%" PRIx64 " = ",
	       _tabs(depth), be64toh(cid->cid_flags));
	_pretty_print_cid_flags(be64toh(cid->cid_flags));
	printf("\n");

	/* pci values */
	printf("%spcie_gen: %u\n", _tabs(depth), be32toh(cid->pcie_gen));
	printf("%spcie_width: %u\n", _tabs(depth), be32toh(cid->pcie_width));
}

void _pretty_print_ring(uint32_t depth, struct hw_hsu_ring_config *ring)
{
	uint32_t cid = 0;
	
	printf("%sbif: %u\n", _tabs(depth), be32toh(ring->bif));

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
	_pretty_print_flags(cfg->flags);
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
	struct fun_json *jsflags = NULL, *jsstr = NULL;
	uint64_t flags = 0;
	fun_json_index_t i = 0, max = 0;

	assert(fun_json_is_dict(sku));
	
	/* find the sku */
	jsflags = fun_json_lookup(sku, "HuInterface/flags");
	if (!fun_json_is_array(jsflags)) {
		printf("\tsku is missing HU flags, setting to 0\n");
		return 0;
	}

	/* search all the flags */
	max = fun_json_array_count(jsflags);
	for (i = 0; i < max; i++) {
		jsstr = fun_json_array_at(jsflags, i);
		if (!fun_json_is_string(jsstr))
			die("unexpected non-string in HU flags");

		/* append the flag, or die trying */
		flags |= _str2flag(fun_json_to_string(jsstr, NULL));
	}

	return flags;
}

static bool _sku2cfg(struct hw_hsu_api_link_config *cfg,
		     const struct fun_json *sku)
{
	const struct fun_json *hu = NULL;

	assert(cfg != NULL);
	assert(sku != NULL);

	/* clear the config */
	bzero(cfg, sizeof(*cfg));
	
	/* check the input is at least semi-valid */
	if (!fun_json_is_dict(sku))
		return false;	

	/* boilerplate */
	cfg->magic = htobe64(HW_HSU_API_LINK_CONFIG_MAGIC);
	cfg->version = htobe32(HW_HSU_API_LINK_CONFIG_VERSION_V0);

	/* this is redundant since it's implicit at install time. keep
	 * it zero
	 */
	cfg->sku_id = htobe32(0);
	
	/* nominally zero */
	cfg->id = htobe32(0);
	cfg->id_version = htobe32(0);

	/* scrape flags from the json */
	cfg->flags = htobe64(_sku2flags(sku));
	
	/* start by clearing the cfg */
	hu = fun_json_lookup(sku, "HuInterface/HostUnit");
	if (!fun_json_is_array(hu)) {
		eprintf("failed to find HostUnit table\n");
		return false;
	}

	return true;
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
	fprintf(stderr, "usage: %s <input> [<output>]\n", fname);
	fprintf(stderr, "    options\n");
	fprintf(stderr, "        -i <file>      input <file> as text json\n");
	fprintf(stderr, "        -I <file>      input <file> as binary json\n");
	fprintf(stderr, "        -o <dir>       output files to <dir>\n");
	
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
	int infd;
	
	while (1) {
		static struct option long_options[] = {
			{"in",   required_argument, 0,  'i' },
			{"out",  required_argument, 0,  'o' },
			{"inb",  required_argument, 0,  'I' },
			{"outb", required_argument, 0,  'O' },
		};

		
		c = getopt_long(argc, argv, "i:o:l:I:O:",
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
		case '?':
		default:
			_usage(argv[0]);
		}
	}

	if (infile == NULL)
		_usage(argv[0]);

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
	} else
		fprintf(stderr, "read ok\n");

	if (fun_json_is_error_message(input)) {
		const char *message;
		fun_json_fill_error_message(input, &message);
		fprintf(stderr, "%s\n", message);
		exit(1);
	}

	/* iterate over the SKUs */
	const struct fun_json *skus = NULL, *sku = NULL;
	const char *key = NULL;
	uint64_t iter;
	struct hw_hsu_api_link_config cfg;
	bool b;

	/* 1) lookup SKUs */
	skus = fun_json_lookup(input, "skus");
	if (!fun_json_is_dict(skus)) {
		fprintf(stderr, "failed to find skus table in input json\n");
		exit(1);
	}
	
	/* 2) iterate over SKUs */
	iter = fun_json_dict_iterator(skus);

	while (fun_json_dict_iterate(skus, &iter, &key, &sku)) {
		printf("found sku %s\n", key);
		b = _sku2cfg(&cfg, sku);

		if (!b) {
			eprintf("\tFailed to parse sku correctly, ignoring\n");
		}

		/* dump it */
		printf("\tEncoded SKU config:\n");
		_pretty_print_cfg(1, &cfg);
	}

	/* 3) extract HuInterface */

	/* 4) process HuInterface! */
	

	fun_json_release(input);
	
	return r;
}
