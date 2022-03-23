#!/usr/bin/env python3

import sys
import os

SCRIPT_PATH = "/home/cgray/silicon_on_demand"
sys.path.append(SCRIPT_PATH)

import silicon_on_demand_server

os.chdir(SCRIPT_PATH)
silicon_on_demand_server.sod_client()

