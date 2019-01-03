#!/usr/bin/python

from setuptools import setup, find_packages
import os.path
from distutils import dir_util
from os.path import expanduser
import shutil

from setuptools.command.install import install

class JtagExtCommands(install):
    def run(self):
        print('Copying jtag Codescape command scripts ....')
        destination_path = os.path.join(expanduser("~"), "imgtec/console_scripts")
        shutil.rmtree(destination_path, ignore_errors=True)
        dir_util.copy_tree("jtagutils", destination_path, update=1, preserve_mode=0)
        install.run(self)

setup(
    name = 'dbgutils',
    version = '0.3.0',
    author = 'Nag Ponugoti(nag.ponugoti@fungible.com)',
    description = 'python debug utilities for F1',
    scripts = ['dbgsh'],
    packages = find_packages(),
    package_data = {'probeutils': ["probeutils/dut.cfg"]},
    include_package_data=True,
    cmdclass={'install': JtagExtCommands},
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
