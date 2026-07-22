from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.logging import get_logger
from src.db.models import Loan

from .metrics import AggregateMetric

logger = get_logger(__name__)


class ApplicantAnalytics:
    def __init__(self, session: Session):
        self.session = session

    def get_home_ownership_distribution(self) -> AggregateMetric:
        results = (
            self.session.query(Loan.home_ownership, func.count(Loan.id))
            .group_by(Loan.home_ownership)
            .all()
        )
        dist = {k if k else "Unknown": v for k, v in results}
        return AggregateMetric(name="Home Ownership Distribution", distribution=dist)

    def get_income_statistics(self) -> AggregateMetric:
        stats = self.session.query(
            func.avg(Loan.annual_inc), func.min(Loan.annual_inc), func.max(Loan.annual_inc)
        ).first()
        return AggregateMetric(
            name="Income Statistics",
            distribution={"Average": float(stats[0] or 0), "Min": float(stats[1] or 0), "Max": float(stats[2] or 0)},
        )

    def get_state_distribution(self) -> AggregateMetric:
        results = (
            self.session.query(Loan.addr_state, func.count(Loan.id)).group_by(Loan.addr_state).all()
        )
        dist = {k if k else "Unknown": v for k, v in results}
        return AggregateMetric(name="Geographic Distribution", distribution=dist)
