from typing import Any, Generic, List, Type, TypeVar

from sqlalchemy.orm import Session

from src.db.base import Base
from src.observability.metrics import track_db_query

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic CRUD operations for SQLAlchemy models."""

    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    @track_db_query("get_by_id")
    def get_by_id(self, id: Any) -> T | None:
        return self.session.get(self.model_class, id)

    @track_db_query("add")
    def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    @track_db_query("add_all")
    def add_all(self, entities: List[T]) -> None:
        self.session.add_all(entities)
