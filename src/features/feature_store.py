from typing import List

from pydantic import BaseModel, Field


class FeatureMetadata(BaseModel):
    """Metadata regarding the generated feature matrix."""

    feature_names: List[str]
    num_features: int
    transformation_history: List[str] = Field(default_factory=list)


class FeatureStoreRegistry:
    """Mock store to hold references to Train/Test datasets and metadata."""

    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.metadata: FeatureMetadata = None

    def save(self, X_train, X_test, metadata: FeatureMetadata, y_train=None, y_test=None):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.metadata = metadata
