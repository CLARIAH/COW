
# coding: utf-8

# In[1]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS
import csv, os

g = Graph()

HISCO = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/')
RELATION  = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/relation/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

variable_name = 'RELATION'
g.add((HISCO[variable_name], RDF.type, SKOS['Scheme']))
g.add((HISCO[variable_name], RDFS.label, Literal('RELATION')))

g.bind('hisco', HISCO)
g.bind('relation', RELATION)
g.bind('skos', SKOS)

default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
os.chdir(default_path)
hdf = open('./data2rdf/hisco/relation.csv')
hisco = csv.reader(hdf)

next(hisco)

for row in hisco:
    hisco_relation = row[0]
    hisco_relation_label = row[1]

    g.add((RELATION[hisco_relation], RDF.type, SKOS['Concept']))
    g.add((RELATION[hisco_relation], SKOS['inScheme'], HISCO[variable_name]))
    g.add((RELATION[hisco_relation], SKOS['prefLabel'], Literal(hisco_relation_label,'en')))

print g.serialize(format='turtle')

with open('./rdf/hisco/hisco_relation.ttl','w') as out:
    g.serialize(out, format='turtle')



# In[ ]:



