#!/usr/bin/python

import json
import os
import platform
import re
import subprocess


# File containing information about the thread-local region in FunOS
IN_JSON_FILE = "thread-local.js"

# Where we dump the results
OUT_FILE = "thread-local-ident.js"


def dump_thread_locals(funos_binary, tls_start, stride):
    """ Writes the thread local variable information to a file """
    max_vps = 9 * 6 * 4
    result = _identify_thread_locals(funos_binary, tls_start, stride, max_vps)

    s = json.dumps(result)
    with open(OUT_FILE, "w") as f:
        f.write(s)


def _identify_thread_locals(funos_binary, tls_start, stride, num_vps):
    objdump = _objdump_binary()

    # This is pretty much:
    # objdump -t <binary> | grep tdata
    objdump_proc = subprocess.Popen([objdump, "-t", funos_binary],
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
    grep_proc = subprocess.Popen(["grep", "tdata"],
                                 stdin=objdump_proc.stdout,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)

    objdump_proc.stdout.close()
    out, err = grep_proc.communicate()

    tdata_lines = out.splitlines()
    per_vp_vars = []

    for l in tdata_lines:
        parts = l.split()

        # ignore the .tdata section entry
        if len(parts) == 6 and parts[5] == ".tdata":
            continue

        offset = int(parts[0], 16)
        size = int(parts[3], 16)
        name = parts[4]

        per_vp_vars.append((name, offset, size))

    # sort by offset
    per_vp_vars.sort(key=lambda v: v[1])

    result = []
    for vpnum in range(num_vps):
        base = tls_start + (vpnum * stride)

        for v in per_vp_vars:
            name = v[0]
            offset = v[1] + base
            size = v[2]
            var = (name, offset, size, vpnum)
            result.append(var)

    return result


def _objdump_binary():
    current_os = platform.system()
    if current_os == "Darwin":
        return "/Users/Shared/cross/mips64/bin/mips64-unknown-elf-objdump"
    else:
        return "/opt/cross/mips64/bin/mips64-unknown-elf-objdump"


def get_thread_local_info(regions, log_file, json_file):
    """ Return the base and stride of the thread local region """
    stride = None

    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            js = json.load(f)
            stride = js["tls_stride"]
    elif os.path.exists(log_file):
        with open(log_file, "r") as f:
            stride = _scan_log_for_stride(f)

    for r in regions:
        name = r[2]
        if name == "thread-local":
            return r[0], stride
    return None, stride


# Regex for the thread-local log line
STRIDE_RE = r".*thread-local base: 0x[0-9a-f]+, thread-local stride: 0x([0-9a-f]+).*"

def _scan_log_for_stride(f):
    for line in f:
        m = re.match(STRIDE_RE, line)
        if m:
            return int(m.group(1), 16)
    return None


def main():
    """ sanity test """
    dump_thread_locals("funos-f1", 0xa800000000000000, 0xc0, 216);


if __name__ == "__main__":
    main()
