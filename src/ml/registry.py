import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import joblib
from pydantic import BaseModel

from src.core.logging import get_logger

from .exceptions import RegistryError
from .metrics import EvaluationMetrics

logger = get_logger(__name__)


class ModelMetadata(BaseModel):
    model_id: str
    algorithm: str
    training_timestamp: str
    feature_list: List[str]
    training_parameters: Dict[str, Any]
    evaluation_metrics: EvaluationMetrics


class ModelRegistry:
    """Lightweight local registry utilizing joblib."""

    def __init__(self, registry_dir: str = "models/registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)

    def save_model(
        self, model: Any, algorithm: str, features: List[str], params: Dict[str, Any], metrics: EvaluationMetrics
    ) -> str:
        model_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        metadata = ModelMetadata(
            model_id=model_id,
            algorithm=algorithm,
            training_timestamp=timestamp,
            feature_list=features,
            training_parameters=params,
            evaluation_metrics=metrics,
        )

        model_path = self.registry_dir / f"{model_id}.joblib"
        meta_path = self.registry_dir / f"{model_id}_meta.json"

        try:
            joblib.dump(model, model_path)
            with open(meta_path, "w") as f:
                f.write(metadata.model_dump_json(indent=2))
            logger.info(f"Model {model_id} successfully persisted to registry.")
            return model_id
        except Exception as e:
            raise RegistryError(f"Failed to persist model: {e}")

    def load_model(self, model_id: str) -> Any:
        model_path = self.registry_dir / f"{model_id}.joblib"
        if not model_path.exists():
            raise RegistryError(f"Model binary not found: {model_path}")
        try:
            return joblib.load(model_path)
        except Exception as e:
            raise RegistryError(f"Failed to load model {model_id}: {e}")

    def load_metadata(self, model_id: str) -> ModelMetadata:
        meta_path = self.registry_dir / f"{model_id}_meta.json"
        if not meta_path.exists():
            raise RegistryError(f"Metadata file not found: {meta_path}")
        try:
            with open(meta_path, "r") as f:
                data = json.load(f)
            return ModelMetadata(**data)
        except Exception as e:
            raise RegistryError(f"Failed to load metadata {model_id}: {e}")
