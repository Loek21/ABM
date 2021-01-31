import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from SALib.analyze import sobol

'''
Used for plotting Sobol data, make sure results_SOBOL folder contains the neccessary dataframes.
'''

problem = {
    'num_vars': 6,
    'names': ['energy_gain', 'full_catch_reward', 'initial_wallet_survival', 'catch_rate', 'fish_reproduction_number', 'beta_fisherman_spawn'],
    'bounds': [[2, 6], [25, 200], [8, 72], [0.2, 1], [1.03, 1.2], [0.2, 2]]
}

def plot_index(ax, s, params, i, name, title=''):
    """
    Helper function that assists in creating plots for OFAT sensitivity analysis.
    """

    indices = s['S' + i]
    errors = s['S' + i + '_conf']
    l = len(indices)
    ax.set_title(title + f" for {name}")
    ax.set_ylim([-0.2, len(indices) - 1 + 0.2])
    if ax == ax1:
        ax.set_yticks(range(0,6))
        ax.set_yticklabels(params, fontsize=6.5)
    else:
        ax.set_yticklabels([])
    ax.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o', capsize=5)
    ax.axvline(0, c='grey', ls="--")
    ax.set_xlabel(f"S{i}")

if os.path.exists('results_SOBOL'):

    file = pd.read_pickle('results_SOBOL/merged')
    for i, param in enumerate(["Cumulative_gain", "Fish mean", "Fish slope", "Fish variance"]):
        data = sobol.analyze(problem, file[param].values, print_to_console=True, calc_second_order=False)
        fig = plt.figure(figsize=(11,5))
        fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=0.7)
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2)
        plot_index(ax1, data, problem['names'], '1', param, 'First order sensitivity')
        plot_index(ax2, data, problem['names'], 'T', param, 'Total order sensitivity')

        plt.savefig(f"results_SOBOL/plot_{param}_test")
