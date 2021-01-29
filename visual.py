from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from classes.model import *

# Sets up an agent portrayal for all agents in the model
def agent_portrayal(agent):

    if type(agent) == Fish:
        color = "orange"
        portrayal = {"Shape": "circle",
                     "Color": color,
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.5}
    elif type(agent) == Food:
        color = "green"
        if agent.food == False:
            color = "blue"
        portrayal = {"Shape": "rect",
                     "Color": color,
                     "Filled": "true",
                     "Layer": 0,
                     "w": 1,
                     "h": 1}
    else:
        color = "red"
        portrayal = {"Shape": "circle",
                     "Color": color,
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.5}
    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 40, 40, 500, 500)

# Creates graphs for the main parameters
chart_agents = ChartModule([{"Label": "Total fish",
                      "Color": "orange"},
                      {"Label": "Fishermen",
                      "Color": "red"}],
                    data_collector_name='datacollector')

chart_finance = ChartModule([{"Label": "Average wallet", "Color": "brown"},
                            {"Label": "Fish price", "Color": "red"}])

chart_gain = ChartModule([{"Label": "Cumulative gain", "Color": "black"}])

no_fish_slider = UserSettableParameter('slider', 'No-fishing zone size', value=0, min_value=0, max_value=0.9, step=0.1)
quotum_slider = UserSettableParameter('slider', 'Yearly fishing quotum (in tonnes of fish)', value=0, min_value=0, max_value=8000, step=1000)

# Creates the server with some slider parameters
server = ModularServer(FishingModel,
                       [grid, chart_agents, chart_finance, chart_gain],
                       "Fishing model",
                        model_params={"no_fish_size": no_fish_slider, "quotum": quotum_slider})

server.port = 8521

server.launch()
