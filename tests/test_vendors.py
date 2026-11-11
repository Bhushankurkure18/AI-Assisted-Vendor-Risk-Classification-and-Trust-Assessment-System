"""
Integration tests for Vendor API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_vendor_api.db"

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


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Vendor Risk Assessment API is running"}


def test_create_vendor_valid():
    payload = {
        "vendor_name": "Acme Cloud Services",
        "revenue": 5000000.0,
        "debt": 1000000.0,
        "financial_score": 35.0,
        "security_score": 25.0,
        "compliance_score": 30.0,
        "operational_score": 40.0,
        "reputation_score": 20.0
    }
    response = client.post("/vendors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["vendor_id"] > 0
    assert data["vendor_name"] == "Acme Cloud Services"
    assert data["financial_score"] == 35.0


def test_create_vendor_invalid_score():
    # Negative score
    payload = {
        "vendor_name": "Faulty Vendor",
        "revenue": 100000.0,
        "debt": 20000.0,
        "financial_score": -10.0,  # Invalid
        "security_score": 50.0,
        "compliance_score": 50.0,
        "operational_score": 50.0,
        "reputation_score": 50.0
    }
    response = client.post("/vendors", json=payload)
    assert response.status_code == 422

    # Score > 100
    payload["financial_score"] = 150.0
    response = client.post("/vendors", json=payload)
    assert response.status_code == 422


def test_get_vendor():
    payload = {
        "vendor_name": "DataTech Solutions",
        "revenue": 2000000.0,
        "debt": 500000.0,
        "financial_score": 45.0,
        "security_score": 60.0,
        "compliance_score": 50.0,
        "operational_score": 55.0,
        "reputation_score": 40.0
    }
    create_res = client.post("/vendors", json=payload)
    assert create_res.status_code == 201
    vendor_id = create_res.json()["vendor_id"]

    get_res = client.get(f"/vendors/{vendor_id}")
    assert get_res.status_code == 200
    assert get_res.json()["vendor_name"] == "DataTech Solutions"


def test_get_nonexistent_vendor():
    response = client.get("/vendors/99999")
    assert response.status_code == 404
