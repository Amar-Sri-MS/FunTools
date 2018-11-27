This test folder contains snapshot of FunOS config files for hu and hw_cap, as well as expected generated c and h files.
Note that the config files in this folder are only for testing they are in FunOS repository and will be updated as part of the FunOS repository.

The test is done as part of `make test_hucfggen`, it will generate files based on the snapshot config files in `test` directory, and compare the output with expected files in `generated_reference`. This test will ensure code gen script to generate expected output.

