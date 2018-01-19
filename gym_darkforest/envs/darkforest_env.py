
# coding: utf-8

# In[1]:


import gym
from gym import error, spaces, utils
from gym.utils import seeding

from arrival_rate import *
from reward import *

class MyClient:

    total_budget = 500

    def __init__(self):
        self.latency = [1, 1, 1]

        self.controller = ArrivalController(latency_list = self.latency)

        self.purchase_budget = 140
        self.transfer_budget = [ 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
                                 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
                                 15, 15, 15, 15
                               ]

        # We must have purchase_budget + transfer_budget <= total_budget !

    def get_state(self):
        return self.latency

    def execute(self, action): # action is in the exactly same format as state
        if sum(action) > MyClient.total_budget:
            self.purchase_budget = 0
            self.transfer_budget = [0 for i in range(ArrivalController.slot_num)]
        self.purchase_budget = action[0]
        self.transfer_budget = action[1:ArrivalController.slot_num+1]

        self.controller.set_latency(self.latency)

        d = self.controller.get_arrival_users()
        P = self.purchase_budget
        C = self.transfer_budget

        problem = Problem(d,P,C)
        result = problem.solve()

        reward = result[0]
        x = result[1]
        
        self.latency = map(lambda x: sum(x)/ArrivalController.slot_num,
                           np.divide( np.array(d), np.array(x) + 1e-6 ) )
        return reward

class DarkForestEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    max_step = 100

    def __init__(self):
        self.client = MyClient()

        self.observation_space = spaces.Box(low=0, high=100000, shape=(3))
        self.action_space = spaces.Box(low=0, high=10, shape=(1 + ArrivalController.slot_num,)) # Set with 8 elements {0, 1, 2, ..., 7}
        self.step_index = 0

    def _step(self, action):


        action[0] = 150
        if sum(action) > MyClient.total_budget:
            reward = -1
        else:
            reward = self.client.execute(action)


        if reward >= 250000:

            print action
            print reward
            raw_input()
            
        ob = self.client.get_state()
        
        self.step_index += 1
        
        episode_over = False
        if self.step_index >= DarkForestEnv.max_step:
            episode_over = True
            self.step_index = 0
            
        return ob, reward, episode_over, {}
    
    
    def _reset(self):
        state = self.client.get_state()
        return state

    def _render(self, mode='human', close=False):
        pass


# In[ ]:


# !jupyter nbconvert --to script lei.ipynb

