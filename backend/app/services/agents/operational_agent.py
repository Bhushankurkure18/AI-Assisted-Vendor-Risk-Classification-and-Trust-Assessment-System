"""
Operational Risk Agent.
"""
from backend.app.services.agents.base_agent import BaseRiskAgent


class OperationalRiskAgent(BaseRiskAgent):
    agent_name = "OperationalRiskAgent"
    dimension = "Operational"
    keywords = [
        "operational", "delivery", "supply chain", "disruption",
        "downtime", "sla", "capacity", "infrastructure", "process",
        "quality", "performance", "continuity", "recovery", "incident"
    ]

