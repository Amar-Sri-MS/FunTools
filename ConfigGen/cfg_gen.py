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

	json.dump(full_cfg, fout)

	fout.close()

if __name__ == "__main__":

	generate_config()
