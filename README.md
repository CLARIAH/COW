## COW: Integrated CSV to RDF Converter

> COW (Csv On the Web) is an integrated CSV to RDF converter that uses the W3C standard [CSVW](https://www.w3.org/TR/tabular-data-primer/) for rich semantic table specificatons, and [nanopublications](http://nanopub.org/) as an output RDF model



### What is COW

COW is a command-line utility to convert any CSV file into an RDF dataset. Its distinctive features are:

- Expressive CSVW-compatible schemas based on the [Jinja](https://github.com/pallets/jinja) template enginge
- Highly efficient implementation leveraging multithread and multicore architectures
- Available as a pythonic [CLI tool](#cli), [library](#library), and [web service](#web-service)
- Supports Python2 Python 3

Known issues:
- The Python3 implementation is functional but currently does not support binary comparison operators in JSF Jinja templates. If you need these, we recommend you use Python2 until we fix this, or the [cattle legacy](http://legacy.cattle.datalegend.net/) web service version

### Install

`pip` is the recommended method of installing COW in your system:

```
pip install cow-csvw
```

You can upgrade your currently installed version with:

```
pip install cow-csvw --upgrade
```

Possible issues:

- Permission issues. You can get around them by installing COW in user space: `pip install cow-csvw --user`. Make sure your binary user directory (typically something like `/Users/user/Library/Python/3.7/bin` in MacOS or `/home/user/.local/bin` in Linux) is in your PATH. For Windows/MacOS we recommend to install Python via the [official distribution page](https://www.python.org/downloads/). You can also use [virtualenv](https://virtualenv.pypa.io/en/latest/) to avoid conflicts with your system libraries
- Please [report your unlisted issue](https://github.com/CLARIAH/COW/issues/new)

If you can't/don't want to deal with installing COW, you can use the [cattle](http://cattle.datalegend.net/) [web service version](#web-service) (with some limitations).

### Usage

#### CLI

The CLI (command line interface) is the recommended way of using COW for most users. The straightforward CSV to RDF conversion is done in two steps. First:

```
cow_tool build myfile.csv
```

This will create a file named `myfile.csv-metadata.json` (from now on: JSON schema file or just JSF). You don't need to worry about this file if you only want a syntactic conversion. Then:

```
cow_tool convert myfile.csv
```

Will output a `myfile.csv.nq` RDF file (nquads by default; you can control the output RDF serialization with e.g. ``--format turtle``). That's it!

If you want to control the base URI namespace, URIs used in predicates, virtual columns, and the many other features of COW, you'll need to edit the `myfile.csv-metadata.json` JSF and/or use COW arguments. Have a look at the [CLI options](#options) below, the examples in the [wiki](https://github.com/CLARIAH/COW/wiki), and the [technical documentation](http://csvw-converter.readthedocs.io/en/latest/).

##### Options

Check the ``--help`` for a complete list of options:

```
usage: cow_tool [-h] [--dataset DATASET] [--delimiter DELIMITER]
                [--quotechar QUOTECHAR] [--processes PROCESSES]
                [--chunksize CHUNKSIZE] [--base BASE]
                [--format [{xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}]]
                [--version]
                {convert,build} file [file ...]

Not nearly CSVW compliant schema builder and RDF converter

positional arguments:
  {convert,build}       Use the schema of the `file` specified to convert it
                        to RDF, or build a schema from scratch.
  file                  Path(s) of the file(s) that should be used for
                        building or converting. Must be a CSV file.

optional arguments:
  -h, --help            show this help message and exit
  --dataset DATASET     A short name (slug) for the name of the dataset (will
                        use input file name if not specified)
  --delimiter DELIMITER
                        The delimiter used in the CSV file(s)
  --quotechar QUOTECHAR
                        The character used as quotation character in the CSV
                        file(s)
  --processes PROCESSES
                        The number of processes the converter should use
  --chunksize CHUNKSIZE
                        The number of rows processed at each time
  --base BASE           The base for URIs generated with the schema (only
                        relevant when `build`ing a schema)
  --format [{xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}], -f [{xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}]
                        RDF serialization format
  --version             show program's version number and exit
```

#### Web service

There is web service and interface running COW, called [cattle](http://cattle.datalegend.net/). Two public instances are running at:

- http://cattle.datalegend.net/ - runs COW in Python3
- http://legacy.cattle.datalegend.net/ - runs COW in Python2 for legacy reasons

Beware of the web service limitations:

- There's a limit to the size of the CSVs you can upload
- It's a public instance, so your conversion could take longer

#### Library

Once installed, COW can be used as a library as follows:

```
from cow_csvw.csvw_tool import COW
import os

COW(mode='build', files=[os.path.join(path, filename)], dataset='My dataset', delimiter=';', quotechar='\"')

COW(mode='convert', files=[os.path.join(path, filename)], dataset='My dataset', delimiter=';', quotechar='\"', processes=4, chunksize=100, base='http://example.org/my-dataset', format='turtle')
```

### Examples

 As an addition to this documentation the [wiki](https://github.com/CLARIAH/COW/wiki) provides more hands-on examples of transposing csv's into Linked Data

### Documentation

Technical documentation for COW are maintained in this GitHub repository (under <docs>), and published through [Read the Docs](http://readthedocs.org) at <http://csvw-converter.readthedocs.io/en/latest/>.

To build the documentation from source, change into the `docs` directory, and run `make html`. This should produce an HTML version of the documentation in the `_build/html` directory.

### License

MIT License (see [license.txt](license.txt))

### Acknowledgements

**Authors:**    Albert Meroño-Peñuela, Roderick van der Weerdt, Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman

**Copyright:**  Vrije Universiteit Amsterdam, Utrecht University, International Institute for Social History


COW is developed and maintained by the CLARIAH project and funded by NWO.
