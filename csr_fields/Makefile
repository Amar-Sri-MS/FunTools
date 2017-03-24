## Makefile

all: csr_fields

auto-generated.c: testgen.py
	./testgen.py 1000 > auto-generated.c

csr_fields: csr_fields.c csr_fields.h auto-generated.c
	$(CC) -Wall -Werror -g -o csr_fields csr_fields.c
