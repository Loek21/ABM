import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from .agent import *

class FishingModel(Model):
    '''
    Wolf-Sheep Predation Type Model for Fishermen and Fish
    '''

    def __init__(self, height=50, width=50,
                 initial_fish=100, initial_fishermen=30,
                 fish_reproduction_number=1750, catch_rate=24,
                 max_load=24, initial_wallet = 10000, initial_school_size = 10000):

        super().__init__()

        self.height = height
        self.width = width
        self.initial_fish = initial_fish
        self.initial_fishermen = initial_fishermen
        self.fish_reproduction_number = fish_reproduction_number
        self.catch_rate = catch_rate
        self.initial_wallet = initial_wallet
        self.initial_school_size = initial_school_size

        # Add a schedule for fish and fishermen seperately to prevent race-conditions
        self.schedule_Fish = RandomActivation(self)
        self.schedule_Fisherman = RandomActivation(self)

        self.grid = MultiGrid(self.width, self.height, torus=True)
        self.datacollector = DataCollector(
             {"Fish": lambda m: self.schedule_Fish.get_agent_count(),
              "Fishermen": lambda m: self.schedule_Fisherman.get_agent_count()})

        # Create fish and fishermen
        self.init_population(Fish, self.initial_fish)
        self.init_population(Fisherman, self.initial_fishermen)

        # This is required for the datacollector to work
        self.running = True
        self.datacollector.collect(self)

    def init_population(self, agent_type, n):
        '''
        Method that provides an easy way of making a bunch of agents at once.
        '''
        for i in range(n):
            x = random.randrange(self.width)
            y = random.randrange(self.height)

            if agent_type == Fish:
              self.new_agent(agent_type, (x, y), self.initial_school_size, 0, True, 0)
            else:
              self.new_agent(agent_type, (x, y), 0, self.initial_wallet, True, 0)


    def new_agent(self, agent_type, pos, size, wallet, switch, init_wait_time):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        agent = agent_type(self.next_id(), self, pos, size, wallet, switch, init_wait_time)

        self.grid.place_agent(agent, pos)
        getattr(self, f'schedule_{agent_type.__name__}').add(agent)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the grid and the correct scheduler.
        '''
        self.grid.remove_agent(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

    def step(self):
        '''
        Method that calls the step method for each of the sheep, and then for each of the wolves.
        '''
        self.schedule_Fish.step()
        self.schedule_Fisherman.step()

        # Save the statistics
        self.datacollector.collect(self)

    def run_model(self, step_count=1825):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            self.step()
