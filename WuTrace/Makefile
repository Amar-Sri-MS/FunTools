test:
	python -m unittest discover -p '*test.py' -v

end_to_end: sampleTrace
	./wu_trace.py sampleTrace > /tmp/out.html
	echo 'Open "/tmp/out.html" to check results.'