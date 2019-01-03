# Makefile for Fungible header generator.


SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory where we install the working version.
SBUS_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/sbus

all:

# install to SDK
install:
	mkdir -p $(SBUS_INSTALL_DIR)
	rsync -Rr --exclude=Makefile . $(SBUS_INSTALL_DIR)

clean:

