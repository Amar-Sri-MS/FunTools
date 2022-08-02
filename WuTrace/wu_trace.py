#!/usr/bin/env python3
#
# Converts output from funos-posix's --wulog option into a graphical
# form to show the order and timing of work units.
#
# Usage:
# wutrace.py inputfile [-o outputfile]
#
# Input can be a mix of arbitrary log messages and the wulog messages.
#
# All wu event messages are expected to start with:
#
# 9999999.999999999 faddr VP9.9.9 VERB NOUN ...
#
# where the initial number is the number of seconds and nanoseconds
# since epoch, and the VP... is the fabric address of the unit sending
# the log message.    Verb, for now, is either WU, TIMER, or HU.    For
# WUs, VERB un can be START, END, or SEND.    For timers, VERB must
# be START.    Remaining arguments are always of the form
# 'name value', and should have no separators other than spaces.
#
# Log messages get combined into sequences of WUs, representing all the
# work done on behalf of an incoming request.    Sometimes, a single item
# in the sequence can trigger some sub-tasks, such as timers triggering
# a separate sequence of requests.
#
# TODO(bowdidge): Consider when a WU send represents a call or suboperation,
# and when it represents the next operation.
#
# Copyright (c) 2017 Fungible Inc.    All rights reserved.
#


import argparse
import os
import re
import sys

import event
import read_trace
import render

verbose = False

last_time = 0
saw_time_backwards = False

HU_LID = 0
RGX_LID = 4
LE_LID = 5
ZIP_LID = 6

class TraceProcessor:
    """Converts list of events into transactions.

    This class takes the sequence of WU start, stop, and sends, and
    groups the events into a chain of events called a transaction.

    Transactions represent single conceptual operations from a user's
    point of view - a single packet being handled by the network, or a
    single commit done to storage.
    """

    def __init__(self, input_filename):
        # Map of VPs to sent WUs that have not yet started.
        # Mapped items are tuples of (sender event, called wu, called arg0,
        # called arg1).
        self.caller_queues = {}

        # Map from timer id to the event setting the timer.
        self.timer_to_caller = {}

        # Map from timer id to the time the timer was set.
        # For setting start_time for event.
        self.timer_to_start_time = {}

        # Map from VP to the currently running WU on that VP.
        self.vp_to_event = {}

        # String name of the file which is being read.
        self.input_filename = input_filename

        boot_event = event.TraceEvent(0, 0, 'boot', None)
        self.boot_transaction = event.Transaction(boot_event)
        self.transactions = [self.boot_transaction]

        # list to keep a track of previous start-end events
        self.start_events = []

        # this is a queue representing all the hardware sends
        self.hardware_sends = []

        # this is a dictionary of unpaired hardware sends.
        # Mapping is done using LID from from faddr.
        self.unpaired_hw_sends = {0: [],       # to store all the HU sends
                                  4: [],       # to store all the RGX sends
                                  5: [],       # to store all the LE sends
                                  6: []}       # to store all the ZIP sends

    def remember_send(self, event, wu_id, arg0, arg1, dest, send_time,
                      is_timer, flags):
        """Records the WU send event for later matching with a start.

        event is the sending WU.
        wu_id is the sent wu id.
        arg0 and arg1 are arguments to send_wu to double-check we're correctly
        matching WU order.
        dest is the receiving VP.
        send_time is when the wu send was sent.    This is less interesting for
        WU sends (though it describes order), but important for timers.
        is_timer is true if the send is a timer send.
        flags is raw flag bits from FunOS, indicating gated WUs or sends to HW.
        """
        # TODO(bowdidge): Explicitly keep track of high and low prio WUs.
        # Clear queue so high and low priority queues have same dest.
        dest.queue = 0
        if dest not in self.caller_queues:
            self.caller_queues[dest] = []
        self.caller_queues[dest].append((event, wu_id, arg0, arg1, send_time,
                                         is_timer, flags))

    def find_previous_send(self, wu_id, arg0, arg1, dest):
        """Returns the WU send that would have started a WU with the arguments.
        Returns predecessor event, time that the message was sent, and true if
        the send was a timer start and trigger.
        """
        if dest not in self.caller_queues:
            return (None, 0, False, 0)
        if len(self.caller_queues[dest]) == 0:
            return (None, 0, False, 0)
        for entry in self.caller_queues[dest]:
            (sender, sent_wu_id, sent_arg0, sent_arg1, send_time, is_timer,
             flags) = entry
            if (sent_wu_id == wu_id and sent_arg0 == arg0 and
                    (is_timer or sent_arg1 == arg1)):
                self.caller_queues[dest].remove(entry)
                return (sender, send_time, is_timer, flags)
        return (None, 0, False, 0)

    def find_previous_start(self):
        """ This function will be returning the previous start event so we can
        create a link between the previous start and end using a fake send
        event"""
        return self.start_events[-1]

    def handle_log_line(self, next_event, line_number):
        """Reads in each logging event, and creates or updates log events."""
        global verbose
        if verbose:
            sys.stderr.write('%d: %s\n' % (line_number, next_event))

        if next_event.event_type == event.TIME_SYNC_EVENT:
            # Handled during parsing.
            return
        timestamp = next_event.timestamp

        vp = next_event.faddr
        if next_event.event_type == event.WU_START_EVENT:
            arg0 = next_event.arg0
            arg1 = next_event.arg1
            wu_id = next_event.wuid

            if vp in self.vp_to_event:
                    # Function never saw end.
                    prev_event = self.vp_to_event[vp]
                    prev_event.end_time = timestamp - 0.000000001
                    del self.vp_to_event[vp]
                    sys.stderr.write('%s:%d: START before END.\n' % (
                            self.input_filename,
                            line_number))
                    sys.stderr.write('  timestamp was %d\n' % next_event.timestamp)

            current_event = event.TraceEvent(timestamp, timestamp,
                                             next_event.name, vp)
            self.vp_to_event[vp] = current_event

            # flushing the buffer
            if len(self.start_events) != 0:
                while len(self.hardware_sends) > 0:
                    # this is some hardware send that needs an end
                    previous_start = self.find_previous_start()
                    fake_hw_event = self.hardware_sends[-1]
                    fake_hw_event.end_time = timestamp
                    previous_start.successors.append(fake_hw_event)

                    lid_value = fake_hw_event.vp.lid
                    if (lid_value == 0) or (4 <= lid_value <= 6):
                        self.unpaired_hw_sends[lid_value].append(fake_hw_event)

                    self.hardware_sends.pop()

            (predecessor, send_time,
             is_timer, flags) = self.find_previous_send(wu_id, arg0,
                                                        arg1, vp)

            next_event_lid = next_event.origin_faddr.lid
            if (next_event_lid == HU_LID or next_event_lid == RGX_LID or
                next_event_lid == LE_LID or next_event_lid == ZIP_LID):
                start = len(self.unpaired_hw_sends[next_event_lid]) -1
                for i in range(start, -1, -1):
                    if next_event.origin_faddr == self.unpaired_hw_sends[next_event_lid][i].vp:
                        self.unpaired_hw_sends[next_event_lid][i].end_time = next_event.timestamp
                        self.unpaired_hw_sends[next_event_lid].pop(i)
                        break

            if predecessor and int(flags) & 2:
                    # Hardware WU.
                    hw_event = event.TraceEvent(send_time,
                                                current_event.start_time,
                                                'DMA',
                                                predecessor.vp)
                    hw_event.is_timer = True
                    predecessor.successors.append(hw_event)
                    predecessor = hw_event
                    self.start_events.append(predecessor)
            if predecessor:
                current_event.transaction = predecessor.transaction
                if is_timer:
                    timer_event = event.TraceEvent(send_time,
                                                   current_event.start_time,
                                                   'timer',
                                                   predecessor.vp)
                    timer_event.is_timer = True
                    predecessor.successors.append(timer_event)
                    predecessor = timer_event

                predecessor.successors.append(current_event)
                self.start_events.append(current_event)

            elif next_event.name == 'mp_notify':
                # Bootstrap process. Connect to fake event.
                current_event.transaction = self.boot_transaction
                self.boot_transaction.root_event.successors.append(
                    current_event)
                if not self.boot_transaction.root_event.start_time:
                    self.boot_transaction.root_event.start_time = timestamp
                    self.boot_transaction.root_event.end_time = timestamp

            else:
                # New event not initiated by a previous WU.
                # TODO (SanyaSriv): Remove the merge-all strategy
                if len(self.start_events) != 0:
                    previous_start = self.find_previous_start()
                    previous_start.successors.append(current_event)
                    self.start_events.append(current_event)
                else:
                    transaction = event.Transaction(current_event)
                    self.transactions.append(transaction)
                    current_event.transaction = transaction
                    self.start_events.append(current_event)

        elif next_event.event_type == event.WU_END_EVENT:
            # Identify the matching start event, and set the end time.
            if vp not in self.vp_to_event:
                sys.stderr.write('%s:%d: unexpected WU END.\n' % (
                        self.input_filename,
                        line_number))
                sys.stderr.write('  timestamp was %d\n' % next_event.timestamp)
                return

            current_event = self.vp_to_event[vp]
            del self.vp_to_event[vp]

            if current_event is None:
                sys.stderr.write('Line %d: unexpected WU END.\n' % line_number)
                sys.stderr.write('  timestamp was %d\n' % next_event.timestamp)
                return
            current_event.end_time = timestamp
        elif next_event.event_type == event.WU_SEND_EVENT:
            # Use arg0, the flow pointer, to match up the send with the WU
            # when it starts.
            wuid = next_event.wuid
            arg0 = next_event.arg0
            arg1 = next_event.arg1
            flags = next_event.flags
            send_time = next_event.timestamp

            curr = None

            # TODO(SanyaSriv): Identify associated hardware accelerator WU using faddr, not regex.
            if re.match(".*LE.*", str(next_event.dest_faddr)) != None:
                current_event = event.TraceEvent(send_time, send_time,
                    "HW-LE: " + next_event.name, next_event.dest_faddr)
                # will now connect this to the previous event
                current_event.is_hw_le = True
                self.hardware_sends.append(current_event)

            if re.match(".*ZIP.*", str(next_event.dest_faddr)) != None:
                current_event = event.TraceEvent(send_time, send_time,
                    "HW-ZIP: " + next_event.name, next_event.dest_faddr)
                current_event.is_hw_zip = True
                self.hardware_sends.append(current_event)

            if re.match(".*HU.*", str(next_event.dest_faddr)) != None:
                current_event = event.TraceEvent(send_time, send_time,
                    "HW-HU: " + next_event.name, next_event.dest_faddr)
                current_event.is_hw_hu = True
                self.hardware_sends.append(current_event)

            if re.match(".*RGX.*", str(next_event.dest_faddr)) != None:
                current_event = event.TraceEvent(send_time, send_time,
                    "HW-RGX: " + next_event.name, next_event.dest_faddr)
                current_event.is_hw_rgx = True
                self.hardware_sends.append(current_event)

            if vp in self.vp_to_event:
                curr = self.vp_to_event[vp]
                self.remember_send(curr, wuid, arg0, arg1,
                                   next_event.dest_faddr,
                                   send_time, False, flags)

        elif next_event.event_type == event.HU_SQ_DBL:
            label = 'HU doorbell: sqid=%d' % next_event.sqid
            current_event = event.TraceEvent(
                timestamp, timestamp,
                'HU doorbell: sqid=%d' % next_event.sqid, vp)

            transaction = event.Transaction(current_event)
            self.transactions.append(transaction)
            current_event.transaction = transaction

        elif next_event.event_type == event.TIMER_START_EVENT:
            wuid = next_event.wuid
            timer = next_event.timer
            arg0 = next_event.arg0
            start_time = next_event.timestamp
            if vp not in self.vp_to_event:
                sys.stderr.write('%s:%d: unknown vp in TIMER START\n' % (
                        self.input_filename, line_number))
                return

            current_event = self.vp_to_event[vp]
            if current_event is None:
                sys.stderr.write('%s:%d: unsure what WU started timer.\n' % (
                        self.input_filename, line_number))

            self.remember_send(current_event, wuid, arg0, 0,
                               next_event.dest_faddr,
                               start_time, True, 0)

        elif next_event.event_type == event.TRANSACTION_START_EVENT:
             if vp not in self.vp_to_event:
                 sys.stderr.write('%s:%d: '
                                  'TRANSACTION START not occurring during '
                                  'running WU on %s\n' % (
                         self.input_filename, line_number, vp))
                 return
             current_event = self.vp_to_event[vp]

             # If we've got an active transaction and see START TRANSACTION,
             # stop the old transaction and start a new transaction.
             if (current_event.transaction and
                 not current_event == current_event.transaction.root_event):
                 current_event.transaction.remove(current_event)
                 new_transaction = event.Transaction(current_event)
                 current_event.transaction = new_transaction
                 self.transactions.append(new_transaction)

        elif next_event.event_type == event.TRANSACTION_ANNOT_EVENT:
             if vp not in self.vp_to_event:
                 sys.stderr.write('%s:%d: '
                                  'TRANSACTION ANNOT not occurring in running '
                                  'WU on %s\n' % (
                         self.input_filename, line_number, vp))
                 return
             current_event = self.vp_to_event[vp]
             annot_event = event.TraceEvent(timestamp, timestamp,
                                            next_event.msg, vp)
             annot_event.is_annotation = True
             current_event.successors.append(annot_event)

        else:
            sys.stderr.write('%s:%d: Invalid event type %d\n' % (
                    self.input_filename, line_number, next_event.event_type))
            return


def main(argv):
    global verbose
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('inputs', metavar='file', type=str, nargs='+',
                                            help='log files to read')
    arg_parser.add_argument('--input-format', choices=['uart', 'trace'],
                            type=str, default='uart',
                            help='Choice of input file format. If the trace'
                            'format is used, a funos binary must be '
                            'provided.')
    arg_parser.add_argument('--funos-binary', type=str,
                            help='path to unstripped funos binary')
    arg_parser.add_argument('--wu-list', type=str,
                            help='path to unstripped funos binary')
    arg_parser.add_argument(
        '--format', type=str,
        help='output style: html (default), text, or graphviz.', default=None)
    arg_parser.add_argument('--output', nargs=1, help='file name to write to')
    arg_parser.add_argument('--event-output', type=str, help='file name to write raw events to')
    arg_parser.add_argument('--verbose', action='store_const', const=True,
                            help='add debugging output')
    args = arg_parser.parse_args()

    input_filename = args.inputs[0]
    if not os.path.exists(input_filename):
        sys.stderr.write('No such file "%s"' % input_filename)
        sys.exit(1)

    if args.verbose:
        verbose = True

    # Write out individual trace events for debugging if requested.
    raw_event_file = None
    if args.event_output:
        raw_event_file = args.event_output

    if args.format is not None:
        if args.format not in ['text', 'html', 'graphviz', 'json']:
            sys.stderr.write(
                'Unknown option %s to --format. '
                'Must be text, html, graphviz, json.\n')
            exit(1)
    if args.input_format == 'uart':
        with open(input_filename) as fh:
            trace_parser = read_trace.TraceLogParser()
            events = trace_parser.parse(fh, filename=input_filename)
    else:
        if not args.funos_binary and not args.wu_list:
            sys.stderr.write('Must specify --funos-binary or --wu-list '
                             'when input is a trace file\n')
            exit(1)
        with open(input_filename, 'rb') as fh:
            wu_list = []
            if args.funos_binary:
                extractor = read_trace.WuListExtractor(args.funos_binary)
                wu_list = extractor.generate_wu_list()
            if args.wu_list:
                with open(args.wu_list) as f:
                    wu_list = f.readlines()

            file_parser = read_trace.TraceFileParser(wu_list)
            events = file_parser.parse(fh, raw_event_file)

    trace_parser = TraceProcessor(input_filename)
    for idx, e in enumerate(events):
        trace_parser.handle_log_line(e, idx)
    transactions = trace_parser.transactions

    out_file = sys.stdout
    if args.output is not None:
        out_file = open(args.output[0], 'w')

    # Hack: Update start and end time on fake event on boot.
    boot_events = transactions[0].flatten()

    if args.format == 'text':
        for tr in transactions:
            render.dump(out_file, tr)
            print('\n')
    elif args.format == 'graphviz':
        render.render_graphviz(out_file, transactions)
    elif args.format == 'json':
        json = render.render_json(transactions)
        out_file.write(json)
    elif args.format is None or args.format == 'html':
        out_file.write(render.render_html(transactions))
    out_file.close()


if __name__ == '__main__':
        main(sys.argv[1:])
