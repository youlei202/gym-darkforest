from gym.envs.registration import register

register(
    id='darkforest-v0',
    entry_point='gym_darkforest.envs:DarkForestEnv',
)
