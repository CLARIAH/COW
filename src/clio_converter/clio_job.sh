#!/bin/bash

# clear old graph 
source /scratch/clariah-sdh/converters/virtuoso_scripts/virtuoso-run-script.sh /scratch/clariah-sdh/converters/virtuoso_scripts/clear_clio_graph.sql

#  &> /dev/null

# convert data 
python qbcliodata.py

# load new data
source /scratch/clariah-sdh/converters/virtuoso_scripts/virtuoso-run-script.sh /scratch/clariah-sdh/converters/virtuoso_scripts/load_clio_data.sql

