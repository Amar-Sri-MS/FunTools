test:
	python parse_dasm_test.py
	python html_gen_test.py
	python ttypes_test.py

# Test that we can make it through a large trace without noticeable
# hiccups.  Use the last few lines to detect correctness.
large_test:
	rm -f /tmp/trace_test.out
	./tprs.py -a testdata/funos-f1-palladium.dasm \
 		  -t testdata/samurai_corex_0.trace --format sim \
                  >& /tmp/trace_test.out; \
	tail -16 /tmp/trace_test.out > /tmp/results.out; \
	diff testdata/expected.out /tmp/results.out
