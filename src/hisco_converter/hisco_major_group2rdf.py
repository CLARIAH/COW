print "WARNING: This script is deprecated in favour of the CSVW-based converters"
# coding: utf-8

# In[3]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS, URIRef
import csv, os

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/vocab/hisco/')
MAJOR = Namespace('http://data.socialhistory.org/vocab/hisco/majorGroup/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

g.bind('hisco', HISCO)
g.bind('major', MAJOR)
g.bind('skos', SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../sdh-private-hisco-datasets/hisco_1.csv')
hisco = csv.reader(hdf)

next(hisco)

g.add((HISCO['hiscoScheme'], RDF.type, SKOS['ConceptScheme']))

variable_name = 'majorGroup'
g.add((HISCO[variable_name], RDF.type, SKOS['Collection']))
g.add((HISCO[variable_name], SKOS.prefLabel, Literal('major group','en')))
g.add((HISCO[variable_name], SKOS.editorialNote,
       Literal("For consistency with categories, unit groups and minor groups, the major groups '0/1' and '7/8/9' are split and treated as seperate major groups: 0,1,7,8,9",'en')))
#g.add((HISCO[variable_name], SKOS.inScheme, HISCO['']))



for row in hisco: # define and columns and names for columns
    hisco_major_group = row[1]
    hisco_major_group_label = row[2]
#    hisco_major_group_description = row[3] # uncomment for actual descriptions of major group 3
    #hisco_major_group_url = "http://historyofwork.iisg.nl/list_minor.php?text01=" + str(row[1]) + "&&text01_qt=strict"

    # http://historyofwork.iisg.nl/list_minor.php?text01=3&&text01_qt=strict


    g.add((MAJOR[hisco_major_group], RDF.type, SKOS['Concept']))
    g.add((MAJOR[hisco_major_group], SKOS['member'], HISCO[variable_name]))
    g.add((MAJOR[hisco_major_group], SKOS['prefLabel'], Literal(hisco_major_group_label,'en')))
    # g.add((MAJOR[hisco_major_group], SKOS['definition'], Literal(hisco_major_group_description,'en')))  # uncomment for actual descriptions of major group 3
    g.add((MAJOR[hisco_major_group], SKOS['definition'], URIRef('http://historyofwork.iisg.nl/major.php')))

    g.add((MAJOR[hisco_major_group], SKOS.inScheme, HISCO['hiscoScheme']))


# print g.serialize(format='turtle')

with open('rdf/hisco_major_group.ttl','w') as out:
    g.serialize(out, format='turtle')


# In[ ]:




# In[ ]:




# In[ ]:
