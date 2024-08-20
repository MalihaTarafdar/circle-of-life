from .prey_partial_agent import PreyPartialAgent
from .predator_partial_agent import PredatorPartialAgent
from .combined_partial_agent import CombinedPartialAgent
from .combined_partial_defective_agent import CombinedPartialDefectiveAgent


"""
inheritance model

Predator                       <--  EasilyDistractedPredator

Agent                          <--  Agent1, PreyPartialAgent, PredatorPartialAgent
ImprovedAgent                  <--  Agent2, Agent4, Agent6, Agent8, Agent8Defective

PreyPartialAgent               <--  Agent3, Agent4, CombinedPartialAgent,
                                    CombinedPartialDefectiveAgent
PredatorPartialAgent           <--  Agent5, Agent6, CombinedPartialAgent,
                                    CombinedPartialDefectiveAgent
CombinedPartialAgent           <--  Agent7, Agent8
CombinedPartialDefectiveAgent  <--  Agent7Defective, Agent8Defective
"""


# export all agents
__all__ = [
	"base_agent", "base_agent_improved",
	"PreyPartialAgent", "PredatorPartialAgent",
	"CombinedPartialAgent", "CombinedPartialDefectiveAgent",
	"agent1", "agent2",
	"agent3", "agent4",
	"agent5", "agent6",
	"agent7", "agent8",
	"agent7_defective", "agent8_defective"
]
