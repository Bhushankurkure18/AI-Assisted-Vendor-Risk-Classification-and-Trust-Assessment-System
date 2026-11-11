"""
Tests for LangGraph Multi-Agent Workflow and Verification Agent.
"""
import pytest
from backend.app.schemas.rag import EvidenceItem
from backend.app.schemas.agent import AgentFinding
from backend.app.services.agents.verification_agent import VerificationAgent
from backend.app.services.vector_store.chroma_service import ChromaService
from backend.app.services.rag.retrieval_service import RetrievalService
from backend.app.services.orchestration.workflow import RiskWorkflow


@pytest.fixture
def workflow_with_temp_chroma(tmp_path):
    chroma_dir = str(tmp_path / "workflow_chroma")
    chroma_svc = ChromaService(persist_directory=chroma_dir)
    retrieval_svc = RetrievalService(chroma_service=chroma_svc)
    workflow = RiskWorkflow(retrieval_service=retrieval_svc)
    return chroma_svc, workflow


def test_verification_agent_verified_status():
    evidence = [
        EvidenceItem(
            chunk_id="chunk_1",
            document_id="doc_1",
            vendor_id=1,
            filename="report.pdf",
            quoted_text="Financial profit was high.",
        )
    ]
    finding = AgentFinding(
        agent_name="FinancialRiskAgent",
        dimension="Financial",
        score=20.0,
        risk_level="LOW",
        evidence_references=evidence,
        missing_information=[],
        reasoning_summary="Verified from report.",
        confidence=0.9,
        status="ANALYZED",
    )
    result = VerificationAgent.verify(findings=[finding], all_evidence=evidence)
    assert result.status == "VERIFIED"
    assert result.verified_count == 1
    assert result.overall_confidence == 0.9


def test_verification_agent_insufficient_evidence():
    result = VerificationAgent.verify(findings=[], all_evidence=[])
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert result.verified_count == 0


def test_workflow_runs_end_to_end(workflow_with_temp_chroma):
    chroma_svc, workflow = workflow_with_temp_chroma
    chroma_svc.add_chunks(
        vendor_id=42,
        chunks=[{
            "chunk_id": "c42",
            "document_id": "d42",
            "vendor_id": 42,
            "filename": "vendor_data.txt",
            "page_number": 1,
            "section": "Overview",
            "text": "Acme Tech maintains strong financial cash flow, rigorous cybersecurity SOC2 certification, ISO compliance, robust supply chain disaster recovery, and high customer review satisfaction.",
        }]
    )

    result = workflow.run(vendor_id=42, question="Assess vendor risk")
    assert result is not None
    assert len(result["evidence_chunks"]) > 0
    assert result["verification_result"] is not None
    assert result["verification_result"].verified_count >= 1


def test_workflow_returns_all_five_findings(workflow_with_temp_chroma):
    _, workflow = workflow_with_temp_chroma
    result = workflow.run(vendor_id=99, question="Empty test")
    assert "financial_finding" in result
    assert "cybersecurity_finding" in result
    assert "compliance_finding" in result
    assert "operational_finding" in result
    assert "reputation_finding" in result
    assert result["financial_finding"].status == "INSUFFICIENT_EVIDENCE"

