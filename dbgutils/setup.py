#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'dbgutils',
    version = '0.3.0',
    author = 'Nag Ponugoti(nag.ponugoti@fungible.com)',
    description = 'python debug utilities for F1',
    scripts = ['dbgsh'],
    packages = find_packages(),
    package_data = {'probeutils': ["probeutils/dut.cfg"]},
    include_package_data=True,
    install_requires = [
        'aardvark_py',
        'argparse',
        'jsocket',
        'logging',
        'cmd2==0.8.8',
        'argcomplete',
        'pyusb',
        'urllib3'
    ],
)
