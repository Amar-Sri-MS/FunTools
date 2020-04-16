#!/bin/bash
#
# File: come_Ubuntu_setup.sh
# Copyright © 2020 Fungible. All rights reserved.
#
# Do install time setup

# Macros
FUN_ENV='/etc/fungible.env' # env file with the system information
[ -f ${FUN_ENV} ] && source ${FUN_ENV}
FUNGIBLE_ROOT=${FUNGIBLE_ROOT:-/opt/fungible}

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as ROOT (CurrentEUID=$EUID)"
  exit 1
fi

Update_grub_cmdline()
{
  # debug                  = SWSYS-725
  # iommu                  = vfio support
  # fsck                   = Ubuntu FS corruption issues
  # systemd.log_level=info = SWSYS-754
  FUN_GRUB_CMD="debug console=tty0 console=ttyS0,115200n8 intel_iommu=on iommu=pt fsck.repair=yes fsck.mode=force systemd.log_level=info"
  GRUB_CONF=/etc/default/grub
  PATTERN="GRUB_CMDLINE_LINUX="
  if [ -f ${GRUB_CONF} ]; then
    grep ${PATTERN} ${GRUB_CONF} | grep iommu | grep fsck | grep debug | grep log_level > /dev/null
    RC=$?
    if [ ${RC} -ne 0  ]; then
      echo "Updating grub command line to $FUN_GRUB_CMD"
      /bin/sed -i "s/${PATTERN}.*/${PATTERN}\"${FUN_GRUB_CMD}\"/" ${GRUB_CONF}
      /usr/sbin/update-grub
    fi
  fi
}

Update_grub_cmdline

exit 0
