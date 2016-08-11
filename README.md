## Converters
**Authors:**    Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman
**Copyright:**  VU University Amsterdam, Utrecht University, International Institute for Social History
**License:**    MIT License (see [license.txt](license.txt))

This package contains a comprehensive utility package for batch  conversion of multiple datasets expressed in CSV,
including datasets mapped through the [QBer](https://github.com/CLARIAH/QBer) tool.

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

To run, first make a QBer-style json file describing the csv file's schema:

```
python csv2qber-schema.py csv_file_name_without_extension dataset_name
```

Now convert the csv file by running csv2qb on the resulting JSON file:

```
python csv2qb.py csv_file_name.json output_file_name.nq
```


# CSVW to RDF support

* Extended CSVW standard to support Jinja2 template formatting in URL patterns.
* Also supports patterns in lang attributes.


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
