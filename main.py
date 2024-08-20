import numpy as np
import random
from agents import *
from config import *
from easily_distracted_predator import EasilyDistractedPredator
from graph_utils import Graph
from predator import Predator
from prey import Prey

"""
order of steps

1. survey
2. prey/predator belief observation update (based on surveyed node)
3. move agent
4. prey/predator belief observation update (based on agent node)
5. move prey
6. prey belief transition update
7. prey belief observation update (based on agent node)
8. move predator
9. predator belief transition update
10. predator belief observation update (based on agent node)
"""


def generate_environment():
	graph = Graph(N)

	# connect graph in a circle
	for i in range(N):
		graph.add_edge(i, i + 1 if i != N - 1 else 0)

	# add random edges as specified to increase connectivity
	# pick random node with degree < MAX_DEG
	# add edge within MAX_STEP steps forward/backward
	MAX_DEG = 3
	for src in range(N):
		if len(graph.vertices[src].neighbors) < MAX_DEG: # degree < MAX_DEG
			step = random.randint(2, MAX_STEP)
			f = (src + step) % N # index forward
			b = (src - step) % N # index backward

			# if node with degree < MAX_DEG exists forward and backward
			if (len(graph.vertices[f].neighbors) < MAX_DEG and
					len(graph.vertices[b].neighbors) < MAX_DEG):
				# pick forward/backward node with equal chance
				r = random.randint(0, 1)
				dest = f if r else b
			# if node with degree < MAX_DEG exists forward
			elif len(graph.vertices[f].neighbors) < MAX_DEG:
				dest = f
			# if node with degree < MAX_DEG exists backward
			elif len(graph.vertices[b].neighbors) < MAX_DEG:
				dest = b
			else: # no such node exists
				continue

			graph.add_edge(src, dest)

	return graph


def spawn_agent(agent_type, env, pos=None):
	if agent_type == 1:
		return agent1.Agent1(env, pos)
	if agent_type == 2:
		return agent2.Agent2(env, pos)
	if agent_type == 3:
		return agent3.Agent3(env, pos)
	if agent_type == 4:
		return agent4.Agent4(env, pos)
	if agent_type == 5:
		return agent5.Agent5(env, pos)
	if agent_type == 6:
		return agent6.Agent6(env, pos)
	if agent_type == 7:
		return agent7.Agent7(env, pos)
	if agent_type == 8:
		return agent8.Agent8(env, pos)
	if agent_type == -7:
		return agent7_defective.Agent7Defective(env, pos)
	if agent_type == -8:
		return agent8_defective.Agent8Defective(env, pos)


def spawn_prey(env, pos=None):
	return Prey(env, pos)


def spawn_predator(agent, env, pos=None):
	# agents with partial predator information use easily distracted predator
	if isinstance(agent, PredatorPartialAgent):
		return EasilyDistractedPredator(env, pos)
	return Predator(env, pos)


def game_state(agent, prey, predator, step_count):
	if agent.pos == prey.pos: # success
		return SUCCESS
	if agent.pos == predator.pos: # failure
		return FAILURE
	if step_count >= STEP_LIMIT: # timeout
		return TIMEOUT
	return IN_PROGRESS


def run(agent_type, env=None, agent_pos=None, prey_pos=None, predator_pos=None):
	if not env:
		env = generate_environment()
	agent = spawn_agent(agent_type, env, agent_pos)
	prey = spawn_prey(env, prey_pos)
	predator = spawn_predator(agent, env, predator_pos)

	step = 0 # after all 3 players have moved
	player_step = 0 # after single player has moved
	correctness = [0] * 3 # correct prey, correct predator, total moves
	
	while True:
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
			# calculate correctness for prey
			if isinstance(agent, PreyPartialAgent):
				max_prob = max(agent.prey_beliefs)
				guess_prey_pos = np.where(agent.prey_beliefs == max_prob)[0]
				if len(guess_prey_pos) == 1 and guess_prey_pos == prey.pos:
					correctness[0] += 1
			# calculate correctness for predator
			if isinstance(agent, PredatorPartialAgent):
				max_prob = max(agent.predator_beliefs)
				guess_predator_pos = np.where(agent.predator_beliefs == max_prob)[0]
				if len(guess_predator_pos) == 1 and guess_predator_pos == predator.pos:
					correctness[1] += 1
			correctness[2] += 1
		# move prey (step 5)
		elif player_step % 3 == 1:
			prey.move(env)
			# prey belief transition update (step 6)
			if isinstance(agent, PreyPartialAgent):
				agent.prey_transition_update()
		# move predator (step 8)
		else:
			predator.move(env, agent.pos)
			# predator belief transition update (step 9)
			if isinstance(agent, PredatorPartialAgent):
				agent.predator_transition_update(env)
			step += 1
		player_step += 1

		# check success/failure
		state = game_state(agent, prey, predator, step)
		if state != IN_PROGRESS:
			return state, correctness

		# prey belief observation update (steps 4, 7)
		if ((player_step % 3 == 0 or player_step % 3 == 1) and
				isinstance(agent, PreyPartialAgent)):
			agent.prey_observation_update(agent.pos, False, env)
		# predator belief observation update (steps 4, 10)
		if ((player_step % 3 == 0 or player_step % 3 == 2) and
				isinstance(agent, PredatorPartialAgent)):
			agent.predator_observation_update(agent.pos, False, env)
