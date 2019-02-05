##
##  Makefile
##
##  Created by Charles Gray on 2019-02-05.
##  Copyright (c) 2019 Fungible. All rights reserved.
##

# build libfunsandbox for mips64


### Begin FunOS toolchain defines

# OS
OS := $(shell uname)

ifeq ($(OS),Darwin)
	TOOL_ROOT := /Users/Shared/cross/mips64
else
ifeq ($(OS),Linux)
	TOOL_ROOT := /opt/cross/mips64
endif
endif

TOOL_PREFIX  := $(TOOL_ROOT)/bin/mips64-unknown-elf-

CC := $(TOOL_PREFIX)gcc
AR := $(TOOL_PREFIX)gcc-ar
LD := $(TOOL_PREFIX)ld

ifneq ($(ENDIAN),little)
# strongly support big endian, unless otherwise specified
CC_ENDIANNESS := -EB
else
CC_ENDIANNESS := -EL
endif

CFLAGS := -mips64r6 $(CC_ENDIANNESS) -mabi=64 -nostdlib -nostdinc
CFLAGS += -G 8 -mno-abicalls -fno-pic
CFLAGS += -O3
# Do not allow builtins which may try to recursively call into pdclib itself.
CFLAGS += -fno-builtin

# LDFLAGS += -ggdb2
STRIP_FLAGS += -s

SDKDIR ?= ../../FunSDK

# CFLAGS += -I $(SDKDIR)/platform/mips64/include
CFLAGS += -D__STDC_HOSTED__=0
CFLAGS += -I $(TOOL_ROOT)/lib/gcc/mips64-unknown-elf/8/include

### End FunOS toolchain defines

all: funsandbox

%.o: %.c
	@echo CC $^
	$(CC) -o $@ $(CFLAGS) -ggdb2 -c $^


funsandbox: funsandbox.o
	$(LD) -o $@ $(LDFLAGS) $^
