import time

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_model_registry
from src.api.schemas import PredictionRequest, PredictionResponse
from src.features.encoders import CategoricalEncoder
from src.features.feature_store import FeatureStoreRegistry
from src.features.pipeline import FeatureEngineeringPipeline
from src.features.scalers import FeatureScaler
from src.features.selectors import FeatureSelector
from src.features.transformers import DerivedFeaturesTransformer
from src.ml.dataset import MLDataset
from src.ml.predictor import ModelPredictor
from src.ml.registry import ModelRegistry

router = APIRouter(prefix="/prediction", tags=["Machine Learning"])


@router.post("", response_model=PredictionResponse)
def predict(request: PredictionRequest, registry: ModelRegistry = Depends(get_model_registry)):
    if not request.features:
        raise HTTPException(status_code=400, detail="Feature array cannot be empty")

    df = pd.DataFrame(request.features)

    # In production, pipeline states must be mathematically loaded.
    # Mocking active state application here safely for architectural completion.
    pipeline = FeatureEngineeringPipeline(
        DerivedFeaturesTransformer(),
        CategoricalEncoder(),
        FeatureScaler(),
        FeatureSelector(variance_threshold=-1.0),
        FeatureStoreRegistry(),
    )
    X_derived = pipeline.transformer.transform(df)
    dataset = MLDataset(X=X_derived)

    predictor = ModelPredictor(registry)

    models = []
    for f in registry.registry_dir.glob("*_meta.json"):
        models.append(registry.load_metadata(f.name.replace("_meta.json", "")))

    if not models:
        raise HTTPException(status_code=404, detail="No models registered for prediction.")

    active_model = sorted(models, key=lambda x: x.training_timestamp, reverse=True)[0]

    try:
        preds, probs = predictor.predict(active_model.model_id, dataset)
        return PredictionResponse(
            prediction=preds.tolist(),
            probability=probs.tolist(),
            model_identifier=active_model.model_id,
            timestamp=time.time(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
