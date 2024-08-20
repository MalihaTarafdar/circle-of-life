import random
from config import *


class Prey:
	def __init__(self, env, pos=None):
		# spawn prey randomly
		self.pos = pos if pos else random.randint(0, N - 1)
		# prey cannot spawn on agent
		while env.vertices[self.pos].has_agent:
			self.pos = random.randint(0, N - 1)
		# update environment
		env.vertices[self.pos].has_prey = True


	# selects among its neighbors and itself uniformly at random
	def select(self, env):
		possible_moves = env.vertices[self.pos].neighbors.copy()
		possible_moves.append(self.pos)
		return random.choice(possible_moves)


	def move(self, env):
		env.vertices[self.pos].has_prey = False
		self.pos = self.select(env)
		env.vertices[self.pos].has_prey = True
