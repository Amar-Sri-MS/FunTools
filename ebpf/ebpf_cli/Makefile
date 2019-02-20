
OS := $(shell uname)

SDKDIR ?= ../../FunSDK
CXXFLAGS ?= -g -std=c++11 -I $(SDKDIR) -I $(SDKDIR)/FunSDK -g -Wall -Werror -Wno-multichar
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/x86_64 -lfunclient -lreadline -lpthread

INSTALL_DIR ?= .

all: cli_mgr

%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) $<

cli_mgr: frontend.o cli_mgr.o bpf_module.o tcp_cli.o json_factory.o
	$(CXX) -o $@ $^ $(LDFLAGS)

cli-install: cli_mgr
	cp cli_mgr $(INSTALL_DIR)
clean:
	rm -f *.o
	rm -f cli_mgr
