# This file should house AFL build rules for jsonutil.
# Currently that has deep dependencies on FunOS spititng out
# AFL-compatible libraries, which we don't use yet. This make
# fragment is fundamentally broken until we fix the other dependencies.
# This should be used as a reference for how to structure AFL, though.
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
