from classes.model import *
import matplotlib.pyplot as plt
import sys
import os
import datetime

'''
Function for obtaining results with different no fishing zone sizes and quotum amounts.
'''

iterations   = 4800
no_fish_size = [0, .2, .4,    0,    0,    0]
quotum       = [0,  0,  0, 2000, 4000, 6000]

# check that the directory exists
if not os.path.exists('results_detailed'):
    os.makedirs('results_detailed')

for i in range(len(no_fish_size)):
    if not os.path.exists('results_detailed/' + 'fs=' + str(no_fish_size[i]) + ',q=' + str(quotum[i])):
        os.makedirs('results_detailed/' + 'fs=' + str(no_fish_size[i]) + ',q=' + str(quotum[i]))

while True:
    for i in range(len(no_fish_size)):
        model = FishingModel(no_fish_size = no_fish_size[i], quotum = quotum[i])
        model.run_model(iterations)
        data = model.datacollector.get_model_vars_dataframe()
        data.to_csv('results_detailed/' + 'fs=' + str(no_fish_size[i]) + ',q=' + str(quotum[i]) + '/' + datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%f") + '.csv')
        print(".")
