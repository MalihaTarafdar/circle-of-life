from .prey_partial_agent import PreyPartialAgent

# partial prey information setting


class Agent3(PreyPartialAgent):
	def __init__(self, env, pos=None):
		super(Agent3, self).__init__(env, pos)


	def move(self, env, prey_pos=None, predator_pos=None):
		prey_pos = self.estimate_prey_pos(env)
		super(Agent3, self).move(env, prey_pos, predator_pos)
