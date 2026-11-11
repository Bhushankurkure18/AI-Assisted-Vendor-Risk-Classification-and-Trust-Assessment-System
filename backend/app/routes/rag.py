"""
RAG REST API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.vendor import Vendor
from backend.app.schemas.rag import RAGQueryRequest, RAGResponse
from backend.app.services.rag.rag_service import RAGService

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["Phase 2 - RAG Retrieval"],
)

rag_service = RAGService()


@router.post(
    "/vendors/{vendor_id}/ask",
    response_model=RAGResponse,
    status_code=status.HTTP_200_OK,
    summary="Query vendor documentation using RAG semantic retrieval",
)
def ask_vendor_documentation(
    vendor_id: int,
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Retrieves evidence and answers questions about a vendor from indexed documents.
    Enforces vendor isolation and provides document citations with page numbers.
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} does not exist.",
        )

    response = rag_service.query(
        vendor_id=vendor_id,
        question=request.question,
        top_k=request.top_k,
    )
    return response

