#!/bin/bash
#
# Collect files that need to go into host_test_tools component.
#
# These binaries and scripts are needed for 

mkdir -p $DEPLOY_ROOT/bin/scripts
mkdir -p $DEPLOY_ROOT/bin/Linux/x86_64

install bin/mips64/Linux/{dpc_client.py,dpc_binary.py,binary_json.py} $DEPLOY_ROOT/bin/scripts

# TODO(bowdidge):jsonutil, log_tools.
install bin/scripts/fungdbserver.py $DEPLOY_ROOT/bin/scripts

# TODO: FunTools/fungdbserver/hbm_unshard,ddr_unshard, etc.
install bin/Linux/x86_64/jsonutil $DEPLOY_ROOT/bin/Linux/x86_64/jsonutil

install ../FunSDK/dash_test_tools.tgz $DEPLOY_ROOT
