from converter import convert
import argparse

parser = argparse.ArgumentParser(description="Convert CSV files to RDF Data Cube (in parallel)")
parser.add_argument('source_file', metavar='source_file', type=str, help="The input CSV file")
parser.add_argument('target_file', metavar='target_file', type=str, help="The filename to which the RDF will be written (NT-format)")
parser.add_argument('dataset_name', metavar='dataset_name', type=str, help="A short name (slug) for the name of the dataset (will use input file name if not specified)")
parser.add_argument('--family', type=str, default=None, required=False, help="Determines which mapping specification to use, e.g. 'napp' (see converter/mappings.py)")
parser.add_argument('--stop', metavar='N', type=int, default=None, required=False, help="Specifies at what iteration to stop (currently ignored)")
parser.add_argument('--processes', metavar='N', type=int, default=4, required=False, help="Specifies the number of processes to spawn (default = 4)")
parser.add_argument('--chunksize', metavar='N', type=int, default=1000, required=False, help="Specifies the number of lines from the CSV file to send to each process (lower numbers use less memory, but make things slower")
parser.add_argument('--numberedobservations', type=bool, default=True, required=False, help="Use the sequence number of each line to generate the URI for the observation")


if __name__ == '__main__':
    args = parser.parse_args()

    config = {
        'stop': args.stop,
        'family': args.family,
        'number_observations': args.numberedobservations
    }
    
    c = convert(args.source_file, args.target_file, dataset_name=args.dataset_name, processes=args.processes, chunksize=args.chunksize, config=config)
