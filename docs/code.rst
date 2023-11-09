Documentation for the Code
**************************

.. .. automodule:: csvw-tool
..    :members:


The ``converter`` package
=========================

This package focuses on QBer-style conversions. In other words, the instructions are a JSON datastructure that
either specifies mappings for each potential value in the CSV file, or generates a standard URI or Literal value.

The resulting RDF is always a Nanopublication with a DataCube datastructure definition and dataset containing the converted data.

.. automodule:: converter
   :members:

The ``converter.csvw`` module
=============================

.. automodule:: converter.csvw
   :members:

The ``converter.util`` package
==============================

.. automodule:: converter.util
   :members:

.. .. autoclass:: converter.csvw.CSVWConverter
..    :members:
