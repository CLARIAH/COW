import sys
sys.path.append('csvw-parser')

from csvwparser import CSVW

c = CSVW(path='../sdh-private-hisco-datasets/hisco_45.csv',
         metadata_path='../sdh-private-hisco-datasets/hisco_45.csv-metadata.json')

import pprint

pprint(c.to_json())
