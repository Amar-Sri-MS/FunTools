#!/usr/bin/env python3

"""Usage: run_dharma.py [-h] [-c=<N>] [-p=<prefix>]

Run fuzzy testing with dharma.
Arguments:
  -c=N number of iteration to run, default 1000
  -p=prefix prefix to be added to each file
  -h --help
"""

from docopt import docopt
import subprocess
import os
import re

if __name__ == '__main__':
  arguments = docopt(__doc__)
  count = 1000 if arguments['-c'] is None else int(arguments['-c'])
  prefix = "" if arguments['-p'] is None else arguments['-p']
  for i in range(0, count):
    json_text = prefix + str(i) + ".json"
    json_bin = prefix + str(i) + ".bin"
    subprocess.check_call('dharma -grammars fuzz/json.dg > {0} 2>/dev/null'.format(json_text), shell=True)
    out = subprocess.check_output('./jsonutil -i {0} -O {1}'.format(json_text, json_bin), shell=True)
    out = re.sub(r"\*\*\* Duplicate key in json: \'.*?\'", '', out).strip()
    if out == "":
      os.unlink(json_text)
      os.unlink(json_bin)
    else:
      with open(prefix + str(i) + '.txt', 'w') as f:
        f.write(out)
        print("Saved case " + str(i))

