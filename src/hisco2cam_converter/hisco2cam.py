import requests
import bs4
import re
import csv
import rdflib
import urllib2
import json

baseurl = "http://www.camsis.stir.ac.uk/hiscam/v1_3_1/"

soup = bs4.BeautifulSoup(requests.get(baseurl).text, "html5lib")

csvs = {}
for lnk in soup.find_all('a', {'href': re.compile("dat")}):
    print(baseurl + lnk['href'])
    dat = csv.reader(urllib2.urlopen(baseurl + lnk['href'], 'rU'), delimiter='\t')
    csvs[re.sub('.*_|.dat', '', lnk['href'])] = dat

HISCO = rdflib.Namespace("http://qber.data2semantics.org/vocab/ocs/hisco/category/")
HISCAM = rdflib.Namespace("http://qber.data2semantics.org/vocab/ocs/hiscam/")
SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
PROV = rdflib.Namespace("http://www.w3.org/ns/prov/")
SDMXMSR = rdflib.Namespace('http://purl.org/linked-data/sdmx/2009/measure#')
QB = rdflib.Namespace('http://purl.org/linked-data/cube#')

g = rdflib.Graph()

g.bind('hisco', HISCO)
g.bind('hiscam', HISCAM)
g.bind('skos', SKOS)
g.bind('sdmxmsr', SDMXMSR)
g.bind('qb', QB)
g.bind('prov', PROV)

for key, dat in csvs.items():
    g.add((HISCAM[key + 'hiscam'], rdflib.RDF.type, SKOS['Scheme']))
    g.add((HISCAM[key + 'hiscam'], PROV["wasDerivedFrom"], rdflib.Literal("http://www.camsis.stir.ac.uk/hiscam/v1_3_1/")))
    
    dat.next()
    for row in dat:
        obsid = row[0] + key
        hisco_code = row[0].zfill(5)
        hiscam_score = float(row[1])

        # g.add((HISCO[hisco_code], rdflib.RDF.type, SKOS['Concept']))
        g.add((HISCO[obsid], HISCO['hiscoCode'], HISCO[hisco_code]))
        g.add((HISCO[obsid], SKOS['inScheme'], HISCAM[key + 'hiscam']))
        g.add((HISCO[obsid], HISCAM['hiscamValue'], rdflib.Literal(hiscam_score)))
        g.add((HISCO[obsid], SDMXMSR['obsValue'], rdflib.Literal(hiscam_score)))
        g.add((HISCO[obsid], QB['refArea'], HISCAM[key.upper()]))

 
with open("hiscamlbls.json") as infile:
    labels = json.load(infile)

for key in labels:
    g.add((HISCAM[key], SKOS['prefLabel'], rdflib.Literal(labels[key])))

with open('hisco2hiscam.ttl', 'w') as outfile:
    g.serialize(outfile, format='turtle')