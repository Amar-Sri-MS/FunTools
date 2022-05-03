#!/bin/bash
#
# Install all the scripts needed for host_test_tools.
#
# Because host_test_tools is only used to build other scripts into
# a deploy image, we only need to install our deploy script which
# assembles the archive.

mkdir -p ${SDK_INSTALL_DIR}/bin/scripts
cp deploy_host_test_tools.sh ${SDK_INSTALL_DIR}/bin/scripts/deploy_host_test_tools.sh
