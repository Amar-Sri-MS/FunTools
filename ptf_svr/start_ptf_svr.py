#!/usr/bin/env python3
#
#  start_ptf_svr.py
#
#  Created by eddie.ruan@fungible.com on 2018 05-11
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#

import argparse
import os
import time
import errno
import sys
sys.path.append(os.getcwd())
import subprocess
import platform
import json

#
# DOCKER is optional. 
#
env_docker = os.environ.get('DOCKER')

#
# Prepare PTF command with virtual env
#
# Add user bin path for internal pipenv operations.
user_bin_path = os.getenv("HOME") + "/.local/bin"
pipenv_env_vars = "PATH=" + user_bin_path + ":$PATH PIPENV_MAX_DEPTH=16"

if env_docker:
    pipenv_env_vars = pipenv_env_vars + " PYTHONUSERBASE=/fun_external"
pipenv_cmd = "env " + pipenv_env_vars + " pipenv"

try:
    venv_path = subprocess.check_output(pipenv_cmd + " --venv",
                                        shell=True).strip()
    # We have venv. Use it to figure out how to run PTF automatically.
    # ptf_path allows scripts using ptf to check if we actually have PTF
    # installed in both venv and non-venv case.
    ptf_path = venv_path + "/bin/ptf"
    ptf_cmd = "sudo -E " + pipenv_cmd + " run ptf"
except subprocess.CalledProcessError:
    # This is not fatal until we start using the venv, which not every command
    # uses. Just point things at the old root install and hope for the best.
    ptf_path = "/usr/local/bin/ptf"
    ptf_cmd = "sudo -E " + ptf_path

#
# Log files location
#
logdir = "./logs"
if not os.path.exists(logdir):
            os.makedirs(logdir)
logfile= logdir+"/ptf_svr.log"
psim_logfile= logdir+"/psim_ptf_svr.log"
f = open(psim_logfile, 'w')
if f:
    f.write('\n\n>>>>>>Start test %s' % time.ctime())

ptf_testcases_loc= os.path.dirname(os.path.realpath(__file__))
testcase =""
intf_map_file=ptf_testcases_loc+"/intf_map.json"

#
# Start to trigger PTF dummy test case for launching this server
#
def run_testcase(ptf_testcases_loc, testcase_name, intf_map_file,
                 psim_log_file=None, logfile=None):

    if not os.path.isfile(ptf_path):
        if logfile is not None:
            lfile = open(logfile, 'a')
            lfile.write("FAILED: Can't find PTF in " + ptf_path)
            lfile.close()
        raise RuntimeError('PTF not found in '+ptf_path + '. Please do a "pipenv install" as the right user.')

    #
    # intf_map.json provides UUT port name to PTF port # mapping
    #
    intf_map = json.load(open(intf_map_file))
    interfaces = ''
    for intf_name, intf in intf_map.items():
        interfaces = interfaces + ''.join(' --interface %s@%s' % (intf['id'], intf_name))

    cmd = "%s --test-dir %s %s --relax --log-file %s --debug debug %s " % (
        ptf_cmd, ptf_testcases_loc, interfaces,
        logfile, testcase_name)
    if psim_log_file:
        cmd += ' --test-params="intf_map_file=\'' + intf_map_file + '\';mode=\'psim\'' + ';psim_log_file=\'' + psim_log_file + '\'"'
    else:
        cmd += ' --test-params="intf_map_file=\'' + intf_map_file + '\';mode=\'psim\'' + '"'

    print("\nStart Traffic: %s" % cmd)
    try:
        return subprocess.call(cmd, shell=True)
    except:
        return 1

#
# Main
#
def main():
    run_testcase(ptf_testcases_loc, testcase, intf_map_file, psim_logfile, logfile)
    
if __name__ == '__main__':
    main()
