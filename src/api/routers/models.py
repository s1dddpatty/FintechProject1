import os
from typing import List

from fastapi import APIRouter, Depends

from src.api.dependencies import get_model_registry
from src.ml.registry import ModelMetadata, ModelRegistry

router = APIRouter(prefix="/models", tags=["Machine Learning"])


@router.get("", response_model=List[ModelMetadata])
def list_models(registry: ModelRegistry = Depends(get_model_registry)):
    """Retrieve all tracked machine learning models strictly from internal registry JSON configurations."""
    models = []
    if not registry.registry_dir.exists():
        return models

    for file in os.listdir(registry.registry_dir):
        if file.endswith("_meta.json"):
            model_id = file.replace("_meta.json", "")
            try:
                models.append(registry.load_metadata(model_id))
            except Exception:
                continue
    return models
