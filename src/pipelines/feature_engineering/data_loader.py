import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.db.models import Loan
from src.core.logging import get_logger

logger = get_logger(__name__)

class FeatureDataLoader:
    """Loads raw data from PostgreSQL for feature engineering."""

    def __init__(self, session: Session):
        self.session = session

    def load_raw_features(self) -> pd.DataFrame:
        """Loads a dataset from the Loan table."""
        logger.info("Loading raw data from database...")
        
        # Querying Loan
        stmt = select(Loan)
        
        results = self.session.execute(stmt).scalars().all()
        
        if not results:
            logger.warning("No data found in the database.")
            return pd.DataFrame()

        rows = []
        for loan in results:
            row = {
                # Loan features
                "loan_amnt": loan.loan_amnt,
                "int_rate": loan.int_rate,
                "term": loan.term,
                "grade": loan.grade,
                "issue_d": loan.issue_d,
                "loan_status": loan.loan_status,
                
                # Applicant Snapshot features
                "annual_inc": loan.annual_inc,
                "home_ownership": loan.home_ownership,
                "addr_state": loan.addr_state,
                "fico_range_low": loan.fico_range_low,
                "fico_range_high": loan.fico_range_high,
            }
            rows.append(row)
            
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns.")
        return df
