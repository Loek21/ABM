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

    def __init__(self, height=40, width=40,
                 initial_fish=100, initial_fishermen=10,
                 initial_school_size = 100, split_size = 200, fish_reproduction_number=1.03,
                 initial_wallet = 100, catch_rate=15, max_load=30, full_catch_reward = 100, fisherman_wait_time = 2,
                 initial_wallet_survival = 4*12*2, prop_plus_wallet_spawn = 20, avg_wallet_spawn_threshold = 1.05
                 ):
        super().__init__()

        self.height = height
        self.width = width
        self.initial_fish = initial_fish
        self.initial_fishermen = initial_fishermen
        self.fish_reproduction_number = fish_reproduction_number
        self.catch_rate = catch_rate
        self.initial_wallet = initial_wallet
        self.initial_school_size = initial_school_size
        self.split_size = split_size
        self.max_load = max_load
        self.avg_wallet = initial_wallet
        self.avg_school_size = initial_school_size
        self.full_catch_reward = full_catch_reward
        self.initial_wallet_survival = initial_wallet_survival
        self.fisherman_wait_time = fisherman_wait_time
        self.prop_plus_wallet_spawn = prop_plus_wallet_spawn
        self.avg_wallet_spawn_threshold = avg_wallet_spawn_threshold
        
        # Add a schedule for fish and fishermen seperately to prevent race-conditions
        self.schedule_Fish = RandomActivation(self)
        self.schedule_Fisherman = RandomActivation(self)

        self.this_avg_wallet        = initial_wallet
        self.this_avg_school_size   = initial_school_size
        
        self.grid = MultiGrid(self.width, self.height, torus=True)
        self.datacollector = DataCollector(
             {"Fish": lambda m: self.schedule_Fish.get_agent_count(),
              "Fishermen": lambda m: self.schedule_Fisherman.get_agent_count(),
              "Average wallet": lambda m: self.this_avg_wallet,
              "Average school size": lambda m: self.this_avg_school_size})

        # Keep a list of all agents
        self.agents = []

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
        self.agents.append(agent)

        getattr(self, f'schedule_{agent_type.__name__}').add(agent)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the grid and the correct scheduler.
        '''
        self.grid.remove_agent(agent)
        self.agents.remove(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

    def recruit_fisherman(self):
        '''
        Method that spawns new fisherman based on the average gains of the existing fisherman.
        '''
        n_fisherman   = self.schedule_Fisherman.get_agent_count()
        profitability = self.this_avg_wallet / self.initial_wallet
        
        # make sure that at least one fisherman exists, who wouldn't try a new bussiness in a new field?
        if n_fisherman == 0:
            self.init_population(Fisherman, 1)
        # add new fisherman proportional to the profitability
        elif profitability > self.avg_wallet_spawn_threshold:
                n_new_fisherman = int( (profitability / self.avg_wallet_spawn_threshold)*self.prop_plus_wallet_spawn)
                print("SPAWNING NEW FISHERMAN ", n_new_fisherman)
                self.init_population(Fisherman, n_new_fisherman)

    def get_fish_stats(self):
        '''
        Method that computes information about fishes.
        '''
        fish_size = [fish.size for fish in self.schedule_Fish.agents]
        if len(fish_size) == 0:
            self.this_avg_school_size = 0
        else:
            self.this_avg_school_size = sum(fish_size) / len(fish_size)
        
    def get_fisherman_stats(self):
        '''
        Method that computes information about fisherman.
        '''
        fisherman_wallet = [fisherman.wallet for fisherman in self.schedule_Fisherman.agents]
        if len(fisherman_wallet) == 0:
            self.this_avg_wallet = 0
        else:
            self.this_avg_wallet = sum(fisherman_wallet) / len(fisherman_wallet)
        
    def step(self):
        '''
        Method that calls the step method for each of the sheep, and then for each of the wolves.
        '''
        self.schedule_Fish.step()
        self.schedule_Fisherman.step()
        
        self.get_fish_stats()
        self.get_fisherman_stats()
        
        self.recruit_fisherman()
          
        # Save the statistics
        self.datacollector.collect(self)

    def run_model(self, step_count=5000):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            print(i)
            # if either the Fish or the Fishermen amount reaches 0, stop.
            if self.schedule_Fish.get_agent_count() == 0 or self.schedule_Fisherman.get_agent_count() == 0:
                break
            self.step()
