"""
Document database model for Phase 2 Document Ingestion.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String(64), primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filepath = Column(String(512), nullable=False)
    file_type = Column(String(32), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_status = Column(String(32), default="PENDING", nullable=False)
    page_count = Column(Integer, default=1, nullable=False)
    extraction_method = Column(String(64), nullable=True)
    extracted_text = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    vendor = relationship("Vendor", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

