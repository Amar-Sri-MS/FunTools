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

# Directory where we install the working version of the StatsGen
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/StatsGen

SRC = *.py

#test_stats_gen:
#	./$(SRC) -i $(INPUT_DIR) -o $(OUTPUT_DIR) -s $(SDKDIR)

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -R $(SRC) $(FUNSDK_INSTALL_DIR)
clean:
	@rm -rf out
