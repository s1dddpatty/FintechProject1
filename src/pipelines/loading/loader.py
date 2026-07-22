import time
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.logging import get_logger
from src.db.base import Base

from .exceptions import BatchInsertError

logger = get_logger(__name__)


class BatchLoader:
    """Loads ORM models into PostgreSQL in chunks with atomic transaction support."""

    def __init__(self, session: Session, chunk_size: int = 1000):
        self.session = session
        self.chunk_size = chunk_size

    def load(self, models: List[Base]) -> None:
        total = len(models)
        if total == 0:
            logger.info("No records to load. Skipping.")
            return

        logger.info(f"Starting batch load of {total} records. Chunk size: {self.chunk_size}")
        start_time = time.time()

        try:
            for i in range(0, total, self.chunk_size):
                chunk = models[i : i + self.chunk_size]
                
                # Check if it's the first element to determine table
                if chunk:
                    model_class = type(chunk[0])
                    from sqlalchemy.dialects.postgresql import insert
                    
                    # Convert models to dictionaries for bulk execution
                    chunk_dicts = [
                        {
                            c.name: getattr(model, c.name) 
                            for c in model_class.__table__.columns 
                            if getattr(model, c.name) is not None
                        }
                        for model in chunk
                    ]
                    
                    stmt = insert(model_class)
                    stmt = stmt.on_conflict_do_nothing()
                    self.session.execute(stmt, chunk_dicts)

                # Flush sends the SQL statements to the DB without committing the transaction.
                # This catches constraint violations immediately, avoiding huge memory overheads.
                self.session.flush()
                logger.debug(f"Flushed chunk {i} to {i + len(chunk)}...")

            # If all chunks flushed successfully without violating constraints, commit transaction.
            self.session.commit()
            duration = time.time() - start_time
            logger.info(f"Successfully loaded {total} records in {duration:.2f} seconds.")

        except SQLAlchemyError as e:
            logger.error(f"Batch loading failed! Rolling back entire batch transaction. Error: {e}")
            self.session.rollback()
            raise BatchInsertError(f"Database insertion failed: {e}")
