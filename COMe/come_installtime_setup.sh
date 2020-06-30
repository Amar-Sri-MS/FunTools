#!/bin/bash
#
# File: come_installtime_setup.sh
# Created by David Peet (david.peet@fungible.com)
# Copyright © 2020 Fungible. All rights reserved.
#
# Do install time setup
# 1. Set up fun user authorized_keys so BMC can ssh in.
# 2. Set up fun user passwordless sudo.
#
# Macros
FUN_ENV='/etc/fungible.env' # env file with the system information
[ -f ${FUN_ENV} ] && source ${FUN_ENV}
FUNGIBLE_ROOT=${FUNGIBLE_ROOT:-/opt/fungible}

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as ROOT (CurrentEUID=$EUID)"
  exit 1
fi

FACTORY_BMC_KEY_PUB="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDlbQy9N8gi4ruzFgENd7T6eNVa3m2OPHuzBD65tpD/0uviCwuL8NKUH+7UZPpbVDrpeE3iaP+a7MqZxplfS55U0S5ZjfX0n2cDtw9xi0PsQ+kdJdz4txyjo1Xbh+jGq2+FJgg4tH6jnx3RbEcIC9ng9xFuE4gywnXe0Bk5dVSJeS/qV4nKDAMPtjThjs7TKG8iXjsadq0h4PujXqXke4dI8VesStf4zzrP4tXAAkCXgqYD+VdPSqHqKbjUtW3Jn/sbEkBphpJStm7URBK0qwdMJBaldWm7y4DNZiyg1R5VvZ2b2xFjUwuLY76ph+W7s385V3UPcHGvDyf15LI4VoYv BMC"

# Make sure a BMC public key is in /home/fun/.ssh/authorized_keys.
# When none, add from either /opt/firmware/ssh/bmc_id_rsa.pub
# or the factory default.
Update_fun_user_ssh()
{
  sudo -u fun mkdir -p /home/fun/.ssh 
  chmod 700 /home/fun/.ssh
  if [ ! -f /home/fun/.ssh/authorized_keys ] ; then
    sudo -u fun touch /home/fun/.ssh/authorized_keys
  fi
  chmod 644 /home/fun/.ssh/authorized_keys
  cat /home/fun/.ssh/authorized_keys | awk '{print $3}' | grep -q '^BMC'
  HAS_BMC=${?}
  [ ${HAS_BMC} -eq 0 ] && return
  if [ -f /opt/firmware/ssh/bmc_id_rsa.pub ] ; then
    cat /opt/firmware/ssh/bmc_id_rsa.pub >> /home/fun/.ssh/authorized_keys
  else
    echo "${FACTORY_BMC_KEY_PUB}" >> /home/fun/.ssh/authorized_keys
  fi
}

Ensure_come_rsa_id()
{
  if [ ! -f /home/fun/.ssh/id_rsa ] ; then
    sudo -u fun ssh-keygen -t rsa -f /home/fun/.ssh/id_rsa -P '' 2> /dev/null > /dev/null
  fi
}

Update_sudoer()
{
    echo 'fun ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/fun
    chmod 600 /etc/sudoers.d/fun
}

Update_netplan()
{
  [ ! -f /opt/fungible/third_party/ubuntu/update_netplan.sh ] && return
  cd /opt/fungible/third_party/ubuntu
  bash ./update_netplan.sh
}

# SWLINUX-1346: 
# Remove the cron job which will set the F1 management port IP
# Setting the IP is now done by cclinux
# The cron job is configured during system bundle install which
# is already addresses. Removing previously configured cron jobs
rm -f /etc/cron.d/sys_mgmt

Update_fun_user_ssh
Ensure_come_rsa_id
Update_sudoer
Update_netplan
exit 0
