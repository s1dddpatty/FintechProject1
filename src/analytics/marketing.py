from sqlalchemy.orm import Session

from .metrics import AggregateMetric, MetricValue


class MarketingAnalytics:
    """Mock implementation pending future MarketingCampaign DB Models."""

    def __init__(self, session: Session):
        self.session = session

    def get_campaign_performance(self) -> AggregateMetric:
        return AggregateMetric(
            name="Campaign Performance", distribution={"Organic": 1000, "Paid Search": 500, "Referral": 250}
        )

    def get_conversion_rate(self) -> MetricValue:
        return MetricValue(name="Average Conversion Rate", value=0.035)

    def get_roi(self) -> MetricValue:
        return MetricValue(name="Marketing ROI", value=1.5)
