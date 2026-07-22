"""
SQLAlchemy session and engine management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Create Engine
engine_kwargs = {}
if settings.use_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

logger.info(f"Initializing database engine with driver: {'sqlite' if settings.use_sqlite else settings.db_driver}")

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Enables connection health checks
    **engine_kwargs,
)

# Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures safe creation and teardown of connections.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()
