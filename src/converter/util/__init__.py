from rdflib import Dataset, Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
import os
import yaml
import datetime
import string
import logging

from hashlib import sha1


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

"""
Initialize a set of default namespaces from a configuration file (namespaces.yaml)
"""
# global namespaces
namespaces = {}
YAML_NAMESPACE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'namespaces.yaml')


def init():
    """
    Initialize the module and assign namespaces to globals
    """
    # Read the file into a dictionary
    with open(YAML_NAMESPACE_FILE, 'r') as nsfile:
        global namespaces
        namespaces = yaml.load(nsfile)

    # Replace each value with a Namespace object for that value
    for prefix, uri in namespaces.items():
        if isinstance(prefix, str) and isinstance(uri, str):
            namespaces[prefix] = Namespace(uri)

    # Add all namespace prefixes to the globals dictionary (for exporting)
    for prefix, namespace in namespaces.items():
        globals()[prefix.upper()] = namespace

# Make sure the namespaces are initialized when the module is imported
init()


def reindent(s, numSpaces):
    s = s.split('\n')
    s = [(numSpaces * ' ') + string.lstrip(line) for line in s]
    s = "\n".join(s)
    return s


def serializeTrig(rdf_dataset):
    turtles = []
    for c in rdf_dataset.contexts():
        if c.identifier != URIRef('urn:x-rdflib:default'):
            turtle = "<{id}> {{\n".format(id=c.identifier)
            turtle += reindent(c.serialize(format='turtle'), 4)
            turtle += "}\n\n"
        else:
            turtle = c.serialize(format='turtle')
            turtle += "\n\n"

        turtles.append(turtle)

    return "\n".join(turtles)


def git_hash(data):
    """
    Generates a Git-compatible hash for identifying (the current version of) the data
    """
    s = sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return s.hexdigest()


def apply_default_namespaces(graph):
    """
    Apply a set of default namespaces to the RDFLib graph
    provided as argument and returns the graph.
    """

    for prefix, namespace in namespaces:
        graph.bind(prefix, namespace)

    return graph


def get_namespaces():
    return namespaces


class Profile(Graph):
    """
    An RDFLib Graph that contains author information based on a Google Profile
    """

    def __init__(self, profile):
        # A URI that represents the author
        author_uri = SDP[profile['email']]

        super(Graph, self).__init__(identifier=author_uri)

        self.add((author_uri, RDF.type, FOAF['Person']))
        self.add((author_uri, FOAF['name'], Literal(profile['name'])))
        self.add((author_uri, FOAF['email'], Literal(profile['email'])))
        self.add((author_uri, SDV['googleId'], Literal(profile['id'])))
        try:
            self.add((author_uri, FOAF['depiction'], URIRef(profile['image'])))
        except KeyError:
            logger.warning('No author depiction provided in author profile')



class Nanopublication(Dataset):
    """
    A subclass of the rdflib Dataset class that comes pre-initialized with
    required Nanopublication graphs: np, pg, ag, pig, for nanopublication, provenance,
    assertion and publication info, respectively.

    NOTE: Will only work if the required namespaces are specified in namespaces.yaml and the init()
          function has been called
    """

    def __init__(self, file_name):
        """
        Initialize the graphs needed for the nanopublication
        """
        super(Dataset, self).__init__()

        # Assign default namespace prefixes
        for prefix, namespace in namespaces.items():
            self.bind(prefix, namespace)

        # Get the current date and time (UTC)
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")

        # Obtain a hash of the source file used for the conversion.
        # TODO: Get this directly from GitLab
        source_hash = git_hash(file(file_name).read())

        # Shorten the source hash to 8 digits (similar to Github)
        short_hash = source_hash[:8]

        # Determine a 'hash_part' for all timestamped URIs generated through this procedure
        hash_part = short_hash + '/' + timestamp

        # A URI that represents the version of the file being converted
        self.dataset_version_uri = SDR[source_hash]
        self.add((self.dataset_version_uri, SDV['path'], Literal(file_name, datatype=XSD.string)))
        self.add((self.dataset_version_uri, SDV['sha1_hash'], Literal(source_hash, datatype=XSD.string)))

        # ----
        # The nanopublication graph
        # ----
        nanopublication_uri = SDR['nanopublication/' + hash_part]

        # The Nanopublication consists of three graphs
        assertion_graph_uri = SDR['assertion/' + hash_part]
        provenance_graph_uri = SDR['provenance/' + hash_part]
        pubinfo_graph_uri = SDR['pubinfo/' + hash_part]

        self.ag = self.graph(assertion_graph_uri)
        self.pg = self.graph(provenance_graph_uri)
        self.pig = self.graph(pubinfo_graph_uri)

        # The nanopublication
        self.add((nanopublication_uri, RDF.type, NP['Nanopublication']))
        # The link to the assertion
        self.add((nanopublication_uri, NP['hasAssertion'], assertion_graph_uri))
        self.add((assertion_graph_uri, RDF.type, NP['Assertion']))
        # The link to the provenance graph
        self.add((nanopublication_uri, NP['hasProvenance'], provenance_graph_uri))
        self.add((provenance_graph_uri, RDF.type, NP['Provenance']))
        # The link to the publication info graph
        self.add((nanopublication_uri, NP['hasPublicationInfo'], pubinfo_graph_uri))
        self.add((pubinfo_graph_uri, RDF.type, NP['PublicationInfo']))

        # ----
        # The provenance graph
        # ----

        # Provenance information for the assertion graph (the data structure definition itself)
        self.pg.add((assertion_graph_uri, PROV['wasDerivedFrom'], self.dataset_version_uri))
        # self.pg.add((dataset_uri, PROV['wasDerivedFrom'], self.dataset_version_uri))
        self.pg.add((assertion_graph_uri, PROV['generatedAtTime'],
                     Literal(timestamp, datatype=XSD.datetime)))
        self.pg.add((assertion_graph_uri, PROV['wasAttributedTo'], author_uri))

        # ----
        # The publication info graph
        # ----

        # The URI of the latest version of QBer
        # TODO: should point to the actual latest commit of this QBer source file.
        # TODO: consider linking to this as the plan of some activity, rather than an activity itself.
        qber_uri = URIRef('https://github.com/CLARIAH/qber.git')

        self.pig.add((nanopublication_uri, PROV['wasGeneratedBy'], qber_uri))
        self.pig.add((nanopublication_uri, PROV['generatedAtTime'],
                      Literal(timestamp, datatype=XSD.datetime)))
        self.pig.add((nanopublication_uri, PROV['wasAttributedTo'], author_uri))
