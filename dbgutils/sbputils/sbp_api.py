import click

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from sbp_structs import *

import sys
import re

@click.group()
def sbp_api():
	pass

@sbp_api.command()
@click.option('--filename', required=True, help='decode a binary blob as per OTP hexbyte filename')
def otp_decode(filename):
	""" read otp binary or hex file and display the internal fields """
	with open(filename) as f:
		B = f.read()
	f.close()
	BLOB = wordpack(' '.join(re.findall(r'........', B)))
	#hexdump(BLOB)
	click.echo(otp(BLOB).show())

if __name__ == '__main__':
	sbp_api()
