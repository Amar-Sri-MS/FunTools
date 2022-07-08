#!/usr/bin/env python3
"""Run a single commnnd """

"""
# start dpcsh with tcp proxy mode
./bin/Darwin/dpcsh -cfs800-20*-cc:4223 -T 40221 


cd ~/Projects/Fng/Integration/tools/dpcsh_interactive_client/src
export WORKSPACE=~/Projects/Fng/Integration
export PYTHONPATH=.:$PYTHONPATH

python ./funos_stats_analysis/run_fun_malloc_slot.py

"""


from dpcsh_interactive_client.funos_commands import *
from dpcsh_interactive_client.dpc_client import *

target_ip = "localhost"
target_port = 40221
verbose = False

dpc_client = DpcClient(target_ip=target_ip, target_port=target_port, verbose=verbose)
funos_cmd_obj = FunOSCommands(dpc_client=dpc_client)
for i in range(2):
    funos_cmd_obj.peek_fun_malloc_slot_stats(non_coh=i, from_cli=False)
