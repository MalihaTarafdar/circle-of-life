# The Circle of Life
This project is a collection of AI models for pursuit-evasion strategy in uncertain and noisy environments. There are 8 different agents that simulate informed decision-making in random environments with varying levels of information access and noise conditions. They use Bayesian networks and Markov chains to predict the positions of moving targets in noisy, uncertain environments in real-time, employing belief propagation to perform exact inference. 

## Usage
To run the game with a visualization, run the following command:
```bash
python3 visualization.py [--debug] agent_type
```
where debug mode (optional) shows the node numbers and agent_type is the number of the agent. The possible values of agent_type are 1-8 for the main agents, -7 for agent 7 with defective drone, and -8 for agent 8 with defective drone.

A script for data collection is included:
```bash
python3 test.py agent_type num_trials
```
where agent_type is the number of the agent with the same possible values as specified above and num trials is the number of trials to collect data over.
