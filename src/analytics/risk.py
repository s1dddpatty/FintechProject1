from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import Loan

from .metrics import AggregateMetric


class RiskAnalytics:
    def __init__(self, session: Session):
        self.session = session

    def _calculate_default_rate_by_group(self, group_col) -> AggregateMetric:
        total_sq = (
            self.session.query(group_col.label("grp"), func.count(Loan.id).label("total"))
            .group_by(group_col)
            .subquery()
        )
        default_sq = (
            self.session.query(group_col.label("grp"), func.count(Loan.id).label("defaults"))
            .filter(Loan.loan_status.in_(["Charged Off", "Default"]))
            .group_by(group_col)
            .subquery()
        )

        results = (
            self.session.query(total_sq.c.grp, default_sq.c.defaults, total_sq.c.total)
            .outerjoin(default_sq, total_sq.c.grp == default_sq.c.grp)
            .all()
        )

        dist = {}
        for grp, defaults, total in results:
            grp_name = str(grp) if grp else "Unknown"
            rate = float(defaults or 0) / float(total) if total else 0.0
            dist[grp_name] = rate

        return AggregateMetric(name="Default Rate", distribution=dist)

    def get_default_rate_by_grade(self) -> AggregateMetric:
        metric = self._calculate_default_rate_by_group(Loan.grade)
        metric.name = "Default Rate by Grade"
        return metric

    def get_default_rate_by_state(self) -> AggregateMetric:
        # Require join
        total_sq = (
            self.session.query(Customer.addr_state.label("grp"), func.count(Loan.id).label("total"))
            .join(Loan)
            .group_by(Customer.addr_state)
            .subquery()
        )
        default_sq = (
            self.session.query(Customer.addr_state.label("grp"), func.count(Loan.id).label("defaults"))
            .join(Loan)
            .filter(Loan.loan_status.in_(["Charged Off", "Default"]))
            .group_by(Customer.addr_state)
            .subquery()
        )
        results = (
            self.session.query(total_sq.c.grp, default_sq.c.defaults, total_sq.c.total)
            .outerjoin(default_sq, total_sq.c.grp == default_sq.c.grp)
            .all()
        )

        dist = {str(g) if g else "Unknown": float(d or 0) / float(t) for g, d, t in results if t}
        return AggregateMetric(name="Default Rate by State", distribution=dist)
