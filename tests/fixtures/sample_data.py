import os
import tempfile

import pandas as pd


def create_sample_csv() -> str:
    fd, path = tempfile.mkstemp(suffix=".csv")
    df = pd.DataFrame(
        {
            "member_id": ["A1", "B2", "C3"],
            "loan_amnt": [5000.0, 10000.0, 15000.0],
            "int_rate": [5.0, 10.0, 15.0],
            "term": ["36 months", "60 months", "36 months"],
            "grade": ["A", "B", "C"],
            "loan_status": ["Current", "Charged Off", "Current"],
            "issue_d": ["2023-01-01", "2023-02-01", "2023-03-01"],
            "annual_inc": [50000.0, 60000.0, 120000.0],
            "home_ownership": ["RENT", "MORTGAGE", "OWN"],
            "addr_state": ["CA", "NY", "TX"],
            "fico_range_low": [700.0, 650.0, 750.0],
            "fico_range_high": [704.0, 654.0, 754.0],
            "dti": [15.0, 20.0, 10.0],
        }
    )
    df.to_csv(path, index=False)
    os.close(fd)
    return path
