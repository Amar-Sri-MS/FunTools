#!/usr/bin/env python2.7

# Responds to any message that is received
# on stdin with the same message in CAPS on stdout

import sys
sys.stdout.write(sys.stdin.readline().strip().upper() + '\n')

