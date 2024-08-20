# a module for graph utilities

import heapq as hq
from config import *


class Node:
	def __init__(self, index):
		self.index = index
		self.neighbors = []
		self.has_agent = False
		self.has_prey = False
		self.has_predator = False

	def add_neighbor(self, index):
		self.neighbors.append(index)


# undirected graph
class Graph:
	# vertices = list of nodes
	def __init__(self, n):
		self.vertices = [Node(i) for i in range(n)]

	def add_edge(self, s, d):
		self.vertices[s].add_neighbor(d)
		self.vertices[d].add_neighbor(s)


# uses UFCS
def shortest_dist(s, d, graph, restricted_set=set()):
	fringe = [] # priority queue with priority g(n)
	closed_set = set()

	if s not in restricted_set:
		fringe.append((0, s))
		closed_set.add(s)

	while fringe:
		g, cur = hq.heappop(fringe)
		if cur == d: # destination found
			return g
		for n in graph.vertices[cur].neighbors:
			if n not in restricted_set and n not in closed_set:
					hq.heappush(fringe, (g + 1, n))
					closed_set.add(n)

	# N / 2 is the max distance between any 2 nodes
	return N / 2 + 1
