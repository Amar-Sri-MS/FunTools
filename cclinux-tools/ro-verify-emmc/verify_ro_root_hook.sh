#!/bin/sh

for delay in `seq 1 30`; do
  state=$(cat /tmp/.verify_ro_root.state)
  case $state in
  OK )
    echo "rootfs verified"
    exit 0
    ;;
  IN_PROGRESS )
    echo "rootfs verification still in progress, waiting ... ($delay/30)"
    /usr/bin/dpcsh -Q uboot boot { "in_progress":true } >/dev/null
    sleep 10
    ;;
  FAIL )
    echo "rootfs verification failed"
    exit 1
    ;;
  * )
    echo "rootfs verification: unexpected state"
    exit 1
    ;;
  esac
done

exit 1
