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
import concurrent.futures
import sys

# OFAT parameters

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

def plot_param_var_conf(ax, df, var, param, i):
    """
    Helper function for plot_all_vars. Plots the individual parameter vs
    variables passed.

    Args:
        ax: the axis to plot to
        df: dataframe that holds the data to be plotted
        var: variables to be taken from the dataframe
        param: which output variable to plot
    """
    x = df.groupby(var).mean().reset_index()[var]
    y = df.groupby(var).mean()[param]

    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)

    ax.plot(x, y, c='k')
    ax.fill_between(x, y - err, y + err, alpha=0.5)

    ax.set_xlabel(var)
    ax.set_ylabel(f"Mean {param}")
    ax.set_title(f"Influence of {var} on {param}")
    # plt.show()

def plot_all_vars(df, param, problem):
    """
    Plots the parameters passed vs each of the output variables.

    Args:
        df: dataframe that holds all data
        param: the parameter to be plotted
    """
    f, axs = plt.subplots(int(problem['num_vars']), figsize=(10, 5))

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs, df[var], var, param, i)
    # plt.savefig(f"{var}_{param}")

def job(problem):
    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates = 1
    max_steps = 2400
    distinct_samples = 10

    # Set the outputs
    model_reporters = {"Fish": lambda m: m.schedule_Fish.get_agent_count() * m.this_avg_school_size*0.01,
                        "Cumulative gain": lambda m: m.cumulative_gain}

    data = {}

    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype = int)

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

with concurrent.futures.ThreadPoolExecutor() as executor:
    data = [executor.submit(job, problem_list[i]) for i in range(len(problem_list))]

    for f in concurrent.futures.as_completed(data):
        for param in ['Fish', "Cumulative_gain"]:
            plot_all_vars(f.result()[0], param, f.result()[1])
            plt.savefig(f"{f.result()[1]['names'][0]}_{param}")
