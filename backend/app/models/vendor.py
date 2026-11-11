"""
Vendor database model.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_name = Column(String(255), nullable=False, index=True)
    revenue = Column(Float, nullable=False, default=0.0)
    debt = Column(Float, nullable=False, default=0.0)
    financial_score = Column(Float, nullable=False)
    security_score = Column(Float, nullable=False)
    compliance_score = Column(Float, nullable=False)
    operational_score = Column(Float, nullable=False)
    reputation_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assessments = relationship("Assessment", back_populates="vendor", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="vendor", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="vendor", cascade="all, delete-orphan")
    ai_assessments = relationship("AIAssessment", back_populates="vendor", cascade="all, delete-orphan")
