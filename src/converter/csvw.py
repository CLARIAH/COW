import os
import datetime
import csv
import json
import logging
import re
import iribaker
import traceback
import rfc3987
from jinja2 import Template
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
        metadata = json.load(open(schema_file_name, 'r'))

        self.base = metadata['@context'][1]['@base']
        self.BASE = Namespace(self.base)
        self.schema = metadata['tableSchema']

        # The metadata schema overrides the default namespace values
        # (NB: this does not affect the predefined Namespace objects!)
        namespaces.update({ns: url for ns, url in metadata['@context'][1].items() if not ns.startswith('@')})

        self.templates = {}
        self.aboutURLSchema = self.schema['aboutUrl']
        self.columns = self.schema['columns']

    def convert(self):
        logger.info("Starting conversion")
        with open(self.file_name) as csvfile:
            logger.info("Opening CSV file for reading")
            reader = csv.DictReader(csvfile)
            logger.info("Starting parsing process")
            count = 0
            for row in reader:
                count += 1
                logger.debug("row: {}".format(count))

                for c in self.columns:
                    # default
                    s = self.expandURL(self.aboutURLSchema, row)

                    try:
                        if 'valueUrl' in c:
                            # This is an object property
                            if len(self.render_pattern(c['valueUrl'], row)) == 0:
                                # Skip value if length is zero
                                continue

                            if 'virtual' in c and c['virtual'] and 'aboutUrl' in c:
                                s = self.expandURL(c['aboutUrl'], row)

                            p = self.expandURL(c['propertyUrl'], row)
                            o = self.expandURL(c['valueUrl'], row)
                        else:
                            # This is a datatype property

                            if 'value' in c:
                                value = self.render_pattern(c['value'], row)
                            else:
                                value = row[c['name']].decode('latin')

                            if len(value) == 0:
                                # Skip value if length is zero
                                continue

                            # If propertyUrl is specified, use it, otherwise use the column name
                            if 'propertyUrl' in c:
                                p = self.expandURL(c['propertyUrl'], row)
                            else:
                                p = self.expandURL(c['name'], row)

                            if 'datatype' in c:
                                if c['datatype'] == 'string' and 'lang' in c:
                                    # If it is a string datatype that has a language, we turn it into a
                                    # language tagged literal
                                    # We also render the lang value in case it is a pattern.
                                    o = Literal(value, lang=self.render_pattern(c['lang'], row))
                                elif isinstance(c['datatype'], dict):
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
                        # print row[0], value
                        traceback.print_exc()
        logger.info("... done")

    def serialize(self):
        trig_file_name = self.file_name + '.trig'
        logger.info("Starting serialization to {}".format(trig_file_name))

        with open(trig_file_name, 'w') as f:
            self.np.serialize(f, format='trig')
        logger.info("... done")

    def render_pattern(self, pattern, row):
        # Significant speedup by not re-instantiating Jinja templates for every row.
        if pattern in self.templates:
            template = self.templates[pattern]
        else:
            template = self.templates[pattern] = Template(pattern)

        # TODO This should take into account the special CSVW instructions such as {_row}
        # First we interpret the url_pattern as a Jinja2 template, and pass all column/value pairs as arguments
        rendered_template = template.render(**row)
        # We then format the resulting string using the standard Python2 expressions
        return rendered_template.format(**row)

    def expandURL(self, url_pattern, row, datatype=False):
        url = self.render_pattern(url_pattern, row)

        for ns, nsuri in namespaces.items():
            if url.startswith(ns):
                url = url.replace(ns + ':', nsuri)
                break

        try:
            rfc3987.parse(url, rule='IRI')
            iri = iribaker.to_iri(url)
        except:
            try:
                if datatype == False:
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
