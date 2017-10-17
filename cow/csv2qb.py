from converter import Converter
import argparse
import json
import os.path 
import config

parser = argparse.ArgumentParser(description="Convert CSV files to RDF Data Cube (in parallel)")
parser.add_argument('source_file', metavar='source_file', type=str, help="The QBer-style JSON file that gives the schema of the CSV")
parser.add_argument('target_file', metavar='target_file', type=str, default='output.nq', help="The filename to which the RDF will be written (NQuads-format)")
parser.add_argument('--stop', metavar='N', type=int, default=None, required=False, help="IGNORED Specifies at what iteration to stop (currently ignored)")
parser.add_argument('--processes', metavar='N', type=int, default=4, required=False, help="Specifies the number of processes to spawn (default = 4)")
parser.add_argument('--chunksize', metavar='N', type=int, default=1000, required=False, help="Specifies the number of lines from the CSV file to send to each process (lower numbers use less memory, but make things slower")
parser.add_argument('--numberedobservations', type=bool, default=True, required=False, help="IGNORED Use the sequence number of each line to generate the URI for the observation")


if __name__ == '__main__':
    args = parser.parse_args()
    dirname = os.path.dirname(os.path.realpath(args.source_file))
    
    with open(args.source_file) as dataset_file:
        dataset = json.load(dataset_file)

    author_profile = {
        'email': config.EMAIL,
        'name': config.NAME,
        'id': config.ID
    }
    
    c = Converter(dataset['dataset'], dirname, author_profile, target=args.target_file)
    c.setProcesses(args.processes)
    c.setChunksize(args.chunksize)

    c.convert()
