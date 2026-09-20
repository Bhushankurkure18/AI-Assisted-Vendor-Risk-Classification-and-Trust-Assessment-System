"""
Database engine and session management.
Supports PostgreSQL with transparent fallback to SQLite for environments without active Postgres services.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_engine():
    try:
        # Attempt to create engine with configured DATABASE_URL
        if settings.DATABASE_URL.startswith("sqlite"):
            engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
            # Test connection probe
            with engine.connect() as conn:
                pass
            return engine
    except Exception as exc:
        logger.warning(
            f"Could not connect to configured DATABASE_URL ({settings.DATABASE_URL}): {exc}. "
            f"Falling back to local SQLite engine: {settings.FALLBACK_SQLITE_URL}"
        )
        return create_engine(settings.FALLBACK_SQLITE_URL, connect_args={"check_same_thread": False})
    return engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
