from converter import convert
import argparse

# AGE: format to 3 positions
mappings = {
    'AGE': lambda x: x.zfill(3)
}

nocode = ['BPLPARSE', 'CFU', 'CFUSIZE', 'CITYPOP', 'CNTYAREA', 'COUNTYUS',
          'ELDCH', 'ENUMDIST', 'FAMUNIT', 'HEADLOC', 'HHNBRNO', 'HHWT',
          'LINENUM', 'MOMLOC', 'NAMEFRST', 'NAMELAST', 'NFAMS', 'NHGISJOIN',
          'OCCSTRNG', 'OCSCORUS', 'PAGENUM', 'PARISHGB', 'PARSE', 'PERNUM',
          'PERWT', 'POPLOC', 'PRMFAMSZ', 'QOCCGB', 'REALPROP', 'RECTYPE',
          'REEL', 'RELATS', 'RESLSNO', 'SDSTCA', 'SEAUS', 'SEIUS', 'SERIAL',
          'SPLOC', 'YNGCH', 'YRSUSA1', 'NUMPERHH']


parser = argparse.ArgumentParser(description="Convert NAPP files")
parser.add_argument('source_file', metavar='source_file', type=str)
parser.add_argument('target_file', metavar='target_file', type=str)
parser.add_argument('dataset_name', metavar='dataset_name', type=str)
parser.add_argument('--stop', metavar='N', type=int, default=None, required=False)
parser.add_argument('--processes', metavar='N', type=int, default=4, required=False)
parser.add_argument('--chunksize', metavar='N', type=int, default=1000, required=False)
parser.add_argument('--numberedobservations', type=bool, default=True, required=False)




if __name__ == '__main__':
    args = parser.parse_args()

    infile = args.source_file
    outfile = args.target_file
    dataset_name = args.dataset_name
    stop = args.stop
    numberedobservations = args.numberedobservations

    processes = args.processes
    chunksize = args.chunksize

    config = {
        'stop': stop,
        'mappings': {},
        'nocode': nocode,
        'family': 'napp',
        'number_observations': numberedobservations
    }
    c = convert(infile, outfile, dataset_name=dataset_name, processes=processes, chunksize=chunksize, config=config)
