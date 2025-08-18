"""
Information Gatherer API tools.

These tools handle API data gathering and store results in static variables
or gathered_info. They use the existing endpoint functions from src/api/endpoints/.
"""

from langchain.tools import tool
from typing import Dict, Any, List, Optional

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
    SimplifiedExperiment,
    DecisionPoint,
    Condition,
    ToolPostExperimentRule,
    InclusionExclusionGroup
)
from src.models.enums import (
    ExperimentState,
    ExperimentType,
    AssignmentUnit,
    ConsistencyRule,
    FilterMode,
    PostExperimentRule
)


@tool
@register_gatherer_tool("check_upgrade_health")
@auto_store("upgrade_health")
@handle_errors()
async def check_upgrade_health() -> Dict[str, Any]:
    """
    Check UpGrade service health and version information.
    
    Returns:
        Dict with keys: name, version, description
    """
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
    """
    Get available app contexts and their supported values.
    
    Returns:
        Dict mapping context names to their metadata with lowercase keys
    """
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
    """
    Get all experiment names and IDs.
    
    Returns:
        List of dicts with keys: id, name
    """
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
    """
    Get all experiments with simplified format for tool responses.
    
    Returns:
        List of simplified experiment dicts
    """
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
        
    Returns:
        Simplified experiment dict
    """
    if not experiment_id or not experiment_id.strip():
        raise ValueError("experiment_id is required and cannot be empty")
        
    response = await api_get_experiment_details(experiment_id)
    return _transform_experiment_data(response)


def _transform_experiment_data(experiment: Dict[str, Any]) -> SimplifiedExperiment:
    """Transform raw experiment data to simplified format for tools."""
    
    # Extract decision points from partitions
    decision_points: List[DecisionPoint] = []
    if "partitions" in experiment:
        for partition in experiment["partitions"]:
            decision_points.append(DecisionPoint({
                "site": partition.get("site", ""),
                "target": partition.get("target", ""),
                "exclude_if_reached": partition.get("excludeIfReached", False)
            }))
    
    # Extract conditions
    conditions: List[Condition] = []
    if "conditions" in experiment:
        for condition in experiment["conditions"]:
            conditions.append(Condition({
                "code": condition.get("conditionCode", ""),
                "weight": condition.get("assignmentWeight", 50)
            }))
    
    # Extract post experiment rule
    revert_to_id = experiment.get("revertTo")
    condition_code: Optional[str] = None
    
    # If revertTo is set, find the corresponding condition code
    if revert_to_id:
        # Look through conditions to find the one with matching ID
        for condition in experiment.get("conditions", []):
            if condition.get("id") == revert_to_id:
                condition_code = condition.get("conditionCode")
                break
    
    post_experiment_rule: ToolPostExperimentRule = {
        "rule": PostExperimentRule(experiment.get("postExperimentRule", "continue")),
        "condition_code": condition_code
    }
    
    # Build the simplified experiment with proper typing
    simplified: SimplifiedExperiment = {
        "created_at": experiment.get("createdAt", ""),
        "updated_at": experiment.get("updatedAt", ""),
        "id": experiment.get("id", ""),
        "status": ExperimentState(experiment.get("state", "inactive")),
        "name": experiment.get("name", ""),
        "description": experiment.get("description", ""),
        "tags": experiment.get("tags", []),
        "context": experiment.get("context", ["unknown"])[0] if experiment.get("context") else "unknown",
        "type": ExperimentType(experiment.get("type", "Simple")),
        "assignment_unit": AssignmentUnit(experiment.get("assignmentUnit", "individual")),
        "group_type": experiment.get("group", "None") if experiment.get("group") else "None",
        "consistency_rule": ConsistencyRule(experiment.get("consistencyRule", "individual")),
        "post_experiment_rule": post_experiment_rule,
        "decision_points": decision_points,
        "conditions": conditions,
        "filter_mode": FilterMode(experiment.get("filterMode", "includeAll")),
        "inclusion_users": [],
        "inclusion_groups": [],
        "exclusion_users": [],
        "exclusion_groups": []
    }
    
    # Extract inclusion/exclusion data from segments
    _extract_segment_data(experiment, simplified)
    
    return simplified


def _extract_segment_data(experiment: Dict[str, Any], simplified: SimplifiedExperiment) -> None:
    """Extract inclusion/exclusion user and group data from experiment segments."""
    # Extract inclusion data
    _extract_inclusion_data(experiment, simplified)
    
    # Extract exclusion data
    _extract_exclusion_data(experiment, simplified)


def _extract_inclusion_data(experiment: Dict[str, Any], simplified: SimplifiedExperiment) -> None:
    """Extract inclusion users and groups from experiment segment."""
    inclusion_segment = experiment.get("experimentSegmentInclusion")
    if inclusion_segment is not None:
        segment = inclusion_segment.get("segment", {})
        
        # Extract inclusion users
        _extract_segment_users(segment, simplified["inclusion_users"])
        
        # Extract inclusion groups
        _extract_segment_groups(segment, simplified["inclusion_groups"])


def _extract_exclusion_data(experiment: Dict[str, Any], simplified: SimplifiedExperiment) -> None:
    """Extract exclusion users and groups from experiment segment."""
    exclusion_segment = experiment.get("experimentSegmentExclusion")
    if exclusion_segment is not None:
        segment = exclusion_segment.get("segment", {})
        
        # Extract exclusion users
        _extract_segment_users(segment, simplified["exclusion_users"])
        
        # Extract exclusion groups
        _extract_segment_groups(segment, simplified["exclusion_groups"])


def _extract_segment_users(segment: Dict[str, Any], user_list: List[str]) -> None:
    """Extract user IDs from a segment."""
    individuals = segment.get("individualForSegment", [])
    for individual in individuals:
        user_id = individual.get("userId", "")
        if user_id:
            user_list.append(user_id)


def _extract_segment_groups(segment: Dict[str, Any], group_list: List[InclusionExclusionGroup]) -> None:
    """Extract group data from a segment."""
    groups = segment.get("groupForSegment", [])
    for group in groups:
        group_id = group.get("groupId", "")
        group_type = group.get("type", "")
        if group_id and group_type:
            group_list.append(InclusionExclusionGroup({
                "type": group_type,
                "group_id": group_id
            }))
