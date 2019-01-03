
MACHINE ?= posix

GENERATED = ../
HU_CFG_C = ../generated/hu_cfg.c

CFLAGS = -g -Wall -I $(GENERATED)

test_hu_cfg: test_hu_cfg.c
	$(CC) -o $@ $(CFLAGS) test_hu_cfg.c $(HU_CFG_C)

.PHONY: clean
clean:
	@echo Cleaning tree
	rm -rf test_hu_cfg *.o
