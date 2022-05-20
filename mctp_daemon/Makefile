QUIET ?= 1

ifeq ($(QUIET),1)
 QUIET_CPP   = @echo '  ' CCP'   '$(notdir $<);
 QUIET_CC    = @echo '  ' CC'    '$(notdir $<);
 QUIET_AS    = @echo '  ' AS'    '$(notdir $<);
 QUIET_RM    = @echo '  ' RM'    '$(notdir $<);
 QUIET_LD    = @echo '  ' LD'    '$@;
 QUIET_SIZE  = @echo '  ' SIZE'  '$@;
 QUIET_NM    = @echo '  ' NM'    '$@;
 QUIET_DUMP  = @echo '  ' DUMP'  '$@;
 QUIET_CP    = @echo '  ' CP'    '$@;
 QUIET_MKDIR = @echo '  ' MKDIR' '$@;
 Q          = @
 VERBOSE_AR =
endif

MACHINE ?= mips64

ifeq ($(MACHINE),x86_64)
 TOOLCHAIN_PREFIX :=
 SDK_LIB_SUBDIR := noasan
 SDK_INSTALL_PREFIX :=
else ifeq ($(MACHINE),mips64)
 SDK_LIB_SUBDIR :=
 SDK_INSTALL_PREFIX := mips64
 ARCH_BIG_ENDIAN=y
ifeq ($(PRIVATE_BUILD),y)
 SDKTARGETSYSROOT=/opt/poky/3.0.2/sysroots/mipsisa64r6-poky-linux
 PATH:=$(PATH):/opt/poky/3.0.2/sysroots/x86_64-pokysdk-linux/usr/bin/mipsisa64r6-poky-linux:/opt/poky/3.0.2/sysroots/x86_64-pokysdk-linux/usr/bin/mipsisa64r6-poky-linux-musl
 CC=mipsisa64r6-poky-linux-gcc  -meb -mabi=64 -mhard-float -march=mips64r6 --sysroot=$(SDKTARGETSYSROOT)
 CXX=mipsisa64r6-poky-linux-g++  -meb -mabi=64 -mhard-float -march=mips64r6 --sysroot=$(SDKTARGETSYSROOT)
 CPP=mipsisa64r6-poky-linux-gcc -E  -meb -mabi=64 -mhard-float -march=mips64r6 --sysroot=$(SDKTARGETSYSROOT)
 AS=mipsisa64r6-poky-linux-as 
 LD=mipsisa64r6-poky-linux-ld  --sysroot=$(SDKTARGETSYSROOT)
 CFLAGS=-O2 -pipe -g -feliminate-unused-debug-types
 CXXFLAGS=-O2 -pipe -g -feliminate-unused-debug-types
 LDFLAGS=-Wl,-O1  -Wl,--as-needed
 CPPFLAGS=""
 ARCH=mips
endif
else
 $(error Unknown machine type $(MACHINE))
endif

BUILD_ROOT ?= build_$(MACHINE)
SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)/bin

ifeq ($(ARCH_BIG_ENDIAN),y)
CFLAGS += -DARCH_BIG_ENDIAN
endif

# define header and library location in FunSDK
CFLAGS += -I./ -I./include -I./$(BUILD_ROOT) -g -Wall -Werror -Wno-multichar 

SRCS = smbus.c pcie_vdm.c utils.c pldm.c pldm_mcd.c pldm_pmc.c pldm_fru.c ncsi.c ncsi_cmds.c dell.c mctp.c mctp_daemon.c main_loop.c
OBJS = $(addprefix $(BUILD_ROOT)/,$(SRCS:.c=.o))

MCTP_CONFIG ?= .config
MCTP_DAEMON_INSTALL_DIR ?= ${MACHINE}/Linux/mctp_daemon

export MCTP_CONFIG

.PHONY: FORCE version all install clean

all: $(BUILD_ROOT)/mctp_daemon

$(BUILD_ROOT): FORCE
	$(QUIET_MKDIR)mkdir -p $@

version: FORCE
	$(Q)./update.sh -p $(BUILD_ROOT)

$(BUILD_ROOT)/auto_conf.h: $(MCTP_CONFIG)
	$(Q)./gen_auto_conf.sh -p $(BUILD_ROOT)

$(BUILD_ROOT)/pldm_repo.h: FORCE
	$(Q)echo "#ifndef _INC_PLDM_REPO_HDR_" > $@
	$(Q)echo "#define _INC_PLDM_REPO_HDR_" >> $@
	$(Q)echo "#define REPO_BUILD_SEC            `date +%-S`" >> $@
	$(Q)echo "#define REPO_BUILD_MIN            `date +%-M`" >> $@
	$(Q)echo "#define REPO_BUILD_HOUR           `date +%-H`" >> $@
	$(Q)echo "#define REPO_BUILD_DAY            `date +%-d`" >> $@
	$(Q)echo "#define REPO_BUILD_MONTH          `date +%-m`" >> $@
	$(Q)echo "#define REPO_BUILD_YEAR           `date +%-Y`" >> $@
	$(Q)echo "#define REPO_BUILD_TZ             `date +%-z`" >> $@
	$(Q)echo "struct pldm_timestamp oem_update = {REPO_BUILD_TZ, REPO_BUILD_SEC, REPO_BUILD_MIN, REPO_BUILD_HOUR, REPO_BUILD_DAY, REPO_BUILD_MONTH, REPO_BUILD_YEAR, 1};" >> $@
	$(Q)echo "const struct pldm_timestamp repo_update = {REPO_BUILD_TZ, REPO_BUILD_SEC, REPO_BUILD_MIN, REPO_BUILD_HOUR, REPO_BUILD_DAY, REPO_BUILD_MONTH, REPO_BUILD_YEAR, 1};" >> $@
	$(Q)echo "#endif /* _INC_PLDM_REPO_HDR_ */" >> $@


$(BUILD_ROOT)/mctp_daemon: $(BUILD_ROOT) $(BUILD_ROOT)/auto_conf.h $(BUILD_ROOT)/pldm_repo.h version $(OBJS)
	$(QUIET_LD)$(CC) -o $@ $(OBJS) 

$(BUILD_ROOT)/%.o: %.c 
	$(QUIET_CC)$(CC) -c -o $@ $< $(CFLAGS)

install: $(BUILD_ROOT)/mctp_daemon
	@echo "Installing mctp_daemon.$(MACHINE) @ $(SDK_INSTALL_DIR)"
	@for dir in usr/bin etc; do mkdir -p $(SDK_INSTALL_DIR)/$(MCTP_DAEMON_INSTALL_DIR)/$$dir; done
	@cp -f $< $(SDK_INSTALL_DIR)/$(MCTP_DAEMON_INSTALL_DIR)/usr/bin/
	@cp -fr init.d $(SDK_INSTALL_DIR)/$(MCTP_DAEMON_INSTALL_DIR)/etc/
	@cp -f mctp_tmp_agent.sh $(SDK_INSTALL_DIR)/$(MCTP_DAEMON_INSTALL_DIR)/usr/bin/
	@cp -f mctp_transport.py $(SDK_INSTALL_DIR)/$(MCTP_DAEMON_INSTALL_DIR)/usr/bin/

clean:
	$(Q)rm -rf $(BUILD_ROOT)

FORCE:
