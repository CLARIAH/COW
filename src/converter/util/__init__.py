from rdflib import Dataset, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
import os
import yaml
import datetime
from hashlib import sha1


"""
Initialize a set of default namespaces from a configuration file (namespaces.yaml)
"""
namespaces = {}
YAML_NAMESPACE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'namespaces.yaml')


def init():
    """
    Initialize the module and assign namespaces to globals
    """
    # Read the file into a dictionary
    with open(YAML_NAMESPACE_FILE, 'r') as nsfile:
        namespaces = yaml.load(nsfile)

    # Replace each value with a Namespace object for that value
    for prefix, uri in namespaces.items():
        if isinstance(prefix, str) and isinstance(uri, str):
            namespaces[prefix] = Namespace(uri)

    # Add a number of standard namespaces (if not already present in namespaces.yaml)
    namespaces['owl'] = OWL
    namespaces['rdf'] = RDF
    namespaces['rdfs'] = RDFS
    namespaces['xsd'] = XSD

    # Add all namespace prefixes to the globals dictionary (for exporting)
    for prefix, namespace in namespaces.items():
        globals()[prefix.upper()] = namespace


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

# Make sure the namespaces are initialized when the module is imported
init()

class Nanopublication(Dataset):
    """
    A subclass of the rdflib Dataset class that comes pre-initialized with
    required Nanopublication graphs: np, pg, ag, pig, for nanopublication, provenance,
    assertion and publication info, respectively.
    """

    def __init__(self, file_name, author_email):
        """
        Initialize the graphs needed for the nanopublication
        """
        super.__init__()

        # Assign default namespace prefixes
        for prefix, namespace in namespaces:
            self.bind(prefix, namespace)

        # Get the current date and time (UTC)
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")

        # Obtain a hash of the source file used for the conversion.
        source_hash = git_hash(file(file_name).read())
        # Shorten the source hash to 8 digits (similar to Github)
        short_hash = source_hash[:8]

        # Determine a 'hash_part' for all timestamped URIs generated through this procedure
        hash_part = short_hash + '/' + timestamp

        # A URI that represents the author
        author_uri = SDP[author_email]
        self.add((author_uri, RDF.type, FOAF['Person']))
        self.add((author_uri, FOAF['email'], Literal(author_email)))

        # A URI that represents the version of the file being converted
        dataset_version_uri = SDR[source_hash]
        self.add((dataset_version_uri, SDV['path'], Literal(file_name, datatype=XSD.string)))
        self.add((dataset_version_uri, SDV['sha1_hash'], Literal(source_hash, datatype=XSD.string)))

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
        self.add((nanopublication_uri, NP['hasProvenance'], self.pg_uri))
        self.add((self.pg_uri, RDF.type, NP['Provenance']))
        # The link to the publication info graph
        self.add((nanopublication_uri, NP['hasPublicationInfo'], pubinfo_graph_uri))
        self.add((pubinfo_graph_uri, RDF.type, NP['PublicationInfo']))

        # ----
        # The provenance graph
        # ----

        # Provenance information for the assertion graph (the data structure definition itself)
        self.pg.add((assertion_graph_uri, PROV['wasDerivedFrom'], dataset_version_uri))
        self.pg.add((dataset_uri, PROV['wasDerivedFrom'], dataset_version_uri))
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
        pubinfo_graph.add((nanopublication_uri, PROV['generatedAtTime'],
                          Literal(timestamp, datatype=XSD.datetime)))
        pubinfo_graph.add((nanopublication_uri, PROV['wasAttributedTo'], author_uri))
