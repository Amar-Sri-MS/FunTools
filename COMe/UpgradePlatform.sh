#!/bin/sh
#
# File: UpgradePlatform.sh
#
# Created by Ramanand Narayanan (ram.narayanan@fungible.com) on 09/30/2019
#
# Copyright © 2019 Fungible. All rights reserved.
#

#
# This script is expected to go through and upgrade the firmware of various
# non-F1 platform components if needed and log information for trackability
#

# Macros 
FUN_ENV='/etc/fungible.env' # env file with the system information
PROG='UpgradePlatform.sh'
FUNGIBLE_ROOT='/opt/fungible'
MODULE_LIST='BMC FPGA COMe' # TODO: Manage modules based on system type 
BMC_UPGRADE_TOOL='/opt/fungible/bmc/Yafuflash'


#
# fun_log (): Generic function to have a consistently formatted output 
#
fun_log() {
    echo "[`date '+%D %T'`]: $PROG $1";
} # end of fun_log()

#
# upgrade_bmc (): Function to handle the BMC upgrade
#
upgrade_bmc() {
    # fun_log "Starting BMC upgrade process ..."
    fun_log "<BMC upgrade not yet implemented>"
} # end of upgrade_bmc()


#
# Main logic begins here 
#
fun_log "Starting platform upgrade ..."

# Source the fungible system env file if it exists
if [ -f $FUN_ENV ]; then
    source $FUN_ENV
fi

# Let us upgrade module by module
for module in $MODULE_LIST
do
    case $module in
        "BMC")
            upgrade_bmc;
            ;;
        "FPGA")
            fun_log "<FPGA upgrade not yet implemented>"
            ;;
        "COMe")
            fun_log "<COMe upgrade not yet implemented>"
            ;;
    esac
done

# All good exit with a zero
fun_log "Platform upgrade process completed!!!"

exit 0

#
# End of UpgradePlatform.sh
#
