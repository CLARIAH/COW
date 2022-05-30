#!/usr/bin/python3

try:
    # git install
    from converter.csvw import CSVWConverter, build_schema, extensions
except ImportError:
    # pip install
    from cow_csvw.converter.csvw import CSVWConverter, build_schema, extensions
import os
import datetime
import argparse
import sys
import gzip
import traceback
from glob import glob
from rdflib import ConjunctiveGraph
from werkzeug.utils import secure_filename
import codecs
from pathlib import Path


class COW(object):

    def __init__(self, mode=None, files=None, dataset=None, delimiter=None,
                 encoding=None, quotechar='\"', processes=4, chunksize=5000,
                 base="https://example.com/id/", output_format='nquads',
                 gzipped=False):
        """
        COW entry point
        """

        for source_file in files:
            if mode == 'build':
                print("Building schema for {}".format(source_file))
                target_file = "{}-metadata.json".format(source_file)

                if os.path.exists(target_file):
                    path = Path(target_file)
                    modifiedTime = os.path.getmtime(path)
                    timestamp = datetime.datetime.fromtimestamp(modifiedTime)
                    timestamp = timestamp.isoformat()
                    filename = secure_filename(f"{path.name} {timestamp}")
                    new_path = Path(path.parent, filename)
                    os.rename(path, new_path)
                    print(f"Backed up prior version of schema to {new_path}")

                build_schema(source_file, target_file, dataset_name=dataset,
                             delimiter=delimiter, encoding=encoding,
                             quotechar=quotechar, base=base)

            elif mode == 'convert':
                print("Converting {} to RDF".format(source_file))

                try:
                    c = CSVWConverter(source_file, delimiter=delimiter,
                                      quotechar=quotechar, encoding=encoding,
                                      processes=processes, chunksize=chunksize,
                                      output_format='nquads', base=base,
                                      gzipped=gzipped)
                    c.convert()

                    # We convert the output serialization if different from nquads
                    if output_format not in ['nquads']:
                        func = open
                        quads_filename = source_file + '.' + 'nq'
                        new_filename = source_file + '.' + extensions[output_format]
                        if gzipped:
                            func = gzip.open
                            quads_filename = quads_filename + '.gz'
                            new_filename = new_filename + '.gz'

                        with func(quads_filename, 'rb') as nquads_file:
                            g = ConjunctiveGraph()
                            g.parse(nquads_file, format='nquads') if not gzipped\
                                    else g.parse(data=nquads_file.read(), format='nquads')

                        # We serialize in the requested format
                        with func(new_filename, 'w') as output_file:
                            g.serialize(destination=output_file,
                                        format=output_format)

                except ValueError:
                    raise
                except:
                    print("Something went wrong, skipping {}.".format(source_file))
                    traceback.print_exc(file=sys.stdout)
            else:
                print("Whoops for file {}".format(source_file))

def main():
    parser = argparse.ArgumentParser(description="Not nearly CSVW compliant schema builder and RDF converter")
    parser.add_argument('mode', choices=['convert','build'], default='convert', help='Use the schema of the `file` specified to convert it to RDF, or build a schema from scratch.')
    parser.add_argument('files', metavar='file', nargs='+', type=str, help="Path(s) of the file(s) that should be used for building or converting. Must be a CSV file.")
    parser.add_argument('--dataset', dest='dataset', type=str, help="A short name (slug) for the name of the dataset (will use input file name if not specified)")
    parser.add_argument('--delimiter', dest='delimiter', default=None, type=str, help="The delimiter used in the CSV file(s)")
    parser.add_argument('--quotechar', dest='quotechar', default='\"', type=str, help="The character used as quotation character in the CSV file(s)")
    parser.add_argument('--encoding', dest='encoding', default=None, type=str, help="The character encoding used in the CSV file(s)")
    parser.add_argument('--processes', dest='processes', default='4', type=int, help="The number of processes the converter should use")
    parser.add_argument('--chunksize', dest='chunksize', default='5000', type=int, help="The number of rows processed at each time")
    parser.add_argument('--gzip', action='store_true', help="Compress the output using gzip")
    parser.add_argument('--base', dest='base', default='https://example.com/id/', type=str, help="The base for URIs generated with the schema (only relevant when `build`ing a schema)")
    parser.add_argument('--format', '-f', dest='format', nargs='?', choices=['xml', 'n3', 'turtle', 'nt', 'pretty-xml', 'trix', 'trig', 'nquads'], default='nquads', help="RDF serialization format")
    parser.add_argument('--version', dest='version', action='version', version = '1.16')

    args = parser.parse_args()

    files = []
    for f in args.files:
        files += glob(f)

    if args.encoding:
        try:
            codecs.lookup(args.encoding)
        except LookupError:
            print("Invalid character encoding. See https://docs.python.org/3.8/library/codecs.html#standard-encodings to see which encodings are possible.")
            sys.exit(1)

    COW(args.mode, files, args.dataset, args.delimiter, args.encoding,
        args.quotechar, args.processes, args.chunksize, args.base,
        args.format, args.gzip)

if __name__ == '__main__':
    main()

# FILE = '../sdh-private-hisco-datasets/hisco_45.csv'
# SCHEMA = '../sdh-private-hisco-datasets/hisco_45.csv-metadata.json'
