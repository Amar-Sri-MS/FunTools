# Basic Makefile
# First, install this module
# Then do a make cfg_upd to pull in the CSR configs from NFS Mount
# Then, do a make csr to create the csr-library
#
# Do a make clean to remove the derived files (except the pulled in CSR)
# Do a make distclean to remove all the CSR configurations as well

SUDO = sudo
INDIR = jsb

OS := $(shell uname)



#
# Different tools on MacOS vs linux
ifeq ($(OS),Darwin)
  INSTALL := brew
else
ifeq ($(OS),Linux)
  INSTALL := apt
endif
endif



all: build

.PHONY: build clean libcsr cfg_pull cfg
build:
	$(SUDO) python setup.py install --record files.txt

libcsr:

	cd csr-rt && astyle -c gen/csr_gen.cpp &&  make

cfg: cfg_pull
	csr-slurp -i csr/csr_cfg -o csr-rt/gen


cfg_pull: build
	#$(SUDO) $(INSTALL) install nfs-common
	cd csr; csr-get -i $(INDIR)

clean:
	cat files.txt | sudo xargs rm -rf
	$(SUDO) rm -rf dist
	$(SUDO) rm -rf build
	$(SUDO) rm -rf *.egg-info
	$(SUDO) rm -f files.txt
	cd csr-rt; make clean

distclean: clean
	cd csr/csr_cfg && rm -rf *
	cd csr-rt; make distclean



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
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/FunSDK/config/csr


SRC = csr-rt/gen/csr_metadata.json

# install to SDK
install:
	csr-slurp -i $(FUNSDK_INSTALL_DIR)/csr_cfg -o csr-rt/gen
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -av $(SRC) $(FUNSDK_INSTALL_DIR)

