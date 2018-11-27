#!/usr/bin/env python

# cfg_gen.py
# The config generator is intended to simplify configuration file maintenance,
# now that we are getting more files. The files are all stored in a flat
# layout (configs/*.cfg) and are combined into one out/default.cfg. This is
# subject to change as requirements for different configurations grow.
#
# The input files are allowed to make two side-steps from the standard JSON
# specification:
#	- Allow comments
#	- Allow hex values
#
# Both are intended to improve readability of the files, and leverage our
# own jsonutil (which has a lenient parser) to do the initial parsing.
#
# Created by Michael Boksanyi, August 10 2017
# Modified by Fred stanley, Nov 9 2017
# Copyright Fungible Inc. 2017

import glob, os, sys, re, datetime
import getopt, platform, tempfile

from itertools import chain
import json
from string import Template
import re

