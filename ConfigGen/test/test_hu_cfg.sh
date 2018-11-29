#!/bin/bash

#
# compare the output from executable with generated C struct with
# the output from json parsed output
#

DEFAULT_JSON=../out/default.cfg
TEST_HU_CFG_C_OUT=test_hu_cfg_c_out
TEST_HU_CFG_JSON_OUT=test_hu_cfg_JSON_out

echo ""
echo "START: testing generated hu cconfig with expected output.."

# output from generated C file
make clean
make
./test_hu_cfg > $TEST_HU_CFG_C_OUT 

# output from jason file
python ./test_hu_cfg.py -c $DEFAULT_JSON > $TEST_HU_CFG_JSON_OUT

cmp --silent $TEST_HU_CFG_C_OUT $TEST_HU_CFG_JSON_OUT
ret=$?
if [ $ret -ne 0 ]; then
        echo "Generated file differ with expected output $TEST_HU_CFG_C_OUT $TEST_HU_CFG_JSON_OUT"
        exit -1
fi

rm $TEST_HU_CFG_C_OUT $TEST_HU_CFG_JSON_OUT

echo ""
echo "DONE: testing generated hu cconfig with expected output"
