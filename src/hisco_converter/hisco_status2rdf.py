
# coding: utf-8

# In[10]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS
import csv, os

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/vocab/hisco/')
STATUS  = Namespace('http://data.socialhistory.org/vocab/hisco/status/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

variable_name = 'statusCollection'
g.add((STATUS[variable_name], RDF.type, SKOS['Collection']))
g.add((STATUS[variable_name], RDFS.label, Literal('STATUS')))
g.add((STATUS[variable_name], SKOS.definition, Literal('STATUS is a subsidiary classification designed to reduce the loss '+
                                                            'of information caused by ISCO68\'s failure to accomodate residual ' +
                                                            'information about employment status, educational qualifications, ' + 
                                                            'and social position.')))


g.bind('hisco', HISCO)
g.bind('status', STATUS)
g.bind('skos', SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../datasets/hisco/status.csv')
hisco = csv.reader(hdf)

next(hisco)

for row in hisco:
    hisco_status = row[0]
    hisco_status_label = row[1]

    g.add((STATUS[hisco_status], RDF.type, SKOS['Concept']))
    g.add((STATUS[hisco_status], SKOS['inScheme'], HISCO['hiscoScheme']))
    g.add((STATUS[hisco_status], SKOS['member'], HISCO[variable_name]))  
    g.add((STATUS[hisco_status], SKOS['prefLabel'], Literal(hisco_status_label,'en')))

# print g.serialize(format='turtle')

with open('rdf/hisco_status.ttl','w') as out:
    g.serialize(out, format='turtle')


# In[ ]:




# In[ ]:



