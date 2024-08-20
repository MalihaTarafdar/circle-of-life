from .base_agent_improved import ImprovedAgent
from .predator_partial_agent import PredatorPartialAgent

# partial predator information setting
# should out-perform agent 5


class Agent6(ImprovedAgent, PredatorPartialAgent):
	def __init__(self, env, pos=None):
		PredatorPartialAgent.__init__(self, env, pos)


	def move(self, env, prey_pos=None, predator_pos=None):
		# if predator pos given, observation update instead of survey
		if not predator_pos:
			predator_pos = self.estimate_predator_pos(env)
		else:
			self.predator_observation_update(predator_pos, True, env)

		super(Agent6, self).move(env, prey_pos, predator_pos)
