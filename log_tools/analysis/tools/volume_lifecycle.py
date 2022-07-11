#!/usr/bin/env python3

#
# Storage Tool for finding the lifecycle of a volume.
#
# Requires Part Volume UUID to get the lifecycle of it.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import datetime
import json
import logging
import re

import config_loader

from elasticsearch7 import Elasticsearch


# Mapping of volume types
VOLUME_TYPES = {
    'SNAPSHOT': 'VOL_TYPE_BLK_SNAP',
    'PV': 'VOL_TYPE_BLK_PART_VOL',
    'PVG': 'VOL_TYPE_BLK_PART_VG',
    'LSV': 'VOL_TYPE_BLK_LSV',
    'JVOL': 'VOL_TYPE_BLK_REPLICA',
    'RDS': 'VOL_TYPE_BLK_RDS',
    'EC': 'VOL_TYPE_BLK_EC'
}

# Mapping of operation with opcodes
OPERATIONS = {
    'CREATE': 'VOL_ADMIN_OPCODE_CREATE',
    'MOUNT': 'VOL_ADMIN_OPCODE_MOUNT',
    'FAIL_PLEX': 'VOL_ADMIN_OPCODE_FAIL_PLEX',
    'FAIL_PLEX_ACK': 'VOL_ADMIN_OPCODE_FAIL_PLEX_ACK',
    'REBUILD': 'VOL_ADMIN_OPCODE_REBUILD'
}

def convert_to_json(log_line):
    """
    FunOS logs JSON as string. This function extracts the JSON out of
    the log message.
    """
    log_levels = ('NOTICE', 'ERR', 'CRIT', 'ALERT', 'WDT:', 'WARNING')
    json_list = list()
    try:
        for line in log_line.split('\n'):
            line = line.strip()
            # JSON logs could be multiline or single line.
            # Start of the json
            if any(level in line for level in log_levels):
                pos = line.find('{')
                # Parses single line JSON logs.
                if pos != -1 and line.endswith('}"'):
                    decoder = json.JSONDecoder()
                    return decoder.raw_decode(line[pos:])[0]
                else:
                    continue
            if line != "" and line != '--':
                # End of the json
                if line != '}"':
                    json_list.append(line)
        json_str = ' '.join(json_list)

        ret_json = json.loads('{' + json_str + '}')
        return ret_json
    except:
        logging.exception(f'Malformed JSON: {log_line}')
        return None

def build_search_body(queries, time_filters=None, operator='AND'):
    """
    Building ES query body based on the given list of queries and time
    filters.
    """
    must_queries = list()
    if queries and len(queries) > 0:
        must_queries.append({'query_string': {
            'query': f' {operator} '.join([f'{query}' for query in queries])
        }})

    filter_queries = list()
    # Time filters are range filters
    if time_filters:
        start = time_filters[0]
        end = time_filters[1]
        time_range = {}
        if start:
            time_range['gte'] = start
        if end:
            time_range['lte'] = end
        range = {'range': {
            '@timestamp': time_range
        }}
        filter_queries.append(range)

    compound_query = {}
    compound_query['must'] = must_queries
    compound_query['filter'] = filter_queries

    body = {}
    body['query'] = {}
    body['query']['bool'] = compound_query
    return body

def get_value_from_params(info, key, default=None):
    """ Extracts value from the FunOS JSON log """
    if (info and info.get('msg') and 'params' in info['msg']
        and key in info['msg']['params']):
        return info['msg']['params'][key]
    return default

def convert_datetime_str(datetime_str, format= '%Y-%m-%dT%H:%M:%S.%f'):
    if not datetime_str:
        return None
    return datetime.datetime.strptime(datetime_str, format)


class Volume(object):
    def __init__(self, log_id, pvol_id):
        self.index = log_id
        # Part volume ID
        self.pvol_id = pvol_id

        # Time of the current operation
        self.op_time = None
        # Time of the previous operation
        self.prev_op_time = None
        # Time of the current JVOL operation
        self.jvol_time = None
        # Time of the current EC operation
        self.ec_time = None
        self.jvol_uuids = set()
        self.ec_uuids = set()

        self.config = config_loader.get_config()

        ELASTICSEARCH_HOSTS = self.config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = self.config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = self.config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)

    def _perform_es_search(self, queries, time_filters=None):
        """ Returns ES results based on the given queries """
        body = build_search_body(queries, time_filters)
        result = self.es.search(body=body,
                                index=self.index,
                                size=1000,
                                sort='@timestamp:asc',
                                ignore_throttled=False)

        results = list()
        for hit in result['hits']['hits']:
            document = {
                '_id': hit['_id'],
                **hit['_source'],
                'msg': convert_to_json(hit['_source']['msg'])
            }
            results.append(document)

        return results

    def _build_query(self, operation, vol_type, uuid):
        """
        Building query list for searching.
        Args:
            operation: Type of operation
                    (CREATE/MOUNT/FAIL_PLEX_ACK/REBUILD)
            vol_type: Type of volume
            uuid
        Returns: list of queries
        """
        opcode = OPERATIONS.get(operation)
        if not opcode:
            raise Exception(f'Could not find opcode for operation: {operation}')
        queries = list()
        if opcode:
            queries.append(f'"opcode: {opcode}"')
        if vol_type:
            queries.append(f'"type: {vol_type}"')
        if uuid:
            queries.append(f'"uuid: {uuid}"')
        return queries

    def get_create_info(self):
        """ Returns info of CREATE operation """
        return self.get_info('CREATE')

    def get_mount_info(self):
        """ Returns info of MOUNT operation """
        return self.get_info('MOUNT')

    def get_snapshot_info(self, uuid, operation='CREATE'):
        queries = self._build_query(operation, VOLUME_TYPES.get('SNAPSHOT'), uuid)
        if operation == 'CREATE':
            pass
            # CHECK: Do we need this?
            # queries.append('"user_created: true"')

        results = self._perform_es_search(queries)
        return results

    def get_clone_info(self, uuid, operation='CREATE'):
        # Base volume of clones can be either snapshots or RDS
        snapshot_info = self.get_snapshot_info(uuid, operation)
        if snapshot_info:
            return snapshot_info
        rds_info = self.get_plex_info(uuid, operation=operation)
        return rds_info

    def get_pv_info(self, pv_id, operation='CREATE'):
        """ Returns results for Part Volume creation/mount """
        queries = self._build_query(operation, VOLUME_TYPES.get('PV'), pv_id)
        if operation == 'CREATE':
            # CHECK: Do we need this?
            queries.append('"user_created: true"')

        results = self._perform_es_search(queries)
        return results

    def get_pvg_info(self, pvg_id, start_time=None, end_time=None, operation='CREATE'):
        """ Returns result for Part Volume Group creation/mount """
        queries = self._build_query(operation, VOLUME_TYPES.get('PVG'), pvg_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        if len(results) == 0:
            raise Exception(f'Could not find PVG Info for UUID: {pvg_id} from time: {start_time} till time: {end_time}')
        # CHECK: Only 1 entry everytime?
        return results[0]

    def get_lsv_info(self, svol_id, start_time=None, end_time=None, operation='CREATE'):
        """ Returns result for LSV creation/mount """
        queries = self._build_query(operation, VOLUME_TYPES.get('LSV'), svol_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        if len(results) == 0:
            raise Exception(f'Could not find LSV Info for UUID: {svol_id} from time: {start_time} till time: {end_time}')
        # CHECK: Only 1 entry everytime?
        return results[0]

    def get_journal_volume_info(self, jvol_id, start_time=None, end_time=None, operation='CREATE'):
        """ Returns result for Journal Volume creation/mount """
        queries = self._build_query(operation, VOLUME_TYPES.get('JVOL'), jvol_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        if len(results) == 0:
            raise Exception(f'Could not find Journal Volume Info for UUID: {jvol_id} from time: {start_time} till time: {end_time}')
        # CHECK: Only 1 entry everytime?
        return results[0]

    def get_ec_volume_info(self, vol_id, start_time=None, end_time=None, operation='CREATE'):
        """ Returns result for EC Volume creation/mount """
        queries = self._build_query(operation, VOLUME_TYPES.get('EC'), vol_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        if len(results) == 0:
            raise Exception(f'Could not find EC Volume Info for UUID: {vol_id} from time: {start_time} till time: {end_time}')
        # CHECK: Only 1 entry everytime?
        return results[0]

    def get_plexes_info(self, pvol_ids, start_time=None, end_time=None, operation='CREATE'):
        """ Returns result of all the plexes found by pvol_ids """
        result = dict()
        for pvol_id in pvol_ids:
            result[pvol_id] = self.get_plex_info(pvol_id, start_time, end_time, operation)

        return result

    def get_primary_info_from_rds(self, rds_info, operation='CREATE'):
        """ Returns primary volume info from RDS volume info """
        subsys_nqn = get_value_from_params(rds_info, 'subsys_nqn')
        # Primary volume ID can be parsed from the subsys_nqn
        vol_id = self._parse_nqn(subsys_nqn)
        replica_info = self.get_plex_info(vol_id, end_time=self.op_time, operation=operation)
        return replica_info

    def _parse_nqn(self, nqn):
        return nqn.split(':')[-1]

    def get_plex_info(self, pvol_id, start_time=None, end_time=None, operation='CREATE'):
        """ Returns result of the plex found by pvol_id """
        # Plexes can be created during the CREATE or MOUNT operation.
        queries = [
            f'("opcode: VOL_ADMIN_OPCODE_CREATE" OR "opcode: VOL_ADMIN_OPCODE_MOUNT")',
            f'"uuid: {pvol_id}"'
        ]
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        if len(results) == 0:
            logging.error(f'Could not find Plex Info for UUID: {pvol_id} from time: {start_time} till time: {end_time}')
            return []

        type = get_value_from_params(results[0], 'type')
        info = list()
        info.append(results[0])
        # Getting info for primary volume if it is replica volume.
        if type == VOLUME_TYPES.get('RDS'):
            # CHECK: What if there are more than 1 entry?
            replica_plex_info = self.get_primary_info_from_rds(results[0], operation)
            info.extend(replica_plex_info)

        return info

    def _get_plex_status_logs(self, vol_id, vol_type='EC', start_time=None, end_time=None):
        """ Returns logs of the plexes' statues found by JVOL/EC uuid """
        vol_type_prefix = 'ecvol' if vol_type == 'EC' else 'repvol'
        queries = [
            f'"{vol_type_prefix} UUID: {vol_id} plex"'
        ]
        time_filters = (start_time, end_time)

        body = build_search_body(queries, time_filters)
        result = self.es.search(body=body,
                                index=self.index,
                                size=1000,
                                sort='@timestamp:asc',
                                ignore_throttled=False)

        return result['hits']['hits']

    def get_plex_status(self, vol_id, vol_type='EC', start_time=None, end_time=None):
        """ Returns the plex status for the given JVOL/EC uuid """
        result = self._get_plex_status_logs(vol_id, vol_type, start_time, end_time)

        plex_status = dict()
        for hit in result:
            log = hit['_source']['msg']
            m = re.match('.*UUID: ([\S]+) plex(?:|\S) ([0-9]+) marked ([\S]+) total failed:([0-9]+)', log)
            if m:
                uuid, plex_num, status, total_failed = m.group(1), m.group(2), m.group(3), m.group(4)
                plex_status[int(plex_num)] = {
                    'info': hit,
                    'status': status
                }

        return plex_status

    # CHECK: Need an example log for this
    def get_failed_plex_info(self, vol_id, start_time=None, end_time=None):
        """ Returns the plex failed status for the given JVOL/EC uuid """
        queries = self._build_query('FAIL_PLEX', None, vol_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        return results

    def _get_failed_plex_ack_info_logs(self, vol_id, start_time=None, end_time=None):
        """ Returns the failed plex ACK logs for the given JVOL/EC uuid """
        queries = self._build_query('FAIL_PLEX_ACK', None, vol_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)
        return results

    def get_failed_plex_ack_info(self, ec_id, start_time=None, end_time=None):
        """ Returns the failed plexes with the timestamp for the given JVOL/EC uuid """
        results = self._get_failed_plex_ack_info_logs(ec_id, start_time, end_time)

        failed_uuids = dict()
        for result in results:
            failed_ids = get_value_from_params(result, 'failed_uuids')
            for id in failed_ids:
                failed_uuids[id] = result

        return failed_uuids

    def get_plex_rebuild_info(self, ec_id, start_time=None, end_time=None):
        """ Returns the plex rebuild status for the given JVOL/EC uuid """
        queries = self._build_query('REBUILD', None, ec_id)
        time_filters = (start_time, end_time)

        results = self._perform_es_search(queries, time_filters)

        rebuild_info = dict()
        for result in results:
            uuid = get_value_from_params(result, 'failed_uuid')
            rebuild_info[uuid] = result

        return rebuild_info

    def get_lifecycle(self):
        """
        Returns the lifecycle of the PV.
        Returns a dict containing keys:
            create: info during CREATE operation
            mount: info during MOUNT operation
            jvol_plex_status_history: Plex status history of JVOL plexes
            ec_plex_status_history: Plex status history of EC plexes
            jvol_failed_plex_ack_history: Failed Plex ACK of JVOL plexes
            ec_failed_plex_ack_history: Failed Plex ACK of EC plexes
        """
        lifecycle = dict()
        lifecycle['create'] = self.get_create_info()
        lifecycle['mount'] = self.get_mount_info()
        lifecycle['jvol_plex_status_history'] = {uuid: self._get_plex_status_logs(uuid, vol_type='JVOL')
                                                    for uuid in self.jvol_uuids}
        lifecycle['ec_plex_status_history'] = {uuid: self._get_plex_status_logs(uuid, vol_type='EC')
                                                    for uuid in self.ec_uuids}

        lifecycle['jvol_failed_plex_ack_history'] = {uuid: self._get_failed_plex_ack_info_logs(uuid)
                                                    for uuid in self.jvol_uuids}
        lifecycle['ec_failed_plex_ack_history'] = {uuid: self._get_failed_plex_ack_info_logs(uuid)
                                                    for uuid in self.ec_uuids}

        return lifecycle

    def get_complete_plex_info(self, vol_id, vol_time, vol_type='EC'):
        """ Returns complete information of plexes for the given JVOL/EC uuid """
        plex_status = self.get_plex_status(vol_id, vol_type, start_time=vol_time, end_time=self.prev_op_time)
        # These occur after the operation in between mounts
        fail_plex_info = self.get_failed_plex_info(vol_id, start_time=self.prev_op_time, end_time=self.op_time)
        fail_plex_ack_info = self.get_failed_plex_ack_info(vol_id, start_time=self.prev_op_time, end_time=self.op_time)
        plex_rebuild_info = self.get_plex_rebuild_info(vol_id, start_time=self.prev_op_time, end_time=self.op_time)

        return {
            'plex_status': plex_status,
            'plex_fail': fail_plex_info,
            'plex_fail_ack': fail_plex_ack_info,
            'plex_rebuild': plex_rebuild_info
        }

    def get_info(self, operation='CREATE'):
        """ Returns PV, PVG and LSV info for the given operation """
        result = list()

        ec_uuid = None
        jvol_uuid = None
        result_data = None

        snapshot_info = self.get_snapshot_info(self.pvol_id, operation)
        if snapshot_info:
            # Snapshot have PV as their base_uuid
            self.pvol_id = get_value_from_params(snapshot_info[0], 'base_uuid')

        pv_info_list = self.get_pv_info(self.pvol_id, operation)
        for pv_info in pv_info_list:
            is_clone = get_value_from_params(pv_info, 'clone')
            clone_info = None
            if is_clone:
                # Check for base volume info
                base_uuid = get_value_from_params(pv_info, 'base_uuid')
                clone_info = self.get_clone_info(base_uuid, operation)
            pvg_uuid = get_value_from_params(pv_info, 'partvg_uuid')
            self.op_time = convert_datetime_str(pv_info['@timestamp'])
            primary_dpu = get_value_from_params(pv_info, 'Dpu')
            # Primary DPU information is either in key Dpu or dpu
            if not primary_dpu:
                primary_dpu = get_value_from_params(pv_info, 'dpu')
            secondary_dpu = get_value_from_params(pv_info, 'secondary')

            pv_result_data = {
                'timestamp': pv_info['@timestamp'],
                'pv_info': pv_info,
                'pvg_uuid': pvg_uuid,
                'primary_dpu': primary_dpu,
                'secondary_dpu': secondary_dpu
            }

            # Checking for status between two CREATE/MOUNT operations
            if self.prev_op_time:
                if jvol_uuid:
                    complete_plex_info = self.get_complete_plex_info(jvol_uuid, jvol_time, vol_type='JOURNAL')
                    result_data['lsv_info'][lsv_uuid]['jvol_info'].update(complete_plex_info)

                if ec_uuid:
                    complete_plex_info = self.get_complete_plex_info(ec_uuid, ecvol_time, vol_type='EC')
                    result_data['lsv_info'][lsv_uuid]['ec_info'].update(complete_plex_info)

                if result_data:
                    result.append(result_data)

            pvg_info = self.get_pvg_info(pvg_uuid, end_time=self.op_time, operation=operation)
            lsv_uuids = get_value_from_params(pvg_info, 'svol_uuid', [])

            pvg_result_data = {
                'timestamp': pvg_info['@timestamp'],
                'pvg_info': pvg_info,
                'lsv_uuids': lsv_uuids
            }

            lsv_result_data = dict()
            # Each PVG can be in multiple LSV
            for lsv_uuid in lsv_uuids:
                lsv_info = self.get_lsv_info(lsv_uuid, end_time=self.op_time, operation=operation)
                jvol_uuid = get_value_from_params(lsv_info, 'jvol_uuid')
                # CHECK: Why is this a list?
                ec_uuids = get_value_from_params(lsv_info, 'pvol_id')
                if len(ec_uuids) == 0:
                    raise Exception(f'Could not find EC UUIDs from LSV UUID: {lsv_uuid}')

                ec_uuid = ec_uuids[0]

                self.jvol_uuids.add(jvol_uuid)
                self.ec_uuids.add(ec_uuid)

                lsv_result_data[lsv_uuid] = {
                    'timestamp': lsv_info['@timestamp'],
                    'lsv_uuid': lsv_uuid,
                    'lsv_info': lsv_info,
                    'jvol_uuid': jvol_uuid,
                    'ec_uuid': ec_uuid
                }

                jvol_info = self.get_journal_volume_info(jvol_uuid, end_time=self.op_time, operation=operation)
                ec_volume_info = self.get_ec_volume_info(ec_uuid, end_time=self.op_time, operation=operation)

                jvol_pvol_uuids = get_value_from_params(jvol_info, 'pvol_id')
                ec_pvol_uuids = get_value_from_params(ec_volume_info, 'pvol_id')

                jvol_plexes_info = self.get_plexes_info(jvol_pvol_uuids)
                ec_plexes_info = self.get_plexes_info(ec_pvol_uuids)

                jvol_time = convert_datetime_str(jvol_info['@timestamp'])
                ecvol_time = convert_datetime_str(ec_volume_info['@timestamp'])

                jvol_result_data = {
                    'timestamp': convert_datetime_str(jvol_info['@timestamp']),
                    'pvol_uuids': jvol_pvol_uuids,
                    'plex_info': jvol_plexes_info
                }
                ec_result_data = {
                    'timestamp': convert_datetime_str(ec_volume_info['@timestamp']),
                    'pvol_uuids': ec_pvol_uuids,
                    'plex_info': ec_plexes_info
                }

                lsv_result_data[lsv_uuid].update({
                    'jvol_info': jvol_result_data,
                    'ec_info': ec_result_data
                })

                # Keeping track of previous operation's time
                self.prev_op_time = self.op_time

            result_data = {
                'snapshot_info': snapshot_info,
                'clone_info': clone_info,
                'pv_info': pv_result_data,
                'pvg_info': pvg_result_data,
                'lsv_info': lsv_result_data
            }

        self.op_time = None
        if jvol_uuid:
            complete_plex_info = self.get_complete_plex_info(jvol_uuid, jvol_time, vol_type='JOURNAL')
            result_data['lsv_info'][lsv_uuid]['jvol_info'].update(complete_plex_info)

        if ec_uuid:
            complete_plex_info = self.get_complete_plex_info(ec_uuid, ecvol_time, vol_type='EC')
            result_data['lsv_info'][lsv_uuid]['ec_info'].update(complete_plex_info)

        if result_data:
            result.append(result_data)

        return result