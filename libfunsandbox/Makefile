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
NM := $(TOOL_PREFIX)nm
STRIP := $(TOOL_PREFIX)strip
OBJCOPY := $(TOOL_PREFIX)objcopy

CC_ENDIANNESS := -EB
LD_ENDIANNESS := -m elf64btsmip

CFLAGS := -mips64r6 $(CC_ENDIANNESS) -mabi=64 -nostdlib -nostdinc
CFLAGS += -mno-abicalls -fno-pic -G8 -membedded-data
CFLAGS += -O2
# Do not allow builtins which may try to recursively call into pdclib itself.
CFLAGS += -fno-builtin 

# LDFLAGS += -ggdb2
LDFLAGS += $(LD_ENDIANNESS) -Ttext=0x100000

STRIP_FLAGS += -s

SDKDIR ?= ../../FunSDK

# CFLAGS += -I $(SDKDIR)/platform/mips64/include
CFLAGS += -I $(TOOL_ROOT)/lib/gcc/mips64-unknown-elf/8/include

### End FunOS toolchain defines

all: funsandbox

%.o: %.c
	@echo CC $^
	$(CC) -o $@ $(CFLAGS) -ggdb2 -c $^


funsandbox: funsandbox.o
	$(LD) -o $@ $(LDFLAGS) $^
	$(STRIP) $@ -o $@.stripped
	$(OBJCOPY) -O binary --only-section=.text $@.stripped $@.bin
	$(NM) $@ > $@.syms

dpc: funsandbox
	@echo Making DPC transactions
	./mkdpc.py libfunsandbox funsandbox.bin funsandbox.syms

clean:
	rm -f funsandbox
	rm -f *.o
