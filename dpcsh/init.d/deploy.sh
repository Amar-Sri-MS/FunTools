#!/bin/bash -e

_DPCSH_STARTUP_ID=${DPCSH_STARTUP_ID:-55}
_DPCSH_DEBUG_STARTUP_ID=${DPCSH_DEBUG_STARTUP_ID:-56}

mkdir -p $DEPLOY_ROOT/usr/bin
install ${DPCSH_INSTALL_DIR}/{dpcsh,dpc_client.py,dpc_utils.py,dpctest.py,dpc_uboot_env.py,binary_json.py,dpc_binary.py,auth_firmware.py} $DEPLOY_ROOT/usr/bin
cp ${DPCSH_INSTALL_DIR}/init.d/{dpc-debug,dpc} ${DEPLOY_ROOT}/etc/init.d
mkdir -p ${DEPLOY_ROOT}/etc/rc5.d
cd ${DEPLOY_ROOT}/etc/rc5.d
ln -sf ../init.d/dpc S${_DPCSH_STARTUP_ID}dpc
ln -sf ../init.d/dpc-debug S${_DPCSH_DEBUG_STARTUP_ID}dpc-debug

ln -sf ../init.d/dpc-libfunq S${_DPCSH_STARTUP_ID}dpc-libfunq
ln -sf ../init.d/dpc-libfunq-debug S${_DPCSH_DEBUG_STARTUP_ID}dpc-libfunq-debug
