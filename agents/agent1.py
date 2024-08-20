from .base_agent import Agent

# complete information setting
# implemented in base agent since all agents build upon agent 1


class Agent1(Agent):
	def __init__(self, env, pos=None):
		super(Agent1, self).__init__(env, pos)
