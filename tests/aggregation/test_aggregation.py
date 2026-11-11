"""
Tests for Risk Aggregation Service and Multi-Agent Assessment REST Endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models.vendor import Vendor
from backend.app.models.assessment import Assessment
from backend.app.schemas.agent import AgentFinding
from backend.app.services.aggregation.risk_aggregation import RiskAggregationService

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_aggregation_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


def test_aggregation_formula_correct():
    findings = [
        AgentFinding(
            agent_name="FinancialRiskAgent",
            dimension="Financial",
            score=20.0,
            risk_level="LOW",
            reasoning_summary="",
            confidence=0.8,
            status="ANALYZED",
        ),
        AgentFinding(
            agent_name="CybersecurityRiskAgent",
            dimension="Security",
            score=20.0,
            risk_level="LOW",
            reasoning_summary="",
            confidence=0.8,
            status="ANALYZED",
        ),
        AgentFinding(
            agent_name="ComplianceRiskAgent",
            dimension="Compliance",
            score=20.0,
            risk_level="LOW",
            reasoning_summary="",
            confidence=0.8,
            status="ANALYZED",
        ),
        AgentFinding(
            agent_name="OperationalRiskAgent",
            dimension="Operational",
            score=20.0,
            risk_level="LOW",
            reasoning_summary="",
            confidence=0.8,
            status="ANALYZED",
        ),
        AgentFinding(
            agent_name="ReputationRiskAgent",
            dimension="Reputation",
            score=20.0,
            risk_level="LOW",
            reasoning_summary="",
            confidence=0.8,
            status="ANALYZED",
        ),
    ]

    phase1_score = 40.0
    agg = RiskAggregationService.aggregate(
        phase1_score=phase1_score,
        findings=findings,
        alpha=0.5,
        beta=0.5,
    )
    # phase2_score = 20 * 0.25 + 20 * 0.25 + 20 * 0.20 + 20 * 0.20 + 20 * 0.10 = 20.0
    # final_score = 0.5 * 40.0 + 0.5 * 20.0 = 30.0
    assert agg["phase2_score"] == 20.0
    assert agg["final_score"] == 30.0
    assert agg["risk_level"] == "LOW"


def test_risk_level_mapping():
    assert RiskAggregationService.map_score_to_level(25.0) == "LOW"
    assert RiskAggregationService.map_score_to_level(39.0) == "LOW"
    assert RiskAggregationService.map_score_to_level(40.0) == "MEDIUM"
    assert RiskAggregationService.map_score_to_level(69.0) == "MEDIUM"
    assert RiskAggregationService.map_score_to_level(70.0) == "HIGH"
    assert RiskAggregationService.map_score_to_level(95.0) == "HIGH"


def test_run_ai_assessment_endpoint():
    db = TestingSessionLocal()
    v = Vendor(
        vendor_id=600,
        vendor_name="Tech Global Corp",
        financial_score=35.0,
        security_score=40.0,
        compliance_score=30.0,
        operational_score=35.0,
        reputation_score=25.0,
    )
    db.merge(v)
    db.commit()
    db.close()

    res = client.post(
        "/api/v1/assessments/ai/vendors/600/run",
        json={"question": "Assess overall enterprise security and compliance", "alpha": 0.5, "beta": 0.5}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["vendor_id"] == 600
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "phase1_score" in data
    assert "phase2_score" in data
    assert "final_score" in data
    assert "verification_status" in data
    assert len(data["findings"]) == 5


def test_get_latest_assessment_endpoint():
    db = TestingSessionLocal()
    v = Vendor(
        vendor_id=700,
        vendor_name="Vendor Seven",
        financial_score=50.0,
        security_score=50.0,
        compliance_score=50.0,
        operational_score=50.0,
        reputation_score=50.0,
    )
    db.merge(v)
    db.commit()
    db.close()

    # First check 404 when no assessment has been run
    res_empty = client.get("/api/v1/assessments/ai/vendors/700/latest")
    assert res_empty.status_code == 404

    # Run assessment
    client.post(
        "/api/v1/assessments/ai/vendors/700/run",
        json={"question": "Evaluate risk", "alpha": 0.5, "beta": 0.5}
    )

    # Now latest should return 200
    res_latest = client.get("/api/v1/assessments/ai/vendors/700/latest")
    assert res_latest.status_code == 200
    assert res_latest.json()["vendor_id"] == 700

    # History should return list of length 1
    res_hist = client.get("/api/v1/assessments/ai/vendors/700/history")
    assert res_hist.status_code == 200
    assert len(res_hist.json()) == 1

