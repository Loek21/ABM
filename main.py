from classes.model import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
    model = FishingModel()
    model.run_model()

    data = model.datacollector.get_model_vars_dataframe()
    print(data.plot())
    plt.show()
    print(data)
