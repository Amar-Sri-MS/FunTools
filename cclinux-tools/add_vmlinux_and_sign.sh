#/bin/bash -e


function usage() {
    echo "Usage: $0 fun-os-image-name [vmlinux.bin-url]"
    exit 1
    }

if [ -z "${WORKSPACE}" ]; then
    export WORKSPACE=`pwd`
    echo "WORKSPACE is not set, using ${WORKSPACE}"
else
    echo "WORKSPACE ${WORKSPACE}"
fi
if [ -z "${SDKDIR}" ]; then
    SDKDIR=${WORKSPACE}/FunSDK
fi

XDATA_PY=${SDKDIR}/bin/scripts/xdata.py

if [ ! -x $XDATA_PY ]; then
    echo "Error: No $XDATA_PY"
    exit 1
fi

if [ $# -lt 1 ] ; then
    usage
fi
image_name=$1
image_name_stripped=${image_name}.stripped

echo "Using image: $image_name"

if [ -f $SDKDIR/bin/$image_name_stripped ] ; then
    source_image=$image_name_stripped
elif [ -f $SDKDIR/bin/$image_name ] ; then
    source_image=$image_name
else
    echo "Not found: $image_name"
    exit 1
fi

if [ $# -ge 2 ] ; then
    vmlinux_url=$2
else
    vmlinux_url='http://dochub.fungible.local/doc/jenkins/master/cc-linux-yocto/latest/mips64hv/vmlinux.bin'
fi

tmp_image=`mktemp ${source_image}.XXXXX`
signed_image=${image_name}.signed

cp $SDKDIR/bin/$source_image $tmp_image

curl -s -f --output vmlinux.bin $vmlinux_url

$SDKDIR/bin/scripts/xdata.py $tmp_image add vmlinux.bin

sed -e "s/funos-f1.stripped/$tmp_image/" -e "s/funos.signed.bin/$signed_image/g" $SDKDIR/bin/flash_tools/mmc_config_fungible.json > $tmp_image.json

$SDKDIR/bin/flash_tools/generate_flash.py --action sign $SDKDIR/bin/flash_tools/key_bag_config.json $tmp_image.json

rm $tmp_image.json
rm -f $tmp_image vmlinux.bin
