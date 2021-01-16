from mesa import Agent, Model
from mesa.space import MultiGrid
import random

# from classes.model import FishingModel

class Random(Agent):
    def __init__(self, id, model, pos, size, wallet, switch, init_wait_time):
        super().__init__(id, model)

        self.pos = pos
        self.size = size
        self.wallet = wallet
        self.switch = switch
        self.init_wait_time = init_wait_time

    def move(self):
        neighbourhood = MultiGrid.get_neighborhood(self.model.grid, self.pos, True, False, 1)
        new_pos = random.choice(neighbourhood)
        MultiGrid.move_agent(self.model.grid, self, new_pos)


class Fish(Random):
    def __init__(self, id, model, pos, size, wallet, switch, init_wait_time):
        super().__init__(id, model, pos, size, wallet, switch, init_wait_time)

    def step(self):
        '''
        Randomly move Fish school and spawn new fish every year
        '''

        curr_time = self.model.schedule_Fish.time
        self.move()

        # New fish spawn every 52 weeks (added + 1 just so they don't reproduce immediately)
        if (curr_time + 1) % 52 == 0:
            print('reproduction2', curr_time)
            self.size *= self.model.fish_reproduction_number
            # print('SIZE INCREASED TO', self.size)

        # Schools above N tonnes will split in half
        if self.size > self.model.split_size:
            # print('SPLITTING')
            self.model.new_agent(Fish, self.pos, self.size*0.5, 0, True, 0)
            self.size *= 0.5

        # Schools under a threshold are removed
        if self.size < (self.model.initial_school_size / 20):
            self.model.remove_agent(self)

class Fisherman(Random):
    def __init__(self, id, model, pos, size, wallet, switch, init_wait_time):
        super().__init__(id, model, pos, size, wallet, switch, init_wait_time)

        self.start_wait_time = 0
        
    def step(self):

        # fishing or waiting behavior
        #if not self.switch:
        if self.model.total_yearly_caught < self.model.yearly_quotum:
                
            self.move()

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
                    
                    print(self.model.total_yearly_caught)
                break
        
            if self.size == self.model.max_load:
                self.size    = 0
                self.wallet += self.model.full_catch_reward
                #self.switch  = True
                self.start_wait_time = self.model.schedule_Fisherman.time
                
            # Pauses if load is full
            # elif self.start_wait_time + self.model.fisherman_wait_time > self.model.schedule_Fisherman.time:
            #     self.switch = False

            # paying the weekly cost of living
            self.wallet -= self.model.initial_wallet / self.model.initial_wallet_survival

            # removing ig going bankrupt
            if self.wallet <= 0:
                self.model.remove_agent(self)
        