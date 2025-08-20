"""
Simulation endpoints for the UpGrade API.

Simple wrapper functions that directly call API endpoints listed in README.md.
These functions return raw API responses and match tool function names from tools.md.
"""

from typing import Dict, Any, Union, List
from src.api.client import get_client
from src.models.constants import INIT_ENDPOINT, ASSIGN_ENDPOINT, MARK_ENDPOINT
from src.models.types import (
    InitExperimentUserRequest,
    ExperimentAssignmentRequest, 
    MarkExperimentRequest
)


def _to_dict(data: Union[Dict[str, Any], InitExperimentUserRequest, ExperimentAssignmentRequest, MarkExperimentRequest]) -> Dict[str, Any]:
    """Convert typed data to dictionary format for API calls."""
    # TypedDict is a dict at runtime, so we can safely cast it
    return dict(data)


async def init_experiment_user(user_id: str, init_data: Union[InitExperimentUserRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """
    POST /v6/init - Initialize users with group memberships.
    
    Registers users who could be eligible for experiments and assigns 
    group memberships (e.g., grade level, class, teacher) and working groups.
    
    Args:
        user_id: The user ID to register (sent in User-Id header)
        init_data: User initialization data containing group and workingGroup
        
    Returns:
        User object with assigned groups and working group
        
    Raises:
        APIError: For network errors or server issues
    """
    client = get_client()
    return await client.post(INIT_ENDPOINT, data=_to_dict(init_data), user_id=user_id)


async def get_decision_point_assignments(user_id: str, assignment_data: Union[ExperimentAssignmentRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """
    POST /v6/assign - Get experiment condition assignments for users.
    
    Retrieves experiment conditions when a user reaches a decision point.
    Returns assigned conditions for every active experiment the user is eligible for.
    
    Args:
        user_id: The user ID requesting assignments (sent in User-Id header)
        assignment_data: Assignment request data containing context and optional filters
        
    Returns:
        Dict containing 'data' key with list of experiment assignments
        
    Raises:
        APIError: For network errors or server issues
    """
    client = get_client()
    response = await client.post(ASSIGN_ENDPOINT, data=_to_dict(assignment_data), user_id=user_id)
    # Wrap the list response in a consistent dictionary format
    return {"data": response}


async def mark_decision_point(user_id: str, mark_data: Union[MarkExperimentRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """
    POST /v6/mark - Record decision point visits.
    
    Records that a user has reached a decision point and received a condition.
    Tracks whether the condition was successfully applied and maintains enrollment data.
    
    Args:
        user_id: The user ID marking the decision point (sent in User-Id header)
        mark_data: Mark request data containing decision point info and status
        
    Returns:
        Confirmation object with decision point details
        
    Raises:
        APIError: For network errors or server issues
    """
    client = get_client()
    return await client.post(MARK_ENDPOINT, data=_to_dict(mark_data), user_id=user_id)