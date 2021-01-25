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
    if param == "Fish mean":
        x = df.groupby(var).mean().reset_index()[var]
        y = df.groupby(var).mean()[param] + df.groupby(var).mean()['Fish slope']*1200
    else:
        x = df.groupby(var).mean().reset_index()[var]
        y = df.groupby(var).mean()[param]

    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)

    ax.plot(x, y, c='k')
    ax.fill_between(x, y - err, y + err, alpha=0.5)

    ax.set_xlabel(var, fontsize=8)
    ax.set_ylabel(f"Mean {param}", fontsize=8)
    ax.set_title(f"Influence of {var} on {param}", fontsize=10)

if os.path.exists('results_OFAT'):
    for i, d in enumerate(os.listdir('results_OFAT')):
        file1 = pd.read_pickle('results_OFAT/' + d +'/merged')
        file2 = pd.read_pickle('results_OFAT/' + d +'/merged_F')
        file = pd.concat([file1, file2])
        fig = plt.figure(figsize=(10,4))
        fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=0.7)
        for problem in problem_list:
            if problem['names'][0] == d:
                instance = problem
        for i, param in enumerate(["Cumulative gain", "Fish mean", "Fish slope", "Fish variance"]):
            ax = fig.add_subplot(2,2,(i+1))
            plot_param_var_conf(ax, file, instance['names'][0], param, i)
        plt.savefig(f"results_OFAT/" + d +f"/plot_{instance['names'][0]}")
