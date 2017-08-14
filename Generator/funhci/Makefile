
# Platform
OS := $(shell uname)

MACHINE ?= posix

ifeq ($(OS),Darwin)
	TOOL_ROOT := /Users/Shared/cross-el/bin
	TOOL_PREFIX := mips64el-
else
ifeq ($(OS),Linux)
	TOOL_ROOT ?= /opt/cross/bin
	TOOL_PREFIX ?= mipsel-unknown-linux-gnu-
endif
endif

ifeq ($(MACHINE),posix)
	FULLPREFIX =
	LIBDST = posix/$(OS)
else
ifeq ($(MACHINE),mips)
	FULLPREFIX = $(TOOL_ROOT)/$(TOOL_PREFIX)
	LIBDST = mips64
endif
endif

CC = $(FULLPREFIX)gcc
AR = $(FULLPREFIX)ar

BUILD = build

SDKDIR ?= ../../../FunSDK

LIBS = $(SDKDIR)/lib/$(OS)/noasan/libfunclient.a

LIB_HCI = libfunhci-$(MACHINE).a

HCI_SRC = fun_hci_json.c
HCI_HDR = fun_hci_json.h

HCI_OBJS = $(patsubst %.c,$(BUILD)/obj/%.o,$(filter %c,$(HCI_SRC)))

CFLAGS = -Wall -Werror
CFLAGS += -I $(SDKDIR)/FunSDK -I $(SDKDIR)

.PHONY: all
all: funos_code host_code $(BUILD)/$(LIB_HCI)

.PHONY: funos_code
funos_code:
	@mkdir -p out
	../generator.py -c pack,json -g code -o out/fun_hci_json fun_hci.gen

.PHONY: host_code
host_code:
	@mkdir -p out
	../generator.py -c pack -g code -o out/fun_hci fun_hci.gen

.PHONY: doc
doc:
	@mkdir -p out
	../generator.py -g html -o out/fun_hci fun_hci.gen
	../generator.py -g html -o out/port_enum fun_port.gen

$(BUILD)/obj/fun_hci_json.o: out/fun_hci_json.c
	@echo CC $<
	@mkdir -p `dirname $@`
	$(CC) -o $@ $(CFLAGS) -c $<

$(BUILD)/$(LIB_HCI): $(HCI_OBJS)
	$(AR) rcs $(BUILD)/$(LIB_HCI) $(HCI_OBJS)

.PHONY: install
install: $(BUILD)/$(LIB_HCI)
	mkdir -p $(SDKDIR)/FunSDK/hci/lib/$(LIBDST)
	mkdir -p $(SDKDIR)/FunSDK/hci/include
	cp $(BUILD)/$(LIB_HCI) $(SDKDIR)/FunSDK/hci/lib/$(LIBDST)/libfunhci.a
	cp out/$(HCI_HDR) $(SDKDIR)/FunSDK/hci/include

.PHONY: clean
clean:
	rm -rf out
	rm  -rf $(BUILD)
