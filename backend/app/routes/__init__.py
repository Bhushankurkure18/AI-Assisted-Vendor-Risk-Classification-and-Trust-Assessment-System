"""
API Routes Package.
"""
from backend.app.routes.vendors import router as vendors_router
from backend.app.routes.assessments import router as assessments_router

__all__ = ["vendors_router", "assessments_router"]
