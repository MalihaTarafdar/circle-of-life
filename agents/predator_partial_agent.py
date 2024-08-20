import numpy as np
import random
from config import *
from graph_utils import shortest_dist
from .base_agent import Agent

# abstract class - agent with partial predator information

"""
belief system (5 cases)

(1) initialization
Belief(0,i) =
	0     if i contains agent
	1/49  otherwise

(2) observation: predator in surveyed node
Belief(t,i) =
	1  if i contains predator
	0  otherwise

(3) observation: predator not in surveyed node and Belief(t,s) is 1
s = surveyed node
Belief(t+1,i) =
	Transition(t,j,i) for j in neighbors(i)  if i is s
	0                                        otherwise

(4) observation: predator not in surveyed node and Belief(t,s) is not 1
s = surveyed node
Belief(t+1,i) =
	0                                if i is s
	Belief(t,i) / (1 - Belief(t,s))  otherwise

(5) transition
d(i) = shortest distance from i to agent
c = count j where d(j) == min(d(n)) for n in neighbors(i)
Transition(t,j,i) =
	0.6 / c + 0.4 / deg(i)  if j in neighbors(i) and d(j) == min(d(n)) for n in neighbors(i)
	0.4 / deg(i)            if j in neighbors(i) and d(j) != min(d(n)) for n in neighbors(i)
	0                       otherwise
Belief(t+1) = (Transition(t+1))(Belief(t))
"""


class PredatorPartialAgent(Agent):
	def __init__(self, env, pos=None):
		super(PredatorPartialAgent, self).__init__(env, pos)

		# initialize belief system for predator (case 1)
		self.predator_beliefs = np.empty(N)
		for i in range(N):
			# uniformly distribute probabilities
			# predator not in same node as agent
			self.predator_beliefs[i] = 1 / (N - 1) if i != self.pos else 0
		self.verify_belief_sum(self.predator_beliefs)
		
		# initialize transition matrix
		self.predator_transition_matrix = np.empty((N, N))
		self.set_transition_matrix(env)


	# set transition matrix (case 5)
	def set_transition_matrix(self, env):
		for i in range(N):
			for j in range(N):
				neighbors = env.vertices[i].neighbors
				if j in neighbors:
					j_dist = shortest_dist(j, self.pos, env)
					# count neighbors with min shortest dist
					dists = [shortest_dist(n, self.pos, env) for n in neighbors]
					min_dist = min(dists)
					c = dists.count(min_dist)
					# set transition probability based on shortest distances
					if j_dist == min_dist:
						p = (1 - DISTRACTED_PROB) / c + DISTRACTED_PROB / len(neighbors)
						self.predator_transition_matrix[j][i] = p
					else:
						self.predator_transition_matrix[j][i] = DISTRACTED_PROB / len(neighbors)
				else:
					self.predator_transition_matrix[j][i] = 0

		self.verify_transition_matrix(self.predator_transition_matrix)


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


	def node_highest_prob_predator(self, env):
		# find nodes with max probability
		max_prob = max(self.predator_beliefs)
		max_prob_nodes = np.where(self.predator_beliefs == max_prob)[0]

		# find nodes with max probability and min distance to agent
		min_dist = min([shortest_dist(n, self.pos, env) for n in max_prob_nodes])
		best_nodes = [] # nodes with shortest distance
		for n in max_prob_nodes:
			if shortest_dist(n, self.pos, env) == min_dist:
				best_nodes.append(n)

		# break ties by proximity to agent, then by random
		return random.choice(best_nodes)


	def survey_predator(self, node, env):
		return env.vertices[node].has_predator


	# updates beliefs based on whether or not given node contains predator
	def predator_observation_update(self, node, has_predator, env):
		# node contains predator (case 2)
		if has_predator:
			self.predator_beliefs.fill(0)
			self.predator_beliefs[node] = 1
		# node does not contain predator
		else:
			# if was certain predator was in surveyed node (case 3)
			if self.is_one(self.predator_beliefs[node]):
				# predator transitioned to a neighbor
				neighbors = env.vertices[node].neighbors
				for n in neighbors:
					self.predator_beliefs[n] = self.predator_transition_matrix[n][node]
				self.predator_beliefs[node] = 0
			# if was not certain predator was in surveyed node (case 4)
			else:
				# set surveyed node belief to 0 & redistribute
				for i in range(N):
					if i != node:
						self.predator_beliefs[i] /= (1 - self.predator_beliefs[node])
				self.predator_beliefs[node] = 0

		self.verify_belief_sum(self.predator_beliefs)


	# update beliefs based on transition probabilities (case 5)
	def predator_transition_update(self, env):
		self.set_transition_matrix(env)
		self.predator_beliefs = np.dot(self.predator_transition_matrix, self.predator_beliefs)
		self.verify_belief_sum(self.predator_beliefs)


	# returns position of predator if agent is certain where it is
	def predator_pos_certain(self):
		for i in range(N):
			if self.is_one(self.predator_beliefs[i]):
				return i
		return -1


	def estimate_predator_pos(self, env):
		# don't survey node if certain where predator is
		predator_pos_guess = self.predator_pos_certain()
		if predator_pos_guess != -1:
			return predator_pos_guess

		# survey node with highest probability of containing predator
		survey_node = self.node_highest_prob_predator(env)
		has_predator = self.survey_predator(survey_node, env)

		# belief observation update (based on surveyed node)
		self.predator_observation_update(survey_node, has_predator, env)

		# assume predator located in node with highest probability
		return self.node_highest_prob_predator(env)
