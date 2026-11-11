"""
SQLAlchemy model for Phase 2 Consolidated Multi-Agent AI Assessment.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class AIAssessment(Base):
    __tablename__ = "ai_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    phase1_score = Column(Float, nullable=False)
    phase2_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    risk_level = Column(String(32), nullable=False)

    financial_score = Column(Float, nullable=False)
    cybersecurity_score = Column(Float, nullable=False)
    compliance_score = Column(Float, nullable=False)
    operational_score = Column(Float, nullable=False)
    reputation_score = Column(Float, nullable=False)

    verification_status = Column(String(32), nullable=False)
    overall_confidence = Column(Float, nullable=False)
    evidence_count = Column(Integer, default=0, nullable=False)

    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    assessment_json = Column(Text, nullable=True)

    vendor = relationship("Vendor", back_populates="ai_assessments")

