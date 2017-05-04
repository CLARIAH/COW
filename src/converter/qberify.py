import os
import csv
import json
import logging
from util import SDR
from iribaker import to_iri

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


_RESOURCE_BASE = str(SDR)
_RESOURCE_URI_PATTERN = "{0}{{}}/{{}}".format(_RESOURCE_BASE)

def build_schema(infile, outfile, delimiter=',', quotechar='\"', dataset_name=None):
    """Builds a basic QBer-style schema (probably deprecated)"""
    
    if dataset_name is None:
        dataset_name = os.path.basename(infile)

    dataset_uri = to_iri(SDR[dataset_name])

    metadata = {
        "dataset": {
            "file": infile,
            "name": dataset_name,
            "uri": dataset_uri,
            "variables": {}
        }
    }

    with open(infile, 'r') as infile_file:
        r = csv.reader(infile_file, delimiter=delimiter, quotechar=quotechar)

        header = r.next()

        logger.debug(header)

        for variable in header:
            variable = variable.decode('utf-8')
            variable_iri = to_iri(_RESOURCE_URI_PATTERN.format('variable', variable))
            col = {
                "category": "identifier",
                "category_comment": "`category` can be one of identifier, coded or other",
                "description": "The variable '{}' as taken from the '{}' dataset.".format(variable, dataset_name),
                "label": variable,
                "uri": variable_iri,
                "original": {
                    "label": variable,
                    "uri": variable_iri
                },
                "type": "http://purl.org/linked-data/cube#DimensionProperty",
                "valueUrl": "{}/{{{}}}".format(variable_iri,variable),
                "datatype_REMOVEME": "Any XML Schema datatype, only applicable for variables of type `other`",
                "transform_REMOVEME": "Any body of a JavaScript function, that returns some value based on an input `v`, the actual value of a variable",
                "values_REMOVEME": [
                    {
                        "comment": "`values` is a list of variable values that has the form specified here",
                        "count": "The frequency of this value for this variable",
                        "label": "The value itself, used as Literal value or as label in case of `identifier` or `coded`",
                        "original": {
                            "label": "The original value, in case of a mapped/modified value",
                            "uri": "The original URI of the value (typically follows the `valueUrl` template)"
                        },
                        "uri": "The URI for the value, ignored in case of `other`"
                    }
                ]
            }

            metadata['dataset']['variables'][variable] = col

    with open(outfile, 'w') as outfile_file:
        outfile_file.write(json.dumps(metadata, indent=True))

    logger.info("Done")
    return
