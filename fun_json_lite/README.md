# fun_json_lite

Minimalistic fun_json encoder/decoder implementation targeted for UEFI environment does not allocate memory, using strlen, memcpy

To test run:
```bash
$ ./run_tests.py
test-double.bjson -- OK
test-empty-string.bjson -- OK
test-dict-complex.bjson -- OK
...
```

To see a usage example, check fun_json_lite_tester.c