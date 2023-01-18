#!/usr/bin/env python3

"""Query code coverage from InfluxDB

   Copyright (c) 2023 Fungible. All rights reserved.

    Examples
    --------
    >>> python3 ./cov_influxdb_query.py --module sdk
    >>> python3 ./cov_influxdb_query.py --module base

    >>> % python ./cov_influxdb_query.py --module sdk
        % Last function coverage of module 'sdk': {'module': 'sdk', 'coverage_type': 'function_percent', 'value': 54.19822192953573, 'time': '2023-01-13T11:45:45.995988Z'}
    >>> % python ./cov_influxdb_query.py --module base --cov_type line
        % Last function coverage of module 'base': {'module': 'base', 'coverage_type': 'line_percent', 'value': 41.1, 'time': '2023-01-13T11:45:45.845045Z'}

    Checks
    ------
    static check:
    >>> mypy ./cov_influxdb_query.py
    >>> pylint ./cov_influxdb_query.py

    format:
    >>> black ./cov_influxdb_query.py

"""

"""
TODO
----

- handle flexible query, cureently it is only limited to last and first data
"""

import argparse
import json
import sys
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple

try:
    from influxdb import InfluxDBClient  # type: ignore
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules;")
    print(">>> pip install influxdb")
    sys.exit(-1)


def _get_args() -> argparse.Namespace:
    description = "Query code coverage percentage from InfluxDB"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--cov_type",
        type=str,
        default="function",
        help="Coverage type: function, line, branch",
    )
    parser.add_argument(
        "--module",
        type=str,
        required=True,
        help="Coverage module name: sdk, base, nucleus, alloc",
    )
    return parser.parse_args()


class CodeCoverageQuery:
    """
    Query code coverage from InfluxDB
    """

    def __init__(self, influx_config) -> None:
        """Initialise the Code coverage Ingester with Influx client

        Parameters
        ----------
        influx_config : dict
            InfluxDB configuration

        Returns
        -------
        None
        """

        self.influx_config = influx_config
        self.influx_client = self.get_influx_client()
        self.influx_client.switch_database(self.influx_config["database"])

    def get_influx_client(self) -> InfluxDBClient:
        """Returns influx client object

        Parameters
        ----------
        None

        Returns
        -------
        InfluxDBClient
            InfluxDB client object
        """
        influx_host = self.influx_config["host"]
        influx_port = self.influx_config["port"]
        influx_database = self.influx_config["database"]
        influx_client = InfluxDBClient(influx_host, influx_port, influx_database)  # type: ignore
        return influx_client

    def query(
        self, module: str, measurement: str, last: bool = True, first: bool = False
    ) -> Any:
        """Query function coverage from InfluxDB

        Parameters
        ----------
        module : str
            Module name
        measurement : str
            Measurement name
        last : bool
            Query last data
        first : bool
            Query first data

        Returns
        -------
        Any : Query result
        """

        if last:
            order = "ORDER BY DESC LIMIT 1"
        elif first:
            order = "ORDER BY ASC LIMIT 1"
        else:
            assert False, "Not implemented"

        query = f"select value from {measurement} where module=$module {order};"
        bind_params = {"module": module}
        results = self.influx_client.query(query, bind_params=bind_params)

        return results

    def query_coverage_percent_last(self, module: str, cov_type: str) -> Dict[str, Any]:
        """Query latest function coverage data from InfluxDB

        Parameters
        ----------
        module : str
            Module name

        cov_type : str
            Coverage type, function, line, branch

        Returns
        -------
        dict : resut dict
            ex> `{"module": module, "function_percent": func_percent, "time": time}`
        """

        query_type = f"{cov_type}_percent"
        results = self.query(module, query_type, last=True)
        """Example of results.raw
            {'statement_id': 0,
            'series': [{'name': 'function_percent',
            'columns': ['time', 'value'],
            'values': [['2023-01-13T11:45:45.995988Z', 54.19822192953573]]}]} 
        """

        if results is None or results.raw is None:
            return {}
        if "series" not in results.raw or len(results.raw["series"]) == 0:
            return {}
        if (
            "values" not in results.raw["series"][0]
            or len(results.raw["series"][0]["values"][0]) != 2
        ):
            return {}

        time = results.raw["series"][0]["values"][0][0]
        value = results.raw["series"][0]["values"][0][1]

        return {
            "module": module,
            "coverage_type": query_type,
            "value": value,
            "time": time,
        }


def main() -> None:
    """Main entry point"""

    args = _get_args()

    if args.module == "sdk":
        assert (
            args.cov_type == "function"
        ), "sdk module only support function coverage type"

    influx_config = dict(host="fun-mongo-02", port=8086, database="code_coverage")
    code_query = CodeCoverageQuery(influx_config)

    ret = code_query.query_coverage_percent_last(args.module, args.cov_type)

    print("Last function coverage of module '{}': {}".format(args.module, ret))


if __name__ == "__main__":
    main()
