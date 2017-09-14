
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK

all: jsonutil

# AFL pieces
include build-afl.mk

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR)/FunSDK  \
	-I $(SDKDIR)

# XXX: compatibility with FunOS build parameters
LDFLAGS_ASAN ?= -fsanitize=address 
ifeq ($(OS),Linux)
#asan library linking does not work for Linux
LDFLAGS += -L $(SDKDIR)/lib/${OS}/noasan/ -lfunclient -lm
else
LDFLAGS += -L $(SDKDIR)/lib/${OS}/ -lfunclient -lm $(LDFLAGS_ASAN)
endif

SRC += jsonutil.c

jsonutil: jsonutil.c
	$(CC) -o jsonutil $(SRC) $(CFLAGS) $(LDFLAGS)

install: jsonutil
	cp jsonutil $(SDKDIR)/bin

clean:
	rm jsonutil
