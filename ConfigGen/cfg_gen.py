#!/usr/bin/python

import glob, os, sys

import json

def generate_config():

	full_cfg = {}

	for cfg in glob.glob("configs/*.cfg"):
		
		os.system('../jsonutil/jsonutil -i %s -o %s.tmp' % (cfg, cfg));

		f = open("%s.tmp" % cfg, 'r')
		cfg_j = json.load(f)
		f.close()
		os.system('rm %s.tmp' % cfg)

		full_cfg.update(cfg_j)

	fout = open("out/default.cfg", 'w')

	# indent=4 does pretty printing for us
	json.dump(full_cfg, fout, indent=4)

	fout.close()

	# XXX next step: output bjson


def build_jsonutil():

	startdir = os.getcwd()

	os.chdir(os.path.join('..', 'jsonutil'))

	if os.path.isfile('jsonutil'):
		os.chdir(startdir)
		return True

	rc = os.system('make clean; make')
	if rc != 0:
		os.chdir(startdir)
		return False

	os.chdir(startdir)

	return True



if __name__ == "__main__":

	# We are using jsonutil because the parser is more lenient than
	# a classical json parser, allowing us to write more readable
	# configurations thanks to comments and hex values
	rc = build_jsonutil()
	if rc == False:
		print 'Failed to build jsonutil'
		sys.exit(1)

	rc = generate_config()
	if rc == False:
		print 'Failed to generate config'
		sys.exit(1)
