from rdflib import Dataset, Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
import os
import yaml
import datetime
import string
import logging
import iribaker
import urllib
import uuid

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

    for prefix, namespace in namespaces.items():
        graph.bind(prefix, namespace)

    return graph


def get_namespaces():
    """Return the global namespaces"""
    return namespaces


def safe_url(NS, local):
    """Generates a URIRef from the namespace + local part that is safe for
    use in RDF graphs

    Arguments:
    NS      -- a @Namespace object
    local   -- the local name of the resource
    """
    return URIRef(iribaker.to_iri(NS[local]))


def get_base_uri(dataset):
    """Get a base uri for the ``dataset`` (name)"""
    return Namespace('{}{}/'.format(namespaces['sdr'], dataset))


def get_value_uri(dataset, variable, value):
    """Generates a variable value IRI for a given combination of dataset, variable and value"""
    BASE = get_base_uri(dataset)

    return iribaker.to_iri(BASE['code/' + variable + '/' + value])


def get_variable_uri(dataset, variable):
    """Generates a variable IRI for a given combination of dataset and variable"""
    BASE = get_base_uri(dataset)

    return iribaker.to_iri(BASE[variable])


class DatastructureDefinition(Graph):
    """
    An RDFLib Graph that contains a datastructure definition, as specified by a QBer JSON dataset structure
    """

    def __init__(self, dataset_uri, dataset_name, variables):
        super(DatastructureDefinition, self).__init__()

        # Use the dataset_uri as BASE namespace
        BASE = Namespace("{}/".format(dataset_uri))

        # The URI of the DatastructureDefinition
        structure_uri = BASE['structure']

        self.add((dataset_uri, RDF.type, QB['DataSet']))
        self.add((dataset_uri, RDFS.label, Literal(dataset_name)))
        self.add((structure_uri, RDF.type, QB['DataStructureDefinition']))

        self.add((dataset_uri, QB['structure'], structure_uri))

        for variable_id, variable in variables.items():
            variable_uri = URIRef(variable['original']['uri'])
            variable_label = Literal(variable['original']['label'])
            variable_type = URIRef(variable['type'])


            # The variable as component of the definition
            component_uri = safe_url(BASE, 'component/' + variable['original']['label'])

            # Add link between the definition and the component
            self.add((structure_uri, QB['component'], component_uri))

            # Add label to variable
            # TODO: We may need to do something with a changed label for the variable
            self.add((variable_uri, RDFS.label, variable_label))

            if 'description' in variable and variable['description'] != "":
                self.add((variable_uri, RDFS.comment, Literal(variable['description'])))

            # If the variable URI is not the same as the original,
            # it is a specialization of a prior variable property.
            if variable['uri'] != str(variable_uri):
                self.add((variable_uri,
                          RDFS['subPropertyOf'],
                          URIRef(variable['uri'])))

            if variable_type == QB['DimensionProperty']:
                self.add((variable_uri, RDF.type, variable_type))
                self.add((component_uri, QB['dimension'], variable_uri))

                # Coded variables are also of type coded property (a subproperty of dimension property)
                if variable['category'] == 'coded':
                    self.add((variable_uri, RDF.type, QB['CodedProperty']))

            elif variable_type == QB['MeasureProperty']:
                # The category 'other'
                self.add((variable_uri, RDF.type, variable_type))
                self.add((component_uri, QB['measure'], variable_uri))
            elif variable_type == QB['AttributeProperty']:
                # Actually never produced by QBer at this stage
                self.add((variable_uri, RDF.type, variable_type))
                self.add((component_uri, QB['attribute'], variable_uri))

            # If this variable is of category 'coded', we add codelist and URIs for
            # each variable (including mappings between value uris and etc....)
            if variable['category'] == 'coded':
                codelist_uri = URIRef(variable['codelist']['original']['uri'])
                codelist_label = Literal(variable['codelist']['original']['label'])

                self.add((codelist_uri, RDF.type, SKOS['Collection']))
                self.add((codelist_uri, RDFS.label, Literal(codelist_label)))

                # The variable should point to the codelist
                self.add((variable_uri, QB['codeList'], codelist_uri))

                # The variable is mapped onto an external code list.
                # If the codelist uri is not the same as the original one, we
                # have a derived codelist.
                if variable['codelist']['uri'] != str(codelist_uri):
                    self.add((codelist_uri,
                              PROV['wasDerivedFrom'],
                              URIRef(variable['codelist']['uri'])))

                # Generate a SKOS concept for each of the values and map it to the
                # assigned codelist
                # But only if the 'values' are specified for this variable.
                if 'values' not in variable:
                    continue

                for value in variable['values']:
                    value_uri = URIRef(value['original']['uri'])
                    value_label = Literal(value['original']['label'])

                    self.add((value_uri, RDF.type, SKOS['Concept']))
                    self.add((value_uri, SKOS['prefLabel'], Literal(value_label)))
                    self.add((codelist_uri, SKOS['member'], value_uri))

                    # The value has been changed, and therefore there is a mapping
                    if value['original']['uri'] != value['uri']:
                        self.add((value_uri, SKOS['exactMatch'], URIRef(value['uri'])))
                        self.add((value_uri, RDFS.label, Literal(value['label'])))

            elif variable['category'] == 'identifier':
                # Generate a SKOS concept for each of the values
                # But only if the variable has specified values
                if 'values' not in variable:
                    continue

                for value in variable['values']:
                    value_uri = URIRef(value['original']['uri'])
                    value_label = Literal(value['original']['label'])

                    self.add((value_uri, RDF.type, SKOS['Concept']))
                    self.add((value_uri, SKOS['prefLabel'], value_label))

                    # The value has been changed, and therefore there is a mapping
                    if value['original']['uri'] != value['uri']:
                        self.add((value_uri, SKOS['exactMatch'], URIRef(value['uri'])))
                        self.add((value_uri, RDFS.label, Literal(value['label'])))

            elif variable['category'] == 'other':
                # Generate a literal for each of the values when converting the dataset (but not here)
                pass


class Profile(Graph):
    """
    An RDFLib Graph that contains author information based on a Google Profile
    """

    def __init__(self, profile):
        # A URI that represents the author

        # Virtuoso does not accept the @
        self.author_uri = SDP[urllib.quote_plus(profile['email'])]

        super(Profile, self).__init__(identifier=self.author_uri)

        self.add((self.author_uri, RDF.type, FOAF['Person']))
        self.add((self.author_uri, FOAF['name'], Literal(profile['name'])))
        self.add((self.author_uri, FOAF['email'], Literal(profile['email'])))
        self.add((self.author_uri, SDV['googleId'], Literal(profile['id'])))
        try:
            self.add((self.author_uri, FOAF['depiction'], URIRef(profile['image'])))
        except KeyError:
            logger.warning('No author depiction provided in author profile')



class Nanopublication(Dataset):
    """
    A subclass of the rdflib Dataset class that comes pre-initialized with
    required Nanopublication graphs: np, pg, ag, pig, for nanopublication, provenance,
    assertion and publication info, respectively.

    NOTE: Will only work if the required namespaces are specified in namespaces.yaml and the init() function has been called
    """

    def __init__(self, file_name):
        """
        Initialize the graphs needed for the nanopublication
        """
        super(Dataset, self).__init__()

        # Virtuoso does not accept BNodes as graph names
        self.default_context = Graph(store=self.store, identifier=URIRef(uuid.uuid4().urn))


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
        name = (os.path.basename(file_name)).split('.')[0]
        self.uri = SDR[name + '/nanopublication/' + hash_part]


        # The Nanopublication consists of three graphs
        assertion_graph_uri = SDR[name + '/assertion/' + hash_part]
        provenance_graph_uri = SDR[name + '/provenance/' + hash_part]
        pubinfo_graph_uri = SDR[name + '/pubinfo/' + hash_part]

        self.ag = self.graph(assertion_graph_uri)
        self.pg = self.graph(provenance_graph_uri)
        self.pig = self.graph(pubinfo_graph_uri)

        # The nanopublication
        self.add((self.uri , RDF.type, NP['Nanopublication']))
        # The link to the assertion
        self.add((self.uri , NP['hasAssertion'], assertion_graph_uri))
        self.add((assertion_graph_uri, RDF.type, NP['Assertion']))
        # The link to the provenance graph
        self.add((self.uri , NP['hasProvenance'], provenance_graph_uri))
        self.add((provenance_graph_uri, RDF.type, NP['Provenance']))
        # The link to the publication info graph
        self.add((self.uri , NP['hasPublicationInfo'], pubinfo_graph_uri))
        self.add((pubinfo_graph_uri, RDF.type, NP['PublicationInfo']))

        # ----
        # The provenance graph
        # ----

        # Provenance information for the assertion graph (the data structure definition itself)
        self.pg.add((assertion_graph_uri, PROV['wasDerivedFrom'], self.dataset_version_uri))
        # self.pg.add((dataset_uri, PROV['wasDerivedFrom'], self.dataset_version_uri))
        self.pg.add((assertion_graph_uri, PROV['generatedAtTime'],
                     Literal(timestamp, datatype=XSD.dateTime)))

        # ----
        # The publication info graph
        # ----

        # The URI of the latest version of this converter
        # TODO: should point to the actual latest commit of this converter.
        # TODO: consider linking to this as the plan of some activity, rather than an activity itself.
        clariah_uri = URIRef('https://github.com/CLARIAH/wp4-converters')

        self.pig.add((self.uri, PROV['wasGeneratedBy'], clariah_uri))
        self.pig.add((self.uri, PROV['generatedAtTime'],
                      Literal(timestamp, datatype=XSD.dateTime)))


    def ingest(self, graph, target_graph=None):
        """
        Adds all triples in the RDFLib ``graph`` to this :class:`Nanopublication` dataset.
        If ``target_graph`` is ``None``, then the triples are added to the default graph,
        otherwise they are added to the indicated graph
        """
        if target_graph is None:
            for s, p, o in graph:
                self.add((s, p, o))
        else:
            for s, p, o in graph:
                self.add((s, p, o, target_graph))
