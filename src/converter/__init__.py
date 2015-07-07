import os
import csv
import urllib
import rfc3987
import urlparse
import logging
from rdflib import Graph, Namespace, URIRef, RDF, Literal


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


def to_iri(iri):
    """
    Safely quotes an IRI in a way that is resilient to unicode and incorrect
    arguments (checks for RFC 3987 compliance and falls back to percent encoding)
    """
    # First decode the IRI if needed
    if not isinstance(iri, unicode):
        logger.debug("Converting IRI to unicode")
        iri = iri.decode('utf-8')

    try:
        # If we can safely parse the URI, then we don't
        # need to do anything special here
        rfc3987.parse(iri, rule='IRI')
        logger.debug("This is already a valid IRI, doing nothing...")
        return iri
    except:
        # The URI is not valid, so we'll have to fix it.
        logger.debug("The IRI is not valid, proceeding to quote...")
        # First see whether we can actually parse it *as if* it is a URI

        parts = urlparse.urlsplit(iri)
        if not parts.scheme or not parts.netloc:
            # If there is no scheme (e.g. http) nor a net location (e.g.
            # example.com) then we cannot do anything
            logger.error("The argument you provided does not comply with"
                         "RFC 3987 and is not parseable as a IRI")
            raise Exception("""The argument you provided does not comply with
                            RFC 3987 and is not parseable as a IRI""")

        quoted_parts = {}
        # We'll now convert the path, query and fragment parts of the URI

        # Get the 'anti-pattern' for the valid characters (see rfc3987 package)
        # This is roughly the ipchar pattern plus the '/' as we don't need to match
        # the entire path, but merely the individual characters
        no_invalid_characters = rfc3987.get_compiled_pattern("(?!%(iunreserved)s|%(pct_encoded)s|%(sub_delims)s|:|@|/)(.)")

        # Replace the invalid characters with an underscore (no need to roundtrip)
        quoted_parts['path'] = no_invalid_characters.sub(u'_',parts.path)
        quoted_parts['fragment'] = no_invalid_characters.sub(u'_',parts.fragment)
        quoted_parts['query'] = urllib.quote(parts.query.encode('utf-8'))
        # Leave these untouched
        quoted_parts['scheme'] = parts.scheme
        quoted_parts['authority'] = parts.netloc

        # Extra check to make sure we now have a valid IRI
        quoted_iri = rfc3987.compose(**quoted_parts)
        try:
            rfc3987.parse(quoted_iri)
        except:
            # Unable to generate a valid quoted iri, using the straightforward
            # urllib percent quoting (but this is ugly!)
            logger.warning('Could not safely quote as IRI, falling back to '
                           'percent encoding')
            quoted_iri = urllib.quote(iri.encode('utf-8'))

        return quoted_iri


class Converter(object):

    _VOCAB_BASE = "http://data.socialhistory.org/vocab"
    _RESOURCE_BASE = "http://data.socialhistory.org/resource"

    def __init__(self, nocode=[], mappings={}, family=None, number_observations=True):
        self._nocode = nocode
        self._mappings = mappings
        self._number_observations = number_observations

        if family is None:
            self._VOCAB_URI_PATTERN = "{0}/{{}}/{{}}".format(self._VOCAB_BASE)
            self._RESOURCE_URI_PATTERN = "{0}/{{}}/{{}}".format(self._RESOURCE_BASE)
        else:
            self._VOCAB_URI_PATTERN = "{0}/{1}/{{}}/{{}}".format(self._VOCAB_BASE, family)
            self._RESOURCE_URI_PATTERN = "{0}/{1}/{{}}/{{}}".format(self._RESOURCE_BASE, family)

        self.g = apply_default_namespaces(Graph())

    def convert(self, infile, outfile, delimiter=',', quotechar='\"', dataset_name=None, stop=None):

        if dataset_name is None:
            dataset_name = os.path.basename(infile).rstrip('.csv')

        dataset_uri = self.resource('dataset', dataset_name)
        self.g.add((dataset_uri, RDF.type, QB['Dataset']))


        with open(infile) as infile_file:
            r = csv.reader(infile_file, delimiter=delimiter, quotechar=quotechar, strict=True)

            headers = r.next()
            obs_count = 0
            for row in r:
                index = 0
                obs_count += 1
                logger.debug(obs_count)

                if self._number_observations:
                    obs = self.resource('observation/{}'.format(dataset_name), obs_count)
                else :
                    obs = self.resource('observation/{}'.format(dataset_name),
                                        ''.join(row))

                self.g.add((obs, QB['dataset'], dataset_uri))

                for col in row:
                    if len(col) < 1:
                        index += 1
                        logger.debug('Col length < 1')
                        continue
                    elif headers[index] in self._mappings:
                        value = self._mappings[headers[index]](col)
                    else:
                        value = col

                    dimension_uri = self.vocab('dimension', headers[index])
                    if headers[index] in self._nocode:
                        self.g.add((obs, dimension_uri, Literal(value)))
                    else:
                        value_uri = self.resource(headers[index], value)
                        self.g.add((obs, dimension_uri, value_uri))

                    index += 1

                if stop is not None and obs_count == stop:
                    logger.info("Stopping at {}".format(obs_count))
                    break

            with open(outfile, 'w') as f:
                logger.info('Serializing to file...')
                self.g.serialize(f, format='nt')

    def resource(self, resource_type, resource_name):
        raw_iri = self._RESOURCE_URI_PATTERN.format(resource_type, resource_name)
        iri = to_iri(raw_iri)

        return URIRef(iri)

    def vocab(self, concept_type, concept_name):
        raw_iri = self._VOCAB_URI_PATTERN.format(concept_type, concept_name)
        iri = to_iri(raw_iri)

        return URIRef(iri)
