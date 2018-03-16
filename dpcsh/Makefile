
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR) -I $(SDKDIR)/FunSDK  -g -Wall -Werror -Wno-multichar

# XXX: compatibility with FunOS build parameters
#LDFLAGS += -L $(SDKDIR)/lib/${OS}/x86_64 -lfunclient -fsanitize=address
#LDFLAGS += -lpthread -L $(SDKDIR)/lib/${OS}/x86_64 -lfunclient -fsanitize=address
LDFLAGS += -lpthread -L $(SDKDIR)/lib/${OS}/noasan/x86_64 -lfunclient

OBJS = dpcsh.o dpcsh_macros.o web.o

# Deal with gcc versioning for ASAN
ifeq ($(OS),Linux)
CC := gcc$(GCC_SUFFIX)
endif


%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

dpcsh: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

install: dpcsh
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)
	# FIXME: remove OS versioning on dpc_client.py when
	# integration tests are fixed
	cp dpc_client.py dpcsh $(SDK_INSTALL_DIR)/bin/$(OS)

clean:
	rm -f dpcsh $(OBJS)
