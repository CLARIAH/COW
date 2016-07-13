
# coding: utf-8

# In[2]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS
import csv, os

g = Graph()

HISCO     = Namespace('http://data.socialhistory.org/ns/vocab/hisco/')
RELATION  = Namespace('http://data.socialhistory.org/ns/vocab/hisco/relation/')
SKOS      = Namespace('http://www.w3.org/2004/02/skos/core#')

variable_name = 'relationCollection'
g.add((RELATION[variable_name], RDF.type, SKOS['Collection']))
g.add((RELATION[variable_name], RDFS.label, Literal('RELATION')))
g.add((RELATION[variable_name], SKOS.definition, Literal('RELATION is a subsidiary classification designed to reduce the loss '+
                                                            'of information caused by ISCO68\'s failure to accomodate residual ' +
                                                            'information about people who do not give a current occupational ' + 
                                                            'title, but who nevertheless indicate a relationship to the formal' +
                                                            'labour market.')))

g.bind('hisco', HISCO)
g.bind('relation', RELATION)
g.bind('skos', SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../sdh-private-hisco-datasets/relation.csv')
hisco = csv.reader(hdf)

next(hisco)

for row in hisco:
    hisco_relation = row[0]
    hisco_relation_label = row[1]

    g.add((RELATION[hisco_relation], RDF.type, SKOS['Concept']))
    g.add((RELATION[hisco_relation], SKOS['inScheme'], HISCO['hiscoScheme']))
    g.add((RELATION[hisco_relation], SKOS['member'], HISCO[variable_name]))  
    g.add((RELATION[hisco_relation], SKOS['prefLabel'], Literal(hisco_relation_label,'en')))

# print g.serialize(format='turtle')

with open('rdf/hisco_relation.ttl','w') as out:
    g.serialize(out, format='turtle')



# In[ ]:



