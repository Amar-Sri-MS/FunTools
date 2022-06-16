# Simple Signing Server

This file explain how to create a new instance of the Simple Signing Server, 
a simple implementation of the Fungible Signing Server API.

This Signing Server API is consumed by build scripts to get the public keys and signatures for the various images: Firmware, FunOS, CCLinux.

The Simple Signing Server can be installed on any OS that supports Apache2 and Python.

The Simple Signing Server can be installed on each developer machine or a single server can be shared across a team of developers so that the developers only need to configure their FunSDK. 

(Configuring the SDK is explained in the companion file README-SDKConfiguration.md)

## Installation

To install the signing server, execute the `signing_server.run` script as root:

```sh
sudo ./signing_server.run
```

#### Self Test
The installer will perform a simple test to verify everything is working:

```sh
$ sudo ./signing_server.run
Verifying archive integrity...  100%   All good.
Uncompressing Fungible Simple Signing Server Installer  100%  
<...snip...>
--2021-07-29 10:02:22--  http://localhost/cgi-bin/signing_server.cgi?cmd=modulus&key=hkey1&format=c_struct
Resolving localhost (localhost)... 127.0.0.1
Connecting to localhost (localhost)|127.0.0.1|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1576 (1.5K) [text/plain]
Saving to: ‘STDOUT’

-                                    0%[                                                               ]       0  --.-KB/s               256,
{
0xb2, 0x71, 0x29, 0x80, 0x90, 0x26, 0x0c, 0x15,
0x34, 0xc5, 0xe2, 0xa0, 0xac, 0xfa, 0x88, 0xb8,
0x5e, 0x72, 0x68, 0x71, 0x10, 0xfc, 0xee, 0xab,
0xe4, 0x38, 0x36, 0xad, 0x0d, 0xcf, 0x12, 0x51,
0x94, 0x5e, 0xc8, 0x11, 0x68, 0xcb, 0xaa, 0x2a,
0xac, 0x73, 0xda, 0x48, 0xd2, 0x7c, 0x01, 0x89,
0x04, 0xf5, 0x16, 0xa5, 0x97, 0x21, 0x83, 0x08,
0x03, 0x9d, 0x7c, 0xc2, 0x31, 0x03, 0x68, 0xab,
0xf6, 0xa0, 0x52, 0x4a, 0xd6, 0x4c, 0x20, 0xad,
0xb9, 0xfc, 0x61, 0x7b, 0x04, 0xc7, 0xcb, 0x14,
0x7f, 0x7b, 0x98, 0x1b, 0x9b, 0x45, 0x9f, 0x8d,
0x3a, 0x54, 0x18, 0x53, 0x29, 0x83, 0x63, 0xb4,
0x6e, 0xa5, 0xc7, 0x9e, 0x7e, 0x05, 0xf5, 0x04,
0xf7, 0xa9, 0x4d, 0xc2, 0x86, 0x73, 0xc5, 0x09,
0x87, 0xdd, 0x72, 0x6c, 0x72, 0xbc, 0xc3, 0x35,
0xdb, 0x21, 0x4e, 0x9b, 0xcc, 0x43, 0xb5, 0xfc,
0x67, 0xa6, 0xed, 0x15, 0xf0, 0xef, 0x74, 0xdc,
0xc5, 0x24, 0x4c, 0xc3, 0x70, 0x1c, 0x70, 0x57,
0x38, 0xf5, 0x0e, 0x97, 0x68, 0xf6, 0x9d, 0x89,
0xd5, 0xd0, 0xb0, 0x58, 0x49, 0xf9, 0x6b, 0xec,
0xb7, 0x26, 0x58, 0x1f, 0x9f, 0x7b, 0xf1, 0x62,
0xe1, 0xb0, 0x21, 0x08, 0x62, 0x06, 0xa3, 0x69,
0x83, 0x65, 0xe7, 0x11, 0x78, 0xb8, 0x70, 0x7d,
0x20, 0x04, 0x61, 0xf0, 0xc1, 0xc1, 0x55, 0x95,
0x1b, 0x34, 0x81, 0xfe, 0x90, 0x7f, 0x4d, 0xc8,
0x5e, 0x97, 0x3d, 0xcc, 0x89, 0xf8, 0xb8, 0xa5,
0xf6, 0x40, 0xdc, 0x4b, 0xfc, 0x6d, 0xfa, 0xb6,
0x79, 0xce, 0xfe, 0x2e, 0x7b, 0x2a, 0x5b, 0xda,
0x70, 0xd5, 0xaa, 0x59, 0xcd, 0x66, 0x01, 0x73,
0x34, 0x7f, 0xf7, 0xcd, 0xba, 0xa8, 0xad, 0x8d,
0xe5, 0x56, 0x50, 0xd8, 0x8f, 0xce, 0x3b, 0x58,
0x04, 0xeb, 0x39, 0x0f, 0x17, 0xfc, 0xa4, 0xbb,
-                                  100%[==============================================================>]   1.54K  --.-KB/s    in 0s

2021-07-29 10:02:23 (314 MB/s) - written to stdout [1576/1576]
```

### FAQ & Troubleshooting

The installation script can report some errors on some preexisting Linux installations.

#### HTTP Response 500

The Simple Signing Server returns a 500 Error, including during the Self Test

```HTTP request sent, awaiting response... 500 Internal Server Error
2022-06-14 02:57:11 ERROR 500: Internal Server Error. <<<<<<<<
```

The Apache error.log (typically `/var/log/apache2/error.log`) will have more information about this error.
This type of error is usually caused by a problem with the installed Python libraries. 

Error messages in the Apache `error.log` should suggest ways to solve the problem. 

If not, please contact Fungible Support with the information in the Apache error log.

###### Tip: 
Apache rotates its logs. If there is no error in the `error.log`, look at the previous instances of the file: `error.log.1` and `error.log.<n>.gz`


#### The Linux installation is not using systemd as the init sytem

```
$ sudo systemctl restart apache2
System has not been booted with systemd as init system (PID 1). Can't operate.
Failed to connect to bus: Host is down
```

##### Solution:
Restart apache2 using the appropriate command for the sytem. 
Example:
```
$ sudo service apache2 restart
```

#### Port 80 cannot be used by Apache2 httpd

```
* Restarting Apache httpd web server apache2 (13)Permission denied: AH00072: make_sock: could not bind to address [::]:80
(13)Permission denied: AH00072: make_sock: could not bind to address 0.0.0.0:80
no listening sockets available, shutting down
AH00015: Unable to open logs
Action 'start' failed.
The Apache error log may have more information.
```

Most likely, there is another process using port 80 on the machine that conflicts with the default Apache2 http installation.

##### Solution:
This can be fixed by at least 3 different methods:


1. stop/remove the process using port 80 on that machine.
1. if that process is an HTTP server, use it as the signing server instead of Apache2 httpd. It might be necessary to move the files `*.pem, signing_server.cgi` that are now in the `/usr/lib/cgi-bin` to that other HTTP server cgi-bin directory. Consult that HTTP server documentation.
1. reconfigure the Apache HTTP server NOT to use port 80 but another port (8080/8081/etc...) by editing the Apache configuration files (/etc/apache2/ports.conf and /etc/apache2/sites-enabled/000-default.conf). Consult the Apache2 documentation.


