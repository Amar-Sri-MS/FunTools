#! /usr/bin/env python3

##############################################################################
#  trng_data_summary.py
#
#  Generate a CSV file for Excel summarising the results obtained
#  with trng.py.
#
#  python3 trng_data_summary.py <directory_with_json_files> > <csv file>
#
#  Copyright (c) 2021. Fungible, inc. All Rights Reserved.
#
##############################################################################


import os
import sys
import json
import glob

class autofill_list(list):

    def __init__(self, filler=None):
        self.filler = filler
        list.__init__(self)

    def __setitem__(self, index, value):
        size = len(self)
        if index >= size:
            self.extend(self.filler for _ in range(size, index + 1))
        list.__setitem__(self, index, value)

    def set_filler(self, filler):
        self.filler = filler


data_summary = {}  # disabled_rings -> array of pr indexed by clock divider


# collect all the files
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = "./"

glob_path = os.path.join(path, "trng_data*")

for f in glob.iglob(glob_path):
    with open(f, 'r') as fp:
        data = json.load(fp)

    dis_rings = hex(data['disabled_rings'])[2:]
    clock_div = data['clock_divider']
    pr = data["pr"]

    values_arr = data_summary.get(dis_rings)
    if not values_arr:
        values_arr = autofill_list("")
        data_summary[dis_rings] = values_arr

    values_arr[clock_div] = pr

# output CSV
for k in sorted(data_summary.keys(), reverse=True):
    print('%s, ' % k, end='')
    values = data_summary[k]
    for v in values:
        print('%s, ' % str(v), end='')
    print()
