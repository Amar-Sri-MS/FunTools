#!/usr/bin/env python3

import argparse
import sys

from itertools import zip_longest

# This script is used to pre-process the SBUS FW files
# for both HU and HBM and generate the binary format
# that will be loaded directly.
#
# 16nm Details:
# The SBUS FW files are defined as follows: Each line
# is an ascii representation of a 10 bit value. The
# script combines the lines three at a time, putting
# them in [29:20], [19:10], and [9:0], and the number
# of words in [31:30]. Since we don't want the SBP
# code to waste time with this parsing and combining,
# this script handles the work.
#
# 07nm Details:
# The SBUS FW files are defined as follows: Each line
# is an ascii representation of a 12 bit value. The
# script combines eight lines at a time to form three
# words of four bytes each.

def grouper(iterable, n, fillvalue=None):
	args = [iter(iterable)] * n
	return zip_longest(*args, fillvalue=fillvalue)

def combine_16nm(w0, w1, w2, wcnt):

	w0_v = int(w0, 16)
	w1_v = 0
	w2_v = 0

	if wcnt > 1:
		w1_v = int(w1, 16)

	if wcnt > 2:
		w2_v = int(w2, 16)

	fullword = ((wcnt << 30) | (w2_v << 20) | (w1_v << 10) | w0_v)

	return fullword

def combine_07nm(w0, w1, w2, w3, w4, w5, w6, w7, wcnt):

	w0_v = int(w0, 16)
	w1_v = w2_v = w3_v = w4_v = w5_v = w6_v = w7_v = 0

	if wcnt > 1:
		w1_v = int(w1, 16)

	if wcnt > 2:
		w2_v = int(w2, 16)

	if wcnt > 3:
		w3_v = int(w3, 16)

	if wcnt > 4:
		w4_v = int(w4, 16)

	if wcnt > 5:
		w5_v = int(w5, 16)

	if wcnt > 6:
		w6_v = int(w6, 16)

	if wcnt > 7:
		w7_v = int(w7, 16)


	fullword1 = (((w2_v & 0xff) << 24) | (w1_v << 12) | w0_v)
	fullword2 = (((w5_v & 0xf) << 28) | (w4_v << 16) | (w3_v << 4) | ((w2_v >> 8) & 0xf))
	fullword3 = ((w7_v << 20) | (w6_v << 8) | ((w5_v >> 4) & 0xff))

	return [fullword1, fullword2, fullword3]

# Already prep as little endian
def bin_array(val, little_endian):

	ba = [val>>24, (val>>16) & 0xff, (val>>8) & 0xff, val & 0xff]

	if little_endian:
		ba.reverse()

	return ba

def rom_convert_16nm(infile, outfile, little_endian):

	print("Beginning 16nm rom_convert (%s)" % infile)

	fout = open(outfile, 'wb')

	iteration = 0

	with open(infile) as f:
		for lines in grouper(f, 3, ''):

			wcnt = len([v for v in lines if len(v) != 0])

			tot_w = combine_16nm(lines[0], lines[1], lines[2], wcnt)

			tot_w_arr = bin_array(tot_w, little_endian)

			#print "sbus_fw[%s] = %s" % (iteration, hex(tot_w))
			#print ([hex(x) for x in tot_w_arr])
			iteration = iteration + 1

			fout.write(bytearray(tot_w_arr))

	fout.close()

	print("16nm Rom conversion completed")

def rom_convert_07nm(infile, outfile, little_endian):

	print("Beginning 07nm rom_convert (%s)" % infile)

	fout = open(outfile, 'wb')

	iteration = 0

	with open(infile) as f:
		for lines in grouper(f, 8, ''):
			wcnt = len([v for v in lines if len(v) != 0])
			tot_w_list = combine_07nm(lines[0], lines[1], lines[2], lines[3], lines[4], lines[5], lines[6], lines[7], wcnt)

			for word in tot_w_list:
				tot_w_arr = bin_array(word, little_endian)
				fout.write(bytearray(tot_w_arr))
				iteration += 1

	fout.close()

	print("07nm Rom conversion completed")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--BE', dest='little_endian', action='store_false', help='Generate big-endian output')
	group.add_argument('--LE', dest='little_endian', action='store_true', help='Generate little-endian output')

	parser.add_argument('--format', choices=['07nm', '16nm'], required=True,
                        help='Generate output on 07nm tech IMEM format or 16nm tech IMEM format')
	parser.add_argument('input', help='Input file name')
	parser.add_argument('output', help='Output file name')

	args = parser.parse_args()

	if args.format == '07nm':
		rom_convert_07nm(args.input, args.output, args.little_endian)
	elif args.format == '16nm':
		rom_convert_16nm(args.input, args.output, args.little_endian)
	else:
		print("Invalid format selected.")
