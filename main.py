from classes.model import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
    food_bool = True
    no_fish_zone_bool = True
    quotum_bool = False
    no_fish_size = 0
    quotum = 4000
    iterations = 5000
    model = FishingModel(food_bool = food_bool, no_fish_zone_bool = no_fish_zone_bool, quotum_bool = quotum_bool, no_fish_size = no_fish_size, quotum = quotum)
    model.run_model(iterations)

    data = model.datacollector.get_model_vars_dataframe()
    data.plot()
    plt.show()
    print(data)
