"""
Document Ingestion, Processing & Chunking REST Endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.models.vendor import Vendor
from backend.app.schemas.document import (
    DocumentUploadResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentProcessResponse,
)
from backend.app.schemas.chunk import (
    ChunkResponse,
    ChunkListResponse,
    ChunkProcessResponse,
)
from backend.app.services.ingestion.document_processor import DocumentProcessor
from backend.app.services.chunking.chunking_service import ChunkingService

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Phase 2 - Document Ingestion & Chunking"],
)


@router.post(
    "/upload/{vendor_id}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload vendor document (PDF, DOCX, TXT, CSV)",
)
async def upload_document(
    vendor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Validates, stores, and ingests an unstructured or tabular vendor document.
    Automatically initiates content extraction and registers metadata in PostgreSQL.
    """
    try:
        content = await file.read()
        doc = DocumentProcessor.ingest_document(
            db=db,
            vendor_id=vendor_id,
            filename=file.filename or "uploaded_file",
            content=content,
            auto_process=True
        )
        return doc
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get(
    "/vendor/{vendor_id}",
    response_model=DocumentListResponse,
    summary="List all uploaded documents for a vendor",
)
def list_vendor_documents(vendor_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all ingested documents and their extraction status for a given vendor.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor {vendor_id} not found.")

    docs = db.query(Document).filter(Document.vendor_id == vendor_id).order_by(Document.upload_timestamp.desc()).all()
    return DocumentListResponse(
        vendor_id=vendor_id,
        total=len(docs),
        documents=docs
    )


@router.get(
    "/vendor/{vendor_id}/chunks",
    response_model=ChunkListResponse,
    summary="List all document chunks belonging to a vendor",
)
def list_vendor_chunks(vendor_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all canonical chunks across all documents belonging to a vendor.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor {vendor_id} not found.")

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.vendor_id == vendor_id
    ).order_by(DocumentChunk.created_at.desc(), DocumentChunk.chunk_index.asc()).all()

    total_tokens = sum(c.token_count for c in chunks)
    return ChunkListResponse(
        document_id=None,
        vendor_id=vendor_id,
        total_chunks=len(chunks),
        total_tokens=total_tokens,
        chunks=chunks,
    )


@router.get(
    "/{vendor_id}/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document details and extracted content with vendor ownership verification",
)
def get_document_detail(vendor_id: int, document_id: str, db: Session = Depends(get_db)):
    """
    Retrieves detailed metadata and extracted text for an ingested document,
    strictly verifying vendor ownership boundaries.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor {vendor_id} not found.")

    doc = db.query(Document).filter(
        Document.document_id == document_id,
        Document.vendor_id == vendor_id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found for vendor {vendor_id}."
        )
    return doc


@router.post(
    "/{vendor_id}/{document_id}/process",
    response_model=DocumentProcessResponse,
    summary="Trigger or re-trigger document text extraction with vendor verification",
)
def process_document_for_vendor(vendor_id: int, document_id: str, db: Session = Depends(get_db)):
    """
    Triggers text extraction and OCR fallback processing for a stored document
    after verifying vendor ownership boundaries.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor {vendor_id} not found.")

    doc = db.query(Document).filter(
        Document.document_id == document_id,
        Document.vendor_id == vendor_id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found for vendor {vendor_id}."
        )

    try:
        result = DocumentProcessor.process_document(db, document_id)
        return result
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/{vendor_id}/{document_id}/chunk",
    response_model=ChunkProcessResponse,
    summary="Chunk extracted document into canonical token-bounded chunks",
)
def chunk_document(vendor_id: int, document_id: str, db: Session = Depends(get_db)):
    """
    Cleans and segments document text into token-bounded, sentence-preserving chunks
    and persists them to PostgreSQL / SQLite.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor {vendor_id} not found.")

    try:
        db_chunks = ChunkingService.chunk_and_persist(db=db, document_id=document_id, vendor_id=vendor_id)
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        total_tokens = sum(c.token_count for c in db_chunks)

        return ChunkProcessResponse(
            document_id=document_id,
            vendor_id=vendor_id,
            original_filename=doc.original_filename if doc else "unknown",
            total_chunks=len(db_chunks),
            total_tokens=total_tokens,
            chunks=db_chunks,
        )
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{vendor_id}/{document_id}/chunks",
    response_model=ChunkListResponse,
    summary="List all chunks for a document",
)
def list_document_chunks(vendor_id: int, document_id: str, db: Session = Depends(get_db)):
    """
    Retrieves canonical chunks for a specific document with vendor verification.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor {vendor_id} not found.")

    doc = db.query(Document).filter(
        Document.document_id == document_id,
        Document.vendor_id == vendor_id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found for vendor {vendor_id}."
        )

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id,
        DocumentChunk.vendor_id == vendor_id
    ).order_by(DocumentChunk.chunk_index.asc()).all()

    total_tokens = sum(c.token_count for c in chunks)
    return ChunkListResponse(
        document_id=document_id,
        vendor_id=vendor_id,
        total_chunks=len(chunks),
        total_tokens=total_tokens,
        chunks=chunks,
    )


@router.post(
    "/{document_id}/process",
    response_model=DocumentProcessResponse,
    summary="Trigger or re-trigger document text extraction (Deprecated)",
    deprecated=True,
)
def process_document(document_id: str, db: Session = Depends(get_db)):
    """
    Triggers text extraction and OCR fallback processing for a stored document.
    """
    try:
        result = DocumentProcessor.process_document(db, document_id)
        return result
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
