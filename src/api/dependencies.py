from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.analytics.applicant import ApplicantAnalytics
from src.analytics.executive import ExecutiveAnalytics
from src.analytics.loan import LoanAnalytics
from src.analytics.portfolio import PortfolioAnalytics
from src.analytics.risk import RiskAnalytics
from src.db.session import SessionLocal
from src.ml.registry import ModelRegistry


def get_db() -> Generator[Session, None, None]:
    """Provides a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_model_registry() -> ModelRegistry:
    return ModelRegistry()


def get_portfolio_analytics(db: Session = Depends(get_db)) -> PortfolioAnalytics:
    return PortfolioAnalytics(db)


def get_applicant_analytics(db: Session = Depends(get_db)) -> ApplicantAnalytics:
    return ApplicantAnalytics(db)


def get_loan_analytics(db: Session = Depends(get_db)) -> LoanAnalytics:
    return LoanAnalytics(db)


def get_risk_analytics(db: Session = Depends(get_db)) -> RiskAnalytics:
    return RiskAnalytics(db)


def get_executive_analytics(db: Session = Depends(get_db)) -> ExecutiveAnalytics:
    return ExecutiveAnalytics(db)
