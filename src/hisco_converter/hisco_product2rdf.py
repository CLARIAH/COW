
# coding: utf-8

# In[1]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS
import csv, os

g = Graph()

HISCO = Namespace('http://data.socialhistory.org/vocab/hisco/')
PRODUCT = Namespace('http://data.socialhistory.org/vocab/hisco/product/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

variable_name = 'productCollection'
g.add((PRODUCT[variable_name], RDF.type, SKOS['Collection']))
g.add((PRODUCT[variable_name], RDFS.label, Literal('PRODUCT')))
g.add((PRODUCT[variable_name], SKOS.definition, Literal('PRODUCT is a subsidiary classification designed to reduce the loss '+
                                                            'of information caused by ISCO68\'s failure in some cases ' +
                                                            '(especially in relation to major group 4) to accomodate ' + 
                                                            'information on products traded by those in particular occupational '+
                                                            'categories.')))

g.bind('hisco', HISCO)
g.bind('product', PRODUCT)
g.bind('skos', SKOS)

# default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
# os.chdir(default_path)
hdf = open('../../sdh-private-hisco-datasets/product.csv')
hisco = csv.reader(hdf)

next(hisco)

for row in hisco:
    hisco_product = row[0]
    hisco_product_label = row[1]

    g.add((PRODUCT[hisco_product], RDF.type, SKOS['Concept']))
    g.add((PRODUCT[hisco_product], SKOS['inScheme'], HISCO['hiscoScheme']))
    g.add((PRODUCT[hisco_product], SKOS['member'], HISCO[variable_name]))  
    g.add((PRODUCT[hisco_product], SKOS['prefLabel'], Literal(hisco_product_label,'en')))
    
# print g.serialize(format='turtle')

with open('rdf/hisco_product.ttl','w') as out:
    g.serialize(out, format='turtle')




# In[ ]:




# In[ ]:



