import gym
from gym import spaces
from arrival_rate import ArrivalController
import numpy as np

epsilon = 1e-6
infinity = 1e09

def column(matrix, i):
    return [row[i] for row in matrix]

class DarkForestEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    max_step = ArrivalController.slot_num

    # action format:
    # [ transfer matrix, purchased_vm, transfer_budget]
    def __init__(self):
        self.observation_space = spaces.Box(low=0, high=ArrivalController.max_user,
                shape=(ArrivalController.server_num))

        self.action_space = spaces.MultiDiscrete(
            [ [0,12] for i in range((ArrivalController.server_num+1) * ArrivalController.server_num + 1) ]
        )

        self.latency = [1 for i in range(ArrivalController.server_num)]
        self.transfer_cost = [
                [2,3,4],
                [3,1,2],
                [5,2,2] ]
        self.purchase_cost = [1, 2, 4, 5, 6, 5, 2, 3, 4, 2,
                              2, 2, 3, 3, 2, 2, 5, 3, 2, 3,
                              2, 1, 1, 1]
        self.reset()

    def vm_operations(self,action): # vm deployment and transferring:
        action[-1] = 30
        action_vm = np.array(action[:-1]).reshape(
                ArrivalController.server_num+1,
                ArrivalController.server_num
                )

        budget_transfer = action[-1]
        self.budget_remain -= budget_transfer
        vm = []
        for i in range(ArrivalController.server_num):
            transferred_vm = 0
            for j in range(ArrivalController.server_num):
                if j != i:
                    transferred_vm += action_vm[j][i]
            purchased_vm = action_vm[-1][i]
            self.budget_remain -= purchased_vm * self.purchase_cost[self.step_index]
            vm.append(transferred_vm + purchased_vm)

        feasible = True
        if budget_transfer < 0 or self.budget_remain < 0:
            feasible = False

        return vm, feasible


    def _step(self, action):
        ob = column(self.arrival_users, self.step_index)
        (vm, feasible) = self.vm_operations(action)

        if feasible == False:
            self.min_utility = 0

        for i in range(ArrivalController.server_num):
            self.accumulated_latency[i] += ob[i]/(vm[i] + epsilon)

        utility = min(np.true_divide(vm, map( lambda x: x+epsilon, ob)))

        if utility < self.min_utility:
            self.min_utility = utility

        self.step_index += 1

        episode_over = False
        reward = 0
        if self.step_index >= DarkForestEnv.max_step:
            self.latency = [ x/ArrivalController.slot_num for x in self.accumulated_latency ]
            episode_over = True
            reward = self.min_utility

        print map(int,ob)
        return ob, reward, episode_over, {}


    def _reset(self):
        self.accumulated_latency = [0 for i in range(ArrivalController.server_num) ]
        self.controller = ArrivalController(latency_list = self.latency)
        self.arrival_users = self.controller.get_arrival_users()
        self.step_index = 0
        self.min_utility = infinity
        self.budget_remain = 5000
        ob = column(self.arrival_users, self.step_index)
        return ob

    def _render(self, mode='human', close=False):
        pass


