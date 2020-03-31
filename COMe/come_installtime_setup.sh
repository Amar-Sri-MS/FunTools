#!/bin/bash
#
# File: come_installtime_setup.sh
# Created by David Peet (david.peet@fungible.com)
# Copyright © 2020 Fungible. All rights reserved.
#
# Do install time setup
# 1. Add to cron: run come_config_mgmt.sh once an hour
# 2. Set up fun user authorized_keys so BMC can ssh in.
#
# Macros
FUN_ENV='/etc/fungible.env' # env file with the system information
[ -f ${FUN_ENV} ] && source ${FUN_ENV}
FUNGIBLE_ROOT=${FUNGIBLE_ROOT:-/opt/fungible}

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as ROOT (CurrentEUID=$EUID)"
  exit 1
fi

cat << EOF > /etc/cron.d/sys_mgmt
# Run 14 minutes after every hour
14 * * * *   root    test -x /opt/fungible/etc/come_config_mgmt.sh && /opt/fungible/etc/come_config_mgmt.sh
EOF
chmod 644 /etc/cron.d/sys_mgmt

BMC_KEY_PUB="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDlbQy9N8gi4ruzFgENd7T6eNVa3m2OPHuzBD65tpD/0uviCwuL8NKUH+7UZPpbVDrpeE3iaP+a7MqZxplfS55U0S5ZjfX0n2cDtw9xi0PsQ+kdJdz4txyjo1Xbh+jGq2+FJgg4tH6jnx3RbEcIC9ng9xFuE4gywnXe0Bk5dVSJeS/qV4nKDAMPtjThjs7TKG8iXjsadq0h4PujXqXke4dI8VesStf4zzrP4tXAAkCXgqYD+VdPSqHqKbjUtW3Jn/sbEkBphpJStm7URBK0qwdMJBaldWm7y4DNZiyg1R5VvZ2b2xFjUwuLY76ph+W7s385V3UPcHGvDyf15LI4VoYv BMC"

Update_fun_user_ssh()
{
  if [[ -f /home/fun/.ssh/authorized_keys ]] ; then
    grep -q "${BMC_KEY_PUB}" /home/fun/.ssh/authorized_keys
    [ ${?} -eq 0 ] && return
  fi
  sudo -u fun mkdir -p /home/fun/.ssh 
  chmod 700         /home/fun/.ssh
  sudo -u fun touch /home/fun/.ssh/authorized_keys
  chmod 644      /home/fun/.ssh/authorized_keys
  echo "${BMC_KEY_PUB}" >> /home/fun/.ssh/authorized_keys
  if [ ! -f /home/fun/.ssh/id_rsa ] ; then
    sudo -u fun ssh-keygen -t rsa -f /home/fun/.ssh/id_rsa -P '' 2> /dev/null > /dev/null
  fi
}
Update_fun_user_ssh

exit 0
