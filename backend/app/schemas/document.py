"""
Pydantic schemas for Phase 2 Document Ingestion and Processing.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentPageExtract(BaseModel):
    page_number: int
    text: str
    char_count: int
    has_text: bool
    used_ocr: bool = False


class DocumentBase(BaseModel):
    original_filename: str
    file_type: str
    file_size: int
    content_hash: str
    processing_status: str
    page_count: int = 1
    extraction_method: Optional[str] = None


class DocumentUploadResponse(DocumentBase):
    document_id: str
    vendor_id: int
    upload_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentUploadResponse):
    extracted_text: Optional[str] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    vendor_id: int
    total: int
    documents: List[DocumentUploadResponse]


class DocumentProcessResponse(BaseModel):
    document_id: str
    vendor_id: int
    original_filename: str
    file_type: str
    processing_status: str
    page_count: int
    extraction_method: str
    total_characters: int
    pages: List[DocumentPageExtract]
    error_message: Optional[str] = None

