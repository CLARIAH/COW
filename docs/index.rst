.. CSVW Converters documentation master file, created by
   sphinx-quickstart on Fri Nov 18 13:15:57 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. highlight:: python
  :linenothreshold: 5

.. toctree::
  :hidden:
  :maxdepth: 2

  self

COW
===

This package contains a comprehensive tool (COW [#f2]_) for batch conversion of multiple datasets expressed in CSV. It uses a JSON schema expressed using an extended version of the CSVW standard, to convert CSV files to RDF in scalable fashion.

`CSV on the Web (CSVW) <https://www.w3.org/ns/csvw>`_ is a W3C standard for metadata descriptions for tabular data. Typically, these data reside in CSV files. CSVW metadata is captured in ``.csv-metadata.json`` files that live alongside the CSV files that they describe. For instance, a CSV file called ``data.csv`` and its metadata ``data.csv-metadata.json`` would be hosted at::

  http://example.com/data.csv
  http://example.com/data.csv-metadata.json

Another feature of CSVW is that it allows the specification of a mapping (or interpretation) of values in the CSV in terms of RDF. The ``tableSchema`` element in CSVW files defines per column what its properties should be, but may also define custom mappings to e.g. URIs in RDF.

Interestingly, the JSON format used by CSVW metadata is an `extension of the JSON-LD specification <https://www.w3.org/TR/json-ld/>`_, a JSON-based serialization for Linked Data. As a consequence of this, the CSVW metadata can be directly attached (as provenance) to the RDF resulting from a CSVW-based conversion.

This is exactly what the CSVW Converters do.

Features & Limitations
^^^^^^^^^^^^^^^^^^^^^^

Compared to the CSVW specification, the converters have a number of limitations and extra features. These are:

1. COW *does not* perform any schema checking, and ignores any and all parts of the `CSVW Specification <https://www.w3.org/ns/csvw>`_ that are not directly needed for the RDF conversion.

2. COW extends the CSVW specification in several ways:

  * Advanced formatting of URLs and values
  * Dealing with multiple null values and null values for one or more other columns.
  * Simple SKOS support (generating collections and schemes)
  * Optionally skipping/not skipping empty cells
  * A default set of namespace prefixes

3. COW does some smart guessing:

  * Determining file encoding
  * Determining the delimiter
  * Generating a skeleton schema for any CSV file (see :ref:`here <skeleton-schema>`)

Installation
^^^^^^^^^^^^^

Prerequisites
-------------

* Python 2.7 (installed on most systems)
* ``pip``
* ``virtualenv`` (simply `pip install virtualenv`) [#f1]_

Step by step instructions
-------------------------

Open up a terminal, and clone this repository to a directory of your choice::

  git clone https://github.com/CLARIAH/wp4-converters.git

Of course you can also use a git client with a UI.

Change into the directory that was just created, and instantiate a virtual Python environment::

  virtualenv .

Activate the virtual environment::

  source bin/activate

Install the required packages::

  pip install -r requirements.txt

Change directory to `src`, and optionally replace the author in the config.py with your own data.


Usage
^^^^^

The primary command line script for CSVW-based conversion is ``csvw-tool.py``. It can be used for two tasks:

1. Generating a :ref:`skeleton CSVW JSON-Schema <skeleton-schema>` for a specific CSV file.
2. Using such a schema to :ref:`convert a CSV file to RDF <converting-csv>` (in `NQuads format <https://www.w3.org/TR/n-quads/>`_)

General usage instructions can be obtained by running ``python csvw-tool.py -h``::

  usage: csvw-tool.py [-h] [--dataset DATASET] [--delimiter DELIMITER]
                      [--quotechar QUOTECHAR] [--processes PROCESSES]
                      [--chunksize CHUNKSIZE] [--base BASE]
                      {convert,build} file [file ...]

.. table:: Explanation of commandline options for ``csvw-tool.py``

   ===================    ===========
   Option                 Explanation
   ===================    ===========
   ``dataset``            Specifies the name of the dataset, if it is different from the filename with the ``.csv`` extension stripped.
   ``delimiter``          Forces the use of a specific delimiter when parsing the CSV file (only used with ``build`` option)
   ``quotechar``          Forces the use of a specific quote character (default is ``"``, only used with ``build`` option)
   ``processes``          Specifies the number of parallel processes to use when converting a CSV file (default is 4)
   ``chunksize``          Specifies the number of lines that will be passed to each process (default is 5000)
   ``base``               The base for URIs generated with the schema (only used with ``build`` option, the default is ``http://data.socialhistory.org``)
   ``{convert,build}``    The ``convert`` option triggers a conversion to RDF for the files specified in ``file [file ...]``. The ``build`` option generates a skeleton JSON schema for the files specified.
   ``file [file ...]``    A list of files to be converted (or "built"); any unix-style wildcards are allowed.
   ===================    ===========

.. _skeleton-schema:

Generating a Skeleton Schema
----------------------------

Since JSON is a rather verbose language, and we currently do not have a convenient UI for constructing CSVW schema files, COW allows you to generate a skeleton schema for any CSV file.

Suppose you want to build a skeleton schema for a file ``imf_gdppc.csv`` (from [#f4]_) that looks like::

  Rank;Country;Int$
  1;Qatar;131,063
  2;Luxembourg;104,906
  3;Macau;96,832
  4;Singapore;90,249
  5;Brunei Darussalam;83,513
  6;Kuwait;72,675
  7;Ireland;72,524
  8;Norway;70,645

Make sure you have your virtual environment enabled (if applicable), and run::

  python csvw-tool.py build imf_gdppc.csv --base=http://example.com/resource

The ``--base`` option specifies the base for all URIs generated through the schema. This is ``http://data.socialhistory.org/resource`` by default (see http://datalegend.net)

This will genrate a file called ``imf_gdppc.csv-metadata.json`` with the following contents:

.. code-block:: json
  :linenos:

  {
   "dialect": {
    "quoteChar": "\"",
    "delimiter": ";",
    "encoding": "ascii"
   },
   "dcat:keyword": [],
   "dc:license": {
    "@id": "http://opendefinition.org/licenses/cc-by/"
   },
   "dc:publisher": {
    "schema:name": "CLARIAH Structured Data Hub - Datalegend",
    "schema:url": {
     "@id": "http://datalegend.org"
    }
   },
   "url": "imf_gdppc.csv",
   "@context": [
    "http://www.w3.org/ns/csvw",
    {
     "@base": "http://example.com/resource/",
     "@language": "en"
    },
    {
     [...]
    }
   ],
   "dc:title": "imf_gdppc.csv",
   "@id": "http://example.com/resource/imf_gdppc.csv",
   "dc:modified": {
    "@value": "2017-02-28",
    "@type": "xsd:date"
   },
   "tableSchema": {
    "aboutUrl": "{_row}",
    "primaryKey": "Rank",
    "columns": [
     {
      "datatype": "string",
      "titles": [
       "Rank"
      ],
      "@id": "http://example.com/resource/imf_gdppc.csv/column/Rank",
      "name": "Rank",
      "dc:description": "Rank"
     },
     {
      "datatype": "string",
      "titles": [
       "Country"
      ],
      "@id": "http://example.com/resource/imf_gdppc.csv/column/Country",
      "name": "Country",
      "dc:description": "Country"
     },
     {
      "datatype": "string",
      "titles": [
       "Int$"
      ],
      "@id": "http://example.com/resource/imf_gdppc.csv/column/Int$",
      "name": "Int$",
      "dc:description": "Int$"
     }
    ]
   }
  }



.. _converting-csv:

Converting a CSV file
---------------------

If we now want to convert our example file ``imf_gdppc.csv``, you first make sure you have your virtual environment enabled (if applicable), and run::

  python csvw-tool.py convert imf_gdppc.csv

This is also the preferred method for converting multiple files at the same time. For instance, if you want to convert `all` CSV files in a specific directory, simply use unix-style wildcards::

  python csvw-tool.py convert /path/to/some/directory/*.csv

The Schema
^^^^^^^^^^

1. While CSVW allows only for simple references to values in a column using the curly-brackets syntax (e.g. ``{name}`` to refer to the value of the name column at the current row), COW interprets the strings containing these references in two ways:

  1. as `Python Format Strings <https://docs.python.org/2/library/string.html#formatstrings>`_, and
  2. as `Jinja2 Templates <http://jinja.pocoo.org>`_

  This allows for very elaborate operations on row contents (e.g. containing conditionals, loops, and string operations.) [#f3]_.

2. CSVW allows only to specify a single ``null`` value for a column; when the cell in that column is equal to the null value, it is ignored for RDF conversion. COW extends the CSVW treatment of ``null`` values in two ways:

  1. multiple potential ``null`` values for a column, expressed as a JSON list, and
  2. conditional on values in *another* column, as a JSON-LD list (using the ``@list`` keyword)

3. COW allows the use of ``csvw:collectionUrl`` and ``csvw:schemeUrl`` on column specifications. This will automatically cast the value for ``valueUrl`` to a ``skos:Concept``, and adds it to the collection or scheme respectively indicated by these urls using a ``skos:member`` or ``skos:inScheme`` predicate.

4. By default COW skips cells that are empty (as per the CSVW specification), setting the ``csvw:parseOnEmpty`` attribute to ``true`` overrides this setting. This is useful when an empty cell has a specific meaning.

5. Column specifications with a ``xsd:anyURI`` datatype are converted to proper URIs rather than Literals with the ``xsd:anyURI`` datatype.

6. Column specifications in COW should have a JSON-LD style ``@id`` attribute. This ensures that all predicates generated through the conversion are linked back to the RDF representation of the CSVW JSON schema that informed the conversion.

7. COW converts column names to valid Python dictionary keys. In general this means that spaces in column names will be replaced with underscores.

8. For convenience, COW uses a default set of namespaces, specified in the ``src/converter/namespaces.yaml`` file, that will be used to interpret namespace prefix use in the JSON schema. Any namespace prefixes defined in the JSON schema will override the default ones.




====


API Documentation
=================

* :ref:`code`



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Footnotes
---------
.. rubric:: Footnotes

.. [#f2] `COW`: **C**SV **O**n the **W**eb.
.. [#f1] These instructions use ``virtualenv`` but you can also install all packages globally, or use an alternative such as ``conda``.
.. [#f3] In the future we may enable the Jinja2 plugin mechanism. This will allow running custom Python functions as filters over values.
.. [#f4] https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28PPP%29_per_capita
