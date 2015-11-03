
# coding: utf-8

# In[2]:

from rdflib import Graph, Namespace, RDF, Literal, RDFS
import csv, os

g = Graph()

HISCO = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/')
PRODUCT = Namespace('http://qber.data2semantics.org/vocab/ocs/hisco/product/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')

variable_name = 'PRODUCT'
g.add((HISCO[variable_name], RDF.type, SKOS['Scheme']))
g.add((HISCO[variable_name], RDFS.label, Literal('PRODUCT')))

g.bind('hisco', HISCO)
g.bind('product', PRODUCT)
g.bind('skos', SKOS)

default_path = "/Users/RichardZ/Dropbox/II/projects/clariah/sdh/basecamp/Files/Files attached directly to project/Files attached directly to project (1)/"
os.chdir(default_path)
hdf = open('./data2rdf/hisco/product.csv')
hisco = csv.reader(hdf)

next(hisco)

for row in hisco:
    hisco_product = row[0]
    hisco_product_label = row[1]

    g.add((PRODUCT[hisco_product], RDF.type, SKOS['Concept']))
    g.add((PRODUCT[hisco_product], SKOS['inScheme'], HISCO[variable_name]))
    g.add((PRODUCT[hisco_product], SKOS['prefLabel'], Literal(hisco_product_label,'en')))

print g.serialize(format='turtle')

with open('./rdf/hisco/hisco_product.ttl','w') as out:
    g.serialize(out, format='turtle')




# In[ ]:




# In[ ]:



