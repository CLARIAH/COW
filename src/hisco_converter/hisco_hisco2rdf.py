
# coding: utf-8

# In[1]:

from rdflib import Graph, Namespace, RDF, Literal, XSD
import csv, datetime, os

g = Graph()

HISCO   = Namespace('http://data.socialhistory.org/vocab/hisco/')
HSRC    = Namespace('http://data.socialhistory.org/vocab/hisco/resource/')
STAFF   = Namespace('http://data.socialhistory.org/staff/csdh/')
SKOS    = Namespace('http://www.w3.org/2004/02/skos/core#')
PROV    = Namespace('http://www.w3.org/ns/prov#')
DC      = Namespace('http://purl.org/dc/elements/1.1/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
FABIO   = Namespace('http://purl.org/spar/fabio/')
FOAF    = Namespace('http://xmlns.com/foaf/0.1/')

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)

g.bind('hisco', HISCO)
g.bind('hsrc', HSRC)
g.bind('skos', SKOS)
g.bind('prov', PROV)
g.bind('dc', DC)
g.bind('dcterms', DCTERMS)
g.bind('fabio', FABIO)
g.bind('foaf', FOAF)

g.add((HISCO['hiscoScheme'], RDF.type, SKOS['ConceptScheme']))
g.add((HISCO['hiscoScheme'], RDF.type, PROV['Entity']))
g.add((HISCO['hiscoScheme'], PROV.wasAttributedTo, STAFF['rlzijdeman']))
g.add((HISCO['hiscoScheme'], DCTERMS.title, Literal('Historical International Standard Classification of Occupations', 'en')))
g.add((HISCO['hiscoScheme'], PROV.wasDerivedFrom, HSRC['hiscoBook']))
g.add((HISCO['hiscoScheme'], PROV.wasDerivedFrom, HSRC['hiscoWebsite']))
g.add((HSRC['hiscoBook'], RDF.type, FABIO['Book']))
g.add((HSRC['hiscoBook'], FABIO.has_ISBN, Literal('9789058671967')))
g.add((HSRC['hiscoWebsite'], RDF.type, FABIO['Website']))
g.add((HSRC['hiscoWebsite'], RDF.about, Literal('http://historyofwork.iisg.nl')))

g.add((STAFF['rlzijdeman'], RDF.ID, Literal('http://orcid.org/0000-0003-0782-2704')))
g.add((STAFF['rlzijdeman'], RDF.ID, Literal('info:eu-repo/dai/nl/304832960')))
g.add((STAFF['rlzijdeman'], RDF.ID, Literal('http://isni.org/isni/000000010711579X')))

g.add((STAFF['rlzijdeman'], RDF.type, PROV['Person']))
g.add((STAFF['rlzijdeman'], RDF.type, PROV['Agent']))
g.add((STAFF['rlzijdeman'], RDF.type, FOAF['Person']))
g.add((STAFF['rlzijdeman'], RDF.type, FOAF['Agent']))
g.add((STAFF['rlzijdeman'], FOAF.givenName, Literal('Richard')))
g.add((STAFF['rlzijdeman'], FOAF.familyName, Literal('Zijdeman')))
g.add((STAFF['rlzijdeman'], FOAF.mbox, Literal('mailto:richard.zijdeman@iisg.nl')))

g.add((HSRC['hisco2rdf_01'], RDF.type, PROV.Activity))
g.add((HSRC['hisco2rdf_01'], PROV.startedAtTime, Literal('2015-06-10T12:05:00+02:00', datatype = XSD.dateTime)))
g.add((HSRC['hisco2rdf_01'], PROV.endedAtTime, 
       Literal(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S+02:00'),datatype = XSD.dateTime)))
fileout = 'rdf/hisco_hisco.ttl'
g.add((HSRC['hisco2rdf_01'], PROV.generated, Literal(fileout)))

# print g.serialize(format='turtle')

with open(fileout,'w') as out:
    g.serialize(out, format='turtle')


# In[ ]:




# In[ ]:



