# Machine Learning Platform Architecture

The Machine Learning Platform provides a robust, reproducible, and highly modular pipeline for predictive modeling, evaluation, comparison, and persistence. It rigidly consumes data produced strictly by the upstream `Feature Store` and relies on `scikit-learn` primitives.

## 1. Overall ML Architecture
The ML tier enforces strict separation of concerns through specialized components.
- **ModelTrainer**: Encapsulates algorithm initializations. Avoids raw scripting by providing a standardized interface to fit datasets.
- **ModelEvaluator**: Evaluates prediction vectors and structures multi-metric outputs via strongly-typed Pydantic classes (`EvaluationMetrics`). Also natively implements Cross-Validation scoring.
- **ModelRegistry**: A lightweight local model tracker using `joblib` acting as an infrastructural precursor to tools like MLflow. It stores binary `.joblib` files identically alongside highly audited `.json` metadata.
- **ModelExplainer**: Performs agnostic permutation feature importance to extract interpretability insights and "top-feature" lists from complex tree algorithms dynamically.
- **ModelPredictor**: Isolates offline inference logic. Loads requested models by ID dynamically from the registry and generates both scoring vectors and underlying probability thresholds.

## 2. Supported Algorithms
Currently, the `ModelTrainer` abstracts the initialization natively for:
- Logistic Regression
- Random Forest
- Gradient Boosting

*Extension Guide*: To add a new algorithm (e.g., XGBoost or LightGBM), simply add the new library class map into the `SUPPORTED_MODELS` dictionary inside `ModelTrainer`. No other pipeline orchestration loops need to be modified.

## 3. Training & Evaluation Lifecycle
The pipeline securely consumes `X_train` and `X_test` via an explicit `MLDataset` wrapper. When requested to run multiple algorithms, the `MachineLearningPipeline` iterates over them automatically, computes testing KPIs using the `ModelEvaluator`, compares the results using a built-in optimizer, and persists strictly the **best-performing** model (optimizing over ROC AUC) to the `ModelRegistry`.

## 4. Evaluation Methodology
Model evaluation enforces multi-metric computation over purely held-out test groups:
*   Accuracy, Precision, Recall, F1
*   ROC AUC
*   Standard Classification Report Maps
*   Standard Confusion Matrices

## 5. Explainability Approach
Due to dependency optimizations preventing massive tree visualization libraries, the `ModelExplainer` relies on mathematically agnostic `permutation_importance`. This loop shuffles data points sequentially per feature column to observe the actual performance drop in model accuracy, effectively isolating true predictive impact reliably without relying on underlying algorithm-specific attributes.
