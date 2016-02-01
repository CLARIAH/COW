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
