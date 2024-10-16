#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
import collections
import subprocess

from perf_sample import PerfSample, perf_table_from_perf_samples
from perf_sample import table_from_custom_samples
from perf_data import PerfData
from wu_stack_range import WuStackRange


# Standard constant names for files that contain important
# information about the perf run.
MIPS_CONSOLE_INFO_FILENAME = "mips_console_perf_info.json"
WU_LIST_FILENAME = "wu_list.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workdir", help="path to directory with perfmon files")
    parser.add_argument("funos_image", help="path to symbol-rich FunOS binary")
    parser.add_argument("--funos-log", help="path to FunOS UART log file")
    args = parser.parse_args()
    run(args)


def run(args):
    print("Working directory: %s" % args.workdir)
    make_perf_data(args)


def make_perf_data(args):
    generate_mips_console_perf_info(args.workdir, args.funos_log)
    generate_wu_list(args.workdir, args.funos_image)

    # Outputs:
    perf_samples_file = "perf_samples.txt"
    perf_table_file = "perf_table.txt"
    custom_data_file = "custom_perf_table.txt"

    generate_perf_data(
        args.workdir,
        glob.glob(os.path.join(args.workdir, "*perfmon*")),
        perf_samples_file,
        perf_table_file,
        custom_data_file,
    )


def generate_wu_list(job_dir, funos_image_path):
    """Generates WU List file from FunOS Image file.

    Args:
        job_dir: the job directory.
        funos_image_file: file name of FunOS Image. [input]

    Returns:
        None.  Only reads input file(s), writes output file(s).
    """

    print("Generating WU List")

    linux_gdb_path = "/opt/cross/mips64/bin/mips64-unknown-elf-gdb"
    mac_gdb_path = "/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb"
    gdb_path = mac_gdb_path if os.uname()[0] == "Darwin" else linux_gdb_path

    gdb_command = [
        gdb_path,
        "--nx",  # Do not read any .gdbinit files in any directory.
        "-batch",  # Exit after processing options.
        "--eval-command",
        "set print elements 100000",
        "--eval-command",
        "set print repeats 0",
        "--eval-command",
        "set print array on",
        "--eval-command",
        "set max-value-size 262144",
        "--eval-command",
        "p *wu_handlers_default@16384",
        funos_image_path,
    ]

    gdb_command_string = " ".join(gdb_command).replace(" -", " \\\n-")
    print("Executing GDB as:")
    print("  ", gdb_command_string.replace("\n", "\n    "))

    try:
        gdb_output = subprocess.check_output(gdb_command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        print("GDB failed with return code %d\n" % error.returncode)
        print("GDB output:\n%s\n" % error.output)
        raise error

    # GDB output is like so:
    #
    # $1 =   {0xa800000000118c38 <wuh_idle>,
    #   0xa800000000104e38 <ws_free_frame>,
    #   0xa800000000107348 <ws_free_frame_with_callback>,
    #   ...
    #   0xa800000000103e80 <invalid_runtime_wuh>,
    #   0xa800000000103e80 <invalid_runtime_wuh>}
    #
    decoded_output = gdb_output.decode("utf-8")

    wu_pattern = r"<(?P<wu>.+?)>"
    wu_regex = re.compile(wu_pattern)

    wu_list = []
    for line in decoded_output.split("\n"):
        match = wu_regex.search(line)
        if match:
            wu = match.group("wu")
            assert " " not in wu
            wu_list.append(wu)

    wu_list_path = os.path.join(job_dir, WU_LIST_FILENAME)
    with open(wu_list_path, "w") as fp:
        json.dump(wu_list, fp)

    print("Succeeded in Generating WU List")


def get_wu_list(job_dir, wu_list_file):
    """Returns WU List."""

    wu_list_path = os.path.join(job_dir, wu_list_file)
    with open(wu_list_path, "r") as fp:
        wu_list = json.load(fp)
        return wu_list


# Generate Perf Data.
#
# Inputs:
#     mips_console_perf_info.json (Perf-relevant Info from MIPS Console)
#     wu_list.json                (WU List)
#     one or more files           (Perf Profiling Output)
#
# Outputs:
#     perf_samples.txt (Perf Samples)
#     perf_table.txt   (Perf Table)
#
def generate_perf_data(
    job_dir,
    perf_profiling_output_file_list,
    perf_samples_file,
    perf_table_file,
    custom_data_file,
):
    """Generates Perf Data files from Perf Profiling Output file(s) and other files.

    Args:
        job_dir: the job directory.
        perf_profiling_output_file_list: list of file names of Perf Profiling Output. [input]
        perf_samples_file: file name of Perf Samples. [output]
        perf_table_file: file name of Perf Table. [output]
        custom_data_file: file name of custom data file [output]
        perf_data_file: file name of Perf Data. [output]

    Returns:
        None.  Only reads input file(s), writes output file(s).
    """

    print("Generating Perf Data")
    print

    # Get Perf-relevant Info from MIPS Console.
    mips_console_perf_info = get_mips_console_perf_info(
        job_dir, MIPS_CONSOLE_INFO_FILENAME
    )
    for kvp in mips_console_perf_info.items():
        print("%-14s : %s" % kvp)

    # Get WU List.
    wu_list = get_wu_list(job_dir, WU_LIST_FILENAME)
    print("%-14s : %s" % ("wu_count", len(wu_list)))

    event_types = mips_console_perf_info["event_types"]
    wu_stack_range = mips_console_perf_info["wu_stack_range"]
    debug_build = mips_console_perf_info["debug_build"]

    if debug_build:
        print(
            "WARNING!!! This appears to be a debug build, which is not a good candidate for Perf Profiling"
        )

    # Parse Perf Profiling Output file(s) to extract Perf Samples.
    perf_samples, custom_samples = parse_perf_profiling_output(
        job_dir, perf_profiling_output_file_list, wu_list
    )

    # Transform Perf Samples into Perf Table.
    perf_table = perf_table_from_perf_samples(perf_samples, event_types)

    # Transform custom samples into table
    custom_data_table = table_from_custom_samples(custom_samples)

    overflow_stats = determine_overflow_stats(job_dir)

    # Create Perf Data from Perf Table and other pieces of information.
    perf_data = PerfData(
        event_types, wu_stack_range, debug_build, perf_table, overflow_stats
    )

    # Tahsin's request: the dispatch cycles calculation should be removed.
    # The reasons are:
    #    1. The calculation includes part of the previous dispatch (flushing)
    #       as well as the current one, and it is hard to draw conclusions as
    #       a result.
    #    2. Most users do not care about the dispatch loop and are confused
    #       by this metric.
    #    3. The users that do care already have a test to measure and optimize
    #       the dispatch loop.
    #
    # perf_data.calculate_dispatch_cycles()

    # Write Perf Samples in text file for manual validation.
    with open(os.path.join(job_dir, perf_samples_file), "w") as fp:
        fp.write("%s\n" % PerfSample.header_str())
        for sample in perf_samples:
            fp.write("%s\n" % sample)

    # Write Perf Table in text file for manual inspection.
    with open(os.path.join(job_dir, perf_table_file), "w") as fp:
        for row in perf_table:
            cells = map(lambda elm: str(elm), row)
            line = "\t".join(cells)
            fp.write("%s\n" % line)

    # Write custom data to a file
    with open(os.path.join(job_dir, custom_data_file), "w") as fp:
        for row in custom_data_table:
            cells = map(lambda cell: str(cell), row)
            line = "\t".join(cells)
            fp.write("%s\n" % line)

    print("Succeeded in Generating Perf Data")


def get_perf_data_from_table(job_dir, perf_data_file):
    """
    Read perf data from multiple data sources:
        1. The raw samples in the perf_data_file
        2. The WU list file
        3. The parsed MIPS console information file.

    Returns a PerfData object holding all the information necessary to
    view perf results.
    """
    table_file = os.path.join(job_dir, perf_data_file)

    mips_console_perf_info = get_mips_console_perf_info(
        job_dir, MIPS_CONSOLE_INFO_FILENAME
    )
    wu_list = get_wu_list(job_dir, WU_LIST_FILENAME)

    event_types = mips_console_perf_info["event_types"]
    wu_stack_range = mips_console_perf_info["wu_stack_range"]
    debug_build = mips_console_perf_info["debug_build"]

    rows = []
    with open(table_file) as f:
        header = True
        for line in f:
            parts = line.split()
            if header:
                # Column headers just get appended without fuss
                header = False
                rows.append(tuple(parts))
                continue

            # This is stupifyingly expensive in memory usage: each entry
            # in the tuple is 8 bytes, each int is an additional 24 bytes, and
            # each string is a minimum of 37 bytes. This goes some way towards
            # explaining why the perf server is such a memory hog.
            rows.append(
                (
                    int(parts[0]),  # timestamp
                    parts[1],  # vp
                    parts[2],  # wu
                    int(parts[3]),
                    int(parts[4]),  # cycles, ctr0
                    int(parts[5]),
                    int(parts[6]),  # ctr1, ctr2
                    int(parts[7]),
                    int(parts[8]),
                )
            )  # ctr3, arg0

    overflow_stats = determine_overflow_stats(job_dir)

    perf_data = PerfData(event_types, wu_stack_range, debug_build, rows, overflow_stats)
    return perf_data


def parse_perf_profiling_output(job_dir, perf_profiling_output_file_list, wu_list):
    perf_samples = []
    all_custom_samples = []
    for perf_profiling_output_file in perf_profiling_output_file_list:
        samples, custom_samples = parse_perf_samples(
            perf_profiling_output_file, wu_list
        )
        perf_samples += samples
        all_custom_samples += custom_samples
    return perf_samples, all_custom_samples


def parse_perf_samples(perf_profiling_output_path, wu_list):

    with open(perf_profiling_output_path, "r") as perf_profiling_output:
        lines = filter(
            lambda line: len(line) > 0,
            map(lambda line: line.strip(), perf_profiling_output),
        )

        values = map(lambda line: int(line, base=16), lines)

        # Group values by vp.
        vp_to_values = collections.defaultdict(list)
        for value in values:
            vp = value & 0xFF
            assert vp < 9 * 24
            vp_to_values[vp].append(value)

        samples, custom_samples = construct_samples(vp_to_values, wu_list)
        return samples, custom_samples


def construct_samples(vp_to_values, wu_list):
    """
    Constructs the samples for the given vp_to_values dict.

    :param vp_to_values: dict of vp to values list
    :param wu_list: wu names as list indexed by wu id
    :return: (list of samples, list of custom samples)
    """
    samples = []
    custom_samples = []
    for vp, values in vp_to_values.items():
        sample_count_for_vp = 0
        assert len(values) % PerfSample.LINES_PER_SAMPLE == 0, len(values)
        for i in range(0, len(values), PerfSample.LINES_PER_SAMPLE):
            sample = PerfSample(
                vp, wu_list, *values[i : i + PerfSample.LINES_PER_SAMPLE]
            )
            if sample.custom_data is not None:
                custom_samples.append(sample)
                continue
            samples.append(sample)
            sample_count_for_vp += 1

            # Make sure the samples for a given VP are in chronological order
            if sample_count_for_vp > 1:
                assert samples[-2].timestamp < samples[-1].timestamp, "\n%s\n%s" % (
                    samples[-2],
                    samples[-1],
                )
    return samples, custom_samples


def determine_overflow_stats(job_dir):
    """
    Finds all overflow reports in the odp directory and creates a
    cluster.core to overflow stats dictionary.
    """
    file_glob = os.path.join(job_dir, "odp", "overflow*.txt")
    files = glob.glob(file_glob)
    overflow_stats = {}

    for f in files:
        match = re.match(r".*/overflow_(\d+)_(\d+).txt", f)
        if match:
            cluster_core = "%s.%s" % (match.group(1), match.group(2))
            with open(f, "r") as fh:
                stats = json.load(fh)
                overflow_stats[cluster_core] = stats

    return overflow_stats


def generate_mips_console_perf_info(job_dir, mips_console_output):
    """Generates Perf-relevant Info file from MIPS Console Output file(s).

    Args:
        job_dir: the job directory.
        mips_console_output: file name of MIPS Console Output. [input]

    Returns:
        None.  Only reads input file(s), writes output file(s).
    """

    print("Generating Perf-relevant Info from MIPS Console")

    event_types, wu_stack_range, debug_build = parse_mips_console_output(
        job_dir, mips_console_output
    )

    # If debug build, adjust the values of WU Stack start & end.
    if debug_build:
        wu_stack_range = wu_stack_range.xkphys_to_xkseg()

    mips_console_perf_info = {
        "event_types": event_types,
        "wu_stack_range": wu_stack_range,
        "debug_build": debug_build,
    }

    for kvp in mips_console_perf_info.items():
        print("%-14s : %s" % kvp)

    mips_console_perf_info_path = os.path.join(job_dir, MIPS_CONSOLE_INFO_FILENAME)
    with open(mips_console_perf_info_path, "w") as fp:
        json.dump(mips_console_perf_info, fp)

    print("Succeeded in Generating Perf-relevant Info from MIPS Console")


def get_mips_console_perf_info(job_dir, mips_console_perf_info_file):
    """Returns Perf-relevant Info extracted from MIPS Console."""

    mips_console_perf_info_path = os.path.join(job_dir, mips_console_perf_info_file)
    with open(mips_console_perf_info_path, "r") as fp:
        perf_info = json.load(fp)

        # Fix-up WU Stack Range by converting it from list to WuStackRange.
        wu_stack_range = perf_info.get("wu_stack_range")
        if wu_stack_range:
            perf_info["wu_stack_range"] = WuStackRange(*wu_stack_range)

        return perf_info


def parse_mips_console_output(job_dir, mips_console_output_path):
    """Parses MIPS Console Output file for Perf-relevant info."""

    event_types = parse_event_types(mips_console_output_path)
    if len(event_types) != PerfData.EVENT_COUNT:
        print(
            "Could not find exactly %d event types in MIPS Console Output: %s"
            % (PerfData.EVENT_COUNT, mips_console_output_path)
        )

    wu_stack_range = parse_wu_stack_range(mips_console_output_path)

    debug_build = parse_debug_build_marker(mips_console_output_path)

    return event_types, wu_stack_range, debug_build


def parse_event_types(mips_console_output_path):

    header_text = "Perf interposer is collecting counters for events:"
    header_regex = re.compile(header_text)
    if mips_console_output_path is None:
        return ["unknown"] * 4

    with open(mips_console_output_path, "r") as mips_console:

        # Seek to the line matching the header text.
        for line in iter(mips_console.readline, ""):
            if header_regex.search(line):
                break

        # Read the next EVENT_COUNT number of lines.  Note that file.readline
        # does not raise exception on reaching EOF but simply returns empty
        # string.  So in cases of no header line found or premature EOF after
        # the header line, we correctly return empty or partial list.
        lines = [mips_console.readline().strip() for _ in range(PerfData.EVENT_COUNT)]
        lines = filter(lambda line: len(line) > 0, lines)
        event_types = map(lambda line: line.split()[-1], lines)
        return list(event_types)


def parse_wu_stack_range(mips_console_output_path):
    if mips_console_output_path is None:
        return WuStackRange(0xA800000000000000, 0xA800000000000000)

    # Looking for line containing string of form:
    #   "wustack 0x0123456789ABCDEF 0x0123456789ABCDEF <integer> <unit: KB or MB>"
    wu_stack_range_pattern = r"wustack\s+(?P<start>0x[0-9a-fA-F]{16})\s+(?P<end>0x[0-9a-fA-F]{16})\s+\d+\s+[KM]B"
    wu_stack_range_regex = re.compile(wu_stack_range_pattern)

    with open(mips_console_output_path, "r") as mips_console:
        for line in mips_console:
            match = wu_stack_range_regex.search(line)
            if match:
                start = int(match.group("start"), base=16)
                end = int(match.group("end"), base=16)
                return WuStackRange(start, end)
    return None


def parse_debug_build_marker(mips_console_output_path):
    if mips_console_output_path is None:
        return False

    debug_build_text = "installing interposer 'validate'"
    debug_build_regex = re.compile(debug_build_text)

    with open(mips_console_output_path, "r") as mips_console:
        for line in mips_console:
            if debug_build_regex.search(line):
                return True
    return False


if __name__ == "__main__":
    main()
