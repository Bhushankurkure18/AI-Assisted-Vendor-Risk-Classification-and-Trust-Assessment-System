"""
Regulatory Compliance Risk Agent.
"""
from backend.app.services.agents.base_agent import BaseRiskAgent


class ComplianceRiskAgent(BaseRiskAgent):
    agent_name = "ComplianceRiskAgent"
    dimension = "Compliance"
    keywords = [
        "compliance", "regulation", "iso", "certified", "audit",
        "gdpr", "hipaa", "pci", "sox", "policy", "procedure",
        "violation", "penalty", "legal", "standard", "governance"
    ]

