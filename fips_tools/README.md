# CAVP Testing

`cavp.py` is the main script used for running CAVP tests. It takes a 'request' file (extension `'.req.json'`), parses it, sends individual tests to a Tester class, and writes the results into a 'response' file (extension `'.rsp.json'`) in the same directory as the request file.

2 Tester classes are provided: 

* TestTester class that returns always the same canned answer
* DPCCAVP class that uses DPC to send the test to FunOS.


## Dummy Testing

The cavp.py will execute a dummy testing by default using the TestTester class. 

This mode is to verify that `cavp.py` is able to parse the test file correctly.

```sh
./cavp.py <test_files>
```
## Local Testing

The cavp.py can be used to run the test locally. This mode is useful to test on the POSIX platform:

### Posix

To test on the POSIX platform, copy the `dpc_client.py` from the dpcsh directory in the same directory as `cavp.py`.

Start FunOS as a DPC server:

```sh
./build/funos-f1-posix --dpc-server
```

Start a dpcsh process (macOS example):

```sh
./bin/Darwin/dpcsh -T
```

The `dpcsh` program will print the port it listens to:

```
2023-02-01T17:15:22.355722Z INF FunSDK version bld_19335, branch: 725b16e
2023-02-01T17:15:22.357369Z INF connecting server socket
Publishing on port 40221
```

And then run the `cavp.py` program using the `--dpc-port` option to indicate the port:

```sh
./cavp.py --dpc-port 40221 -t DPCCAVP <test_files>
```

## Remote Testing

This is the mode used for real testing on the real hardware. 

The remote refers to the fact that the file must be stored remotely, on a WebDav server.

Example:

```sh
cavp.py --remote http://<someserver>/webdav -t DPCCAVP -u <webdav_user> -p <webdav_password> responses/sha2/132238/SHA-1.408819.req.json
```

An alternate syntax allows to specify the full path as the `--remote` option:

```sh
cavp.py -t DPCCAVP -u <webdav_user> -p <webdav_password> --remote http://<someserver>/webdav/responses/sha2/132238/SHA-1.408819.req.json
```

Here is an example of a parameter file to use with a local copy of `cavp.py`:

```
# NAME is required as it is used as usrname
NAME : F1 CAVP Test
# At least one email is required in EXTRA_EMAIL for sending failures
EXTRA_EMAIL : fabrice.ferino@fungible.com

HW_MODEL : F1
PRIORITY : normal_priority
RUN_TARGET : F1
FAST_EXIT : false
MAX_DURATION : 30

TAGS : CAVP Test
NOTE : CAVP Test
BOOTARGS : app=load_mods --dpc-server
CENTRAL_SCRIPT: cavp.py --remote http://ferino-vm1.fungible.local/webdav -t DPCCAVP -u <user> -p <password> responses/sha2/132238/SHA-1.408819_trunc.req.json
```

And then start the job:

```sh
 ~robotpal/bin/run_f1.py --params ../run_upgrade/cavp_test_short_sha1.params funos-f1.signed
```

Note that a `run_f1.py` feature is that it will strip the path to the script if it cannot be found. So the CENTRAL_SCRIPT line could use the FunSDK path to cavp.py and will still load the local script which allows local testing for development. Prefixing with the FunSDK path is useful to run from Jenkins. So the sample file `cavp.params` is using the FunSDK prefix.

```
CENTRAL_SCRIPT: FunSDK/bin/fips_tools/cavp.py --remote http://ferino-vm1.fungible.local/webdav -t DPCCAVP -u <user> -p <password> responses/sha2/132238/SHA-1.408819_trunc.req.json
```


## Other options	

`cavp.py` has a `-s, --suffix-test-type` option that can be used to pass more information to the tester so that the test can be dispatched to the proper implementation.
