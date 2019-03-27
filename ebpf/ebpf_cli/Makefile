
OS := $(shell uname)

SDKDIR ?= ../../../FunSDK
CXXFLAGS ?= -g -std=c++17 -I $(SDKDIR) -I $(SDKDIR)/FunSDK -g -Wall -Werror -Wno-multichar
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/x86_64 -lfunclient -lreadline -lpthread

INSTALL_DIR ?= .

COMMON := cli_mgr.o bpf_module.o tcp_cli.o json_factory.o

all: ebpf_shell ebpf_cli

ebpf_shell: $(COMMON) ebpf_shell.o  
	$(CXX) -o $@ $^ $(LDFLAGS)

ebpf_cli: $(COMMON) ebpf_cli.o
	$(CXX) -o $@ $^ $(LDFLAGS)




%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) $<

clean:
	rm -f *.o
	rm -f ebpf_shell ebpf_cli
