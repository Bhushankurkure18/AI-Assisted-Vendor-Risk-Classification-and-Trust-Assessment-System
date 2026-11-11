"""
FastAPI Main Application Entry Point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.routes.vendors import router as vendors_router
from backend.app.routes.assessments import router as assessments_router
from backend.app.routes.mfg006_ml import router as mfg006_ml_router
from backend.app.routes.documents import router as documents_router
from backend.app.routes.rag import router as rag_router
from backend.app.routes.ai_assessments import router as ai_assessments_router

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-Assisted Vendor Risk Classification and Trust Assessment System REST API with Swagger documentation.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health Check"])
def root():
    """
    Root Health Check endpoint.
    """
    return {
        "message": "Vendor Risk Assessment API is running"
    }


# Include modular routers
app.include_router(vendors_router)
app.include_router(assessments_router)
app.include_router(mfg006_ml_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(ai_assessments_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
