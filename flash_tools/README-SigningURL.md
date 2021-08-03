# Fungible SDK Signing Server

The Fungible SDK is configured by default to use the Fungible Intranet signing server.

This file explains how to configure the SDK to use another Signing Server.

(Fungible provide a Simple Signing Server that can be installed almost anywhere and that exposes the Fungible Signing API using a set of development keys that are only valid on development DPUs. This is explained in the companion file README-ServerInstallation.md).

## Client configuration

To use another Signing Server instance with the Fungible SDK, use the script `config_sdk_signing_server.sh` to specify the URL (HTTP(S)) of the Signing Server instance.

```sh 
./config_sdk_signing_server.sh <-C /path/to/Fungible_SDK> [SIGNING_SERVER_HTTP_URL]
```


The script should be invoked with the current directory set to the Fungible SDK. If not, use the option `-C` to speficy the location of the Fungible SDK.

#### Examples:

Using a server installed on the same machine:

```sh
$ ~/config_sdk_signing_server.sh -C ~/work/FunSDK http://localhost
Replaced 1 occurrence(s) to "http://localhost"
```

Using a team server:

```sh
$ ~/config_sdk_signing_server.sh -C ~/work/FunSDK https://teamserver.mycompany.com:8080
Replaced 1 occurrence(s) to "https://teamserver.mycompany.com:8080"
```

Using a team server (current directory is Fungible SDK)

```sh 
$ ./config_sdk_signing_server.sh https://teamserver.mycompany.com:8080
Replaced 1 occurrence(s) to "https://teamserver.mycompany.com:8080"
```


#### Note:
The configuration client can be used multiple times on the same Fungible SDK to change/correct the URL of the Signing Server.
