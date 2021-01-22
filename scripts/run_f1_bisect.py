#!/usr/bin/env python3

"""
Run an automated git bisect using the Fun-on-Demand infrastructure.

This leverages the run_f1.py script, so that script must be available (path can
be provided as an argument), and it must be setup to properly transfer the
binary to Fun-on-Demand servers. Check the wiki here:

http://confluence.fungible.local/display/SW/Fun-on-demand%3A+Running+FunOS+on+Palladium+or+FS1600

To use this, do something like:

git bisect reset
git bisect bad <rev>
git bisect good <rev>
git bisect run /path/to/run_f1_bisect.py --description "test" "make -j24 MACHINE=f1 SIGN=1" "tcp_pkt_gen_perf_f1.params" "./build/funos-f1.signed"
"""

import subprocess
import argparse
import traceback
import shlex
import sys
import os


def get_sha():
    """
    Return the SHA for the checked out commit.
    """

    cmd = shlex.split("git rev-parse --short HEAD")

    return subprocess.check_output(cmd).decode().strip()


def build(args):
    """
    Using the build command provided in the buildcmd argument, try to build
    FunOS.

    If the build fails, a CalledProcessError will be raised. We can use this to
    return 125 which indicates to Git that it should skip the commit.

    If we encounter some other exception, return > 127, which will indicate to
    Git that it should abort the bisect.
    """

    cmd = shlex.split(args.buildcmd)

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        sys.stderr.write("Skipping commit that cannot be built\n")

        # Special code telling Git to skip this commit
        sys.exit(125)
    except:
        sys.stderr.write("Encountered unexpected exception, aborting\n")
        sys.stderr.write(traceback.format_exc())

        # Return values > 127 indicate to Git to abort the bisect
        sys.exit(128)


def main(args):
    sha = get_sha()

    print(f"Checking SHA {sha}")

    build(args)

    run_f1_path = os.path.expandvars(args.run_f1_path)
    params_path = os.path.expandvars(args.params)
    binary_path = os.path.expandvars(args.binary)
    description = f"auto bisect sha1={sha} {args.description}"
    cmd = f'{run_f1_path} --wait-until-complete --note "{description}" --params {params_path} {binary_path}'

    for _ in range(args.times):
        try:
            print(f"Submission command is {cmd}")
            subprocess.check_call(shlex.split(cmd))
        except subprocess.CalledProcessError:
            sys.stderr.write("Fun-on-demand job exited with non-zero status\n")
            sys.exit(1)


def handle_args():
    parser = argparse.ArgumentParser(description="Bisect FunOS using run_f1.py")

    parser.add_argument(
        "--description",
        help="Add a description to the fun-on-demand job",
        default="",
    )
    parser.add_argument(
        "--run-f1-path",
        help="Path to run_f1.py",
        default="$WORKSPACE/PalladiumOnDemand/run_f1/run_f1.py",
    )
    parser.add_argument(
        "--times", help="Number of times to run job", type=int, default=3
    )
    parser.add_argument("buildcmd", help="Build command for FunOS")
    parser.add_argument("params", help="Params file for run_f1.py")
    parser.add_argument("binary", help="Path to built FunOS binary")

    return parser.parse_args()


if __name__ == "__main__":
    args = handle_args()
    main(args)
