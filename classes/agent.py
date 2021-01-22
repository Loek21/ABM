from mesa import Agent, Model
from mesa.space import MultiGrid
import random
import statistics as statistics

# from classes.model import FishingModel

class Random(Agent):
    def __init__(self, id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss):
        super().__init__(id, model)

        self.pos    = pos
        self.size   = size
        self.wallet = wallet
        self.switch = switch
        self.energy_loss = energy_loss

        # for food
        self.regrowth_time = regrowth_time
        self.food = True

    def move(self):
        neighbourhood = MultiGrid.get_neighborhood(self.model.grid, self.pos, True, False, 1)
        new_pos = random.choice(neighbourhood)
        MultiGrid.move_agent(self.model.grid, self, new_pos)

    def fisherman_move(self):
    	neighbourhood = MultiGrid.get_neighborhood(self.model.grid, self.pos, True, False, 1)
    	new_pos = random.choice(neighbourhood)
    	while (new_pos[0] < self.model.no_fish_size) and (new_pos[1] < self.model.no_fish_size):
    		new_pos = random.choice(neighbourhood)

    	MultiGrid.move_agent(self.model.grid, self, new_pos)

class Food(Random):
    def __init__(self, id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss):
        super().__init__(id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss)

    def step(self):
        if self.food == False:
            self.regrowth_time -= 1
            if self.regrowth_time <= 0:
                self.food = True
                self.regrowth_time = self.model.regrowth_time


class Fish(Random):
    def __init__(self, id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss):
        super().__init__(id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss)

    def step(self):
        '''
        Randomly move Fish school and spawn new fish every year
        '''

        curr_time = self.model.schedule_Fish.time
        self.move()

        # New fish spawn every 52 weeks (added + 1 just so they don't reproduce immediately)
        if (curr_time + 1) % 48 == 0:
            if self.model.food_bool == False:
                self.size *= self.model.fish_reproduction_number*random.uniform(0.95,1.05)
                # print(self.model.fish_reproduction_number)
            else:
                self.size *= self.model.fish_reproduction_number*random.uniform(0.95,1.05)

        # Looking for Food
        surrounding = MultiGrid.get_neighbors(self.model.grid, self.pos, True, True,0)

        for agent in surrounding:

            if type(agent) == Food and agent.food == True:
                agent.food = False
                self.wallet += self.model.energy_gain
                break
            elif type(agent) == Fisherman:
                pass
            else:
                if self.model.food_bool == True:
                    percentage = 1 - (self.model.split_size - self.size)/self.model.split_size
                    self.energy_loss = 1/(1+0.00005**(percentage-0.5)) + 1
                self.wallet -= self.energy_loss
                break

        if self.wallet <= 0 and self.model.food_bool == True:
            self.size /= 2
            self.wallet += self.model.energy_gain

        # Schools above N tonnes will split in half
        if self.size > self.model.split_size and random.uniform(0,1) > 0.75:
            # print('SPLITTING')
            self.model.new_agent(Fish, self.pos, self.size*0.5, self.wallet*0.5, True, 0, False, self.model.energy_loss)
            self.size *= 0.5
            if self.model.food_bool == True:
                self.wallet *= 0.5

        # Schools under a threshold are removed
        if self.size < (self.model.initial_school_size / 20):
            self.model.remove_agent(self)

class Fisherman(Random):
    def __init__(self, id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss):
        super().__init__(id, model, pos, size, wallet, switch, regrowth_time, food, energy_loss)

        self.start_wait_time = 0
        self.rolling_gains   = [0] * self.model.track_n_rolling_gains

    def step(self):

        temp_gain = 0

        # fishing or waiting behavior
        #if not self.switch:
        if self.model.total_yearly_caught < self.model.yearly_quotum:

            self.fisherman_move()

            surrounding = MultiGrid.get_neighbors(self.model.grid, self.pos, True, True,0)

            for agent in surrounding:

                if type(agent) == Fish:

                    if agent.size <= self.model.catch_rate:
                        self.size += agent.size
                        self.model.total_yearly_caught += agent.size
                        agent.size = 0
                    elif self.model.max_load - self.size < self.model.catch_rate:
                        agent.size -= self.model.max_load - self.size
                        self.size = self.model.max_load
                        self.model.total_yearly_caught += self.model.max_load - self.size
                    else:
                        agent.size -= self.model.catch_rate
                        self.size += self.model.catch_rate
                        self.model.total_yearly_caught += self.model.catch_rate

                    # print(self.model.total_yearly_caught)
                    break

            if self.size == self.model.max_load:
                self.size    = 0
                temp_gain    += self.model.full_catch_reward
                #self.switch  = True
                self.start_wait_time = self.model.schedule_Fisherman.time

        # paying the weekly cost of living
        temp_gain -= self.model.initial_wallet / self.model.initial_wallet_survival

        # removing ig going bankrupt
        if self.wallet <= 0:
            self.model.remove_agent(self)

        # update the rolling gains
        del self.rolling_gains[0]
        self.rolling_gains.append(temp_gain)

        # update the wallet
        self.wallet  += temp_gain

        # update the overall cumulative gain
        self.model.cumulative_gain += temp_gain
