import random
from config import *
from graph_utils import shortest_dist

# abstract class - base agent


class Agent(object):
	def __init__(self, env, pos=None):
		super(Agent, self).__init__()
		# spawn agent randomly
		self.pos = pos if pos else random.randint(0, N - 1)
		# update environment
		env.vertices[self.pos].has_agent = True


	def select(self, env, prey_pos=None, predator_pos=None):
		# shortest distances from agent to prey and predator
		a_prey = shortest_dist(self.pos, prey_pos, env)
		a_predator = shortest_dist(self.pos, predator_pos, env)

		# shortest distances from neighbors to prey and predator
		neighbors = env.vertices[self.pos].neighbors.copy()
		n_prey = {}
		n_predator = {}
		for n in neighbors:
			n_prey[n] = shortest_dist(n, prey_pos, env)
			n_predator[n] = shortest_dist(n, predator_pos, env)

		# select from neighbors with specified priority
		# closer to prey = n_prey < a_prey
		# farther from predator = n_predator > a_predator
		# not closer to predator = n_predator == a_predator
		# not farther from prey = n_prey == a_prey
		conds = [] # priority conditions

		# closer to prey, farther from predator
		conds.append(lambda n: n_prey[n] < a_prey and n_predator[n] > a_predator)
		# closer to prey, not closer to predator
		conds.append(lambda n: n_prey[n] < a_prey and n_predator[n] == a_predator)
		# not farther from prey, farther from predator
		conds.append(lambda n: n_prey[n] == a_prey and n_predator[n] > a_predator)
		# not farther from prey, not closer to predator
		conds.append(lambda n: n_prey[n] == a_prey and n_predator[n] == a_predator)
		# farther from predator
		conds.append(lambda n: n_predator[n] > a_predator)
		# not closer to predator
		conds.append(lambda n: n_predator[n] == a_predator)

		for c in conds:
			selected_neighbors = list(filter(c, neighbors))
			if not selected_neighbors: # continue if empty
				continue

			# move selected
			if len(selected_neighbors) == 1:
				return selected_neighbors[0]

			# check for tie
			tie = True
			for i in range(len(selected_neighbors) - 1):
				n1 = selected_neighbors[i]
				n2 = selected_neighbors[i + 1]
				if n_prey[n1] != n_prey[n2] or n_predator[n1] != n_predator[n2]:
					tie = False
					break
			# break tie randomly
			if tie:
				return random.choice(selected_neighbors)
		
		# all else fails, sit still and pray
		return self.pos


	def move(self, env, prey_pos=None, predator_pos=None):
		env.vertices[self.pos].has_agent = False
		self.pos = self.select(env, prey_pos, predator_pos)
		env.vertices[self.pos].has_agent = True
