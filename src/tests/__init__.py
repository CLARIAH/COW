import unittest
import json
import os

from converter import Converter
from converter.qberify import build_schema
import converter.csvw as csvw
from rdflib import Dataset

THIS_DIRECTORY = os.path.dirname(__file__)

class TestConversion(unittest.TestCase):

    def test_intialization(self):
        """
        Tests basic initialization capability of converter.Converter class
        """
        with open(os.path.join(os.path.dirname(__file__), 'qber-output-example.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile)

    def test_simple_conversion(self):
        """
        Tests simple conversion (non-parallel) capability of converter.Converter class
        """
        with open(os.path.join(os.path.dirname(__file__), 'qber-output-example.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile, target="simple_conversion_output.nq")
        c.setProcesses(1)

        c.convert()

    def test_parallel_conversion(self):
        """
        Tests parallel conversion (2 threads) capability of converter.Converter class
        """
        with open(os.path.join(os.path.dirname(__file__), 'qber-output-example.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile, target="parallel_conversion_output.nq")
        c.setProcesses(2)

        c.convert()

    def test_parallel_csvw_conversion(self):
        """
        Tests parallel CSVW conversion (2 threads) capability of csvw.Converter class
        """

        c = csvw.CSVWConverter(os.path.join(os.path.dirname(__file__), 'hsn2013a_hisco_comma_short.csv'))

        c.convert()

    def test_datatype_conversion(self):
        """
        Tests simple conversion that takes datatypes for 'other' variables in converter.Converter class
        """
        with open(os.path.join(os.path.dirname(__file__), 'qber-output-example.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile, target="datatype_conversion_output.nq")
        c.setProcesses(1)

        c.convert()

        dataset = Dataset()
        with open(os.path.join(os.path.dirname(__file__), 'datatype_conversion_output.nq'), "r") as graph_file:
            dataset.load(graph_file, format='nquads')

        q = """
            ASK {
                GRAPH ?g {
                    [] <http://data.socialhistory.org/ns/resource/utrecht_1829_clean_01/variable/leeftijd> "55"^^<http://www.w3.org/2001/XMLSchema#integer> .
                    [] <http://data.socialhistory.org/ns/resource/utrecht_1829_clean_01/variable/huisnummer> "170"^^<http://www.w3.org/2001/XMLSchema#integer> .
                }
            }
        """

        result = dataset.query(q)

        for row in result:
            assert row is True

    def test_transformation_function(self):
        """
        Tests simple conversion that transforms the 'achternaam' variable values using the `transformation` attribute
        """
        with open(os.path.join(os.path.dirname(__file__), 'qber-output-example.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile, target="transformation_function_output.nq")
        c.setProcesses(1)

        c.convert()

        dataset = Dataset()
        with open("transformation_function_output.nq", "r") as graph_file:
            dataset.load(graph_file, format='nquads')

        q = """
            ASK {
                GRAPH ?g {
                    [] <http://data.socialhistory.org/ns/resource/utrecht_1829_clean_01/variable/achternaam> "hofmanhofman" .
                }
            }
        """

        result = dataset.query(q)

        for row in result:
            assert row is True

    def test_valueUrl(self):
        """
        Tests simple conversion that takes a minimal example that specifies a valueUrl mapping
        """
        with open(os.path.join(os.path.dirname(__file__), 'qber-output-no-values.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile, target="output_valueUrl.nq")
        c.setProcesses(1)

        c.convert()

    def test_extract_qber_schema(self):
        """
        Tests the extraction of a QBer-style schema from a CSV file, and subsequent conversion in a single process
        """

        build_schema(os.path.join(os.path.dirname(__file__), 'englandwales1881_tiny.csv'),
                     os.path.join(os.path.dirname(__file__), 'englandwales1881_tiny.json'),
                     dataset_name='englandwales1881')

        with open(os.path.join(os.path.dirname(__file__), 'englandwales1881_tiny.json')) as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], THIS_DIRECTORY, author_profile, target="output_extract_qber_schema.nq")
        c.setProcesses(4)

        c.convert()



if __name__ == '__main__':
    unittest.main()
