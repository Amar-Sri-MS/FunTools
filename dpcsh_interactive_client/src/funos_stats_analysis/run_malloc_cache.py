#!/usr/bin/env python3

"""Run a single commnnd """

"""
# start dpcsh with tcp proxy mode
./bin/Darwin/dpcsh -cfs800-20*-cc:4223 -T 40221


cd ~/Projects/Fng/Integration/tools/dpcsh_interactive_client/src
export WORKSPACE=~/Projects/Fng/Integration
export PYTHONPATH=.:$PYTHONPATH

# NOTE: runs from "Integration/tools/dpcsh_interactive_client/src" dir
python ./funos_stats_analysis/run_malloc_cache.py output.generate_report=True

"""


import logging
import warnings

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf
from hydra.utils import get_original_cwd, to_absolute_path

from dpcsh_interactive_client.funos_commands import *
from dpcsh_interactive_client.dpc_client import *
from dpcsh_interactive_client.convert_nb import *

import inspect


# A logger for this file
log = logging.getLogger(__name__)


def TEST_save_collect_malloc_caches(funos_cmd_obj):
    """Test function to mimic running as integration runs"""
    # generate data
    for nc in range(2):
        for i in range(6, 16):
            funos_cmd_obj.peek_malloc_caches_slot_stats(
                i,
                non_coh=nc,
                from_cli=False,
                save_df=True,
                save_df_dir=funos_cmd_obj.temp_dir,
            )

    log.info("Generate report")
    _, mod_dirname = get_module_info(generate_report)
    _html_filename = generate_report(
        "malloc_report.ipynb",
        in_dir=mod_dirname,
        out_dir=funos_cmd_obj.temp_dir,
        execute=True,
        working_dir=funos_cmd_obj.temp_dir,
        log=log,
    )
    log.info(_html_filename)


def collect_malloc_caches(funos_cmd_obj, save_df):
    for nc in range(2):
        for i in range(6, 16):
            funos_cmd_obj.peek_malloc_caches_slot_stats(
                i, non_coh=nc, from_cli=False, save_df=save_df
            )

    funos_cmd_obj.peek_malloc_caches_slot_stats(
        6, non_coh=0, from_cli=False, save_df=False
    )


def setup(cfg):
    target_port = (
        int(cfg.dut.target_port)
        if not isinstance(cfg.dut.target_port, int)
        else cfg.dut.target_port
    )
    dpc_client = DpcClient(
        target_ip=cfg.dut.target_ip, target_port=target_port, verbose=cfg.dut.verbose
    )
    funos_cmd_obj = FunOSCommands(dpc_client=dpc_client, logger=log)

    return funos_cmd_obj


def working_env_info():
    print(f"Current working directory : {os.getcwd()}")
    print(f"Orig working directory    : {get_original_cwd()}")
    print(f"to_absolute_path('foo')   : {to_absolute_path('foo')}")
    print(f"to_absolute_path('/foo')  : {to_absolute_path('/foo')}")


@hydra.main(config_path="conf", config_name="malloc")
def main(cfg):

    log.info(OmegaConf.to_yaml(cfg))
    # log.info(HydraConfig.get().runtime.cwd)
    working_env_info()

    funos_cmd_obj = setup(cfg)

    # for testing
    # TEST_save_collect_malloc_caches(funos_cmd_obj)
    # return

    # SKIP the following for testing
    collect_malloc_caches(funos_cmd_obj, cfg.output.save_df)

    if cfg.output.generate_report:
        log.info("Generate report")
        _mod_filename, mod_dirname = get_module_info(generate_report)
        _html_filename = generate_report(
            cfg.input.report_notebook,
            in_dir=mod_dirname,
            out_dir=os.getcwd(),
            execute=True,
            logger=log,
        )

    # run_train(cfg)


if __name__ == "__main__":
    main()
