import SALib
from classes.model import *
from classes.agent import *
from SALib.sample import saltelli
from mesa.batchrunner import BatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import os
import datetime
from itertools import combinations
import sys

'''
Runs OFAT sensitivity analysis, run using run_SOBOLi.bat to enable concurrent processes.
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

BatchRunner.run_model = run_model_new

problem = {
    'num_vars': 6,
    'names': ['energy_gain', 'full_catch_reward', 'initial_wallet_survival', 'catch_rate', 'fish_reproduction_number', 'beta_fisherman_spawn'],
    'bounds': [[2, 6], [25, 200], [8, 72], [0.2, 1], [1.03, 1.2], [0.2, 2]]
}

model_reporters = {"Fish mean":       lambda m: m.fish_mean,
                   "Fish slope":      lambda m: m.fish_slope,
                   "Fish variance":   lambda m: m.fish_variance,
                   "Cumulative gain": lambda m: m.cumulative_gain}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 1
max_steps = 2400
distinct_samples = 10

# check that the directory exists
if not os.path.exists('results_SOBOL'):
    os.makedirs('results_SOBOL')

while True:
     # We get all our samples here
    param_values = saltelli.sample(problem, distinct_samples, calc_second_order=False)

    batch = BatchRunner(FishingModel,
                        max_steps=max_steps,
                        variable_parameters={name:[] for name in problem['names']},
                        model_reporters=model_reporters)

    count = 0
    data = pd.DataFrame(index=range(replicates*len(param_values)),
                                    columns=['energy_gain', 'full_catch_reward', 'initial_wallet_survival', 'catch_rate', 'fish_reproduction_number', 'beta_fisherman_spawn'])
    data['Run'], data['Fish mean'], data['Fish slope'], data['Fish variance'], data['Cumulative_gain'] = None, None, None, None, None


    for vals in param_values:

        # Change parameters that should be integers
        vals = list(vals)
        vals[1] = int(vals[1])
        vals[0] = int(vals[0])

        # Transform to dict with parameter names and their values
        variable_parameters = {}
        for name, val in zip(problem['names'], vals):
            variable_parameters[name] = val

        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]
        iteration_data['Run'] = count
        data.iloc[count, 0:problem['num_vars']] = vals
        data.iloc[count, problem['num_vars']:problem['num_vars']+len(model_reporters)+1] = iteration_data
        count += 1

        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done', end="\r", flush = True)

    data.to_pickle("results_SOBOL/" + datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%f"))
    print("\n")
