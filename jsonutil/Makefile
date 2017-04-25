
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK

all: jsonutil

# AFL pieces
include build-afl.mk

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR)/FunSDK

# XXX: compatibility with FunOS build parameters
LDFLAGS_ASAN ?= -fsanitize=address 
LDFLAGS += -L $(SDKDIR)/lib/${OS}/ -lfunclient -lm $(LDFLAGS_ASAN)

SRC += jsonutil.c

jsonutil: jsonutil.c
	$(CC) -o jsonutil $(SRC) $(CFLAGS) $(LDFLAGS)

install: jsonutil
	cp jsonutil $(SDKDIR)/bin

clean:
	rm jsonutil
