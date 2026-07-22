import io
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException
from src.core.logging import get_logger

logger = get_logger(__name__)

class PredictionEngine:
    """End-to-end inference workflow."""
    
    REQUIRED_COLUMNS = [
        "loan_amnt", "int_rate", "annual_inc", "fico_range_low", 
        "fico_range_high", "term", "grade", "home_ownership", "addr_state"
    ]
    
    # Central configuration for thresholds
    THRESHOLDS = {
        "low": 0.20,
        "high": 0.50
    }

    def __init__(self):
        self.artifacts_dir = Path("artifacts/models")
        self.pipeline_path = self.artifacts_dir / "preprocessing_pipeline.joblib"
        self.model_path = self.artifacts_dir / "best_model.joblib"
        
        self.preprocessor = None
        self.model = None
        self.metadata = None

    def _load_artifacts(self):
        """Loads required joblib artifacts or throws explicit errors."""
        if not self.pipeline_path.exists():
            raise HTTPException(status_code=500, detail="Missing preprocessing_pipeline.joblib. Please run the feature engineering pipeline.")
            
        if not self.model_path.exists():
            raise HTTPException(status_code=500, detail="Missing best_model.joblib. Please train a model first.")
            
        if self.preprocessor is None:
            self.preprocessor = joblib.load(self.pipeline_path)
            
        if self.model is None:
            self.model = joblib.load(self.model_path)
            
        if self.metadata is None:
            metadata_path = self.artifacts_dir / "metadata.json"
            import json
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}

    async def predict(self, file: UploadFile) -> List[Dict[str, Any]]:
        """Processes an uploaded CSV, runs preprocessing, and generates predictions."""
        # 1. Load Data
        contents = await file.read()
        try:
            df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
            
        # 2. Validate Schema
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Invalid schema. Missing required columns: {missing_cols}")

        # Ensure we have an ID column
        if "member_id" in df.columns:
            ids = df["member_id"].astype(str).tolist()
        elif "id" in df.columns:
            ids = df["id"].astype(str).tolist()
        else:
            ids = [f"APP-{i+1}" for i in range(len(df))]

        self._load_artifacts()
        
        # 3. Transform
        try:
            X = self.preprocessor.transform(df)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Preprocessing failed on input data: {str(e)}")
            
        # 4. Predict
        try:
            # Fallback for models without predict_proba
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)[:, 1]
            else:
                preds = self.model.predict(X)
                # Fake probabilities if none available
                probs = [0.9 if p == 1 else 0.1 for p in preds]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

        # 5. Format Output
        results = []
        timestamp = datetime.utcnow().isoformat()
        
        threshold = float(self.metadata.get("operating_threshold", 0.50))
        version = self.metadata.get("version", "1.0")
        
        for i, prob in enumerate(probs):
            if prob >= self.THRESHOLDS["high"]:
                risk_label = "High Risk"
            elif prob >= threshold:
                risk_label = "Medium Risk"
            else:
                risk_label = "Low Risk"
                
            predicted_class = 1 if prob >= threshold else 0
            
            # Confidence is how far it is from the decision boundary
            confidence = abs(prob - threshold) * 2
            confidence = min(1.0, confidence)
            
            results.append({
                "id": ids[i],
                "probability_of_default": float(prob),
                "decision_threshold": float(threshold),
                "predicted_class": int(predicted_class),
                "risk_label": risk_label,
                "confidence_score": float(confidence),
                "model_version": version,
                "timestamp": timestamp
            })
            
        return results
