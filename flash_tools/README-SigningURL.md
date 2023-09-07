# Fungible SDK Signing Server

The Fungible SDK is configured by default to use the Fungible Intranet signing server.

This file explains how to configure the SDK to use another Signing Server.

(Fungible provide a Simple Signing Server that can be installed almost anywhere and that exposes the Fungible Signing API using a set of development keys that are only valid on development DPUs. This is explained in the companion file README-ServerInstallation.md).

## Client configuration

To use another Signing Server instance with the Fungible SDK, edit or create the file ```signing.ini`` in the ```.config``` subdirectory of your home directory.

Specify the new URL for the server by adding a line in this file:

```server_url = [DESIRED_SIGNING_SERVER_HTTP_URL]```

#### Examples:

Using a server installed on the same machine:


```sh
server_url = http://localhost
```

Using a team server:

```sh
server_url = https://teamserver.mycompany.com:8080
```
