"""
Tests for Specialized Risk Dimension Agents.
"""
from backend.app.schemas.rag import EvidenceItem
from backend.app.schemas.agent import AgentFinding
from backend.app.services.agents.financial_agent import FinancialRiskAgent
from backend.app.services.agents.cybersecurity_agent import CybersecurityRiskAgent
from backend.app.services.agents.compliance_agent import ComplianceRiskAgent
from backend.app.services.agents.operational_agent import OperationalRiskAgent
from backend.app.services.agents.reputation_agent import ReputationRiskAgent


def test_financial_agent_with_evidence():
    evidence = [
        EvidenceItem(
            chunk_id="f1",
            document_id="d1",
            vendor_id=1,
            filename="financials.pdf",
            page_number=1,
            section="Balance Sheet",
            chunk_index=0,
            quoted_text="Company reported solid revenue growth, healthy cash liquidity, and positive EBITDA.",
        )
    ]
    finding = FinancialRiskAgent.analyze(vendor_id=1, evidence_chunks=evidence)
    assert isinstance(finding, AgentFinding)
    assert finding.dimension == "Financial"
    assert finding.status == "ANALYZED"
    assert finding.risk_level in ["LOW", "MEDIUM", "HIGH"]
    assert len(finding.evidence_references) > 0


def test_cybersecurity_agent_insufficient_evidence():
    finding = CybersecurityRiskAgent.analyze(vendor_id=2, evidence_chunks=[])
    assert finding.status == "INSUFFICIENT_EVIDENCE"
    assert finding.confidence == 0.0
    assert len(finding.missing_information) > 0


def test_compliance_agent_returns_finding():
    evidence = [
        EvidenceItem(
            chunk_id="c1",
            document_id="d2",
            vendor_id=3,
            filename="compliance_report.docx",
            page_number=2,
            section="ISO Standards",
            chunk_index=1,
            quoted_text="The organization maintains full compliance with ISO 9001 and GDPR regulations.",
        )
    ]
    finding = ComplianceRiskAgent.analyze(vendor_id=3, evidence_chunks=evidence)
    assert finding.dimension == "Compliance"
    assert finding.status == "ANALYZED"
    assert "ISO" in finding.evidence_references[0].quoted_text or "GDPR" in finding.evidence_references[0].quoted_text


def test_operational_agent_risk_level_mapping():
    # Negative disruption detected -> higher risk
    negative_evidence = [
        EvidenceItem(
            chunk_id="o1",
            document_id="d3",
            vendor_id=4,
            filename="ops.txt",
            page_number=1,
            section="Incident Log",
            chunk_index=0,
            quoted_text="Severe supply chain disruption and critical server downtime occurred last quarter.",
        )
    ]
    finding = OperationalRiskAgent.analyze(vendor_id=4, evidence_chunks=negative_evidence)
    assert finding.risk_level in ["MEDIUM", "HIGH"]
    assert finding.score >= 40.0


def test_reputation_agent_with_evidence():
    evidence = [
        EvidenceItem(
            chunk_id="r1",
            document_id="d4",
            vendor_id=5,
            filename="reviews.csv",
            page_number=1,
            section="Customer Feedback",
            chunk_index=0,
            quoted_text="Excellent customer satisfaction score, top partner rating, and high trust reviews.",
        )
    ]
    finding = ReputationRiskAgent.analyze(vendor_id=5, evidence_chunks=evidence)
    assert finding.dimension == "Reputation"
    assert finding.status == "ANALYZED"
    assert finding.confidence > 0.0


def test_all_agents_return_agent_finding_schema():
    agents = [
        FinancialRiskAgent,
        CybersecurityRiskAgent,
        ComplianceRiskAgent,
        OperationalRiskAgent,
        ReputationRiskAgent,
    ]
    for agent in agents:
        res = agent.analyze(vendor_id=10, evidence_chunks=[])
        assert isinstance(res, AgentFinding)
        assert res.agent_name == agent.agent_name
        assert 0.0 <= res.score <= 100.0

