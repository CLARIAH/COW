from rdflib import Graph, Namespace, Literal, URIRef
import csv, iribaker, io, codecs, cStringIO, warnings

warnings.warn('This script has an decoding issue, leading to' 
              'a illegal character. Use "rapper -c -i turtle <file>"'
              'to find and code the mistake and'
              ' mannually uncomment ("#") the .ttl file')

g = Graph()

CATEGORY = Namespace('http://data.socialhistory.org/vocab/hisco/category/')
ENTRY    = Namespace('http://data.socialhistory.org/vocab/hisco/entry/')
SKOS     = Namespace('http://www.w3.org/2004/02/skos/core#')
PROV     = Namespace('http://www.w3.org/ns/prov#')

g.bind('cat'  , CATEGORY)
g.bind('skos' , SKOS)
g.bind('entry', ENTRY)
g.bind('prov' , PROV)

hsn = open('../../sdh-public-datasets/hsn2013a_hisco_comma.csv')
hisco = csv.reader(hsn)

##  attempt 1: using io
#with io.open('../../sdh-public-datasets/hsn2013a_hisco_comma.csv', 'r', encoding = 'utf8') as f:
#    hisco = f.read()
# apparently results in a string, rather than an iterable file ???


## attempt 2: using UnicodeReader, works in principle 
## but throws all kinds of turtle/N3 errors

#class UnicodeReader:
#        """
#        A CSV reader which will iterate over lines in the CSV file "f",
#        which is encoded in the given encoding.
#        """
#
#        def __init__(self, hisco, dialect=csv.excel, encoding="utf-8", **kwds):
#            f = UTF8Recoder(hisco, encoding)
#            self.reader = csv.reader(hisco, dialect=dialect, **kwds)
#
#        def next(self):
#            row = self.reader.next()
#            return [unicode(s, "utf-8") for s in row]
#
#        def __iter__(self):
#            return self


next(hisco)
    

for row in hisco: # define and columns and names for columns
    if len(row[3]) == 4: # some zero's missing
        row[0] = "0" + row[0]
    
    hisco_occupational_category = row[3].decode('utf-8')
    hisco_occupational_entry = row[1].decode('utf-8').lower()
    hisco_occupational_standard = row[2].decode('utf-8').lower()

    hisco_status = row[4]
    hisco_relation = row[5]
    hisco_product = row[6]
    hisco_provenance = row[12] 
    
    # print URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry))
                 
    g.add((CATEGORY[hisco_occupational_category], SKOS['hiddenLabel'], Literal(hisco_occupational_entry, 'nl')))
    g.add((CATEGORY[hisco_occupational_category], SKOS['prefLabel'],   Literal(hisco_occupational_standard, 'nl')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), PROV.wasQuotedFrom, URIRef('http://hdl.handle.net/10622/UQJZKJ')))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['closeMatch'], CATEGORY[hisco_occupational_category]))
    g.add((URIRef(iribaker.to_iri(ENTRY + hisco_occupational_entry)), SKOS['member'], ENTRY['entryCollection']))



with open('rdf/hsn_hisco_entry_2013a.ttl','w') as out: 
    g.serialize(out, format='turtle')
