
# coding: utf-8

# In[38]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS, URIRef
import csv, os, iribaker

g = Graph()

HISCO = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/')
MAJOR = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/majorGroup/')
MINOR = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/minorGroup/')
UNIT  = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/unitGroup/')
CATEGORY = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/category/')
STATUS  = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/status/')
RELATION  = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/relation/')
PRODUCT = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/product/')
ENTRY = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/entry/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')
HSRC    = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/resource/')
PROV    = Namespace('http://www.w3.org/ns/prov/')
# BIBO    = Namespace('http://purl.org/ontology/bibo/')
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

g.add((HSRC['hiscoBook'], RDF.type, FABIO['Book']))
g.add((HSRC['hiscoBook'], FABIO.has_ISBN, Literal('urn:isbn:9789058671967')))
g.add((ENTRY[''], RDF.type, SKOS['ConceptScheme']))
g.add((ENTRY[''], SKOS.definition, Literal('A hisco:entry is a recording of an occupational activity in a register, '+
                                          'such as a marriage record or census enumerator\'s book.')))
                                          
g.add((ENTRY[''], SKOS.scopeNote, Literal('''While some hisco:entry\'s are correctly spelled occupations, e.g. "butcher", 
                                          "historian", or "architect", most recordings of occupational activity 
                                          will contain spelling errors, other recordings, multiple recordings 
                                          or elaborative recordings, such as "nurse in St. Mary\'s hospital". 
                                          All of these are considered to be hisco:entry\'s, thus even if they cannot
                                          be (easily) linked to an occupation. Examples of hisco:entry\'s from the
                                          hsrc:hiscoBook are clean and referred to as skos:example. All other
                                          entries are instances of skos:hiddenLabel''')))


default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
os.chdir(default_path)

hdf = open('./data2rdf/hisco/occupation_link.csv')
hisco = csv.reader(hdf)

next(hisco)



for row in hisco: # define and columns and names for columns
    if len(row[0]) == 4: # some zero's missing
        row[0] = "0" + row[0]

    hisco_occupational_category  = row[6].decode('latin-1')
    hisco_occupational_entry_any = row[1].decode('latin-1').lower()
    hisco_occupational_entry_en  = row[2].decode('latin-1').lower()
    hisco_country   = row[3].decode('latin-1').lower()
    hisco_language  = row[4].decode('latin-1').lower()
    if hisco_language == 'uk':
        hisco_language = 'en'
    
    g.add((CATEGORY[hisco_occupational_category], RDF.type, SKOS['Concept']))
    g.add((CATEGORY[hisco_occupational_category], SKOS['inScheme'], HISCO['ENTRY']))
    g.add((CATEGORY[hisco_occupational_category], SKOS['example'], Literal(hisco_occupational_entry_any, hisco_language)))
    
    if hisco_occupational_entry_en: # not all entries have equivalents in English
        g.add((CATEGORY[hisco_occupational_category], SKOS['example'], Literal(hisco_occupational_entry_en, 'en')))
            
    # Now let's create the provenance for the titles
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), SKOS['prefLabel'] , Literal(hisco_occupational_entry_en)))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), PROV.wasQuotedFrom, HSRC['hiscoBook']))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry_en)), SKOS['closeMatch'], HSRC['hiscoBook']))
                

# This takes some time...
print g.serialize(format='turtle')

with open('./rdf/hisco/hisco_entry_book.ttl','w') as out:
    g.serialize(out, format='turtle')


# In[ ]:



