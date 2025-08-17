"""
Information Gatherer utility tools.

These tools provide schema information, documentation, and static data
that help guide parameter collection and user interactions.
"""

from langchain.tools import tool
from typing import Dict, Any, List

from src.tools.decorators import auto_store
from src.tools.registry import register_gatherer_tool


@tool
@register_gatherer_tool("get_core_terms")
@auto_store("core_terms")
def get_core_terms() -> Dict[str, str]:
    """Get basic A/B testing and UpGrade terminology."""
    return {
        "app_context": "Indicates where the experiment will run (e.g., 'assign-prog', 'mastering'). Available options are read from the context metadata.",
        "experiment": "A controlled test comparing different versions of content or features to determine which performs better.",
        "condition": "A specific version or variant in an experiment (e.g., 'control', 'treatment', 'condition-a').",
        "assignment": "The process of giving users specific conditions when they reach decision points.",
        "decision_point": "A location in the app where experiment assignment occurs, defined by site and target.",
        "enrollment": "The process of users being included in an experiment when status is 'enrolling'.",
        "consistency_rule": "Rules ensuring users get the same assignment across sessions (individual or group).",
        "unit_of_assignment": "Specifies the level at which conditions are assigned (individual or group).",
        "post_experiment_rule": "What happens to participants after experiment ends (continue or assign to specific condition).",
        "partition": "Another term for decision point - where assignments happen in the application."
    }


@tool
@register_gatherer_tool("get_assignment_terms")
@auto_store("assignment_terms")
def get_assignment_terms() -> Dict[str, str]:
    """Get assignment rules, consistency, and algorithm information."""
    return {
        "individual_assignment": "Each user gets independently assigned to conditions based on random assignment.",
        "group_assignment": "Users are assigned based on group membership (e.g., school, class, teacher).",
        "individual_consistency": "Same user always gets same condition throughout experiment duration.",
        "group_consistency": "Users in same working group always get same condition.",
        "random_algorithm": "Conditions assigned using weighted randomization based on condition weights.",
        "stratified_sampling": "Assignment considers user characteristics for balance (not supported in MVP).",
        "post_rule_continue": "After experiment ends, users keep their current assigned conditions.",
        "post_rule_assign": "After experiment ends, all users get assigned to a specific condition.",
        "enrolling_status": "Experiment is actively running and assigning conditions to users.",
        "inactive_status": "Experiment is not running, all users get default condition.",
        "enrollment_complete": "Experiment has stopped enrolling new users, post-experiment rule applies."
    }


@tool
@register_gatherer_tool("get_create_experiment_schema")
@auto_store("create_experiment_schema")
def get_create_experiment_schema() -> Dict[str, Any]:
    """Get schema and validation rules for experiment creation."""
    return {
        "required_parameters": {
            "name": "string - Experiment name (must be unique across all experiments)",
            "context": "array - App contexts where experiment runs (e.g., ['assign-prog'])",
            "description": "string - Clear description of what the experiment tests",
            "type": "string - Experiment type: 'simple' (MVP only supports simple experiments)",
            "assignmentUnit": "string - 'individual' or 'group' (who gets assigned conditions)",
            "consistencyRule": "string - 'individual' or 'group' (consistency during experiment)",
            "assignmentAlgorithm": "string - 'random' (MVP only supports random)",
            "conditions": "array - Condition objects with 'conditionCode' and 'assignmentWeight'",
            "partitions": "array - Decision points with 'site', 'target', and 'excludeIfReached'"
        },
        "optional_parameters": {
            "tags": "array - Tags for organization and filtering (e.g., ['math', 'pilot'])",
            "group": "string - Group identifier when using group assignment",
            "enrollmentCompleteCondition": "object - When to stop enrollment (userCount, groupCount)",
            "postExperimentRule": "string - 'continue' or 'assign' (what happens after experiment)",
            "revertTo": "string - Condition code when postExperimentRule is 'assign'",
            "filterMode": "string - 'includeAll' or 'excludeAll' (default: includeAll)",
            "startOn": "string - ISO datetime when experiment should start",
            "endOn": "string - ISO datetime when experiment should end"
        },
        "validation_rules": {
            "name": "Must be unique, 1-255 characters, no special characters except spaces and hyphens",
            "context": "Must exist in available contexts from context metadata",
            "conditions": "Must have at least 1 condition, assignment weights should sum to 100",
            "partitions": "Must have at least 1 decision point, site/target must exist in context",
            "assignmentUnit": "If 'group', must specify group type in 'group' parameter",
            "consistency_rule": "Group consistency only available with group assignment unit"
        },
        "examples": {
            "simple_experiment": {
                "name": "Math Hints Test",
                "context": ["assign-prog"],
                "description": "Testing effectiveness of math hints",
                "conditions": [
                    {"conditionCode": "control", "assignmentWeight": 50},
                    {"conditionCode": "treatment", "assignmentWeight": 50}
                ],
                "partitions": [
                    {"site": "CurriculumSequence", "target": "math_problem", "excludeIfReached": False}
                ]
            }
        }
    }


@tool
@register_gatherer_tool("get_update_experiment_schema")
@auto_store("update_experiment_schema")
def get_update_experiment_schema() -> Dict[str, Any]:
    """Get schema and validation rules for experiment updates."""
    return {
        "required_parameters": {
            "experiment_id": "string - UUID of experiment to update"
        },
        "optional_parameters": {
            "name": "string - New experiment name",
            "description": "string - New description", 
            "tags": "array - New tags",
            "conditions": "array - Updated condition objects",
            "partitions": "array - Updated decision points",
            "enrollmentCompleteCondition": "object - Updated enrollment rules",
            "postExperimentRule": "string - Updated post-experiment behavior",
            "revertTo": "string - Updated revert condition"
        },
        "validation_rules": {
            "experiment_id": "Must be valid UUID of existing experiment",
            "name": "If provided, must be unique",
            "conditions": "If provided, weights must sum to 100",
            "state_restrictions": "Some fields cannot be changed if experiment is enrolling"
        }
    }


@tool
@register_gatherer_tool("get_update_experiment_status_schema")
@auto_store("update_experiment_status_schema")
def get_update_experiment_status_schema() -> Dict[str, Any]:
    """Get schema for experiment status updates."""
    return {
        "required_parameters": {
            "experiment_id": "string - UUID of experiment to update",
            "status": "string - New status: 'inactive', 'enrolling', 'enrollmentComplete', or 'cancelled'"
        },
        "valid_transitions": {
            "inactive": ["enrolling", "cancelled"],
            "enrolling": ["enrollmentComplete", "cancelled"],
            "enrollmentComplete": ["cancelled"],
            "cancelled": []  # Terminal state - no transitions allowed
        },
        "status_meanings": {
            "inactive": "Experiment is not running, all users get default condition",
            "enrolling": "Experiment is actively assigning conditions to users",
            "enrollmentComplete": "Stopped enrolling, post-experiment rule applies",
            "cancelled": "Experiment permanently stopped, no longer accessible"
        },
        "validation_rules": {
            "experiment_id": "Must be valid UUID of existing experiment",
            "status": "Must be valid status value and allowed transition from current state"
        },
        "examples": {
            "start_experiment": {"experiment_id": "uuid-here", "status": "enrolling"},
            "stop_experiment": {"experiment_id": "uuid-here", "status": "enrollmentComplete"},
            "cancel_experiment": {"experiment_id": "uuid-here", "status": "cancelled"}
        }
    }


@tool
@register_gatherer_tool("get_delete_experiment_schema")
@auto_store("delete_experiment_schema")
def get_delete_experiment_schema() -> Dict[str, Any]:
    """Get schema for experiment deletion."""
    return {
        "required_parameters": {
            "experiment_id": "string - UUID of experiment to delete"
        },
        "validation_rules": {
            "experiment_id": "Must be valid UUID of existing experiment",
            "state_restrictions": "Cannot delete experiments that are currently enrolling"
        },
        "confirmation_required": True,
        "irreversible": True
    }


@tool
@register_gatherer_tool("get_init_experiment_user_schema")
@auto_store("init_experiment_user_schema")
def get_init_experiment_user_schema() -> Dict[str, Any]:
    """Get schema for user initialization parameters."""
    return {
        "required_parameters": {
            "user_id": "string - Unique identifier for the user"
        },
        "optional_parameters": {
            "group": "object - Group memberships {groupType: [groupIds]}",
            "workingGroup": "object - Working group assignments {groupType: groupId}"
        },
        "validation_rules": {
            "user_id": "Must be non-empty string",
            "group": "Keys must match available group types for context",
            "workingGroup": "Keys must match available group types for context"
        }
    }


@tool
@register_gatherer_tool("get_get_decision_point_assignments_schema")
@auto_store("get_decision_point_assignments_schema")
def get_get_decision_point_assignments_schema() -> Dict[str, Any]:
    """Get schema for decision point assignment requests."""
    return {
        "required_parameters": {
            "user_id": "string - Unique identifier for the user",
            "context": "string - App context for assignments"
        },
        "optional_parameters": {
            "site": "string - Specific site to get assignments for",
            "target": "string - Specific target to get assignments for"
        },
        "validation_rules": {
            "user_id": "Must be non-empty string",
            "context": "Must exist in available contexts",
            "site": "If provided, must exist in context metadata",
            "target": "If provided, must exist in context metadata"
        }
    }


@tool
@register_gatherer_tool("get_mark_decision_point_schema")
@auto_store("mark_decision_point_schema")
def get_mark_decision_point_schema() -> Dict[str, Any]:
    """Get schema for marking decision point visits."""
    return {
        "required_parameters": {
            "user_id": "string - Unique identifier for the user",
            "site": "string - Decision point site",
            "target": "string - Decision point target"
        },
        "optional_parameters": {
            "assigned_condition": "object - Condition assignment details",
            "status": "string - Status of the decision point visit"
        },
        "validation_rules": {
            "user_id": "Must be non-empty string",
            "site": "Must exist in context metadata",
            "target": "Must exist in context metadata",
            "status": "Must be valid MarkedDecisionPointStatus enum value"
        }
    }


@tool
@register_gatherer_tool("get_available_contexts")
@auto_store("available_contexts")
def get_available_contexts() -> List[str]:
    """Get list of available context names."""
    # This will use context_metadata when available
    from src.tools.decorators import _state_ref
    
    if _state_ref and 'context_metadata' in _state_ref:
        return list(_state_ref['context_metadata'].keys())
    
    # Fallback to common contexts if metadata not loaded
    return ["assign-prog", "mastering", "other"]


@tool
@register_gatherer_tool("get_conditions_for_context")
def get_conditions_for_context(context: str) -> List[str]:
    """Get available conditions for a specific context."""
    from src.tools.decorators import _state_ref
    
    if not context or not context.strip():
        raise ValueError("context is required and cannot be empty")
    
    # Check if context metadata is available
    if _state_ref and 'context_metadata' in _state_ref:
        context_metadata = _state_ref['context_metadata']
        
        # Validate context exists
        if context not in context_metadata:
            available_contexts = list(context_metadata.keys())
            raise ValueError(f"Context '{context}' not found. Available contexts: {available_contexts}")
        
        context_data = context_metadata.get(context, {})
        conditions = context_data.get('conditions', [])
    else:
        # No metadata available
        raise RuntimeError("Context metadata not available. Call get_context_metadata() first.")
    
    # Auto-store with dynamic key
    if _state_ref:
        if "gathered_info" not in _state_ref:
            _state_ref["gathered_info"] = {}
        _state_ref["gathered_info"][f"conditions_for_{context}"] = conditions
    
    return conditions


@tool
@register_gatherer_tool("get_decision_points_for_context")
def get_decision_points_for_context(context: str) -> List[Dict[str, str]]:
    """Get available decision points (sites/targets) for a specific context."""
    from src.tools.decorators import _state_ref
    
    if not context or not context.strip():
        raise ValueError("context is required and cannot be empty")
    
    if _state_ref and 'context_metadata' in _state_ref:
        context_metadata = _state_ref['context_metadata']
        
        # Validate context exists
        if context not in context_metadata:
            available_contexts = list(context_metadata.keys())
            raise ValueError(f"Context '{context}' not found. Available contexts: {available_contexts}")
            
        context_data = context_metadata.get(context, {})
        sites = context_data.get('sites', [])
        targets = context_data.get('targets', [])
        
        # Combine sites and targets into decision points
        decision_points = []
        for site in sites:
            for target in targets:
                decision_points.append({"site": site, "target": target})
    else:
        # No metadata available
        raise RuntimeError("Context metadata not available. Call get_context_metadata() first.")
    
    # Auto-store with dynamic key
    if _state_ref:
        if "gathered_info" not in _state_ref:
            _state_ref["gathered_info"] = {}
        _state_ref["gathered_info"][f"decision_points_for_{context}"] = decision_points
    
    return decision_points


@tool
@register_gatherer_tool("get_group_types_for_context")
def get_group_types_for_context(context: str) -> List[str]:
    """Get available group types for a specific context."""
    from src.tools.decorators import _state_ref
    
    if not context or not context.strip():
        raise ValueError("context is required and cannot be empty")
    
    if _state_ref and 'context_metadata' in _state_ref:
        context_metadata = _state_ref['context_metadata']
        
        # Validate context exists
        if context not in context_metadata:
            available_contexts = list(context_metadata.keys())
            raise ValueError(f"Context '{context}' not found. Available contexts: {available_contexts}")
            
        context_data = context_metadata.get(context, {})
        group_types = context_data.get('group_types', [])
    else:
        # No metadata available
        raise RuntimeError("Context metadata not available. Call get_context_metadata() first.")
    
    # Auto-store with dynamic key
    if _state_ref:
        if "gathered_info" not in _state_ref:
            _state_ref["gathered_info"] = {}
        _state_ref["gathered_info"][f"group_types_for_{context}"] = group_types
    
    return group_types
