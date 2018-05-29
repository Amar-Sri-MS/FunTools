# Copyright © 2017 Fungible. All rights reserved.

# We set these for Jenkins. But if you want to change Python dependencies by
# using pipenv directly, please set these in your shell.

export PIPENV_MAX_DEPTH := 16

ifdef DOCKER
PIPENV :=/usr/local/bin/pipenv
else
export PATH := $(HOME)/.local/bin:$(PATH)
PIPENV := ~/.local/bin/pipenv
$(PIPENV):
	@pip install --user pipenv
endif

# We switched to putting venv in user's dir. But making a fake target here
# so people can "make venv".
VENV := venv
.PHONY: $(VENV)
$(VENV): Pipfile Pipfile.lock | $(PIPENV)
	@echo "PIPENV loc: " $(PIPENV)
ifdef DOCKER
	sudo WORKON_HOME=/fun_external/.local/ $(PIPENV) install --dev
else
	$(PIPENV) install --dev
endif

.PHONY: clean_venv
clean_venv:
ifdef DOCKER
	@if [ -f $(PIPENV) ] && sudo WORKON_HOME=/fun_external/.local/ $(PIPENV) --venv > /dev/null 2>&1; then sudo WORKON_HOME=/fun_external/.local/ $(PIPENV) --rm; fi
else
	@if [ -f $(PIPENV) ] && $(PIPENV) --venv > /dev/null 2>&1; then $(PIPENV) --rm; fi
endif

BRANCH_PYTHON_FILES = $(shell git diff --name-only master...HEAD | grep '\.py$$')
STAGED_PYTHON_FILES = $(shell git diff --name-only --staged | grep '\.py$$')
UNSTAGED_PYTHON_FILES = $(shell git diff --name-only | grep '\.py$$')
CHANGED_PYTHON_FILES = $(sort $(BRANCH_PYTHON_FILES) $(STAGED_PYTHON_FILES) $(UNSTAGED_PYTHON_FILES))

.PHONY: python_style
python_style:
	@-[ -n "$(CHANGED_PYTHON_FILES)" ] && $(PIPENV) check --style $(CHANGED_PYTHON_FILES)
