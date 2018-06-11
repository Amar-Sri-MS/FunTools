# Makefile for Stats Code Generation.

# Build platform OS
OS := $(shell uname)

# The build is where our SDK is rooted
SDKDIR ?= ../../FunSDK

# Where install files go
SDK_INSTALL_DIR ?= $(SDKDIR)

# The FunOS dir where config files reside
FUNOSDIR ?= ../../FunOS

# Directory to install working version of the StatsGen
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/StatsGen

SRC = *.py templates
INPUT_DIR = $(FUNOSDIR)/Configfiles/stats
OUTPUT_DIR = /tmp/generated
CSR_METADATA_DIR = $(SDKDIR)/FunSDK/config/csr/

test_stats_gen:
	mkdir -p $(OUTPUT_DIR)
	./hw_stats_gen.py -c $(INPUT_DIR) -o $(OUTPUT_DIR) -m $(CSR_METADATA_DIR)

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	mkdir -p $(FUNSDK_INSTALL_DIR)/templates
	rsync -rR $(SRC) $(FUNSDK_INSTALL_DIR)
clean:
	@rm -rf $(OUTPUT_DIR)
