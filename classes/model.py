import random
import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from .agent import *

class FishingModel(Model):
    '''
    Wolf-Sheep Predation Type Model for Fishermen and Fish
    '''
    food_bool = False
    no_fish_zone_bool = True
    quotum_bool = False
    no_fish_size = 0.25
    quotum = 3000
    step_count = 5000
    # model = FishingModel(food_bool = food_bool, no_fish_zone_bool = no_fish_zone_bool, quotum_bool = quotum_bool, no_fish_size = no_fish_size, quotum = quotum)
    # model.run_model(iterations)

    def __init__(self, height=40, width=40,
                 initial_fish=300, initial_fishermen=100,
                 initial_school_size = 100, split_size = 200, fish_reproduction_number=1.03,
                 initial_wallet = 100, catch_rate=15, max_load=30, full_catch_reward = 100,
                 initial_wallet_survival = 4*6, beta_fisherman_spawn = 1, energy_gain = 5, energy_loss = 1, track_n_rolling_gains = 4*3,
                 initial_energy = 10, regrowth_time = 10, food_bool = False, no_fish_zone_bool = False, quotum_bool = False, no_fish_size = 0, quotum = 0,
                ):
        super().__init__()

        # Initialization
        self.height = height
        self.width = width
        self.initial_fish = initial_fish
        self.initial_fishermen = initial_fishermen
        self.initial_wallet = initial_wallet
        self.initial_wallet_survival = initial_wallet_survival
        self.initial_school_size = initial_school_size
        self.cumulative_gain = 0

        # Booleans
        self.food_bool = food_bool
        self.no_fish_zone_bool = no_fish_zone_bool
        self.quotum_bool = quotum_bool

        #  Fish
        self.fish_reproduction_number = fish_reproduction_number
        self.split_size = split_size
        self.fish_cap = 5 * initial_fish * initial_school_size
        self.this_avg_school_size = initial_school_size

        # Fisherman
        self.max_load = max_load
        self.full_catch_reward = full_catch_reward
        self.catch_rate = catch_rate
        if self.quotum_bool == True:
            self.yearly_quotum = quotum
        else:
            self.yearly_quotum = 1000000000
        self.total_yearly_caught = 0
        self.total_yearly_caught_prev = 8000
        self.recruitment_switch = True
        self.beta_fisherman_spawn = beta_fisherman_spawn
        self.this_avg_wallet = initial_wallet
        self.track_n_rolling_gains = track_n_rolling_gains

        # food
        self.energy_gain = energy_gain
        if self.food_bool == False:
            self.energy_loss = 0
        else:
            self.energy_loss = energy_loss
        self.initial_energy = initial_energy
        self.regrowth_time = regrowth_time
        self.food_amount = height*width

        # No fish zone
        if self.no_fish_zone_bool == True:
            self.no_fish_size = int(no_fish_size*(1/no_fish_size)**(1/2) * width)
        else:
            self.no_fish_size = 0

        # Add a schedule for fish and fishermen seperately to prevent race-conditions
        # self.schedule = RandomActivation(self)
        # new_agent()
        self.schedule_Fish = RandomActivation(self)
        self.schedule_Fisherman = RandomActivation(self)
        if self.food_bool == True:
            self.schedule_Food = RandomActivation(self)

        self.grid = MultiGrid(self.width, self.height, torus=True)

        if self.food_bool == True:
            self.datacollector = DataCollector(
                 {"Fish schools": lambda m: self.schedule_Fish.get_agent_count(),
                  "Fishermen": lambda m: self.schedule_Fisherman.get_agent_count(),
                  "Average wallet": lambda m: self.this_avg_wallet,
                  "Average school size": lambda m: self.this_avg_school_size,
                  "Total fish": lambda m: self.schedule_Fish.get_agent_count() * self.this_avg_school_size*0.01,
                  "Available food": lambda m: self.food_amount,
                  "Cumulative gain": lambda m: self.cumulative_gain,
                  "Fish price": lambda m: self.full_catch_reward})
        else:
            self.datacollector = DataCollector(
                 {"Fish schools": lambda m: self.schedule_Fish.get_agent_count(),
                  "Fishermen": lambda m: self.schedule_Fisherman.get_agent_count(),
                  "Average wallet": lambda m: self.this_avg_wallet,
                  "Average school size": lambda m: self.this_avg_school_size,
                  "Total fish": lambda m: self.schedule_Fish.get_agent_count() * self.this_avg_school_size*0.01,
                  "Cumulative gain": lambda m: self.cumulative_gain,
                  "Fish price": lambda m: self.full_catch_reward})

        # Keep a list of all agents
        self.agents = []

        # Create fish and fishermen
        self.init_population(Fish, self.initial_fish)
        self.init_population(Fisherman, self.initial_fishermen)
        if self.food_bool == True:
            self.init_food()


        # This is required for the datacollector to work
        self.running = True
        self.datacollector.collect(self)

    def init_food(self):
        '''
        Fills grid with fish food
        '''
        for i in range(self.width):
            for j in range(self.height):
                self.new_agent(Food, (i,j), 0, 0, True, self.regrowth_time, True, 0)

    def init_population(self, agent_type, n):
        '''
        Method that provides an easy way of making a bunch of agents at once.
        '''
        for i in range(n):
            x = random.randrange(self.width)
            y = random.randrange(self.height)

            if agent_type == Fish:
              self.new_agent(agent_type, (x, y), self.initial_school_size, self.initial_energy, True, 0, False, self.energy_loss)
            else:
              self.new_agent(agent_type, (x, 0), 0, self.initial_wallet, True, 0, False, 0)


    def new_agent(self, agent_type, pos, size, wallet, switch, regrowth_time, food, energy_loss):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        agent = agent_type(self.next_id(), self, pos, size, wallet, switch, regrowth_time, food, energy_loss)

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
        rolling_mean_gains = statistics.mean( [statistics.mean(fisherman.rolling_gains) for fisherman in self.schedule_Fisherman.agents] )

        # make sure that at least one fisherman exists, who wouldn't try a new bussiness in a new field?
        if self.schedule_Fisherman.get_agent_count() == 0:
            self.init_population(Fisherman, 1)
        # add new fisherman proportional to the profitability
        elif rolling_mean_gains > 0:
                n_new_fisherman = int( np.random.poisson(lam = rolling_mean_gains*self.beta_fisherman_spawn, size = 1) )
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

    def get_food_stats(self):
        food_amount = 0
        for agent in self.schedule_Food.agents:
            if agent.food == True:
                food_amount += 1
        self.food_amount = food_amount


    def calc_fish_reproduction(self):
        """
        Calculates the reproduction ratio for the fish per year, which caps the total fish pop.
        """
        total_fish = self.schedule_Fish.get_agent_count() * self.this_avg_school_size

        percentage = 1 - (self.fish_cap - total_fish)/self.fish_cap

        self.fish_reproduction_number = 0.2/(1+0.00005**(-(percentage-0.5))) + 1
        # print(self.fish_reproduction_number)
        # the function doesn't cap at 1 exactly, so making sure it does here
        if percentage == 1:
            self.fish_reproduction_number = 1

    def get_fisherman_stats(self):
        '''
        Method that computes information about fisherman.
        '''
        fisherman_wallet = [fisherman.wallet for fisherman in self.schedule_Fisherman.agents]
        if len(fisherman_wallet) == 0:
            self.this_avg_wallet = 0
        else:
            self.this_avg_wallet = sum(fisherman_wallet) / len(fisherman_wallet)

    def get_fish_price(self):
        '''
        Method for computing reward for fish based on number of previous fish caught
        '''
        if (self.schedule_Fish.time + 1) % (4*12) == 0:
            
            if self.total_yearly_caught == 0:
                self.full_catch_reward = 20
            else:
                self.full_catch_reward = 100 * self.total_yearly_caught_prev/self.total_yearly_caught
                if self.full_catch_reward < 20:
                    self.full_catch_reward = 20
                if self.full_catch_reward > 250:
                    self.full_catch_reward = 250

            self.total_yearly_caught_prev = self.total_yearly_caught
            self.total_yearly_caught = 0
            self.recruitment_switch = True
        

    def step(self):
        '''
        Method that calls the step method for each of the sheep, and then for each of the wolves.
        '''

        self.calc_fish_reproduction()
        self.get_fish_price()

        self.schedule_Fish.step()
        self.schedule_Fisherman.step()

        if self.food_bool == True:
            self.schedule_Food.step()
            self.get_food_stats()

        self.get_fish_stats()
        self.get_fisherman_stats()

        if self.recruitment_switch == True and (self.schedule_Fish.time + 1) % 4*3 == 0:
            self.recruit_fisherman()

        # Save the statistics
        if (self.schedule_Fish.time + 4*6) % (4*12) == 0:
            self.datacollector.collect(self)

    def run_model(self, step_count):
        '''
        Method that runs the model for a specific amount of steps.
        '''

        for i in range(step_count):

            # if either the Fish or the Fishermen amount reaches 0, stop.
            if self.schedule_Fish.get_agent_count() == 0 or self.schedule_Fisherman.get_agent_count() == 0:
                break

            if self.total_yearly_caught >= self.yearly_quotum:
                self.recruitment_switch = False

            self.step()
