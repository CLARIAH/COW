from rdflib import Dataset, Namespace, Literal, BNode, RDF, RDFS, XSD, URIRef
import datetime
import csv
from rdflib import URIRef
from hashlib import sha1
import string


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
        else :
            turtle = c.serialize(format='turtle')
            turtle += "\n\n"

        turtles.append(turtle)

    return "\n".join(turtles)

def githash(data):
    s = sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return s.hexdigest()




CLIOIND = Namespace('http://data.socialhistory.org/resource/clio/indicator/')
CLIOPROP = Namespace('http://data.socialhistory.org/resource/clio/property/')
CLIOCTR = Namespace('http://data.socialhistory.org/resource/clio/country/')
CLIO = Namespace('http://data.socialhistory.org/resource/clio/')

SDMX = Namespace('http://purl.org/linked-data/sdmx#')
SDMXMSR = Namespace('http://purl.org/linked-data/sdmx/2009/measure#')
SDMXDIM = Namespace('http://purl.org/linked-data/sdmx/2009/dimension#')

QBRV = Namespace('http://data.socialhistory.org/vocab/')
QBR = Namespace('http://data.socialhistory.org/resource/')

QB = Namespace('http://purl.org/linked-data/cube#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
PROV = Namespace('http://www.w3.org/ns/prov#')
NP = Namespace('http://www.nanopub.org/nschema#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')




dataset = "gdppc"
pathtofile = '../../sdh-public-datasets/allcliodata_raw.csv'


BASE = Namespace('http://data.socialhistory.org/resource/{}/'.format(dataset))


# Initialize a conjunctive graph for the whole lot
rdf_dataset = Dataset()
rdf_dataset.bind('qbrv', QBRV)
rdf_dataset.bind('qbr', QBR)
rdf_dataset.bind('qb', QB)
rdf_dataset.bind('skos', SKOS)
rdf_dataset.bind('prov', PROV)
rdf_dataset.bind('np', NP)
rdf_dataset.bind('foaf', FOAF)

rdf_dataset.bind('clio-property', CLIOPROP)
rdf_dataset.bind('clio-indicator', CLIOIND)
rdf_dataset.bind('clio-country', CLIOCTR)
rdf_dataset.bind('clio', CLIO)

rdf_dataset.bind('sdmx', SDMX)
rdf_dataset.bind('sdmx-dimension', SDMXDIM)
rdf_dataset.bind('sdmx-measure', SDMXMSR)


# Initialize the graphs needed for the nanopublication
timestamp = datetime.datetime.now().isoformat()

source_hash = githash(file(pathtofile).read())
hash_part = source_hash + '/' + timestamp



# The Nanopublication consists of three graphs
assertion_graph_uri = BASE['assertion/' + hash_part]
assertion_graph = rdf_dataset.graph(assertion_graph_uri)

provenance_graph_uri = BASE['provenance/' + hash_part]
provenance_graph = rdf_dataset.graph(provenance_graph_uri)

pubinfo_graph_uri = BASE['pubinfo/' + hash_part]
pubinfo_graph = rdf_dataset.graph(pubinfo_graph_uri)
    

# A URI that represents the author
author_uri = QBR['person/k.dentler@vu.nl']
rdf_dataset.add((author_uri, RDF.type, FOAF['Person']))
rdf_dataset.add((author_uri, FOAF['name'], Literal('Kathrin Dentler')))
rdf_dataset.add((author_uri, FOAF['email'], Literal('k.dentler@vu.nl')))
rdf_dataset.add((author_uri, FOAF['depiction'], URIRef('http://www.dentler.org/kathrin.jpg')))
# rdf_dataset.add((author_uri, QBRV['googleId'], Literal(profile['id'])))


# A URI that represents the version of the dataset source file
dataset_version_uri = BASE[source_hash]
    
# Some information about the source file used
rdf_dataset.add((dataset_version_uri, QBRV['path'], Literal(pathtofile, datatype=XSD.string)))
rdf_dataset.add((dataset_version_uri, QBRV['sha1_hash'], Literal(source_hash, datatype=XSD.string)))


# ----
# The nanopublication itself
# ----
nanopublication_uri = BASE['nanopublication/' + hash_part]

rdf_dataset.add((nanopublication_uri, RDF.type, NP['Nanopublication']))
rdf_dataset.add((nanopublication_uri, NP['hasAssertion'], assertion_graph_uri))
rdf_dataset.add((assertion_graph_uri, RDF.type, NP['Assertion']))
rdf_dataset.add((nanopublication_uri, NP['hasProvenance'], provenance_graph_uri))
rdf_dataset.add((provenance_graph_uri, RDF.type, NP['Provenance']))
rdf_dataset.add((nanopublication_uri, NP['hasPublicationInfo'], pubinfo_graph_uri))
rdf_dataset.add((pubinfo_graph_uri, RDF.type, NP['PublicationInfo']))
    
    
# ----
# The provenance graph
# ----

# Provenance information for the assertion graph (the data structure definition itself)
provenance_graph.add((assertion_graph_uri, PROV['wasDerivedFrom'], dataset_version_uri))
provenance_graph.add((assertion_graph_uri, PROV['generatedAtTime'], Literal(timestamp, datatype=XSD.datetime)))
provenance_graph.add((assertion_graph_uri, PROV['wasAttributedTo'], author_uri))
    


# ----
# The publication info graph
# ----

# The URI of the latest version of QBer
# TODO: should point to the actual latest commit of this QBer source file.
# TODO: consider linking to this as the plan of some activity, rather than an activity itself.
converters_uri = URIRef('https://github.com/CLARIAH-SDH/converters.git')

pubinfo_graph.add((nanopublication_uri, PROV['wasGeneratedBy'], converters_uri))
pubinfo_graph.add((nanopublication_uri, PROV['generatedAtTime'], Literal(timestamp, datatype=XSD.datetime)))
pubinfo_graph.add((nanopublication_uri, PROV['wasAttributedTo'], author_uri))


# ----
# The assertion graph
# ----
dataset_uri = QBR[dataset]
structure_uri = BASE['structure']

assertion_graph.add((dataset_uri, RDF.type, QB['DataSet']))
assertion_graph.add((dataset_uri, RDFS.label, Literal('GDP per capita in 1990 $GK')))
assertion_graph.add((dataset_uri, QB['structure'], structure_uri))
assertion_graph.add((dataset_uri, PROV['wasDerivedFrom'], dataset_version_uri))

assertion_graph.add((structure_uri, RDF.type, QB['DataStructureDefinition']))

bn = BNode()
assertion_graph.add((structure_uri, QB['component'], bn))
assertion_graph.add((bn, QB['dimension'], SDMXDIM['refArea']))
assertion_graph.add((bn, QB['dimension'], SDMXDIM['refPeriod']))
assertion_graph.add((bn, QB['measure'], SDMXMSR['obsValue']))
assertion_graph.add((bn, QB['attribute'], CLIOPROP['indicator']))


assertion_graph.add((CLIOIND['GDPPC1990GKD'], SKOS['prefLabel'], Literal('GDP per capita, PPP (contant 1990 international GK dollars)', lang='en')))
assertion_graph.add((CLIOIND['GDPPC1990GKD'], SKOS['definition'], Literal("GDP per capita based on purchasing power parity (PPP). PPP GDP is gross domestic product converted to international dollars using purchasing power parity rates. An international dollar has the same purchasing power over GDP as the U.S. dollar has in the United States. GDP at purchaser's prices is the sum of gross value added by all resident producers in the economy plus any product taxes and minus any subsidies not included in the value of the products. It is calculated without making deductions for depreciation of fabricated assets or for depletion and degradation of natural resources. Data are in constant 1990 international dollars.", lang='en')))
assertion_graph.add((CLIOIND['GDPPC1990GKD'], RDF.type, SDMX['ConceptRole']))
assertion_graph.add((CLIOIND['GDPPC1990GKD'], RDF.type, SKOS['Concept']))


with open(pathtofile, 'rb') as infile:
    lines = csv.reader(infile)
    header = next(lines)
    for row in lines:
        obsid = str(row[0]) + str(row[1])
        if row[3] == 'NA':
            continue
        assertion_graph.add((CLIO[obsid], RDF.type, QB['Observation']))
        assertion_graph.add((CLIO[obsid], QB['dataSet'], dataset_uri))
        assertion_graph.add((CLIO[obsid], SDMXDIM['refArea'], CLIOCTR[row[0]]))
        assertion_graph.add((CLIO[obsid], SDMXDIM['refPeriod'], Literal(row[1], datatype=XSD.gYear)))
        assertion_graph.add((CLIO[obsid], SDMXDIM['refPeriodInt'], Literal(row[1], datatype=XSD.int)))
        assertion_graph.add((CLIO[obsid], SDMXMSR['obsValue'], Literal(float(row[3]))))
        assertion_graph.add((CLIO[obsid], CLIOPROP['indicator'], CLIOIND['GDPPC1990GKD']))


with open('rdf/qbcliogdp.ttl', 'w') as outfile:
    outfile.write(serializeTrig(rdf_dataset))


