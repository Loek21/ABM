import SALib
from classes.model import *
from classes.agent import *
from SALib.sample import saltelli
from mesa.batchrunner import BatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
from itertools import combinations
import concurrent.futures
import sys
import os
import datetime
import pickle

'''
Runs OFAT sensitivity analysis for the no fishing zone size and quotum amounts, run using run_results.bat to enable concurrent processes.
'''

def run_model_new(self, model):
        """
        Adjustment to run_model function in Mesa API
        """
        while model.running and model.schedule_Fisherman.steps < self.max_steps:
            model.step()
        model.get_model_stats()

        if hasattr(model, "datacollector"):
            return model.datacollector
        else:
            return None

def job(problem):
    '''
    Function that performs the OFAT job for one repetition, returns the data and problem it belongs to.
    '''
    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates       = 1
    max_steps        = 4800
    distinct_samples = 50

    # Set the outputs
    model_reporters = {"Fish mean":       lambda m: m.fish_mean,
                       "Fish slope":      lambda m: m.fish_slope,
                       "Fish variance":   lambda m: m.fish_variance,
                       "Cumulative gain": lambda m: m.cumulative_gain}

    data = {}

    for i, var in enumerate(problem['names']):

        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype = float)

        batch = BatchRunner(FishingModel,
                            max_steps=max_steps,
                            iterations=replicates,
                            variable_parameters={var: samples},
                            model_reporters=model_reporters,
                            display_progress=True)

        batch.run_all()

        data[var] = batch.get_model_vars_dataframe()

    return [data, problem]

BatchRunner.run_model = run_model_new

problem_list = [{
    'num_vars': 1,
    'names': ['no_fish_size'],
    'bounds': [[0, .80]]
}, {
    'num_vars': 1,
    'names': ['quotum'],
    'bounds': [[0, 10000]]
}]

# check that the directory exists
if not os.path.exists('results'):
    os.makedirs('results')

for i in range(len(problem_list)):
    if not os.path.exists('results/' + problem_list[i]["names"][0]):
        os.makedirs('results/' + problem_list[i]["names"][0])


# start saving the replications
while True:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(len(problem_list)):
            temp_data = executor.submit(job, problem_list[i])
            list(temp_data.result()[0].values())[0].to_pickle("results/" + problem_list[i]["names"][0] + "/" + datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%f"))
            print(list(temp_data.result()[0].values())[0])
