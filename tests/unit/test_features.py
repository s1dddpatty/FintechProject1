import numpy as np
import pandas as pd
import pytest

from src.features.encoders import CategoricalEncoder
from src.features.feature_store import FeatureStoreRegistry
from src.features.pipeline import FeatureEngineeringPipeline
from src.features.scalers import FeatureScaler
from src.features.selectors import FeatureSelector
from src.features.transformers import DerivedFeaturesTransformer


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "loan_amnt": [1000, 5000, 10000, 15000],
            "annual_inc": [50000, 60000, 120000, 80000],
            "int_rate": [5.0, 10.0, 15.0, 20.0],
            "grade": ["A", "B", "C", "D"],
            "home_ownership": ["RENT", "MORTGAGE", "RENT", "OWN"],
            "target": [0, 1, 0, 1],
            "constant_feature": [1, 1, 1, 1],
        }
    )


def test_derived_features(sample_df):
    transformer = DerivedFeaturesTransformer()
    df_transformed = transformer.transform(sample_df)

    assert "loan_to_income_ratio" in df_transformed.columns
    assert "interest_burden_proxy" in df_transformed.columns
    assert "annual_inc_log" in df_transformed.columns


def test_categorical_encoder(sample_df):
    encoder = CategoricalEncoder(ordinal_cols=["grade"], onehot_cols=["home_ownership"])
    encoder.fit(sample_df)
    df_encoded = encoder.transform(sample_df)

    assert "grade" in df_encoded.columns
    assert df_encoded["grade"].dtype in [np.float64, np.int64]

    # OneHot drops original column completely
    assert "home_ownership" not in df_encoded.columns
    assert any(col.startswith("home_ownership_") for col in df_encoded.columns)


def test_feature_scaler(sample_df):
    scaler = FeatureScaler(method="standard", columns=["loan_amnt", "annual_inc"])
    scaler.fit(sample_df)
    df_scaled = scaler.transform(sample_df)

    assert np.isclose(df_scaled["loan_amnt"].mean(), 0, atol=1e-7)


def test_feature_selector(sample_df):
    selector = FeatureSelector(variance_threshold=0.1)

    df_numeric = sample_df.drop(columns=["grade", "home_ownership"])
    selector.fit(df_numeric)
    df_selected = selector.transform(df_numeric)

    # Constant feature dropped
    assert "constant_feature" not in df_selected.columns
    assert "loan_amnt" in df_selected.columns


def test_pipeline_orchestration(sample_df):
    transformer = DerivedFeaturesTransformer()
    encoder = CategoricalEncoder(ordinal_cols=["grade"], onehot_cols=["home_ownership"])
    scaler = FeatureScaler(
        method="standard",
        columns=[
            "loan_amnt",
            "annual_inc",
            "int_rate",
            "loan_to_income_ratio",
            "interest_burden_proxy",
            "annual_inc_log",
            "loan_amnt_log",
        ],
    )
    selector = FeatureSelector(variance_threshold=0.0)
    store = FeatureStoreRegistry()

    pipeline = FeatureEngineeringPipeline(transformer, encoder, scaler, selector, store)

    X_train, X_test = pipeline.fit_transform(sample_df, target_col="target", test_size=0.25)

    assert len(X_train) == 3
    assert len(X_test) == 1
    assert store.metadata is not None
    assert "target" not in X_train.columns
