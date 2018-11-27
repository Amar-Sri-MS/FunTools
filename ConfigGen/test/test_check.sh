#!/bin/bash

#
# compare the generated files with expected genrated file
#

if [ "$#" -ne 2 ]; then
	echo "Usage: $1 TEST_OUTPUT_DIR REFERENC_OUTPUT_DIR"
	exit -1
fi

echo "START: testing generated files with expected output.."
echo "generated files at: $1"
echo "reference files at: $2"
INPUT_DIR=$1
EXPECTED_DIR=$2

for filename in $INPUT_DIR/*; do
	base_filename=$(basename $filename)
	grep -v \/\/ $INPUT_DIR/$base_filename > $INPUT_DIR/$base_filename.tmp
	grep -v \/\/ $EXPECTED_DIR/$base_filename > $EXPECTED_DIR/$base_filename.tmp
	cmp --silent $INPUT_DIR/$base_filename.tmp $EXPECTED_DIR/$base_filename.tmp
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "Generated file differ with expected output $INPUT_DIR/$base_filename.tmp $EXPECTED_DIR/$base_filename.tmp"
		exit -1
	fi
	echo "PASSED: $INPUT_DIR/$base_filename"

	rm $INPUT_DIR/$base_filename.tmp $EXPECTED_DIR/$base_filename.tmp
done

echo ""
echo "DONE: all generated files are matched with expected output files"
