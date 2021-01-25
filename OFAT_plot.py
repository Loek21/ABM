import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

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

instance = None

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
    # print(problem['num_vars'])
    f, axs = plt.subplots(int(problem['num_vars']), figsize=(10, 5))

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs, df, var, param, i)

if os.path.exists('results_OFAT'):
    for i, d in enumerate(os.listdir('results_OFAT')):
        file = pd.read_pickle('results_OFAT/' + d +'/merged')
        for problem in problem_list:
            if problem['names'][0] == d:
                instance = problem
        for param in ["Cumulative gain", "Fish mean", "Fish slope", "Fish variance"]:
            plot_all_vars(file, param, instance)
            plt.savefig(f"results_OFAT/" + d +f"/plot_{param}")
