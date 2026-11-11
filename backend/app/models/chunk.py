"""
DocumentChunk database model for Phase 2 Milestone 2.
Maintains canonical document chunk metadata and text in PostgreSQL / SQLite.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    page_number = Column(Integer, default=1, nullable=False)
    section = Column(String(255), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="chunks")
    vendor = relationship("Vendor", back_populates="chunks")

