#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""Utility functions for funos module init time analysis.

This module contains utility functions for funos module init time analysis.
It parses the log files or dpchsh output json file and extract the module init time data.
It also contains utility functions to plot the data.

To run `PYTHONPATH` needs to be set to point where `dpcsh_interactive_client` modules are located.

```
$ export PYTHONPATH=$WORKSPACE/FunTools/dpcsh_interactive_client/src/dpcsh_interactive_client:$PYTHONPATH
```


Example:
    The following example runs the module init time analysis on the log file and plots the data:

        ```
        $ python3 funos_module_init_time.py
        ```

Todo:
    * x-axis labels, currently not showing the full range, seems to be a bug in adding xticks
    * expose plotly options, currently working, but y-axis is not showing simple group names

"""

import os
import re
import json
from typing import Tuple
from typing import List, Dict

import yaml
import requests

import pandas as pd

from utils import DefaultLogger


def _remove_timestamps_from_log(lines: str) -> str:
    """Remove timestamps from log

    remove time stamp from each line
    > [1664319485.206378 0.0.0] pci_early: performing i2c/MUD initialization

    Parameters
    ----------
    lines: str
        lines to parse

    Returns
    -------
    filtered_lines: str
        lines with timestamp removed
    """

    lines = re.sub(r"\[.*\] ", "", lines)

    return lines


def _filter_log_with_marker(
    lines: str, marker_type: str, logger=DefaultLogger()
) -> str:
    """Filter based on the marker and create an output with json format by adding the ending "}"

    Parameters
    ----------

    lines: str
        lines to parse
    marker_type: str
        marker type string, "module_init", "notif"

    Returns
    -------
    filtered_lines: str
        filtered lines in json format

    Raises
    ------
    AssertionError
        if regex does not match
    """

    if marker_type == "module_init":
        marker = r"Time-chart data for module init = (.*?)}"
    elif marker_type == "notif":
        marker = r"Time-chart data for notifications = (.*?)}"
    else:
        assert False, f"Marker {marker} not supported"

    try:
        filtered_lines = re.search(marker, lines, re.DOTALL).group(1)
        filtered_lines += "}"  # add back the end marker

    except AttributeError as ex:
        logger.error(f"Read result : {lines}")
        logger.error(f"Error parsing log file: {ex}")
        raise ex

    return json.loads(filtered_lines)


def _read_from_file_or_url(
    working_dir: str, file_name_url: str, logger=DefaultLogger()
) -> str:
    """Read from file or url
    if it is file, `working_dir` is expected to be the directory where the file is located

    """
    if file_name_url.startswith("http"):
        logger.info(f"Use file from URL: {file_name_url}")
        try:
            response = requests.get(file_name_url, timeout=10)
            lines = response.text
        except requests.exceptions.HTTPError as ex:
            logger.error(f"Http error: {ex}")
            raise ex
        except requests.exceptions.ConnectionError as ex:
            logger.error(f"Error Connecting: {ex}")
            raise ex
        except requests.exceptions.Timeout as ex:
            logger.error(f"Timeout Error: {ex}")
            raise ex
        except requests.exceptions.RequestException as ex:
            logger.error(f"Exception {ex}")
            raise ex
    else:
        file_name = os.path.join(working_dir, file_name_url)
        logger.info(f"Use file this path {file_name}")
        try:
            with open(file_name, encoding="utf-8") as f:
                lines = f.read()
        except FileNotFoundError as ex:
            logger.error(f"File not found: {file_name}")
            raise ex
    return lines


def _extract_module_init_data(
    file_name_url: str,
    working_dir: str = "./",
    module_init_file: str = "modules.json",
    notif_init_file: str = "notifications.json",
    logger=DefaultLogger(),
) -> Tuple[str, str]:

    """Extract module and notif init data either from file or raw log from url.
    Create json files for module and notif init data.

    Parameters
    ----------
    file_name_url : str
        file name or url for funlos raw log
        if it url, then it is expected to starts with 'http'
        if it is file, then it is expected to be in the working_dir
    logger : logger
        logger
    working_dir : str, optional
        working directory, by default "./"
    module_init_file: str, optional
        result module init file name, by default "modules.json",
        full path for saved file will be working_dir/module_init_file
    notif_init_file: str, optional
        result notification init file name, by default "notifications.json",
        full path for saved file will be working_dir/notif_init_file

    Returns
    -------
    module_init_file_name: str
        full path of the saved module init file
    notif_init_file_name: str
        full path of the saved notification init file

    Raises
    ------
    FileNotFoundError
        if file_name_url is not a file or url
    requests.exceptions*
        if file_name_url is url and it is not accessible
    AttributeError
        log parsing error
    """

    working_dir = os.path.abspath(working_dir)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    logger.info(f"Working dir is {working_dir}")

    lines = _read_from_file_or_url(working_dir, file_name_url, logger=logger)

    lines = _remove_timestamps_from_log(lines)

    module_init = _filter_log_with_marker(lines, "module_init", logger)
    notif_init = _filter_log_with_marker(lines, "notif", logger)

    modules_init_file_name = os.path.join(working_dir, module_init_file)
    notificaiotns_init_file_name = os.path.join(working_dir, notif_init_file)

    with open(modules_init_file_name, "w", encoding="utf-8") as f:
        json.dump(module_init, f, indent=4)

    with open(notificaiotns_init_file_name, "w", encoding="utf-8") as f:
        json.dump(notif_init, f, indent=4)

    logger.debug(f"Module init file saved to {modules_init_file_name}")
    logger.debug(f"Notifications init file saved to {notificaiotns_init_file_name}")

    return modules_init_file_name, notificaiotns_init_file_name


def _convert_to_list_of_dicts(
    raw_data: dict,
    convert_time_to_ns: bool,
    logger=DefaultLogger(),
    debug: bool = False,
) -> List[Dict]:
    """convert the raw data (dict with key with module name) to list of dicts

    Parameters
    ----------
    raw_data : dict
        raw data in dict format, module_name: [start_time, end_time]

    convert_time_to_ns : bool, optional
        convert time to ns, by default True

    Returns
    -------
    fun_module_init_list : list of dict
        list of dicts, each dict is a module, with keys: module_name, start_time, finish_time
    """
    time_unit = 0

    if convert_time_to_ns:
        time_unit = 1000000000
    fun_module_init_list = []

    for module_name, module_data in raw_data.items():
        temp_dict = {}
        temp_dict["module_name"] = module_name
        temp_dict["start_time"] = time_unit * float(module_data[0])
        temp_dict["finish_time"] = time_unit * float(module_data[1])
        # add duration column
        temp_dict["module_init_duration"] = (
            temp_dict["finish_time"] - temp_dict["start_time"]
        )
        fun_module_init_list.append(temp_dict)

    if debug:
        logger.info("List created")
        logger.info(fun_module_init_list[:2])
        logger.info(f"Time conversion unit: {time_unit}")

    return fun_module_init_list


def _load_module_init_data(
    input_file: str,
    convert_time_to_ns: bool = True,
    logger=DefaultLogger(),
    debug: bool = False,
) -> pd.DataFrame:
    """load module init data from json file and convert to pandas dataframe

    Parameters
    ----------
    input_file : str
        input file name

    Returns
    -------

    fun_module_init_df : pd.DataFrame
        pandas dataframe with module_name, start_time, finish_time, module_init_duration

    """

    with open(input_file, "r", encoding="utf-8") as f:
        fun_module_init = json.load(f)

    if debug:
        logger.info(f"Number of modules: {fun_module_init}")
        logger.info(f"fun_module_init.keys: {fun_module_init.keys()}")

    # convert to list of dicts
    fun_module_init_list = _convert_to_list_of_dicts(
        fun_module_init,
        convert_time_to_ns=convert_time_to_ns,
        debug=debug,
        logger=logger,
    )

    # convert to df
    fun_module_init_df = pd.DataFrame(fun_module_init_list)
    fun_module_init_df.set_index("module_name", inplace=True)

    return fun_module_init_df


def _load_notification_init_data(
    input_file: str,
    convert_time_to_ns: bool = True,
    dummy_duration: float = 1e-1,
    debug: bool = False,
    notif_suffix: str = "**",
    notificaiotns_init_file_name: str = "notifications.json",
    logger=DefaultLogger(),
) -> pd.DataFrame:
    """load notificaiton init data from json file and convert to pandas dataframe

    notification formation is different than module init data
    first load json and modifiy the data to match module init data format
    then call load function

    Parameters
    ----------
    input_file : str
        input file name

    Returns
    -------

    fun_module_init_df : pd.DataFrame
        pandas dataframe with module_name, start_time, finish_time, module_init_duration

    """

    with open(input_file, "r", encoding="utf-8") as f:
        fun_notification_init = json.load(f)

    new_dict = {}
    for k, v in fun_notification_init.items():
        # add `notif_suffix` to easily identify
        new_dict[f"{k}-{notif_suffix}"] = [v, v + dummy_duration]

    temp_file_name = notificaiotns_init_file_name + "_temp.json"
    with open(temp_file_name, "w", encoding="utf-8") as f:
        json.dump(new_dict, f)

    fun_notification_init_df = _load_module_init_data(
        temp_file_name,
        convert_time_to_ns=convert_time_to_ns,
        debug=debug,
        logger=logger,
    )

    if debug:
        fun_notification_init_df.head()

    return fun_notification_init_df


def _dump_df_to_files(df: pd.DataFrame, file_name: str, sorted_key: str = None) -> None:
    """Dump the dataframe to a file in sorted order in txt, csv, json, yml formats

    Parameters
    ----------
    df : pd.DataFrame
        dataframe to dump
    file_name : str
        file name to dump to
    sorted_key : str, optional
        key to sort the dataframe, by default None
    """

    # save df to json file
    sorted_df = df.copy()
    if sorted_key:
        sorted_df.sort_values(by=[sorted_key], inplace=True, ascending=True)

    txt_file_name = file_name + ".txt"
    with open(txt_file_name, "w", encoding="utf-8") as f:
        f.write(sorted_df.to_string())
    sorted_df_file_name = file_name
    json_file_name = sorted_df_file_name + ".json"
    sorted_df.to_json(json_file_name)
    csv_file_name = sorted_df_file_name + ".csv"
    sorted_df.to_csv(csv_file_name)

    yaml_file_name = sorted_df_file_name + ".yaml"
    with open(yaml_file_name, "w", encoding="utf-8") as f:
        yaml.dump(
            {"result": json.loads(sorted_df.to_json(orient="records"))},
            f,
            default_flow_style=False,
        )


#########################################
# APIs
#########################################


def print_group_table(
    group_table: dict,
    threshold: float,
    save_file_name: str = None,
    logger=DefaultLogger(),
):
    """logger.info the group table

    Parameters
    ----------
    group_table : dict
        group table, key is the group name, value is the list of modules in the group
    threshold : float
        threshold (nsec) value to collapse, fraction to the largest duration
    save_file_name : str, optional
        file to save the group table, by default None


    Returns
    -------
    out: str
        report string
    """
    output = f"Collapsed module group report (threshold time of {threshold} ns):\n"
    output += "========================\n"
    for key, value in group_table.items():
        output += "{}({}): {}\n".format(key, len(value), value)
        # logger.info("{}({}): {}".format(key, len(value), value))

    logger.info(output)

    if save_file_name:
        if save_file_name[:-4] != ".txt":
            save_file_name += ".txt"
        with open(save_file_name, "w", encoding="utf-8") as f:
            f.write(output)
    return output


def get_start_finish_times(
    df: pd.DataFrame, logger=DefaultLogger(), debug: bool = False
) -> Tuple[float, float, float]:
    """Utility to get start and finish times from df

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with module_name, start_time, finish_time, module_init_duration
    logger : logger, optional
        logger, by default DefaultLogger()
    debug : bool, optional
        debug flag, by default False

    Returns
    -------
    start_min, finish_max, duration: Tuple[float, float, float]
        start_min: minimum start time
        finish_max: maximum finish time
        duration: finish_max - start_min
    """

    start_min = df["start_time"].min()  # first module start time
    finish_max = df["finish_time"].max()  # last module finish time
    duration = (
        finish_max - start_min
    )  # time between the first module start time and last module finish time

    if debug:
        logger.info(f"start_min (start time of the first module): {start_min}")
        logger.info(f"finish_max: (finish time of the last module) {finish_max}")
        # summary
        total_module_time = df["module_init_duration"].sum()
        logger.info(f"Total module init time: {total_module_time} ns")
        logger.info(
            f"duration (time between the first module start and last module finish): {duration} ns"
        )
        logger.info(
            "'Total module init time' / 'duration' (greater than 1 is better, which means more concurrent modules init): {} ".format(
                ((total_module_time / duration)).round(4)
            )
        )

    return start_min, finish_max, duration


def get_collapsed_df(
    df_in: pd.DataFrame,
    threshold: float,
    notif_suffix: str = "**",
    logger=DefaultLogger(),
    debug: bool = False,
) -> Tuple[pd.DataFrame, dict]:
    """Collpased df using the threshold.
    Collapsed modules into groups if the duration is less than the threshold.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with module init data
    threshold : float
        threshold value to collapse, fraction to the largest duration
        ex> 0.10 means collapse all the modules with duration less than 10% of the largest duration
    notif_suffix : str, optional
        suffix to add to notifications, by default "**"

    Returns
    -------
    pd.DataFrame
        collapsed dataframe
    group_table: dict
        collapsed group table dict, key is the group name, value is the list of modules in the group
    """

    def _get_group_name(name):
        """form group name"""
        if name.endswith(notif_suffix):
            # for notification
            group_name = f"group_{n_event}{notif_suffix}"
        else:
            group_name = f"group_{n_event}"
        return group_name

    df = df_in.copy()
    df.sort_values(by=["start_time"], inplace=True, ascending=True)

    new_events, n_event, num_included = [], 0, 0
    cur_duration = 0  # current start to the finish of the last event
    cur_start, cur_finish, last = 0, 0, len(df)
    group_table = {}
    for i in range(len(df)):
        name, start, finish, duration = (
            df.index[i],
            df.iloc[i].start_time,
            df.iloc[i].finish_time,
            df.iloc[i].module_init_duration,
        )
        if debug:
            logger.info(name, start, finish, duration)

        if cur_duration == 0:
            num_included = 0
            cur_duration = duration
            cur_start, cur_finish = start, finish
            group_modules = []

        cur_finish = max(cur_finish, finish)
        cur_duration = cur_finish - cur_start

        # peek the next check if next module passes the thresholds
        next_module_pass_threshold = False
        if i < last - 1:
            next_finish = df.iloc[i + 1].finish_time
            next_finish = max(cur_finish, next_finish)
            if next_finish - cur_start > threshold:
                next_module_pass_threshold = True
                group_modules.append(name)

        if cur_duration > threshold or next_module_pass_threshold:
            # peek the next one and keep adding until the threshold is reached
            # create a new one

            group_name = _get_group_name(name)

            new_d = {
                "module_name": group_name,
                "start_time": cur_start,
                "finish_time": cur_finish,
                "module_init_duration": cur_duration,
            }
            if debug:
                logger.info(f"includes {num_included}, added: {new_d}")
            new_events.append(new_d)
            cur_duration = 0
            n_event += 1
            group_table[group_name] = group_modules if num_included > 0 else [name]
        else:
            group_modules.append(name)
            num_included += 1

    if cur_duration != 0:
        group_name = _get_group_name(name)
        new_d = {
            "module_name": group_name,
            "start_time": cur_start,
            "finish_time": cur_finish,
            "module_init_duration": cur_duration,
        }
        if debug:
            logger.info(f"added: {new_d}")
        new_events.append(new_d)
        group_table[group_name] = group_modules

    df_collapsed = pd.DataFrame(new_events)
    df_collapsed.set_index("module_name", inplace=True)
    df_collapsed.head()

    return df_collapsed, group_table


def get_duration_threshold(df: pd.DataFrame, threshold: float = 0.10) -> float:
    """Get the threshold value from the dataframe
    Use threshold value based on the max duration multiplied by `threshold` argument

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with module init data
    threshold : float, optional
        threshold value, by default 0.10

    Returns
    -------
    float
        threshold value
    """
    max_duration = df["module_init_duration"].max()

    return float(int(max_duration * threshold))


def process_module_notif_init_data(
    file_name_url: str = None,
    modules_init_file_name: str = None,
    notificaiotns_init_file_name: str = None,
    working_dir: str = "./",
    logger=DefaultLogger(),
):
    """Process module init data, generate a report

    Parameters
    ----------
    file_name_url : str, optional
        file name or url, by default None
    modules_init_file_name : str, optional
        modules init file name, by default None
    notificaiotns_init_file_name : str, optional
        notifications init file name, by default None
    working_dir : str, optional
        working directory, by default "./"
    logger : logging.Logger, optional
        logger, by default DefaultLogger()

    Returns
    -------
    pd.DataFrame
        dataframe with module init data
    result: dict
        result dictionary
    """

    # input data can be raw funos log file or url for the log
    # or processed module and notif init json files
    if file_name_url is not None:
        (
            modules_init_file_name,
            notificaiotns_init_file_name,
        ) = _extract_module_init_data(
            file_name_url=file_name_url, logger=logger, working_dir=working_dir
        )
    else:
        assert (
            modules_init_file_name is not None
            and notificaiotns_init_file_name is not None
        )

    # process module init data
    fun_module_init_df = _load_module_init_data(
        modules_init_file_name, convert_time_to_ns=True, debug=False, logger=logger
    )

    threshold_collapse = get_duration_threshold(fun_module_init_df, threshold=0.01)
    logger.info(f"Threshold collapse: {threshold_collapse}")

    # process notif init data
    fun_notification_init_df = _load_notification_init_data(
        notificaiotns_init_file_name,
        convert_time_to_ns=True,
        dummy_duration=2 * threshold_collapse / 1e9,
        debug=False,
        logger=logger,
    )

    # combine module and notif init data
    fun_module_notif_init_df = pd.concat([fun_module_init_df, fun_notification_init_df])

    def _get_perf_stat(df: pd.DataFrame) -> dict:
        # get the longest module duration
        # total duration
        longest_duraiton_id = df["module_init_duration"].idxmax()
        longest_duraiton = df["module_init_duration"].loc[longest_duraiton_id]

        start_min = df["start_time"].min()
        finish_max = df["finish_time"].max()

        result = {
            "longest_duration_ns": longest_duraiton,
            "longest_duration_id": longest_duraiton_id,
            "total_duration_ns": finish_max - start_min,
        }
        return result

    result = _get_perf_stat(fun_module_notif_init_df)

    return fun_module_notif_init_df, result


def main(logger=DefaultLogger()):
    """Main function"""

    # load config file
    current_path = os.getcwd()
    logger.info("current directory is: " + current_path)

    # INPUT_FILE_URL = "uartout0.0.txt"
    input_file_url = os.environ["INPUT_FILE_URL"]

    process_module_notif_init_data(
        input_file_url, logger=logger, working_dir=current_path
    )


if __name__ == "__main__":

    logger = DefaultLogger()

    os.environ[
        "INPUT_FILE_URL"
    ] = "http://palladium-jobs.fungible.local:8080/job/4297914/raw_file/odp/uartout0.0.txt"

    main(logger)
