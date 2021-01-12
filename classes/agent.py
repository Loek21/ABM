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

        # New fish spawn yearly (added + 1 just so they don't reproduce immediately)
        if (curr_time + 1) % 365 == 0:
            self.size *= self.model.fish_reproduction_number
            print('SIZE INCREASED TO', self.size)

        # Schools above N tonnes will split in half
        if self.size > self.model.split_size:
            print('SPLITTING')
            self.model.new_agent(Fish, self.pos, self.size*0.5, 0, True, 0)
            self.size *= 0.5

        # Schools under a threshold are removed
        if self.size < 1:
            self.model.remove_agent(self)
        
        total_fish = 0
        for agent in self.model.agents:
            total_fish += agent.size

        average_school = total_fish / self.model.schedule_Fish.get_agent_count()
        self.model.avg_school_size = average_school


class Fisherman(Random):
    def __init__(self, id, model, pos, size, wallet, switch, init_wait_time):
        super().__init__(id, model, pos, size, wallet, switch, init_wait_time)

    def step(self):

        if self.switch == False:
            curr_time = self.model.schedule_Fisherman.time
            self.move()

            surrounding = MultiGrid.get_neighbors(self.model.grid, self.pos, True, True,0)

            for agent in surrounding:

                if type(agent) == Fish:
                    if agent.size <= self.model.catch_rate:
                        self.size += agent.size
                        agent.size = 0
                    elif self.model.max_load - self.size < self.model.catch_rate:
                        agent.size -= self.model.max_load - self.size
                        self.size = self.model.max_load
                    else:
                        agent.size -= self.model.catch_rate
                        self.size += self.model.catch_rate
                break

            if self.size == self.model.max_load:
                self.size = 0
                self.wallet += self.model.initial_wallet
                self.switch = True
                self.init_wait_time = curr_time
            
        # Pauzes if load is full
        elif self.model.schedule_Fisherman.time - self.init_wait_time > 4:
            self.switch = False

        total_wallet = 0
        for agent in self.model.agents:
            total_wallet += agent.wallet

        wallet_mean = total_wallet / self.model.schedule_Fisherman.get_agent_count()
        self.model.avg_wallet = wallet_mean

        if wallet_mean > 40000:
            for _ in range(max(5,int(self.model.schedule_Fisherman.get_agent_count()*0.05))):
                self.model.new_agent(Fisherman, self.pos, 0, self.model.initial_wallet, False, 0)

        # Daily cost of living
        self.wallet -= 750

        if self.wallet <= 0:
            if self.model.schedule_Fisherman.get_agent_count() <= 1:
                self.model.new_agent(Fisherman, self.pos, 0, self.model.initial_wallet, False, 0)
            self.model.remove_agent(self)
        
        

