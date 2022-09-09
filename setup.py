#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup
import os
import sys

with open('requirements.txt') as f:
    required = f.read().splitlines()

cow_base = os.path.join('src', '')
cow_data = [ os.path.join('.', os.path.join(root.replace(cow_base, ''), '*')) for root,dirs,files in os.walk(cow_base) ]

version = '1.21'

setup(name = 'cow_csvw',
      version = version,
      description = 'Integrated CSV to RDF converter, using CSVW and nanopublications',
      long_description = open('README.md').read(),
      long_description_content_type="text/markdown",
      author = 'Albert Meroño-Peñuela, Roderick van der Weerdt, Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman, Melvin Roest, Xander Wilcke',
      author_email = 'albert.merono@vu.nl',
      url = 'https://github.com/CLARIAH/COW',
      download_url = 'https://github.com/CLARIAH/COW/archive/' + version + '.tar.gz',
      license = "MIT",
      classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10"
        ],
      packages = ['cow_csvw'],
      package_dir = {'cow_csvw': 'src'},
      package_data = {'cow_csvw': cow_data},
      entry_points={'console_scripts' : [ 'cow_tool = cow_csvw.csvw_tool:main' ]},
      keywords = ['csv', 'rdf', 'csvw'],
      install_requires=required
)
