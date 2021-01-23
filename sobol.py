import SALib
from classes.model import *
from classes.agent import *
from SALib.sample import saltelli
from mesa.batchrunner import BatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import sys

def run_model_new(self, model):
        """Run a model object to completion, or until reaching max steps.
        If your model runs in a non-standard way, this is the method to modify
        in your subclass.
        """
        while model.running and model.schedule_Fisherman.steps < self.max_steps:
            model.step()

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

model_reporters = {"Fish": lambda m: m.schedule_Fish.get_agent_count() * m.this_avg_school_size*0.01,
                    "Cumulative gain": lambda m: m.cumulative_gain}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 100
max_steps = 2400
distinct_samples = 10

# We get all our samples here
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=False)

# READ NOTE BELOW CODE
batch = BatchRunner(FishingModel,
                    max_steps=max_steps,
                    variable_parameters={name:[] for name in problem['names']},
                    model_reporters=model_reporters)

count = 0
data = pd.DataFrame(index=range(replicates*len(param_values)),
                                columns=['energy_gain', 'full_catch_reward', 'initial_wallet_survival', 'catch_rate', 'fish_reproduction_number', 'beta_fisherman_spawn'])
data['Run'], data['Fish'], data['Cumulative gain'] = None, None, None

for i in range(replicates):
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
        iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
        print(data)
        data.iloc[count, 0:problem['num_vars']] = vals
        data.iloc[count, problem['num_vars']:problem['num_vars']+len(model_reporters)+1] = iteration_data
        count += 1


        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done', end="\r", flush = True)

print(data)

fish = sobol.analyze(problem, data['Fish'].values, print_to_console=True)
gain = sobol.analyze(problem, data['Cumulative_gain'].values, print_to_console=True)

analysed_data = [fish, gain]

def plot_index(s, params, i, name, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    # if i == '2':
    #     p = len(params)
    #     params = list(combinations(params, 2))
    #     indices = s['S' + i].reshape((p ** 2))
    #     indices = indices[~np.isnan(indices)]
    #     errors = s['S' + i + '_conf'].reshape((p ** 2))
    #     errors = errors[~np.isnan(errors)]
    # else:
    indices = s['S' + i]
    errors = s['S' + i + '_conf']
    plt.figure(figsize=(12,5))

    l = len(indices)
    # plt.figure(figsize=(5,10))
    plt.title(title + f" for {name}")
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o', capsize=5)
    plt.axvline(0, c='grey', ls="--")

for Si in range(len(analysed_data)):
    # First order
    if Si == 0:
        name = "fish"
    else:
        name = "cumulative gain"
    plot_index(analysed_data[Si], problem['names'], '1', name, 'First order sensitivity')
    plt.show()

    # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    # plt.show()

    # Total order
    plot_index(analysed_data[Si], problem['names'], 'T', name, 'Total order sensitivity')
    plt.show()
