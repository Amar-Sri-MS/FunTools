
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

MACHINE ?= $(shell uname -m)

ifeq ($(MACHINE),x86_64)
 SDK_LIB_SUBDIR := noasan
 SDK_INSTALL_PREFIX :=
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

ifeq ($(MACHINE),x86_64)
LFUNQ_PATH = $(SDKDIR)/FunSDK/host-drivers/$(MACHINE)/user/posix
else
LFUNQ_PATH = $(SDKDIR)/FunSDK/host-drivers/$(MACHINE)/user/native
endif

CFLAGS += -I $(LFUNQ_PATH)/include -DWITH_LIBFUNQ
LDFLAGS += -L $(LFUNQ_PATH)/lib -lbin_ctl -lfunq

# define header and library location in FunSDK
CFLAGS += -I $(SDKDIR) -I $(SDKDIR)/FunSDK -g -Wall -Werror -Wno-multichar $(BRANCH) $(VER)

# XXX: compatibility with FunOS build parameters
#LDFLAGS += -L $(SDKDIR)/lib/${OS}/x86_64 -lfunclient -fsanitize=address
LDFLAGS += -lpthread -L $(SDKDIR)/lib/$(OS)/$(SDK_LIB_SUBDIR)/$(MACHINE) -lfunclient -ldl

SRCS = bin_ctl_sample.c
OBJS = $(addprefix $(BUILD_ROOT)/,$(SRCS:.c=.o))

# default target goes first
all: bin_ctl_sample

$(BUILD_ROOT):
	mkdir -p $@

$(BUILD_ROOT)/%.o: %.c $(DEPS) | $(BUILD_ROOT)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: bin_ctl_sample
bin_ctl_sample: $(BUILD_ROOT)/bin_ctl_sample

$(BUILD_ROOT)/bin_ctl_sample: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	-rm -rf $(BUILD_ROOT) build_*
