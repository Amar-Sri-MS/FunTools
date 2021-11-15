#!/bin/bash
#
# tester_cron.sh: Run automated tests for Log Analyzer ingestion.
#
# This script is a simple wrapper so cron doesn't need to know how to
# set up the Python environment.
#

set -e  # Exit on first error

program_dir=$(dirname "$0")

source "../.venv/bin/activate"

"${program_dir}/qa_tester.py"