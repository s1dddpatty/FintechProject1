import json
import joblib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from src.core.logging import get_logger

logger = get_logger(__name__)

class ModelRegistry:
    """Evaluates models, selects the best one, and persists the artifacts."""
    
    def __init__(self):
        self.artifacts_dir = Path("artifacts/models")
        self.best_model_path = self.artifacts_dir / "best_model.joblib"
        self.metadata_path = self.artifacts_dir / "metadata.json"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_model(self, model, X_test, y_test, threshold: float = 0.5) -> Dict[str, Any]:
        """Calculates evaluation metrics for a single model."""
        try:
            if len(set(y_test)) == 1:
                roc_auc = 0.5
                preds = model.predict(X_test)
            elif hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_test)[:, 1]
                roc_auc = roc_auc_score(y_test, probs)
                preds = (probs >= threshold).astype(int)
            else:
                preds = model.predict(X_test)
                roc_auc = roc_auc_score(y_test, preds)
        except Exception:
            roc_auc = 0.5
            preds = model.predict(X_test)
            
        cm = confusion_matrix(y_test, preds)
        
        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "f1": f1_score(y_test, preds, zero_division=0),
            "roc_auc": roc_auc,
            "confusion_matrix": cm.tolist()
        }
        return metrics

    def select_best_model(self, model_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Selects the best model primarily based on ROC-AUC."""
        best_eval = max(model_evaluations, key=lambda x: x["metrics"]["roc_auc"])
        logger.info(f"Selected best model: {best_eval['name']} with ROC-AUC {best_eval['metrics']['roc_auc']:.4f}")
        return best_eval

    def persist_best_model(self, best_eval: Dict[str, Any], metadata_extras: Dict[str, Any]):
        """Saves the best model and its metadata."""
        joblib.dump(best_eval["model"], self.best_model_path)
        logger.info(f"Best model saved to {self.best_model_path}")
        
        metadata = {
            "model_name": best_eval["name"],
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            **metadata_extras,
            "metrics": best_eval["metrics"]
        }
        
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Metadata saved to {self.metadata_path}")
        return metadata
