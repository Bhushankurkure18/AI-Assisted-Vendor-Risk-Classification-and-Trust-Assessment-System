"""
LangGraph Multi-Agent Workflow connecting RAG retrieval, 5 Risk Agents, and Verification.
"""
import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from backend.app.schemas.orchestration import WorkflowState
from backend.app.services.rag.retrieval_service import RetrievalService
from backend.app.services.agents.financial_agent import FinancialRiskAgent
from backend.app.services.agents.cybersecurity_agent import CybersecurityRiskAgent
from backend.app.services.agents.compliance_agent import ComplianceRiskAgent
from backend.app.services.agents.operational_agent import OperationalRiskAgent
from backend.app.services.agents.reputation_agent import ReputationRiskAgent
from backend.app.services.agents.verification_agent import VerificationAgent

logger = logging.getLogger(__name__)


class RiskWorkflow:
    """
    Orchestrates the multi-agent vendor risk assessment pipeline via LangGraph.
    """

    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.graph = self._build_graph()

    def _retrieve_node(self, state: WorkflowState) -> Dict[str, Any]:
        vendor_id = state.get("vendor_id", 0)
        query = state.get("question", "comprehensive vendor risk evaluation")
        evidence = self.retrieval_service.retrieve_evidence(vendor_id=vendor_id, query=query, top_k=10)
        return {"evidence_chunks": evidence}

    def _financial_node(self, state: WorkflowState) -> Dict[str, Any]:
        vendor_id = state.get("vendor_id", 0)
        chunks = state.get("evidence_chunks", [])
        finding = FinancialRiskAgent.analyze(vendor_id=vendor_id, evidence_chunks=chunks)
        return {"financial_finding": finding}

    def _cybersecurity_node(self, state: WorkflowState) -> Dict[str, Any]:
        vendor_id = state.get("vendor_id", 0)
        chunks = state.get("evidence_chunks", [])
        finding = CybersecurityRiskAgent.analyze(vendor_id=vendor_id, evidence_chunks=chunks)
        return {"cybersecurity_finding": finding}

    def _compliance_node(self, state: WorkflowState) -> Dict[str, Any]:
        vendor_id = state.get("vendor_id", 0)
        chunks = state.get("evidence_chunks", [])
        finding = ComplianceRiskAgent.analyze(vendor_id=vendor_id, evidence_chunks=chunks)
        return {"compliance_finding": finding}

    def _operational_node(self, state: WorkflowState) -> Dict[str, Any]:
        vendor_id = state.get("vendor_id", 0)
        chunks = state.get("evidence_chunks", [])
        finding = OperationalRiskAgent.analyze(vendor_id=vendor_id, evidence_chunks=chunks)
        return {"operational_finding": finding}

    def _reputation_node(self, state: WorkflowState) -> Dict[str, Any]:
        vendor_id = state.get("vendor_id", 0)
        chunks = state.get("evidence_chunks", [])
        finding = ReputationRiskAgent.analyze(vendor_id=vendor_id, evidence_chunks=chunks)
        return {"reputation_finding": finding}

    def _verification_node(self, state: WorkflowState) -> Dict[str, Any]:
        findings = []
        for key in [
            "financial_finding",
            "cybersecurity_finding",
            "compliance_finding",
            "operational_finding",
            "reputation_finding",
        ]:
            val = state.get(key)
            if val is not None:
                findings.append(val)

        all_evidence = state.get("evidence_chunks", [])
        verification = VerificationAgent.verify(findings=findings, all_evidence=all_evidence)
        return {"verification_result": verification}

    def _build_graph(self):
        builder = StateGraph(WorkflowState)

        # Add Nodes
        builder.add_node("retrieve", self._retrieve_node)
        builder.add_node("financial", self._financial_node)
        builder.add_node("cybersecurity", self._cybersecurity_node)
        builder.add_node("compliance", self._compliance_node)
        builder.add_node("operational", self._operational_node)
        builder.add_node("reputation", self._reputation_node)
        builder.add_node("verify", self._verification_node)

        # Connect Edges:
        # retrieve -> financial -> cybersecurity -> compliance -> operational -> reputation -> verify -> END
        builder.set_entry_point("retrieve")
        builder.add_edge("retrieve", "financial")
        builder.add_edge("financial", "cybersecurity")
        builder.add_edge("cybersecurity", "compliance")
        builder.add_edge("compliance", "operational")
        builder.add_edge("operational", "reputation")
        builder.add_edge("reputation", "verify")
        builder.add_edge("verify", END)

        return builder.compile()

    def run(self, vendor_id: int, question: str = "Provide comprehensive vendor risk assessment") -> WorkflowState:
        """
        Executes compiled LangGraph workflow end-to-end.
        """
        initial_state: WorkflowState = {
            "vendor_id": vendor_id,
            "question": question,
            "evidence_chunks": [],
            "errors": [],
        }
        final_state = self.graph.invoke(initial_state)
        return final_state

