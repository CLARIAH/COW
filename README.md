## Converters
**Authors:**    Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman
**Copyright:**  VU University Amsterdam, Utrecht University, International Institute for Social History
**License:**    MIT License (see [license.txt](license.txt))

This package contains a comprehensive utility package for batch  conversion of multiple datasets expressed in CSV,
including datasets mapped through the [QBer](https://github.com/CLARIAH/QBer) tool.

[![Build Status](https://travis-ci.org/CLARIAH/wp4-converters.svg?branch=master)](https://travis-ci.org/CLARIAH/wp4-converters)

### Open issues

* We do not yet have a standard way to convert vocabularies (e.g. HISCO) expressed in CSV files
* We do not yet convert CSV on the basis of [CSVW metadata](http://w3c.github.io/csvw/metadata/), but we plan to

### Prerequisites

* Python 2.7
* `pip`
* `virtualenv` (simply `pip install virtualenv`)

#### Datasets required for tests (but not included)

* Requires an excerpt from the 1881 England Wales dataset (NAPP) for the schema-extraction tests
* Requires utrecht_1829_clean_01 for other conversion tests

### Installation

Open up a terminal, and clone this repository to a directory of your choice:

```
git clone https://github.com/CLARIAH/wp4-converters.git
```

Change into the directory that was just created, and instantiate a virtual Python environment:

```
virtualenv .
```

Activate the virtual environment:

```
source bin/activate
```

Install the required packages:

```
pip install -r requirements.txt
```

Change directory to `src`, and optionally replace the author in the config.py with your own data.  


# Using the converters

This library supports two converter styles, one takes a QBer specific JSON file as input, the other takes a CSVW-style JSON file as input (CSVW implementation is not fully compliant, nor guaranteed to work.)

## Running QBer-style conversions

To run, first make a QBer-style json file describing the csv file's schema:

```
python csv2qber-schema.py csv_file_name_without_extension dataset_name
```

Now convert the csv file by running csv2qb on the resulting JSON file:

```
python csv2qb.py csv_file_name.json output_file_name.nq
```

## Running  CSVW to RDF support

To run, first build a CSVW schema file (a file ending with `-metadata.json`).

For example, if you want to convert the file `data/example.csv`:

```
python csvw-tool.py build data/example.csv
```

This will generate the file `data/example.csv-metadata.json`, a rudimentary CSVW schema file in JSON-LD format. If a prior version of that file exists, it will be renamed with a timestamp of its last modification date. The builder will assume a comma-separated CSV file with a double quote as quotation character, and makes an educated guess as to its encoding. If you want to treat a CSV file in a different format, you can do e.g.:

```
python csvw-tool.py build data/example.csv --delimiter=';' --encoding=latin --quotechar='"'
```

Run `python csvw-tool.py --help` for details.

Edit the `data/example.csv-schema.json` file to suit your needs (see [the CSVW to RDF specification](http://www.w3.org/TR/csv2rdf/)). See below for the CSVW implementation status.

The next step is to convert the CSV file to RDF (NQuads) according to your specification. To do this for our `data/example.csv`, you run:

```
python csvw-tool.py convert data/example.csv
```

This will run the converter in 4 parallel processes. If something goes wrong (and it often does), you may want to run the converter as a single process:

```
python csvw-tool.py convert data/example.csv --processes=1
```

You can convert multiple files in one go by simply using unix-style file masks, or enumerating the files in a space-separated list:

```
python csvw-tool.py convert data/*.csv data/more/example1.csv data/more/example2.csv
```

Have fun!

### CSVW status
* Extended CSVW standard to support Jinja2 template formatting in URL patterns.
* Also supports patterns in lang attributes.
* CSVW has several 'special' formatting keywords, such as {_title} and {_row}. This converter currently only supports {_row}, which will insert a row number.
* Literal values can also be formatted as patterns, but this is not supported by CSVW. You need to use `csvw:value` as key to a column specification (rather than just `value`). The `csvw:value` instruction works in the same way as the `valueUrl` (and friends), but results in a Literal, rather than a URI.


## OLD (below)

This repository contains a collection of conversion scripts for various datasets and code lists to RDF:

* HISCO vocabulary
* Canadian Families data
* NAPP data
* ClioInfra converters

Also:

* Data ingestion scripts for uploading the results of data conversion to Virtuoso
* A parallelized converter for very (very) large datasets.

### TODO

We're in the process of harmonizing these converters to a comprehensive utility package for batch conversion of multiple datasets in various formats (including datasets mapped through the [QBer](https://github.com/CLARIAH/QBer) tool).
