import csv
import os
import rdflib

YAML_NAMESPACE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'namespaces.yaml')

FOAF = rdflib.Namespace('http://xmlns.com/foaf/0.1/')
LODE = rdflib.Namespace('http://linkedevents.org/ontology/')
IDS = rdflib.Namespace('http://data.socialhistory.org/resource/ids/')
TIME = rdflib.Namespace('https://www.w3.org/2006/time#')

rdf_graph = rdflib.Graph()

rdf_graph.bind('foaf', FOAF)
rdf_graph.bind('ids', IDS)
rdf_graph.bind('lode', LODE)

with open("../../../../Downloads/data/qqt/Complete_SEDD-IDS_PUBLIC_3_1/Complete_SEDD-IDS_PUBLIC_3_1_smpl.csv") as infile:
    reader = csv.reader(infile)
    for row in reader:
        personid = row[0]
        date = row[1]
        predicate = row[2]
        value = row[3]
        rdf_graph.add((IDS['event/' + personid + "_" + date], rdflib.RDF.type, LODE['Event']))
        rdf_graph.add((IDS['person/' + personid], rdflib.RDF.type, FOAF["Person"]))
        rdf_graph.add((IDS['event/' + personid + "_" + date], LODE['involvedAgent'], IDS['person/' + personid]))
        rdf_graph.add((IDS['event/' + personid + "_" + date], LODE['atTime'], rdflib.Literal(date, datatype=rdflib.XSD.date)))
        rdf_graph.add((IDS['event/' + personid + "_" + date], IDS[predicate], IDS[predicate +'/' + value]))

with open("ids_test.ttl", "w") as outfile:
    rdf_graph.serialize(outfile, format="turtle")

# entirely LODE-based, is a bit cumbersome
# rdf_graph_drc = rdflib.Graph()

# rdf_graph_drc.bind('foaf', FOAF)
# rdf_graph_drc.bind('ids', IDS)
# rdf_graph_drc.bind('lode', LODE)

# with open("../../../../downloads/data/qqt/Complete_SEDD-IDS_PUBLIC_3_1/Complete_SEDD-IDS_PUBLIC_3_1_smpl.csv") as infile:
#     reader = csv.reader(infile)
#     for row in reader:
#         personid = row[0]
#         date = row[1]
#         predicate = row[2]
#         value = row[3]
#         rdf_graph_drc.add((IDS['person/' + personid], IDS[predicate], IDS[predicate + '/' + value]))
#         rdf_graph_drc.add((IDS['person/' + personid], rdflib.RDF.type, FOAF["Person"]))
#         rdf_graph_drc.add((IDS[predicate + '/' + value], LODE['atTime'], rdflib.Literal(date, datatype=rdflib.XSD.date)))

# with open("ids_test_drct.ttl", "w") as outfile:
#     rdf_graph_drc.serialize(outfile, format="turtle")