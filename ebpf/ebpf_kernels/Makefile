#
#
#  Makefile
#
#  Created by Hariharan Thantry on 2019-04-01
#
#
#  Copyright © 2019 Fungible Inc. All rights reserved.
#
#  Specialized makefile.
#
#  Generates BPF text bytecode (bpfel and bpfeb)
#  Creates C source/header files for direct use of these kernels inside FunOS
#  through static compilation
#
#  Artifact output from here is used in ebpf_cli to transport this bytecode
#  into running FunOS instance
#



CC := clang
TARGET ?= bpfeb
CFLAGS := -O2
SRCS := $(wildcard *.c)

OBJFILES := $(patsubst %.c,%.o,$(SRCS))
BCFILES := $(patsubst %.c,%.$(TARGET).bc,$(SRCS))
ASMFILES := $(patsubst %.c,%.$(TARGET).S,$(SRCS))

WORKSPACE ?= ../../../

GEN_BC ?= ebpf_bc_$(TARGET)
EXPORT_HDR ?= ebpf_kern_args.h
GEN_HDR ?= ebpf_gen.h
INDENT_ARGS=-npro -kr -i8 -ts8 -sob -l80 -ss -ncs -cp1 -il0


ifeq ($(TARGET),$(filter $(TARGET),bpfeb bpfel))
	CC := clang
    CFLAGS += -funroll-loops -target $(TARGET)
else
    $(error Unknown TARGET. Please specify either bpfeb or bpfel)
endif

define generate_bc
    m_file=$(basename $(1) .o)
    @objdump -h $(1) | \
		grep .text | \
		awk -v m_file=$(1) '{print "dd if='$$m_file'.o of='$$m_file'.$(TARGET).bc bs=1 count=$$[0x" $$3 "] skip=$$[0x" $$6 "]"}' | \
		bash
endef

define generate_bcc
	@touch $(GEN_BC).bcc
	@echo "#if 0" >> $(GEN_BC).bcc
	@cat $(1).c >> $(GEN_BC).bcc
	@echo "#endif" >> $(GEN_BC).bcc
	xxd -c 8 -i $(1).$(TARGET).bc >> $(GEN_BC).bcc
endef

define generate_bcc_hdr
	@touch $(GEN_HDR)
	@echo 'extern unsigned char $(1)_bc[];' >> $(GEN_HDR)
	@echo 'extern unsigned int $(1)_bc_len;' >> $(GEN_HDR)
endef

define c_tidy
	sed 's/^[ \t]*//' --in-place $(1)
	indent $(INDENT_ARGS) $(1)
endef

.ONESHELL:

all: $(BCFILES) $(ASMFILES) tidy

%.$(TARGET).S: %.o
	llvm-objdump -S $< > $@

.PHONY:tidy
tidy:
	$(call c_tidy,$(GEN_BC).bcc)

%.$(TARGET).bc: %.o
	$(call generate_bc,$<)
	$(call generate_bcc,$(basename $(basename $<)))
	$(call generate_bcc_hdr,$(basename $(basename $<)))

#.SECONDARY: $(OBJFILES)

%.o: %.c
	$(call c_tidy,$<)
	$(CC) $(CFLAGS)  -c $< -o $@


.PHONY: install
install: all
	cp $(GEN_BC).bcc $(WORKSPACE)/FunOS/tests/$(GEN_BC).c
	cp $(EXPORT_HDR) $(WORKSPACE)/FunOS/tests
	cp $(GEN_HDR) $(WORKSPACE)/FunOS/tests


.PHONY: clean
clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.S
	rm -f *.bcc
	rm -f ebpf_gen.h
	rm -f *~
