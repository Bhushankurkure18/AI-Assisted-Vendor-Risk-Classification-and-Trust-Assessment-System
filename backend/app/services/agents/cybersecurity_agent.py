"""
Cybersecurity Risk Agent.
"""
from backend.app.services.agents.base_agent import BaseRiskAgent


class CybersecurityRiskAgent(BaseRiskAgent):
    agent_name = "CybersecurityRiskAgent"
    dimension = "Security"
    keywords = [
        "security", "breach", "hack", "vulnerability", "encryption",
        "iso27001", "soc2", "firewall", "incident", "cyber",
        "malware", "ransomware", "data protection", "gdpr", "nist"
    ]

