"""
Database health check utilities.
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.core.logging import get_logger
from src.db.session import engine

logger = get_logger(__name__)


def check_database_health() -> dict:
    """
    Verifies database connectivity.
    Returns a dictionary containing status and details.
    """
    status = {"status": "unhealthy", "details": ""}

    logger.info("Running database health check...")
    try:
        with engine.connect() as connection:
            # Simple ping
            connection.execute(text("SELECT 1"))
            status["status"] = "healthy"
            status["details"] = "Successfully connected to the database."
            logger.info("Database health check passed.")

    except SQLAlchemyError as e:
        status["details"] = str(e)
        logger.error(f"Database health check failed: {e}")

    return status
