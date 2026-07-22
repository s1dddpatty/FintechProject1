from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict


class MLDataset(BaseModel):
    """Holds engineered features strictly isolated for training or evaluation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    X: pd.DataFrame
    y: Optional[pd.Series] = None
