"""
Unit tests for Rule-Based Risk Engine.
"""
import pytest
from backend.app.services.risk_engine import RiskEngine


def test_risk_score_calculation():
    # Financial 25%, Security 25%, Compliance 20%, Operational 20%, Reputation 10%
    category_scores = {
        "financial": 50.0,
        "security": 50.0,
        "compliance": 50.0,
        "operational": 50.0,
        "reputation": 50.0
    }
    score = RiskEngine.calculate_weighted_score(category_scores)
    assert score == 50.0


def test_low_risk_classification():
    # Score <= 39.0
    category_scores = {
        "financial": 20.0,
        "security": 25.0,
        "compliance": 30.0,
        "operational": 20.0,
        "reputation": 15.0
    }
    score = RiskEngine.calculate_weighted_score(category_scores)
    level = RiskEngine.classify_level(score)
    assert score <= 39.0
    assert level == "LOW"


def test_medium_risk_classification():
    # 40.0 <= Score <= 69.0
    category_scores = {
        "financial": 55.0,
        "security": 60.0,
        "compliance": 50.0,
        "operational": 45.0,
        "reputation": 40.0
    }
    score = RiskEngine.calculate_weighted_score(category_scores)
    level = RiskEngine.classify_level(score)
    assert 40.0 <= score <= 69.0
    assert level == "MEDIUM"


def test_high_risk_classification():
    # Score >= 70.0
    category_scores = {
        "financial": 85.0,
        "security": 90.0,
        "compliance": 75.0,
        "operational": 80.0,
        "reputation": 70.0
    }
    score = RiskEngine.calculate_weighted_score(category_scores)
    level = RiskEngine.classify_level(score)
    assert score >= 70.0
    assert level == "HIGH"


def test_full_assess_with_explanations():
    category_scores = {
        "financial": 85.0,
        "security": 90.0,
        "compliance": 30.0,
        "operational": 20.0,
        "reputation": 20.0
    }
    result = RiskEngine.assess(category_scores)
    assert "score" in result
    assert "risk_level" in result
    assert "key_risk_factors" in result
    assert len(result["key_risk_factors"]) > 0
    assert any("Security" in f for f in result["key_risk_factors"])
