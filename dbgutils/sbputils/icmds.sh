#! /bin/bash

ARGS=$*

VIRTUALENV=/home/pmanjrekar/py2venv
pushd $(pwd) && cd $VIRTUALENV && source bin/activate && popd

set -x
python icli.py $ARGS