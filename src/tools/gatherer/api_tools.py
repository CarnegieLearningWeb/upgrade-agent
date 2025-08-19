"""
Information Gatherer API tools.

These tools handle API data gathering and store results in static variables
or gathered_info. They use the existing endpoint functions from src/api/endpoints/.
"""

from langchain.tools import tool
from typing import Dict, Any, List

from src.tools.decorators import auto_store, auto_store_static, handle_errors
from src.tools.registry import register_gatherer_tool
from src.api.endpoints.system import (
    check_upgrade_health as api_check_upgrade_health, 
    get_context_metadata as api_get_context_metadata
)
from src.api.endpoints.experiments import (
    get_experiment_names as api_get_experiment_names,
    get_all_experiments as api_get_all_experiments, 
    get_experiment_details as api_get_experiment_details
)
from src.models.tool_types import (
    ToolHealthResponse,
    ToolContextMetadata,
    ToolExperimentName,
    SimplifiedExperiment
)
from src.utils.experiment_transforms import _transform_experiment_data


@tool
@register_gatherer_tool("check_upgrade_health")
@auto_store("upgrade_health")
@handle_errors()
async def check_upgrade_health() -> ToolHealthResponse:
    """Check UpGrade service health and version information."""
    response = await api_check_upgrade_health()
    return {
        "name": response.get("name", "UpGrade"),
        "version": response.get("version", "unknown"),
        "description": response.get("description", "A/B Testing Platform")
    }


@tool
@register_gatherer_tool("get_context_metadata")
@auto_store_static("context_metadata")
@handle_errors("api")
async def get_context_metadata() -> Dict[str, ToolContextMetadata]:
    """Get available app contexts and their supported values."""
    response = await api_get_context_metadata()
    context_data = {}
    
    # Transform API response to tool-friendly format
    if 'contextMetadata' in response:
        for context_name, metadata in response['contextMetadata'].items():
            context_data[context_name] = {
                "conditions": metadata.get("CONDITIONS", []),
                "group_types": metadata.get("GROUP_TYPES", []),
                "sites": metadata.get("EXP_IDS", []),  # EXP_IDS are site names
                "targets": metadata.get("EXP_POINTS", [])  # EXP_POINTS are target names
            }
    
    return context_data


@tool
@register_gatherer_tool("get_experiment_names")
@auto_store_static("experiment_names")
@handle_errors("api")
async def get_experiment_names() -> List[ToolExperimentName]:
    """Get all experiment names and IDs."""
    response = await api_get_experiment_names()
    
    # Handle the case where response might be a wrapper dict or direct list
    experiment_list = response if isinstance(response, list) else response.get("data", response)
    
    return [
        {"id": exp.get("id", ""), "name": exp.get("name", "")} 
        for exp in experiment_list
        if isinstance(exp, dict)
    ]


@tool
@register_gatherer_tool("get_all_experiments")
@auto_store_static("all_experiments")
@handle_errors("api")
async def get_all_experiments() -> List[SimplifiedExperiment]:
    """Get all experiments with simplified format for tool responses."""
    response = await api_get_all_experiments()
    
    # Handle the case where response might be a wrapper dict or direct list
    experiment_list = response if isinstance(response, list) else response.get("data", response)
    
    return [
        _transform_experiment_data(exp) 
        for exp in experiment_list
        if isinstance(exp, dict)
    ]


@tool
@register_gatherer_tool("get_experiment_details")
@auto_store("experiment_details")
@handle_errors("api")
async def get_experiment_details(experiment_id: str) -> SimplifiedExperiment:
    """
    Get detailed experiment configuration.
    
    Args:
        experiment_id: UUID of the experiment
    """
    if not experiment_id or not experiment_id.strip():
        raise ValueError("experiment_id is required and cannot be empty")
        
    response = await api_get_experiment_details(experiment_id)
    return _transform_experiment_data(response)
