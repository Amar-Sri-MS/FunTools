# Makefile for Fungible header generator.


SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory where we install the working version.
FLASHTOOLS_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/flash_tools

all:

# install to SDK
install:
	mkdir -p $(FLASHTOOLS_INSTALL_DIR)
	rsync -aRr --exclude=Makefile --exclude=__pycache__ . $(FLASHTOOLS_INSTALL_DIR)

clean:

