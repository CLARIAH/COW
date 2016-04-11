from converter.qberify import build_schema
import argparse

parser = argparse.ArgumentParser(description="Convert CSV files to JSON Metadata files (according to W3C CSV on the Web)")
parser.add_argument('source_file', metavar='source_file', type=str, help="The input CSV file (without the .csv extension)")
parser.add_argument('dataset_name', metavar='dataset_name', type=str, help="A short name (slug) for the name of the dataset (will use input file name if not specified)")


if __name__ == '__main__':
    args = parser.parse_args()

    source_file = "{}.csv".format(args.source_file)
    target_file = "{}.json".format(args.source_file)

    build_schema(source_file, target_file, dataset_name=args.dataset_name)
