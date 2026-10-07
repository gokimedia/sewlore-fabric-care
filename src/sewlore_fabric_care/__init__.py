"""Local fabric-care CSV validation; original software by Sewlore.

Use validate_submission for the bounded anonymous-record policy. The generic
validate_csv API deliberately has different limits and allows free-text notes.
"""
from .validator import (
    BLANK_CSV, INPUT_COLUMNS, OUTPUT_COLUMNS, ERROR_COLUMNS,
    calculate_changes, convert_length, export_errors, export_validated,
    validate_csv,
)
from .input_policy import CARE_CODES, MAX_BYTES, MAX_RECORDS, validate_submission

__version__ = "0.1.0"
__all__ = [
    "BLANK_CSV", "INPUT_COLUMNS", "OUTPUT_COLUMNS", "ERROR_COLUMNS",
    "CARE_CODES", "MAX_BYTES", "MAX_RECORDS", "calculate_changes",
    "convert_length", "export_errors", "export_validated", "validate_csv",
    "validate_submission",
]
