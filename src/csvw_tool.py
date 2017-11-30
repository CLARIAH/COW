from converter.csvw import CSVWConverter, build_schema
import os
import datetime
import argparse
import sys
import traceback

def main():
    parser = argparse.ArgumentParser(description="Not nearly CSVW compliant schema builder and RDF converter")
    parser.add_argument('mode', choices=['convert','build'], default='convert', help='Use the schema of the `file` specified to convert it to RDF, or build a schema from scratch.')
    parser.add_argument('files', metavar='file', nargs='+', type=str, help="Path(s) of the file(s) that should be used for building or converting. Must be a CSV file.")
    parser.add_argument('--dataset', dest='dataset', type=str, help="A short name (slug) for the name of the dataset (will use input file name if not specified)")
    parser.add_argument('--delimiter', dest='delimiter', default=None, type=str, help="The delimiter used in the CSV file(s)")
    parser.add_argument('--quotechar', dest='quotechar', default='\"', type=str, help="The character used as quotation character in the CSV file(s)")
    parser.add_argument('--processes', dest='processes', default='4', type=int, help="The number of processes the converter should use")
    parser.add_argument('--chunksize', dest='chunksize', default='5000', type=int, help="The number of rows processed at each time")
    parser.add_argument('--base', dest='base', default='https://iisg.amsterdam/resource/', type=str, help="The base for URIs generated with the schema (only relevant when `build`ing a schema)")
    parser.add_argument('--version', dest='versoin', action='version', version='x.xx')

    args = parser.parse_args()

    for source_file in args.files:

        if args.mode == 'build':
            print "Building schema for {}".format(source_file)
            target_file = "{}-metadata.json".format(source_file)

            if os.path.exists(target_file):
                modifiedTime = os.path.getmtime(target_file)
                timestamp = datetime.datetime.fromtimestamp(modifiedTime).isoformat()
                os.rename(target_file, target_file+"_"+timestamp)
                print "Backed up prior version of schema to {}".format(target_file+"_"+timestamp)

            # print "Delimiter is: ", repr(args.delimiter)
            build_schema(source_file, target_file, dataset_name=args.dataset, delimiter=args.delimiter, quotechar=args.quotechar, base=args.base)

        elif args.mode == 'convert':
            print "Converting {} to RDF".format(source_file)

            try:
                c = CSVWConverter(source_file, delimiter=args.delimiter, quotechar=args.quotechar, processes=args.processes, chunksize=args.chunksize)
                c.convert()
            except:
                print "Something went wrong, skipping {}.".format(source_file)
                traceback.print_exc(file=sys.stdout)
        else:
            print "Whoops for file {}".format(f)

if __name__ == '__main__':
    main()

# FILE = '../sdh-private-hisco-datasets/hisco_45.csv'
# SCHEMA = '../sdh-private-hisco-datasets/hisco_45.csv-metadata.json'
