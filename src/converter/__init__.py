import os
from os import listdir
from os.path import isfile, join
import csv
import logging
import multiprocessing as mp
import uuid
import mappings
from iribaker import to_iri
from functools import partial
from itertools import izip_longest

from rdflib import Graph, Namespace, URIRef, RDF, Literal, XSD

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


SDH = Namespace("http://data.socialhistory.org/resource/")
QB = Namespace("http://purl.org/linked-data/cube#")


def apply_default_namespaces(graph):
    """
    Applies a set of default namespaces to the RDFLib graph
    provided as argument and returns the graph.
    """

    graph.bind('sdh', SDH)
    graph.bind('qb', QB)

    return graph


def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return izip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


def convert(infile, outfile, delimiter=',', quotechar='\"', dataset_name=None, processes=4, chunksize=1000, config={}):
    if dataset_name is None:
        dataset_name = os.path.basename(infile).rstrip('.csv')

    if processes > 1 :
        logger.info("Using "+ str(processes) +" parallel processes")
        parallel_convert(infile, outfile, delimiter, quotechar, dataset_name, processes, chunksize, config)
    else:
        logger.info("Using a single process")
        simple_convert(infile, outfile, delimiter, quotechar, dataset_name, config)
    logger.info("Done")


def simple_convert(infile, outfile, delimiter, quotechar, dataset_name, config):
    with open(outfile, 'w') as outfile_file:
        with open(infile, 'r') as infile_file:
            r = csv.reader(infile_file,
                           delimiter=delimiter,
                           quotechar=quotechar,
                           strict=True)

            headers = r.next()

            c = Converter(dataset_name, headers, config)
            c.g.add((c._dataset_uri, RDF.type, QB['DataSet']))
            outfile_file.write(c.g.serialize(format='nt'))

            result = c.process(0, r, 1)
            
            outfile_file.write(result)


def parallel_convert(infile, outfile, delimiter, quotechar, dataset_name, processes, chunksize, config):
    pool = mp.Pool(processes=processes)

    with open(outfile, 'w') as outfile_file:

        with open(infile, 'r') as infile_file:
            r = csv.reader(infile_file,
                           delimiter=delimiter,
                           quotechar=quotechar,
                           strict=True)

            headers = r.next()

            c = Converter(dataset_name, headers, config)
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
    c = Converter(dataset_name, headers, config)
    print mp.current_process().name, count, len(rows)
    result = c.process(count, rows, chunksize)
    print mp.current_process().name, 'done'
    return result


class Converter(object):

    _VOCAB_BASE = "http://data.socialhistory.org/vocab"
    _RESOURCE_BASE = "http://data.socialhistory.org/resource"

    def __init__(self, dataset_name, headers, config):
        self._headers = headers
        if 'family' in config:
            self._family = config['family']
            try:
                family_def = getattr(mappings, config['family'])
                self._nocode = family_def['nocode']
                self._integer = family_def['integer']
                self._mappings = family_def['mappings']
            except:
                logger.warning('No family definition found')
                self._nocode = []
                self._integer = []
                self._mappings = {}
        else:
            self._family = None

        if 'number_observations' in config:
            self._number_observations = config['number_observations']
        else:
            self._number_observations = None

        self._stop = config['stop']

        if self._family is None:
            self._VOCAB_URI_PATTERN = "{0}/{{}}/{{}}".format(self._VOCAB_BASE)
            self._RESOURCE_URI_PATTERN = "{0}/{{}}/{{}}".format(self._RESOURCE_BASE)
        else:
            self._VOCAB_URI_PATTERN = "{0}/{1}/{{}}/{{}}".format(self._VOCAB_BASE, self._family)
            self._RESOURCE_URI_PATTERN = "{0}/{1}/{{}}/{{}}".format(self._RESOURCE_BASE, self._family)

        self.g = apply_default_namespaces(Graph())

        self._dataset_name = dataset_name
        self._dataset_uri = self.resource('dataset', dataset_name)

    def process(self, count, rows, chunksize):

        obs_count = count * chunksize
        for row in rows:
            # rows may be filled with None values (because of the izip_longest function)
            if row is None:
                continue

            if self._number_observations:
                obs = self.resource('observation/{}'.format(self._dataset_name), obs_count)
            else:
                obs = self.resource('observation/{}'.format(self._dataset_name),
                                    uuid.uuid4())

            self.g.add((obs, QB['dataSet'], self._dataset_uri))

            index = 0
            for col in row:
                if len(col) < 1:
                    index += 1
                    logger.debug('Col length < 1')
                    continue
                elif self._headers[index] in self._mappings:
                    value = self._mappings[self._headers[index]](col)
                else:
                    value = col

                dimension_uri = self.vocab('dimension', self._headers[index])
                if self._headers[index] in self._nocode:
                    self.g.add((obs, dimension_uri, Literal(value)))
                elif self._headers[index] in self._integer:
                    self.g.add((obs, dimension_uri, Literal(value, datatype=XSD.integer)))
                else:
                    value_uri = self.resource(self._headers[index], value)
                    self.g.add((obs, dimension_uri, value_uri))

                index += 1

            obs_count += 1
            # if stop is not None and obs_count == stop:
            #     logger.info("Stopping at {}".format(obs_count))
            #     break
        
        

        files = [f for f in listdir("update-queries/") if os.path.isfile(os.path.join("update-queries/", f))]
        for f in files: 
            if self._family in f and f.endswith("rq"): 
                query = file("update-queries/" + f).read()
                self.g.update(query)
                

        return self.g.serialize(format='nt')

    def resource(self, resource_type, resource_name):
        raw_iri = self._RESOURCE_URI_PATTERN.format(resource_type, resource_name)
        iri = to_iri(raw_iri)

        return URIRef(iri)

    def vocab(self, concept_type, concept_name):
        raw_iri = self._VOCAB_URI_PATTERN.format(concept_type, concept_name)
        iri = to_iri(raw_iri)

        return URIRef(iri)
