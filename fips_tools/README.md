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

The cavp.py can be used to run the test locally. This mode is useful to test on the POSIX platform.

`./cavp.py -t DPCCAVP <test_files>
`

### Posix

To test on the POSIX platform, copy the `dpc_client.py` from the dpcsh directory in the same directory as `cavp.py`.

Start FunOS as a DPC server:

```sh
./build/funos-posix --dpc-server
```

Start a dpcsh process (macOS example):

```sh
./bin/Darwin/dpcsh -T
```

And then run the `cavp.py` program.

```sh
./cavp.py -t DPCCAVP <test_files>
```

## Remote Testing

This is the mode used for real testing on the real hardware. In that mode, the `cavp.py` is executed as a remote PCI script.

The remote refers to the fact that the file must be stored remotely, on a WebDav server.

Example:

```sh
cavp.py --remote http://ferino-vm1.fungible.local/webdav -t DPCCAVP -u <webdav_user> -p <webdav_password> responses/sha2/132238/SHA-1.408819.req.json
```

It is more convenient to place the `cavp.py` script in a server directory with a parameter file:


```
# NAME is required as it is used as usrname
NAME : F1 CAVP Test
# At least one email is required in EXTRA_EMAIL for sending failures
EXTRA_EMAIL : fabrice.ferino@fungible.com

HW_MODEL : F1Endpoint
PRIORITY : normal_priority
RUN_TARGET : F1
FAST_EXIT : false
MAX_DURATION : 30

# Optional params
TAGS : team_lostsouls, CAVP Test, F1Endpoint
NOTE : CAVP Test
BOOTARGS : app=load_mods --dpc-server
REMOTE_SCRIPT: cavp.py --remote http://ferino-vm1.fungible.local/webdav -t DPCCAVP -u <user> -p <password> responses/sha2/132238/SHA-1.408819_trunc.req.json
```

And then start the job:

```sh
 ~robotpal/bin/run_f1.py --params ../run_upgrade/cavp_test_short_sha1.params funos-f1.signed
```

## Other options	

`cavp.py` has a `-s, --suffix-test-type` option that can be used to pass more information to the tester so that the test can be dispatched to the proper implementation.
