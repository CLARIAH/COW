# canfam
Scripts to make a rdf-conversion ready csv file from the "Canadian families" spps dataset and to create a vocabulary. Should be run in the following order

1. canfamconvert.r - read and clean spss file, convert to csv file
2. canfamvocab.r - make canadacodes.json from csv file
3. canfamvocab.py - canadacodes.json into rdf
4. canfamcsv2rdf.sh - shell file to make rdf out of csv

canadadefs.txt is a text file containing the definitions of the variables required for canfamvocab.r. They were taken from the pdf codebook available at the [website of the Canadian Family project](http://web.uvic.ca/hrd/cfp/data/index.html). The spss dataset can also be found there.