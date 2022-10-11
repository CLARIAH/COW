## CSV on the Web (CoW)

> CoW is an integrated CSV to RDF converter using the W3C standard [CSVW](https://www.w3.org/TR/tabular-data-primer/) for rich semantic table specificatons, producing [nanopublications](http://nanopub.org/) as an output RDF model. CoW converts any CSV file into an RDF dataset.



### Features

- Expressive CSVW-compatible schemas based on the [Jinja](https://github.com/pallets/jinja) template enginge.
- Highly efficient implementation leveraging multithreaded and multicore architectures.
- Available as a [Docker image](#docker-image), [command line interface (CLI) tool](command-line-interface), and [library](#library).

### Documentation and support
For user documentation see the [basic introduction video](https://t.co/SDWC3NhWZf) and the  [GitHub wiki](https://github.com/clariah/cow/wiki/). [Technical details](#technical-details) are provided below. If you encounter an issue then please [report](https://github.com/CLARIAH/COW/issues/new/choose) it. Also feel free to create pull requests.

## Quick Start Guide

### Docker Image

Several data science tools, including CoW, are available via a [Docker image](https://github.com/CLARIAH/datalegendtools).

#### Install

First, install the Docker virtualisation engine on your computer. Instructions on how to accomplish this can be found on the [official Docker website](https://docs.docker.com/get-docker). Use the following command in the Docker terminal:

```
# docker pull wxwilcke/datalegend
```
Here, the #-symbol refers to the terminal of a user with administrative privileges on your machine and is not part of the command.

After the image has successfully been downloaded (or 'pulled'), the container can be run as follows:

```
# docker run --rm -p 3000:3000 -it wxwilcke/datalegend
```
The virtual system can now be accessed by opening [http://localhost:3000/wetty](http://localhost:3000/wetty) in your preferred browser, and by logging in using username **datalegend** and password **datalegend**.

For detailed instructions on this Docker image, see [DataLegend Playground](https://github.com/CLARIAH/datalegendtools). For instructions on how to use the tool, see  [usage](#usage) below.



### Command Line Interface (CLI)

The Command Line Interface (CLI) is the recommended way of using CoW for most users.

#### Install

> Check whether the latest version of Python is installed on your device. For Windows/MacOS we recommend to install Python via the [official distribution page](https://www.python.org/downloads/).

The recommended method of installing CoW on your system is `pip3`:

```
pip3 install cow-csvw
```

You can upgrade your currently installed version with:

```
pip3 install cow-csvw --upgrade
```

Possible installation issues:

- Permission issues. You can get around them by installing CoW in user space: `pip3 install cow-csvw --user`. 
- Cannot find command: make sure your binary user directory (typically something like `/Users/user/Library/Python/3.7/bin` in MacOS or `/home/user/.local/bin` in Linux) is in your PATH (in MacOS: `/etc/paths`).
- Please [report your unlisted issue](https://github.com/CLARIAH/CoW/issues/new).

#### Usage

The straightforward CSV to RDF conversion is done by entering the following commands:

```
cow_tool build myfile.csv
```

This will create a file named `myfile.csv-metadata.json` (JSON schema file). Next:

```
cow_tool convert myfile.csv
```
This command will output a `myfile.csv.nq` RDF file (nquads by default).

You don't need to worry about the JSON file, unless you want to change the metadata schema. To control the base URI namespace, URIs used in predicates, virtual columns, etcetera, edit the `myfile.csv-metadata.json` file and/or use CoW commands. For instance, you can control the output RDF serialization (with e.g. ``--format turtle``). Have a look at the [options](#options) below, the examples in the [GitHub wiki](https://github.com/CLARIAH/CoW/wiki), and the [technical documentation](http://csvw-converter.readthedocs.io/en/latest/).

#### Options

Check the ``--help`` for a complete list of options:

```
usage: cow_tool [-h] [--dataset DATASET] [--delimiter DELIMITER]
                [--quotechar QUOTECHAR] [--encoding ENCODING] [--processes PROCESSES]
                [--chunksize CHUNKSIZE] [--base BASE]
                [--format [{xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}]]
				[--gzip] [--version]
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
  --encoding ENCODING   The character encoding used in the CSV file(s)

  --processes PROCESSES
                        The number of processes the converter should use
  --chunksize CHUNKSIZE
                        The number of rows processed at each time
  --base BASE           The base for URIs generated with the schema (only
                        relevant when `build`ing a schema)
  --gzip 				Compress the output file using gzip
  --format [{xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}], -f [{xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}]
                        RDF serialization format
  --version             show program's version number and exit
```



### Library

Once installed, CoW can be used as a library as follows:

```
from cow_csvw.csvw_tool import COW
import os

COW(mode='build', files=[os.path.join(path, filename)], dataset='My dataset', delimiter=';', quotechar='\"')

COW(mode='convert', files=[os.path.join(path, filename)], dataset='My dataset', delimiter=';', quotechar='\"', processes=4, chunksize=100, base='http://example.org/my-dataset', format='turtle', gzipped=False)
```



## Further Information

### Examples

The [GitHub wiki](https://github.com/CLARIAH/COW/wiki) provides more hands-on examples of transposing CSVs into Linked Data.

### Technical documentation

Technical documentation for CoW are maintained in this GitHub repository (under <docs>), and published through [Read the Docs](http://readthedocs.org) at <http://csvw-converter.readthedocs.io/en/latest/>.

To build the documentation from source, change into the `docs` directory, and run `make html`. This should produce an HTML version of the documentation in the `_build/html` directory.

### License

MIT License (see [license.txt](license.txt))

### Acknowledgements

**Authors:**    Albert Meroño-Peñuela, Roderick van der Weerdt, Rinke Hoekstra, Kathrin Dentler, Auke Rijpma, Richard Zijdeman, Melvin Roest, Xander Wilcke

**Copyright:**  Vrije Universiteit Amsterdam, Utrecht University, International Institute of Social History


CoW is developed and maintained by the CLARIAH project](https://www.clariah.nl) and funded by NWO.
