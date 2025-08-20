"""
Experiment data transformation utilities.

Functions for transforming raw API experiment data to simplified tool formats.
"""

from typing import Dict, Any, List, Optional

from src.models.tool_types import (
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
        "context": experiment.get("context", ["unknown"])[0],
        "type": ExperimentType(experiment.get("type", "Simple")),
        "assignment_unit": AssignmentUnit(experiment.get("assignmentUnit", "individual")),
        "group_type": experiment.get("group", None),
        "consistency_rule": ConsistencyRule(experiment.get("consistencyRule", "individual")),
        "post_experiment_rule": post_experiment_rule,
        "decision_points": decision_points,
        "conditions": conditions,
        "filter_mode": FilterMode(experiment.get("filterMode", "excludeAll")),
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
