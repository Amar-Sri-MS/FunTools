#
#  Makefile
#
#  Created by Hariharan Thantry on 2019-04-01
#
#
#  Copyright © 2019 Fungible Inc. All rights reserved.
#
#
TARGET ?= bpfel
KERNEL ?= 01
WORKSPACE ?= ../../../


OS := $(shell uname)

SDKDIR = $(WORKSPACE)/FunSDK

CXXFLAGS ?= -g -std=c++17 -I $(SDKDIR) -I $(SDKDIR)/FunSDK -g -Wall -Werror -Wno-multichar
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/x86_64 -lfunclient -lreadline -lpthread

COMMON := cli_mgr.o bpf_module.o tcp_cli.o json_factory.o

ifeq ($(TARGET),$(filter $(TARGET),bpfeb bpfel))
	BC_FILE := ../ebpf_kernels/k_$(KERNEL).$(TARGET).bc
else
	$(error Unknown $(TARGET). Please specify either bpfeb or bpfel)
endif

define cpp_tidy
        sed 's/[[:blank:]]*$$//' --in-place $(1)
	clang-format -style="{BasedOnStyle: google, IndentWidth: 4}" -i $(1) -fallback-style=none
endef

all: ebpf_shell ebpf_cli

ebpf_shell: $(COMMON) ebpf_shell.o
	$(CXX) -o $@ $^ $(LDFLAGS)

ebpf_cli: $(COMMON) ebpf_cli.o
	$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(call cpp_tidy,$<)
	$(CXX) -c $(CXXFLAGS) $<
attach:
	./ebpf_cli -p 40221 cmd=attach sec=xdp cl_id=22 tx_id=22 qid=128 order=10 bpf_file=$(BC_FILE)
detach:
	./ebpf_cli -p 40221 cmd=detach sec=xdp cl_id=22 tx_id=22

clean:
	rm -f *.o *~
	rm -f ebpf_shell ebpf_cli
