#!/usr/bin/env python3

from prettytable import PrettyTable, FRAME
from datetime import datetime
import time
import re
import os
import tempfile
import shutil
import numpy as np

try:
    import pandas as pd

    pd.options.display.float_format = "{:,.0f}".format
except ImportError:
    print("{}: Import failed, pandas numpy!".format(__file__))
    print(">>> 'pip install pandas' will fix this")
    os.exit(-1)

"""NOTE: this method is a duplicate from nu_commands.py"""
TIME_INTERVAL = 1
TOTAL_CLUSTERS = 8
TOTAL_CORES_PER_CLUSTER = 6
TOTAL_VPS_PER_CORE = 4
START_VP_NUMBER = 8


"""MCACHE_RULES """
SZ_ST1 = 4#8  # state1
SZ_ST2 = 4#8  # state2
SZ_A = 3  # action


def do_sleep_for_interval():
    time.sleep(TIME_INTERVAL)
    return True


class _default_logger:
    def __init__(self):
        pass

    def info(self, str):
        print(str)

    def error(self, str):
        print("Error: {}".format(str))


class FunOSCommands(object):
    __version__ = "0.0.6"

    def __init__(self, dpc_client, logger=None, temp_dir=None):
        """Handling FunOS related dpcsh

        Parameters
        ----------
        dpc_client: dpc_client
            dpc communication client
        logger: logger
            logger
        temp_dir: str
            temp dir for saving data files
        """
        self.dpc_client = dpc_client

        if logger:
            self.logger = logger
        else:
            self.logger = _default_logger()

        self.logger.info("FunOSCommands: v{} initialized".format(self.__version__))
        self.version_info = self._read_version()

        self.temp_dir = temp_dir if temp_dir else tempfile.mkdtemp()

    def __del__(self):

        if not self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def gets_version(self):
        return "DUT version version version version version version version version: {}, {}".format(
            self.version_info["FunSDK"], self.version_info["branch"]
        )

    def gets_git_url(self):
        return "https://github.com/fungible-inc/FunOS/commit/{}".format(
            self.version_info["branch"]
        )

    def gets_timestamp(self):
        ts = time.time()
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

    def _get_difference(self, result, prev_result):
        """NOTE: this method is a duplicate from nu_commands.py,
        made a duplicated copy here in order to keep the funos_commands class to be standalone
        """

        """
        :param result: Should be dict or dict of dict
        :param prev_result: Should be dict or dict of dict
        :return: dict or dict of dict
        """
        diff_result = {}
        for key in result:
            if type(result[key]) == dict:
                diff_result[key] = {}
                for _key in result[key]:
                    if key in prev_result and _key in prev_result[key]:
                        if type(result[key][_key]) == dict:
                            diff_result[key][_key] = {}
                            for inner_key in result[key][_key]:
                                if inner_key in prev_result[key][_key]:
                                    diff_value = (
                                        result[key][_key][inner_key]
                                        - prev_result[key][_key][inner_key]
                                    )
                                    diff_result[key][_key][inner_key] = diff_value
                                else:
                                    diff_result[key][_key][inner_key] = 0
                        else:
                            diff_value = result[key][_key] - prev_result[key][_key]
                            diff_result[key][_key] = diff_value
                    else:
                        diff_result[key][_key] = 0
            elif type(result[key]) == str:
                diff_result[key] = result[key]
            else:
                if key in prev_result:
                    if type(result[key]) == list:
                        diff_result[key] = result[key]
                        continue
                    diff_value = result[key] - prev_result[key]
                    diff_result[key] = diff_value
                else:
                    diff_result[key] = result[key]

        return diff_result

    def _add_hline(self, _table_obj, col):
        s = ["-" * len(c) for c in col]
        _table_obj.add_row(s)

    def _fmt(self, s, show_d=True):
        """show decimal number with comma"""
        if show_d:
            return format(s, ",d")
        else:
            return s

    def _read_version(self):
        """Read install versions, sdk and funos sha
        > peek config/version
        {
            "duration": 1.3954e-05,
            "result": {
                "FS800": 1,
                "FunSDK": "bld_17826",
                "bootmode": "emmc",
                "branch": "892aa9d75e",
                "buildid": "b43959e5-169d-39eb-dc48-2e54cd494dc4",
                "debug": false,
                "dev_upgrade": false,
                "release": "6.0.0",
                "sku": "fs800r2"
            },
            "tid": 0
        }

        Parameters
        ----------

        Returns
        -------
        result: dict
            {"FunSDK": result["FunSDK"], "branch": result["branch"]}

        """

        cmd = "config/version"
        self.logger.info("dpcsh: {}".format(cmd))
        result = self.dpc_client.execute(verb="peek", arg_list=[cmd])

        return {"FunSDK": result["FunSDK"], "branch": result["branch"]}

    def _get_max_mcache(self, non_coh):
        """get configured max value for mcache
        > peek config/fun_malloc/cache_max/coherent
        {
            "duration": 4.945e-05,
            "result": {
                "slot_00064B": 32767,
                "slot_00128B": 4095,
                "slot_00256B": 2047,
                "slot_00512B": 1023,
                "slot_01024B": 511,
                "slot_02048B": 255,
                "slot_04096B": 127,
                "slot_08192B": 63,
                "slot_16384B": 31,
                "slot_32768B": 15
            },
            "tid": 3
        }

        Parameters
        ----------
        non_coh: int
            1 : non coherent, 0 : coherent

        Returns:
        slot_max: list
            list of max

        """

        if non_coh:
            nc_str = "non_coh"
        else:
            nc_str = "coherent"

        cmd = "config/fun_malloc/cache_max/%s" % nc_str
        self.logger.info("dpcsh: {}".format(cmd))
        result = self.dpc_client.execute(verb="peek", arg_list=[cmd])

        slot_max = []
        # will use sorted iterate instead of exact parsing of the key for simplicity and known key pattern
        for key in sorted(result):
            # print("key : {}, {}".format(key, result[key]))
            slot_max.append(int(result[key]))

        return slot_max

    def _get_stats_ws_stack_in_use(self):
        # wu stack in_use check
        cmd = "stats/wustacks"
        result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
        if "in_use" in result:
            self.logger.info("")
            self.logger.info("wu stack in_use: {}".format(result["in_use"]))

    def _get_stats_ws_alloc(self):
        # ws_alloc fail check
        cmd = "stats/ws_alloc"
        result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
        if "flow_ctl_ws_alloc_first_attempt_failures" in result:
            self.logger.info("")
            self.logger.info(
                "flow_ctl_ws_alloc_first_attempt_failures: {}".format(
                    result["flow_ctl_ws_alloc_first_attempt_failures"]
                )
            )
            self.logger.info(
                "ws_alloc_failures: {}".format(result["ws_alloc_failures"])
            )

    def peek_fun_malloc_slot_stats(
        self, non_coh, from_cli=True, grep_regex=None, sh_d=True
    ):
        """peek stats/fun_malloc

        Parameters
        ----------
        slot: int
            slot number 6-15
        non_coh: int
            1 : non coherent, 0 : coherent
        from_cli: bool
            from dpc_cli, keep runnint till key interupt
        grep_regex: str
            regex str
        sh_d: bool
            show in decimal with comma

        """

        col = [
            "Slot",
            "Avail(total)",
            "Avail Bytes(total)",
            "Avail(per slot avg)",
            "Fill % (per slot)",
            "Avail Bytes(per slot avg)",
            "Hit",
            "Miss",
            "Replenish_req",
        ]
        col_diff = [
            "Slot",
            "Avail(total)",
            "Avail(total) diff",
            "Avail Bytes(total)",
            "Avail(per slot avg)",
            "Avail(per slot avg) diff",
            "Avail Bytes(per slot avg)",
            "Hit",
            "Hit diff",
            "Miss",
            "Miss diff",
        ]

        prev_result = {}
        while True:
            try:
                slot_max = self._get_max_mcache(non_coh)

                if non_coh:
                    nc_str = "non_coh"
                else:
                    nc_str = "coherent"

                cmd = "stats/fun_malloc/%s/slot_stats" % nc_str
                self.logger.info("dpcsh: {}".format(cmd))

                result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                self.logger.info(
                    "\n--------------> Fun malloc slot stat {} <--------------".format(
                        nc_str
                    )
                )

                total_avail, total_avail_byte, total_avail_avg_byte = 0, 0, 0
                total_hit, total_miss, total_repl_req = 0, 0, 0

                table_obj = None
                if "Desc" in result:
                    del result["Desc"]  # remove description row
                if result:
                    if prev_result:
                        table_obj = PrettyTable(col_diff)
                        table_obj.align = "r"
                        diff_result = self._get_difference(
                            result=result, prev_result=prev_result
                        )
                        for key in sorted(result):
                            if key in ["Desc", "total"]:
                                continue
                            vals = [
                                key,
                                self._fmt(result[key]["avail"], sh_d),
                                self._fmt(diff_result[key]["avail"], sh_d),
                                self._fmt(
                                    2 ** int(key) * int(result[key]["avail"]), sh_d
                                ),
                                self._fmt(result[key]["avail_avg_per_mcache"], sh_d),
                                self._fmt(
                                    diff_result[key]["avail_avg_per_mcache"], sh_d
                                ),
                                self._fmt(
                                    2 ** int(key)
                                    * int(result[key]["avail_avg_per_mcache"]),
                                    sh_d,
                                ),
                                self._fmt(result[key]["hit"], sh_d),
                                self._fmt(diff_result[key]["hit"], sh_d),
                                self._fmt(result[key]["miss"], sh_d),
                                self._fmt(diff_result[key]["miss"], sh_d),
                            ]
                            if grep_regex and not re.search(
                                grep_regex, key, re.IGNORECASE
                            ):
                                continue
                            total_avail += int(int(result[key]["avail"]))
                            total_avail_byte += int(
                                2 ** int(key) * int(result[key]["avail"])
                            )
                            total_avail_avg_byte += int(
                                2 ** int(key) * int(result[key]["avail_avg_per_mcache"])
                            )
                            total_hit += int(result[key]["hit"])
                            total_miss += int(result[key]["miss"])
                            table_obj.add_row(vals)

                        self._add_hline(table_obj, col_diff)
                        table_obj.add_row(
                            [
                                "Total",
                                format(total_avail, ",d"),
                                "-",
                                format(total_avail_byte, ",d"),
                                "-",
                                "-",
                                format(total_avail_avg_byte, ",d"),
                                format(
                                    total_hit,
                                    ",d",
                                ),
                                "-",
                                format(
                                    total_miss,
                                    ",d",
                                ),
                                "-",
                            ]
                        )
                    else:
                        table_obj = PrettyTable(col)
                        table_obj.align = "r"

                        for idx, key in enumerate(sorted(result)):
                            if key in ["Desc", "total"]:
                                continue

                            fill_percentage = int(
                                result[key]["avail_avg_per_mcache"]
                                / slot_max[idx]
                                * 100
                            )
                            vals = [
                                key,
                                self._fmt(result[key]["avail"], sh_d),
                                self._fmt(
                                    2 ** int(key) * int(result[key]["avail"]), sh_d
                                ),
                                self._fmt(result[key]["avail_avg_per_mcache"], sh_d),
                                self._fmt(fill_percentage, sh_d),
                                self._fmt(
                                    2 ** int(key)
                                    * int(result[key]["avail_avg_per_mcache"]),
                                    sh_d,
                                ),
                                self._fmt(result[key]["hit"], sh_d),
                                self._fmt(result[key]["miss"], sh_d),
                                self._fmt(result[key]["repl_req"], sh_d),
                            ]

                            if grep_regex and not re.search(
                                grep_regex, key, re.IGNORECASE
                            ):
                                continue

                            total_avail += int(int(result[key]["avail"]))
                            total_avail_byte += int(
                                2 ** int(key) * int(result[key]["avail"])
                            )
                            total_avail_avg_byte += int(
                                2 ** int(key) * int(result[key]["avail_avg_per_mcache"])
                            )
                            total_hit += int(result[key]["hit"])
                            total_miss += int(result[key]["miss"])
                            total_repl_req += int(result[key]["repl_req"])

                            table_obj.add_row(vals)

                        self._add_hline(table_obj, col)
                        table_obj.add_row(
                            [
                                "Total",
                                format(total_avail, ",d"),
                                format(total_avail_byte, ",d"),
                                "-",
                                "-",
                                format(total_avail_avg_byte, ",d"),
                                format(
                                    total_hit,
                                    ",d",
                                ),
                                format(
                                    total_miss,
                                    ",d",
                                ),
                                format(
                                    total_repl_req,
                                    ",d",
                                ),
                            ]
                        )
                prev_result = result
                self.logger.info("\n{}".format(table_obj))

                cmd = "stats/fun_malloc/%s/%s" % (nc_str, "size_in_use")
                size_in_use = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                cmd = "stats/fun_malloc/%s/%s" % (nc_str, "size_cached_by_cores")
                size_cached_by_cores = self.dpc_client.execute(
                    verb="peek", arg_list=[cmd]
                )

                self.logger.info("")
                self.logger.info("size_in_use: {} B".format(format(size_in_use, ",d")))
                self.logger.info(
                    "size_cached_by_cores: {} B".format(
                        format(size_cached_by_cores, ",d")
                    )
                )
                size_in_use_minus_cached = size_in_use - size_cached_by_cores
                self.logger.info(
                    "size_in_use_minus_cached: {} B".format(
                        format(size_in_use_minus_cached, ",d")
                    )
                )
                size_in_use_percent = int(size_in_use_minus_cached / size_in_use * 100)
                self.logger.info(
                    "* Percentage of data in use (size_in_use_minus_cached/size_in_use) : {}%".format(
                        format(size_in_use_percent, ",d")
                    )
                )

                self._get_stats_ws_alloc()
                self._get_stats_ws_stack_in_use()
                self.logger.info("")

                self.logger.info("{}".format(self.gets_version()))
                self.logger.info("open {}".format(self.gets_git_url()))
                self.logger.info(
                    "\n########################  {} ########################\n".format(
                        str(self.gets_timestamp())
                    )
                )

                if not from_cli:
                    break

                do_sleep_for_interval()

            except KeyboardInterrupt:
                self.dpc_client.disconnect()
                break
            except Exception as ex:
                self.logger.error(("{}".format(str(ex))))
                self.dpc_client.disconnect()
                break

    def peek_malloc_caches_slot_stats(
        self,
        slot,
        non_coh,
        from_cli=True,
        grep_regex=None,
        sh_d=True,
        save_df=False,
        save_df_dir=None,
    ):
        """peek stats/malloc_caches

        Parameters
        ----------
        slot: int
            slot number 6-15 (valid range), note -1 will be used as a wild card
        non_coh: int
            1 : non coherent, 0 : coherent
        from_cli: bool
            from dpc_cli, keep runnint till key interupt
        grep_regex: str
            regex str
        sh_d: bool
            show in decimal with comma
        save_df: bool
            save dataframe
        save_df_dir: str
            directory to save dataframe

        """

        assert (slot >= 6 and slot <= 15) or (slot == -1), "Invalid slot numbers"
        prev_result = {}
        col = [
            "VP",
            "Avail",
            "Avail(avg)",
            "Avail(std)",
            "Avail Bytes",
            "Avail(max)",
            "Avail(min)",
            "Hit",
            "Miss",
            "Max",
            "Repl_th_val",
            "Avg_rewards",
        ]
        # TODO
        # handle wild card slot
        # - imporove to take wild card slot, to reduce the calling peek
        # - add miss ratio, get the max
        # - add avg/std replenish for those non zero nsec

        if non_coh:
            nc_str = "_non_coh"
        else:
            nc_str = ""

        df_filename = "malloc_caches_slot_stats_slot{}_{}.pkl".format(nc_str, slot)
        if save_df_dir:
            assert isinstance(save_df_dir, str), "Invalid type for {}: {}".format(
                save_df_dir, type(save_df_dir)
            )
            df_filename = os.path.join(save_df_dir, df_filename)

        while True:
            rows = []
            try:
                cmd = "stats/malloc_caches%s" % nc_str
                result = self.dpc_client.execute(verb="peek", arg_list=[cmd])
                self.logger.info(
                    "\n--------------> Malloc caches slot {} (size {} (2^{}) Bytes) stat {} <--------------".format(
                        slot, 2**slot, slot, nc_str
                    )
                )
                table_obj = None
                if "Desc" in result:
                    del result["Desc"]  # remove descriptin row

                total_avail_byte = 0
                total_hit, total_miss = 0, 0

                if result:
                    table_obj = PrettyTable(col)
                    table_obj.align = "r"

                    for key in sorted(result):
                        if "vp" not in key:
                            continue

                        vp_list = result[key]["cached"]
                        for vp in vp_list:
                            if vp["lcs"] != slot:
                                continue
                            if "avail_avg" not in vp:
                                vp["avail_avg"] = 0.0
                            if "avail_std" not in vp:
                                vp["avail_std"] = 0.0
                            avail_total = 2**slot * int(vp["avail"])

                            repl_th_idx = (
                                vp["replenish_th_idx"]
                                if "replenish_th_idx" in vp
                                else 0
                            )

                            val_func = vp["val_func"] if "val_func" in vp else []
                            val_func_np = (
                                np.reshape(val_func, (SZ_ST1, SZ_ST2, SZ_A))
                                if "val_func" in vp
                                else np.zeros((SZ_ST1, SZ_ST2, SZ_A))
                            )

                            repl_th_val = (int)((vp["max"] / 8) * (repl_th_idx + 1))
                            avg_reward = vp["avg_reward"] if "avg_reward" in vp else 0.0
                            val = [
                                key,
                                self._fmt(vp["avail"], sh_d),
                                "{:7.2f}".format(vp["avail_avg"]),
                                "{:7.2f}".format(vp["avail_std"]),
                                self._fmt(avail_total),
                                self._fmt(vp["avail_max"], sh_d),
                                self._fmt(vp["avail_min"], sh_d),
                                self._fmt(vp["hit"], sh_d),
                                self._fmt(vp["miss"], sh_d),
                                self._fmt(vp["max"], sh_d),
                                self._fmt(repl_th_val, sh_d),
                                "{:7.4f}".format(avg_reward),
                            ]

                            row = [
                                key,
                                vp["avail"],
                                vp["avail_avg"],
                                vp["avail_std"],
                                avail_total,
                                vp["avail_max"],
                                vp["avail_min"],
                                vp["hit"],
                                vp["miss"],
                                vp["max"],
                                repl_th_val,
                                avg_reward,
                                val_func_np,
                            ]
                            rows.append(row)

                            if grep_regex and not re.search(
                                grep_regex, key, re.IGNORECASE
                            ):
                                continue
                            table_obj.add_row(val)

                            total_avail_byte += int(2**slot * int(vp["avail"]))
                            total_hit += int(vp["hit"])
                            total_miss += int(vp["miss"])
                    # total
                    self._add_hline(table_obj, col)

                    table_obj.add_row(
                        [
                            "Total",
                            "-",  # avail
                            "-",  # avail_avg
                            "-",  # avail_std
                            format(total_avail_byte, ",d"),
                            "-",
                            "-",
                            format(
                                total_hit,
                                ",d",
                            ),
                            format(
                                total_miss,
                                ",d",
                            ),
                            "-",
                            "-",
                            "-",
                        ]
                    )

                prev_result = result
                # print max, and threhold...
                self.logger.info("\n{}".format(table_obj))
                # summary stat
                col.append("val_func")
                df = pd.DataFrame(rows, columns=col)
                df.set_index("VP", inplace=True)
                # df_str = df[['Avail', 'Avail Bytes', 'Avail(max)', 'Avail(min)', 'Hit', 'Miss']].describe().to_string()
                df_str = df.describe().to_string()
                self.logger.info("\nSummary statistics")
                self.logger.info("\n{}".format(df_str))

                self.logger.info("{}".format(self.gets_version()))
                self.logger.info("open {}".format(self.gets_git_url()))
                self.logger.info(
                    "\n########################  {} ########################\n".format(
                        str(self.gets_timestamp())
                    )
                )

                if save_df:
                    df.to_pickle(df_filename)

                if not from_cli:
                    break

                do_sleep_for_interval()
            except KeyboardInterrupt:
                self.dpc_client.disconnect()
                break
            except Exception as ex:
                self.logger.error("{}".format(ex))
                self.dpc_client.disconnect()
                break
