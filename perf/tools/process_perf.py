#!/usr/bin/env python3

#
# Runs the sequence of tools that are required to turn raw data dumps from
# perf into something suitable for the perf visualization tools (the
# perfmon format).
#
# Usage: process_perf.py -h to see options and usage
#

import argparse
import glob
import os
import subprocess
import shutil
import sys
import tempfile
import time

from subprocess import CalledProcessError

PARSER_DIR = None
DQR_DIR = None
WUPROF_DIR = None
MISSMAP_DIR = None

MAX_CLUSTERS = 9
CC_ID = 8
MAX_CORES_PER_PC = 6
MAX_CORES_PER_CC = 4

MODULE_PATH = os.path.realpath(__file__)
MODULE_DIRECTORY = os.path.dirname(MODULE_PATH)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("trace_files", type=str, nargs="+", help="Files with traces")
    parser.add_argument(
        "--output-dir", type=str, help="Output directory", default="results"
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skips the clean up of intermediate files",
        default=False,
    )
    parser.add_argument(
        "--parse-mode",
        type=str,
        help="type of parser to run",
        default="perf",
        choices=["perf", "perf_pdt", "perf_emu", "cache_miss"],
    )
    parser.add_argument(
        "--tools-dir",
        type=str,
        help="directory for tools (FunTools)",
        default=os.path.join(os.getenv("WORKSPACE"), "FunTools"),
    )
    parser.add_argument(
        "--funos-image",
        type=str,
        help="path to symbol-rich FunOS binary",
    )
    parser.add_argument(
        "--funos-log",
        type=str,
        help="path to FunOS UART log",
    )
    args = parser.parse_args()
    set_global_tool_locations(args.tools_dir)

    if args.parse_mode == "perf_emu":
        run_perf_parser(args)
    elif args.parse_mode == "perf":
        run_trace_record_parsing(args)
    elif args.parse_mode in ["perf_pdt", "cache_miss"]:
        run_pdtrace_parsing(args)


def set_global_tool_locations(tools_dir):
    global PARSER_DIR
    global DQR_DIR
    global WUPROF_DIR
    global MISSMAP_DIR

    PARSER_DIR = os.path.join(tools_dir, "TraceParser")
    DQR_DIR = os.path.join(tools_dir, "mips_dqr")
    WUPROF_DIR = os.path.join(tools_dir, "perf")
    MISSMAP_DIR = os.path.join(tools_dir, "csi_miss")


def run_trace_record_parsing(args):
    """Parsing flow for trace records"""
    trace_file = args.trace_files[0]
    if len(args.trace_files) > 1:
        print(
            "Only one file supported for trace records. Ignoring {}".format(
                args.trace_files[1:]
            )
        )
    parse_trace_record_dump(trace_file, args.output_dir)
    run_perf_parser(args)
    run_wuprof(args)


def parse_trace_record_dump(trace_file, outdir):
    """Converts trace record dumps into perfmon files"""
    perf_bin = os.path.join(PARSER_DIR, "parse_perf_record.py")
    perf_cmd = [perf_bin, "--output-dir", outdir, trace_file]

    print("--- Start parsing trace records with {}".format(perf_cmd))
    try:
        out = subprocess.check_output(perf_cmd)
        print(out.decode("utf-8"))
    except CalledProcessError as e:
        log_error("Failed to run parsing, " "output was %s\n" % e.output)
    print("--- End parsing trace records")


def run_pdtrace_parsing(args):
    """Parsing flow for pdtrace"""
    # Perf on silicon can use pdtrace as the mechanism by which traces are
    # packed and sent to memory.
    #
    # The sequence is:
    #    [ raw pdtrace data ] -> parse_pdtrace_dump -> [ dequeuer input (.rtd) ]
    #    [ dequeuer input (.rtd) ] -> MIPS dequeuer -> [ trace messages (.tm) ]
    #    [ trace messages (.tm) ] -> parse_dqr_tm -> [ perfmon (palladium perf) ]
    #
    for trace_file in args.trace_files:
        parse_pdtrace_dump(trace_file, args.output_dir)

    run_dequeuer(args.output_dir, args.funos_image)
    if args.parse_mode == "perf_pdt":
        run_perfmon_converter(args.output_dir)
        run_perf_parser(args)
        run_wuprof(args)
    elif args.parse_mode == "cache_miss":
        run_cache_miss_parser(args.output_dir)
        run_cache_missmapper(args.output_dir, args.funos_image)
    else:
        raise ValueError("unknown parse mode %s" % args.parse_mode)


def parse_pdtrace_dump(trace_file, outdir):
    """
    Calls the pdtrace dump parser which converts raw trace data
    for the specified cluster (a trace_cluster_xx file) into
    input for the MIPS dequeuer (a dqr_xx.rtd file).
    """
    parser_path = os.path.join(PARSER_DIR, "parse_pdt_dump.py")
    parser_cmd = [parser_path, trace_file, "--output-dir", outdir, "--format", "dqr"]
    print("--- Start pdtrace dump conversion with {}".format(parser_cmd))
    try:
        out = subprocess.check_output(parser_cmd)
        print(out.decode("utf-8"))
    except CalledProcessError as e:
        log_error("Failed to run parser on pdt dump: output was %s\n" % e.output)
        return
    print("--- End pdtrace dump conversion")


def run_dequeuer(trace_dir, funos_image):
    """
    Runs the MIPS dequeuer on all dqr_xx.rtd files in the specified
    trace directory. This creates multiple dqr_xx_y_trace.tm files,
    where xx is the cluster and y is the core.

    The .tm files contain trace message output from the dequeuer.
    """
    print("--- Start DQR decoding")
    # First make a temp directory to do our work. The dequeuer likes files
    # to be together in one directory, without any additional files that may
    # confuse it. It supposedly can handle "specifying absolute paths and
    # filenames to each of the required files", and "sets of files to use",
    # but I just get exceptions when using those options.
    tempdir = tempfile.mkdtemp("dqr", "tmp")

    # The dequeuer expects three files:
    # 1. The binary
    # 2. An RTD file, which contains the data dumps for a cluster.
    # 3. A TCF file, which contains configuration for a cluster.
    #
    # We will copy the binary once because it is large. Each iteration will
    # replace the RTD and TCF file with a new one.
    shutil.copyfile(funos_image, os.path.join(tempdir, "funos-f1"))

    for cluster in range(0, MAX_CLUSTERS):
        cluster_str = _get_cluster_id_str(cluster)

        # The configuration TCF files are different for PCs and CCs
        tcf_dir = os.path.join(MODULE_DIRECTORY, "trace_configs")
        tcf_file = "pc_trace.tcf" if cluster != CC_ID else "cc_trace.tcf"
        tcf_file = os.path.join(tcf_dir, tcf_file)
        shutil.copyfile(tcf_file, os.path.join(tempdir, "dqr.tcf"))

        rtd_file = "dqr_%s.rtd" % cluster_str
        rtd_file = os.path.join(trace_dir, rtd_file)
        if not os.path.exists(rtd_file):
            print("Skipping missing rtd file %s" % rtd_file)
            continue
        shutil.copyfile(rtd_file, os.path.join(tempdir, "dqr.rtd"))

        dqr_bin = os.path.join(DQR_DIR, "dq.sh")
        max_cores = MAX_CORES_PER_PC if cluster != CC_ID else MAX_CORES_PER_CC
        for core in range(0, max_cores):
            dqr_cmd = [dqr_bin, "-op", tempdir, "tm", "src", str(core), "all"]
            print("Running DQR for cluster {} core {}".format(cluster, core))
            try:
                output = subprocess.check_output(dqr_cmd)
            except CalledProcessError as e:
                log_error(
                    "Failed to dq cluster %d core %d, output "
                    "was %s\n" % (cluster, core, e.output)
                )

            out_file = "dqr_%s_%d_trace.tm" % (cluster_str, core)
            out_file = os.path.join(trace_dir, out_file)
            try:
                with open(out_file, "w") as fh:
                    fh.write(output.decode("utf-8"))
            except Exception as e:
                log_error(
                    "Failed to write out file %s "
                    "exception was %s\n" % (out_file, str(e))
                )

    shutil.rmtree(tempdir)
    print("--- End DQR decoding")


def _get_cluster_id_str(cluster_index):
    cluster_id = format(cluster_index, '02d')
    return cluster_id


def run_perfmon_converter(trace_dir):
    """
    Converts trace messages from the dequeuer (.tm files) into the perfmon
    format (which is what Palladium perf runs generate, and which is what
    perf visualization tools expect as input).
    """
    for cluster in range(0, MAX_CLUSTERS):
        cluster_str = _get_cluster_id_str(cluster)
        max_cores = MAX_CORES_PER_PC if cluster != CC_ID else MAX_CORES_PER_CC

        for core in range(0, max_cores):
            perf_bin = os.path.join(PARSER_DIR, "parse_dqr_tm.py")
            tm_file = "dqr_%s_%d_trace.tm" % (cluster_str, core)
            tm_file = os.path.join(trace_dir, tm_file)
            if not os.path.exists(tm_file):
                print("Skipping missing tm file %s" % tm_file)
                continue

            perf_cmd = [
                perf_bin,
                tm_file,
                "--cluster",
                str(cluster),
                "--core",
                str(core),
                "--output-dir",
                trace_dir,
            ]

            print("Running TM converter for cluster {} core {}".format(cluster, core))
            try:
                subprocess.check_output(perf_cmd)
            except CalledProcessError as e:
                log_error(
                    "Failed to run perf on cluster %d core %d, "
                    "output was %s\n" % (cluster, core, e.output)
                )


def run_perf_parser(args):
    """
    Runs the perf parser on the perfmon files.
    """
    parser = os.path.join(MODULE_DIRECTORY, "perf_parser.py")
    parse_cmd = [parser, args.output_dir, args.funos_image]
    if args.funos_log:
        parse_cmd.extend(["--funos-log", args.funos_log])

    print("--- Start perfmon parsing with {}".format(parse_cmd))
    try:
        out = subprocess.check_output(parse_cmd)
        print(out.decode("utf-8"))
    except CalledProcessError as e:
        log_fatal("Failed to run perf parser, " "output was %s\n" % e.output)
    print("--- End perfmon parsing")


def run_wuprof(args):
    """Runs wuprof post-processing"""
    workdir = args.output_dir
    wuprof_script = os.path.join(WUPROF_DIR, "wuprof.py")
    perf_data = os.path.join(workdir, "perf_table.txt")
    out_file = os.path.join(workdir, "wuprof.html")

    wuprof_cmd = [wuprof_script, "wuvp", perf_data, "-o", out_file]
    if args.funos_log:
        wuprof_cmd.extend(["-u", args.funos_log])

    print("--- Start wuprof with {}".format(wuprof_cmd))
    try:
        out = subprocess.check_output(wuprof_cmd)
        print(out.decode("utf-8"))
    except CalledProcessError as e:
        log_error("Failed to run wuprof processing, " "output was %s\n" % e.output)
    print("--- End wuprof")


def run_cache_miss_parser(trace_dir):
    """
    Converts trace messages from the dequeuer (.tm files) into cache miss
    files.
    """
    for cluster in range(0, MAX_CLUSTERS):
        cluster_str = _get_cluster_id_str(cluster)
        max_cores = MAX_CORES_PER_PC if cluster != CC_ID else MAX_CORES_PER_CC

        for core in range(0, max_cores):
            cache_miss_bin = os.path.join(PARSER_DIR, "parse_dqr_tm.py")
            tm_file = "dqr_%s_%d_trace.tm" % (cluster_str, core)
            tm_file = os.path.join(trace_dir, tm_file)
            if not os.path.exists(tm_file):
                print("Skipping missing tm file %s" % tm_file)
                continue

            cm_cmd = [
                cache_miss_bin,
                tm_file,
                "--cluster",
                str(cluster),
                "--core",
                str(core),
                "--parse-mode",
                "cache_miss",
                "--output-dir",
                trace_dir,
            ]

            try:
                subprocess.check_output(cm_cmd)
            except CalledProcessError as e:
                log_error(
                    "Failed to run cache miss on cluster %d core %d, "
                    "output was %s\n" % (cluster, core, e.output)
                )


def run_cache_missmapper(out_dir, funos_image):
    """Runs the tool that turns raw cache miss data into spiffy HTML"""
    missmap_bin = os.path.join(MISSMAP_DIR, "missmap-pipeline.py")
    missmap_cmd = [missmap_bin, "-b", funos_image]

    # missmap needs to run in the directory where the raw files live
    work_dir = out_dir
    proc = subprocess.Popen(
        args=missmap_cmd, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    if proc.returncode != 0:
        log_error(
            "Failed to run missmap: "
            "error code %d, output %s\n" % (proc.returncode, out)
        )
        return


def clean_up_intermediate_files(trace_dumps_dir):
    """Removes intermediate files generated by this script."""

    # Clean up all RTD files (dequeuer input)
    rtd_files = glob.glob("%s/*.rtd" % trace_dumps_dir)
    for f in rtd_files:
        os.remove(f)

    # Clean up all TM files (dequeuer output)
    tm_files = glob.glob("%s/*trace.tm" % trace_dumps_dir)
    for f in tm_files:
        os.remove(f)


def log_error(msg):
    """Non-fatal error: reported at end"""
    sys.stderr.write(msg)


def log_fatal(msg):
    """Fatal error: report immediately and exit"""
    sys.stderr.write(msg)
    sys.exit(1)


if __name__ == "__main__":
    main()
