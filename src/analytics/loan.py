from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import Loan

from .metrics import AggregateMetric


class LoanAnalytics:
    def __init__(self, session: Session):
        self.session = session

    def get_grade_distribution(self) -> AggregateMetric:
        results = self.session.query(Loan.grade, func.count(Loan.id)).group_by(Loan.grade).all()
        dist = {k if k else "Unknown": v for k, v in results}
        return AggregateMetric(name="Loan Grade Distribution", distribution=dist)

    def get_term_distribution(self) -> AggregateMetric:
        results = self.session.query(Loan.term, func.count(Loan.id)).group_by(Loan.term).all()
        dist = {k if k else "Unknown": v for k, v in results}
        return AggregateMetric(name="Loan Term Distribution", distribution=dist)

    def get_status_analysis(self) -> AggregateMetric:
        results = self.session.query(Loan.loan_status, func.count(Loan.id)).group_by(Loan.loan_status).all()
        dist = {k if k else "Unknown": v for k, v in results}
        return AggregateMetric(name="Loan Status Analysis", distribution=dist)
