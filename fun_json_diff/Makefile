# Makefile for Stats Code Generation.

# Build platform OS
OS := $(shell uname)

# The build is where our SDK is rooted
SDKDIR ?= ../../FunSDK

# install path
SDK_INSTALL_DIR ?= SDKDIR

# The FunOS dir where config files reside
FUNOSDIR ?= ../../FunOS

MACHINE ?= $(shell uname -m)

ifeq ($(MACHINE),x86_64)
 SDK_LIB_SUBDIR := noasan
else ifeq ($(MACHINE),arm64)
 SDK_LIB_SUBDIR := noasan
else ifeq ($(MACHINE),arm)
 SDK_LIB_SUBDIR :=
else ifeq ($(MACHINE),mips64)
 SDK_LIB_SUBDIR :=
else
 $(error Unknown machine type $(MACHINE))
endif

CHIP = f1

BUILD_ROOT ?= build_$(MACHINE)

CFLAGS += -I $(SDKDIR)  -I $(SDKDIR)/FunSDK/funosrt/include/FunOS/platform/include -I $(SDKDIR)/FunSDK/chip/$(CHIP)/include -I $(SDKDIR)/FunSDK/funosrt/include -g -Wall -Werror -Wno-multichar  -DPLATFORM_POSIX -D_XOPEN_SOURCE

LDFLAGS += -L $(SDKDIR)/lib/$(OS)/$(SDK_LIB_SUBDIR)/$(MACHINE) -lfunclient

SRCS = fun_json_diff.c
OBJS = $(addprefix $(BUILD_ROOT)/,$(SRCS:.c=.o))

# default target goes first
all: fun_json_diff

$(BUILD_ROOT):
	mkdir -p $@

$(BUILD_ROOT)/%.o: %.c $(DEPS) | $(BUILD_ROOT)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: fun_json_diff
fun_json_diff: $(BUILD_ROOT)/fun_json_diff

$(BUILD_ROOT)/fun_json_diff: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

.PHONY: install
install: fun_json_diff
	mkdir -p $(SDKDIR)/bin/$(MACHINE)/$(OS)
	cp $(BUILD_ROOT)/fun_json_diff $(SDK_INSTALL_DIR)/bin/$(MACHINE)/$(OS)

clean:
	-rm -rf build_*
