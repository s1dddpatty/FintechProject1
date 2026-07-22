import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.analytics.executive import ExecutiveAnalytics
from src.analytics.portfolio import PortfolioAnalytics
from src.analytics.risk import RiskAnalytics
from src.db.base import Base
from src.db.models import Loan


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def session(engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    l1 = Loan(id="L1", loan_amnt=1000, int_rate=5.0, grade="A", loan_status="Current", addr_state="CA", annual_inc=50000)
    l2 = Loan(id="L2", loan_amnt=5000, int_rate=15.0, grade="D", loan_status="Charged Off", addr_state="NY", annual_inc=100000)
    session.add_all([l1, l2])

    session.commit()
    yield session
    session.close()


def test_portfolio_analytics(session):
    analytics = PortfolioAnalytics(session)
    total_loans = analytics.get_total_loans()
    assert total_loans.value == 2

    default_rate = analytics.get_portfolio_default_rate()
    assert default_rate.value == 0.5  # 1 out of 2 is charged off


def test_risk_analytics(session):
    analytics = RiskAnalytics(session)
    grade_risk = analytics.get_default_rate_by_grade()
    assert grade_risk.distribution["A"] == 0.0
    assert grade_risk.distribution["D"] == 1.0


def test_executive_analytics(session):
    analytics = ExecutiveAnalytics(session)
    report = analytics.generate_executive_summary()
    assert len(report.portfolio_kpis) == 3
    assert len(report.risk_kpis) == 1
    assert len(report.loan_kpis) == 2
