"""
UpGrade API client exception classes.

This package provides a comprehensive set of exception classes for handling
various error conditions when interacting with the UpGrade API.
"""

from .exceptions import (
    UpGradeError,
    APIError,
    AuthenticationError,
    ValidationError,
    ExperimentNotFoundError,
    InvalidExperimentStateError,
    create_api_exception,
)

__all__ = [
    "UpGradeError",
    "APIError", 
    "AuthenticationError",
    "ValidationError",
    "ExperimentNotFoundError",
    "InvalidExperimentStateError",
    "create_api_exception",
]
