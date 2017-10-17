#!/bin/bash

# clear old graph 
source /scratch/clariah-sdh/converters/scripts/virtuoso-run-script.sh /scratch/clariah-sdh/converters/scripts/clear_clio_graph.sql &> /dev/null

# convert data 
python qbcliodata.py
gzip -f rdf/qbcliogdp.ttl

# load new data
source /scratch/clariah-sdh/converters/scripts/virtuoso-run-script.sh /scratch/clariah-sdh/converters/scripts/load_clio_data.sql &> /dev/null

