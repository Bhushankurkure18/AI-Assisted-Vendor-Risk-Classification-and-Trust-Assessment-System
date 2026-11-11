"""
Pydantic validation schemas for Document Chunking.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ChunkMetadata(BaseModel):
    chunk_id: str
    document_id: str
    vendor_id: int
    filename: str
    page_number: int
    section: Optional[str] = None
    chunk_index: int
    token_count: int
    content_hash: str


class ChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    vendor_id: int
    original_filename: str
    page_number: int
    section: Optional[str] = None
    chunk_index: int
    token_count: int
    content_hash: str
    chunk_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChunkListResponse(BaseModel):
    document_id: Optional[str] = None
    vendor_id: int
    total_chunks: int
    total_tokens: int
    chunks: List[ChunkResponse]


class ChunkProcessResponse(BaseModel):
    document_id: str
    vendor_id: int
    original_filename: str
    total_chunks: int
    total_tokens: int
    chunks: List[ChunkResponse]

