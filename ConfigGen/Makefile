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
##   The FunOS dir where config files reside
#
FUNOSDIR ?= ../../FunOS

# Directory where we install the working version of the ConfigGen
FUNSDK_INSTALL_DIR = $(SDKDIR)/bin/ConfigGen

# Directory where the *.cfg file is stored.
INPUT_DIR = $(FUNOSDIR)/Configfiles

HWCAP_OUT_DIR = $(FUNOSDIR)/Configfiles/

#Local output dir
OUTPUT_DIR = out/

#json util dir
JSONUTIL_DIR = $(SDKDIR)/bin/$(OS)/x86_64

SRC = cfg_gen.py

test_cfggen:
	./$(SRC) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -j $(JSONUTIL_DIR)
	./$(SRC) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -s $(HWCAP_OUT_DIR) -j $(JSONUTIL_DIR)

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -R $(SRC) $(FUNSDK_INSTALL_DIR)
clean:
	@rm -rf out
