import dask.dataframe as dd
pd = dd.read_csv("artists.csv",delimiter = " ",error_bad_lines = False)
print(pd)