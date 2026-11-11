"""
Integration tests for Assessment API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_assessment_api.db"

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


def test_assess_vendor_endpoint():
    # 1. Create a vendor
    payload = {
        "vendor_name": "SecureCorp Ltd",
        "revenue": 10000000.0,
        "debt": 1500000.0,
        "financial_score": 75.0,
        "security_score": 80.0,
        "compliance_score": 70.0,
        "operational_score": 65.0,
        "reputation_score": 60.0
    }
    create_res = client.post("/vendors", json=payload)
    assert create_res.status_code == 201
    vendor_id = create_res.json()["vendor_id"]

    # 2. Run assessment
    assess_res = client.post(f"/assess/{vendor_id}")
    assert assess_res.status_code == 200
    data = assess_res.json()

    assert data["vendor"]["id"] == vendor_id
    assert data["vendor"]["name"] == "SecureCorp Ltd"
    assert "rule_based_assessment" in data
    assert data["rule_based_assessment"]["score"] > 70.0
    assert data["rule_based_assessment"]["risk_level"] == "HIGH"
    assert "ml_assessment" in data
    assert "explanation" in data
    assert len(data["explanation"]) > 0

    # 3. Retrieve assessment history
    history_res = client.get(f"/assessments/{vendor_id}")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert history[0]["vendor_id"] == vendor_id


def test_assess_nonexistent_vendor():
    response = client.post("/assess/99999")
    assert response.status_code == 404


def test_assess_invalid_id():
    response = client.post("/assess/0")
    assert response.status_code == 400
