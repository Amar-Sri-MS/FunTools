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

# Directory where the *.cfg file is stored.
INPUT_DIR = $(FUNOSDIR)/Configfiles

#Local output dir
OUTPUT_DIR = out/

#Generated hwcap files output dir
HWCAP_OUT_DIR = $(OUTPUT_DIR)

#json util dir
JSONUTIL_DIR = $(SDKDIR)/bin/$(OS)/x86_64

SRC = cfg_gen.py csr_db_gen.py hu_cfg_gen.py
CFGGEN_PY := ./cfg_gen.py
TEST_HU_CFG_SH := ./test_hu_cfg.sh

QUIET=@
CMD_LOG := cmd.log

# Test Diretory for generated files
GEN_OUT_DIR:= generated

test_cfggen:
	./$(SRC) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -j $(JSONUTIL_DIR)
	./$(SRC) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -s $(HWCAP_OUT_DIR) -j $(JSONUTIL_DIR)

test_hucfggen:
	$(QUIET)mkdir -p $(GEN_OUT_DIR)
	@echo  "$(CFGGEN_PY) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -j -s $(GEN_OUT_DIR) -c" >>$(CMD_LOG)
	$(QUIET)$(CFGGEN_PY) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -j -s $(GEN_OUT_DIR) -c
	@echo  "cd test; $(TEST_HU_CFG_SH)" >> $(CMD_LOG)
	$(QUIET)cd test; $(TEST_HU_CFG_SH)

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -R $(SRC) $(FUNSDK_INSTALL_DIR)
clean:
	@rm -rf out
	@rm -rf $(GEN_OUT_DIR)
