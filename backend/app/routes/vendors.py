"""
Vendor API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.vendor import Vendor
from backend.app.schemas.vendor import VendorCreate, VendorResponse

router = APIRouter(tags=["Vendors"])


@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(vendor_in: VendorCreate, db: Session = Depends(get_db)):
    """
    Create and store a new vendor record.
    Scores are strictly validated between 0.0 and 100.0.
    """
    db_vendor = Vendor(**vendor_in.model_dump())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.get("/vendors", response_model=List[VendorResponse])
def list_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all registered vendors.
    """
    vendors = db.query(Vendor).offset(skip).limit(limit).all()
    return vendors


@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific vendor by vendor_id.
    """
    if vendor_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vendor ID")
    
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor with ID {vendor_id} not found")
    return vendor
