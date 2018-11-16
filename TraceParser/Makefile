all: test large_test

test:
	parse_dasm_test.py
	html_gen_test.py
	ttypes_test.py

# Test that we can make it through a large trace without noticeable
# hiccups.  Use the last few lines to detect correctness.
large_test:
	rm -f /tmp/trace_test.out
	zcat testdata/samurai_coreX_2.trace.gz > /tmp/samurai_coreX_2.trace
	./tprs.py -a testdata/funos-f1-emu.dasm \
 		  -t /tmp/samurai_coreX_2.trace --format sim \
                  >& /tmp/trace_test.out; \
	tail -16 /tmp/trace_test.out > /tmp/results.out; \
	cp /tmp/results.out results.out ; \
	diff testdata/expected.out /tmp/results.out; \
 	rm -f /tmp/trace.out; \
	rm -f /tmp/results.out; \
	rm -f /tmp/samurai_coreX_2.trace
