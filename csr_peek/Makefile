# Basic Makefile

OS := $(shell uname)
# The build is where our SDK is rooted

SDKDIR ?= ${WORKSPACE}/FunSDK
CFG_DIR ?= $(SDKDIR)/FunSDK/chip/f1/hw/yaml/
TMPL_FILE ?= csr/template/csr_filter.yaml
TMP_DIR ?= csr/libcsr/gen

all: cfg

# Install Pipenv for user if necessary
ifeq ($(PYTHONUSERBASE),)
	PYTHONUSERBASE := $(HOME)/.local
endif

PIPENV := $(or $(wildcard $(PYTHONUSERBASE)/bin/pipenv),\
	$(wildcard /usr/local/bin/pipenv),\
	$(wildcard /usr/bin/pipenv),\
	$(PYTHONUSERBASE/bin/pipenv))
$(PYTHONUSERBASE)/bin/pipenv:
	pip install --user pipenv

# Create venv if not exists
VENV = $(or $(shell $(PIPENV) --venv 2>/dev/null),venv)

.PHONY: venv
venv: | $(PIPENV)
	$(PIPENV) install --verbose -e . --dev

ifneq ($(VENV), venv)
	touch $(VENV)
$(VENV): Pipfile Pipfile.lock
	$(MAKE) venv
endif

.PHONY: clean libcsr cfg

libcsr: cfg
	cd csr-rt &&  make
csrsh: libcsr
	cd csr-rt && make csrsh
cfg: $(VENV)
	pipenv run csr-slurp \
		-d ${CFG_DIR} \
		-t $(TMP_DIR) \
		-f $(TMPL_FILE) \
		-c $(SDKDIR)/FunSDK/config/csr
	        

clean: | clean_venv
	cd csr-rt; make distclean

clean_venv:
	@if [ -f $(PIPENV) ] && $(PIPENV) --venv > /dev/null 2>&1; then $(PIPENV) --rm; fi
	@rm -rf csr_slurp.egg-info
