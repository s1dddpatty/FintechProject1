from typing import Dict, Union

from pydantic import BaseModel


class MetricValue(BaseModel):
    """Represents a single scalar business metric."""

    name: str
    value: Union[float, int, str]
    description: str = ""


class AggregateMetric(BaseModel):
    """Represents a distribution or grouped metric."""

    name: str
    distribution: Dict[str, Union[float, int]]
    description: str = ""
