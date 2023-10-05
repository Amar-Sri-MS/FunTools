#! /bin/bash -e

SDK_DIR=../../

csr2_chips=(s1 f1d1 s2)

#Check for PWD , needs to be invoked from FunTools/dbgutils directory
if [[ "$PWD" != */FunTools/dbgutils ]]; then
    echo "Not in FunTools/dbgutils directory. Exiting."
    exit 1
fi

mkdir -p ./bundles
mkdir -p ./FunHW
mkdir -p ./FunHW/csr2api
mkdir -p ./FunSDK
mkdir -p ./FunSDK/config

cp -r $SDK_DIR/FunHW/csr2api/v2 ./FunHW/csr2api/
cp -r $SDK_DIR/FunSDK/config/csr/ ./FunSDK/config

for item in "${csr2_chips[@]}"; do
    echo "chip_$item::root"
    mkdir -p ./bundles/$item
    $SDK_DIR/FunHW/csr2api/v2/csr2bundle.py chip_$item::root -I $SDK_DIR/FunSDK/FunSDK/chip/$item/csr -o ./bundles/$item/bundle.json -n $item
done

current_date_time=$(date +"%Y%m%d_%H%M%S")

echo "Building docker container  for dbgsh"
docker build -t dbgsh:${current_date_time} .

#Delete the temporay bundles and FunHW
rm -rf ./bundles
rm -rf ./FunHW
rm -rf ./FunSDK
