"""
Experiments endpoints for the UpGrade API.

Simple wrapper functions that directly call API endpoints listed in README.md.
These functions return raw API responses and match tool function names from tools.md.
"""

from typing import Dict, Any
from src.api.client import get_client


async def get_experiment_names() -> Dict[str, Any]:
    """
    GET /experiments/names - Get all experiment names and IDs.
    
    Returns:
        List of dicts with 'id' and 'name' fields
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
    """
    client = get_client()
    return await client.get("/experiments/names")


async def get_all_experiments() -> Dict[str, Any]:
    """
    GET /experiments - Get all experiments with full configuration.
    
    Returns:
        List of complete experiment objects with all fields
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
    """
    client = get_client()
    return await client.get("/experiments")


async def get_experiment_details(experiment_id: str) -> Dict[str, Any]:
    """
    GET /experiments/single/<experiment_id> - Get detailed experiment configuration.
    
    Args:
        experiment_id: UUID of the experiment to retrieve
        
    Returns:
        Complete experiment object with all configuration details
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
        ExperimentNotFoundError: If experiment with given ID doesn't exist
    """
    client = get_client()
    return await client.get(f"/experiments/single/{experiment_id}")


async def create_experiment(experiment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    POST /experiments - Create a new experiment.
    
    Args:
        experiment_data: Complete experiment configuration
        
    Returns:
        Created experiment object with generated IDs and timestamps
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
        ValidationError: If experiment configuration is invalid
    """
    client = get_client()
    return await client.post("/experiments", data=experiment_data)


async def update_experiment(experiment_id: str, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    PUT /experiments/<experiment_id> - Update experiment configuration.
    
    Args:
        experiment_id: UUID of the experiment to update
        experiment_data: Experiment configuration data (can be partial)
        
    Returns:
        Updated experiment object with new configuration
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
        ExperimentNotFoundError: If experiment with given ID doesn't exist
    """
    client = get_client()
    return await client.put(f"/experiments/{experiment_id}", data=experiment_data)


async def update_experiment_status(experiment_id: str, state: str) -> Dict[str, Any]:
    """
    POST /experiments/state - Update experiment status/state.
    
    Args:
        experiment_id: UUID of the experiment to update
        state: New state for the experiment (e.g., 'inactive', 'enrolling')
        
    Returns:
        Updated experiment object with new state and state change logs
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
        ExperimentNotFoundError: If experiment with given ID doesn't exist
    """
    state_request: Dict[str, Any] = {
        "experimentId": experiment_id,
        "state": state
    }
    
    client = get_client()
    return await client.post("/experiments/state", data=state_request)


async def delete_experiment(experiment_id: str) -> Dict[str, Any]:
    """
    DELETE /experiments/<experiment_id> - Delete an experiment.
    
    Args:
        experiment_id: UUID of the experiment to delete
        
    Returns:
        API response (format depends on implementation)
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
        ExperimentNotFoundError: If experiment with given ID doesn't exist
    """
    client = get_client()
    return await client.delete(f"/experiments/{experiment_id}")