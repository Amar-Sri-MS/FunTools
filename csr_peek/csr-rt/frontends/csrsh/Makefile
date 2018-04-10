
OS := $(shell uname)
CC=g++

CFLAGS ?= -std=c++11 -I $(WORKSPACE)/FunSDK -I $(WORKSPACE)/FunSDK/FunSDK -I $(WORKSPACE)/FunTools/csr_peek/csr_rt/include -g -Wall -Werror -Wno-multichar
#CFLAGS ?= -std=c++11 -I $(WORKSPACE)/FunTools/csr_peek/csr_rt/include -g 

LDFLAGS += -L $(WORKSPACE)/FunSDK/lib/$(OS)/noasan/x86_64 -L $(WORKSPACE)/FunTools/csr_peek/csr-rt  -lfunclient -lcsr -lreadline -lpthread
#LDFLAGS += -L $(WORKSPACE)/FunTools/csr_peek/csr-rt  -lcsr -lreadline


all: csrsh

csrsh: frontend.cpp
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

