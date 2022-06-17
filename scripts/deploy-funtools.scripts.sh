#!/bin/sh

mkdir -p ${DEPLOY_ROOT}/usr/bin
cp bin/scripts/issu ${DEPLOY_ROOT}/usr/bin
chmod 0555 ${DEPLOY_ROOT}/usr/bin/issu
