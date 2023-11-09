#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import datetime
import json
import gzip
import logging
import iribaker
import traceback
import rfc3987
from chardet.universaldetector import UniversalDetector
import multiprocessing as mp
import unicodecsv as csv
import hashlib
from collections import OrderedDict
from jinja2 import Template
from .util import (patch_namespaces_to_disk, process_namespaces,
                   get_namespaces, Nanopublication, validateTerm,
                   parse_value, CSVW, PROV, DC, SKOS, RDF)
from rdflib import URIRef, Literal, Graph, BNode, XSD, Dataset
from rdflib.resource import Resource
from rdflib.collection import Collection
from functools import partial
from itertools import zip_longest
from functools import lru_cache
import io

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

rdfTermLogger = logging.getLogger('rdflib.term')
rdfTermLogger.setLevel(logging.ERROR) # It's too chatty with warnings

# Serialization extension dictionary
extensions = {'xml': 'xml', 'n3' : 'n3', 'turtle': 'ttl', 'nt' : 'nt',
              'pretty-xml' : 'xml', 'trix' : 'trix', 'trig' : 'trig',
              'nquads' : 'nq'}

UTF8 = 'utf-8'

def build_schema(infile, outfile, delimiter=None, quotechar='\"',
                 encoding=None, dataset_name=None,
                 base="https://example.com/id/"):
    
    """
    Build a CSVW schema based on the ``infile`` CSV file, and write the
    resulting JSON CSVW schema to ``outfile``.

    Takes various optional parameters for instructing the CSV reader, but
    is also quite good at guessing the right values.
    """

    url = os.path.basename(infile)
    # Get the current date and time (UTC)
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    if dataset_name is None:
        dataset_name = url

    if encoding is None:
        detector = UniversalDetector()
        with open(infile, 'rb') as f:
            for line in f:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        encoding = detector.result['encoding']
        logger.info("Detected encoding: {} ({} confidence)".format(detector.result['encoding'],
                                                                   detector.result['confidence']))

    if delimiter is None:
        with open(infile, 'r', errors='ignore') as csvfile:
            # dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=";,$\t")
            dialect = csv.Sniffer().sniff(csvfile.readline()) #read only the header instead of the entire file to determine delimiter
            csvfile.seek(0)
        logger.info("Detected dialect: {} (delimiter: '{}')".format(dialect, dialect.delimiter))
        delimiter = dialect.delimiter


    logger.info("Delimiter is: {}".format(delimiter))

    if base.endswith('/'):
        base = base[:-1]

    metadata = {
#        "@context": [ {"@language": "en",
#                       "@base": "{}/".format(base)},
#                     process_namespaces(base),
#                    "https://raw.githubusercontent.com/CLARIAH/COW/master/csvw.json"],
        "@context": ["https://raw.githubusercontent.com/CLARIAH/COW/master/csvw.json",
                     {"@language": "en",
                      "@base": "{}/".format(base)},
                     process_namespaces(base)],
        "tableSchema": {
            "aboutUrl": "{_row}",
            "primaryKey": None,
            "columns": []
        },       
        "url": url,
        "dialect": {"delimiter": delimiter,
                    "encoding": encoding,
                    "quoteChar": quotechar
                    },
        "dc:title": dataset_name,
        "dcat:keyword": [],
        "dc:publisher": {
            "schema:name": "CLARIAH Structured Data Hub - Datalegend",
            "schema:url": {"@id": "http://datalegend.net"}
        },
        "dc:license": {"@id": "http://opendefinition.org/licenses/cc-by/"},
        "dc:modified": {"@value": today, "@type": "xsd:date"},
        "@id": iribaker.to_iri("{}/{}".format(base, url))
    }

    with io.open(infile, 'rb') as infile_file:
        r = csv.reader(infile_file, delimiter=delimiter, quotechar=quotechar, encoding=encoding)

        header = next(r)

        logger.info("Found headers: {}".format(header))

        if '' in header:
            logger.warning("WARNING: You have one or more empty column headers in your CSV file. Conversion might produce incorrect results because of conflated URIs or worse")
        if len(set(header)) < len(header):
            logger.warning("WARNING: You have two or more column headers that are syntactically the same. Conversion might produce incorrect results because of conflated URIs or worse")

        # First column is primary key
        metadata['tableSchema']['primaryKey'] = header[0]

        for head in header:
            col = {
                "name": head,
                # "titles": [head],        # to reduce 'clutter' in the output
                # "dc:description": head,  # to reduce 'clutter in the output
                "datatype": "string",
                "@id": iribaker.to_iri("{}/{}/column/{}".format(base, url, head))
            }

            metadata['tableSchema']['columns'].append(col)

    with open(outfile, 'w') as outfile_file:
        outfile_file.write(json.dumps(metadata, indent=True))

    logger.info("Done")
    return


class Item(Resource):
    """Wrapper for the rdflib.resource.Resource class that allows getting property values from resources."""

    def __getattr__(self, p):
        """Returns the object for predicate p, either as a list (when multiple bindings exist), as an Item
           when only one object exists, or Null if there are no values for this predicate"""
        try:
            objects = list(self.objects(self._to_ref(*p.split('_', 1))))
        except:
            # logger.debug("Calling parent function for Item.__getattr__ ...") #removed for readability
            super().__getattr__(self, p)
            # raise Exception("Attribute {} does not specify namespace prefix/qname pair separated by an ".format(p) +
            #                 "underscore: e.g. `.csvw_tableSchema`")

        # If there is only one object, return it, otherwise return all objects.
        if len(objects) == 1:
            return objects[0]
        elif len(objects) == 0:
            return None
        else:
            return objects

    def _to_ref(self, pfx, name):
        """Concatenates the name with the expanded namespace prefix into a new URIRef"""
        return URIRef(self._graph.store.namespace(pfx) + name)


class CSVWConverter(object):
    """
    Converter configuration object for **CSVW**-style conversion. Is used to set parameters for a conversion,
    and to initiate an actual conversion process (implemented in :class:`BurstConverter`)

    Takes a dataset_description (in CSVW format) and prepares:

    * An array of dictionaries for the rows to pass to the :class:`BurstConverter` (either in one go, or in parallel)
    * A nanopublication structure for publishing the converted data (using :class:`converter.util.Nanopublication`)
    """

    def __init__(self, file_name, delimiter=',', quotechar='\"',
                 encoding=UTF8, processes=4, chunksize=5000,
                 output_format='nquads', base="https://example.com/id/",
                 gzipped=False):
        logger.info("Initializing converter for {}".format(file_name))
        self.file_name = file_name
        self.output_format = output_format
        self.gzipped = gzipped
        self.target_file = f"{self.file_name}.{extensions[self.output_format]}"
        schema_file_name = f"{file_name}-metadata.json"

        if self.gzipped:
            self.target_file = self.target_file + ".gz"

        if not os.path.exists(schema_file_name) or not os.path.exists(file_name):
            raise Exception(
                "Could not find source or metadata file in path; make sure you called with a .csv file")

        self._processes = processes
        self._chunksize = chunksize
        logger.info("Processes: {}".format(self._processes))
        logger.info("Chunksize: {}".format(self._chunksize))

        # Get @base from the metadata.json file
        with open(schema_file_name, 'r') as f:
            schema = json.load(f)
            self.base = schema['@context'][1]['@base']
            if self.base == None or self.base == "":
                self.base = base
            patch_namespaces_to_disk({
                'sdr' : str(self.base),
                'sdv' : str(self.base + 'vocab/')
            })

        self.np = Nanopublication(file_name)
        # self.metadata = json.load(open(schema_file_name, 'r'))
        self.metadata_graph = Graph()
        with open(schema_file_name, 'rb') as f:
            try:
                self.metadata_graph.load(f, format='json-ld')
            except ValueError as err:
                err.message = f"{err.message} ; please check the syntax of your JSON-LD schema file"
                raise
        # from pprint import pprint
        # pprint([term for term in sorted(self.metadata_graph)])

        # Get the URI of the schema specification by looking for the subject
        # with a csvw:url property.

        (self.metadata_uri, _) = next(self.metadata_graph.subject_objects(CSVW.url))


        self.metadata = Item(self.metadata_graph, self.metadata_uri)

        # Add a prov:wasDerivedFrom between the nanopublication assertion graph
        # and the metadata_uri
        self.np.pg.add((self.np.ag.identifier, PROV['wasDerivedFrom'], self.metadata_uri))
        # Add an attribution relation and dc:creator relation between the
        # nanopublication, the assertion graph and the authors of the schema
        for o in self.metadata_graph.objects(self.metadata_uri, DC['creator']):
            self.np.pg.add((self.np.ag.identifier, PROV['wasAttributedTo'], o))
            self.np.add((self.np.uri, PROV['wasAttributedTo'], o))
            self.np.pig.add((self.np.ag.identifier, DC['creator'], o))

        self.schema = self.metadata.csvw_tableSchema

        # Taking defaults from init arguments
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.encoding = encoding

        # Read csv-specific dialiect specification from JSON structure
        if self.metadata.csvw_dialect is not None:
            if self.metadata.csvw_dialect.csvw_delimiter is not None:
                self.delimiter = str(self.metadata.csvw_dialect.csvw_delimiter)

            if self.metadata.csvw_dialect.csvw_quotechar is not None:
                self.quotechar = str(self.metadata.csvw_dialect.csvw_quoteChar)

            if self.metadata.csvw_dialect.csvw_encoding is not None:
                self.encoding = str(self.metadata.csvw_dialect.csvw_encoding)

        logger.info("Quotechar: {}".format(self.quotechar.__repr__()))
        logger.info("Delimiter: {}".format(self.delimiter.__repr__()))
        logger.info("Encoding : {}".format(self.encoding.__repr__()))
        logger.warning(
            "Taking encoding, quotechar and delimiter specifications into account...")

        # All IRIs in the metadata_graph need to at least be valid, this validates them
        headersDict = {}
        with io.open(self.file_name, 'rb') as f:
            r = csv.reader(f, delimiter=self.delimiter, quotechar=self.quotechar, encoding=self.encoding)
            headers = next(r)
            headersDict = dict.fromkeys(headers)

            # e.g. {{_row + 42}}, TypeError checking done in validateTerm for {{_row + <not_an_int>}} combinations
            headersDict['_row'] = 0

        for s, p, o in self.metadata_graph:
            # We need to validate the terms on being valid IRIs, otherwise the conversion will break later on
            validateTerm(s, headersDict)
            validateTerm(p, headersDict)
            validateTerm(o, headersDict)

        # The metadata schema overrides the default namespace values
        # (NB: this does not affect the predefined Namespace objects!)
        # DEPRECATED
        # namespaces.update({ns: url for ns, url in self.metadata['@context'][1].items() if not ns.startswith('@')})

        # Cast the CSVW column rdf:List into an RDF collection
        #print(self.schema.csvw_column)
        # print(len(self.metadata_graph))

        # TODO: change this to Python 3 as the line below is for Python 2 but it doesn't seem easy to change
        # self.columns = Collection(self.metadata_graph, BNode(self.schema.csvw_column))
        # Python 3 can't work out Item so we'll just SPARQL the graph

        self.columns = [column_item.identifier for column_item in self.schema.csvw_column.items()]
        #
        # from pprint import pprint
        # pprint(self.columns)
        # print("LOOOOOOOOOOOOOOOOOOOOOOO")
        # from pprint import pprint
        # # pprint(self.schema.csvw_column)
        # pprint([term for term in self.schema])
        # pprint('----------')
        # pprint([term for term in self.schema.csvw_column])



    def convert_info(self):
        """Converts the CSVW JSON file to valid RDF for serializing into the Nanopublication publication info graph."""

        results = self.metadata_graph.query("""SELECT ?s ?p ?o
                                               WHERE { ?s ?p ?o .
                                                       FILTER(?p = csvw:valueUrl ||
                                                              ?p = csvw:propertyUrl ||
                                                              ?p = csvw:aboutUrl)}""")

        for (s, p, o) in results:
            # Use iribaker
            object_value = str(o)
            escaped_object = URIRef(iribaker.to_iri(object_value))
            # print(escaped_object)

            # If the escaped IRI of the object is different from the original,
            # update the graph.
            if escaped_object != o:
                self.metadata_graph.set((s, p, escaped_object))
                # Add the provenance of this operation.
                self.np.pg.add((escaped_object,
                            PROV.wasDerivedFrom,
                            Literal(object_value, datatype=XSD.string)))
                # print(str(o))

        #walk through the metadata graph to remove illigal "Resource" blank node caused by python3 transition.
        for s, p, o in self.metadata_graph.triples((None, None, None)):
            subject_value = str(s)
            if s.startswith("Resource("):
                self.metadata_graph.remove((s,p,o))
                self.metadata_graph.add((BNode(subject_value[9:-1]), p, o))
                logger.debug("removed a triple because it was not formatted right. (started with \"Resource\")")

        # Add the information of the schema file to the provenance graph of the
        # nanopublication
        self.np.ingest(self.metadata_graph, self.np.pg.identifier)

        # for s,p,o in self.np.triples((None,None,None)):
        #     print(s.__repr__,p.__repr__,o.__repr__)

        return

    def convert(self):
        """Starts a conversion process (in parallel or as a single process) as defined in the arguments passed to the :class:`CSVWConverter` initialization"""
        logger.info("Starting conversion")
        writer = gzip.open if self.gzipped else open

        with writer(self.target_file, 'wb') as target_file:
            with open(self.file_name, 'rb') as csvfile:
                logger.info("Opening CSV file for reading")
                reader = csv.DictReader(csvfile,
                                        encoding=self.encoding,
                                        delimiter=self.delimiter,
                                        quotechar=self.quotechar)

                # If single-threaded
                if self._processes == 1:
                    self._simple(reader, target_file)

                # If multi-threaded
                elif self._processes > 1:
                    try:
                        self._parallel(reader, target_file)
                    except TypeError:
                        logger.info("TypeError in multiprocessing... falling back to serial conversion")
                        self._simple(reader, target_file)
                    except Exception:
                        logger.error("Some exception occurred, falling back to serial conversion")
                        traceback.print_exc()
                        self._simple(reader, target_file)
                else:
                    logger.error("Incorrect process count specification")

    def _simple(self, reader, target_file):
        """Starts a single process for converting the file"""
        logger.info("Starting in a single process")
        c = BurstConverter(self.np.ag.identifier, self.columns,
                        self.schema, self.metadata_graph, self.encoding, self.output_format)

        # Out will contain an N-Quads serialized representation of the converted CSV
        out = c.process(0, reader, 1)
        target_file.write(out.encode())

        self.convert_info()
        target_file.write(self.np.serialize(format=self.output_format).encode())

    def _parallel(self, reader, target_file):
        """Starts parallel processes for converting the file. Each process will receive max ``chunksize`` number of rows"""
        pool = mp.Pool(processes=self._processes)
        logger.info(f"Running in {self._processes} processes")

        burstConvert_partial = partial(_burstConvert,
                                    identifier=self.np.ag.identifier,
                                    columns=self.columns,
                                    schema=self.schema,
                                    metadata_graph=self.metadata_graph,
                                    encoding=self.encoding,
                                    chunksize=self._chunksize,
                                    output_format=self.output_format)

        for out in pool.imap(burstConvert_partial, enumerate(grouper(self._chunksize, reader))):
            target_file.write(out.encode())

        pool.close()
        pool.join()

        self.convert_info()
        target_file.write(self.np.serialize(format=self.output_format).encode())


def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


# This has to be a global method for the parallelization to work.
def _burstConvert(enumerated_rows, identifier, columns, schema, metadata_graph, encoding, chunksize, output_format):
    """The method used as partial for the parallel processing initiated in :func:`_parallel`."""
    try:
        count, rows = enumerated_rows
        c = BurstConverter(identifier, columns, schema,
                           metadata_graph, encoding, output_format)

        logger.info("Process {}, nr {}, {} rows".format(
            mp.current_process().name, count, len(rows)))

        result = c.process(count, rows, chunksize)

        logger.info("Process {} done".format(mp.current_process().name))

        return result
    except:
        traceback.print_exc()


class BurstConverter(object):
    """The actual converter, that processes the chunk of lines from the CSV file, and uses the instructions from the ``schema`` graph to produce RDF."""

    def __init__(self, identifier, columns, schema, metadata_graph, encoding, output_format):
        self.ds = Dataset()
        # self.ds = apply_default_namespaces(Dataset())
        self.g = self.ds.graph(URIRef(identifier))

        self.columns = columns
        self.schema = schema
        self.metadata_graph = metadata_graph
        self.encoding = encoding
        self.output_format = output_format
        self.render_pattern_cache = LRUCache(1000)
        self.expandURL_cache = LRUCache(256)
        self.get_property_url_cache = LRUCache(10000)
        self.templates = {}

        self.aboutURLSchema = self.schema.csvw_aboutUrl

    def equal_to_null(self, nulls, row):
        """Determines whether a value in a cell matches a 'null' value as specified in the CSVW schema)"""
        for n in nulls:
            n = Item(self.metadata_graph, n)
            col = str(n.csvw_name)
            val = str(n.csvw_null)
            if row[col] == val:
                # logger.debug("Value of column {} ('{}') is equal to specified 'null' value: '{}'".format(col, unicode(row[col]).encode('utf-8'), val))
                # There is a match with null value
                return True
        # There is no match with null value
        return False
    def process(self, count, rows, chunksize):
        obs_count = count * chunksize

        mult_proc_counter = 0
        iter_error_counter = 0

        columns_data = [
            {
                'column_item': Item(self.metadata_graph, c),
                'csvw_name_str': str(Item(self.metadata_graph, c).csvw_name)
            }
            for c in self.columns
        ]

        for row in rows:
            if row is None:
                mult_proc_counter += 1
                continue

            row['_row'] = obs_count
            obs_count += 1
            count += 1

            default_subject = self.expandURL(self.aboutURLSchema, row)

            for column_data in columns_data:
                column_item = column_data['column_item']
                csvw_name_str = column_data['csvw_name_str']

                try:
                    value = row[csvw_name_str]

                    if self.isValueNull(value, column_item):
                        continue

                    elif isinstance(column_item.csvw_null, Item):
                        nulls = Collection(self.metadata_graph, BNode(column_item.csvw_null.identifier))
                        if self.equal_to_null(nulls, row):
                            continue

                except KeyError:
                    iter_error_counter += 1
                    if isinstance(column_item.csvw_null, Item):
                        nulls = Collection(self.metadata_graph, BNode(column_item.csvw_null.identifier))
                        if self.equal_to_null(nulls, row):
                            continue

                parsed_column_data = {
                    'csvw_virtual': parse_value(column_item.csvw_virtual),
                    'csvw_name': csvw_name_str,
                    'csvw_value': parse_value(column_item.csvw_value),
                    'csvw_about_url': parse_value(column_item.csvw_aboutUrl),
                    'csvw_value_url': parse_value(column_item.csvw_valueUrl),
                    'csvw_datatype': parse_value(column_item.csvw_datatype)
                }

                try:
                    s, p, o = self._process_column(row, default_subject, column_item, parsed_column_data)
                    self.g.add((s, p, o))

                    if '@id' in column_item:
                        self.g.add((p, PROV['wasDerivedFrom'], URIRef(column_item['@id'])))

                except Exception:
                    traceback.print_exc()

        logger.debug(f"{mult_proc_counter} row skips caused by multiprocessing...")
        logger.debug(f"{iter_error_counter} errors encountered while trying to iterate over a NoneType...")
        logger.info("... done")
        return self.ds.serialize(format=self.output_format)

    def _process_column(self, row, default_subject, column_item, parsed_column_data):
        """This is a helper method to process each column item."""

        csvw_virtual = parsed_column_data['csvw_virtual']
        csvw_name = parsed_column_data['csvw_name']
        csvw_value = parsed_column_data['csvw_value']
        csvw_about_url = parsed_column_data['csvw_about_url']
        csvw_value_url = parsed_column_data['csvw_value_url']
        csvw_datatype = parsed_column_data['csvw_datatype']

        if csvw_about_url is not None:
            s = self.expandURL(csvw_about_url, row)
        else:
            s = default_subject

        p = self.get_property_url(column_item.csvw_propertyUrl, csvw_name, row)

        # Object property logic
        if csvw_value_url is not None:
            o = self.expandURL(csvw_value_url, row)
            object_value = str(o)
            if self.isValueNull(os.path.basename(object_value), column_item):
                return s, p, None

            if csvw_virtual == 'true' and csvw_datatype:
                if URIRef(csvw_datatype) == XSD.anyURI:
                    value = row[csvw_name]
                    o = URIRef(iribaker.to_iri(value))

                if URIRef(csvw_datatype) == XSD.linkURI:
                    csvw_about_url = self._extract_between_braces(csvw_about_url)
                    s = self.expandURL(csvw_about_url, row)
                    csvw_value_url = self._extract_between_braces(csvw_value_url)
                    o = self.expandURL(csvw_value_url, row)

            if column_item.csvw_collectionUrl is not None:
                self._handle_collection_url(column_item, o, row)

            if column_item.csvw_schemeUrl is not None:
                self._handle_scheme_url(column_item, o, row)

        else:
            value = self._determine_value(row, column_item, csvw_value, csvw_name)
            o = self._determine_object(value, csvw_datatype, column_item.csvw_lang, row)

        return s, p, o

    def _determine_value(self, row, column_item, csvw_value, csvw_name):
        if csvw_value is not None:
            return self.render_pattern(csvw_value, row)
        elif csvw_name is not None:
            return row[csvw_name]
        else:
            raise Exception("No 'name' or 'csvw:value' attribute found for this column specification")

    def _determine_object(self, value, csvw_datatype, csvw_lang, row):
        if csvw_datatype is not None:
            if URIRef(csvw_datatype) == XSD.anyURI:
                return URIRef(iribaker.to_iri(value))
            elif URIRef(csvw_datatype) == XSD.string and csvw_lang is not None:
                return Literal(value, lang=self.render_pattern(csvw_lang, row))
            else:
                return Literal(value, datatype=csvw_datatype, normalize=False)
        return Literal(value)

    def _extract_between_braces(self, value):
        return value[value.find("{"):value.find("}")+1]

    def _handle_collection_url(self, column_item, o, row):
        collection = self.expandURL(column_item.csvw_collectionUrl, row)
        self.g.add((collection, RDF.type, SKOS['Collection']))
        self.g.add((o, RDF.type, SKOS['Concept']))
        self.g.add((collection, SKOS['member'], o))

    def _handle_scheme_url(self, column_item, o, row):
        scheme = self.expandURL(column_item.csvw_schemeUrl, row)
        self.g.add((scheme, RDF.type, SKOS['Scheme']))
        self.g.add((o, RDF.type, SKOS['Concept']))
        self.g.add((o, SKOS['inScheme'], scheme))

#    def process(self, count, rows, chunksize):
#        """Process the rows fed to the converter. Count and chunksize are used to determine the
#        current row number (needed for default observation identifiers)"""
#
#        obs_count = count * chunksize
#
#        # logger.info("Row: {}".format(obs_count)) #removed for readability
#
#        # We iterate row by row, and then column by column, as given by the CSVW mapping file.
#        mult_proc_counter = 0
#        iter_error_counter= 0
#        for row in rows:
#            # This fixes issue:10
#            if row is None:
#                mult_proc_counter += 1
#                # logger.debug( #removed for readability
#                #     "Skipping empty row caused by multiprocessing (multiple of chunksize exceeds number of rows in file)...")
#                continue
#
#            # set the '_row' value in case we need to generate 'default' URIs for each observation ()
#            # logger.debug("row: {}".format(obs_count)) #removed for readability
#            row['_row'] = obs_count
#            count += 1
#
#            # print(row)
#
#            # The self.columns dictionary gives the mapping definition per column in the 'columns'
#            # array of the CSVW tableSchema definition.
#
#            default_subject = self.expandURL(self.aboutURLSchema, row)
#
#            for c in self.columns:
#                s = None
#                c = Item(self.metadata_graph, c)
#
#                try:
#                    # Can also be used to prevent the triggering of virtual
#                    # columns!
#
#                    # Get the raw value from the cell in the CSV file
#                    value = row[str(c.csvw_name)]
#
#                    # This checks whether we should continue parsing this cell, or skip it.
#                    if self.isValueNull(value, c):
#                        continue
#
#                    # If the null values are specified in an array, we need to parse it as a collection (list)
#                    elif isinstance(c.csvw_null, Item):
#                        nulls = Collection(self.metadata_graph, BNode(c.csvw_null.identifier))
#
#                        if self.equal_to_null(nulls, row):
#                            # Continue to next column specification in this row, if the value is equal to (one of) the null values.
#                            continue
#                except:
#                    # No column name specified (virtual) because there clearly was no c.csvw_name key in the row.
#                    # logger.debug(traceback.format_exc()) #removed for readability
#                    iter_error_counter +=1
#                    if isinstance(c.csvw_null, Item):
#                        nulls = Collection(self.metadata_graph, BNode(c.csvw_null.identifier))
#                        if self.equal_to_null(nulls, row):
#                            # Continue to next column specification in this row, if the value is equal to (one of) the null values.
#                            continue
#
#                try:
#                    # This overrides the subject resource 's' that has been created earlier based on the
#                    # schema wide aboutURLSchema specification.
#
#                    #TODO: set your environment correctly
#                    csvw_virtual = parse_value(c.csvw_virtual)
#                    csvw_name = parse_value(c.csvw_name)
#                    csvw_value = parse_value(c.csvw_value)
#                    csvw_about_url = parse_value(c.csvw_aboutUrl)
#                    csvw_value_url = parse_value(c.csvw_valueUrl)
#                    csvw_datatype = parse_value(c.csvw_datatype)
#
#                    if csvw_about_url is not None:
#                        s = self.expandURL(csvw_about_url, row)
#
#                    p = self.get_property_url(c.csvw_propertyUrl, csvw_name, row)
#
#                    if csvw_value_url is not None:
#                        # This is an object property, because the value needs to be cast to a URL
#                        o = self.expandURL(csvw_value_url, row)
#                        object_value = str(o)
#                        if self.isValueNull(os.path.basename(object_value), c):
#                            logger.debug("skipping empty value")
#                            continue
#
#                        if csvw_virtual == 'true' and csvw_datatype is not None: 
#                            
#                            if URIRef(csvw_datatype) == XSD.anyURI:
#                                # Special case: this is a virtual column with object values that are URIs
#                                # For now using a test special property
#                                value = row[csvw_name]
#                                o = URIRef(iribaker.to_iri(value))
#
#                            if URIRef(csvw_datatype) == XSD.linkURI:
#                                csvw_about_url = csvw_about_url[csvw_about_url.find("{"):csvw_about_url.find("}")+1]
#                                s = self.expandURL(csvw_about_url, row)
#                                # logger.debug("s: {}".format(s))
#                                csvw_value_url = csvw_value_url[csvw_value_url.find("{"):csvw_value_url.find("}")+1]
#                                o = self.expandURL(csvw_value_url, row)
#                                # logger.debug("o: {}".format(o))
#
#                        # For coded properties, the collectionUrl can be used to indicate that the
#                        # value URL is a concept and a member of a SKOS Collection with that URL.
#                        if c.csvw_collectionUrl is not None:
#                            collection = self.expandURL(c.csvw_collectionUrl, row)
#                            self.g.add((collection, RDF.type, SKOS['Collection']))
#                            self.g.add((o, RDF.type, SKOS['Concept']))
#                            self.g.add((collection, SKOS['member'], o))
#
#                        # For coded properties, the schemeUrl can be used to indicate that the
#                        # value URL is a concept and a member of a SKOS Scheme with that URL.
#                        if c.csvw_schemeUrl is not None:
#                            scheme = self.expandURL(c.csvw_schemeUrl, row)
#                            self.g.add((scheme, RDF.type, SKOS['Scheme']))
#                            self.g.add((o, RDF.type, SKOS['Concept']))
#                            self.g.add((o, SKOS['inScheme'], scheme))
#                    else:
#                        # This is a datatype property
#                        if csvw_value is not None:
#                            value = self.render_pattern(csvw_value, row)
#                        elif csvw_name is not None:
#                            # print s
#                            # print c.csvw_name, self.encoding
#                            # print row[unicode(c.csvw_name)], type(row[unicode(c.csvw_name)])
#                            # print row[unicode(c.csvw_name)].encode('utf-8')
#                            # print '...'
#                            value = row[csvw_name]
#                        else:
#                            raise Exception("No 'name' or 'csvw:value' attribute found for this column specification")
#
#                        p = self.get_property_url(c.csvw_propertyUrl, csvw_name, row)
#
#                        if csvw_datatype is not None:
#                            if URIRef(csvw_datatype) == XSD.anyURI:
#                                # The xsd:anyURI datatype will be cast to a proper IRI resource.
#                                o = URIRef(iribaker.to_iri(value))
#                            elif URIRef(csvw_datatype) == XSD.string and c.csvw_lang is not None:
#                                # If it is a string datatype that has a language, we turn it into a
#                                # language tagged literal
#                                # We also render the lang value in case it is a
#                                # pattern.
#                                o = Literal(value, lang=self.render_pattern(
#                                    c.csvw_lang, row))
#                            else:
#                                # csvw_datatype = str(c.csvw_datatype)
#                                # print(type(csvw_datatype))
#                                # print(csvw_datatype)
#                                o = Literal(value, datatype=csvw_datatype, normalize=False)
#                        else:
#                            # It's just a plain literal without datatype.
#                            o = Literal(value)
#
#
#                    # Add the triple to the assertion graph
#                    s = s if s else default_subject
#                    self.g.add((s, p, o))
#
#                    # Add provenance relating the propertyUrl to the column id
#                    if '@id' in c:
#                        self.g.add((p, PROV['wasDerivedFrom'], URIRef(c['@id'])))
#
#                except:
#                    # print row[0], value
#                    traceback.print_exc()
#
#            # We increment the observation (row number) with one
#            obs_count += 1
#
#        # for s,p,o in self.g.triples((None,None,None)):
#        #     print(s.__repr__,p.__repr__,o.__repr__)
#
#        logger.debug(
#            "{} row skips caused by multiprocessing (multiple of chunksize exceeds number of rows in file)...".format(mult_proc_counter))
#        logger.debug(
#            "{} errors encountered while trying to iterate over a NoneType...".format(mult_proc_counter))
#        logger.info("... done")
#        return self.ds.serialize(format=self.output_format)
#
#    # def serialize(self):
#    #     trig_file_name = self.file_name + '.trig'
#    #     logger.info("Starting serialization to {}".format(trig_file_name))
#    #
#    #     with open(trig_file_name, 'w') as f:
#    #         self.np.serialize(f, format='trig')
#    #     logger.info("... done")
##        self.render_pattern_cache = {}
##        self.expandURL_cache = {}
##        self.get_property_url_cache = {}
    
    def render_pattern(self, pattern, row):
        """Takes a Jinja or Python formatted string, and applies it to the row value"""
        # Significant speedup by not re-instantiating Jinja templates for every
        # row.
        row_key = frozenset(row.items())
        cache_key = (pattern,row_key)
        cache_value = self.render_pattern_cache.get(cache_key)
        if cache_value:
            return cache_value
        
        if pattern in self.templates:
            template = self.templates[pattern]
        else:
            template = self.templates[pattern] = Template(pattern)

        # TODO This should take into account the special CSVW instructions such as {_row}
        # First we interpret the url_pattern as a Jinja2 template, and pass all
        # column/value pairs as arguments
        # row = {str('Int'): int('104906'), str('Country'): str('Luxembourg'), str('_row'): 1, str('Rank'): str('2')}

        # print(pattern)
        # print(type(pattern))
        # print(row)
        # print(type(row))
        # rendered_template = template.render(Int=120000)

        rendered_template = template.render(**row)

        try:
            # We then format the resulting string using the standard Python2
            # expressions
            result = rendered_template.format(**row)
        except:
            logger.warning(
                "Could not apply python string formatting, probably due to mismatched curly brackets. IRI will be '{}'. ".format(rendered_template))
            result = rendered_template.format(**row)
        
        self.render_pattern_cache.put(cache_key,result)
        return result

    def get_property_url(self, csvw_propertyUrl, csvw_name, row):
        # If propertyUrl is specified, use it, otherwise use the column name

        row_key = frozenset(row.items())
        cache_key = (csvw_propertyUrl, csvw_name, row_key)
        cache_value = self.get_property_url_cache.get(cache_key)
        if cache_value:
            return cache_value
        
        p = None
        propertyUrl = None
        if csvw_propertyUrl is not None:
            p = self.expandURL(csvw_propertyUrl, row)
        else:
            if "" in self.metadata_graph.namespaces():
                propertyUrl = self.metadata_graph.namespaces()[""][
                    csvw_name]
            else:
                propertyUrl = "{}{}".format(get_namespaces()['sdv'],
                                            csvw_name)
            p = self.expandURL(propertyUrl, row)

        self.get_property_url_cache.put(cache_key,p)
        return p
    

    def expandURL(self, url_pattern, row, datatype=False):
        """Takes a Jinja or Python formatted string, applies it to the row values, and returns it as a URIRef"""
        unicode_url_pattern = parse_value(url_pattern)
        row_key = frozenset(row.items())
        cache_key = (url_pattern, row_key)
        cache_value = self.expandURL_cache.get(cache_key)
        if cache_value:
            return cache_value

        url = self.render_pattern(unicode_url_pattern, row)
        try:
            iri = iribaker.to_iri(url)
            rfc3987.parse(iri, rule='IRI')
        except: 
            raise Exception("Cannot convert `{}` to valid IRI".format(url))
        iri = URIRef(iri)
        self.expandURL_cache.put(cache_key,iri)
        return iri
    
    def isValueNull(self, value, c):
        """This checks whether we should continue parsing this cell, or skip it because it is empty or a null value."""
        try:
            if len(value) == 0 and str(c.csvw_parseOnEmpty) == "true":
                # print("Not skipping empty value")
                return False #because it should not be skipped
            elif len(value) == 0 or value == parse_value(c.csvw_null) or value in [parse_value(n) for n in c.csvw_null] or value == parse_value(self.schema.csvw_null):
                # Skip value if length is zero and equal to (one of) the null value(s)
                # logger.debug(
                #     "Length is 0 or value is equal to specified 'null' value")
                return True
        except:
            # logger.debug("null does not exist or is not a list.") #this line will print for every cell in a csv without a defined null value.
            pass
        return False

#Least Recently used Cache    
class LRUCache:

    def __init__(self,capacity = 256):
        self.capacity = capacity
        self.data = OrderedDict()
        self.key_set = set()


#Gets the data the cache
    def get(self,key):
        if key in self.key_set:
            value = self.data.pop(key)
            self.data[key] = value
            return value
        return None
#adding the data to cache
    def put(self,key,value):
        if key in self.key_set:
            self.data.pop(key)
        elif len(self.data) >= self.capacity:
            self.key_set.remove(next(iter(self.data)))
            self.data.popitem(last=False)
        self.data[key] = value
        self.key_set.add(key)

