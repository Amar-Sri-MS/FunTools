
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR) -I $(SDKDIR)/FunSDK  -g -Wall -Werror -Wno-multichar

# XXX: compatibility with FunOS build parameters
LDFLAGS += -L $(SDKDIR)/lib/${OS}/x86_64 -lfunclient -fsanitize=address

OBJS = dpcsh.o web.o


%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

dpcsh: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

install: dpcsh
	cp dpcsh $(SDKDIR)/bin

clean:
	rm -f dpcsh $(OBJS)
