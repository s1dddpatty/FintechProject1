from typing import List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from .loan import LoanAnalytics
from .metrics import AggregateMetric, MetricValue
from .portfolio import PortfolioAnalytics
from .risk import RiskAnalytics


class ExecutiveDashboardReport(BaseModel):
    portfolio_kpis: List[MetricValue]
    risk_kpis: List[AggregateMetric]
    loan_kpis: List[AggregateMetric]


class ExecutiveAnalytics:
    def __init__(self, session: Session):
        self.session = session
        self.portfolio = PortfolioAnalytics(session)
        self.risk = RiskAnalytics(session)
        self.loan = LoanAnalytics(session)

    def generate_executive_summary(self) -> ExecutiveDashboardReport:
        portfolio_kpis = [
            self.portfolio.get_total_loans(),
            self.portfolio.get_total_funded_amount(),
            self.portfolio.get_average_loan_amount(),
            self.portfolio.get_average_interest_rate(),
            self.portfolio.get_portfolio_default_rate(),
        ]
        risk_kpis = [self.risk.get_default_rate_by_grade()]
        loan_kpis = [self.loan.get_grade_distribution(), self.loan.get_status_analysis()]
        return ExecutiveDashboardReport(portfolio_kpis=portfolio_kpis, risk_kpis=risk_kpis, loan_kpis=loan_kpis)
