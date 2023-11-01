# Signing Server

The signing server is a HTTPS server running on port 4443.


The URL is "[https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi](https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi)"


It implements the following commands:

## GET

GET requests are used to query the server for some information

### cmd=modulus

Returns the modulus of a key in various formats.

#### Arguments:

##### key (optional argument, default value: 'fpk4')

Specify the label of the key in the HSM. The modulus of this key is returned in the body of the response.

##### production (optional argument, default value: 0)

0: development security group
1: security group 1

(These are the only currently defined security groups)

##### format (optional argument, default value: 'binary')

Specify the format of the modulus in the response.

Possible values are:

* binary: raw bytes of the modulus

* public_key: a PUBLIC KEY PEM file compatible with OpenSSL

		-----BEGIN PUBLIC_KEY-----
		MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6AXllROlNJL+kxUl/Jen
		Qf3elTQkclTCJwi22l6nhzYNsz11b2kxzsKdXA9TfqrzJB64pqTb+cJEIMYtSoIc
		iw7zGbic4ByLaT82pIbf8BiFvh9dwhhPYfHWd5NUtoa7bQWPWJVhaTjzsNo7WQvK
		YV3TFM9zXu5913nV+gKNSs/ZaZ1E+ymyM7ijxCJOrU9xH5XIAGSh4o3EpXFmw7j5
		JzjqetOX+eBLnXQoK5iOAIQEXKOlph+EmNTI4vBnB+kKALa99g7dLT/QB+hcih5G
		rNe0nmmmKobvlAOTOVRM5V0PK7ruZCKfvBdPuFnPvUbC1OteB6ojOS2vG7nAuh7Q
		hwIDAQAB
		-----END PUBLIC_KEY-----

* hex: hexadecimal encoding of the bytes of the modulus

		e805e59513a53492fe931525fc97a741fdde9534247254c22708b6da5ea787360db33d756f6931cec29d5c0f537eaaf3241eb8a6a4dbf9c24420c62d4a821c8b0ef319b89ce01c8b693f36a486dff01885be1f5dc2184f61f1d6779354b686bb6d058f5895616938f3b0da3b590bca615dd314cf735eee7dd779d5fa028d4acfd9699d44fb29b233b8a3c4224ead4f711f95c80064a1e28dc4a57166c3b8f92738ea7ad397f9e04b9d74282b988e0084045ca3a5a61f8498d4c8e2f06707e90a00b6bdf60edd2d3fd007e85c8a1e46acd7b49e69a62a86ef94039339544ce55d0f2bbaee64229fbc174fb859cfbd46c2d4eb5e07aa23392daf1bb9c0ba1ed087


* base64: base64 encoding of the bytes of the modulus

		6AXllROlNJL+kxUl/JenQf3elTQkclTCJwi22l6nhzYNsz11b2kxzsKdX
		A9TfqrzJB64pqTb+cJEIMYtSoIciw7zGbic4ByLaT82pIbf8BiFvh9dwh
		hPYfHWd5NUtoa7bQWPWJVhaTjzsNo7WQvKYV3TFM9zXu5913nV+gKNSs/
		ZaZ1E+ymyM7ijxCJOrU9xH5XIAGSh4o3EpXFmw7j5JzjqetOX+eBLnXQo
		K5iOAIQEXKOlph+EmNTI4vBnB+kKALa99g7dLT/QB+hcih5GrNe0nmmmK
		obvlAOTOVRM5V0PK7ruZCKfvBdPuFnPvUbC1OteB6ojOS2vG7nAuh7Qhw
		==

* c_struct: a "C" array representation of bytes of the modulus, preceded by its length

		256,
		{
		0xe8, 0x05, 0xe5, 0x95, 0x13, 0xa5, 0x34, 0x92,
		0xfe, 0x93, 0x15, 0x25, 0xfc, 0x97, 0xa7, 0x41,
		0xfd, 0xde, 0x95, 0x34, 0x24, 0x72, 0x54, 0xc2,
		0x27, 0x08, 0xb6, 0xda, 0x5e, 0xa7, 0x87, 0x36,
		0x0d, 0xb3, 0x3d, 0x75, 0x6f, 0x69, 0x31, 0xce,
		0xc2, 0x9d, 0x5c, 0x0f, 0x53, 0x7e, 0xaa, 0xf3,
		0x24, 0x1e, 0xb8, 0xa6, 0xa4, 0xdb, 0xf9, 0xc2,
		0x44, 0x20, 0xc6, 0x2d, 0x4a, 0x82, 0x1c, 0x8b,
		0x0e, 0xf3, 0x19, 0xb8, 0x9c, 0xe0, 0x1c, 0x8b,
		0x69, 0x3f, 0x36, 0xa4, 0x86, 0xdf, 0xf0, 0x18,
		0x85, 0xbe, 0x1f, 0x5d, 0xc2, 0x18, 0x4f, 0x61,
		0xf1, 0xd6, 0x77, 0x93, 0x54, 0xb6, 0x86, 0xbb,
		0x6d, 0x05, 0x8f, 0x58, 0x95, 0x61, 0x69, 0x38,
		0xf3, 0xb0, 0xda, 0x3b, 0x59, 0x0b, 0xca, 0x61,
		0x5d, 0xd3, 0x14, 0xcf, 0x73, 0x5e, 0xee, 0x7d,
		0xd7, 0x79, 0xd5, 0xfa, 0x02, 0x8d, 0x4a, 0xcf,
		0xd9, 0x69, 0x9d, 0x44, 0xfb, 0x29, 0xb2, 0x33,
		0xb8, 0xa3, 0xc4, 0x22, 0x4e, 0xad, 0x4f, 0x71,
		0x1f, 0x95, 0xc8, 0x00, 0x64, 0xa1, 0xe2, 0x8d,
		0xc4, 0xa5, 0x71, 0x66, 0xc3, 0xb8, 0xf9, 0x27,
		0x38, 0xea, 0x7a, 0xd3, 0x97, 0xf9, 0xe0, 0x4b,
		0x9d, 0x74, 0x28, 0x2b, 0x98, 0x8e, 0x00, 0x84,
		0x04, 0x5c, 0xa3, 0xa5, 0xa6, 0x1f, 0x84, 0x98,
		0xd4, 0xc8, 0xe2, 0xf0, 0x67, 0x07, 0xe9, 0x0a,
		0x00, 0xb6, 0xbd, 0xf6, 0x0e, 0xdd, 0x2d, 0x3f,
		0xd0, 0x07, 0xe8, 0x5c, 0x8a, 0x1e, 0x46, 0xac,
		0xd7, 0xb4, 0x9e, 0x69, 0xa6, 0x2a, 0x86, 0xef,
		0x94, 0x03, 0x93, 0x39, 0x54, 0x4c, 0xe5, 0x5d,
		0x0f, 0x2b, 0xba, 0xee, 0x64, 0x22, 0x9f, 0xbc,
		0x17, 0x4f, 0xb8, 0x59, 0xcf, 0xbd, 0x46, 0xc2,
		0xd4, 0xeb, 0x5e, 0x07, 0xaa, 0x23, 0x39, 0x2d,
		0xaf, 0x1b, 0xb9, 0xc0, 0xba, 0x1e, 0xd0, 0x87,
		}

## POST

The post request is used
1-to sign a single digest with the development or production keys.
2-to generate/retrieve debugging certificates

### Hash signing

#### Arguments:

##### digest (required)

The digest to package as a PKCS v1.5 signature.

##### algo (optional, default = 'sha512')

The hash algorithm that generated the digest.

##### modulus (optional)

The modulus of the RSA key used for signing.

##### key (optional)

Label identifying the key used for signing.


*NOTE: The two arguments modulus and key are optional but at least one of them must be provided.*

##### production (optional)

Identify the security group to use for the operation.

0: development HSM (default)
other groups requires TLS client authentication


### Debugging Certificate generation

#### Arguments

##### serial_number (required, 48 character hexadecimal string):

The serial number of the DPU

##### key (required, PEM public key):

Public key associated with the requested certificate




