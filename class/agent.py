from mesa import Agent, Model
from model import FishingModel

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
    def __init__(self, id, model, pos, size):
        super().__init__(id, model, pos, size)

    def step(self):
        '''
        Randomly move Fish school and spawn new fish every year
        '''

        curr_time = self.model.schedule_Fish.time
        self.move()

        # New fish spawn yearly
        if curr_time % 365 == 0:
            self.size *= self.model.fish_reproduction_number

        # Schools above N tonnes will split in half
        if self.size > self.model.split_size:
            self.model.new_agent(Fish, self.pos, self.size*0.5, 0, True, 0)
            self.size *= 0.5

        # Schools under a threshold are removed
        if self.size < 1:
            self.model.remove_agent(self)


class Fisherman(Random):
    def __init__(self, id, model, pos, size, wallet, switch, init_wait_time):
        super().__init__(id, model, pos, size, wallet, switch, init_wait_time)

    def step(self):

        if switch == False:
            curr_time = self.model.schedule_Fisherman.time
            self.move()

            surrounding = MultiGrid.get_neighbors(self.model.grid, self.pos, True, True,0)

            for fish in surrounding:

                if type(agent) == Fish:
                    if agent.size <= self.model.catch_rate:
                        self.size += agent.size
                        agent.size = 0
                    elif self.model.catch_rate - self.size < self.model.max_load:
                        agent.size -= self.model.catch_rate - self.size
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

            if self.wallet == 0:
                self.model.remove_agent(self)

            # Daily cost of living
            self.wallet -= 1000

            total_wallet = 0
            for agent in self.model.agents:
                total_wallet += agent.wallet

            wallet_mean = total_wallet / self.schedule_Fisherman.get_agent_count()

            if wallet_mean > 30000:
                self.model.new_agent(Fisherman, self.pos, 0, self.model.initial_wallet, False, 0)

        # Pauzes if load is full
        elif self.model.schedule_Fisherman.time - self.init_wait_time > 4:
            self.switch = False
