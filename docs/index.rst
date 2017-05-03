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
  :doc:`code`


*********************************
COW: Converter for CSV on the Web
*********************************

This package contains a comprehensive tool (COW [#f2]_) for batch conversion of multiple datasets expressed in CSV. It uses a JSON schema expressed using an extended version of the CSVW standard, to convert CSV files to RDF in scalable fashion.

`CSV on the Web (CSVW) <https://www.w3.org/ns/csvw>`_ is a W3C standard for metadata descriptions for tabular data. Typically, these data reside in CSV files. CSVW metadata is captured in ``.csv-metadata.json`` files that live alongside the CSV files that they describe. For instance, a CSV file called ``data.csv`` and its metadata ``data.csv-metadata.json`` would be hosted at::

  http://example.com/data.csv
  http://example.com/data.csv-metadata.json

Another feature of CSVW is that it allows the specification of a mapping (or interpretation) of values in the CSV in terms of RDF. The ``tableSchema`` element in CSVW files defines per column what its properties should be, but may also define custom mappings to e.g. URIs in RDF.

Interestingly, the JSON format used by CSVW metadata is an `extension of the JSON-LD specification <https://www.w3.org/TR/json-ld/>`_, a JSON-based serialization for Linked Data. As a consequence of this, the CSVW metadata can be directly attached (as provenance) to the RDF resulting from a CSVW-based conversion.

This is exactly what the COW converter does.

Features & Limitations
======================

Compared to the CSVW specification, the converter has a number of limitations and extra features. These are:

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

4. COW produces extensive provenance:

  * Converted data is encapsulated in a `Nanopublication <http://nanopub.org>`_
  * The original CSVW schema is encapsulated in the `np:hasProvenance` graph associated with the nanopublication.

Installation
============

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

Change directory to ``src``, and optionally replace the author in the ``config.py`` with your own data.

Usage
=====

The primary command line script for CSVW-based conversion is ``csvw-tool.py``. It can be used for two tasks:

1. Generating a :ref:`skeleton CSVW JSON-Schema <skeleton-schema>` for a specific CSV file.
2. Using such a schema to :ref:`convert a CSV file to RDF <converting-csv>` (in `NQuads format <https://www.w3.org/TR/n-quads/>`_)

General usage instructions can be obtained by running ``python csvw-tool.py -h``::

  usage: csvw-tool.py [-h] [--dataset DATASET] [--delimiter DELIMITER]
                      [--quotechar QUOTECHAR] [--processes PROCESSES]
                      [--chunksize CHUNKSIZE] [--base BASE]
                      {convert,build} file [file ...]

The table below gives a brief description of each of these options.

.. table:: Commandline options for ``csvw-tool.py``

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

  Rank;Country;Int
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
       "Int"
      ],
      "@id": "http://example.com/resource/imf_gdppc.csv/column/Int",
      "name": "Int",
      "dc:description": "Int"
     }
    ]
   }
  }

The exact meaning of this structure is explained in :ref:`the section below <the-schema>`.

.. _converting-csv:

Converting a CSV file
---------------------

If we now want to convert our example file ``imf_gdppc.csv``, you first make sure you have your virtual environment enabled (if applicable), and run::

  python csvw-tool.py convert imf_gdppc.csv

This will produce a file `imf_gdppc.csv.nq` that holds an NQuads serialization of the RDF.

This is also the preferred method for converting multiple files at the same time. For instance, if you want to convert `all` CSV files in a specific directory, simply use unix-style wildcards::

  python csvw-tool.py convert /path/to/some/directory/*.csv

Going back to our running example, the resulting RDF looks like this (when serialized as TriG):

.. code-block:: turtle
  :linenos:

  @prefix dlr: <http://data.socialhistory.org/resource/> .
  @prefix prov-o: <http://www.w3.org/ns/prov#> .
  @prefix schema: <http://schema.org/> .
  @prefix csvw: <http://www.w3.org/ns/csvw#> .
  @prefix dcterms: <http://purl.org/dc/terms/> .
  @prefix uuid: <urn:uuid:> .
  @prefix dlv: <http://data.socialhistory.org/vocab/> .
  @prefix np: <http://www.nanopub.org/nschema#> .
  @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
  @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
  @prefix xml: <http://www.w3.org/XML/1998/namespace> .
  @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

  <http://data.socialhistory.org/resource/imf_gdppc/pubinfo/769bcbf7/2017-02-28T14:05> {
      <http://data.socialhistory.org/resource/imf_gdppc/nanopublication/769bcbf7/2017-02-28T14:05> prov-o:generatedAtTime "2017-02-28T14:05:00"^^xsd:dateTime ;
          prov-o:wasGeneratedBy <https://github.com/CLARIAH/wp4-converters> .
  }

  <http://data.socialhistory.org/resource/imf_gdppc/provenance/769bcbf7/2017-02-28T14:05> {
      <http://data.socialhistory.org/resource/imf_gdppc/assertion/769bcbf7/2017-02-28T14:05> prov-o:generatedAtTime "2017-02-28T14:05:00"^^xsd:dateTime ;
          prov-o:wasDerivedFrom <http://data.socialhistory.org/resource/769bcbf7c31b526ce7bcf889c92837e276fd545d>,
              <http://example.com/imf_gdppc.csv> .

      <http://example.com/__row_> prov-o:wasDerivedFrom "http://example.com/{_row}"^^xsd:string .

      <http://example.com/imf_gdppc.csv> dcterms:license <http://opendefinition.org/licenses/cc-by/> ;
          dcterms:modified "2017-02-28"^^xsd:date ;
          dcterms:publisher [ schema:name "CLARIAH Structured Data Hub - Datalegend"@en ;
                  schema:url <http://datalegend.org/> ] ;
          dcterms:title "imf_gdppc.csv"@en ;
          csvw:dialect [ csvw:delimiter ";" ;
                  csvw:encoding "ascii" ;
                  csvw:quoteChar "\"" ] ;
          csvw:tableSchema [ csvw:aboutUrl <http://example.com/__row_> ;
                  csvw:column ( <http://example.com/imf_gdppc.csv/column/Rank> <http://example.com/imf_gdppc.csv/column/Country> <http://example.com/imf_gdppc.csv/column/Int> ) ;
                  csvw:primaryKey "Rank" ] ;
          csvw:url "imf_gdppc.csv"^^xsd:anyURI .

      <http://example.com/imf_gdppc.csv/column/Country> dcterms:description "Country"@en ;
          csvw:datatype xsd:string ;
          csvw:name "Country" ;
          csvw:title "Country"@en .

      <http://example.com/imf_gdppc.csv/column/Int> dcterms:description "Int"@en ;
          csvw:datatype xsd:string ;
          csvw:name "Int" ;
          csvw:title "Int"@en .

      <http://example.com/imf_gdppc.csv/column/Rank> dcterms:description "Rank"@en ;
          csvw:datatype xsd:string ;
          csvw:name "Rank" ;
          csvw:title "Rank"@en .
  }

  <http://data.socialhistory.org/resource/imf_gdppc/assertion/769bcbf7/2017-02-28T14:05> {
      <http://example.com/0> dlr:Country "Qatar"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "131.63"^^xsd:string ;
          dlr:Rank "1"^^xsd:string .

      <http://example.com/1> dlr:Country "Luxembourg"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "104.906"^^xsd:string ;
          dlr:Rank "2"^^xsd:string .

      <http://example.com/2> dlr:Country "Macau"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "96.832"^^xsd:string ;
          dlr:Rank "3"^^xsd:string .

      <http://example.com/3> dlr:Country "Singapore"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "90.249"^^xsd:string ;
          dlr:Rank "4"^^xsd:string .

      <http://example.com/4> dlr:Country "Brunei Darussalam"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "83.513"^^xsd:string ;
          dlr:Rank "5"^^xsd:string .

      <http://example.com/5> dlr:Country "Kuwait"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "72.675"^^xsd:string ;
          dlr:Rank "6"^^xsd:string .

      <http://example.com/6> dlr:Country "Ireland"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "72.524"^^xsd:string ;
          dlr:Rank "7"^^xsd:string .

      <http://example.com/7> dlr:Country "Norway"^^xsd:string ;
          <http://data.socialhistory.org/resource/Int> "70.645"^^xsd:string ;
          dlr:Rank "8"^^xsd:string .
  }

  uuid:af2851b5-405f-484b-869f-9f119f4b796f {
      <http://data.socialhistory.org/resource/769bcbf7c31b526ce7bcf889c92837e276fd545d> dlv:path "imf_gdppc.csv"^^xsd:string ;
          dlv:sha1_hash "769bcbf7c31b526ce7bcf889c92837e276fd545d"^^xsd:string .

      <http://data.socialhistory.org/resource/imf_gdppc/nanopublication/769bcbf7/2017-02-28T14:05> a np:Nanopublication ;
          np:hasAssertion <http://data.socialhistory.org/resource/imf_gdppc/assertion/769bcbf7/2017-02-28T14:05> ;
          np:hasProvenance <http://data.socialhistory.org/resource/imf_gdppc/provenance/769bcbf7/2017-02-28T14:05> ;
          np:hasPublicationInfo <http://data.socialhistory.org/resource/imf_gdppc/pubinfo/769bcbf7/2017-02-28T14:05> .

      <http://data.socialhistory.org/resource/imf_gdppc/assertion/769bcbf7/2017-02-28T14:05> a np:Assertion .

      <http://data.socialhistory.org/resource/imf_gdppc/provenance/769bcbf7/2017-02-28T14:05> a np:Provenance .

      <http://data.socialhistory.org/resource/imf_gdppc/pubinfo/769bcbf7/2017-02-28T14:05> a np:PublicationInfo .
  }

What does this mean?

* Everything in ``http://data.socialhistory.org/resource/imf_gdppc/provenance/769bcbf7/2017-02-28T14:05`` is the RDF representation of the CSVW JSON schema.
* Everything in ``http://data.socialhistory.org/resource/imf_gdppc/assertion/769bcbf7/2017-02-28T14:05`` is the RDF representation of the CSV file.

  Since the global ``aboutUrl`` is set to ``{_row}``, every row is represented in RDF as a resource with the base URI concatenated with the row number. The column names are used as predicates to relate the row resource to a string literal representation of the value of a cell in that row.

* The graph ``uuid:af2851b5-405f-484b-869f-9f119f4b796f`` is the default graph that contains the Nanopublication.


.. _the-schema:

The Schema
==========

The COW converter uses the CSWV standard syntax for defining mappings from CSV to RDF graphs. These mappings are all defined in the ``tableSchema`` dictionary. For a full reference of the things you can do, we refer to the `CSV on the Web (CSVW) <https://www.w3.org/ns/csvw>`_ specification and in particular to the document on `Generating RDF from Tabular Data on the Web <http://www.w3.org/TR/csv2rdf/>`_.

**Important**: COW does not purport to implement the full CSVW specification, nor has it been tested against the `official test suite <http://www.w3.org/2013/csvw/tests/>`_. In fact, COW extends and deviates from the CSVW specification in several important ways.

We document the most important differences in the section below, and give a :ref:`short overview <short-overview>` of how schemas can be defined.

Differences and Extensions
--------------------------

1. While CSVW allows only for simple references to values in a column using the curly-brackets syntax (e.g. ``{name}`` to refer to the value of the name column at the current row), COW interprets the strings containing these references in two ways:

  1. as `Python Format Strings <https://docs.python.org/2/library/string.html#formatstrings>`_, and
  2. as `Jinja2 Templates <http://jinja.pocoo.org>`_

  This allows for very elaborate operations on row contents (e.g. containing conditionals, loops, and string operations.) [#f3]_.

2. CSVW allows only to specify a single ``null`` value for a column; when the cell in that column is equal to the null value, it is ignored for RDF conversion. COW extends the CSVW treatment of ``null`` values in two ways:

  1. multiple potential ``null`` values for a column, expressed as a JSON list, and
  2. conditional on values in *another* column, as a JSON-LD list (using the ``@list`` keyword)

3. COW allows the use of ``csvw:collectionUrl`` and ``csvw:schemeUrl`` on column specifications. This will automatically cast the value for ``valueUrl`` to a ``skos:Concept``, and adds it to the collection or scheme respectively indicated by these urls using a ``skos:member`` or ``skos:inScheme`` predicate.

4. By default COW skips cells that are empty (as per the CSVW specification), setting the ``csvw:parseOnEmpty`` attribute to ``true`` overrides this setting. This is useful when an empty cell has a specific meaning.

5. Column specifications with a ``xsd:anyURI`` datatype are converted to proper URIs rather than Literals with the ``xsd:anyURI`` datatype. This allows for conditionally generating URIs across multiple namespaces using Jinja2 templates, see `issue #13 <https://github.com/CLARIAH/wp4-converters/issues/13>`_ .

6. Column specifications in COW should have a JSON-LD style ``@id`` attribute. This ensures that all predicates generated through the conversion are linked back to the RDF representation of the CSVW JSON schema that informed the conversion.

7. COW converts column names to valid Python dictionary keys. In general this means that spaces in column names will be replaced with underscores.

8. For convenience, COW uses a default set of namespaces, specified in the ``src/converter/namespaces.yaml`` file, that will be used to interpret namespace prefix use in the JSON schema. Any namespace prefixes defined in the JSON schema will override the default ones.

9. The COW CSVW schema builder creates identifieres for each column specification in the schema file itselfs. This allows us to trace back any triples generated to the column schema that informed the conversion to RDF.


.. _short-overview:

Short Overview
--------------

A very simple ``tableSchema`` may have the following structure::

  "tableSchema": {
    "aboutUrl": "{_row}",
    "primaryKey": "Rank",
    "columns": [
      {
       "@id": "http://example.com/resource/imf_gdppc.csv/column/Rank",
       "dc:description": "Rank",
       "datatype": "string",
       "name": "Rank"
      }
    ]
  }

For the conversion to RDF, only the ``aboutUrl`` and ``columns`` attributes are of importance.

``aboutUrl``
^^^^^^^^^^^^

The ``aboutUrl`` attribute defines a template for all URIs that occur in the *subject* position of triples generated by the converter. It may appear in the ``tableSchema`` or in one of the ``columns``.  If defined in the ``tableSchema``, it acts as a *global* template that may be overriden by individual columns.

We explain URL template expansion :ref:`here <template-expansion>`.

``columns``
^^^^^^^^^^^

The ``columns`` array defines a schema for each column, and any additional ``virtual`` columns. The distinction between the two is important, as non-virtual columns must actually be present in the CSV (schema compliance) while virtual columns only instruct the conversion to RDF.

In the schema above, we state that the column identifiable with the ``name`` ``Rank`` specifies a literal value, with the ``datatype`` of ``string`` (a shorthand for ``xsd:string``). The ``titles`` array gives a number of alternative

Column Attributes
^^^^^^^^^^^^^^^^^

Every column is a dictionary that may have the following attributes.

.. table:: Attributes usable in column specifications

   =====================  ===========
   Attribute              Explanation
   =====================  ===========
   ``name``               Specifies the column to which this column specification applies. If no ``propertyUrl`` is defined on the column, the value for ``name`` will be used to generate the URL for the *predicate* position of the triple generated.
   ``virtual``            If set to ``true``, the column specification is not taken into account when validating a CSV file against this schema.
   ``aboutUrl``           Overrides the *global* ``aboutUrl`` template defined for the schema. This template will be used to generate the *subject* URL of the triple.
   ``valueUrl``           If present, this template will be used to generate the *object* URL of the triple. Otherwise, the value for ``name`` is used to retrieve the value for that cell, to generate a URL.
   ``datatype``           Specifies that this column should result in a triple where the *object* is a ``Literal`` with the datatype specified here (for common XML Schema datatypes, it is possible to drop the ``xsd:`` prefix). The value of the literal is then the value of the cell in this row indicated by the value of ``name``. **Special case**: when the ``datatype`` is ``xsd:anyURI`` COW creates a URI rather than a literal value.
   ``csvw:value``         Specifies that this column should result in a triple where the *object* is a ``Literal`` with the default ``xsd:string`` datatype (unless otherwise specified in the ``datatype`` attribute). The literal value for this cell is determined by applying the ref::`template expansion <template-expansion>` rule to this row. Can only be used in ``virtual`` columns.
   ``csvw:parseOnEmpty``  When set to ``true``, specifies that this column should be processed even when the cell corresponding to this column in this row is empty.
   ``null``               Specifies that this template does not apply if the cell in this column in this row corresponds to the value specified here. Can take a single value (as per the CSVW spec) or an array of values.
   ``lang``               Specifies the language tag for the literal in the *object* position, but only if the ``datatype`` is set to be ``string``.
   ``collectionUrl``      Specifies that the ``valueUrl`` (or equivalent) should be of type ``skos:Concept`` and that it is a ``skos:member`` of the URL generated by applying the ``collectionUrl`` template.
   ``schemeUrl``          Specifies that the ``valueUrl`` (or equivalent) should be of type ``skos:Concept`` and that it is ``skos:inScheme`` the URL generated by applying the ``schemeUrl`` template.
   =====================  ===========

.. _template-expansion:

Template Expansion
^^^^^^^^^^^^^^^^^^

When a CSV file is processed, COW does this row by row in the file, producing a dictionary where key/value pairs correspond to column headers and the value of the cell. So for::

  Rank;Country;Int
  1;Qatar;131063

the first row becomes [#f5]_ ::

  row = {'Rank': 1, 'Country': 'Qatar', 'Int': 131063}

For each row, COW then applies each column definition in the ``columns`` array (i.e. not for each column in the CSV file).

The URL templates in the attributes ``aboutUrl``, ``propertyUrl``, ``valueUrl``, and the regular template in the ``csvw:value`` are used to generate URLs and Literal values from the values of the cells in a specific row.

The values for the URL templates that the parser receives are *interpreted as URLs*. This means that they are expanded relative to the ``@base`` URI of the CSVW JSON schema file, unless they are explicitly preceded by a defined namespace prefix.

The names of Jinja2 or Python formatting field names should correspond to the keys of the dictionary (i.e. to the column names). COW supports a special CSVW field name ``_row`` that inserts the row number. This means that our row now becomes::

  row = {'Rank': 1, 'Country': 'Qatar', 'Int': 131063, '_row': 1}

COW always first applies the Jinja2 template, and then the Python formatting.

For instance (assuming a ``@base`` of ``http://example.com/``), we define an ``aboutUrl`` with the special ``_row`` key as a Python string formatting field name, and ``Country`` as a Jinja2 field name::

  "aboutUrl": "{_row}/{{Country}}"

the JSON-LD parser interprets the value for ``aboutUrl`` as the following URI::

  "http://example.com/{_row}/{{Country}}"

we then apply the Jinja2 formatting (``Template("http://example.com/{_row}{{Country}}").render(**row)``)::

  "http://example.com/{_row}/Qatar"

followed by the Python formatting (``"http://example.com/{_row}/{{Country}}".format(**row)``)::

  "http://example.com/1/Qatar"

For ``csvw:value`` attributes this works similarly, with the exception that the JSON-LD parser will not interpret these fields as URIs::

  "csvw:value": "{_row}/{{Country}}"

is parsed as::

  "{_row}/{{Country}}"

This means that one can use Jinja2 conditional formatting on ``csvw:value`` atributes in combination with an ``xsd:anyURI`` value for ``datatype`` to generate custom URIs that do not fit within a defined namespace.

Jinja2 is a very expressive templating language. To give a small example, we could define a ``virtual`` column that allows us to specify whether a country is ``http://example.com/rich`` or ``http://example.com/poor`` depending on whether the GDP is over 100k.

Our virtual column may look as follows::

  {
    "virtual": "true",
    "aboutUrl": "{Country}"
    "propertyUrl": "rdf:type",
    "valueUrl": "{% if Int > 100000 %}rich{% else %}poor{% endif %}"
  }

This will produce, for Qatar and Singapore, the respective triples::

  <http://example.com/Qatar>     rdf:type <http://example.com/rich> .
  <http://example.com/Singapore> rdf:type <http://example.com/poor> .

FAQ: Frequently Asked Questions
==========================

What's the general structure of the resulting ``.csv-schema.json`` file?
    - block 1 contains information on the csv file such as delimiter and encoding
    - block 2 provides information on the licensing
    - block 3 provides information on the publisher (you)
    - block 4 contains the reference to the file, your base URI, language and short-hand uri definitions, and finally some provenance info, such as date first created
    - block 5 starts with ``tableSchema``. This is the section that you will want to focus on, as this is where you'll describe your variables in RDF. Note that the ``aboutUrl`` just under tableSchema is the default ``aboutUrl``.

After I build my file I get all kinds of ``@id`` rows. What should I do with those?
  The purpose of these rows is that they identify the schema instruction itself. This way we can explicitly refer generated RDF back to the part of the schema that produced it.

How can I expand the description of my variable in RDF?
  You can add information by adding a 'virtual block'. For example, suppose we started out with the block above, we could expand on it in the follow way::

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
    }

  If our base url would be ``http://example.com``, it would create a series of URI's representing all the different values (institutes) in the dataset, like so: ``http://example.com/institute/Institute4AwesomeResearch``, ``http://example.com/institute/StarWarsAcademy``, etc..

My variable contains web addresses (URLs). How can I have them as proper addresses rather than strings?
  Change the datatype to: ``xsd:anyURI``

Can I assign values conditionally, i.e. use an if-statement?
  Indeed you can. For example, HISCO codes ought to be 5 digits, but sometimes the first digit is a zero and then gets 'lost'. So we want to add that zero back, when HISCO has less than 5 digits. However, we don't want to add a zero, to the codes indicating missing HISCO's: (-1, -2 (and -3 in the Dutch Historical Sample version of HISCO)). Ergo::

    "aboutUrl": "hisco:{% if not HISCO in ['-1','-3','-2']%}{HISCO:0>5}{% else %}{HISCO}{% endif %}"

  Also see the section :ref:`common-jinja2`

What does ``ValueError: Expecting , delimiter: line 161 column 5 (char 5716)`` mean?
  This might happen when you use the csvw-tool to convert a dataset. It indicates that you probably forgot a comma (or other delimiter) in the line before.

What does ``ValueError:"No JSON object could be decoded"`` mean?
  In general it means that the Json schema is not syntactically valid. This could mean anything from missing commas, brackets, closing quotes, incorrect string quotes or invalid structure. E.g. this error occurs when your second to final `}` is followed by a comma.

When converting, I get the following error: ``"Exception: Could not find source file or necessary metadata file in path..."``
  It's likely your trying to convert the ``.csv-metadata.json`` file rather than the ``.csv`` file itself.

I've added a language tag using ``"lang": "whatever_language"``, but why doesn't show ``@whatever_language`` in the n-quads file?
  The ``"lang":`` part should be placed directly after the specification of the skos:pref/hidden/altLabel.

.. _common-jinja2:

Commonly used Template Formatting
----------------------------------------

* Leading zeroes: ``variable:{0>N}``, where ``N`` is the number of digits to fill up to.
* If-else statements: ``{% if conditional_variable=="something" %} value_if {% else %} value_else {% endif %}``.
* Convert to string and concatenate: ``{{variable ~ 'string'}}``, e.g. if variable has value "Hello" then the result would be "Hello string". Note the double braces.
* Arithmetic: use double braces and cast as numeric first, e.g. ``{{variable|float() * 1000}}``.
* Lowercase, uppercase, etc.: ``{{variable|lower()}}```. Note the double brace.
* String slices: ``{{variable[n:m]}}`` as described `here <https://docs.python.org/2/tutorial/introduction.html#strings>`_.

====


API Documentation
=================

* :doc:`code`


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
.. [#f5] Assuming that you have the proper locale settings that instructs Python to interpret the comma as a thousands separator.
