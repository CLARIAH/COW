
# coding: utf-8

# In[1]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS
import csv, os

g = Graph()

HISCO = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/')
STATUS  = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/status/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

variable_name = 'STATUS'
g.add((HISCO[variable_name], RDF.type, SKOS['Scheme']))
g.add((HISCO[variable_name], RDFS.label, Literal('STATUS')))

g.bind('hisco', HISCO)
g.bind('status', STATUS)
g.bind('skos', SKOS)

default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
os.chdir(default_path)
hdf = open('./data2rdf/hisco/status.csv')
hisco = csv.reader(hdf)

next(hisco)

for row in hisco:
    hisco_status = row[0]
    hisco_status_label = row[1]

    g.add((STATUS[hisco_status], RDF.type, SKOS['Concept']))
    g.add((STATUS[hisco_status], SKOS['inScheme'], HISCO[variable_name]))
    g.add((STATUS[hisco_status], SKOS['prefLabel'], Literal(hisco_status_label,'en')))

print g.serialize(format='turtle')

with open('./rdf/hisco/hisco_status.ttl','w') as out:
    g.serialize(out, format='turtle')


# In[ ]:




# In[ ]:



