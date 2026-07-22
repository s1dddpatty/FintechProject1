import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin

class TermToIntegerTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer to parse ' 36 months' to 36."""
    
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X_out = X.copy()
        if "term" in X_out.columns:
            # Extract digits and convert to float (will be imputed/scaled later if needed)
            X_out["term"] = X_out["term"].astype(str).str.extract(r'(\d+)').astype(float)
        return X_out

class DropColumnsTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer to drop columns not needed for modeling."""
    
    def __init__(self, cols_to_drop):
        self.cols_to_drop = cols_to_drop
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X_out = X.copy()
        for col in self.cols_to_drop:
            if col in X_out.columns:
                X_out.drop(columns=[col], inplace=True)
        return X_out

def build_preprocessing_pipeline() -> Pipeline:
    """Builds the main scikit-learn preprocessing pipeline."""
    
    numeric_features = [
        "loan_amnt", "int_rate", "annual_inc", "fico_range_low", "fico_range_high", "term"
    ]
    categorical_features = [
        "grade", "home_ownership", "addr_state"
    ]
    columns_to_drop = ["issue_d"]

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
        remainder="drop" # Drop any other columns that weren't explicitly transformed
    )

    # Full Pipeline
    full_pipeline = Pipeline([
        ("custom", preprocessor_custom),
        ("preprocessor", preprocessor)
    ])

    return full_pipeline
