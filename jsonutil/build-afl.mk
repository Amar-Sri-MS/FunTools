ifeq ($(OS),Linux)

# clear these for fuzzing
CFLAGS :=
LDFLAGS_ASAN :=

# build with AFL
# CC := ../../afl-2.41b/afl-clang
CC := ../../afl-2.41b/afl-gcc

FUZZ := ../../afl-2.41b/afl-fuzz

FUNOS := ../../FunOS
SRC += fun_json.c fun_map.c fun_heap.c fun_set.c

fuzztext: jsonutil
	$(FUZZ) -i testcase_dir -o findings_dir -- ./jsonutil --in @@

fuzzbinary: jsonutil
	$(FUZZ) -i testcase_bindir -o findings_bindir -- ./jsonutil --inb @@

endif
