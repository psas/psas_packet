#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import psas_packet

setup(
    name='psas_packet',
    version=psas_packet.__version__,
    description='serializer for PSAS data standards',
    long_description=open('README.rst').read(),
    author='Nathan Bergey',
    author_email='nathan.bergey@gmail.com',
    url='http://psas-packet-serializer.readthedocs.org',
    packages=['psas_packet'],
    package_dir={'psas_packet': 'psas_packet'},
    include_package_data=True,
    install_requires=[],
    scripts=[
        'scripts/gen-psas-types',
        'scripts/log2csv',
        'scripts/slicelog',
        'scripts/replaylog',
        'scripts/autodoc',
    ],
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=[
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
