
# coding: utf-8

# In[1]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS, URIRef
import csv

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/ns/vocab/hisco/')
MAJOR = Namespace('http://data.socialhistory.org/ns/vocab/hisco/majorGroup/')
MINOR = Namespace('http://data.socialhistory.org/ns/vocab/hisco/minorGroup/')
UNIT  = Namespace('http://data.socialhistory.org/ns/vocab/hisco/unitGroup/')
CATEGORY = Namespace('http://data.socialhistory.org/ns/vocab/hisco/category/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

g.bind('hisco', HISCO)
g.bind('major', MAJOR)
g.bind('minor', MINOR)
g.bind('unit',  UNIT)
g.bind('category', CATEGORY)
g.bind('skos',  SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../sdh-private-hisco-datasets/hisco_45.csv')

hisco = csv.reader(hdf)
next(hisco)

variable_name = 'category'
g.add((HISCO[variable_name], RDF.type, SKOS['Collection']))
g.add((HISCO[variable_name], RDFS.label, Literal('occupational category')))
g.add((HISCO[variable_name], SKOS.member, HISCO['hiscoScheme'])) 


for row in hisco: # define and columns and names for columns
    if len(row[1]) == 1: # some zero's missing
        row[1] = "0" + row[1]
   
    hisco_occupational_category = row[4] + row[3] + row[2] + row[1]
    hisco_major_group = row[4]
    hisco_minor_group = row[4] + row[3]
    
    hisco_unit_group = row[4] + row[3] + row[2]
    hisco_occupational_category_label = row[5].decode('latin-1') # need to decode to avoid error
    # hisco_occupational_category_description = row[6].decode('latin-1') # need to decode to avoid error, uncomment for descriptions
    hisco_occupational_category_url = "http://historyofwork.iisg.nl/list_micro.php?keywords=" + str(row[4]) + str(row[3]) + str(row[2]) + "&keywords_qt=lstrict"
    
    g.add((CATEGORY[hisco_occupational_category], RDF.type, SKOS['Concept']))
    g.add((CATEGORY[hisco_occupational_category], SKOS['inScheme'], HISCO[variable_name]))
    g.add((CATEGORY[hisco_occupational_category], SKOS['prefLabel'], Literal(hisco_occupational_category_label,'en')))
    # g.add((CATEGORY[hisco_occupational_category], SKOS['definition'], Literal(hisco_occupational_category_description,'en'))) # uncomment for descriptions
    g.add((CATEGORY[hisco_occupational_category], SKOS['definition'], URIRef(hisco_occupational_category_url)))

    g.add((CATEGORY[hisco_occupational_category], SKOS['broaderTransitive'], MAJOR[hisco_major_group]))
    g.add((CATEGORY[hisco_occupational_category], SKOS['broaderTransitive'], MINOR[hisco_minor_group]))
    g.add((CATEGORY[hisco_occupational_category], SKOS['broaderTransitive'], UNIT[hisco_unit_group]))
    
# print g.serialize(format='turtle')

with open('rdf/hisco_category.ttl','w') as out:
    g.serialize(out, format='turtle')



# In[ ]:



