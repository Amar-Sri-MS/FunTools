
OS := $(shell uname)
INDENT_ARGS=-npro -kr -i8 -ts8 -sob -l80 -ss -ncs -cp1 -il0

SDKDIR ?= ../../../FunSDK
CXXFLAGS ?= -DPLATFORM_POSIX -g -std=c++17 -I $(SDKDIR) -I $(SDKDIR)/FunSDK -g -Wall -Werror -Wno-multichar
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/x86_64 -lfunclient -lreadline -lpthread

INSTALL_DIR ?= .

COMMON := cli_mgr.o bpf_module.o tcp_cli.o json_factory.o

define cpp_tidy
	clang-format -style=file -i $(1) -fallback-style=none
endef

all: ebpf_shell ebpf_cli

ebpf_shell: $(COMMON) ebpf_shell.o
	$(CXX) -o $@ $^ $(LDFLAGS)

ebpf_cli: $(COMMON) ebpf_cli.o
	$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(call cpp_tidy,$<)
	$(CXX) -c $(CXXFLAGS) $<
run:
	./ebpf_cli -p 40221 cmd=attach sec=xdp cl_id=22 tx_id=22 qid=8 order=10 bpf_file=../ebpf_kernels/k_01.bc
clean:
	rm -f *.o *~
	rm -f ebpf_shell ebpf_cli
