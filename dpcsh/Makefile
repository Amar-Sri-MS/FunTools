
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

MACHINE ?= $(shell uname -m)

ifeq ($(MACHINE),x86_64)
 TOOLCHAIN_PREFIX :=
 SDK_LIB_SUBDIR := noasan
 SDK_INSTALL_PREFIX :=
else ifeq ($(MACHINE),arm64)
 TOOLCHAIN_PREFIX :=
 SDK_LIB_SUBDIR := noasan
 SDK_INSTALL_PREFIX :=
else ifeq ($(MACHINE),aarch64)
 TOOLCHAIN_PREFIX := aarch64-linux-gnu-
 SDK_LIB_SUBDIR :=
 SDK_INSTALL_PREFIX := aarch64
else ifeq ($(MACHINE),mips64)
 SDK_LIB_SUBDIR :=
 SDK_INSTALL_PREFIX := mips64
else
 $(error Unknown machine type $(MACHINE))
endif

BUILD_ROOT ?= build_$(MACHINE)

BUILD_INFO_SDK       := $(SDKDIR)/build_info.txt
BUILD_INFO_WORKSPACE := $(SDKDIR)/../build_info.txt

# To track version, see if there's a build info in the workspace
# (ie. in Jenkins) otherwise, pull it out of FunSDK. If that doesn't
# work, make it up
ifneq (,$(wildcard $(BUILD_INFO_SDK)))
version := bld_$(shell cat $(BUILD_INFO_SDK))
else ifneq (,$(wildcard $(BUILD_INFO_WORKSPACE)))
version := bld_$(shell cat $(BUILD_INFO_WORKSPACE))
else
version := $(shell git describe --always --dirty=*)
endif
branch := $(shell git rev-parse --short HEAD)

VER     = -DVER=$(version)
BRANCH  = -DBRANCH=$(branch)

ifeq ($(MACHINE),mips64)
WITH_LIBFUNQ = 1
endif

ifneq ($(WITH_LIBFUNQ),)

ifeq ($(MACHINE),x86_64)
LFUNQ_PATH = $(SDKDIR)/FunSDK/host-drivers/$(MACHINE)/user/posix
else
LFUNQ_PATH = $(SDKDIR)/FunSDK/host-drivers/$(MACHINE)/user/native
endif

CFLAGS += -I $(LFUNQ_PATH)/include -DWITH_LIBFUNQ
LDFLAGS += -L $(LFUNQ_PATH)/lib -lbin_ctl -lfunq
endif

# define header and library location in FunSDK
CFLAGS += -I $(SDKDIR) -I $(SDKDIR)/FunSDK/funosrt/include -g -Wall -Werror -Wno-multichar $(BRANCH) $(VER)

# XXX: compatibility with FunOS build parameters
#LDFLAGS += -L $(SDKDIR)/lib/${OS}/x86_64 -lfunclient -fsanitize=address
LDFLAGS += -lpthread -L $(SDKDIR)/lib/$(OS)/$(SDK_LIB_SUBDIR)/$(MACHINE) -lfunclient -ldl

SRCS = dpcsh.c dpcsh_nvme.c dpcsh_macros.c csr_command.c file_commands.c dpcsh_log.c dpcsh_ptr_queue.c
OBJS = $(addprefix $(BUILD_ROOT)/,$(SRCS:.c=.o))

# Deal with gcc versioning for ASAN
ifneq ($(TOOLCHAIN_PREFIX),)
CC := $(TOOLCHAIN_PREFIX)gcc$(GCC_SUFFIX)
endif

# default target goes first
all: dpcsh

$(BUILD_ROOT):
	mkdir -p $@

$(BUILD_ROOT)/%.o: %.c $(DEPS) | $(BUILD_ROOT)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: dpcsh
dpcsh: $(BUILD_ROOT)/dpcsh

$(BUILD_ROOT)/dpcsh: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

DPC_INSTALL_TARGET_DIR := $(SDK_INSTALL_DIR)/bin/$(SDK_INSTALL_PREFIX)/$(OS)

$(DPC_INSTALL_TARGET_DIR):
	mkdir -p $@

.PHONY: install install-scripts

install-scripts: | $(DPC_INSTALL_TARGET_DIR)
	cp dpc_client.py dpctest.py dpc_binary.py dpc_utils.py binary_json.py dpc_uboot_env.py auth_firmware.py $(DPC_INSTALL_TARGET_DIR)


install: dpcsh install-scripts | $(DPC_INSTALL_TARGET_DIR)
	install $(BUILD_ROOT)/dpcsh $(DPC_INSTALL_TARGET_DIR)
ifeq ($(MACHINE),aarch64)
	mkdir -p ${SDK_INSTALL_DIR}/bin/scripts
	cp deploy_dpcsh_aarch64.sh ${SDK_INSTALL_DIR}/bin/scripts
endif

install-libfunq: dpcsh install-scripts | $(DPC_INSTALL_TARGET_DIR)
	install $(BUILD_ROOT)/dpcsh $(DPC_INSTALL_TARGET_DIR)/dpcsh.libfunq

.PHONY: install-init.d
install-init.d: | $(DPC_INSTALL_TARGET_DIR)
	cp -R init.d $(SDK_INSTALL_DIR)/bin/$(SDK_INSTALL_PREFIX)/$(OS)

clean:
	-rm -rf $(BUILD_ROOT) build_*
