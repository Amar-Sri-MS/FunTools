#!/usr/bin/env python2.7

from setuptools import setup, find_packages
import os.path
from distutils import dir_util
from os.path import expanduser
import shutil
import tempfile
import urllib
import ssl

from setuptools.command.install import install
from sys import platform as _platform

class JtagExtCommands(install):
    def run(self):
        if _platform == "linux" or _platform == "linux2":
            fp = tempfile.NamedTemporaryFile(delete=False)
            url = 'https://s3-eu-west-1.amazonaws.com/downloads-mips/mips-downloads/tools/Codescape-Debugger/Codescape-Debugger-8.5.6.4.CentOS-5.x86_64.py'
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            print "Downloading codescape libraries. It may take few minutes ..."
            filedata = urllib.urlopen(url, context=ctx)
            datatowrite = filedata.read()
            fp.write(datatowrite)
            tempfile_name = fp.name
            fp.close()
            print "Installing codescape libraries..."
            os.system('sudo python ' + fp.name + ' --accept-licence --shared'
                      ' --install-scripting')
            os.unlink(fp.name)
            print('Copying jtag Codescape command scripts(platform:{0}'.format(_platform))
            destination_path = os.path.join(expanduser("~"), "imgtec/console_scripts")
            shutil.rmtree(destination_path, ignore_errors=True)
            dir_util.copy_tree("jtagutils", destination_path, update=1, preserve_mode=0)
            install.run(self)
        else:
            print('Skipping jtagutils on platform: {0}'.format(_platform))


if _platform == "linux" or _platform == "linux2":
    packages_list = ['probeutils', 'csrutils', 'csr2utils', 'dbgmacros', 'jtagutils']
else:
    packages_list = ['probeutils', 'csrutils', 'csr2utils', 'dbgmacros']

setup(
    name = 'dbgutils',
    version = '0.4.0',
    author = 'Nag Ponugoti(nag.ponugoti@fungible.com)',
    description = 'python debug utilities for F1',
    scripts = ['dbgsh'],
    packages = packages_list,
    include_package_data=True,
    package_data = {'probeutils': ["probeutils/dut.cfg"]},
    cmdclass={'jtaginstall': JtagExtCommands},
    install_requires = [
        'pyperclip',
        'contextlib2',
        'jsocket==1.6',
        'logging==0.4.9.6',
        'cmd2==0.8.8',
        'argcomplete',
        'pyparsing==2.4.7',
        'pyusb==1.0.2',
        'paramiko==2.7.1',
        'urllib3==1.22',
        'aardvark-py',
        'pynacl'
    ],
)
