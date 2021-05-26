#!/bin/sh

funos_version=$(dpcsh -Q peek config/version | jq -r .result.FunSDK | sed 's/bld_//')
rootfs_version=$(sed -n 's/cc-linux-rootfs-ro=\(.\)/\1/p' /etc/version.sdk)

if [ "$funos_version" != "$rootfs_version" ]; then
  echo "FunOS and RootFS version mismatch: $funos_version != $rootfs_version"
  exit 1
fi

exit 0
