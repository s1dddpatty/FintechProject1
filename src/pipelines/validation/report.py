"""
Validation report definitions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ValidationReport(BaseModel):
    """
    Serializable report summarizing validation execution.
    """

    is_valid: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    passed_checks: List[str] = Field(default_factory=list)
    failed_checks: List[str] = Field(default_factory=list)
    fatal_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    dataset_statistics: Dict[str, Any] = Field(default_factory=dict)
    quality_metrics: Dict[str, Any] = Field(default_factory=dict)
    business_rule_violations: Dict[str, str] = Field(default_factory=dict)
    valid_indices: List[int] = Field(default_factory=list)
    invalid_indices: List[int] = Field(default_factory=list)

    def add_passed(self, check_name: str) -> None:
        self.passed_checks.append(check_name)

    def add_failed(self, check_name: str, reason: str) -> None:
        self.failed_checks.append(f"{check_name}: {reason}")
        
    def add_fatal(self, check_name: str, reason: str) -> None:
        self.fatal_errors.append(f"{check_name}: {reason}")

    def add_warning(self, warning_msg: str) -> None:
        self.warnings.append(warning_msg)

    def finalize(self) -> None:
        self.is_valid = len(self.fatal_errors) == 0
