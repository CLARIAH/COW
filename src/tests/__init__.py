import unittest
import json

from converter import Converter


class TestConversion(unittest.TestCase):

    def test_intialization(self):
        """
        Tests basic initialization capability of converter.Converter class
        """
        with open('tests/qber-output-example.json') as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], author_profile)

    def test_simple_conversion(self):
        """
        Tests simple conversion (non-parallel) capability of converter.Converter class
        """
        with open('tests/qber-output-example.json') as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], author_profile)
        c.setProcesses(1)

        c.convert()

    def test_parallel_conversion(self):
        """
        Tests parallel conversion (2 threads) capability of converter.Converter class
        """
        with open('tests/qber-output-example.json') as dataset_file:
            dataset = json.load(dataset_file)

        author_profile = {
            'email': 'john@doe.com',
            'name': 'John Doe',
            'id': '2938472912'
        }

        c = Converter(dataset['dataset'], author_profile)
        c.setProcesses(2)

        c.convert()


if __name__ == '__main__':
    unittest.main()
