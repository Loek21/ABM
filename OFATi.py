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

# OFAT parameters

def run_model_new(self, model):
        """Run a model object to completion, or until reaching max steps.
        If your model runs in a non-standard way, this is the method to modify
        in your subclass.
        """
        while model.running and model.schedule_Fisherman.steps < self.max_steps:
            model.step()
        model.get_model_stats()

        if hasattr(model, "datacollector"):
            return model.datacollector
        else:
            return None

def job(problem):
    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates       = 1
    max_steps        = 2400
    distinct_samples = 10

    # Set the outputs
    model_reporters = {"Fish mean":       lambda m: m.fish_mean,
                       "Fish slope":      lambda m: m.fish_slope,
                       "Fish variance":   lambda m: m.fish_variance,
                       "Cumulative gain": lambda m: m.cumulative_gain}

    data = {}

    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype = float)

        # Keep in mind that wolf_gain_from_food should be integers. You will have to change
        # your code to acommodate for this or sample in such a way that you only get integers.
        # if var == 'wolf_gain_from_food':
        #     samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)

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
    'names': ['initial_fish'],
    'bounds': [[100, 500]]
}, {
    'num_vars': 1,
    'names': ['initial_fishermen'],
    'bounds': [[50, 200]]
},
{
     'num_vars': 1,
     'names': ['initial_school_size'],
     'bounds': [[50, 200]]
},
{
    'num_vars': 1,
    'names': ['split_size'],
    'bounds': [[100, 300]]
},
{
    'num_vars': 1,
    'names': ['beta_fisherman_spawn'],
    'bounds': [[0.2, 2]]
},
{
    'num_vars': 1,
    'names': ['fish_reproduction_number'],
    'bounds': [[1.03, 1.2]]
},{
    'num_vars': 1,
    'names': ['regrowth_time'],
    'bounds': [[5, 15]]
},{
    'num_vars': 1,
    'names': ['initial_wallet_survival'],
    'bounds': [[8, 72]]
},{
    'num_vars': 1,
    'names': ['full_catch_reward'],
    'bounds': [[25, 200]]
},{
    'num_vars': 1,
    'names': ['energy_gain'],
    'bounds': [[2, 6]]
},{
    'num_vars': 1,
    'names': ['catch_rate'],
    'bounds': [[0.2, 1]]
}]

# check that the directory exists
if not os.path.exists('results_OFAT'):
    os.makedirs('results_OFAT')

for i in range(len(problem_list)):
    if not os.path.exists('results_OFAT/' + problem_list[i]["names"][0]):
        os.makedirs('results_OFAT/' + problem_list[i]["names"][0])


# start saving the replications
while True:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(len(problem_list)):
            temp_data = executor.submit(job, problem_list[i])
            list(temp_data.result()[0].values())[0].to_pickle("results_OFAT/" + problem_list[i]["names"][0] + "/" + datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%f"))
            print(list(temp_data.result()[0].values())[0])
