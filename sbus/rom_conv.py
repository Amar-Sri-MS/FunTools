#!/usr/bin/env python3

import argparse
import sys

from itertools import zip_longest

# This script is used to pre-process the SBUS FW files
# for both HU and HBM and generate the binary format
# that will be loaded directly.
#
# Details:
# The SBUS FW files are defined as follows: Each line
# is an ascii representation of a 10 bit value. The
# script combines the lines three at a time, putting
# them in [29:20], [19:10], and [9:0], and the number
# of words in [31:30]. Since we don't want the SBP
# code to waste time with this parsing and combining,
# this script handles the work.

def grouper(iterable, n, fillvalue=None):
	args = [iter(iterable)] * n
	return zip_longest(*args, fillvalue=fillvalue)

def combine(w0, w1, w2, wcnt):

	w0_v = int(w0, 16)
	w1_v = 0
	w2_v = 0

	if wcnt > 1:
		w1_v = int(w1, 16)

	if wcnt > 2:
		w2_v = int(w2, 16)

	fullword = ((wcnt << 30) | (w2_v << 20) | (w1_v << 10) | w0_v)

	return fullword

# Already prep as little endian
def bin_array(val, little_endian):

	ba = [val>>24, (val>>16) & 0xff, (val>>8) & 0xff, val & 0xff]

	if little_endian:
		ba.reverse()

	return ba

def rom_convert(infile, outfile, little_endian):

	print("Beginning rom_convert (%s)" % infile)

	fout = open(outfile, 'wb')

	iteration = 0

	with open(infile) as f:
		for lines in grouper(f, 3, ''):

			wcnt = len([v for v in lines if len(v) != 0])

			tot_w = combine(lines[0], lines[1], lines[2], wcnt)

			tot_w_arr = bin_array(tot_w, little_endian)

			#print "sbus_fw[%s] = %s" % (iteration, hex(tot_w))
			#print ([hex(x) for x in tot_w_arr])
			iteration = iteration + 1

			fout.write(bytearray(tot_w_arr))

	fout.close()

	print("Rom conversion completed")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--BE', dest='little_endian', action='store_false', help='Generate big-endian output')
	group.add_argument('--LE', dest='little_endian', action='store_true', help='Generate little-endian output')

	parser.add_argument('input', help='Input file name')
	parser.add_argument('output', help='Output file name')

	args = parser.parse_args()

	rom_convert(args.input, args.output, args.little_endian)
