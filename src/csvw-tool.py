from converter.csvw import CSVWConverter, build_schema
import os
import datetime
import argparse

parser = argparse.ArgumentParser(description="Not nearly CSVW compliant schema builder and RDF converter")
parser.add_argument('mode', choices=['convert','build'], default='convert', help='Use the schema of the `file` specified to convert it to RDF, or build a schema from scratch.')
parser.add_argument('file', type=str, help="Path of the file that should be used for building or converting. Must be a CSV file.")
parser.add_argument('--dataset', dest='dataset', type=str, help="A short name (slug) for the name of the dataset (will use input file name if not specified)")

if __name__ == '__main__':
    args = parser.parse_args()

    if args.mode == 'build':
        source_file = args.file
        target_file = "{}-metadata.json".format(args.file)

        if os.path.exists(target_file):
            modifiedTime = os.path.getmtime(target_file)
            timeStamp = datetime.datetime.fromtimestamp(modifiedTime).isoformat()
            os.rename(target_file, target_file+"_"+timeStamp)

        build_schema(source_file, target_file, dataset_name=args.dataset)

    elif args.mode == 'convert':
        source_file = args.file

        c = CSVWConverter(source_file)
        c.convert()
        c.serialize()
    else :
        print "Whoops"

# FILE = '../sdh-private-hisco-datasets/hisco_45.csv'
# SCHEMA = '../sdh-private-hisco-datasets/hisco_45.csv-metadata.json'
