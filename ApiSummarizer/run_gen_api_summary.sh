#!/bin/bash

# helper script to extract only function prototype from FunSDK header files
# NOTE: that the path to the FunSDK is hardcoded

set -e

if [ $# -eq 0 ]; then
    echo "Missing file name argument without extention"
    echo ""
    echo "./run_gen_api_summary.sh <file_name_without_extention>"

    exit 1
fi

RAW_SUMMARY=$1
RAW_YML_SUMMARY="$1.yml"
RAW_H_SUMMARY="$1.h"
EXTRACTED_H_SUMMARY="$1.func_proto"
EXTRACTED_CSV_TBL="$1.csv"

# ==========================
# generate raw summary
# ==========================
go run main.go ../../FunSDK/FunSDK/funosrt/include/FunOS/  > "$RAW_H_SUMMARY"

# generate raw summary in yml format
go run main.go ../../FunSDK/FunSDK/funosrt/include/FunOS/  -y > "$RAW_YML_SUMMARY"
# post process the yml file
egrep -v '\- }|\- {|-  {|static inline void$|static inline void \*$' "$RAW_YML_SUMMARY" > "$RAW_YML_SUMMARY.tmp"
mv "$RAW_YML_SUMMARY.tmp" "$RAW_YML_SUMMARY"
egrep '^\.|^  -' "$RAW_YML_SUMMARY" > "$RAW_YML_SUMMARY.tmp"
mv "$RAW_YML_SUMMARY.tmp" "$RAW_YML_SUMMARY"

# ==========================
# extract function prototype
# ==========================

# run preprocessing before ctags
# - remove static_assert. This is not properly extracted by ctags
grep -v ^static_assert $RAW_H_SUMMARY > "$RAW_H_SUMMARY.tmp"
mv "$RAW_H_SUMMARY.tmp" $RAW_H_SUMMARY

# extract funtion proto type only
# ctags: Exuberant Ctags 5.8 or above version
# kinds: p:prototype, f:function
ctags -x --c-kinds=pf $RAW_H_SUMMARY >  $EXTRACTED_H_SUMMARY
# ctags -x --c-kinds=pf $RAW_H_SUMMARY | cut -f -1 -d " " >  $EXTRACTED_H_SUMMARY

# run post processing
# - remove ^ALIGNED, ^BITMAP. These are not properly extraced by ctag
grep -v ^ALIGNED    $EXTRACTED_H_SUMMARY > "$EXTRACTED_H_SUMMARY.tmp"
mv "$EXTRACTED_H_SUMMARY.tmp" $EXTRACTED_H_SUMMARY

grep -v ^BITMAP     $EXTRACTED_H_SUMMARY > "$EXTRACTED_H_SUMMARY.tmp"
mv "$EXTRACTED_H_SUMMARY.tmp" $EXTRACTED_H_SUMMARY

# ==========================
# Process the raw summary and generate the summary yml
# - yml generated previously does include more than function prototypes
# - the following script will extract only function prototypes
# ==========================

python3 ./process_api_summary.py --raw_input $RAW_YML_SUMMARY --proto $EXTRACTED_H_SUMMARY --output_csv $EXTRACTED_CSV_TBL

rm $RAW_YML_SUMMARY

echo ""
echo "Generated files:"
echo "================"
echo "Raw funtion header:           $RAW_H_SUMMARY"
echo "Extracted funtion proto:      $EXTRACTED_H_SUMMARY"
echo "Extracted funtion proto tbl:  $EXTRACTED_CSV_TBL"
