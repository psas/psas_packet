#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='psas_packet',
    version='0.1.0',
    description='serializer for PSAS data standards',
    long_description=open('README.md').read(),
    author='Nathan Bergey',
    author_email='nathan.bergey@gmail.com',
    url='https://github.com/psas/packet-serializer',
    packages=['psas_packet'],
    package_dir={'psas_packet': 'psas_packet'},
    include_package_data=True,
    install_requires=[
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