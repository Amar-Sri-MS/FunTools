
OS := $(shell uname)
CC=g++

CFLAGS ?= -g -std=c++11 -I $(WORKSPACE)/FunSDK -I $(WORKSPACE)/FunSDK/FunSDK -I $(WORKSPACE)/FunTools/csr_peek/csr-rt/include -g -Wall -Werror -Wno-multichar
LDFLAGS += -L $(WORKSPACE)/FunSDK/lib/$(OS)/noasan/x86_64 -L $(WORKSPACE)/FunTools/csr_peek/csr-rt  -lfunclient -lcsr -lreadline -lpthread

all: libtcpcli.a

libtcpcli.a: libtcpcli.o



%.o: %.cpp
	$(CC) -c $(CFLAGS) $<

csrsh: frontend.o csrsh.o tcp_cli.o json_util.o
	$(CC) -o $@ $^ $(LDFLAGS)
clean:
	rm -f *.o
	rm -f csrsh
