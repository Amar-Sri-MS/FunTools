# Copyright © 2017 Fungible. All rights reserved.

# We set these for Jenkins. But if you want to change Python dependencies by
# using pipenv directly, please set these in your shell.

export PIPENV_MAX_DEPTH := 16

PIPENV=pipenv
$(PIPENV):
	@pip install --user pipenv

# We switched to putting venv in user's dir. But making a fake target here
# so people can "make venv".
VENV := venv
.PHONY: $(VENV)
$(VENV): Pipfile Pipfile.lock | $(PIPENV)
	@echo "PIPENV loc: " $(PIPENV)
	$(PIPENV) install --dev

.PHONY: clean_venv
clean_venv:
	@if [ -f $(PIPENV) ] && $(PIPENV) --venv > /dev/null 2>&1; then $(PIPENV) --rm; fi

BRANCH_PYTHON_FILES = $(shell git diff --name-only master...HEAD | grep '\.py$$')
STAGED_PYTHON_FILES = $(shell git diff --name-only --staged | grep '\.py$$')
UNSTAGED_PYTHON_FILES = $(shell git diff --name-only | grep '\.py$$')
CHANGED_PYTHON_FILES = $(sort $(BRANCH_PYTHON_FILES) $(STAGED_PYTHON_FILES) $(UNSTAGED_PYTHON_FILES))

.PHONY: python_style
python_style:
	@-[ -n "$(CHANGED_PYTHON_FILES)" ] && $(PIPENV) check --style $(CHANGED_PYTHON_FILES)
