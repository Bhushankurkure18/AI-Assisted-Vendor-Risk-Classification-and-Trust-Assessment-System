"""
API Routes Package.
"""
from backend.app.routes.vendors import router as vendors_router
from backend.app.routes.assessments import router as assessments_router
from backend.app.routes.documents import router as documents_router
from backend.app.routes.rag import router as rag_router
from backend.app.routes.ai_assessments import router as ai_assessments_router

__all__ = ["vendors_router", "assessments_router", "documents_router", "rag_router", "ai_assessments_router"]
