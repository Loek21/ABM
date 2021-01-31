import pandas
import os

'''
Merges results from different dataframes to a single one.
'''

if os.path.exists('results'):
    for d in os.listdir('results'):
        temp_files = os.listdir('results/' + d)
        temp_list  = [pandas.read_pickle('results/' + d + "/" + fname) for fname in temp_files]
        new_df = pandas.concat(temp_list)
        new_df.to_pickle('results/' + d + "/" "merged_F")
        for fname in temp_files:
            if not fname == "merged_F":
                os.remove('results/' + d + "/" + fname)

if os.path.exists('results_SOBOL'):
    temp_files = os.listdir('results_SOBOL')
    temp_list  = [pandas.read_pickle('results_SOBOL/' + fname) for fname in temp_files]
    new_df  = pandas.concat(temp_list)
    new_df.to_pickle('results_SOBOL/' + "merged_F")
    for fname in temp_files:
        if not fname == "merged_F":
            os.remove('results_SOBOL/' + fname)

if os.path.exists('results_OFAT'):
    for d in os.listdir('results_OFAT'):
        temp_files = os.listdir('results_OFAT/' + d)
        temp_list  = [pandas.read_pickle('results_OFAT/' + d + "/" + fname) for fname in temp_files]
        new_df = pandas.concat(temp_list)
        new_df.to_pickle('results_OFAT/' + d + "/" "merged_F")
        for fname in temp_files:
            if not fname == "merged_F":
                os.remove('results_OFAT/' + d + "/" + fname)
