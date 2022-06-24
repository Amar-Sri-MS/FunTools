all: test end_to_end end_to_end_raw

test:
	/usr/bin/env python3 -m unittest discover -p '*test.py' -v

end_to_end: testdata/lsv.trace
	./wu_trace.py testdata/lsv.trace --event-output /tmp/out1.events --output  /tmp/out.html
	echo 'Open "/tmp/out.html" to check results.'

end_to_end_raw: testdata/sw_wu_raw.trace
	./wu_trace.py --input-format trace --wu-list testdata/wu_list.sw_wu_raw.txt testdata/sw_wu_raw.trace --event-output /tmp/out1.events --output /tmp/out1.html
	echo 'Open "/tmp/out1.html" to check results'
