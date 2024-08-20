# script for data collection

import csv
import datetime
import numpy as np
import os
import statistics as st
import sys
import main
from config import *

"""
data to collect for each agent

report average and std. dev. of each metric over NUM_RUNS runs per trial
1 trial = new graph
1 run = new players on a given graph

success rate = how often agent catches prey

failure rate 1 = how often predator catches agent
failure rate 2 = how often simulation hangs (step limit reached)

correctness = how often agent knows exactly where prey/predator is when that info is partial
= # moves pos with highest probability of prey/predator (no ties) == prey/predator pos
"""


def test(agent_type, num_trials):
	# data = success, failure, timeout, total, correct prey, correct predator, total moves
	data = np.zeros((num_trials, 7))

	for i in range(num_trials):
		env = main.generate_environment()

		for j in range(NUM_RUNS):
			result, correctness = main.run(agent_type, env)

			if result == SUCCESS:
				data[i][0] += 1
			elif result == FAILURE:
				data[i][1] += 1
			elif result == TIMEOUT:
				data[i][2] += 1
			data[i][3] += 1

			for k in range(len(correctness)):
				data[i][4 + k] += correctness[k]

	return data


# calculate averages and standard deviations for given data
def calculate_stats(data):
	stats = np.empty((2, 7))

	# line 1 = averages
	for j in range(np.shape(data)[1]):
		stats[0][j] = st.mean(data[:, j])

	# line 2 = standard deviations
	for j in range(np.shape(data)[1]):
		stats[1][j] = st.pstdev(data[:, j])

	return stats


def output_to_csv(agent_type, data, stats):
	header = ["Success", "Fail", "Hung", "Total", "Prey", "Predator", "Total Moves"]

	# create files
	dt = (str(datetime.datetime.now()).replace(' ', '_').replace(':', '-')
			.replace('.', '-'))
	data_path = "./data/trials/agent%s_%s.csv" % (agent_type, dt)
	stats_path = "./data/stats/agent%s_%s.csv" % (agent_type, dt)
	os.makedirs(os.path.dirname(data_path), exist_ok=True)
	os.makedirs(os.path.dirname(stats_path), exist_ok=True)

	# write data to csv
	with open(data_path, 'w', newline='') as data_csv:
		writer = csv.writer(data_csv, delimiter=',')
		writer.writerow(header)
		for line in data:
			writer.writerow(line)

	# write stats to csv
	with open(stats_path, 'w', newline='') as stats_csv:
		writer = csv.writer(stats_csv, delimiter=',')
		writer.writerow(header)
		for line in stats:
			writer.writerow(line)


if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 3:
		print("Usage: python3 test.py agent_type num_trials")
		sys.exit()
	agent_type = int(sys.argv[1])
	num_trials = int(sys.argv[2])

	data = test(agent_type, num_trials)
	stats = calculate_stats(data)
	output_to_csv(agent_type, data, stats)
