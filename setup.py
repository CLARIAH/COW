#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from setuptools import setup
import os
import sys

# The directory containing this file
HERE = os.path.dirname(os.path.realpath(__file__))

# The text of the README file
README = os.path.join(HERE, 'README.md')

with open('requirements.txt') as f:
    required = f.read().splitlines()

cow_base = os.path.join('src', '')
cow_data = [ os.path.join('.', os.path.join(root.replace(cow_base, ''), '*')) for root,dirs,files in os.walk(cow_base) ]

cow_version = 'x.xx'

setup(name = 'cow_csvw',
      version = cow_version,
      description = 'Batch converter of large CSVs into CSVW/RDF',
      long_description=README,
	  long_description_content_type="text/markdown",
      author = 'Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman, Albert Meroño-Peñuela',
      author_email = 'albert.merono@vu.nl',
      url = 'https://github.com/CLARIAH/COW',
      download_url = 'https://github.com/CLARIAH/COW/archive/' + cow_version + '.tar.gz',
      packages = ['cow_csvw'],
      package_dir = {'cow_csvw': 'src'},
      package_data = {'cow_csvw': cow_data},
      entry_points={'console_scripts' : [ 'cow_tool = cow_csvw.csvw_tool:main' ]},
      keywords = ['csv', 'rdf', 'csvw'],
      install_requires=required
)
