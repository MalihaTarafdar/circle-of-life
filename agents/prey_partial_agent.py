import numpy as np
import random
from config import *
from .base_agent import Agent

# abstract class - agent with partial prey information

"""
belief system (5 cases)

(1) initialization
Belief(0,i) =
	0     if i contains agent
	1/49  otherwise

(2) observation: prey in surveyed node
Belief(t,i) =
	1  if i contains prey
	0  otherwise

(3) observation: prey not in surveyed node and Belief(t,s) is 1
s = surveyed node
Belief(t+1,i) =
	1 / deg(s)  if i in neighbors(s)
	0           otherwise

(4) observation: prey not in surveyed node and Belief(t,s) is not 1
s = surveyed node
Belief(t+1,i) =
	0                                if i is s
	Belief(t,i) / (1 - Belief(t,s))  otherwise

(5) transition
Transition(t,j,i) =
	1 / (deg(i) + 1)  if (j is i) or (j in neighbors(i))
	0                 otherwise
Belief(t+1) = (Transition(t+1))(Belief(t))
"""


class PreyPartialAgent(Agent):
	def __init__(self, env, pos=None):
		super(PreyPartialAgent, self).__init__(env, pos)

		# initialize belief system for prey (case 1)
		self.prey_beliefs = np.empty(N)
		for i in range(N):
			# uniformly distribute probabilities
			# prey not in same node as agent
			self.prey_beliefs[i] = 1 / (N - 1) if i != self.pos else 0
		self.verify_belief_sum(self.prey_beliefs)
		
		# initialize transition matrix (case 5)
		self.prey_transition_matrix = np.empty((N, N))
		for i in range(N):
			for j in range(N):
				neighbors = env.vertices[i].neighbors
				if j == i or j in neighbors:
					self.prey_transition_matrix[j][i] = 1 / (len(neighbors) + 1)
				else:
					self.prey_transition_matrix[j][i] = 0
		self.verify_transition_matrix(self.prey_transition_matrix)


	# check if a given number is equal to 1, accounting for floating point error
	def is_one(self, x):
		return x >= 1 - ALLOWED_ERROR and x <= 1 + ALLOWED_ERROR


	def verify_belief_sum(self, beliefs):
		# sum of beliefs must be 1
		assert self.is_one(np.sum(beliefs))


	def verify_transition_matrix(self, transition_matrix):
		# sum of each column of transition matrix must be 1
		for r in range(N):
			assert self.is_one(np.sum(transition_matrix.T[r]))


	def node_highest_prob_prey(self):
		# find nodes with highest probability
		max_prob = max(self.prey_beliefs)
		max_prob_nodes = np.where(self.prey_beliefs == max_prob)[0]

		# break ties randomly
		return random.choice(max_prob_nodes)


	def survey_prey(self, node, env):
		return env.vertices[node].has_prey


	# updates beliefs based on whether or not given node contains prey
	def prey_observation_update(self, node, has_prey, env):
		# node contains prey (case 2)
		if has_prey:
			self.prey_beliefs.fill(0)
			self.prey_beliefs[node] = 1
		# node does not contain prey
		else:
			# if was certain prey was in surveyed node (case 3)
			if self.is_one(self.prey_beliefs[node]):
				# prey transitioned to a neighbor
				neighbors = env.vertices[node].neighbors
				for n in neighbors:
					self.prey_beliefs[n] = 1 / (len(neighbors))
				self.prey_beliefs[node] = 0
			# if was not certain prey was in surveyed node (case 4)
			else:
				# set surveyed node belief to 0 & redistribute
				for i in range(N):
					if i != node:
						self.prey_beliefs[i] /= (1 - self.prey_beliefs[node])
				self.prey_beliefs[node] = 0

		self.verify_belief_sum(self.prey_beliefs)


	# update beliefs based on transition probabilities (case 5)
	def prey_transition_update(self):
		self.prey_beliefs = np.dot(self.prey_transition_matrix, self.prey_beliefs)
		self.verify_belief_sum(self.prey_beliefs)


	# returns position of prey if agent is certain where it is
	def prey_pos_certain(self):
		for i in range(N):
			if self.is_one(self.prey_beliefs[i]):
				return i
		return -1


	def estimate_prey_pos(self, env):
		# don't survey node if certain where prey is
		prey_pos_guess = self.prey_pos_certain()
		if prey_pos_guess != -1:
			return prey_pos_guess

		# survey node with highest probability of containing prey
		survey_node = self.node_highest_prob_prey()
		has_prey = self.survey_prey(survey_node, env)

		# belief observation update (based on surveyed node)
		self.prey_observation_update(survey_node, has_prey, env)

		# assume prey located in node with highest probability
		return self.node_highest_prob_prey()
