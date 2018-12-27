#!/usr/bin/python

from setuptools import setup, find_packages
import os.path
from distutils import dir_util
from os.path import expanduser
import shutil

from setuptools.command.install import install
from sys import platform as _platform

class JtagExtCommands(install):
    def run(self):
        print _platform
        if _platform == "linux" or _platform == "linux2":
            print('Copying jtag Codescape command scripts(platform:{0}'.format(_platform))
            destination_path = os.path.join(expanduser("~"), "imgtec/console_scripts")
            shutil.rmtree(destination_path, ignore_errors=True)
            dir_util.copy_tree("jtagutils", destination_path, update=1, preserve_mode=0)
            install.run(self)
        else:
            print('Skipping jtagutils on platform: {0}'.format(_platform))


if _platform == "linux" or _platform == "linux2":
    packages_list = ['probeutils', 'csrutils', 'dbgmacros', 'jtagutils']
else:
    packages_list = ['probeutils', 'csrutils', 'dbgmacros']

setup(
    name = 'dbgutils',
    version = '0.3.0',
    author = 'Nag Ponugoti(nag.ponugoti@fungible.com)',
    description = 'python debug utilities for F1',
    scripts = ['dbgsh'],
    packages = packages_list,
    package_data = {'probeutils': ["probeutils/dut.cfg"]},
    include_package_data=True,
    cmdclass={'jtaginstall': JtagExtCommands},
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
