# Basic Makefile

OS := $(shell uname)
# The build is where our SDK is rooted

SDKDIR ?= ../../FunSDK
CFG_DIR ?= $(SDKDIR)/FunSDK/chip/f1/hw/yaml/
TMPL_FILE ?= csr/template/csr_filter.yaml
INC_DIR ?= `pwd`/csr/export/include
LIB_DIR ?= `pwd`/csr/export/lib
CSR_JSON ?= csr_metadata.json


# This stuff is needed for FunSDK scripts
# to pull artifacts from here

SDK_INSTALL_DIR ?= $(SDKDIR)

# Get past issues with g++ based compilation on Linux VMs
# by using clang. On MacOS, g++ is clang

ifeq ($(OS), Darwin)
	CXX=g++
else
ifeq ($(OS), Linux)
	CXX=clang++-4.0
endif
endif

# This should be the first target
build: $(LIB_DIR)/csrlib.a
	CSR_LIB=$(LIB_DIR) CSR_INC=$(INC_DIR) INSTALL_DIR=`pwd` CXX=$(CXX) make -C csr-shell csrsh-install
	chmod +x csrsh

$(LIB_DIR)/csrlib.a:
	PYTHONPATH=$(PYTHONPATH):$(shell pwd) CXX=$(CXX) bin/csr-slurp \
		-d ${CFG_DIR}                               \
		-c .                                        \
		-g                                          \
		-i $(INC_DIR)                               \
		-l $(LIB_DIR)                               \
		#-f $(TMPL_FILE)                             \

install: build
	mkdir -p $(SDK_INSTALL_DIR)/FunSDK/config/csr
	mkdir -p $(SDK_INSTALL_DIR)/bin
	cp -f $(CSR_JSON) $(SDK_INSTALL_DIR)/FunSDK/config/csr
	cp -f csrsh $(SDK_INSTALL_DIR)/bin

.PHONY: clean
clean:
	rm -f $(LIB_DIR)/libcsr.a
	rm -f $(INC_DIR)/*
	make -C csr-shell clean
	rm -f csrsh
	rm -f *.json
