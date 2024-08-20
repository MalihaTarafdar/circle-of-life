import random
from config import *
from graph_utils import shortest_dist


class Predator:
	def __init__(self, env, pos=None):
		super(Predator, self).__init__()
		# spawn predator randomly
		self.pos = pos if pos else random.randint(0, N - 1)
		# predator cannot spawn on agent
		while env.vertices[self.pos].has_agent:
			self.pos = random.randint(0, N - 1)
		# update environment
		env.vertices[self.pos].has_predator = True


	# selects move with shortest distance to agent
	def select(self, env, agent_pos):
		# find shortest distance to agent from each move
		move_dist = {}
		min_dist = -1
		for move in env.vertices[self.pos].neighbors:
			move_dist[move] = shortest_dist(move, agent_pos, env)
			if min_dist == -1 or move_dist[move] < min_dist:
				min_dist = move_dist[move]

		# find moves with shortest distance
		best_moves = [] # moves with the shortest distance to agent
		for move, dist in move_dist.items():
			if dist == min_dist:
				best_moves.append(move)

		# if there are multiple moves with the shortest distance to agent,
		# pick move uniformly at random
		return random.choice(best_moves)


	def move(self, env, agent_pos):
		env.vertices[self.pos].has_predator = False
		self.pos = self.select(env, agent_pos)
		env.vertices[self.pos].has_predator = True
