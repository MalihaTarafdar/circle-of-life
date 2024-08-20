# module for global variables

# do not modify (will break program)
N = 50 # number of nodes
ALLOWED_ERROR = 0.000001 # account for floating point error

# can modify
MAX_STEP = 5 # max distance of an edge
STEP_LIMIT = 5000 # number of steps before timeout
DISTRACTED_PROB = 0.4 # probability easily distracted predator is distracted
DRONE_DEFECTIVE_PROB = 0.1 # probability that drone reports false negative
NUM_RUNS = 30 # number of runs per trial

# game states
FAILURE = 0
SUCCESS = 1
TIMEOUT = 2
IN_PROGRESS = -1
