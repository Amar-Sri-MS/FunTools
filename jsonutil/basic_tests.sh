#!/bin/bash -e

TESTFILE=$PWD/test.json

cat << TESTJSON > $TESTFILE
{
   "key1":"value1",
   "key2":"value2",
   "key3":["arr1", "arr2", "arr3"],
   "key4": {
      "subkey1":"subvalue1",
      "subkey2":"subvalue2"
   }
}
TESTJSON


# binary output
./jsonutil -i $TESTFILE -O $TESTFILE.bin
# base64 output
./jsonutil -i $TESTFILE -E $TESTFILE.base64
# oneline output
./jsonutil -i $TESTFILE -l $TESTFILE.oneline

# now try to convert all outputs back to standard text
# binary input
./jsonutil -o $TESTFILE.bin.json -I $TESTFILE.bin
# base64 input 
./jsonutil -o $TESTFILE.base64.json -e $TESTFILE.base64
# oneline input (this is really just text)
./jsonutil -o $TESTFILE.oneline.json -i $TESTFILE.oneline

# normalize all jsons for easy comparison
cat $TESTFILE | jq -MS > $TESTFILE.1
cat $TESTFILE.oneline | jq -MS > $TESTFILE.2
cat $TESTFILE.bin.json | jq -MS > $TESTFILE.3
cat $TESTFILE.base64.json | jq -MS > $TESTFILE.4
cat $TESTFILE.oneline.json | jq -MS > $TESTFILE.5

# all json testfiles should now be the same ...
for f in `seq 1 4`; do
  diff -q $TESTFILE.$f $TESTFILE.$((f+1))
done

echo All tests PASSED
rm $TESTFILE*
