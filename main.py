from classes.model import *
import matplotlib.pyplot as plt

'''
Main.py

Input:
Food_bool - set to True if model runs with food enabled, otherwise False.
no_fish_size - fraction of area that is inaccessible to fisherman, acts as no fishing zone.
quotum - yearly limit of tonnes of fish that can be caught by the fisherman agents.
iterations - How many weeks the model will run for.

Output:
printed overview of data along with a graphical plot.

Notes:
This option is also available in Ipython environment, accessible by running visual.py
'''

if __name__ == "__main__":
    food_bool = True
    no_fish_size = 0
    quotum = 4000
    iterations = 5000
    model = FishingModel(food_bool = food_bool, no_fish_size = no_fish_size, quotum = quotum)
    model.run_model(iterations)

    data = model.datacollector.get_model_vars_dataframe()
    data.plot()
    plt.show()
    print(data)
