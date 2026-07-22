from sqlalchemy.orm import Session

from src.db.models import Customer

from .base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: Session):
        super().__init__(session, Customer)
