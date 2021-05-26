# Makefile for dpc_cli

# Build platform OS
OS := $(shell uname)

# The build is where our SDK is rooted
SDKDIR ?= ../../FunSDK

# Where install files go
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory to install working version of dpc_cli
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/dpc_cli

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -rR . $(FUNSDK_INSTALL_DIR)

