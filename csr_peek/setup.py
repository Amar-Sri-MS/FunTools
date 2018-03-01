#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'csr-slurp',
    version = '0.1.0',
    author = 'Hariharan Thantry',
    description = 'Slurper for csr',
    scripts = ['bin/csr-slurp', 'bin/csr-get'],
    packages = find_packages(),
    package_data = {
      'schema/': ['*.yaml'],
      'template': ['*.j*']
    },
    include_package_data=True,
    install_requires = [
        'setuptools-git',
        'pyyaml',
        'jinja2'
    ],
)
