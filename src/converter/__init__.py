import os
from os import listdir
from os.path import isfile, join
import csv
import logging
import multiprocessing as mp
import uuid
import mappings
import datetime
import json
from iribaker import to_iri
from functools import partial
from itertools import izip_longest

from rdflib import Graph, Dataset, URIRef, Literal

from util import Nanopublication, Profile, DatastructureDefinition, apply_default_namespaces, QB, RDF, XSD, SDV, SDR, PROV

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return izip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


def convert(infile, outfile, delimiter=',', quotechar='\"', dataset_name=None, processes=4, chunksize=1000, config={}):
    if dataset_name is None:
        dataset_name = os.path.basename(infile).rstrip('.csv')

    if processes > 1:
        logger.info("Using " + str(processes) + " parallel processes")
        parallel_convert(infile, outfile, delimiter, quotechar, dataset_name, processes, chunksize, config)
    else:
        logger.info("Using a single process")
        simple_convert(infile, outfile, delimiter, quotechar, dataset_name, config)
    logger.info("Done")

    return


def simple_convert(infile, outfile, delimiter, quotechar, dataset_name, config):
    with open(outfile, 'w') as outfile_file:
        with open(infile, 'r') as infile_file:
            r = csv.reader(infile_file,
                           delimiter=delimiter,
                           quotechar=quotechar,
                           strict=True)

            headers = r.next()

            c = BurstConverter(dataset_name, headers, config)
            c.g.add((c._dataset_uri, RDF.type, QB['DataSet']))
            outfile_file.write(c.g.serialize(format='nt'))

            result = c.process(0, r, 1)

            outfile_file.write(result)


def parallel_convert(infile, outfile, delimiter, quotechar, dataset_name, processes, chunksize, config):
    with open(outfile, 'w') as outfile_file:
        with open(infile, 'r') as infile_file:
            pool = mp.Pool(processes=processes)

            r = csv.reader(infile_file,
                           delimiter=delimiter,
                           quotechar=quotechar,
                           strict=True)

            headers = r.next()

            c = BurstConverter(dataset_name, headers, config)
            c.g.add((c._dataset_uri, RDF.type, QB['DataSet']))
            outfile_file.write(c.g.serialize(format='nt'))

            convert_rows_partial = partial(convert_rows,
                                           dataset_name=dataset_name,
                                           headers=headers,
                                           chunksize=chunksize,
                                           config=config)

            for out in pool.imap(convert_rows_partial,
                                 enumerate(grouper(chunksize, r))):
                outfile_file.write(out)

            pool.close()
            pool.join()


def convert_rows(enumerated_rows, dataset_name, headers, chunksize, config):
    count, rows = enumerated_rows
    c = BurstConverter(dataset_name, headers, config)
    print mp.current_process().name, count, len(rows)
    result = c.process(count, rows, chunksize)
    print mp.current_process().name, 'done'
    return result


class Converter(object):

    def __init__(self, dataset, author_profile, target='output.nq'):
        """
        Takes a dataset_description (currently in QBer format) and prepares:
        * A dictionary for the BurstConverter (either in one go, or in parallel)
        * A nanopublication structure for publishing the converted data
        """

        # Defaults
        self._processes = 4          # Use 4 separate processes by default for converting CSV files
        self._chunksize = 1000       # Feed each process with 1000 lines at a time
        self._delimiter = ','        # Comma is the default delimiter
        self._quotechar = '\"'       # The double parenthesis is the default quoting character

        self._source = dataset['file']
        self._target = target

        self._dataset = dataset

        self.dataset_name = dataset['name']
        self.dataset_uri = URIRef(dataset['uri'])

        # For efficiency, convert the QBer-style value lists into dictionaries
        self._variables = {}
        for variable, variable_definition in dataset['variables'].items():
            self._variables[variable] = variable_definition
            self._variables[variable]['values_dictionary'] = dict([(unicode(v['label']), v) for v in variable_definition['values']])

        # Initialize the nanopublication structure
        self.publication = Nanopublication(self._source)

        # Build profile information from the author profile provided
        self.addProfile(author_profile)

        # Build a datastructure definition based on the dataset description
        self.addDatastructureDefinition()

    def setDelimiter(self, delimiter):
        self._delimiter = delimiter

    def setQuotechar(self, quotechar):
        self._quotechar = quotechar

    def setProcesses(self, processes):
        self._processes = processes

    def setChunksize(self, chunksize):
        self._chunksize = chunksize

    def setTarget(self, target):
        self._target = target

    def addProfile(self, author_profile):
        print "Adding profile"
        # We add all triples from a Profile graph to the default graph of the nanopublication
        profile_graph = Profile(author_profile)
        self.publication.ingest(profile_graph)
        # We add an attribution relation between the nanopub assertion and the Profile author
        self.publication.pg.add((self.publication.ag.identifier, PROV['wasAttributedTo'], profile_graph.author_uri))
        self.publication.pig.add((self.publication.uri, PROV['wasAttributedTo'], profile_graph.author_uri))

    def addDatastructureDefinition(self):
        print "Adding datastructure definition"
        # We add all triples from a DatastructureDefinition graph to the assertion graph of the nanopublication
        self.publication.ingest(DatastructureDefinition(self.dataset_uri, self.dataset_name, self._variables), self.publication.ag.identifier)

        # We link the dataset URI in the Provenance graph to the version of the dataset that was used in the conversion.
        self.publication.pg.add((self.dataset_uri, PROV['wasDerivedFrom'], self.publication.dataset_version_uri))

    def convert(self):
        logger.info("Using {} processes".format(self._processes))

        # Open the target file
        with open(self._target, 'w') as target_file:
            # Write the nanopublication structure to the target file
            target_file.write(self.publication.serialize(format='nquads'))

            # Open the source file
            with open(self._source, 'r') as source_file:
                # Open the source file for reading as CSV
                reader = csv.reader(source_file,
                                    delimiter=self._delimiter,
                                    quotechar=self._quotechar,
                                    strict=True)

                # The headers are the first line (should correspond to variables)
                headers = reader.next()

                # TODO: Add check that headers and variables actually match!

                if self._processes > 1:
                    self._parallel(reader, headers, target_file)
                else:
                    self._simple(reader, headers, target_file)

    def _simple(self, reader, headers, target_file):
        # Initialize the BurstConverter with the dataset and headers
        c = BurstConverter(self.publication.ag.identifier, self._dataset, self._variables, headers)
        # Out will contain an N-Quads serialized representation of the converted CSV
        out = c.process(0, reader, 1)
        # We then write it to the file
        target_file.write(out)

    def _parallel(self, reader, headers, target_file):
        # Initialize a pool of processes (default=4)
        pool = mp.Pool(processes=self._processes)

        # The _burstConvert function is partially instantiated, and will be successively called with
        # chunksize rows from the CSV file
        burstConvert_partial = partial(_burstConvert,
                                       graph_identifier=self.publication.ag.identifier,
                                       dataset=self._dataset,
                                       variables=self._variables,
                                       headers=headers,
                                       chunksize=self._chunksize)

        # The result of each chunksize run will be written to the target file
        for out in pool.imap(burstConvert_partial,
                             enumerate(grouper(self._chunksize, reader))):
            target_file.write(out)

        # Make sure to close and join the pool once finished.
        pool.close()
        pool.join()


# This has to be a global method for the parallelization to work.
def _burstConvert(enumerated_rows, graph_identifier, dataset, variables, headers, chunksize):
    count, rows = enumerated_rows
    c = BurstConverter(graph_identifier, dataset, variables, headers)

    print mp.current_process().name, count, len(rows)

    result = c.process(count, rows, chunksize)

    print mp.current_process().name, 'done'

    return result



class BurstConverter(object):

    _VOCAB_BASE = str(SDV)
    _RESOURCE_BASE = str(SDR)

    def __init__(self, graph_identifier, dataset, variables, headers):
        self._headers = headers
        self._variables = variables

        # TODO: Family is now superseded by a full dataset description in the form of QBer

        # if 'family' in config:
        #     self._family = config['family']
        #     try:
        #         family_def = getattr(mappings, config['family'])
        #         self._nocode = family_def['nocode']
        #         self._integer = family_def['integer']
        #         self._mappings = family_def['mappings']
        #     except:
        #         logger.warning('No family definition found')
        #         self._nocode = []
        #         self._integer = []
        #         self._mappings = {}
        # else:
        #     self._family = None

        # TODO: number_observations is now superseded by a full dataset description in the form of QBer

        # if 'number_observations' in config:
        #     self._number_observations = config['number_observations']
        # else:
        #     self._number_observations = None

        # TODO: stop is now superseded by a full dataset description in the form of QBer
        # self._stop = config['stop']

        # TODO: Now setting these as simple defaults
        self._family = None
        self._number_observations = True
        self._stop = None

        # TODO: Think of what to do here...
        if self._family is None:
            self._VOCAB_URI_PATTERN = "{0}{{}}/{{}}".format(self._VOCAB_BASE)
            self._RESOURCE_URI_PATTERN = "{0}{{}}/{{}}".format(self._RESOURCE_BASE)
        else:
            self._VOCAB_URI_PATTERN = "{0}{1}/{{}}/{{}}".format(self._VOCAB_BASE, self._family)
            self._RESOURCE_URI_PATTERN = "{0}{1}/{{}}/{{}}".format(self._RESOURCE_BASE, self._family)

        self.ds = apply_default_namespaces(Dataset())
        self.g = self.ds.graph(URIRef(graph_identifier))

        self._dataset_name = dataset['name']
        self._dataset_uri = URIRef(dataset['uri'])

    def process(self, count, rows, chunksize):
        obs_count = count * chunksize
        for row in rows:
            # rows may be filled with None values (because of the izip_longest function)
            if row is None:
                continue

            if self._number_observations:
                observation_uri = self.resource('observation/{}'.format(self._dataset_name), obs_count)
            else:
                observation_uri = self.resource('observation/{}'.format(self._dataset_name), uuid.uuid4())

            self.g.add((observation_uri, QB['dataSet'], self._dataset_uri))

            index = 0
            for col in row:
                variable = self._headers[index]
                col = col.decode('utf-8')

                if len(col) < 1:
                    index += 1
                    logger.debug('Col length < 1 (no value)')
                    continue
                # TODO: This applies a lambda function in the old version... but this is not currently
                #       supported.
                # elif variable in self._mappings:
                #     value = self._mappings[variable](col)
                elif variable in self._variables:
                    # The header string is indeed a variable (As it should be)

                    # What type of variable are we dealing with?
                    category = self._variables[variable]['category']

                    # The variable_uri is the URI specified in the variable definition
                    variable_uri = URIRef(self._variables[variable]['uri'])

                    # The original_variable_uri is the URI specified in the variable definition
                    original_variable_uri = URIRef(self._variables[variable]['original']['uri'])

                    try:
                        if col == "NA" or col == "N/A":
                            # Not a value... perhaps map this onto a default 'NA' uri?

                            # We take the default NA uri
                            value = SDR['NA']
                            # Add it to the graph
                            self.g.add((observation_uri, variable_uri, value))

                            # TODO: Add a flag to choose to preserve the original value or not.
                            # We take the original value from the CSV itself (not from the variable definition, as it often does not exist)
                            original_value = col
                            # Add it to the graph
                            self.g.add((observation_uri, original_variable_uri, Literal(original_value)))

                        elif category == "other":
                            # The variable is a literal
                            # TODO: Distinguish between different datatypes

                            # We take the 'label' (i.e. the potentially mapped value) from the
                            # corresponding value of the variable
                            value = self._variables[variable]['values_dictionary'][col]['label']

                            if 'datatype' in self._variables[variable]:
                                datatype = self._variables[variable]['datatype']
                                # If a datatype is specified, we use it to create the literal value
                                self.g.add((observation_uri, variable_uri, Literal(value, datatype=URIRef(datatype))))
                            else :
                                # Simply add the value to the graph without datatype
                                self.g.add((observation_uri, variable_uri, Literal(value)))

                            # TODO: Add a flag to choose to preserve the original value or not.
                            # We take the original 'label' from the corresponding value of the variable
                            original_value = self._variables[variable]['values_dictionary'][col]['original']['label']
                            # Add it to the graph
                            self.g.add((observation_uri, original_variable_uri, Literal(original_value)))

                        elif category == "coded" or category == "identifier":
                            # The variable is a URI

                            # We take the 'uri' (i.e. the potentially mapped value) from the
                            # corresponding value of the variable

                            value = self._variables[variable]['values_dictionary'][col]['uri']
                            self.g.add((observation_uri, variable_uri, URIRef(value)))

                            # TODO: Add a flag to choose to preserve the original value or not.
                            # We take the original 'uri' from the corresponding value of the variable
                            original_value = self._variables[variable]['values_dictionary'][col]['original']['uri']
                            # Add it to the graph
                            self.g.add((observation_uri, original_variable_uri, URIRef(original_value)))

                    except KeyError as ke:
                        print "Value found for variable {} does not exist in dataset description".format(variable)
                        print col
                elif variable == '':
                    # print "Empty variable name"
                    pass
                else:
                    print "Could not find '{}' in defined variables, ignoring".format(variable)

                index += 1

            obs_count += 1
            # if stop is not None and obs_count == stop:
            #     logger.info("Stopping at {}".format(obs_count))
            #     break

        # TODO: This ran inline SPARQL update queries. Need to reintegrate this with the current process.
        #
        # files = [f for f in listdir("update-queries/") if os.path.isfile(os.path.join("update-queries/", f))]
        # for f in files:
        #     if self._family in f and f.endswith("rq"):
        #         query = file("update-queries/" + f).read()
        #         self.g.update(query)

        return self.ds.serialize(format='nquads')

    def resource(self, resource_type, resource_name):
        raw_iri = self._RESOURCE_URI_PATTERN.format(resource_type, resource_name)
        iri = to_iri(raw_iri)

        return URIRef(iri)

    def vocab(self, concept_type, concept_name):
        raw_iri = self._VOCAB_URI_PATTERN.format(concept_type, concept_name)
        iri = to_iri(raw_iri)

        return URIRef(iri)
