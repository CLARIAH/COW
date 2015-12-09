import rdflib
import csv
import urllib2

h2n = csv.reader(open('../../datasets/hisco/occhisco2hisco.csv'))
# original at https://github.com/rlzijdeman/o-clack 

SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
SDMXMSR = rdflib.Namespace('http://purl.org/linked-data/sdmx/2009/measure#')
QB = rdflib.Namespace('http://purl.org/linked-data/cube#')

HISCOCAT = rdflib.Namespace("http://data.socialhistory.org/vocab/hisco/category/")
HISCO = rdflib.Namespace("http://data.socialhistory.org/vocab/hisco/")
HISCAM = rdflib.Namespace("http://data.socialhistory.org/vocab/hiscam/")
OCCHISCO = rdflib.Namespace("http://data.socialhistory.org/resource/napp/OCCHISCO/")
# TD: enforce common namespaces everywhere somehow?

g = rdflib.Graph()

g.bind('hisco', HISCO)
g.bind('hiscocat', HISCOCAT)
g.bind('hiscam', HISCAM)
g.bind('occhisco', OCCHISCO)
g.bind('skos', SKOS)
g.bind('sdmxmsr', SDMXMSR)
g.bind('qb', QB)

g.add((HISCO['crosswalk'], rdflib.RDF.type, SKOS['Scheme']))

h2n.next()

for row in h2n:
    occhisco_code = row[1]
    hisco_code = row[4].zfill(5)
    exactmatch = int(row[5])

    g.add((OCCHISCO[occhisco_code], rdflib.RDF.type, SKOS['Concept']))
    g.add((OCCHISCO[occhisco_code], SKOS['inScheme'], OCCHISCO['occhis2hisco']))
    if exactmatch==1:
        g.add((OCCHISCO[occhisco_code], SKOS['exactMatch'], HISCOCAT[hisco_code]))
    else:
        g.add((OCCHISCO[occhisco_code], SKOS['closeMatch'], HISCOCAT[hisco_code]))
    if row[7]!="":
        g.add((OCCHISCO[occhisco_code], SKOS['note'], rdflib.Literal(row[7])))

with open('rdf/occhisco2hisco.ttl', 'w') as outfile:
    g.serialize(outfile, format='turtle')