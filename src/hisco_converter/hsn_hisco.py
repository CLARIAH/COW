from rdflib import Graph, Namespace, Literal, URIRef
import csv, iribaker, io, codecs, cStringIO, warnings

g = Graph()

CATEGORY = Namespace('http://data.socialhistory.org/vocab/hisco/category/')
ENTRY    = Namespace('http://data.socialhistory.org/vocab/hisco/entry/')
SKOS     = Namespace('http://www.w3.org/2004/02/skos/core#')
PROV     = Namespace('http://www.w3.org/ns/prov#')

g.bind('cat'  , CATEGORY)
g.bind('skos' , SKOS)
g.bind('entry', ENTRY)
g.bind('prov' , PROV)

hsn = open('../../sdh-public-datasets/hsn2013a_hisco_comma.csv')
hisco = csv.reader(hsn)

next(hisco)
    

for row in hisco: # define and columns and names for columns
    if len(row[3]) == 4: # some zero's missing
        row[0] = "0" + row[0]
    
    hisco_occupational_category = row[3].decode('utf-8')
    hisco_occupational_entry = row[1].decode('utf-8').lower().strip()
    # using .strip() since some entries have whitespace at the end of the line, 
    # and iribaker doesn't appreciate that.
    hisco_occupational_standard = row[2].decode('utf-8').lower()

    hisco_status     = row[4]
    hisco_relation   = row[5]
    hisco_product    = row[6]
    hisco_provenance = row[12] 
    
    # print URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry))
                 
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['hiddenLabel'], Literal(hisco_occupational_entry, 'nl')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['prefLabel'],   Literal(hisco_occupational_standard, 'nl')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), PROV.wasQuotedFrom,  URIRef('http://hdl.handle.net/10622/UQJZKJ')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['closeMatch'],  CATEGORY[hisco_occupational_category]))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['member'],      ENTRY['entryCollection']))



with open('rdf/hsn_hisco_entry_2013a.ttl','w') as out: 
    g.serialize(out, format='turtle')
