# Makefile for Fungible header generator.


SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory where we install the working version.
FIPSTOOLS_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/fips_tools

all:

# install to SDK
install:
	mkdir -p $(FIPSTOOLS_INSTALL_DIR)
	rsync -aRr cavp.py trng.py $(FIPSTOOLS_INSTALL_DIR)

clean:
