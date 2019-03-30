#
# Use make to generate the bbv output
#
#

FUNOS_BIN ?= ../../../FunOS/build/funos-f1
OBJDUMP ?= /opt/cross/mips64/bin/mips64-unknown-elf-objdump
PY_FILES := $(wildcard *.py)

all: bbv

bbv: $(PY_FILES) log_file
	python orchestrator.py -f -i log_file -b -o $@.png

log_file:
	$(OBJDUMP) -d --no-show-raw-insn $(FUNOS_BIN) > $@

clean:
	rm -f log_file
	rm -f bbv
	rm *.pyc

