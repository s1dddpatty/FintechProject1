from sqlalchemy.orm import Session

from src.db.models import Loan

from .base import BaseRepository


class LoanRepository(BaseRepository[Loan]):
    def __init__(self, session: Session):
        super().__init__(session, Loan)
