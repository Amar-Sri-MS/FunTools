# DPC Shell (dpcsh)

dpcsh is a general-purpose tool to communicate with FunOS. This allows a remote agent to query, update and inject data in FunOS, as well as execute commands. dpcsh takes care of encoding JSON transactions

There are to main modes of execution of dpcsh:

1) *interactive mode* where a user can type commands at a terminal and view the output. Commands are a json-lite format to help save typing.

2) *proxy mode* where a script or program can make JSON-formatted reqeusts and recieve JSON-formatted replies. 

Between FunOS and dpcsh, the protocol is either over a posix simulator UNIX socket or via the MIPS UART.

Between dpcsh and proxy clients, the protocol can be TCP or UNIX sockets as a client or server or HTTP server. 

Details of the full architecture are on box: <https://fungible.box.com/s/lmfkali5g895ur4m5hpyle8z33ja7zub>

 
## Interactive Mode

To use dpcsh in interactive mode with the posix simulator you first start FunOS. It is available in the SDK, or you can follow similar instructinos if you build it yourself.

```
	$SDKDIR/bin/funos-posix --dpc-server
```
	
Second you can also start dpcsh from FunSDK. It's also available hand-built in FunTools/dpcsh:

```
	$SDKDIR/bin/$OS/dpcsh
```

Then you can type commands like 'help' or 'fibo 10' to talk to send transactions to FunOS.

You can use dpcsh without its interactive interface, e.g. to run certain commands one-off:

```
	./dpcsh --nocli peek params/syslog
	./dpcsh --nocli poke params/syslog/level 6
```

## Text Proxy Mode

You can use dpcsh as a proxy interpreting commander text and returning text JSON, by:

```
	./dpcsh --text_proxy
```

and then running a python script like the one in FunTools/dpcsh/dpctest.py

## HTTP Proxy Mode

You can use dpcsh as a proxy redirecting to a web client, by:

```
	./dpcsh --http_proxy
```

and going to a browser to type URLs like:

```
	localhost:9001/params
```

## Command-line Summary

By default dpcsh connects to a local funos-posix with a UNIX domain socket (the FunOS connection). The default input comes from the stdin TTY (command-socket). These options can be overriden with three main classes of arguments:

* generic arguments
* funos connection arguments
* command-socket arguments

### Generic Arguments

Option        | Arguments              | Description
--------------|------------------------|------------
**--help**    |                        | show usage
**--nocli**   | verb [_\<arguments\>_] | parse unknown command-line arguments as JSON-ish text, make a single transaction to FunOS then exit.
**--oneshot** |                        | in proxy mode, terminate after command socket disconnects.

### FunOS connection arguments

Option            | Arguments      | Description
------------------|----------------|------------
**--unix_sock**   | [=socket_file] | Default operation of dpcsh. Connect on UNIX domain socket to FunOS. Uses standard binary JSON encoding. eg. FunOS posix simulator. Default socket file = /tmp/funos-dpc.sock
**--inet_sock**   | [=port]        | Connect on a TCP port to FunOS. Uses standard binary JSON encoding. Used to connect to --tcp_proxy server. Default port = 40220.
**--dev**         | =device_file   | Open _device\_file_. Uses base64 encoded binary JSON. Useful for communicating with Qemu PTY on Linux or a palladium UART. device\_file has no default and is mandatory.
**--base64_srv**  | [=port]        | Listen on a TCP port for FunOS to connect. Uses base64 encoded binary JSON. Useful for testing with Qemu. Default port = 40223.
**--base64_sock** | [=port]        | Connect on a TCP port to FunOS. Uses base64 encoded binary JSON. Useful for testing with Qemu. Default port = 40222.


### Command-socket arguments

Option            | Arguments      | Description
------------------|----------------|------------
**--text_proxy**  | [=socket_name] | 
**--tcp_proxy**   | [=port]        | Create a TCP proxy server on listening on _port_ (default = 40221). Uses standard binary JSON encoding.
**--http_proxy**  | [=port]        | Create an HTTP proxy server listening on _port_ (default = 9001). Request is encoded in the path parameter of the URL.

## Command-Line Examples

The above options can be mixed on the command-line to control each end of the FunOS connection.

To create a text proxy to a base64 pty:

```
	$SDKDIR/bin/$OS/dpcsh --dev=/dev/pts/2 --text_proxy
```

To connect interactive to a TCP proxy:

```
	$SDKDIR/bin/$OS/dpcsh --inet_sock
```

To connect a text proxy to a TCP proxy:

```
	$SDKDIR/bin/$OS/dpcsh --inet_sock --text_proxy
```
