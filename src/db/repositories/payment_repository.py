from sqlalchemy.orm import Session

from src.db.models import Payment

from .base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: Session):
        super().__init__(session, Payment)
