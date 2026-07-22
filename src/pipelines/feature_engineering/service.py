import os
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.core.logging import get_logger
from .pipeline import build_preprocessing_pipeline
from .data_loader import FeatureDataLoader

logger = get_logger(__name__)

class FeatureEngineeringService:
    """Orchestrates feature engineering, persisting the pipeline and metadata."""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.artifacts_dir = Path("artifacts/models")
        self.pipeline_path = self.artifacts_dir / "preprocessing_pipeline.joblib"
        
        # In-memory caches for the last run
        self.last_df_raw: pd.DataFrame = None
        self.last_df_transformed: pd.DataFrame = None
        self.metadata: Dict[str, Any] = {}

    def run_pipeline(self):
        """Loads data, fits the pipeline, and generates features."""
        logger.info("Running feature engineering pipeline...")
        
        if not self.db_session:
            raise ValueError("Database session is required to load data.")
            
        loader = FeatureDataLoader(self.db_session)
        df_raw = loader.load_raw_features()
        
        if df_raw.empty:
            raise ValueError("No data available in the database for feature engineering.")
            
        self.last_df_raw = df_raw.copy()
        
        missing_before = df_raw.isna().sum().to_dict()

        pipeline = build_preprocessing_pipeline()
        
        # Fit and transform
        X_transformed = pipeline.fit_transform(df_raw)
        
        # Save fitted pipeline
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, self.pipeline_path)
        logger.info(f"Fitted pipeline saved to {self.pipeline_path}")
        
        # Extract feature names
        try:
            # get_feature_names_out works on scikit-learn >= 1.2 for ColumnTransformer
            preprocessor = pipeline.named_steps["preprocessor"]
            feature_names = preprocessor.get_feature_names_out()
        except Exception as e:
            logger.warning(f"Could not extract feature names automatically: {e}")
            feature_names = [f"feature_{i}" for i in range(X_transformed.shape[1])]
            
        df_transformed = pd.DataFrame(X_transformed, columns=feature_names)
        self.last_df_transformed = df_transformed
        
        missing_after = df_transformed.isna().sum().to_dict()

        # Build Metadata
        # Find which features were categorical vs numerical
        numeric_features = [
            "loan_amnt", "int_rate", "annual_inc", "fico_range_low", "fico_range_high", "term"
        ]
        categorical_features = [
            "grade", "home_ownership", "addr_state"
        ]
        
        self.metadata = {
            "original_feature_count": len(df_raw.columns),
            "engineered_feature_count": len(feature_names),
            "original_features": list(df_raw.columns),
            "transformed_features": list(feature_names),
            "numerical_features_input": numeric_features,
            "categorical_features_input": categorical_features,
            "missing_values_before": missing_before,
            "missing_values_after": missing_after,
        }
        
        logger.info("Feature engineering complete.")
        return self.metadata

    def get_summary(self) -> Dict[str, Any]:
        """Returns the summary statistics of the last pipeline run."""
        if not self.metadata:
            # If not in memory, we could load it from a metadata file, but for now we just run it or return empty
            return {"error": "Pipeline has not been run in this session."}
        return self.metadata
        
    def get_preview(self) -> Dict[str, Any]:
        """Returns a preview of the engineered feature matrix."""
        if self.last_df_transformed is None:
            return {"error": "Pipeline has not been run in this session."}
            
        return {
            "columns": list(self.last_df_transformed.columns),
            "data": self.last_df_transformed.head(10).to_dict(orient="records")
        }
