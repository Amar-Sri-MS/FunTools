
OS := $(shell uname)

SDKDIR ?= ../../../../../FunSDK
CXXFLAGS ?= -g -std=c++11 -I $(SDKDIR) -I $(SDKDIR)/FunSDK -I $(CSR_INC) -g -Wall -Werror -Wno-multichar
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/x86_64 -L $(CSR_LIB)  -lfunclient -lcsr -lreadline -lpthread

INSTALL_DIR ?= .

all: csrsh

%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) $<

csrsh: frontend.o csrsh.o tcp_cli.o json_util.o
	$(CXX) -o $@ $^ $(LDFLAGS)

csrsh-install: csrsh
	cp csrsh $(INSTALL_DIR)
clean:
	rm -f *.o
	rm -f csrsh
