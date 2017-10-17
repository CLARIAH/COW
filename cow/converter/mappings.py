"""DEPRECATED"""

napp = {
    # Mappings are dictionaries that map variable names to
    # functions that rewrite the value for a variable (for e.g. unit conversion)
    'mappings': {
        # format AGE to 3 positions
        'AGE': lambda x: x.zfill(3)
        # CITYPOP should be *1000
    },
    # Nocode is a list of variables whose values should not be coded (i.e. they should become literals)
    'nocode': ['BPLPARSE', 'CFU', 'COUNTYUS',
               'ENUMDIST', 'FAMUNIT', 'HEADLOC', 'HHNBRNO',
               'LINENUM', 'MOMLOC', 'NAMEFRST', 'NAMELAST', 'NHGISJOIN',
               'OCCSTRNG', 'PAGENUM', 'PARISHGB', 'PARSE', 'PERNUM',
               'POPLOC', 'QOCCGB', 'RECTYPE', 'REEL', 'RESLSNO',
               'SDSTCA', 'SEAUS', 'SERVANTS', 'SPLOC'],
    'integer': ['AGE', 'CFUSIZE', 'CITYPOP', 'CNTYAREA', 'ELDCH', 'HHWT',
                'NCOUPLES', 'NFAMS', 'NMOTHERS', 'NUMPERHH', 'OCSCORUS',
                'PERWT','REALPROP', 'RELATS', 'SEIUS', 'SERIAL', 'YEAR',
                'YNGCH', 'YRSUSA1']

    # technically OCSCORUS is not int but pretending  for now
    # should YEAR be an integer, a literal gYear or URI? => integer for now
}
canfam = {
    'mappings' : {
        'relhead2' : lambda x: x[0:3]
        # keep first 4 digits of relhead2 to match IPUMS/NAPP
    },
    'nocode': ['occ', 'hhdid', 'indlnm', 'indfnm', 'dwellid', 'chknote',
               'indnote', 'location'],
    'integer':['ageyr', 'magemo', 'moschool', 'urbpop', 'earnings', 'earnper', 'exearn']
}
mosaic = {
    'nocode': ['fname', 'lname', 'occupat'],
    'integer': ['age', 'hhsize', 'year']
}
