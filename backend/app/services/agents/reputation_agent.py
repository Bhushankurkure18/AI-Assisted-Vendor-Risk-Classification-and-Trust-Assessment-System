"""
Reputation Risk Agent.
"""
from backend.app.services.agents.base_agent import BaseRiskAgent


class ReputationRiskAgent(BaseRiskAgent):
    agent_name = "ReputationRiskAgent"
    dimension = "Reputation"
    keywords = [
        "reputation", "review", "complaint", "rating", "award",
        "recognition", "news", "media", "trust", "partner",
        "customer", "satisfaction", "nps", "scandal", "public relations"
    ]

