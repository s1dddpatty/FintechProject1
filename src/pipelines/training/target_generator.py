import pandas as pd
from src.core.logging import get_logger

logger = get_logger(__name__)

class TargetGenerator:
    """Generates target labels for ML from raw loan data."""
    
    DEFAULT_STATUSES = [
        "Charged Off",
        "Default",
        "Does not meet the credit policy. Status:Charged Off"
    ]
    
    NON_DEFAULT_STATUSES = [
        "Fully Paid",
        "Does not meet the credit policy. Status:Fully Paid"
    ]

    @classmethod
    def generate_target(cls, df: pd.DataFrame, status_col: str = "loan_status") -> pd.DataFrame:
        """
        Creates 'is_default' binary target and drops ambiguous rows.
        Returns a DataFrame with 'is_default' included.
        """
        if status_col not in df.columns:
            raise ValueError(f"Target column '{status_col}' not found in dataset.")
            
        logger.info(f"Generating targets from {status_col}...")
        
        # Filter to only terminal statuses
        terminal_mask = df[status_col].isin(cls.DEFAULT_STATUSES + cls.NON_DEFAULT_STATUSES)
        df_filtered = df[terminal_mask].copy()
        
        dropped = len(df) - len(df_filtered)
        if dropped > 0:
            logger.info(f"Dropped {dropped} non-terminal rows (e.g. Current, In Grace Period).")
            
        df_filtered["is_default"] = df_filtered[status_col].apply(
            lambda x: 1 if x in cls.DEFAULT_STATUSES else 0
        )
        
        logger.info(f"Target distribution: {df_filtered['is_default'].value_counts().to_dict()}")
        return df_filtered
