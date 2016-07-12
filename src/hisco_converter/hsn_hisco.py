from rdflib import Graph, Namespace, Literal, URIRef
import csv, iribaker

g = Graph()

CATEGORY = Namespace('http://data.socialhistory.org/vocab/hisco/category/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
ENTRY = Namespace('http://data.socialhistory.org/vocab/hisco/entry/')
PROV = Namespace('http://www.w3.org/ns/prov#')

g.bind('cat', CATEGORY)
g.bind('skos', SKOS)
g.bind('entry', ENTRY)
g.bind('prov', PROV)

hsn = open('../../sdh-public-datasets/hsn2013a_hisco_comma.csv')

hisco = csv.reader(hsn)
next(hisco)
    

for row in hisco: # define and columns and names for columns
    if len(row[3]) == 4: # some zero's missing
        row[0] = "0" + row[0]
    
    hisco_occupational_category = row[3].decode('latin-1')
    hisco_occupational_entry = row[1].decode('latin-1').lower()
    hisco_occupational_standard = row[2].decode('latin-1').lower()
    hisco_status = row[4]
    hisco_relation = row[5]
    hisco_product = row[6]
    hisco_provenance = row[12] 
    
    print URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry))
                 
    g.add((CATEGORY[hisco_occupational_category], SKOS['hiddenLabel'], Literal(hisco_occupational_entry, 'nl')))
    g.add((CATEGORY[hisco_occupational_category], SKOS['prefLabel'], Literal(hisco_occupational_standard, 'nl')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), PROV.wasQuotedFrom, URIRef('http://hdl.handle.net/10622/UQJZKJ')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['closeMatch'], CATEGORY[hisco_occupational_category]))

with open('rdf/hsn_hisco_entry_2013a.ttl','w') as out: 
    g.serialize(out, format='turtle')
