"""
System endpoints for the UpGrade API.

Simple wrapper functions that directly call API endpoints listed in README.md.
These functions return raw API responses and match tool function names from tools.md.
"""

from typing import Dict, Any
from src.api.client import get_client


async def check_upgrade_health() -> Dict[str, Any]:
    """
    GET / - Health check and version info.
    
    This endpoint does not require authentication and returns basic service information
    including name, version, and description. Used for health monitoring and version checking.
    
    Returns:
        Dict containing 'name', 'version', and 'description' fields
        Example: {"name": "A/B Testing Backend", "version": "6.2.0", "description": "Backend for A/B Testing Project"}
        
    Raises:
        APIError: For network errors or server issues
    """
    client = get_client()
    return await client.get("/", include_auth=False)


async def get_context_metadata() -> Dict[str, Any]:
    """
    GET /experiments/contextMetaData - Get available app contexts and their supported values.
    
    Returns metadata for all available app contexts, including supported conditions,
    group types, experiment IDs (targets), and experiment points (sites) for each context.
    This information is essential for validating experiment creation parameters.
    
    Returns:
        Dict with 'contextMetadata' field containing context definitions
        Example: {"contextMetadata": {"mathstream": {"CONDITIONS": [...], "GROUP_TYPES": [...], ...}}}
        
    Raises:
        APIError: For network errors or server issues
        AuthenticationError: If authentication token is invalid or missing
    """
    client = get_client()
    return await client.get("/experiments/contextMetaData")
