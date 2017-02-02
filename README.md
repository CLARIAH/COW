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

## FAQ / Tips and tricks ('under construction')
* What's the general structure of the resulting .nq file?
  - block 1 contains information on the csv file such as delimiter and encoding
  - block 2 provides information on the licensing
  - block 3 provides information on the publisher (you)
  - block 4 contains the reference to the file, your base-uri, language and short-hand uri definitions, and finally some provenance info, such as date first created
  - block 5 starts with 'tableSchema'. This is the section that you will want to focus on, as this is where you'll describe your variables in RDF. Note that the 'aboutUrl' just under tableSchema is the default 'aboutUrl'.
* After I build my file I get all kinds of @id rows. What should I do with those?
    - The purpose of these rows is that they [xxx please add xxx] In principle you can delete them.

* What do the blocks of code for each variable mean?
```
{
 "datatype": "string"
 "titles": [
 "institute"
  ],
"name": "institute",
"dc:description": "institute"
},
```
   - datatype indicates the datatype of your variable. possible values are: string, url, decimal [xxx please add xxx]
   - titles indicates the title ... appearing in ..... It is in plural because [xxx please add xxx]
   - name refers to the name of the variable. It is different from title, because [xxx please add xxx]. Note that when no 'valueUrl' is specified, the values for the column specified by ```"name": "my_column"``` are used as literals. 
   - dc:description provides a way to describe your variable in more detail. E.g. if your variable is called 'age' a more concise description would be 'age at interview'. the 'dc:' part means it is part of the Dublin Core vocabulary (http://dublincore.org/documents/dces/)

* How can I expand the description of my variable in RDF?
    - You can add information by adding a 'virtual block'. For example, suppose we started out with the block above, we could expand on it in the follow way.
```
{
 "datatype": "string",
 "titles": [
 "institution"
 ],
 "name": "institution",
 "dc:description": "The research institute providing the study"
 },
 {
 "virtual": true,
 "propertyUrl": "foaf:Organization",
 "valueUrl": "institute/{institution}"
},
```
   - If our base url would be http://example.com, it would create a series of uri's representing all the different values (institutes) in the dataset, like so: http://example.com/institute/Institute4AwesomeResearch, http://example.com/institute/StarWarsAcademy, etc..

* My variable contains web addresses (urls). How can I have them as proper addresses rather than strings?

    - Change the datatype to: url.
    
* Can I assign values conditionally, i.e. use an if-statement?
    - Indeed you can. For example, HISCO codes ought to be 5 digits, but sometimes the first digit is a zero and then gets 'lost'. So we want to add that zero back, when HISCO has less than 5 digits. However, we don't want to add a zero, to the codes indicating missing HISCO's: (-1, -2 (and -3 in the Dutch Historical Sample version of HISCO)). Ergo:
    ```
    "aboutUrl": "hisco:{% if not HISCO in ['-1','-3','-2']%}{HISCO:0>5}{% else %}{HISCO}{% endif %}"
    ```
    Also see the section https://github.com/CLARIAH/wp4-converters/blob/master/README.md#commonly-used-jinja2-template-formatting below.


* What does ValueError: Expecting , delimiter: line 161 column 5 (char 5716) mean?
  - This might happen when you use the csvw-tool to convert a dataset. It indicates that you probably forgot say a comma in the line before.

* When converting, I get the following error: "Exception: Could not find source file or necessary metadata file in path..."
  - It's likely your trying to convert the .csv-metadata.json file rather than the .csv file itself.
  
### CSVW status
* Extended CSVW standard to support Jinja2 template formatting in URL patterns (see below for commonly used template formatting).
* Also supports patterns in lang attributes.
* CSVW has several 'special' formatting keywords, such as {_title} and {_row}. This converter currently only supports {_row}, which will insert a row number.
* Literal values can also be formatted as patterns, but this is not supported by CSVW. You need to use `csvw:value` as key to a column specification (rather than just `value`). The `csvw:value` instruction works in the same way as the `valueUrl` (and friends), but results in a Literal, rather than a URI.

#### Commonly used Jinja2 template formatting
* Leading zeroes: `variable:{0>N}`, where `N` is the number of digits to fill up to.
* If-else statements: `{% if conditional_variable=="something" %} value_if {% else %} value_else {% endif %}`.
* Convert to string and concatenate: `{{variable ~ 'string'}}`, e.g. if variable has value "Hello" then the result would be "Hello string". Note the double braces.
* Arithmetic: use double braces and cast as numeric first, e.g. `{{variable|float() * 1000}}`.




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
