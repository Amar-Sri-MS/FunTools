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

# SWSYS-890: Disable the redis-server on COMe host OS
# cclinux is having it's own copy inside the docker
Update_disable_redis_server
{
  systemctl disable redis-server > /dev/null 2>&1
}

# SWSYS-874:
Update_resolv_conf_smlink()
{
  PREFERRED_RESOLV_CONF=/run/systemd/resolve/resolv.conf
  RESOLV_CONF=/etc/resolv.conf
  if [ "$(realpath $RESOLV_CONF)" != "$PREFERRED_RESOLV_CONF" ]; then
    rm $RESOLV_CONF
    ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
    # Is below step required?
    # Because after install user will reboot
    systemctl restart systemd-resolved
  fi
}

# SWSYS-845: Disabling use of journal logs
# Logging in /var/log/syslog etc will still work
Update_systemd_journal_cfg()
{
  JRNLD_CFG=/etc/systemd/journald.conf
  if [ ! -f ${JRNLD_CFG} ]; then
    return
  fi
  sed -i 's/^#Storage=.*/Storage=none/g' ${JRNLD_CFG}
  if [ -d /var/log/journal ]; then
    DATE=`date +%Y-%m-%d_%H-%M-%S`
    mv /var/log/journal /var/log/journal_${DATE}_FUN_BKP
  fi
}

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

Update_Fungible_systemd_services()
{
  # All or none
  if [ ! -f ${FUNGIBLE_ROOT}/etc/come_heartbeat_server.py ]       ||
     [ ! -f ${FUNGIBLE_ROOT}/etc/come_heartbeat_server.socket ]   ||
     [ ! -f ${FUNGIBLE_ROOT}/etc/come_heartbeat_server@.service ] ||
     [ ! -f ${FUNGIBLE_ROOT}/etc/come_start_heartbeat_server.service ]; then
    return
  fi

  cp ${FUNGIBLE_ROOT}/etc/come_heartbeat_server.socket /lib/systemd/system/
  chmod 644 /lib/systemd/system/come_heartbeat_server.socket
  cp ${FUNGIBLE_ROOT}/etc/come_heartbeat_server@.service /lib/systemd/system/
  chmod 644 /lib/systemd/system/come_heartbeat_server@.service
  cp ${FUNGIBLE_ROOT}/etc/come_start_heartbeat_server.service /lib/systemd/system/
  chmod 644 /lib/systemd/system/come_start_heartbeat_server.service

  SERVICE_STATUS=`systemctl is-enabled come_start_heartbeat_server.service`
  if [ "${SERVICE_STATUS}" != "enabled" ]; then
    systemctl enable come_start_heartbeat_server.service
    RC=$?
    if [ ${RC} -ne 0 ]; then
      echo "Failed to enable COMe heartbeat server (${RC})"
    fi
  fi
}

Update_timesyncd()
{
  TIMESYNCD_CONF=/etc/systemd/timesyncd.conf
  if [[ -f ${TIMESYNCD_CONF} ]]; then
    cat ${TIMESYNCD_CONF} | grep "^FallbackNTP" | grep -q "192.168.127.2"
    if [[ ${?} -ne 0 ]]; then
      /bin/sed -i '/.*FallbackNTP.*/d' ${TIMESYNCD_CONF}
      echo "FallbackNTP=192.168.127.2" >> ${TIMESYNCD_CONF}
    fi
  fi
}

Update_systemd_journal_cfg

Update_grub_cmdline

Update_Fungible_systemd_services

Update_resolv_conf_smlink

Update_disable_redis_server

Update_timesyncd

exit 0
