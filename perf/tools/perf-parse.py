#!/usr/bin/python2.7
import os
import re
import sys
import urllib.request, urllib.error, urllib.parse
import copy
import collections
import shutil
import pickle
import subprocess

def job_id_from_url(url):
    sep = url.rfind("/")
    assert sep > 0
    job_id = url[sep+1:]
    assert re.match(r"^\d+$", job_id), job_id
    return job_id

def download_files(url):
    # Find out local job directory.
    assert url.startswith("http")
    job_id = job_id_from_url(url)
    local_job_dir = "data/jobs/" + job_id

    if not os.path.exists(local_job_dir):
        os.makedirs(local_job_dir)

    print("Downloading files")

    # html
    html_path = os.path.join(local_job_dir, "html")
    resp = urllib.request.urlopen(url)
    html_data = resp.read()
    assert html_data
    m = re.search(r"<td>Job State</td><td>\"(?P<job_state>\w+)\"</td>", html_data)
    assert m, "Could not extract job_state [%r]" % html_data

    # Find out job directory on the server.
    m = re.search(r"<td>(?P<remote_job_dir>/project[a-zA-Z0-9-/]+-\d\d)</td>", html_data)
    assert m, html_data
    remote_job_dir = m.group("remote_job_dir")

    # Find out config type
    m = re.search(r"/rdp/(?P<config_type>\w+)/cdn_uartout0.txt", html_data)
    assert m, "Could not locate config type [%r]" % html_data
    config_type = m.group("config_type")

    # Copy funos image.
    funos_path = local_job_dir + "/funos-f1-emu"
    if not os.path.exists(funos_path):
        try:
            subprocess.check_output("scp server11:%s/funos-f1-emu.gz %s/" %
                                    (remote_job_dir, local_job_dir),
                                    stderr=subprocess.STDOUT, shell=True)
            subprocess.check_output("gunzip %s/funos-f1-emu.gz" % local_job_dir,
                                    stderr=subprocess.STDOUT, shell=True)
        except Exception as e:
            subprocess.check_output("scp -C server11:%s/funos-f1-emu %s/" %
                                    (remote_job_dir, local_job_dir), shell=True)

    # Copy files.
    config_type_to_perfmon_list = {
        "Compute2": {
            "cut_perfmon.txt":      ("odp", "rdp/Compute2"),
            "put_perfmon.txt":      ("odp", "rdp/Compute2"),
            "cut_mips_uartout.txt": ("odp", "rdp/Compute2"),
            "put_mips_uartout.txt": ("odp", "rdp/Compute2"),
            "cdn_uartout0.txt":     ("odp", "rdp/Compute2"),
        },
        "Storage1": {
            "put_perfmon.txt":  ("odp", "rdp/Storage1"),
            "cdn_uartout0.txt": ("odp", "rdp/Storage1"),
        },
        "Storage2": {
            "cut_perfmon.txt":  ("odp", "rdp/Storage2"),
            "put_perfmon.txt":  ("odp", "rdp/Storage2"),
            "cdn_uartout0.txt": ("odp", "rdp/Storage2"),
        },
    }

    for name, remote_paths in config_type_to_perfmon_list[config_type].items():
        local_path = local_job_dir + "/" + name
        errors = []
        for remote_path in remote_paths:
            try:
                out = subprocess.check_output("scp -C server11:%s/%s/%s %s" %
                                (remote_job_dir, remote_path, name, local_path),
                                stderr=subprocess.STDOUT, shell=True)
                break
            except Exception as e:
                errors.append(e)
        else:
            raise Exception("Could not copy %s, errors=%s" % (name, errors))

    # Merge perfmon files.
    perfmon_path = local_job_dir + "/perfmon.txt"
    if os.path.exists(perfmon_path):
        os.remove(perfmon_path)

    for name in os.listdir(local_job_dir):
        if "_perfmon" in name:
            subprocess.check_output("cat %s/%s >> %s" % (local_job_dir, name, perfmon_path), shell=True)

    # Merge uart files.
    uart_path = local_job_dir + "/uart.txt"
    if os.path.exists(uart_path):
        os.remove(uart_path)

    for name in os.listdir(local_job_dir):
        if "_uartout" in name:
            subprocess.check_output("cat %s/%s >> %s" % (local_job_dir, name, uart_path), shell=True)

    return local_job_dir

def get_uart_data(job_dir):
    with open(os.path.join(job_dir, "uart.txt"), "r") as f:
        return (f.read(), os.fstat(f.fileno()).st_mtime)

def get_wu_list(job_dir, uart_timestamp):

    wu_path = job_dir + "/wu.list"
    if (os.path.exists(wu_path)
        and (os.stat(wu_path).st_mtime > uart_timestamp)):
        print("Using cached WU list")
        with open(wu_path, "r") as f:
            return f.read().split()

    print("Generating WU list")

    if os.uname()[0] == "Darwin":
        gdb_path = "/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb"
    else:
        gdb_path = "/opt/cross/mips64/bin/mips64-unknown-elf-gdb"
    data = subprocess.check_output("%s "
        "-ex 'set print elements 100000' "
        "-ex 'set print repeats 0' "
        "-ex 'set print array on' "
        "-ex 'p wu_handlers_default' -batch "
        "%s/funos-f1-emu" % (gdb_path, job_dir), shell=True)
    wu_list = []
    for line in data.split("\n"):
        if not line:
            continue
        m = re.search(r"<(?P<wu>.+?)>", line)
        assert m, repr(line)
        wu = m.group("wu")
        assert " " not in wu
        wu_list.append(wu)

    with open(wu_path, "w") as f:
        f.write("\n".join(wu_list))
    return wu_list

LINES_PER_SAMPLE = 8
PERF_SAMPLE_FMT = "%s  %16x  %8x  %8x  %8x  %8x  %8x %16x %s"
PERF_HEADER_FMT = "%s  %16s  %8s  %8s  %8s  %8s  %8s %16s %s"
class PerfSample(object):
    def __init__(self, ccv, wu_list, *args):
        assert len(args) == LINES_PER_SAMPLE
        self.vp = ccv
        self.timestamp = (args[0] >> 8)
        self.cp0_count = (args[1] >> 8)
        self.perf_cnt0 = (args[2] >> 8)
        self.perf_cnt1 = (args[3] >> 8)
        self.perf_cnt2 = (args[4] >> 8)
        self.perf_cnt3 = (args[5] >> 8)
        wuid = (args[6] >> 8) & 0xffff
        assert wuid < len(wu_list), (wuid, len(wu_list), [hex(a) for a in args])
        self.wu = wu_list[wuid]
        self.arg0 = ((args[6] >> 24) & 0xff) << 56
        self.arg0 |= (args[7] >> 8)
        assert LINES_PER_SAMPLE == 8

    def header_str(self):
        return PERF_HEADER_FMT % ("ccv", "timestamp", "cp0_count",
                                  "perf0", "perf1", "perf2", "perf3",
                                  "arg0", "wu")
    def __str__(self):
        return PERF_SAMPLE_FMT % (
            self.vp,
            self.timestamp,
            self.cp0_count,
            self.perf_cnt0,
            self.perf_cnt1,
            self.perf_cnt2,
            self.perf_cnt3,
            self.arg0,
            self.wu,
            )

def vp2ccv(vp):
    return "%s.%s.%s" % (vp/24, (vp%24)/4, (vp%24)%4)

def parse_perfmon_data(job_dir, wu_list):
    # Group values by vp.
    vp_to_values = collections.defaultdict(list)
    count = 0
    path = job_dir + "/perfmon.txt"
    with open(path, "r") as f:
        for line in f:
            count = count + 1
            value = int(line, 16)
            vp = value & 0xff
            assert vp < 9*24
            vp_to_values[vp].append(value)
    assert count % LINES_PER_SAMPLE == 0

    samples = []
    for vp in list(vp_to_values.keys()):
        values = vp_to_values[vp]
        del vp_to_values[vp]
        assert len(values) % LINES_PER_SAMPLE == 0, len(values)
        ccv = vp2ccv(vp)
        for i in range(0, len(values), LINES_PER_SAMPLE):
            sample = PerfSample(ccv, wu_list, *values[i:i+LINES_PER_SAMPLE]);
            if sample.cp0_count == 0xacce00000000:
                print("Skipping custom data:", sample)
                continue
            #print sample
            samples.append(sample)
            if i > 0:
                assert samples[-2].timestamp < samples[-1].timestamp, "\n%s\n%s" % (samples[-2], samples[-1])
    return samples

def table_from_samples(samples, event_types):
    rows = []
    rows.append((
        "timestamp",
        "vp",
        "wu",
        "cycles",
        event_types[0],
        event_types[1],
        event_types[2],
        event_types[3],
        "arg0",
        ))
    for s in samples:
        rows.append((
            s.timestamp,
            s.vp,
            s.wu,
            s.cp0_count*2,
            s.perf_cnt0,
            s.perf_cnt1,
            s.perf_cnt2,
            s.perf_cnt3,
            s.arg0,
            ))
    return rows

def parse_event_types(uart_data):
    lines = uart_data.split("\n")
    i = 0
    while (i < len(lines) and
           not lines[i].endswith("Perf interposer is collecting counters for events:\r")):
        i += 1
    assert i != len(lines), "Could not find event types [%r]" % uart_data
    i += 1
    event_types = [l.split()[-1] for l in lines[i:i+4]]
    assert len(event_types) == 4
    return event_types

def parse_wustack_range(data, debug_build):
    m = re.search(r"\"wustack\s+(?P<start>0x[0-9a-fA-F]{16})\s+(?P<end>0x[0-9a-fA-F]{16})\s+\d+\s+[KM]B\"", data)
    assert m
    start, end = int(m.group("start"), 16), int(m.group("end"), 16)
    if debug_build:
        def xkphys_to_xkseg(va):
            assert va >> 48 == 0xa800
            assert (va & 4095) == 0
            va &= ((1 << 48) - 1)
            va *= 2
            va |= (0xc000 << 48)
            return va
        start, end = xkphys_to_xkseg(start), xkphys_to_xkseg(end)
    return start, end

class PerfData(object):
    pass

def main(url):
    if (url.startswith("http")):
        job_dir = download_files(url)
    else:
        # accept a local path as pre-downloaded data
        job_dir = url
        print("Using local job direcotry '%s'" % job_dir)
    (uart_data, timestamp) = get_uart_data(job_dir)
    wu_list = get_wu_list(job_dir, timestamp)
    event_types = parse_event_types(uart_data)
    samples = parse_perfmon_data(job_dir, wu_list)
    debug_build = "installing interposer 'validate'" in uart_data
    wustack_start, wustack_end = parse_wustack_range(uart_data, debug_build)

    if debug_build:
        print()
        print("WARNING!!! This appears to be a debug build, which is not a good candidate for perf testing")
        print()

    with open(os.path.join(job_dir, "perf.data"), "w") as f:
        pd = PerfData()
        pd.event_types = event_types
        pd.wustack_start = wustack_start
        pd.wustack_end = wustack_end
        pd.debug_build = debug_build
        pd.rows = table_from_samples(samples, event_types)
        pickle.dump(pd, f)
    print("Data imported successfully")

    # for manual validation purposes, make a simple text version
    with open(os.path.join(job_dir, "samples.txt"), "w") as f:
        f.write("%s\n" % samples[0].header_str())
        for sample in samples:
            f.write("%s\n" % sample)
    print("Samples saved to samples.txt")


if __name__ == '__main__':
    main(*sys.argv[1:])
