#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for plotting

Todo:

"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple

# plot histogram for min, avg, max, dev columns
def plot_histogram(
    df: pd.DataFrame, col: str, title: str, xlabel: str, ylabel: str, bins: int = 10
) -> None:
    """Plot histogram for min, avg, max, dev columns

    Parameters
    ----------
    df : pd.DataFrame
        dataframe
    col : str
        column name
    title : str
        title
    xlabel : str
        xlabel
    ylabel : str
        ylabel
    bins : int, optional
        number of bins, by default 10
    """

    plt.figure(figsize=(10, 6))
    plt.hist(df[col], bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def plot_2_subplot(
    dfs: List[pd.DataFrame],
    top_title: str,
    xlabel: str,
    col_titles: List[str],
    ylim: int = 0,
    bins: int = 20,
) -> None:
    """plot 2 column subplots

    Parameters
    ----------
    dfs : List[pd.DataFrame]
        list of dataframes
    top_title : str
        top title
    xlabel : str
        xlabel
    col_titles : List[str]
        list of column titles
    ylim : int, optional
        ylim, by default 0
    bins : int, optional
        number of bins for histogram, by default 20

    Returns
    -------
    None
    """

    def _get_xmax(dfs):

        x_max = 0
        for i, df in enumerate(dfs):
            for j, col in enumerate(cols):
                x_max = max(x_max, df[col].max())
        return x_max

    def _get_xmax_in_col(dfs, col):

        x_max = 0
        for i, df in enumerate(dfs):
            x_max = max(x_max, df[col].max())
        return x_max

    cols = ["avg", "max", "dev"]
    fig, axes = plt.subplots(len(cols), len(dfs), figsize=(20, 15))
    fig.suptitle(top_title)
    x_max = _get_xmax(dfs)

    for i, df in enumerate(dfs):
        # ax.plot(df["usecs"], df["count"])
        for j, col in enumerate(cols):
            sns.histplot(df[col], kde=True, bins=bins, ax=axes[j, i])
            y_label = "count of {}".format(col)
            axes[j, i].set(xlabel=xlabel, ylabel=y_label)

            # if x_max is too large, it will be hard to check small values
            # so xlim setting in this case
            SKIP = True
            if (not SKIP) and x_max < 10000:
                axes[j, i].set_xlim(0, x_max)

            x_max_col = _get_xmax_in_col(dfs, col)
            if x_max_col < 10000:
                axes[j, i].set_xlim(0, x_max_col * 1.01)
            if (not SKIP) and ylim > 0:
                axes[j, i].set_ylim(0, ylim)

    for ax, col_title in zip(axes[0], col_titles):
        ax.set_title(col_title)

    plt.show()
