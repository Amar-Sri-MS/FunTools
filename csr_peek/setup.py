#!/usr/bin/env python2.7

from setuptools import setup, find_packages

setup(
    name = 'csr-slurp',
    version = '0.1.0',
    author = 'Hariharan Thantry',
    description = 'Slurper for csr',
    scripts = ['bin/csr-slurp'],
    packages = find_packages(),
    include_package_data=True,
    install_requires = [
        'setuptools-git',
        'pyyaml',
        'jinja2',
        'ply'
    ],
)
