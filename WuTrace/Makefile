test: render_test trace_test

render_test: render_test.py
	python render_test.py

trace_test: trace_test.py
	python trace_test.py

end_to_end: examples/sample.trace
	./wu_trace.py examples/sample.trace > /tmp/out.html
	echo 'Open "/tmp/out.html" to check results.'