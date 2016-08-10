import os
import datetime
import csv
import json
import logging
import re
import iribaker
import traceback
import rfc3987
from util import get_namespaces, Nanopublication, QB, RDF, OWL, SKOS, XSD, SDV, SDR, PROV, namespaces
from rdflib import Namespace, URIRef, Literal



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def build_schema(infile, outfile, delimiter=',', quotechar='\"', dataset_name=None):
    url = os.path.basename(infile)
    # Get the current date and time (UTC)
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    if dataset_name is None:
        dataset_name = url

    metadata = {
        "@context": ["http://www.w3.org/ns/csvw", {"@language": "en", "@base": "http://data.socialhistory.org/ns/resource/"}, get_namespaces()],
        "url": url,
        "dc:title": dataset_name,
        "dcat:keyword": [],
        "dc:publisher": {
            "schema:name": "CLARIAH Structured Data Hub - Datalegend",
            "schema:url": {"@id": "http://datalegend.org"}
        },
        "dc:license": {"@id": "http://opendefinition.org/licenses/cc-by/"},
        "dc:modified": {"@value": today, "@type": "xsd:date"},
        "tableSchema": {
            "columns": [],
            "primaryKey": None,
            "aboutUrl": "{_row}"
        }
    }

    with open(infile, 'r') as infile_file:
        r = csv.reader(infile_file, delimiter=delimiter, quotechar=quotechar)

        header = r.next()

        print header

        # First column is primary key
        metadata['tableSchema']['primaryKey'] = header[0]

        for head in header:
            col = {
                "name": head,
                "titles": [head],
                "dc:description": head,
                "datatype": "string"
            }

            metadata['tableSchema']['columns'].append(col)

    with open(outfile, 'w') as outfile_file:
        outfile_file.write(json.dumps(metadata, indent=True))

    logger.info("Done")
    return




class CSVWConverter(object):

    def __init__(self, file_name):

        self.file_name = file_name
        self.np = Nanopublication(file_name)

        schema_file_name = file_name + '-metadata.json'
        metadata = json.load(open(schema_file_name,'r'))

        self.base = metadata['@context'][1]['@base']
        self.BASE = Namespace(self.base)
        self.schema = metadata['tableSchema']

        namespaces.update({ns: url for ns, url in metadata['@context'][1].items() if not ns.startswith('@')})

        self.aboutURLSchema = self.schema['aboutUrl']
        self.columns = self.schema['columns']


    def convert(self):
        logger.info("Starting conversion")
        with open(self.file_name) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                for c in self.columns:
                    # default
                    s = self.expandURL(self.aboutURLSchema, row)

                    try:
                        if 'valueUrl' in c:
                            # This is an object property
                            if 'virtual' in c and c['virtual'] and 'aboutUrl' in c:
                                s = self.expandURL(c['aboutUrl'], row)

                            p = self.expandURL(c['propertyUrl'], row)
                            o = self.expandURL(c['valueUrl'], row)
                        else:
                            # This is a datatype property

                            value = row[c['name']].decode('latin')
                            if len(value) == 0:
                                # Skip value if length is zero
                                continue

                            # If propertyUrl is specified, use it, otherwise use the column name
                            if 'propertyUrl' in c:
                                p = self.expandURL(c['propertyUrl'], row)
                            else :
                                p = self.expandURL(c['name'], row)

                            if 'datatype' in c:
                                if c['datatype'] == 'string' and 'lang' in c:
                                    # If it is a string datatype that has a language, we turn it into a language tagged literal
                                    o = Literal(value, lang=c['lang'])
                                elif isinstance(c['datatype'], dict) :
                                    # If it is a restricted datatype, we only use its base
                                    dt = self.expandURL(c['datatype']['base'], row, datatype=True)
                                    o = Literal(value, datatype=dt)
                                else:
                                    # Otherwise we just use the datatype specified
                                    dt = self.expandURL(c['datatype'], row, datatype=True)
                                    o = Literal(value, datatype=dt)
                            else:
                                # It's just a plain literal without datatype.
                                o = Literal(value)

                        # Add the triple to the assertion graph
                        self.np.ag.add((s, p, o))
                    except Exception as e:
                        print row['auto_id'], value
                        traceback.print_exc()
        logger.info("... done")

    def serialize(self):
        trig_file_name = self.file_name + '.trig'
        logger.info("Starting serialization to {}".format(trig_file_name))

        with open(trig_file_name, 'w') as f:
            self.np.serialize(f, format='trig')
        logger.info("... done")

    def expandURL(self, url, row, datatype=False):
        # TODO This should take into account the special CSVW instructions such as {_row}
        url = url.format(**row)


        for ns, nsuri in namespaces.items():
            if url.startswith(ns):
                url = url.replace(ns + ':', nsuri)
                break

        try:
            rfc3987.parse(url, rule='IRI')
            iri = iribaker.to_iri(url)
        except:
            try:
                if datatype==False:
                    fullurl = self.base + url
                else:
                    # TODO: This should include the custom namespaces as defined in the CSVW spec
                    fullurl = namespaces['xsd'] + url

                rfc3987.parse(fullurl, rule='IRI')
                iri = iribaker.to_iri(fullurl)
            except:
                raise Exception("Cannot convert `{}` to valid IRI".format(url))

        # print "Baked: ", iri
        return URIRef(iri)
