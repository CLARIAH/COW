
# coding: utf-8

# In[3]:

from rdflib import Graph, Namespace, RDF, Literal, URIRef
import csv, os

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/ns/vocab/hisco/')
MAJOR = Namespace('http://data.socialhistory.org/ns/vocab/hisco/majorGroup/')
MINOR = Namespace('http://data.socialhistory.org/ns/vocab/hisco/minorGroup/')
UNIT  = Namespace('http://data.socialhistory.org/ns/vocab/hisco/unitGroup/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

g.bind('hisco', HISCO)
g.bind('major', MAJOR)
g.bind('minor', MINOR)
g.bind('unit', UNIT)
g.bind('skos', SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../sdh-private-hisco-datasets/hisco_3.csv')
hisco = csv.reader(hdf)

next(hisco)

variable_name = 'unitGroup'
g.add((HISCO[variable_name], RDF.type, SKOS['Collection']))
g.add((HISCO[variable_name], SKOS.preflabel, Literal('unit group')))
g.add((HISCO[variable_name], SKOS.member, HISCO['conceptScheme'])) 

for row in hisco: # define and columns and names for columns
    hisco_major_group = row[3]
    hisco_minor_group = row[3] + row[2]
    
    hisco_unit_group = row[3] + row[2] + row[1]
    hisco_unit_group_label = row[4]
    # hisco_unit_group_description = row[5].decode('latin-1') # need to decode to avoid error, uncomment for actual descriptions
    hisco_unit_group_url = "http://historyofwork.iisg.nl/list_rubri.php?keywords=" + str(row[3]) + str(row[2]) + "&keywords_qt=lstrict&orderby=keywords"
    
    
    g.add((UNIT[hisco_unit_group], RDF.type, SKOS['Concept']))
    g.add((UNIT[hisco_unit_group], SKOS['inScheme'], HISCO[variable_name]))
    g.add((UNIT[hisco_unit_group], SKOS['prefLabel'], Literal(hisco_unit_group_label,'en')))
    # g.add((UNIT[hisco_unit_group], SKOS['definition'], Literal(hisco_unit_group_description,'en'))) #uncomment for actual descriptions
    g.add((UNIT[hisco_unit_group], SKOS['definition'], URIRef(hisco_unit_group_url)))
    
    g.add((UNIT[hisco_unit_group], SKOS.inScheme, HISCO['conceptScheme']))

    g.add((UNIT[hisco_unit_group],SKOS['broaderTransitive'], MAJOR[hisco_major_group]))
    g.add((UNIT[hisco_unit_group],SKOS['broaderTransitive'], MINOR[hisco_minor_group]))
    
# print g.serialize(format='turtle')

with open('rdf/hisco_unit_group.ttl','w') as out:
    g.serialize(out, format='turtle')


# In[ ]:




# In[ ]:



