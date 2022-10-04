#!/usr/bin/env python3
"""Utility code to process funos module init time data"""


import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Tuple
import yaml
import json
import os
import requests
import errno
import re
from pathlib import Path

import logging

from convert_nb import generate_report, get_module_info

# A logger for this file
logger = logging.getLogger(__name__)

# %matplotlib inline

import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 22})

# TODO
# - x-axis labels, currently not showing the full range, seems to be a bug in adding xticks
# - expose plotly options, currently working, but y-axis is not showing simple group names


def _fmt(s, show_d=True):
    """show decimal number with comma"""
    if show_d:
        return format(s, ",d")
    else:
        return s


class _default_logger:
    def __init__(self):
        pass

    def info(self, str):
        logger.info(str)

    def debug(self, str):
        logger.info(str)

    def error(self, str):
        logger.info("Error: {}".format(str))


# ============================================================
# init data loading
# ============================================================


def _remove_timestamps_from_log(lines: str) -> str:
    """
    Remove timestamps from log

    remove time stamp from each line
    > [1664319485.206378 0.0.0] pci_early: performing i2c/MUD initialization

    lines: str
        lines to parse
    """

    lines = re.sub(r"\[.*\] ", "", lines)

    return lines


def _filter_log_with_marker(lines: str, marker: str, logger=_default_logger()) -> str:
    """Filter based on marker and form json format by adding the ending "}"

    Parameters
    ----------

    lines: str
        lines to parse
    marker: str
        marker to filter on

    Returns
    -------
    filtered_lines: str
        filtered lines in json format

    Raises
    ------
    AssertionError
        if regex does not match
    """

    try:
        filtered_lines = re.search(marker, lines, re.DOTALL).group(1)
        filtered_lines += "}"  # add back the end marker

    except AttributeError as ex:
        logger.error("Read result : {}".format(lines))
        logger.error("Error parsing log file: {}".format(ex))
        raise ex

    return json.loads(filtered_lines)


def _extract_module_init_data(
    file_name_url: str,
    working_dir: str = "./",
    module_init_file: str = "modules.json",
    notif_init_file: str = "notifications.json",
    logger=_default_logger(),
):

    """load module init data
    either from file or raw log from url
    extract data and save json file to the working_dir

    Parameters
    ----------
    file_name_url : str
        file name or url,
        if it url, then it is expected to starts with 'http'
        if it is file, then it is expected to be in the working_dir
    logger : logger
        logger
    working_dir : str, optional
        working directory, by default "./"
    module_init_file: str, optional
        module init file name, by default "modules.json", full path for saved file will be working_dir/module_init_file
    notif_init_file: str, optional
        notification init file name, by default "notifications.json", full path for saved file will be working_dir/notif_init_file

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

    # check if the working_dir exists
    working_dir = os.path.abspath(working_dir)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    logger.info("Working dir is {}".format(working_dir))

    read_url = True if file_name_url.startswith("http") else False
    if read_url:
        logger.info("Use file from URL: {}".format(file_name_url))
        try:
            response = requests.get(file_name_url)
            lines = response.text
        except requests.exceptions.HTTPError as ex:
            logger.error("Http error: {}".format(ex))
            raise ex
        except requests.exceptions.ConnectionError as ex:
            logger.error("Error Connecting: {}".format(ex))
            raise ex
        except requests.exceptions.Timeout as ex:
            logger.error("Timeout Error: {}".format(ex))
            raise ex
        except requests.exceptions.RequestException as ex:
            logger.error("Exception {}".format(ex))
            raise ex
    else:
        file_name = os.path.join(working_dir, file_name_url)
        logger.info("Use file this path {}".format(file_name))
        try:
            with open(file_name) as f:
                lines = f.read()
        except FileNotFoundError as ex:
            logger.error("File not found: {}".format(file_name))
            raise ex

    lines = _remove_timestamps_from_log(lines)

    MODULE_MARKERS = r"Time-chart data for module init = (.*?)}"
    NOTIF_MARKERS = r"Time-chart data for notifications = (.*?)}"

    module_init = _filter_log_with_marker(lines, MODULE_MARKERS)
    notif_init = _filter_log_with_marker(lines, NOTIF_MARKERS)

    modules_init_file_name = os.path.join(working_dir, module_init_file)
    notificaiotns_init_file_name = os.path.join(working_dir, notif_init_file)

    # save files
    with open(modules_init_file_name, "w") as f:
        json.dump(module_init, f, indent=4)

    with open(notificaiotns_init_file_name, "w") as f:
        json.dump(notif_init, f, indent=4)

    logger.debug("Module init file saved to {}".format(modules_init_file_name))
    logger.debug(
        "Notifications init file saved to {}".format(notificaiotns_init_file_name)
    )

    return modules_init_file_name, notificaiotns_init_file_name


# ============================================================
# init data handling
# ============================================================
def _convert_to_list_of_dicts(
    raw_data: dict,
    convert_time_to_ns: bool,
    logger=_default_logger(),
    debug: bool = False,
) -> list:
    """convert the raw data (dict based format) to list of dicts

    Parameters
    ----------
    raw_data : dict
        raw data in dict format, module_name: [start_time, end_time]

    convert_time_to_ns : bool, optional
        convert time to ns, by default True

    Returns
    -------
    fun_module_init_list : list
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
        logger.info("Time conversion unit: {}".format(time_unit))

    return fun_module_init_list


def _load_module_init_data(
    input_file: str,
    convert_time_to_ns: bool = True,
    logger=_default_logger(),
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

    with open(input_file, "r") as f:
        fun_module_init = json.load(f)

    if debug:
        logger.info("Number of modules: {}".format(len(fun_module_init)))
        logger.info("fun_module_init.keys: {}".format(fun_module_init.keys()))

    # convert to list of dicts
    fun_module_init_list = _convert_to_list_of_dicts(
        fun_module_init, convert_time_to_ns=convert_time_to_ns, debug=debug
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
    logger=_default_logger(),
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

    with open(input_file, "r") as f:
        fun_notification_init = json.load(f)

    if debug:
        logger.info(fun_notification_init)

    new_dict = {}
    for k, v in fun_notification_init.items():
        ## TEMP, to easily identify
        k = "{}-{}".format(k, notif_suffix)
        new_dict[k] = [v, v + dummy_duration]

    if debug:
        logger.info(new_dict)

    # save to temp json file
    temp_file_name = notificaiotns_init_file_name + "_temp.json"
    with open(temp_file_name, "w") as f:
        json.dump(new_dict, f)

    fun_notification_init_df = _load_module_init_data(
        temp_file_name, convert_time_to_ns=True, debug=debug
    )

    if debug:
        fun_notification_init_df.head()

    return fun_notification_init_df


def _get_start_finish_times(
    df: pd.DataFrame, logger=_default_logger(), debug: bool = False
) -> pd.DataFrame:
    """Utility to get start and finish times from df"""

    start_min = df["start_time"].min()  # first module start time
    finish_max = df["finish_time"].max()  # last module finish time
    duration = (
        finish_max - start_min
    )  # time between the first module start time and last module finish time

    if debug:
        logger.info("start_min (start time of the first module): {}".format(start_min))
        logger.info(
            "finish_max: (finish time of the last module) {}".format(finish_max)
        )
        # summary
        total_module_time = df["module_init_duration"].sum()
        logger.info("Total module init time: {} ns".format(total_module_time))
        logger.info(
            "duration (time between the first module start time and last module finish time): {} ns".format(
                finish_max - start_min
            )
        )
        logger.info(
            "'Total module init time' / 'duration' (greater than 1 is better, which means more concurrent modules init): {} ".format(
                ((total_module_time / duration)).round(4)
            )
        )

    return start_min, finish_max, duration


def _get_color_list(
    df: pd.DataFrame,
    notification_color: str = "red",
    default_color: str = "blue",
    notif_suffix: str = "**",
) -> list:
    """Utility to get color list for plotly"""
    color_list = []
    for i in range(len(df)):
        if df.index[i].endswith(notif_suffix):
            color_list.append(notification_color)
        else:
            color_list.append(default_color)
    return color_list


def _dump_file(df: pd.DataFrame, file_name: str, sorted_key: str = None):
    """Dump the dataframe to a file

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
    with open(txt_file_name, "w") as f:
        f.write(sorted_df.to_string())
    sorted_df_file_name = file_name
    json_file_name = sorted_df_file_name + ".json"
    sorted_df.to_json(json_file_name)
    csv_file_name = sorted_df_file_name + ".csv"
    sorted_df.to_csv(csv_file_name)

    yaml_file_name = sorted_df_file_name + ".yaml"
    with open(yaml_file_name, "w") as f:
        yaml.dump(
            {"result": json.loads(sorted_df.to_json(orient="records"))},
            f,
            default_flow_style=False,
        )


#########################################
# APIs
#########################################


def plot_module_time_chart(
    df: pd.DataFrame,
    small_set: int = -1,
    use_plt: bool = True,
    sort_by: str = "start_time",
    title: str = "FunOS Module Init Duration",
    group_table: dict = None,
    simple_group_name: bool = True,
    cutoff_group_names: int = 10,
    save_file_name: str = "fun_module_notif_init_chart.png",
    disp_granualarity_ms: int = 10,
    logger=_default_logger(),
    debug: bool = False,
) -> None:
    """Plot the module init time chart
    Parameters
    ----------
    df : pd.DataFrame
        dataframe with module init data
    small_set : int, optional
        number of rows to plot, by default -1 (plot all)
    sort_by : str, optional
        sort by column, by default "start_time"
    title : str, optional
        title of the chart, by default 'FunOS Module Init Duration'
    group_table : dict, optional
        group table, by default None, if not None, group the modules based on the group_table
    simple_group_name : bool, optional
        use simple group name, by default True
    cutoff_group_names : int, optional
        cutoff group names, by default 12, cut off text display for group names
    disp_granualarity_ms: int, optional
        X axis display granualarity, in ms time unit, by default 10

    Returns
    -------
    None
    """
    # add max min for creating tick

    df_use = df.copy()

    X_disp_granualarity = disp_granualarity_ms
    X_granualarity = 1000000
    x_tick_str = "ms"

    df_use.sort_values(by=[sort_by], inplace=True, ascending=True)

    if small_set > 0:
        df_use = df_use[:small_set]

    if save_file_name != "" and save_file_name[-4:] != ".png":
        save_file_name = save_file_name + ".png"

    start_min, finish_max, duration = _get_start_finish_times(df_use, debug=debug)

    x_ticks = np.arange(0, duration, X_disp_granualarity * X_granualarity)
    x_tick_labels = [
        "{} {}".format(str(int(x)), x_tick_str) for x in x_ticks / X_granualarity
    ]

    figsize = (40, len(df_use))

    if debug:
        logger.info("x_ticks: {}".format(x_ticks[:10]))
        logger.info("x_tick_labels: {}".format(x_tick_labels[:10]))
        logger.info("figsize: {}".format(figsize))

    if debug:
        logger.info(df_use.head())
        logger.info(df_use.describe())

    if use_plt:
        color_list = _get_color_list(df_use)
        # fig, ax = plt.subplots(1, figsize=(40, 50))
        fig, ax = plt.subplots(1, figsize=figsize)
        p1 = ax.barh(
            df_use.index,
            width=df_use["module_init_duration"],
            left=df_use["start_time"],
            color=color_list,
        )

        ax.set(xlabel="ms", ylabel="Modules")

        # Invert y axis
        plt.gca().invert_yaxis()

        # customize x-ticks
        plt.xticks(ticks=x_ticks, labels=x_tick_labels)

        # title
        if group_table:
            title = "{}: collapsed".format(title)
        plt.title(title, fontsize=20)

        # rotate x-ticks
        plt.xticks(rotation=60)
        # add grid lines
        plt.grid(axis="x", alpha=0.5)
        plt.grid(axis="y", alpha=0.5)

        if group_table:
            if simple_group_name:
                # testing simpler way
                y_pos = np.arange(len(group_table))
                y_label = [
                    "{} & {} modules".format(v[0], len(v)) if len(v) > 1 else v[0]
                    for k, v in group_table.items()
                ]
                ax.set_yticks(y_pos, labels=y_label)
                pass
            else:
                x_base = 6000000
                for i, (k, v) in enumerate(group_table.items()):
                    # logger.info("i: {}, k: {} ({}), v: {}".format(i, k, len(v), v))
                    if len(v) > cutoff_group_names:
                        v_str = "{}...(total: {})".format(
                            v[:cutoff_group_names], len(v)
                        )
                    else:
                        v_str = "{}".format(v)
                    ax.text(x_base * (i + 1), i, v_str, fontsize=21, color="red")
                    # ax.text(20000000, 1, 'Unicode: Institut für Festkörperphysik')

        if save_file_name != "":
            # save fig
            plt.savefig(save_file_name)
            plt.show()
    else:
        # use plotly
        # plotly doesn't support 'left' argument, so need to create manualy bars
        # https://community.plotly.com/t/broken-barh-plot/36496
        # assert False, "Ploty not supported yet"

        df_use.sort_values(by=[sort_by], inplace=True, ascending=False)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=df_use.index,
                x=df_use["start_time"],
                name="start",
                orientation="h",
                # width=20,
                marker=dict(
                    color="rgba(256, 256, 256, 0.0)",
                    line=dict(color="rgba(256, 256, 256, 0.0)", width=1),
                ),
            )
        )

        fig.add_trace(
            go.Bar(
                y=df_use.index,
                x=df_use["module_init_duration"],
                name="module init duration",
                orientation="h",
                # width=20,
                marker=dict(
                    color="rgba(58, 71, 80, 0.6)",
                    line=dict(color="rgba(58, 71, 80, 1.0)", width=1),
                ),
            )
        )

        fig.update_layout(barmode="stack")

        # https://github.com/jupyter/nbconvert/issues/944
        fig.show(renderer="notebook")

    del df_use


def print_group_table(
    group_table: dict,
    threshold: float,
    save_file_name: str = None,
    logger=_default_logger(),
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
    output = "Collapsed module group report (threshold time of {} ns):\n".format(
        threshold
    )
    output += "========================\n"
    for key, value in group_table.items():
        output += "{}({}): {}\n".format(key, len(value), value)
        # logger.info("{}({}): {}".format(key, len(value), value))

    logger.info(output)

    if save_file_name:
        if save_file_name[:-4] != ".txt":
            save_file_name += ".txt"
        with open(save_file_name, "w") as f:
            f.write(output)
    return output


def get_collapsed_df(
    df_in: pd.DataFrame,
    threshold: float,
    notif_suffix: str = "**",
    logger=_default_logger(),
    debug: bool = False,
) -> Tuple[pd.DataFrame, dict]:
    """Collpased df using the threshold

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with module init data
    threshold : float
        threshold value to collapse, fraction to the largest duration
        ex> 0.10 means collapse all the modules with duration less than 10% of the largest duration

    Returns
    -------
    pd.DataFrame
        collapsed dataframe
    dict
        group table, key is the group name, value is the list of modules in the group
    """

    def _get_group_name(name):
        """form group name"""
        if name.endswith(notif_suffix):
            # for notification
            group_name = "group_{}{}".format(n_event, notif_suffix)
        else:
            group_name = "group_{}".format(n_event)
        return group_name

    df = df_in.copy()
    df.sort_values(by=["start_time"], inplace=True, ascending=True)

    new_events = []
    n_event = 0
    num_included = 0
    cur_duration = 0  # current start to the finish of the last event
    cur_start = 0
    cur_finish = 0
    last = len(df)
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
            cur_start = start
            cur_finish = finish
            group_modules = []

        cur_finish = max(cur_finish, finish)
        cur_duration = cur_finish - cur_start

        # peek the next check if next module passes the thresholds
        next_module_pass_threshold = False
        if i < last - 1:
            next_name, next_start, next_finish, next_duration = (
                df.index[i + 1],
                df.iloc[i + 1].start_time,
                df.iloc[i + 1].finish_time,
                df.iloc[i + 1].module_init_duration,
            )
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
                logger.info("includes {}, added: {}".format(num_included, new_d))
            new_events.append(new_d)
            cur_duration = 0
            n_event += 1
            group_table[group_name] = group_modules if num_included > 0 else [name]
            # group_modules = []
        else:
            group_modules.append(name)
            num_included += 1

    if cur_duration != 0:
        # group_name = "group_{}".format(n_event)
        group_name = _get_group_name(name)
        new_d = {
            "module_name": group_name,
            "start_time": cur_start,
            "finish_time": cur_finish,
            "module_init_duration": cur_duration,
        }
        if debug:
            logger.info("added: {}".format(new_d))
        new_events.append(new_d)
        group_table[group_name] = group_modules

    df_collapsed = pd.DataFrame(new_events)
    df_collapsed.set_index("module_name", inplace=True)
    df_collapsed.head()

    return df_collapsed, group_table


def get_duration_threshold(df: pd.DataFrame, threshold: float = 0.10) -> float:
    """Get the threshold value from the dataframe
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
    logger=_default_logger(),
):
    """Process module init data
    generate a report

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
        logger, by default _default_logger()

    Returns
    -------
    pd.DataFrame
        dataframe with module init data
    result: dict
        result dictionary
    """

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
        modules_init_file_name, convert_time_to_ns=True, debug=False
    )

    threshold_collapse = get_duration_threshold(fun_module_init_df, threshold=0.01)
    logger.info("Threshold collapse: {}".format(threshold_collapse))

    # process notif init data

    fun_notification_init_df = _load_notification_init_data(
        notificaiotns_init_file_name,
        convert_time_to_ns=True,
        dummy_duration=2 * threshold_collapse / 1e9,
        debug=False,
    )

    # combine module and notif init data

    fun_module_notif_init_df = pd.concat([fun_module_init_df, fun_notification_init_df])
    # logger.info(fun_module_notif_init_df)

    def _get_perf_stat(df):
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


def main(logger):

    # load config file
    current_path = os.getcwd()
    logger.info("current directory is: " + current_path)

    # INPUT_FILE_URL = "uartout0.0.txt"
    INPUT_FILE_URL = os.environ["INPUT_FILE_URL"]

    process_module_notif_init_data(
        INPUT_FILE_URL, logger=logger, working_dir=current_path
    )


if __name__ == "__main__":

    logger = _default_logger()
    os.environ[
        "INPUT_FILE_URL"
    ] = "http://palladium-jobs.fungible.local:8080/job/4297914/raw_file/odp/uartout0.0.txt"
    main(logger)
