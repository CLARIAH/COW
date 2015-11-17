import csv
import rdflib as rdf

CLIOIND = rdf.Namespace('http://data.socialhistory.org/resource/clio/indicator/')
CLIOPROP = rdf.Namespace('http://data.socialhistory.org/resource/clio/property/')
CLIOCTR = rdf.Namespace('http://data.socialhistory.org/resource/clio/country/')
CLIO = rdf.Namespace('http://data.socialhistory.org/resource/clio/')
QB = rdf.Namespace('http://purl.org/linked-data/cube#')
SKOS = rdf.Namespace('http://www.w3.org/2004/02/skos/core#')
SDMX = rdf.Namespace('http://purl.org/linked-data/sdmx#')
SDMXMSR = rdf.Namespace('http://purl.org/linked-data/sdmx/2009/measure#')
SDMXDIM = rdf.Namespace('http://purl.org/linked-data/sdmx/2009/dimension#')

g = rdf.Graph()

g.bind('clio-property', CLIOPROP)
g.bind('clio-indicator', CLIOIND)
g.bind('clio-country', CLIOCTR)
g.bind('clio', CLIO)
g.bind('qb', QB)
g.bind('skos', SKOS)
g.bind('sdmx', SDMX)
g.bind('sdmx-dimension', SDMXDIM)
g.bind('sdmx-measure', SDMXMSR)

bn = rdf.BNode()

g.add((CLIO['dsd'], rdf.RDF.type, QB['DataStructureDefinition']))
g.add((CLIO['dsd'], QB['component'], bn))
g.add((bn, QB['dimension'], CLIO['refArea']))
g.add((bn, QB['dimension'], CLIO['refPeriod']))
# g.add((bn, QB['measure'], CLIO['gdppc']))
# cube:order->int 
# and rdf:type->cube:ComponentSpecification

g.add((CLIO['gdppc'], rdf.RDF.type, QB['DataSet']))
g.add((CLIO['gdppc'], rdf.RDFS.label, rdf.Literal('GDP per capita in 1990 $GK')))
g.add((CLIO['gdppc'], QB['structure'], CLIO['dsd']))

g.add((CLIOIND['GDPPC1990GKD'], SKOS['prefLabel'], rdf.Literal('GDP per capita, PPP (contant 1990 internaiontal GK dollars)', lang='en')))
g.add((CLIOIND['GDPPC1990GKD'], SKOS['defintion'], rdf.Literal("GDP per capita based on purchasing power parity (PPP). PPP GDP is gross domestic product converted to international dollars using purchasing power parity rates. An international dollar has the same purchasing power over GDP as the U.S. dollar has in the United States. GDP at purchaser's prices is the sum of gross value added by all resident producers in the economy plus any product taxes and minus any subsidies not included in the value of the products. It is calculated without making deductions for depreciation of fabricated assets or for depletion and degradation of natural resources. Data are in constant 1990 international dollars.", lang='en')))
g.add((CLIOIND['GDPPC1990GKD'], rdf.RDF.type, SDMX['ConceptRole']))
# g.add((CLIO['indicator/' + 'GDPPC1990GKD'], SKOS['inScheme'], CLIO['classification/indicators']))
# followed by CLIO['classification/indicators'], a, Concept Scheme and list of all clio indicators
g.add((CLIOIND['GDPPC1990GKD'], rdf.RDF.type, SKOS['Concept']))

with open('allcliodata_raw.csv', 'rb') as infile:
    lines = csv.reader(infile)
    header = next(lines)
    for row in lines:
        obsid = str(row[0]) + str(row[1])
        if row[3] == 'NA':
            continue
        g.add((CLIO[obsid], rdf.RDF.type, QB['Observation']))
        g.add((CLIO[obsid], QB['dataSet'], CLIO['gdppc']))

        g.add((CLIO[obsid], SDMXDIM['refArea'], CLIOCTR[row[0]]))
        g.add((CLIO[obsid], SDMXDIM['refPeriod'], rdf.Literal(row[1], datatype=rdf.XSD.gYear)))

        g.add((CLIO[obsid], SDMXMSR['obsValue'], rdf.Literal(float(row[3]))))
        g.add((CLIO[obsid], CLIOPROP['indicator'], CLIOIND['GDPPC1990GKD']))

with open('qbcliogdp.ttl', 'w') as outfile:
    g.serialize(outfile, format='turtle')