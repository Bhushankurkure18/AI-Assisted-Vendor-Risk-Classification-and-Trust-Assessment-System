"""
Financial Risk Agent.
"""
from backend.app.services.agents.base_agent import BaseRiskAgent


class FinancialRiskAgent(BaseRiskAgent):
    agent_name = "FinancialRiskAgent"
    dimension = "Financial"
    keywords = [
        "revenue", "profit", "loss", "debt", "credit", "financial",
        "audit", "cash", "liquidity", "solvency", "bankruptcy",
        "rating", "investment", "balance sheet", "ebitda"
    ]

