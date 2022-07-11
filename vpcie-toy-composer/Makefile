# vpcie-toy-composer Makefile
#

###
##   The build is where our SDK is rooted
#
SDKDIR ?= ../../FunSDK

###
##   Where install files go
#
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory where we install vpcie-toy-composer
#
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin

.PHONY: test
test:
	@echo "Nothing to do"

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	install vpcie-toy-composer $(FUNSDK_INSTALL_DIR)

clean:

