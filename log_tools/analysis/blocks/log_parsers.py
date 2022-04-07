#
# Parsers for log lines from various sources
#

import datetime
import dateutil
import json
import logging
import re

from blocks.block import Block
from utils import timeline

class FunOSInput(Block):
    """ Handles FunOS log files """
    def __init__(self):
        self.is_multiline = False
        self.multilines = list()

    def process(self, iters):
        timeline.track_start('log_parser')
        yield from self.lines2tuples(iters[0])
        timeline.track_end('log_parser')

    def lines2tuples(self, iter):
        uboot_done = False

        for (_, _, system_type, system_id, uid, _, _, line) in iter:
            line = line.strip()

            if not uboot_done and self.is_uboot(line):
                # TODO (jimmy): deal with u-boot lines
                continue
            else:
                try:
                    uboot_done = True

                    # Example:
                    # [23.855474 1.5.2] NOTICE nvdimm ...
                    ts_vp_sep = line.find(']')

                    # Empty or malformed line ewwwww
                    if not line.startswith('[') or ts_vp_sep == -1:
                        continue

                    ts_vp = line[1:ts_vp_sep]
                    ts, vp = self.split_ts_vp(ts_vp)

                    date_time, usecs = self.normalize_ts(ts)
                    line = line[ts_vp_sep + 1:]

                    # FunOS logs print JSON output as multiline logs.
                    # This is a workaround to gather the JSON output lines and combine
                    # them into one log message. This is useful for searching logs
                    # containing multiple key values from the JSON output.
                    multiline_start = 'NOTICE volume_manager "Storage: command data {'
                    multiline_end = '}"'
                    if multiline_start in line and line[-1] != '"':
                        self.is_multiline = True
                        multiline_tuple = (date_time, usecs, system_type, system_id, uid, None, None)
                        line = '[{}] {}'.format(vp, line)

                    if self.is_multiline:
                        self.multilines.append(line)
                        if multiline_end in line:
                            self.is_multiline = False
                            line = '\n'.join(self.multilines)
                            yield (*multiline_tuple, line)
                            multiline_tuple = tuple()
                            self.multilines = list()

                        continue

                    line = '[{}] {}'.format(vp, line)

                    yield (date_time, usecs, system_type, system_id, uid, None, None, line)
                except:
                    logging.warning(f'Malformed line in FUNOS logs: {line}')
                    continue

    @staticmethod
    def is_uboot(line):
        """
        Silly heuristic that determines if a line is u-boot or not.

        Only needs to work until the first non u-boot line is detected, after which
        it should not be called.
        """
        if not line.startswith('['):
            return True

        return 'microseconds' in line[:30]

    @staticmethod
    def split_ts_vp(ts_vp):
        ts_vp_parts = ts_vp.split(' ')
        return (ts_vp_parts[0], ts_vp_parts[1])

    @staticmethod
    def normalize_ts(ts):
        """
        Turn the timestamp into a datetime object
        """
        dot_idx = ts.find('.')

        secs = int(ts[:dot_idx])
        usecs = int(ts[dot_idx+1:])

        # TODO (jimmy): There is potential precision loss here, but my floating
        #               point error analysis is too rusty. Conventional
        #               wisdom on the WWW suggests 15-17 significant digits
        #               and our timestamps are 16 digits, so we are on the
        #               limit.
        #
        #               Also, the resulting object is timezone-naive. This
        #               is a general question for logs: should we use UTC?
        dt = datetime.datetime.utcfromtimestamp(secs + float(usecs) * 1e-6)

        # There have been some issues FunOS logs which merges logs and make
        # the timestamp incorrect.
        # Elasticsearch has a limit of supporting timestamp upto the year
        # 2262 when storing them in nanoseconds resolution
        if dt.year >= 2262:
            raise Exception('Timestamp out of range')
        return dt, usecs


class ISOFormatInput(Block):
    """ Handles logs with ISO format timestamps """
    def process(self, iters):
        timeline.track_start('log_parser')
        for (_, _, system_type, system_id, uid, _, _, line) in iters[0]:
            line = line.strip()

            # Example:
            # 2020-07-09 16:37:59.240281 Start probing thread
            parts = line.split(' ', 2)

            iso_format_datetime = parts[0] + ' ' + parts[1]
            d = datetime.datetime.fromisoformat(iso_format_datetime)

            yield (d, d.microsecond, system_type, system_id, uid, None, None, parts[2])
        timeline.track_end('log_parser')

class GenericInput(Block):
    """
    Handles logs with generic pattern: <FILE_NAME|EMPTY> <DATE> <TIMESTAMP>
    <MILLISECONDS|MICROSECONDS|EMPTY> <TIMEZONE_OFFSET|EMPTY> <MESSAGE>
    """
    def process(self, iters):
        timeline.track_start('log_parser')
        for (_, _, system_type, system_id, uid, _, _, line) in iters[0]:
            line = line.strip()
            # Ignore if the line is empty
            if line == '':
                continue

            try:
                # Match order <FILE_NAME|EMPTY> <DATE> <TIMESTAMP> <MILLISECONDS|MICROSECONDS|EMPTY>
                # <TIMEZONE_OFFSET|EMPTY> <MESSAGE>
                # The log message at the end also includes newline characters to support multiline logs
                # Examples:
                # 2020-08-03 14:13:04,086085 INFO XXX
                # 2020/08/05 02:48:10.850085 INFO    tracer
                # 2020-08-05 02:20:16.863085 -0700 PDT XXX
                # [simple_ctx_scheduler.go:128] 2020-08-05 02:20:16.863085 -0700 PDT XXX
                # simple_ctx_scheduler.go:128 2020-08-05 02:20:16.863085 XXX
                # 2021-02-11T12:08:00.951926Z DBG XXX
                # [2021-04-29 04:20:32,492] INFO shutting down (kafka.server.KafkaServer)
                m = re.match(
                    r'^(\[[\S]+\]\s|[\S]+\s|)(?:\[|)(\d{2,4}(?:-|/)\d{2}(?:-|/)\d{2,4})+(?:T|\s)([:0-9]+)[\.|\,]{0,1}([0-9]*)(?:\]|)\s?((?:-|\+|)[0-9]{2}[:]{0,1}[0-9]{2}|Z|)([\s\S]*)',
                    line)

                if m:
                    filename, date_str, time_str = m.group(1), m.group(2), m.group(3)
                    secs_str, tz_offset_str, msg = m.group(4), m.group(5), m.group(6)

                    date_time, usecs = self.extract_timestamp(date_str,
                                                            time_str,
                                                            secs_str)
                    # Prepending filename if present to the log message
                    if filename:
                        msg = filename.strip() + ' ' + msg.strip()
                    yield (date_time, usecs, system_type, system_id, uid, None, None, msg)
                else:
                    logging.warning(f'Malformed line in {uid}: {line}')
            except:
                logging.exception(f'Malformed line in {uid}: {line}')
        timeline.track_end('log_parser')

    @staticmethod
    def extract_timestamp(day_str, time_str, secs_str):
        # Converting nanoseconds to microseconds because Python datetime only supports upto microseconds
        # TODO (Sourabh): Precision loss due to conversion microseconds
        usecs_str = secs_str[0:6] if len(secs_str) > 6 else secs_str

        day_str = day_str.replace('-', '/')
        log_time = f"{day_str} {time_str}.{usecs_str}" if usecs_str else f"{day_str} {time_str}.0"
        d = dateutil.parser.parse(log_time)

        return d, d.microsecond


class KeyValueInput(Block):
    """
    Handles logs with key value log format
    """
    def __init__(self):
        # Default key name mappings
        self.key_name_mappings = {
            'time': 'time',
            'msg': 'msg',
            'level': 'level'
        }
        self.value_separator = '='

    def set_config(self, cfg):
        self.key_name_mappings.update(cfg.get('key_name_mappings', {}))

    def process(self, iters):
        timeline.track_start('log_parser')
        # Matches the line into a list of key value tuple
        # Example:
        # time="2020-09-26T03:04:51.267809475-07:00" level=info msg="Previous key not present"
        split_regex = r"""
            (?P<key>[\w\-]+)=       # Key consists of only alphanumerics and '-' character
            (?P<quote>["']?)        # Optional quote character.
            (?P<value>[\S\s]*?)     # Value is a non greedy match
            (?P=quote)              # Closing quote equals the first.
            ($|\s)                  # Entry ends with comma or end of string
        """.replace("=", self.value_separator)
        regex = re.compile(split_regex, re.VERBOSE)

        for (_, _, system_type, system_id, uid, _, _, line) in iters[0]:
            line = line.strip()
            # Ignore if the line is empty
            if line == '':
                continue

            try:
                log_field_tuples = regex.findall(line)
                log_fields = dict()
                for key, _, value, _ in log_field_tuples:
                    # Removing quotations at the start & end if any
                    value = value.lstrip('\"')
                    value = value.rstrip('\"')
                    log_fields[key] = value

                time_str = log_fields.get(self.key_name_mappings.get('time'), None)
                if time_str:
                    date_time, usecs = self.extract_timestamp(time_str)

                    # Extract the log message's level either from the log or from the name of the log file
                    # This field then can be indexed to the log storage and be used for filtering out the
                    # logs. TODO (Sourabh): Need to standardize the names of log message levels
                    msg = log_fields.get(self.key_name_mappings.get('msg'), '')
                    level = log_fields.get(self.key_name_mappings.get('level'))

                    yield (date_time, usecs, system_type, system_id, uid, None, level, msg)
                else:
                    logging.warning(f'Malformed timestamp in {uid}: {line}')
            except:
                logging.exception(f'Malformed line in {uid}: {line}')

        timeline.track_end('log_parser')

    @staticmethod
    def extract_timestamp(time_str):

        # 2020-08-04T23:09:14.705144973-07:00 OR 2020-08-04 23:09:14.705144973-07:00
        # OR 2020/08/04 23:09:14.705144973
        m = re.match(r'^(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+)[.]{0,1}([0-9]*)([\s\S]*)', time_str)
        day_str, time_str, secs_str, tz_offset = m.group(1), m.group(2), m.group(3), m.group(4)

        # Converting nanoseconds to microseconds because Python datetime only supports upto microseconds
        # TODO (Sourabh): Precision loss due to conversion microseconds
        usecs_str = secs_str[0:6] if len(secs_str) > 6 else secs_str

        day_str = day_str.replace('-', '/')
        log_time = f"{day_str} {time_str}.{usecs_str}" if usecs_str else f"{day_str} {time_str}.0"

        d = dateutil.parser.parse(log_time)

        # adding if timezone offset is present, converting to UTC
        # if tz_offset:
        #     tz_d = datetime.datetime.strptime(tz_offset, '%z')
        #     time_delta = tz_d.tzinfo.utcoffset(None)
        #     d = d + time_delta

        return d, d.microsecond


class JSONInput(Block):
    """
    Handles logs with JSON logs
    """
    def __init__(self):
        # Default key name mappings
        self.key_name_mappings = {
            'time': 'time',
            'msg': 'msg',
            'level': 'level'
        }

    def set_config(self, cfg):
        self.key_name_mappings.update(cfg.get('key_name_mappings', {}))

    def process(self, iters):
        timeline.track_start('log_parser')
        for (_, _, system_type, system_id, uid, _, _, line) in iters[0]:
            line = line.strip()
            # Ignore if the line is empty
            if line == '':
                continue

            try:
                # Converts the log line into a dict
                log_fields = json.loads(line)

                time_str = log_fields.get(self.key_name_mappings.get('time'), None)
                if time_str:
                    date_time, usecs = self.extract_timestamp(time_str)

                    # Extract the log message's level either from the log or from the name of the log file
                    # This field then can be indexed to the log storage and be used for filtering out the
                    # logs. TODO (Sourabh): Need to standardize the names of log message levels
                    msg = log_fields.get(self.key_name_mappings.get('msg'), '')
                    level = log_fields.get(self.key_name_mappings.get('level'))

                    yield (date_time, usecs, system_type, system_id, uid, None, level, msg)
                else:
                    logging.warning(f'Malformed timestamp in {uid}: {line}')
            except:
                logging.exception(f'Malformed line in {uid}: {line}')

        timeline.track_end('log_parser')

    @staticmethod
    def extract_timestamp(time_str):
        # 2020-08-04T23:09:14.705144973-07:00 OR 2020-08-04 23:09:14.705144973-07:00
        # OR 2020/08/04 23:09:14.705144973
        m = re.match(r'^(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+)[.]{0,1}([0-9]*)([\s\S]*)', time_str)
        day_str, time_str, secs_str, tz_offset = m.group(1), m.group(2), m.group(3), m.group(4)

        # Converting nanoseconds to microseconds because Python datetime only supports upto microseconds
        # TODO (Sourabh): Precision loss due to conversion microseconds
        usecs_str = secs_str[0:6] if len(secs_str) > 6 else secs_str

        day_str = day_str.replace('-', '/')
        log_time = f"{day_str} {time_str}.{usecs_str}" if usecs_str else f"{day_str} {time_str}.0"

        d = dateutil.parser.parse(log_time)

        # adding if timezone offset is present, converting to UTC
        # if tz_offset:
        #     tz_d = datetime.datetime.strptime(tz_offset, '%z')
        #     time_delta = tz_d.tzinfo.utcoffset(None)
        #     d = d + time_delta

        return d, d.microsecond