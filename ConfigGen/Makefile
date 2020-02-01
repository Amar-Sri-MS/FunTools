# Makefile for Configgen.

###
##  Build platform OS
#

OS := $(shell uname)

###
##   The build is where our SDK is rooted
#
SDKDIR ?= ../../FunSDK

###
##   Where install files go
#
SDK_INSTALL_DIR ?= $(SDKDIR)

###
##   The FunOS dir where config files reside
#
FUNOSDIR ?= ../../FunOS

# Directory where we install the working version of the ConfigGen
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/ConfigGen

# Root directory of config files
INPUT_DIR = $(realpath $(FUNOSDIR)/configs)


CHIP ?= f1
TARGET_MACHINE ?= f1

#json util dir
JSONUTIL_DIR = $(SDKDIR)/bin/$(OS)/x86_64

CFGGEN_SRC :=	cfg_gen.py        \
		csr_db_gen.py     \
		hu_cfg_gen.py     \
		jsonutils.py      \
		sku_cfg_gen.py    \
		hwcap_cfg_gen.py  \
		nu_cfg_gen.py     \
		platform_sku_c.j2 \
		platform_sku_h.j2 \
		hwcap_config_c.j2 \
		hwcap_config_h.j2

CFGGEN_PY := ./cfg_gen.py
TEST_HU_CFG_SH := ./test_hu_cfg.sh

QUIET=@
CMD_LOG := cmd.log

# Test Diretory for generated files
THIS_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
GEN_OUT_DIR := $(THIS_DIR)/generated

.PHONY: test
test:
	@echo "mkdir -p $(GEN_OUT_DIR)" >> $(CMD_LOG)
	$(QUIET)mkdir -p $(GEN_OUT_DIR)
	@echo "$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --funoscfg" >> $(CMD_LOG)
	$(QUIET)$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --funoscfg
	@echo "$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --funoscfg" >> $(CMD_LOG)
	$(QUIET)$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --skucfg
	@echo "$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --eeprom" >> $(CMD_LOG)
	$(QUIET)$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --eeprom
	@echo "$(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --hucfg" >> $(CMD_LOG)
	$(QUIET) $(CFGGEN_PY) --in-dir $(INPUT_DIR) --out-dir $(GEN_OUT_DIR) --chip $(CHIP) --machine $(TARGET_MACHINE) --hucfg
	@echo "cd test; $(TEST_HU_CFG_SH) $(INPUT_DIR) $(GEN_OUT_DIR)" >> $(CMD_LOG)
	$(QUIET)cd test; $(TEST_HU_CFG_SH) $(INPUT_DIR) $(GEN_OUT_DIR)

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -R $(CFGGEN_SRC) $(FUNSDK_INSTALL_DIR)
clean:
	@rm -rf out
	@rm -rf $(GEN_OUT_DIR)
