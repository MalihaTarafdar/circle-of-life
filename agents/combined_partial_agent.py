from .predator_partial_agent import PredatorPartialAgent
from .prey_partial_agent import PreyPartialAgent

# abstract class - agent with partial prey and predator information


class CombinedPartialAgent(PreyPartialAgent, PredatorPartialAgent):
	def __init__(self, env, pos=None):
		super(CombinedPartialAgent, self).__init__(env, pos)
