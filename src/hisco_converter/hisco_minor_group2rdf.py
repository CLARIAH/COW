print "WARNING: This script is deprecated in favour of the CSVW-based converters"
# coding: utf-8

# In[2]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS, URIRef
import csv, os

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/vocab/hisco/')
MAJOR = Namespace('http://data.socialhistory.org/vocab/majorGroup/')
MINOR = Namespace('http://data.socialhistory.org/vocab/minorGroup/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')



g.bind('hisco', HISCO)
g.bind('major', MAJOR)
g.bind('minor', MINOR)
g.bind('skos', SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../sdh-private-hisco-datasets/hisco_2.csv')
hisco = csv.reader(hdf)

next(hisco)


variable_name = 'minorGroup'
g.add((HISCO[variable_name], RDF.type, SKOS['Collection']))
g.add((HISCO[variable_name], SKOS.prefLabel, Literal('minor group')))
g.add((HISCO[variable_name], SKOS.member, HISCO['']))


for row in hisco: # define and columns and names for columns
    hisco_major_group = row[2]
    hisco_minor_group = row[2] + row[1]
    hisco_minor_group_label = row[3].decode('latin-1')
    # hisco_minor_group_description = row[4] # uncomment for actual descriptions
    hisco_minor_group_url = "http://historyofwork.iisg.nl/list_minor.php?text01=" + str(row[2]) + "&&text01_qt=strict"

    g.add((MINOR[hisco_minor_group], RDF.type, SKOS['Collection']))
    g.add((MINOR[hisco_minor_group], SKOS['member'], HISCO[variable_name]))
    g.add((MINOR[hisco_minor_group], SKOS['prefLabel'], Literal(hisco_minor_group_label,'en')))
    # g.add((MINOR[hisco_minor_group], SKOS['definition'], Literal(hisco_minor_group_description,'en'))) # uncomment for actual descriptions
    g.add((MINOR[hisco_minor_group], SKOS.inScheme, HISCO['']))
    g.add((MINOR[hisco_minor_group], SKOS['definition'], URIRef(hisco_minor_group_url)))

    g.add((MINOR[hisco_minor_group],SKOS['broaderTransitive'], MAJOR[hisco_major_group]))

# print g.serialize(format='turtle')

with open('rdf/hisco_minor_group.ttl','w') as out:
    g.serialize(out, format='turtle')


# In[ ]:




# In[ ]:
