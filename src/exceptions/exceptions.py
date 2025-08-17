"""
Custom exception classes for the UpGrade API client.

This module defines a hierarchy of exceptions that provide granular error handling
for different types of failures when interacting with the UpGrade API.
"""

from typing import Optional, Dict, Any


class UpGradeError(Exception):
    """Base exception class for all UpGrade-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the base UpGrade exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class APIError(UpGradeError):
    """
    Exception raised for general API communication errors.
    
    This includes network issues, server errors, timeouts, and other
    communication-related problems with the UpGrade API.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        """
        Initialize API error with additional context.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code if available
            response_body: Raw response body from the API
            endpoint: The API endpoint that failed
        """
        details = {}
        if status_code is not None:
            details['status_code'] = status_code
        if response_body is not None:
            details['response_body'] = response_body
        if endpoint is not None:
            details['endpoint'] = endpoint
            
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body
        self.endpoint = endpoint


class AuthenticationError(APIError):
    """
    Exception raised for authentication and authorization failures.
    
    This occurs when the API token is invalid, expired, or missing,
    or when the user lacks permission for the requested operation.
    """
    
    def __init__(
        self, 
        message: str = "Authentication failed. Please check your API token.",
        token_hint: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize authentication error.
        
        Args:
            message: Human-readable error message
            token_hint: Hint about the token issue (e.g., "expired", "invalid")
            **kwargs: Additional arguments passed to APIError
        """
        if token_hint:
            message = f"{message} Token issue: {token_hint}"
        
        super().__init__(message, **kwargs)
        self.token_hint = token_hint
    
    @classmethod
    def invalid_token(cls, endpoint: Optional[str] = None) -> "AuthenticationError":
        """Create an AuthenticationError for invalid tokens."""
        return cls(
            message="Invalid authentication token. Please verify your UPGRADE_AUTH_TOKEN.",
            token_hint="invalid",
            endpoint=endpoint,
            status_code=401
        )
    
    @classmethod
    def expired_token(cls, endpoint: Optional[str] = None) -> "AuthenticationError":
        """Create an AuthenticationError for expired tokens."""
        return cls(
            message="Authentication token has expired. Please obtain a new token.",
            token_hint="expired",
            endpoint=endpoint,
            status_code=401
        )
    
    @classmethod
    def missing_token(cls) -> "AuthenticationError":
        """Create an AuthenticationError for missing tokens."""
        return cls(
            message="No authentication token provided. Please set UPGRADE_AUTH_TOKEN environment variable.",
            token_hint="missing"
        )


class ValidationError(UpGradeError):
    """
    Exception raised for data validation failures.
    
    This occurs when request parameters don't meet the API's validation
    requirements, such as missing required fields, invalid formats, or
    constraint violations.
    """
    
    def __init__(
        self, 
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        invalid_fields: Optional[list] = None
    ):
        """
        Initialize validation error with field-specific details.
        
        Args:
            message: Human-readable error message
            field_errors: Dictionary mapping field names to error messages
            invalid_fields: List of field names that failed validation
        """
        details = {}
        if field_errors:
            details['field_errors'] = field_errors
        if invalid_fields:
            details['invalid_fields'] = invalid_fields
            
        super().__init__(message, details)
        self.field_errors = field_errors or {}
        self.invalid_fields = invalid_fields or []
    
    @classmethod
    def missing_required_field(cls, field_name: str) -> "ValidationError":
        """Create a ValidationError for missing required fields."""
        return cls(
            message=f"Required field '{field_name}' is missing.",
            field_errors={field_name: "This field is required"},
            invalid_fields=[field_name]
        )
    
    @classmethod
    def invalid_field_value(cls, field_name: str, value: Any, expected: str) -> "ValidationError":
        """Create a ValidationError for invalid field values."""
        return cls(
            message=f"Invalid value for field '{field_name}': {value}. Expected: {expected}",
            field_errors={field_name: f"Expected {expected}, got {type(value).__name__}"},
            invalid_fields=[field_name]
        )
    
    @classmethod
    def multiple_field_errors(cls, field_errors: Dict[str, str]) -> "ValidationError":
        """Create a ValidationError for multiple field validation failures."""
        fields = list(field_errors.keys())
        return cls(
            message=f"Validation failed for fields: {', '.join(fields)}",
            field_errors=field_errors,
            invalid_fields=fields
        )


class ExperimentNotFoundError(APIError):
    """
    Exception raised when a requested experiment cannot be found.
    
    This occurs when referencing an experiment by ID or name that
    doesn't exist in the UpGrade system.
    """
    
    def __init__(
        self, 
        identifier: str,
        identifier_type: str = "ID",
        suggestions: Optional[list[str]] = None
    ):
        """
        Initialize experiment not found error.
        
        Args:
            identifier: The experiment identifier that wasn't found
            identifier_type: Type of identifier ("ID", "name", etc.)
            suggestions: List of similar experiment names/IDs as suggestions
        """
        message = f"Experiment with {identifier_type.lower()} '{identifier}' not found."
        
        if suggestions:
            message += f" Did you mean one of: {', '.join(suggestions)}"
        
        super().__init__(message, status_code=404, endpoint=None)
        # Store additional details as instance attributes
        self.identifier = identifier
        self.identifier_type = identifier_type
        self.suggestions = suggestions or []
        # Update details with our additional info
        if suggestions:
            self.details['suggestions'] = suggestions
        self.details.update({
            'identifier': identifier,
            'identifier_type': identifier_type
        })
    
    @classmethod
    def by_id(cls, experiment_id: str, suggestions: Optional[list[str]] = None) -> "ExperimentNotFoundError":
        """Create an ExperimentNotFoundError for experiment ID lookups."""
        return cls(experiment_id, "ID", suggestions)
    
    @classmethod
    def by_name(cls, experiment_name: str, suggestions: Optional[list[str]] = None) -> "ExperimentNotFoundError":
        """Create an ExperimentNotFoundError for experiment name lookups."""
        return cls(experiment_name, "name", suggestions)


class InvalidExperimentStateError(ValidationError):
    """
    Exception raised when attempting an operation on an experiment
    that's in an invalid state for that operation.
    
    For example, trying to start an already running experiment,
    or attempting to modify a deleted experiment.
    """
    
    def __init__(
        self, 
        experiment_id: str,
        current_state: str,
        required_states: list,
        operation: str
    ):
        """
        Initialize invalid experiment state error.
        
        Args:
            experiment_id: ID of the experiment
            current_state: Current state of the experiment
            required_states: List of valid states for the operation
            operation: The operation that was attempted
        """
        valid_states_str = "', '".join(required_states)
        message = (
            f"Cannot {operation} experiment '{experiment_id}'. "
            f"Current state is '{current_state}', but operation requires "
            f"state to be one of: '{valid_states_str}'"
        )
        
        super().__init__(message)
        # Store additional details as instance attributes  
        self.experiment_id = experiment_id
        self.current_state = current_state
        self.required_states = required_states
        self.operation = operation
        # Update details with our additional info
        self.details.update({
            'experiment_id': experiment_id,
            'current_state': current_state,
            'required_states': required_states,
            'operation': operation
        })
    
    @classmethod
    def cannot_start_running_experiment(cls, experiment_id: str) -> "InvalidExperimentStateError":
        """Create error for trying to start an already running experiment."""
        return cls(
            experiment_id=experiment_id,
            current_state="enrolling",
            required_states=["inactive", "cancelled"],
            operation="start"
        )
    
    @classmethod
    def cannot_modify_deleted_experiment(cls, experiment_id: str, operation: str) -> "InvalidExperimentStateError":
        """Create error for trying to modify a deleted experiment."""
        return cls(
            experiment_id=experiment_id,
            current_state="deleted",
            required_states=["inactive", "enrolling", "enrollmentComplete", "cancelled"],
            operation=operation
        )
    
    @classmethod
    def cannot_delete_running_experiment(cls, experiment_id: str) -> "InvalidExperimentStateError":
        """Create error for trying to delete a running experiment."""
        return cls(
            experiment_id=experiment_id,
            current_state="enrolling",
            required_states=["inactive", "cancelled", "enrollmentComplete"],
            operation="delete"
        )


# Convenience function for creating appropriate exception from API response
def create_api_exception(
    status_code: int,
    response_body: str,
    endpoint: Optional[str] = None,
    message: Optional[str] = None
) -> UpGradeError:
    """
    Create the appropriate exception based on HTTP status code and response.
    
    Args:
        status_code: HTTP status code from the API response
        response_body: Raw response body from the API
        endpoint: The API endpoint that failed
        message: Optional custom message
    
    Returns:
        Appropriate exception instance based on the status code
    """
    if not message:
        message = f"API request failed with status {status_code}"
    
    if status_code == 401:
        return AuthenticationError.invalid_token(endpoint)
    elif status_code == 403:
        return AuthenticationError(
            "Access forbidden. You may not have permission for this operation.",
            endpoint=endpoint,
            status_code=status_code,
            response_body=response_body
        )
    elif status_code == 404:
        return APIError(
            "Resource not found. Please check the URL and parameters.",
            status_code=status_code,
            response_body=response_body,
            endpoint=endpoint
        )
    elif status_code == 422:
        return ValidationError(
            "Request validation failed. Please check your parameters."
        )
    elif 400 <= status_code < 500:
        return ValidationError(
            f"Client error ({status_code}): {message}"
        )
    elif 500 <= status_code < 600:
        return APIError(
            f"Server error ({status_code}): The UpGrade service is experiencing issues.",
            status_code=status_code,
            response_body=response_body,
            endpoint=endpoint
        )
    else:
        return APIError(
            message,
            status_code=status_code,
            response_body=response_body,
            endpoint=endpoint
        )
