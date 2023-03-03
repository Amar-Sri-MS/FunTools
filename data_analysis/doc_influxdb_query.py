#!/usr/bin/env python3

"""Query documentaion metric from InfluxDB

   Copyright (c) 2023 Fungible. All rights reserved.

    Examples
    --------
    >>> python3 ./doc_influxdb_query.py --doc_type file
    >>> python3 ./doc_influxdb_query.py --doc_type api

    >>> % python ./doc_influxdb_query.py --doc_type file
        % Last documentation percentage of 'file': {'type': 'file', 'doc_type': 'sdk_file_doc_gen_percent', 'value': '79.19', 'time': '2023-03-02T11:51:20.311082Z'}
    >>> % python ./doc_influxdb_query.py --type api
        % Last documentation percentage of 'api': {'type': 'api', 'doc_type': 'sdk_apis_doc_gen_percent', 'value': '0.00', 'time': '2023-03-02T11:51:20.311082Z'}

    Checks
    ------
    static check:
    >>> mypy ./doc_influxdb_query.py
    >>> pylint ./doc_influxdb_query.py

    format:
    >>> black ./doc_influxdb_query.py

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
    description = "Query documentation percentage from InfluxDB"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--doc_type",
        type=str,
        default="file",
        help="Metric type, file or api",
    )
    return parser.parse_args()


class DocumentationQuery:
    """
    Query documentation from InfluxDB
    """

    def __init__(self, influx_config) -> None:
        """Initialise the documentation Ingester with Influx client

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

    def query(self, query_type: str, last: bool = True, first: bool = False) -> Any:
        """Query documentation from InfluxDB

        Parameters
        ----------
        query_type : str
            Query name
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

        query = f"select value from {query_type} {order};"
        bind_params = {}
        results = self.influx_client.query(query, bind_params=bind_params)

        return results

    def query_doc_percent_last(self, doc_type: str) -> Dict[str, Any]:
        """Query latest documentation metric from InfluxDB

        Parameters
        ----------
        doc_type : str
            documentaiton type: file or api

        Returns
        -------
        dict : result dict
            ex> `{'type': 'api', 'doc_type': 'sdk_apis_doc_gen_percent', 'value': '0.00', 'time': '2023-03-02T11:51:20.311082Z'}`
        """

        if doc_type == "file":
            query_type = "sdk_file_doc_gen_percent"
        elif doc_type == "api":
            query_type = "sdk_apis_doc_gen_percent"
        else:
            assert False, "doc_type unspported: {}".format(doc_type)

        results = self.query(query_type, last=True)
        """Example of results.raw
        {'statement_id': 0,
            'series': [{'name': 'sdk_file_doc_gen_percent',
            'columns': ['time', 'value'],
            'values': [['2023-03-02T11:51:20.311082Z', '79.19']]}]}
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
            "type": doc_type,
            "doc_type": query_type,
            "value": value,
            "time": time,
        }


def main() -> None:
    """Main entry point"""

    args = _get_args()

    if args.doc_type != "file" and args.doc_type != "api":
        sys.exc_info("doc_type needs to be either file or api")

    influx_config = dict(host="fun-mongo-02", port=8086, database="api_doc_gen")
    doc_query = DocumentationQuery(influx_config)

    ret = doc_query.query_doc_percent_last(args.doc_type)

    print("Last documentation percentage of '{}': {}".format(args.doc_type, ret))


if __name__ == "__main__":
    main()
