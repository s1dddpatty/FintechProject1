# ADR 0004: Feature Engineering Separation

## Status
Accepted

## Context
During initial ML explorations, feature engineering (imputations, scalers, derivation) is commonly tangled inside Jupyter Notebooks or closely bound to the training script.

## Decision
We decoupled the feature engineering (`src.features`) into discrete object-oriented classes (Transformers, Encoders, Selectors, Scalers) operating entirely independently of the ML pipelines. 

## Consequences
- **Positive**: Avoids training-serving skew. The exact same feature engineering pipeline executed during batch ingestion is seamlessly re-executed during real-time FastAPI inferences.
- **Negative**: Increases the upfront engineering overhead for Data Scientists mapping new columns.
