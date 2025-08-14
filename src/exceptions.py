"""
Custom exceptions for UpGradeAgent.

Provides specific exception types for different categories of errors
to enable better error handling in the LangGraph agent.
"""

from typing import Optional, Dict, Any

class UpGradeAgentError(Exception):
    """Base exception for UpGradeAgent"""
    pass

class ValidationError(UpGradeAgentError):
    """Raised when input validation fails"""
    pass

class APIError(UpGradeAgentError):
    """Raised when UpGrade API operations fail"""
    def __init__(self, message: str, status_code: Optional[int] = None, api_response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.api_response = api_response

class AuthenticationError(UpGradeAgentError):
    """Raised when authentication fails"""
    pass

class ExperimentNotFoundError(APIError):
    """Raised when an experiment cannot be found"""
    pass

class InvalidExperimentStateError(ValidationError):
    """Raised when an invalid experiment state transition is attempted"""
    pass
