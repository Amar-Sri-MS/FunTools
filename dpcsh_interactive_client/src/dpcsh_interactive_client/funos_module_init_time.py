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
import errno

import logging

# A logger for this file
logger = logging.getLogger(__name__)

# %matplotlib inline

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})

#https://stackoverflow.com/questions/36288670/how-to-programmatically-generate-markdown-output-in-jupyter-notebooks
# from IPython.display import display, Markdown, Latex

def _fmt(s, show_d=True):
    """show decimal number with comma"""
    if show_d:
        return format(s, ",d")
    else:
        return s

def _convert_to_list_of_dicts(raw_data: dict, convert_time_to_ns: bool, debug: bool) -> list:
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
        temp_dict['module_name'] = module_name
        temp_dict['start_time'] = time_unit * float(module_data[0])
        temp_dict['finish_time'] = time_unit * float(module_data[1])
        # add duration column
        temp_dict['module_init_duration'] = temp_dict['finish_time'] - temp_dict['start_time']
        fun_module_init_list.append(temp_dict)

    if debug:
        print("List created")
        print(fun_module_init_list[:2])
        print("Time conversion unit: {}".format(time_unit))
        # convert list of dicts to pandas dataframe
        # fun_module_init_df = pd.DataFrame(fun_module_init_list)
        # fun_module_init_df.head()
    
    return fun_module_init_list

def _load_module_init_data(input_file: str, convert_time_to_ns: bool = True, debug: bool=False) -> pd.DataFrame:
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
    with open(input_file, 'r') as f:
        fun_module_init = json.load(f)
    
    if debug:
        print("Number of modules: {}".format(len(fun_module_init)))
        print("fun_module_init.keys: {}".format(fun_module_init.keys()))
        # print("fun_module_init['accel_telem-init']: {}".format(fun_module_init['accel_telem-init']))

    # convert to list of dicts
    fun_module_init_list = _convert_to_list_of_dicts(fun_module_init, convert_time_to_ns=convert_time_to_ns, debug=debug)

    # convert to df
    fun_module_init_df = pd.DataFrame(fun_module_init_list)
    fun_module_init_df.set_index('module_name', inplace=True)

    return fun_module_init_df

def _load_notification_init_data(input_file: str, convert_time_to_ns: bool = True, dummy_duration: float=1e-1, debug: bool=False) -> pd.DataFrame:
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

    with open(input_file, 'r') as f:
        fun_notification_init = json.load(f)
    if debug:
        print(fun_notification_init)

    new_dict = {}
    for k, v in fun_notification_init.items():
        ## TEMP, to easily identify
        k = "{}-{}".format(k, notif_suffix)
        new_dict[k] = [v, v+dummy_duration]
    if debug:
        print(new_dict)
    
    # save to temp json file
    temp_file_name = notificaiotns_init_file_name + '_temp.json'
    with open(temp_file_name, 'w') as f:
        json.dump(new_dict, f)

    fun_notification_init_df = _load_module_init_data(temp_file_name, convert_time_to_ns=True, debug=debug)
    if debug:
        fun_notification_init_df.head()
    return fun_notification_init_df

def _get_duration_threshold(df: pd.DataFrame, threshold: float=0.10) -> float:
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
    max_duration = df['module_init_duration'].max()

    return float(int(max_duration * threshold))


def _get_start_finish_times(df: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Utility to get start and finish times from df"""

    start_min = df['start_time'].min() # first module start time
    finish_max = df['finish_time'].max() # last module finish time
    duration = finish_max - start_min # time between the first module start time and last module finish time

    if debug:
        print("start_min (start time of the first module): {}".format(start_min))
        print("finish_max: (finish time of the last module) {}".format(finish_max))
        # print("duration: (finish_max - start_min) {}".format(finish_max - start_min))
        # summary
        total_module_time = df['module_init_duration'].sum()
        print("Total module init time: {} ns".format(total_module_time))
        print("duration (time between the first module start time and last module finish time): {} ns".format(finish_max - start_min))
        print("'Total module init time' / 'duration' (greater than 1 is better, which means more concurrent modules init): {} ".format(((total_module_time / duration)).round(4)))
    
    return start_min, finish_max, duration


def _get_color_list(df: pd.DataFrame, notification_color: str = notification_color, default_color: str=module_color) -> list:
    """Utility to get color list for plotly"""
    color_list = []
    for i in range(len(df)):
        if df.index[i].endswith(notif_suffix):
            color_list.append(notification_color)
        else:
            color_list.append(default_color)
    return color_list


def _plot_module_time_chart(df: pd.DataFrame, small_set: int=-1, use_plt: bool=True, sort_by: str="start_time", title: str='FunOS Module Init Duration', group_table: dict=None, simple_group_name: bool=True, cutoff_group_names: int=10, save_file_name: str =full_chart_file_name, disp_granualarity_ms: int=10, debug: bool=False) -> None:
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
    # if X_granualarity == 1000000:
    #     x_tick_str = "ms"
    # elif X_granualarity == 1000000000:
    #     x_tick_str = "s"

    df_use.sort_values(by=[sort_by], inplace=True, ascending=True)

    if small_set > 0:
        df_use = df_use[:small_set]

    if save_file_name[-4:] != ".png":
        save_file_name = save_file_name + ".png"
    
    start_min, finish_max, duration = get_start_finish_times(df_use, debug=debug)

    x_ticks = np.arange(0, duration, X_disp_granualarity * X_granualarity)
    x_tick_labels = ["{} {}".format(str(int(x)), x_tick_str) for x in x_ticks/X_granualarity]

    figsize=(40, len(df_use))
    
    if debug:
        print("x_ticks: {}".format(x_ticks[:10]))
        print("x_tick_labels: {}".format(x_tick_labels[:10]))
        print("figsize: {}".format(figsize))


    if debug:
        display(df_use.head())
        display(df_use.describe())

    if use_plt:
        color_list = get_color_list(df_use)
        # fig, ax = plt.subplots(1, figsize=(40, 50))
        fig, ax = plt.subplots(1, figsize=figsize)
        p1 = ax.barh(df_use.index, width=df_use['module_init_duration'], left=df_use['start_time'], color=color_list)

        ax.set(xlabel='ms', ylabel='Modules')

        #Invert y axis
        plt.gca().invert_yaxis()

        #customize x-ticks
        plt.xticks(ticks=x_ticks, labels=x_tick_labels)

        # title
        if group_table:
            title = "{}: collapsed".format(title)
        plt.title(title, fontsize=20)

        #rotate x-ticks
        plt.xticks(rotation=60)
        #add grid lines
        plt.grid(axis='x', alpha=0.5)
        plt.grid(axis='y', alpha=0.5)

        if group_table:
            if simple_group_name:
                # testing simpler way
                y_pos = np.arange(len(group_table))
                y_label = ["{} & {} modules".format(v[0], len(v)) if len(v) > 1 else v[0] for k, v in group_table.items()]
                ax.set_yticks(y_pos, labels=y_label)
                pass
            else:
                x_base = 6000000
                for i, (k, v) in enumerate(group_table.items()):
                    # print("i: {}, k: {} ({}), v: {}".format(i, k, len(v), v))
                    if len(v) > cutoff_group_names:
                        v_str = "{}...(total: {})".format(v[:cutoff_group_names], len(v))
                    else:
                        v_str = "{}".format(v)
                    ax.text(x_base*(i+1), i, v_str, fontsize=21, color='red')
                    # ax.text(20000000, 1, 'Unicode: Institut für Festkörperphysik')

        #save fig
        plt.savefig(save_file_name)
        plt.show()
    else:
        # use plotly
        # plotly doesn't support 'left' argument, so need to create manualy bars
        # https://community.plotly.com/t/broken-barh-plot/36496
        # assert False, "Ploty not supported yet"

        df_use.sort_values(by=[sort_by], inplace=True, ascending=False)

        # fig = px.bar(df, x="module_init_duration", y=df.index, orientation='h', height=1000)
        

        # fig = go.Figure(go.Bar(
        #     x=df["module_init_duration"],
        #     y=df.index,
        #     orientation='h'))

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_use.index,
            x=df_use["start_time"],
            name='start',
            orientation='h',
            # width=20,
            marker=dict(
                color='rgba(256, 256, 256, 0.0)',
                line=dict(color='rgba(256, 256, 256, 0.0)', width=1)
            )
        ))

        fig.add_trace(go.Bar(
            y=df_use.index,
            x=df_use["module_init_duration"],
            name='module init duration',
            orientation='h',
            # width=20,
            marker=dict(
                color='rgba(58, 71, 80, 0.6)',
                line=dict(color='rgba(58, 71, 80, 1.0)', width=1)
            )
        ))

        fig.update_layout(barmode='stack')

        # https://github.com/jupyter/nbconvert/issues/944
        fig.show(renderer="notebook")

        # for static image to reduce the embedded image size
        # from IPython.display import Image
        # Image(fig.to_image())

        # fig = px.timeline(df, x_start="start_time", x_end="finish_time", y=df_use.index, title=title)
        # fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
        # fig.show()

    del df_use


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
        yaml.dump({'result': json.loads(sorted_df.to_json(orient='records'))}, f, default_flow_style=False)


def _get_collapsed_df(df_in:pd.DataFrame, threshold: float, debug: bool = False) -> Tuple[pd.DataFrame, dict]:
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
    df.sort_values(by=['start_time'], inplace=True, ascending=True)

    # df_collapsed['module_init_duration'] = df_collapsed['module_init_duration'].apply(lambda x: x if x > threshold else 0)
    # df_collapsed = df_collapsed[df_collapsed['module_init_duration'] > 0]
    new_events = []
    n_event = 0
    num_included = 0
    cur_duration = 0 # current start to the finish of the last event
    cur_start = 0
    cur_finish = 0
    last = len(df)
    group_table = {}
    for i in range(len(df)):
        name, start, finish, duration = df.index[i], df.iloc[i].start_time, df.iloc[i].finish_time, df.iloc[i].module_init_duration
        if debug:
            print(name, start, finish, duration)

        if cur_duration == 0:
            num_included = 0
            cur_duration = duration
            cur_start = start
            cur_finish = finish
            group_modules = []
        
        cur_finish = max(cur_finish, finish)
        cur_duration = cur_finish - cur_start
        # print("cur_start, cur_finish, cur_duration: {}, {}".format(cur_start, cur_finish, cur_duration))

        # peek the next check if next module passes the thresholds
        next_module_pass_threshold = False
        if i < last - 1:
            next_name, next_start, next_finish, next_duration = df.index[i+1], df.iloc[i+1].start_time, df.iloc[i+1].finish_time, df.iloc[i+1].module_init_duration
            next_finish = max(cur_finish, next_finish)
            # print("next_finish {}, next_finish - cur_start {}".format(next_finish, next_finish - cur_start))
            # if next duration is more than threshold and there is more than one collapsed, then stop collapsing the current modules
            # if next_finish - cur_start > threshold and num_included > 0:
            if next_finish - cur_start > threshold:
                next_module_pass_threshold = True
                group_modules.append(name)

        
        # if cur_duration + duration > threshold:
        if cur_duration > threshold or next_module_pass_threshold:
            # peek the next one and keep adding until the threshold is reached
            # create a new one

            # if name.endswith(notif_suffix):
            #     group_name = "group_{}{}".format(n_event, notif_suffix)
            # else:
            #     group_name = "group_{}".format(n_event)
            group_name = _get_group_name(name)
            
            new_d = {"module_name" : group_name, "start_time" : cur_start, "finish_time" : cur_finish, "module_init_duration" : cur_duration}
            if debug:
                print("includes {}, added: {}".format(num_included, new_d))
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
        new_d = {"module_name" : group_name, "start_time" : cur_start, "finish_time" : cur_finish, "module_init_duration" : cur_duration}
        if debug:
            print("added: {}".format(new_d))
        new_events.append(new_d)
        group_table[group_name] = group_modules

    df_collapsed = pd.DataFrame(new_events)
    df_collapsed.set_index('module_name', inplace=True)
    df_collapsed.head()
    
    return df_collapsed, group_table


def _extract_module_init_data(file_name_url: str, working_dir: str="./"):
    """load module init data
    either from file or raw log from url
    extract data and save json file to the working_dir

    Parameters
    ----------
    file_name_url : str
        file name or url
    working_dir : str, optional
        working directory, by default "./"

    Returns
    -------
    result_file_names : list
        list of file names in full path

    """

    pass

    modules_init_file_name, notificaiotns_init_file_name = "", ""

    return modules_init_file_name, notificaiotns_init_file_name 


#########################################
# APIs
#########################################


def process_module_notif_init_data(file_name_url: str=None, modules_init_file_name: str=None, notificaiotns_init_file_name: str=None, working_dir: str="./"):
    """Process module init data
    generate a report
    """

    if file_name_url is not None:
        modules_init_file_name, notificaiotns_init_file_name = _extract_module_init_data(file_name_url=file_name_url, working_dir=working_dir)
    else:
        assert modules_init_file_name is not None and notificaiotns_init_file_name is not None

    # process module init data
    fun_module_init_df = _load_module_init_data(modules_init_file_name, convert_time_to_ns=True, debug=False)

    threshold_collapse = _get_duration_threshold(fun_module_init_df, threshold=0.01)
    print("Threshold collapse: {}".format(threshold_collapse))

    # process notif init data

    fun_notification_init_df = _load_notification_init_data(notificaiotns_init_file_name, convert_time_to_ns=True, dummy_duration = 2*threshold_collapse/1e9, debug=False)

    # combine module and notif init data

    fun_module_notif_init_df = pd.concat([fun_module_init_df, fun_notification_init_df])

    # generate report

    # return data and file name
    # returning result dict and file names
    pass


def main():

    # load config file
    current_path = os.getcwd()
    print("current directory is: "+current_path)

    config_file = "fun_module_init_analysis_config.yml"
    path_to_yaml = os.path.join(current_path, config_file)
    print("path_to_config_file "+path_to_yaml)
    try:
        with open (path_to_yaml, 'r') as c_file:
            config = yaml.safe_load(c_file)
    except Exception as e:
        print('Error reading the config file at {} : {}'.format(path_to_yaml, e))

    # setup config variables

    DEBUG = config['general']['debug']
    debug_log = config['general']['debug_log']

    modules_init_file_name = config['file_names']['input_modules_init']
    notificaiotns_init_file_name = config['file_names']['input_notifications_init']

    full_chart_file_name = config['file_names']['output_full_chart']
    full_module_notif_chart = config['file_names']['output_full_module_notif_chart']
    collapsed_chart_file_name = config['file_names']['output_collapsed_chart']
    collapsed_chart_module_notif_file_name = config['file_names']['output_collapsed_module_notif_chart']
    sorted_df_file_name = config['file_names']['output_sorted_df']

    module_color = config['chart']['module']
    notification_color = config['chart']['notification']

    notif_suffix = config["extra"]["notif_suffix"]

if __name__ == "__main__":
    main()