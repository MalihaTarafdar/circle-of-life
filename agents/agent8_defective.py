from .base_agent_improved import ImprovedAgent
from .combined_partial_defective_agent import CombinedPartialDefectiveAgent

# agent 8 with defective drone
# should out-perform agent 7 with defective drone


class Agent8Defective(ImprovedAgent, CombinedPartialDefectiveAgent):
	def __init__(self, env, pos=None):
		CombinedPartialDefectiveAgent.__init__(self, env, pos)


	def move(self, env, prey_pos=None, predator_pos=None):
		# if predator pos given, observation update
		if predator_pos:
			self.predator_observation_update(predator_pos, True, env)

		# check if certain where prey is
		prey_pos_guess = self.prey_pos_certain()
		if prey_pos_guess != -1:
			prey_pos = prey_pos_guess
		# check if certain where predator is
		predator_pos_guess = self.predator_pos_certain()
		if predator_pos_guess != -1:
			predator_pos = predator_pos_guess

		# if not certain where predator is, survey according to agent 5
		if not predator_pos:
			predator_pos = self.estimate_predator_pos(env)
			prey_pos = self.node_highest_prob_prey()
		else:
			# if not certain where prey is, survey according to agent 3
			if not prey_pos:
				prey_pos = self.estimate_prey_pos(env)
				predator_pos = self.node_highest_prob_predator(env)

		super(Agent8Defective, self).move(env, prey_pos, predator_pos)
