from .base_agent_improved import ImprovedAgent
from .prey_partial_agent import PreyPartialAgent

# partial prey information setting
# should out-perform agent 3


class Agent4(ImprovedAgent, PreyPartialAgent):
	def __init__(self, env, pos=None):
		PreyPartialAgent.__init__(self, env, pos)


	def move(self, env, prey_pos=None, predator_pos=None):
		prey_pos = self.estimate_prey_pos(env)
		super(Agent4, self).move(env, prey_pos, predator_pos)
