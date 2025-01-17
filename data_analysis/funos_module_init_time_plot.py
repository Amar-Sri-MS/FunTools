#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""Plot utility functions for funos module init time analysis.

This module contains plot utility functions for funos module init time analysis.
To run `PYTHONPATH` needs to be set to point where `dpcsh_interactive_client` modules are

```
export PYTHONPATH=$WORKSPACE/FunTools/data_analysis:$PYTHONPATH
```


Example:
    The following example runs the module init time analysis on the log file and plots the data:

        $ python3 funos_module_init_time_plot.py

Todo:
    * x-axis labels, currently not showing the full range, seems to be a bug in adding xticks
    * expose plotly options, currently working, but y-axis is not showing simple group names

"""

import os

import matplotlib.pyplot as plt

import plotly.graph_objects as go
import numpy as np
import pandas as pd

from funos_module_init_time import get_start_finish_times

from utils.utils import *

plt.rcParams.update({"font.size": 22})


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


#########################################
# APIs
#########################################


def plot_module_time_chart(
    df_in: pd.DataFrame,
    small_set: int = -1,
    use_plt: bool = True,
    sort_by: str = "start_time",
    title: str = "FunOS Module Init Duration",
    group_table: dict = None,
    simple_group_name: bool = True,
    cutoff_group_names: int = 10,
    save_file_name: str = "fun_module_notif_init_chart.png",
    disp_granualarity_ms: int = 10,
    min_duration: int = 0,
    shift_left: bool = True,
    logger=DefaultLogger(),
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
    min_duration: int, optional
        minimum duration to plot, by default 0
        if this is non zero, then any duration smaller than this will be used this value as duration
    shift_left: bool, optional
        shift the start time to the left, by default True
        so that the first module starts at 0, so that time chart is more readable
    Returns
    -------
    None
    """
    # add max min for creating tick

    df_use = df_in.copy()

    x_disp_granualarity = disp_granualarity_ms
    x_granualarity = 1000000
    x_tick_str = "ms"

    df_use.sort_values(by=[sort_by], inplace=True, ascending=True)

    # if this is non zero, then any duration smaller than this will be used this value as duration

    logger.info("df_use: %s", df_use.head(20))
    if min_duration > 0:
        df_use["module_init_duration"].clip(lower=min_duration, inplace=True)
        logger.info("df_use updated : %s", df_use.head(20))

    if shift_left:
        time_shift = df_use["start_time"].min()
        df_use["start_time"] = df_use["start_time"] - time_shift
        df_use["finish_time"] = df_use["finish_time"] - time_shift

    if small_set > 0:
        df_use = df_use[:small_set]

    if save_file_name != "" and save_file_name[-4:] != ".png":
        save_file_name = save_file_name + ".png"

    _, _, duration = get_start_finish_times(df_use, debug=debug)

    x_ticks = np.arange(0, duration, x_disp_granualarity * x_granualarity)
    x_tick_labels = [
        "{} {}".format(str(int(x)), x_tick_str) for x in x_ticks / x_granualarity
    ]

    figsize = (40, len(df_use))

    if debug:
        logger.info("x_ticks: {}".format(x_ticks[:10]))
        logger.info("x_tick_labels: {}".format(x_tick_labels[:10]))
        logger.info("figsize: {}".format(figsize))

        logger.info(df_use.head())
        logger.info(df_use.describe())

    if use_plt:
        color_list = _get_color_list(df_use)
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


def main(logger=DefaultLogger()):
    """Main function"""

    # NOTE: use `funos_module_init_time_test.py` to test plot function


if __name__ == "__main__":

    logger = DefaultLogger()

    main(logger)
