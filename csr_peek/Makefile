# Basic Makefile
# First, install this module
# Then do a make cfg_upd to pull in the CSR configs from NFS Mount
# Then, do a make csr to create the csr-library
#
# Do a make clean to remove the derived files (except the pulled in CSR)
# Do a make distclean to remove all the CSR configurations as well

SUDO_I = sudo
SUDO_E = sudo
INDIR = jsb

OS := $(shell uname)



#
# Different tools on MacOS vs linux
ifeq ($(OS),Darwin)
  SUDO_I =
  INSTALL := brew
  NFS :=
else
ifeq ($(OS),Linux)
  INSTALL := apt
  NFS := nfs-common
endif
endif



all: build

.PHONY: build clean libcsr cfg_pull cfg
build:
	$(SUDO_E) python setup.py install --record files.txt

libcsr:
	$(SUDO_I) $(INSTALL) install astyle
	cd csr-rt && astyle -c gen/csr_gen.cpp &&  make

csrsh: libcsr
	cd csr-rt && make csrsh

cfg:build
	csr-slurp -i csr/csr_cfg -o csr-rt/gen


cfg_pull:build $(NFS)
	cd csr; csr-get -i $(INDIR)

$(NFS):
	$(SUDO_I) $(INSTALL) install $(NFS)

clean:
	cat files.txt | sudo xargs rm -rf
	$(SUDO_E) rm -rf dist
	$(SUDO_E) rm -rf build
	$(SUDO_E) rm -rf *.egg-info
	$(SUDO_E) rm -f files.txt
	cd csr-rt; make clean

distclean: clean
	cd csr/csr_cfg && rm -rf *
	cd csr-rt; make distclean



# Build platform OS
OS := $(shell uname)

# The build is where our SDK is rooted
SDKDIR ?= ../../FunSDK

# Where install files go
SDK_INSTALL_DIR ?= $(SDKDIR)

# The FunOS dir where config files reside
FUNOSDIR ?= ../../FunOS

# Directory where csr metadata file is copied
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/FunSDK/config/csr

CSR_METADATA = csr-rt/gen/csr_metadata.json
CSR_TMPL_DIR = csr/template
CSR_RT_DIR = csr-rt/gen
CSR_CFG_DIR = csr/csr_cfg

# Install to SDK
#install: cfg_pull
install:
	csr-slurp -i $(CSR_CFG_DIR) -o $(CSR_RT_DIR) -f $(CSR_TMPL_DIR)/csr_filter_tm.yaml
	#csr-slurp -i $(FUNSDK_INSTALL_DIR) -o $(CSR_RT_DIR) -f $(CSR_TMPL_DIR)/csr_filter_tm.yaml
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -av $(CSR_METADATA) $(FUNSDK_INSTALL_DIR)

