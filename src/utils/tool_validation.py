"""
Validation utilities.

General purpose validation functions for tool parameters and data.
"""

from typing import Dict, Any, List


def _validate_required_params(params: Dict[str, Any], required_keys: List[str]):
    """Validate that all required parameters are present."""
    missing = [key for key in required_keys if key not in params]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")
