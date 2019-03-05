#
# Use make to generate the bbv output
#
#

FUNOS_BIN ?= ../../../FunOS/build/funos-f1
OBJDUMP ?= /opt/cross/mips64/bin/mips64-unknown-elf-objdump

all: bbv

bbv: bbv.py log_file
	python bbv.py -x log_file -b bbv.png

log_file:
	$(OBJDUMP) -d --no-show-raw-insn $(FUNOS_BIN) > $@

clean:
	rm -f log_file
	rm -f bbv

