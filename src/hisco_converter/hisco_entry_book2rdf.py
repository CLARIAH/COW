
# coding: utf-8

# In[3]:

from rdflib import Graph, Namespace, RDF, Literal, URIRef
import csv, os, iribaker

g = Graph()

HISCO    = Namespace('http://data.socialhistory.org/vocab/hisco/')
MAJOR    = Namespace('http://data.socialhistory.org/vocab/hisco/majorGroup/')
MINOR    = Namespace('http://data.socialhistory.org/vocab/hisco/minorGroup/')
UNIT     = Namespace('http://data.socialhistory.org/vocab/hisco/unitGroup/')
CATEGORY = Namespace('http://data.socialhistory.org/vocab/hisco/category/')
STATUS   = Namespace('http://data.socialhistory.org/vocab/hisco/status/')
RELATION = Namespace('http://data.socialhistory.org/vocab/hisco/relation/')
PRODUCT  = Namespace('http://data.socialhistory.org/vocab/hisco/product/')
ENTRY    = Namespace('http://data.socialhistory.org/vocab/hisco/entry/')
HSRC     = Namespace('http://data.socialhistory.org/vocab/hisco/resource/')
SKOS     = Namespace('http://www.w3.org/2004/02/skos/core#')
PROV     = Namespace('http://www.w3.org/ns/prov#')
FABIO    = Namespace('http://purl.org/spar/fabio/')

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


g.add((HSRC['hiscoBook'], RDF.type, FABIO['Book']))
g.add((HSRC['hiscoBook'], FABIO.has_ISBN, Literal('urn:isbn:9789058671967')))

g.add((ENTRY['entryCollection'], RDF.type, SKOS['Collection']))
g.add((ENTRY['entryCollection'], SKOS.definition, Literal('A hisco:entry is a recording of an occupational activity in a register, '+
                                          'such as a marriage record or census enumerator\'s book.')))
                                          
g.add((ENTRY['entryCollection'], SKOS.scopeNote, Literal('''While some hisco:entry\'s are correctly spelled occupations, e.g. "butcher", 
                                          "historian", or "architect", most recordings of occupational activity 
                                          will contain spelling errors, other recordings, multiple recordings 
                                          or elaborative recordings, such as "nurse in St. Mary\'s hospital". 
                                          All of these are considered to be hisco:entry\'s, thus even if they cannot
                                          be (easily) linked to an occupation. Examples of hisco:entry\'s from the
                                          hsrc:hiscoBook are clean and referred to as skos:example. All other
                                          entries are instances of skos:hiddenLabel''')))


# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)

hdf = open('../../sdh-private-hisco-datasets/occupation_link.csv')
hisco = csv.reader(hdf)

next(hisco)



for row in hisco: # define and columns and names for columns
    if len(row[6]) == 4: # some zero's missing
        row[0] = "0" + row[0]

    hisco_occupational_category  = row[6].decode('latin-1')
    hisco_occupational_entry_any = row[1].decode('latin-1').lower()
    hisco_occupational_entry_en  = row[2].decode('latin-1').lower()
    hisco_country    =  row[3].decode('latin-1').lower()
    hisco_language   =  row[4].decode('latin-1').lower()
    hisco_status     =  row[7]
    hisco_relation   =  row[8]
    hisco_product    =  row[9]
    # hisco_provenance = row[11] # add this back in, when the provenance file for the datasets is built.
    
    if hisco_language == 'uk':
        hisco_language = 'en'
    
    g.add((CATEGORY[hisco_occupational_category], RDF.type, SKOS['Concept']))
    g.add((CATEGORY[hisco_occupational_category], SKOS['member'], HISCO['CATEGORY']))
    g.add((CATEGORY[hisco_occupational_category], SKOS['example'], Literal(hisco_occupational_entry_any, hisco_language)))
    
    # not all entries have equivalents in English
    if not hisco_occupational_entry_en:
        continue
    

    g.add((CATEGORY[hisco_occupational_category], SKOS['example'], Literal(hisco_occupational_entry_en, 'en')))
    
    #g.add((CATEGORY[hisco_occupational_category], SKOS['example'], Literal(hisco_occupational_entry_en, 'en')))
    
    # Now let's create the provenance for the titles
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), SKOS['prefLabel'] , Literal(hisco_occupational_entry_en)))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), PROV.wasQuotedFrom, HSRC['hiscoBook']))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), SKOS['closeMatch'], CATEGORY[hisco_occupational_category]))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), SKOS['member'], ENTRY['entryCollection']))
    
    if hisco_status != "0": 
        g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), HISCO.STATUS, Literal(hisco_status)))
    
    if hisco_relation != "0": 
        g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), HISCO.RELATION, Literal(hisco_relation)))
    
    if hisco_product != "0": 
        g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), HISCO.PRODUCT, Literal(hisco_product)))
    

# This takes some time...
# print g.serialize(format='turtle')

with open('rdf/hisco_entry_book.ttl','w') as out:
    g.serialize(out, format='turtle')



# In[ ]:



