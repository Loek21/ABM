import pandas
import os

if os.path.exists('results_SOBOL'):
    temp_files = os.listdir('results_SOBOL')
    temp_list  = [pandas.read_pickle('results_SOBOL/' + fname) for fname in temp_files] 
    new_df  = pandas.concat(temp_list)
    new_df.to_pickle('results_SOBOL/' + "merged")
    for fname in temp_files:
        if not fname == "merged":
            os.remove('results_SOBOL/' + fname)
        
if os.path.exists('results_OFAT'):
    for d in os.listdir('results_OFAT'):
        temp_files = os.listdir('results_OFAT/' + d)
        temp_list  = [pandas.read_pickle('results_OFAT/' + d + "/" + fname) for fname in temp_files] 
        new_df = pandas.concat(temp_list)
        new_df.to_pickle('results_OFAT/' + d + "/" "merged")
        for fname in temp_files:
            if not fname == "merged":
                os.remove('results_OFAT/' + d + "/" + fname)