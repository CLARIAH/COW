import csv
import os
import rdflib
from iribaker import to_iri

YAML_NAMESPACE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'namespaces.yaml')

FOAF = rdflib.Namespace('http://xmlns.com/foaf/0.1/')
LODE = rdflib.Namespace('http://linkedevents.org/ontology/')
IDS = rdflib.Namespace('http://data.socialhistory.org/resource/ids/')
TIME = rdflib.Namespace('https://www.w3.org/2006/time#')
OWLTIME = rdflib.Namespace("http://www.w3.org/TR/owl-time#")

rdf_graph = rdflib.Graph()

rdf_graph.bind('foaf', FOAF)
rdf_graph.bind('ids', IDS)
rdf_graph.bind('lode', LODE)
rdf_graph.bind('owltime', OWLTIME)

with open("indiv_001smpl.csv") as infile:
    reader = csv.reader(infile)
    header = reader.next()
    for row in reader:
        personid = row[2]
        day = str(row[9]).zfill(2)
        mnth = str(row[10]).zfill(2)
        year = str(row[11]).zfill(2)
        date = "{}-{}-{}".format(year, mnth, day)
        predicate = row[4]
        value = row[5]
        rdf_graph.add((IDS['event/' + personid + "_" + date], rdflib.RDF.type, LODE['Event']))
        rdf_graph.add((IDS['person/' + personid], rdflib.RDF.type, FOAF["Person"]))
        rdf_graph.add((IDS['event/' + personid + "_" + date], LODE['involvedAgent'], IDS['person/' + personid]))
        if day != "00" and mnth != "00":
            rdf_graph.add((IDS['event/' + personid + "_" + date], LODE['atTime'], rdflib.Literal(date, datatype=rdflib.XSD.date)))
        elif year != "00":
            rdf_graph.add((IDS['event/' + personid + "_" + date], LODE['atTime'], rdflib.Literal(str(year), datatype=rdflib.XSD.gYear)))
        else:
            rdf_graph.add((IDS['event/' + personid + "_" + date], LODE['atTime'], rdflib.Literal("unknown")))
        if "name" in predicate:
            rdf_graph.add((IDS['event/' + personid + "_" + date], IDS[predicate], rdflib.Literal(value)))
        else:
            rdf_graph.add((IDS['event/' + personid + "_" + date], IDS[predicate], IDS[predicate +'/' + value]))

with open("indiv_indiv_001smpl.csv") as infile:
    reader = csv.reader(infile)
    header = reader.next()
    for row in reader:
        personid1 = row[2]
        personid2 = row[3]
        day1 = str(row[8]).zfill(2)
        mnth1 = str(row[9]).zfill(2)
        year1 = str(row[10]).zfill(2)
        date1 = "{}-{}-{}".format(year1, mnth1, day1)
        day2 = str(row[11]).zfill(2)
        mnth2 = str(row[12]).zfill(2)
        year2 = str(row[13]).zfill(2)
        date2 = "{}-{}-{}".format(year2, mnth2, day2)
        predicate = row[5]
        # rdf_graph.add((IDS['event/' + personid1 + "_" + date], rdflib.RDF.type, IDS['event/' + personid1))
        rdf_graph.add((IDS['event/' + personid1 + "_" + date1 + "_" + date2], IDS[predicate], IDS['event/' + personid2]))
        # rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], rdflib.RDF.type, LODE['Event']))
        rdf_graph.add((IDS['person/' + personid1], rdflib.RDF.type, FOAF["Person"]))
        rdf_graph.add((IDS['person/' + personid2], rdflib.RDF.type, FOAF["Person"]))
        rdf_graph.add((IDS['event/' + personid2 + "_" + date1 + "_" + date2], LODE['involvedAgent'], IDS['person/' + personid2]))
        if day1 != "00" and mnth1 != "00":
            rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], OWLTIME['hasBeginning'], rdflib.Literal(date, datatype=rdflib.XSD.date)))
        elif year1 != "00":
            rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], OWLTIME['hasBeginning'], rdflib.Literal(str(year), datatype=rdflib.XSD.gYear)))
        else:
            rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], OWLTIME['hasBeginning'], rdflib.Literal("unknown")))
        if day2 != "00" and mnth2 != "00":
            rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], OWLTIME['hasEnd'], rdflib.Literal(date, datatype=rdflib.XSD.date)))
        elif year2 != "00":
            rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], OWLTIME['hasEnd'], rdflib.Literal(str(year), datatype=rdflib.XSD.gYear)))
        else:
            rdf_graph.add((IDS['event/' + personid + "_" + date1 + "_" + date2], OWLTIME['hasEnd'], rdflib.Literal("unknown")))

# ditto for context and context_context and indiv_context

with open("henry_ids_test.ttl", "w") as outfile:
    rdf_graph.serialize(outfile, format="turtle")