# A guide to dpc scripting.
# 
First you need to start the dpc server in the FunOS directory where you built it:
	./build/funos-posix --dpc-server
Second you start dpcsh in the FunTools directory where you built it: 
	./dpcsh
Then you can type commands like 'help' or 'fibo 10' to talk to the dpc server.

You can use dpcsh without its command line interface, e.g. to run certain commands, like:
	./dpcsh --nocli peek params/syslog
	./dpcsh --nocli poke params/syslog/level 6

You can use dpcsh as a proxy redirecting to a web client, by:
	./dpcsh --proxy
and going to a browser to type URLs like:
	localhost:9001/params
	
You can use dpcsh as a proxy interpreting commander text and returning text JSON, by:
	./dpcsh --text_proxy
and then running a python script like the one in FunTools/dpcsh/test.py
