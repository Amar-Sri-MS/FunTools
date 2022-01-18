#!/usr/bin/env python2.7
#
#  start_client.py
#
#  Created by eddie.ruan@fungible.com on 2018 05-11
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#

import os
import time
import errno
import sys
sys.path.append(os.getcwd())
import subprocess


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

def main():
    cmd = pipenv_cmd + ' run ./client.py'
    try:
        return subprocess.call(cmd, shell=True)
    except:
        return 1
    
if __name__ == '__main__':
    main()
