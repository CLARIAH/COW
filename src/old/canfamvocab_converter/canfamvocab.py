import logging
from json import load
from rdflib import Graph, Namespace, RDF, Literal, XSD, term 
from iribaker import to_iri

logging.basicConfig(level=logging.ERROR)


def RepresentsInt(s):
    if s != None: 
        try: 
            int(s)
            return True
        except ValueError:
            return False
    
    
def makegraph(codebook, variable, vocab_name):

    base = 'http://data.socialhistory.org/resource/' + vocab_name + '/'
    vrb_iri = to_iri(base + variable + '/')
    VCB_NAMESPACE = Namespace(vrb_iri)
    SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

    g = Graph()
    g.bind(vocab_name, VCB_NAMESPACE)
    g.bind('skos', SKOS)
    
    
    g.add((VCB_NAMESPACE[variable], RDF.type, SKOS['Scheme']))
    
    g.add((VCB_NAMESPACE[variable], SKOS['definition'], Literal(codebook['def'][0])))
    if len(codebook) == 1:
        return g

    for i in range(len(codebook['code'])):
        
        iri = to_iri(VCB_NAMESPACE[str(codebook['code'][i])])

        g.add((term.URIRef(iri), RDF.type, SKOS['Concept']))
        g.add((term.URIRef(iri), SKOS['inScheme'], VCB_NAMESPACE[variable]))
        g.add((term.URIRef(iri), SKOS['prefLabel'], Literal(codebook['label'][i])))


        if RepresentsInt(codebook['code'][i]): 
            g.add((term.URIRef(iri), RDF.value, Literal(codebook['code'][i], datatype=XSD.int)))
    
    return g


with open('canadacodes.json') as datafile:
    codebook = load(datafile)

graphs = {}

for variable in codebook.keys():
    graphs[variable] = makegraph(codebook=codebook[variable],
        variable=variable, vocab_name='canfam')

for variable, graph in graphs.items():
    with open('rdf/' + variable + '.ttl', 'w') as outfile:
        graph.serialize(outfile, format='turtle')
