# OS
OS := $(shell uname)

MACHINE ?= posix

ifeq ($(MACHINE),posix)
 SDK_INSTALL_PREFIX :=
else ifeq ($(MACHINE),arm)
 SDK_INSTALL_PREFIX := arm
else ifeq ($(MACHINE),mips64)
 SDK_INSTALL_PREFIX := mips64
else
 $(error Unknown machine type $(MACHINE))
endif

BUILD_ROOT ?= $(MACHINE)-build

CFLAGS += -g -Wall -Werror -Wno-multichar
LDFLAGS += 

SRCS = fun_json_lite.c fun_json_lite_tester.c
OBJS = $(addprefix $(BUILD_ROOT)/,$(SRCS:.c=.o))

# default target goes first 
all: fun_json_lite_tester

$(BUILD_ROOT):
	mkdir -p $@

$(BUILD_ROOT)/%.o: %.c $(DEPS) | $(BUILD_ROOT)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: fun_json_lite_tester
fun_json_lite_tester: $(BUILD_ROOT)/fun_json_lite_tester

$(BUILD_ROOT)/fun_json_lite_tester: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(BUILD_ROOT)/fun_json_lite_tester $(OBJS)
