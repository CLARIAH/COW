#!/bin/bash

echo "WARNING: This script is deprecated in favour of the CSVW-based converters"

# clear old graph
source /scratch/clariah-sdh/converters/scripts/virtuoso-run-script.sh /scratch/clariah-sdh/converters/scripts/clear_hisco_graph.sql &> /dev/null

# convert data
python hisco_category2rdf.py
python hisco_entry_book2rdf.py
python hisco_hisco2rdf.py
python hisco_major_group2rdf.py
python hisco_minor_group2rdf.py
python hisco_product2rdf.py
python hisco_relation2rdf.py
python hisco_status2rdf.py
python hisco_unit_group2rdf.py
python hisco2cam.py
python occhisco2hisco.py

# load new data
source /scratch/clariah-sdh/converters/scripts/virtuoso-run-script.sh /scratch/clariah-sdh/converters/scripts/load_hisco_data.sql &> /dev/null
