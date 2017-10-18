#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from distutils.core import setup
import os

with open('requirements.txt') as f:
    required = f.read().splitlines()

cow_base = 'src/'
cow_data = [ root.replace(cow_base, '') + '/*' for root,dirs,files in os.walk(cow_base) ]
cow_version = '0.11'

setup(name = 'cow_csvw',
      version = cow_version,
      description = 'Batch converter of large CSVs into CSVW/RDF',
      author = 'Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman, Albert Meroño-Peñuela',
      author_email = 'albert.merono@vu.nl',
      url = 'https://github.com/CLARIAH/COW',
      download_url = 'https://github.com/CLARIAH/COW/archive/' + cow_version + '.tar.gz', # I'll explain this in a second
      packages = ['cow_csvw'],
      package_dir = {'cow_csvw': 'src'},
      package_data = {'cow_csvw': cow_data},
      entry_points={'console_scripts' : [ 'cow_tool = cow_csvw.cow_tool:main' ]},
      keywords = ['csv', 'rdf', 'csvw'],
      install_requires=required
)
