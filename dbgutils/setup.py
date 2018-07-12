#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'dbgutils',
    version = '0.1.0',
    author = 'Nag Ponugoti(nag.ponugoti@fungible.com)',
    description = 'csr debug utilities',
    scripts = ['dbgsh'],
    packages = find_packages(),
    include_package_data=True,
    install_requires = [
        'aardvark_py',
        'argparse',
        'jsocket',
        'logging',
	'cmd2',
	'argcomplete'
    ],
)
