# Feature Engineering Architecture

The Feature Engineering layer isolates the transformation logic required to take "validated but raw" data and convert it into mathematical matrices suitable for Machine Learning model training and inference.

## 1. Feature Lifecycle
1. **Derivation**: Calculating new signals from raw data (e.g., `loan_to_income_ratio`, logarithmic compressions) via the `DerivedFeaturesTransformer`.
2. **Encoding**: Converting categorical text features into numerical representations (`OneHotEncoder`, `OrdinalEncoder`).
3. **Scaling**: Standardizing the mathematical distribution of features (`StandardScaler`, `RobustScaler`, `MinMaxScaler`) to prevent gradient explosion during model training.
4. **Selection**: Automatically pruning zero-variance features or highly co-linear variables (correlation > 0.95) using the `FeatureSelector` to prevent overfitting.
5. **Storage**: Writing the final `X_train` and `X_test` matrices alongside rigorous `FeatureMetadata` to a mock Feature Store for downstream retrieval.

## 2. Leakage Prevention Strategy
To prevent **Data Leakage**, the `FeatureEngineeringPipeline` enforces a strict algorithmic split. The raw `DataFrame` is split into training and testing chunks *before* the Encoders, Scalers, and Selectors are `.fit()`. The `.transform()` method is then safely and independently applied to `X_test` using the boundaries learned strictly from `X_train`.

## 3. Extensibility
The pipeline relies heavily on Dependency Injection. To swap a generic `StandardScaler` for a custom domain-specific percentile scalar, developers only need to instantiate the pipeline passing their custom class ensuring it adheres to the `.fit()` and `.transform()` interfaces. All underlying logic safely leverages `scikit-learn` API standards.
