from json import load
import rdflib as rdf
from iribaker import to_iri

def makegraph(codebook, variable, vocab_name):

    base = 'http://data.socialhistory.org/vocab/' + vocab_name + '/'
    vrb_iri = to_iri(base + variable + '/')
    VCB_NAMESPACE = rdf.Namespace(vrb_iri)
    SKOS = rdf.Namespace('http://www.w3.org/2004/02/skos/core#')

    g = rdf.Graph()

    g.bind(vocab_name, VCB_NAMESPACE)
    g.bind('skos', SKOS)
    g.add((VCB_NAMESPACE[variable], rdf.RDF.type, SKOS['Scheme']))
    
    g.add((VCB_NAMESPACE[variable], SKOS['definition'], rdf.Literal(codebook['def'][0])))
    if len(codebook)==1:
        return g

    for i in range(len(codebook['code'])):
        iri = to_iri(VCB_NAMESPACE[str(codebook['code'][i])])
        g.add((rdf.term.URIRef(iri), rdf.RDF.type, SKOS['Concept']))
        g.add((rdf.term.URIRef(iri), SKOS['inScheme'], VCB_NAMESPACE[variable]))
        g.add((rdf.term.URIRef(iri), SKOS['prefLabel'], rdf.Literal(codebook['label'][i])))
    
    return g


with open('canadacodes.json') as datafile:
    codebook = load(datafile)

graphs = {}

for variable in codebook.keys():
    graphs[variable] = makegraph(codebook=codebook[variable],
        variable=variable, vocab_name='canfam')

for variable, graph in graphs.items():
    with open(variable + '.ttl', 'w') as outfile:
        graph.serialize(outfile, format='turtle')