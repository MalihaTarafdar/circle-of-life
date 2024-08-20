import random
from config import *
from predator import Predator


class EasilyDistractedPredator(Predator):
	def __init__(self, env, pos=None):
		super(EasilyDistractedPredator, self).__init__(env, pos)


	def select(self, env, agent_pos):
		# if predator is distracted, select random neighbor
		r = random.random()
		if r < DISTRACTED_PROB:
			return random.choice(env.vertices[self.pos].neighbors)

		return super(EasilyDistractedPredator, self).select(env, agent_pos)
