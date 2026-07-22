import pandas as pd
from src.pipelines.ingestion.reader import CSVReader
from src.pipelines.ingestion.cleaner import DataCleaner
from src.pipelines.ingestion.normalizer import DataNormalizer
from src.pipelines.validation import (
    BusinessValidator,
    QualityValidator,
    SchemaValidator,
    ValidationPipeline,
    get_standard_loan_rules,
)

reader = CSVReader()
df = reader.read("benchmarks/dataset_100.csv")

cleaner = DataCleaner()
df = cleaner.clean(df)

normalizer = DataNormalizer(bool_columns=[], currency_columns=[])
df = normalizer.normalize(df)

schema_validator = SchemaValidator(
    expected_schema={
        "member_id": "numeric",
        "loan_amnt": "numeric",
        "int_rate": "numeric",
    },
    required_columns=["member_id", "loan_amnt"],
    primary_keys=[]
)
business_validator = BusinessValidator(rules=get_standard_loan_rules())
quality_validator = QualityValidator()

validator = ValidationPipeline(
    schema_validator=schema_validator,
    business_validator=business_validator,
    quality_validator=quality_validator
)
report = validator.run(df)

print("Passed checks:", report.passed_checks)
print("Failed checks:", report.failed_checks)
