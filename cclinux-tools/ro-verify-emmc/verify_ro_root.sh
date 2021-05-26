#!/bin/sh

build_version=$(cat /etc/version.build | tr "\n" " ")
rootfs_version=$(grep "cc-linux-rootfs-ro" /etc/version.sdk)
echo "RootFS build details: $build_version $rootfs_version"

state_file="/tmp/.verify_ro_root.state"

echo IN_PROGRESS > $state_file

rootfs_size=$(python3 <<SCRIPT
import struct
try:
  with open("/dev/vda4", "rb") as f:
    f.seek(4176, 0)
    print("{}".format(struct.unpack("<L", f.read(4))[0]))
except:
  print("0")

SCRIPT
)

if [ "$rootfs_size" == 0 ]; then
  echo FAIL > $state_file
  exit 0
fi

echo "Start rootfs verification, data size: $rootfs_size"

dd status=none if=/dev/vda2 of=/dev/null bs=$rootfs_size count=1

status=$?

if [ $status -eq 0 ]; then
  echo OK > $state_file
else
  echo FAIL > $state_file
fi

exit 0
