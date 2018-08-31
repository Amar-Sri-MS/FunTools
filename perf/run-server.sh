#!/bin/bash
set -ex

if [[ -x /usr/local/bin/python ]]; then
    /usr/local/bin/python ./controller.py
else
    /usr/bin/python ./controller.py
fi
