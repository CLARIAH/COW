from converter import Converter

# AGE: format to 3 positions
mappings = {
    'AGE': lambda x: x.zfill(3)
}

nocode = ['OCCSTRNG', 'HISPAN']


if __name__ == '__main__':
    infile = 'data/napp_test_data.csv'
    outfile = 'data/napp_test_data.ttl'
    c = Converter(mappings=mappings, nocode=nocode, family='napp')

    c.convert(infile, outfile, 'test_data')
