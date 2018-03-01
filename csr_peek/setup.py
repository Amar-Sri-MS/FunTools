#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'csr-slurp',
    version = '0.1.0',
    author = 'Hariharan Thantry',
    description = 'Slurper for csr',
    scripts = ['bin/csr-slurp'],
    packages = find_packages(),
    package_data = {
      'schema/': ['*.yaml'],
      'template': ['*.j*'],
      'csr_cfg': ['AMAP', '*.yaml'],
      'csr_cfg/yaml': ['*.yaml']

    },
    include_package_data=True,
    install_requires = [
        'setuptools-git',
        'pyyaml',
        'jinja2'
    ],
)
