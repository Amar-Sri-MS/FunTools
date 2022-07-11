#!/bin/bash
#
# This script is used for deploying dpcsh binary

mkdir -p $DEPLOY_ROOT/usr/bin

install bin/aarch64/Linux/dpcsh $DEPLOY_ROOT/usr/bin/

