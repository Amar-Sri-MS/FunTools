# Basic Makefile

OS := $(shell uname)
# The build is where our SDK is rooted

SDKDIR ?= ../../FunSDK

# Supply a template file to reduce compile times
# if only a subset of the CSRs need to be in the DB
# See default example template

TMPL_FILE ?= csr/template/csr_filter.yaml

INC_DIR ?= `pwd`/csr/export/include
LIB_DIR ?= `pwd`/csr/export/lib
CSR_JSON ?= csr_metadata.json


# This stuff is needed for FunSDK scripts
# to pull artifacts from here

SDK_INSTALL_DIR ?= $(SDKDIR)

BASE_CFG_DIR ?= $(SDKDIR)
CFG_DIR := $(BASE_CFG_DIR)/FunSDK/chip/f1/yaml


# Get past issues with g++ based compilation on Linux VMs
# by using clang. On MacOS, g++ is clang

CXX := $(notdir $(or $(wildcard /usr/bin/clang++*), $(wildcard /usr/bin/g++)))

.PHONY: build_cfg
build_cfg:
	echo $(CFG_DIR)
	PYTHONPATH=$(PPYTHONPATH):$(shell pwd) bin/csr-slurp \
		-d ${CFG_DIR}                                \
		-c .                                         \

.PHONY: build_shell
build_shell: $(LIB_DIR)/libcsr.a
	CSR_LIB=$(LIB_DIR) CSR_INC=$(INC_DIR) INSTALL_DIR=`pwd` CXX=$(CXX) make -C csr-shell csrsh-install
	chmod +x csrsh

$(LIB_DIR)/libcsr.a:
	PYTHONPATH=$(PYTHONPATH):$(shell pwd) bin/csr-slurp \
		-d ${CFG_DIR}                               \
		-c .                                        \
		-g
	mkdir -p $(LIB_DIR)
	mkdir -p $(INC_DIR)
	LIB_DIR=$(LIB_DIR) INC_DIR=$(INC_DIR) CXX=$(CXX) make -C csr/libcsr install

.PHONY: install_cfg
install_cfg: build_cfg
	mkdir -p $(SDK_INSTALL_DIR)/FunSDK/config/csr
	cp -f $(CSR_JSON) $(SDK_INSTALL_DIR)/FunSDK/config/csr

.PHONY: install_csrsh
install_csrsh: build_shell
	mkdir -p $(SDK_INSTALL_DIR)/bin
	cp -f csrsh $(SDK_INSTALL_DIR)/bin

.PHONY: cfg_clean
cfg_clean:
	rm -f *.json

.PHONY: csrsh_clean
csrsh_clean: libcsr_clean
	make -C csr-shell clean
	rm -f csrsh

libcsr_clean:
	make -C csr/libcsr clean

.PHONY: clean
clean: cfg_clean csrsh_clean libcsr_clean
	rm -f $(LIB_DIR)/libcsr.a
	rm -f $(INC_DIR)/*
