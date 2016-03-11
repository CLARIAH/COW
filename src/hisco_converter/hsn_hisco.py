
# coding: utf-8

# In[1]:
from rdflib import Graph, Namespace, RDF, Literal, URIRef
import csv, os, iribaker

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/vocab/hisco/')
MAJOR = Namespace('http://data.socialhistory.org/vocab/hisco/majorGroup/')
MINOR = Namespace('http://data.socialhistory.org/vocab/hisco/minorGroup/')
UNIT  = Namespace('http://data.socialhistory.org/vocab/hisco/unitGroup/')
CATEGORY = Namespace('http://data.socialhistory.org/vocab/hisco/category/')
STATUS  = Namespace('http://data.socialhistory.org/vocab/hisco/status/')
RELATION  = Namespace('data.socialhistory.org/vocab/hisco/relation/')
PRODUCT = Namespace('http://data.socialhistory.org/vocab/hisco/product/')
ENTRY = Namespace('http://data.socialhistory.org/hisco/entry/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')
HSRC    = Namespace('http://data.socialhistory.org/vocab/hisco/resource/')
PROV    = Namespace('http://www.w3.org/ns/prov/')
FABIO = Namespace('http://purl.org/spar/fabio/')

g.bind('hisco', HISCO)
g.bind('major', MAJOR)
g.bind('minor', MINOR)
g.bind('unit', UNIT)
g.bind('cat', CATEGORY)
g.bind('skos', SKOS)
g.bind('entry', ENTRY)
g.bind('hsrc', HSRC)
g.bind('prov', PROV)
g.bind('fabio', FABIO)
g.bind('status', STATUS)
g.bind('relation', RELATION)
g.bind('product', PRODUCT)



data_path = "/Users/RichardZ/git/sdh-public-datasets/" # NB: In the future, preferably read file in from DATAVERSE 
os.chdir(data_path)
hsn = open('./hsn2013a_hisco_comma.csv')
# hsn = open('../../sdh-public-datasets/hsn2013a_hisco_comma.csv')

hisco = csv.reader(hsn)
next(hisco)
print(hisco)


for row in hisco: # define and columns and names for columns
    if len(row[3]) == 4: # some zero's missing
        row[0] = "0" + row[0]

    hisco_occupational_category  = row[3].decode('latin-1')
    hisco_occupational_entry = row[1].decode('latin-1').lower()
    hisco_occupational_standard = row[2].decode('latin-1').lower()
    hisco_status     =  row[4]
    hisco_relation   =  row[5]
    hisco_product    =  row[6]
    hisco_provenance = row[12] 

    g.add((CATEGORY[hisco_occupational_category], SKOS['hiddenLabel'], Literal(hisco_occupational_entry, 'nl')))
    g.add((CATEGORY[hisco_occupational_category], SKOS['prefLabel'], Literal(hisco_occupational_standard, 'nl')))


    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), PROV.wasQuotedFrom, URIRef('http://hdl.handle.net/10622/UQJZKJ')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), PROV.wasQuotedFrom, URIRef('http://hdl.handle.net/10622/UQJZKJ')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['closeMatch'], CATEGORY[hisco_occupational_category]))

## This takes some time...
# print g.serialize(format='turtle')

with open('./hsn_hisco_entry_2013a.ttl','w') as out:
# with open('rdf/hsn_hisco_entry_2013a.ttl','w') as out: 
    g.serialize(out, format='turtle')

# EOF
