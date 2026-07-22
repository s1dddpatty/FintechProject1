from sqlalchemy.orm import Session

from src.db.models import Prediction

from .base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: Session):
        super().__init__(session, Prediction)
