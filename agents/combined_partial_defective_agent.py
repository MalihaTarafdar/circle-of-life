import random
from config import *
from .predator_partial_agent import PredatorPartialAgent
from .prey_partial_agent import PreyPartialAgent

# abstract class - agent with partial prey and predator information
# with defective survey drone (may return false negative)

"""
belief system observation updates (6 cases)

(1) prey in surveyed node
Belief(t,i) =
	1  if i contains prey
	0  otherwise

(2) prey not in surveyed node and Belief(t,s) is 1
s = surveyed node
Belief(t+1,i) =
	0.9 / deg(s)  if i in neighbors(s)
	0.1           otherwise

(3) prey not in surveyed node and Belief(t,s) is not 1
s = surveyed node
Belief(t+1,i) =
	0.1                                    if i is s
	Belief(t,i) * 0.9 / (1 - Belief(t,s))  otherwise

(4) predator in surveyed node
Belief(t,i) =
	1  if i contains predator
	0  otherwise

(5) predator not in surveyed node and Belief(t,s) is 1
s = surveyed node
Belief(t+1,i) =
	0.9 * Transition(t,j,i) for j in neighbors(i)  if i is s
	0.1                                            otherwise

(6) predator not in surveyed node and Belief(t,s) is not 1
s = surveyed node
Belief(t+1,i) =
	0.1                                    if i is s
	Belief(t,i) * 0.9 / (1 - Belief(t,s))  otherwise


After each step,
a = node with agent
Belief(t+1,i) =
	0                                if i is a
	Belief(t,i) / (1 - Belief(t,a))  otherwise
"""


class CombinedPartialDefectiveAgent(PreyPartialAgent, PredatorPartialAgent):
	def __init__(self, env, pos=None):
		super(CombinedPartialDefectiveAgent, self).__init__(env, pos)


	# survey node for prey with defective drone
	def survey_prey(self, node, env):
		# chance to return false negative
		if env.vertices[node].has_prey:
			r = random.random()
			return r >= DRONE_DEFECTIVE_PROB

		return False


	# survey node for predator with defective drone
	def survey_predator(self, node, env):
		# chance to return false negative
		if env.vertices[node].has_predator:
			r = random.random()
			return r >= DRONE_DEFECTIVE_PROB

		return False


	# updates beliefs based on whether or not given node contains prey
	def prey_observation_update(self, node, has_prey, env):
		# node contains prey (case 1)
		if has_prey:
			self.prey_beliefs.fill(0)
			self.prey_beliefs[node] = 1
		# node does not contain prey
		else:
			# if was certain prey was in surveyed node (case 2)
			if self.is_one(self.prey_beliefs[node]):
				# prey transitioned to a neighbor
				neighbors = env.vertices[node].neighbors
				for n in neighbors:
					self.prey_beliefs[n] = (1 - DRONE_DEFECTIVE_PROB) / (len(neighbors))
				self.prey_beliefs[node] = DRONE_DEFECTIVE_PROB
			# if was not certain prey was in surveyed node (case 3)
			else:
				# set surveyed node belief to DRONE_DEFECTIVE_PROB & redistribute
				s = 1 - self.prey_beliefs[node]
				for i in range(N):
					if i != node:
						self.prey_beliefs[i] *= (1 - DRONE_DEFECTIVE_PROB) / s
				self.prey_beliefs[node] = DRONE_DEFECTIVE_PROB

		# set agent node belief to 0 (if not already) & redistribute
		if self.prey_beliefs[self.pos] != 0:
			for i in range(N):
				if i != self.pos:
					self.prey_beliefs[i] /= (1 - self.prey_beliefs[self.pos])
			self.prey_beliefs[self.pos] = 0

		self.verify_belief_sum(self.prey_beliefs)


	# updates beliefs based on whether or not given node contains predator
	def predator_observation_update(self, node, has_predator, env):
		# node contains predator (case 4)
		if has_predator:
			self.predator_beliefs.fill(0)
			self.predator_beliefs[node] = 1
		# node does not contain predator
		else:
			# if was certain predator was in surveyed node (case 5)
			if self.is_one(self.predator_beliefs[node]):
				# predator transitioned to a neighbor
				neighbors = env.vertices[node].neighbors
				for n in neighbors:
					self.predator_beliefs[n] = ((1 - DRONE_DEFECTIVE_PROB) *
							self.predator_transition_matrix[n][node])
				self.predator_beliefs[node] = DRONE_DEFECTIVE_PROB
			# if was not certain predator was in surveyed node (case 6)
			else:
				# set surveyed node belief to DRONE_DEFECTIVE_PROB & redistribute
				s = 1 - self.predator_beliefs[node]
				for i in range(N):
					if i != node:
						self.predator_beliefs[i] *= (1 - DRONE_DEFECTIVE_PROB) / s
				self.predator_beliefs[node] = DRONE_DEFECTIVE_PROB

		# set agent node belief to 0 (if not already) & redistribute
		if self.predator_beliefs[self.pos] != 0:
			for i in range(N):
				if i != self.pos:
					self.predator_beliefs[i] /= (1 - self.predator_beliefs[self.pos])
			self.predator_beliefs[self.pos] = 0

		self.verify_belief_sum(self.predator_beliefs)
