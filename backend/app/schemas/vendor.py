"""
Vendor Pydantic schemas.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class VendorBase(BaseModel):
    vendor_name: str = Field(..., min_length=1, max_length=255, description="Name of the vendor")
    revenue: float = Field(default=0.0, ge=0.0, description="Annual revenue in USD")
    debt: float = Field(default=0.0, ge=0.0, description="Current debt in USD")
    financial_score: float = Field(..., ge=0.0, le=100.0, description="Financial risk score (0-100)")
    security_score: float = Field(..., ge=0.0, le=100.0, description="Security risk score (0-100)")
    compliance_score: float = Field(..., ge=0.0, le=100.0, description="Compliance risk score (0-100)")
    operational_score: float = Field(..., ge=0.0, le=100.0, description="Operational risk score (0-100)")
    reputation_score: float = Field(..., ge=0.0, le=100.0, description="Reputation risk score (0-100)")


class VendorCreate(VendorBase):
    pass


class VendorResponse(VendorBase):
    vendor_id: int
    created_at: datetime

    class Config:
        from_attributes = True
