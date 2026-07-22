
from fastapi import APIRouter, Depends

from src.analytics.applicant import ApplicantAnalytics
from src.analytics.executive import ExecutiveAnalytics, ExecutiveDashboardReport
from src.analytics.loan import LoanAnalytics
from src.analytics.portfolio import PortfolioAnalytics
from src.analytics.risk import RiskAnalytics
from src.api.dependencies import (
    get_applicant_analytics,
    get_executive_analytics,
    get_loan_analytics,
    get_portfolio_analytics,
    get_risk_analytics,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/portfolio")
def get_portfolio(analytics: PortfolioAnalytics = Depends(get_portfolio_analytics)):
    return {
        "total_loans": analytics.get_total_loans(),
        "total_funded": analytics.get_total_funded_amount(),
        "default_rate": analytics.get_portfolio_default_rate(),
    }


@router.get("/applicant")
def get_applicant(analytics: ApplicantAnalytics = Depends(get_applicant_analytics)):
    return {
        "home_ownership": analytics.get_home_ownership_distribution(),
        "income_stats": analytics.get_income_statistics(),
    }


@router.get("/loan")
def get_loan(analytics: LoanAnalytics = Depends(get_loan_analytics)):
    return {
        "grade_distribution": analytics.get_grade_distribution(),
        "status_analysis": analytics.get_status_analysis(),
    }


@router.get("/risk")
def get_risk(analytics: RiskAnalytics = Depends(get_risk_analytics)):
    return {"default_by_grade": analytics.get_default_rate_by_grade()}


@router.get("/executive", response_model=ExecutiveDashboardReport)
def get_executive(analytics: ExecutiveAnalytics = Depends(get_executive_analytics)):
    return analytics.generate_executive_summary()
