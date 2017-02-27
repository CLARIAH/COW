.. CSVW Converters documentation master file, created by
   sphinx-quickstart on Fri Nov 18 13:15:57 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

COW
===

This package contains a comprehensive utility package (COW [#f2]_) for batch conversion of multiple datasets expressed in CSV, including datasets mapped through the [QBer](https://github.com/CLARIAH/QBer) tool.

This documentation focuses on the first of these functionalities: using a JSON schema expressed using an extended version of the CSVW standard, to convert CSV files to RDF in scalable fashion.

`CSV on the Web (CSVW) <https://www.w3.org/ns/csvw>`_ is a W3C standard for metadata descriptions for tabular data. Typically, these data reside in CSV files. CSVW metadata is captured in ``.csv-metadata.json`` files that live alongside the CSV files that they describe. For instance, a CSV file called ``data.csv`` and its metadata ``data.csv-metadata.json`` would be hosted at::

  http://example.com/data.csv
  http://example.com/data.csv-metadata.json

Another feature of CSVW is that it allows the specification of a mapping (or interpretation) of values in the CSV in terms of RDF. The ``tableSchema`` element in CSVW files defines per column what its properties should be, but may also define custom mappings to e.g. URIs in RDF.

Interestingly, the JSON format used by CSVW metadata is an `extension of the JSON-LD specification <https://www.w3.org/TR/json-ld/>`_, a JSON-based serialization for Linked Data. As a consequence of this, the CSVW metadata can be directly attached (as provenance) to the RDF resulting from a CSVW-based conversion.

This is exactly what the CSVW Converters do.

Features & Limitations
^^^^^^^^^^^^^^^^^^^^^^

Compared to the CSVW specification, the converters have a number of limitations and extra features. These are:

1. The converters *do not* perform any schema checking, and ignore any and all parts of the `CSVW Specification <https://www.w3.org/ns/csvw>`_ that are not directly needed for the RDF conversion.

2. While CSVW allows only for simple references to values in a column using the curly-brackets syntax (e.g. ``{name}`` to refer to the value of the name column at the current row), COW interprets the strings containing these references in two ways:

  1. as `Python Format Strings <https://docs.python.org/2/library/string.html#formatstrings>`_, and
  2. as `Jinja2 Templates <http://jinja.pocoo.org>`_

  This allows for very elaborate operations on row contents (e.g. containing conditionals, loops, and string operations.) [#f3]_.

3. CSVW allows only to specify a single ``null`` value for a column; when the cell in that column is equal to the null value, it is ignored for RDF conversion. COW extends the CSVW treatment of ``null`` values in two ways:

  1. multiple potential ``null`` values for a column, expressed as a JSON list, and
  2. conditional on values in *another* column, as a JSON-LD list (using the ``@list`` keyword)

.. toctree::
  :maxdepth: 2

Installation
------------

Prerequisites
^^^^^^^^^^^^^

* Python 2.7 (installed on most systems)
* ``pip``
* ``virtualenv`` (simply `pip install virtualenv`) [#f1]_

Step by step instructions
^^^^^^^^^^^^^^^^^^^^^^^^^

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
-----

The primary command line script for CSVW-based conversion is the ``csvw-tool.py`` script. It can be used for two tasks:

1. Generating a skeleton CSVW JSON-Schema for a specific CSV file.
2. Using such a schema to convert a CSV file to RDF (in `NQuads format <https://www.w3.org/TR/n-quads/>`_)





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
.. [#f3] In the future we may enable the Jinja2 plugin mechanism that allows running custom Python functions as filters over values.
