import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin

class TermToIntegerTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer to parse ' 36 months' to 36."""
    
    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self
        
    def transform(self, X):
        X_out = X.copy()
        if "term" in X_out.columns:
            # Extract digits and convert to float (will be imputed/scaled later if needed)
            X_out["term"] = X_out["term"].astype(str).str.extract(r'(\d+)').astype(float)
        return X_out

class DropColumnsTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer to drop columns not needed for modeling."""
    
    def __init__(self, cols_to_drop=None):
        self.cols_to_drop = cols_to_drop or []
        
    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self
        
    def transform(self, X):
        X_out = X.copy()
        for col in self.cols_to_drop:
            if col in X_out.columns:
                X_out.drop(columns=[col], inplace=True)
        return X_out

def build_preprocessing_pipeline() -> Pipeline:
    """
    Builds the production mathematical scikit-learn preprocessing pipeline (Pipeline 2)
    ingesting the 21-column canonical credit dataset.
    """
    numeric_features = [
        "loan_amnt", "term", "int_rate", "installment", "annual_inc", "emp_length",
        "fico_score", "fico_range_low", "fico_range_high", "dti", "revol_util",
        "credit_history_months", "installment_to_income", "loan_to_income", "grade_ordinal"
    ]
    
    categorical_features = [
        "home_ownership", "purpose", "addr_state"
    ]
    
    columns_to_drop = ["id", "loan_status", "grade", "issue_d"]

    # Pre-cleaning steps
    preprocessor_custom = Pipeline([
        ("term_to_int", TermToIntegerTransformer()),
        ("drop_columns", DropColumnsTransformer(cols_to_drop=columns_to_drop))
    ])

    # Core transformations
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # Combine
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop" # Drop any other non-canonical columns
    )

    # Full Pipeline
    full_pipeline = Pipeline([
        ("custom", preprocessor_custom),
        ("preprocessor", preprocessor)
    ])

    return full_pipeline
