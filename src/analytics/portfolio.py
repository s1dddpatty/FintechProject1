from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.logging import get_logger
from src.db.models import Loan

from .metrics import MetricValue

logger = get_logger(__name__)


class PortfolioAnalytics:
    def __init__(self, session: Session):
        self.session = session

    def get_total_loans(self) -> MetricValue:
        count = self.session.query(func.count(Loan.id)).scalar() or 0
        return MetricValue(name="Total Loans", value=count)

    def get_total_funded_amount(self) -> MetricValue:
        total = self.session.query(func.sum(Loan.loan_amnt)).scalar() or 0.0
        return MetricValue(name="Total Funded Amount", value=float(total))

    def get_average_loan_amount(self) -> MetricValue:
        avg = self.session.query(func.avg(Loan.loan_amnt)).scalar() or 0.0
        return MetricValue(name="Average Loan Amount", value=float(avg))

    def get_average_interest_rate(self) -> MetricValue:
        avg = self.session.query(func.avg(Loan.int_rate)).scalar() or 0.0
        return MetricValue(name="Average Interest Rate", value=float(avg))

    def get_portfolio_default_rate(self) -> MetricValue:
        total = self.session.query(func.count(Loan.id)).scalar() or 1
        defaults = (
            self.session.query(func.count(Loan.id)).filter(Loan.loan_status.in_(["Charged Off", "Default"])).scalar()
            or 0
        )
        return MetricValue(name="Portfolio Default Rate", value=float(defaults) / total)

    def get_active_loan_percentage(self) -> MetricValue:
        total = self.session.query(func.count(Loan.id)).scalar() or 1
        active = self.session.query(func.count(Loan.id)).filter(Loan.loan_status == "Current").scalar() or 0
        return MetricValue(name="Active Loan Percentage", value=float(active) / total)

    def get_charged_off_percentage(self) -> MetricValue:
        total = self.session.query(func.count(Loan.id)).scalar() or 1
        charged_off = self.session.query(func.count(Loan.id)).filter(Loan.loan_status == "Charged Off").scalar() or 0
        return MetricValue(name="Charged-Off Percentage", value=float(charged_off) / total)
