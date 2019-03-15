#!/usr/bin/env python2.7

#
# Reads in a JSON file containing WU statistics and creates
# chart data files for use by Plotly (in JSON format).
#
# Usage: create_chart_data.py <input_file>
#

import re
import json
import argparse


# These constants were cribbed from nucleus/topology.h in FunOS code
VPS_PER_CORE = 4
VP_BASE = 8


def faddr_to_ccv_id(f_addr):
    """
    Converts a fabric address to a CCV (cluster.core.vp) id.
    This is a direct translation of the code in topo_cc_from_faddr()
    in nucleus/topology.h.
    :param f_addr:
    :return: CCV id
    """
    lid = f_addr['lid']
    cluster = f_addr['gid']
    core = (lid - VP_BASE) / VPS_PER_CORE
    vp = (lid - VP_BASE) % VPS_PER_CORE
    return '%s.%s.%s' % (cluster, core, vp)


def get_chart_data(stat_name, stats):
    """
    Extracts the stat with stat_name and converts it into
    a structure that the plotly library expects for bar
    chart data.
    :param stat_name:
    :param stats:
    :return: bar chart data for plotly
    """
    x = [faddr_to_ccv_id(s['faddr']) for s in stats]
    y = [s[stat_name] for s in stats]
    data = [{
        'x': x,
        'y': y,
        'type': 'bar',
    }]
    return data


def write_to_file(stat_name, chart):
    with open(stat_name + '.json', 'w') as fh:
        res = json.dumps(chart);
        fh.write(res)


def extract_and_write_chart(stat_name, stats):
    """
    Extracts chart data from stats and writes the chart
    to a JSON formatted file with file name <stat_name>.json
    :param stat_name:
    :param stats:
    :return: None
    """
    chart = dict()
    chart['data'] = get_chart_data(stat_name, stats)
    chart['layout'] = get_precanned_layout(stat_name)
    write_to_file(stat_name, chart)


# Kind of lame: this are the title lookups for stat_name
precanned_titles = {
    'util_pct': '% util by VP',
    'wus_sent': 'Count of sent WUs',
    'wus_recvd': 'Count of received WUs',
}


precanned_y_titles = {
    'util_pct': '% util',
    'wus_sent': 'WU count',
    'wus_recvd': 'WU count',
}


def get_precanned_layout(stat_name):
    return {
        'title': precanned_titles[stat_name],
        'xaxis': {
            'title': 'CCV (cluster.core.vp)'
        },
        'yaxis': {
            'title': precanned_y_titles[stat_name]
        },
    }


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('input_file', type=str,
                       help='JSON file containing WU statistics')
    args = parse.parse_args()

    with open(args.input_file, 'r') as fh:
        contents = fh.read()
        if contents.startswith('no_stats'):
            return

        stats = json.loads(contents)
        extract_and_write_chart('util_pct', stats)
        extract_and_write_chart('wus_sent', stats)
        extract_and_write_chart('wus_recvd', stats)
        # TODO update marker to show charts are available


if __name__ == '__main__':
    main()
