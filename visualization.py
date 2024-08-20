# script for visualization

import math
import pygame
import sys
import main
from config import *


SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

CIRCLE_OF_LIFE_RADIUS = 250
NODE_RADIUS = 10

BACKGROUND_COLOR = (0, 0, 0) # black
TEXT_COLOR = (255, 255, 255) # white
NODE_COLOR = (255, 255, 255) # white
EDGE_COLOR = (255, 255, 255) # white
AGENT_COLOR = (0, 0, 255) # blue
PREDATOR_COLOR = (255, 0, 0) # red
PREY_COLOR = (0, 255, 0) # green

FONT_SIZE = 28

DELAY = 100


def init():
	# initialize pygame surface
	pygame.init()
	pygame.display.set_caption("The Circle of Life")
	surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	return surface


def display(env, agent, prey, predator, surface):
	surface.fill(BACKGROUND_COLOR)

	# draw nodes
	# (x,y) = point on perimeter of circle of life
	# (h,k) = center of circle of life (center of surface)
	h = SCREEN_WIDTH / 2
	k = SCREEN_HEIGHT / 2
	centers = {} # center of each node
	for i in range(N):
		# (x,y) = center of node
		angle = math.pi * 2 / N * (i + 1)
		x = CIRCLE_OF_LIFE_RADIUS * math.cos(angle) + h
		y = CIRCLE_OF_LIFE_RADIUS * math.sin(angle) + k
		centers[i] = (x, y)
		# draw node
		pygame.draw.circle(surface, NODE_COLOR, (x, y), NODE_RADIUS)

	# draw edges
	edges_drawn = set()
	for src in range(N):
		for dest in env.vertices[src].neighbors:
			# draw edge if not already drawn
			if (dest, src) not in edges_drawn:
				# draw arc from source node to destination node
				# (c1[0],c1[1]) = center of source node
				# (c2[0],c2[1]) = center of destination node
				c1 = centers[src]
				c2 = centers[dest]
				# d = distance between centers
				d = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

				# rect = rectangle in which ellipse of arc is centered
				mid_x = (c1[0] + c2[0]) / 2
				mid_y = (c1[1] + c2[1]) / 2
				rect = (mid_x - d / 2, mid_y - d / 2, d, d)

				# a1 = angle to start arc
				# a2 = angle to end arc
				a1 = math.atan2(-(c1[1] - mid_y), c1[0] - mid_x)
				a2 = math.atan2(-(c2[1] - mid_y), c2[0] - mid_x)
				# make sure all edges are drawn inward
				if abs(dest - src) > MAX_STEP:
					temp = a1
					a1 = a2
					a2 = temp

				pygame.draw.arc(surface, EDGE_COLOR, rect, a1, a2)
				edges_drawn.add((src, dest))

	# draw players
	# if multiple players are in same node, priority: predator, agent, prey
	pygame.draw.circle(surface, PREY_COLOR, centers[prey.pos], NODE_RADIUS)
	pygame.draw.circle(surface, AGENT_COLOR, centers[agent.pos], NODE_RADIUS)
	pygame.draw.circle(surface, PREDATOR_COLOR, centers[predator.pos], NODE_RADIUS)

	# show debug info
	if debug:
		# draw numbers on nodes
		font = pygame.font.Font(pygame.font.get_default_font(), 10)
		for i in range(N):
			text_surface = font.render(str(i), True, BACKGROUND_COLOR)
			# center text
			x = centers[i][0] - text_surface.get_rect().width / 2
			y = centers[i][1] - text_surface.get_rect().height / 2
			surface.blit(text_surface, (x, y))

	pygame.display.update()


def run(agent_type, env=None, agent_pos=None, prey_pos=None, predator_pos=None):
	if not env:
		env = main.generate_environment()
	agent = main.spawn_agent(agent_type, env, agent_pos)
	prey = main.spawn_prey(env, prey_pos)
	predator = main.spawn_predator(agent, env, predator_pos)

	surface = init()
	font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)

	step = 0 # after all 3 players have moved
	player_step = 0 # after single player has moved
	state = IN_PROGRESS

	while True:
		# stop if window was closed
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return

		if state == IN_PROGRESS:
			# display
			display(env, agent, prey, predator, surface)
			pygame.time.delay(DELAY)

			# move agent (steps 1, 2, 3)
			if player_step % 3 == 0:
				if agent_type == 1 or agent_type == 2:
					agent.move(env, prey.pos, predator.pos)
				elif agent_type == 3 or agent_type == 4:
					agent.move(env, predator_pos=predator.pos)
				elif agent_type == 5 or agent_type == 6:
					# start by knowing predator position
					agent.move(env, prey.pos, None if step > 0 else predator.pos)
				else:
					# start by knowing predator position
					agent.move(env, predator_pos=None if step > 0 else predator.pos)
			# move prey (step 5)
			elif player_step % 3 == 1:
				prey.move(env)
				# prey belief transition update (step 6)
				if isinstance(agent, main.PreyPartialAgent):
					agent.prey_transition_update()
			# move predator (step 8)
			else:
				predator.move(env, agent.pos)
				# predator belief transition update (step 9)
				if isinstance(agent, main.PredatorPartialAgent):
					agent.predator_transition_update(env)
				step += 1

			# check success/failure
			state = main.game_state(agent, prey, predator, step)
			if state != IN_PROGRESS:
				# display
				display(env, agent, prey, predator, surface)
				pygame.time.delay(DELAY)
				continue

			# prey belief observation update (steps 4, 7)
			if ((player_step % 3 == 0 or player_step % 3 == 1) and
					isinstance(agent, main.PreyPartialAgent)):
				agent.prey_observation_update(agent.pos, False, env)
			# predator belief observation update (steps 4, 10)
			if ((player_step % 3 == 0 or player_step % 3 == 2) and
					isinstance(agent, main.PredatorPartialAgent)):
				agent.predator_observation_update(agent.pos, False, env)

			player_step += 1
		else:
			# game over, show end state
			if state == SUCCESS:
				text = "success"
			elif state == FAILURE:
				text = "failure"
			elif state == TIMEOUT:
				text = "timeout"
			text_surface = font.render(text, True, TEXT_COLOR, BACKGROUND_COLOR)

			# center text
			x = SCREEN_WIDTH / 2 - text_surface.get_rect().width / 2
			y = SCREEN_HEIGHT / 2 - text_surface.get_rect().height / 2
			surface.blit(text_surface, (x, y))

			pygame.display.update()


if __name__ == "__main__":
	# check for correct usage
	if ((len(sys.argv) != 2 and len(sys.argv) != 3) or
			(len(sys.argv) == 3 and sys.argv[1] != "--debug")):
		print("Usage: python3 visualization.py [--debug] agent_type")
		sys.exit()
	# parse command-line arguments
	agent_type = int(sys.argv[1 if len(sys.argv) == 2 else 2])
	global debug
	debug = 1 if len(sys.argv) == 3 else 0

	run(agent_type)
