#!/bin/bash

my_sku=unknown
if [ -e /sys/firmware/devicetree/base/fungible,sku ] ; then
    read -d $'\0' my_sku rest_of_line < /sys/firmware/devicetree/base/fungible,sku
fi
case "${my_sku}" in
    # mpg autodetection only required on SKUs that do not
    # have an onboard switch
    # all FC cards
    # S1 bringup board
    fc50* | fc100* | fc200* | \
    ds200* | s1_dev_board* )
    ;;

    *)
    # nothing to do on unsupported platforms
    exit 0
    ;;
esac

if [ -f /tmp/uboot_mpg_update_disable ]; then
    logger -p debug "mpg_update: suspended on user request"
    exit 0
fi

CURRENT_MPG_TYPE=$(dpcsh -Q port linkstatus | jq -r ".result[] | select (.phyport | contains (\"MPG\")) | .speed")

if [ $? -ne 0 ]; then
    logger -p warn "mpg_update: failed to read current mpg config"
    exit 1
fi

case "$CURRENT_MPG_TYPE" in
10G | 1G )
    #
    ;;
* )
    logger -p warn "mpg_update: unhandled mpg type $CURRENT_MPG_TYPE"
    exit 1
esac

SAVED_MPG_TYPE=$(dpcsh -Q uboot env_read | jq -Mr .result.MPG_RATE)

if [ "$CURRENT_MPG_TYPE" != "$SAVED_MPG_TYPE" ]; then
    dpcsh -Q uboot env_set MPG_RATE \"$CURRENT_MPG_TYPE\" > /dev/null
    dpcsh -Q uboot env_write > /dev/null
fi
