"""
Information Gatherer state management tools.

These tools manage the state variables and action parameters for the
Information Gatherer node.
"""

from langchain.tools import tool
from typing import Dict, Any, List, Literal

from src.tools.registry import register_gatherer_tool


@tool
@register_gatherer_tool("set_action_needed")
def set_action_needed(
    action: Literal[
        "create_experiment", 
        "update_experiment", 
        "delete_experiment",
        "update_experiment_status", 
        "init_experiment_user", 
        "get_decision_point_assignments", 
        "mark_decision_point",
        "visit_decision_point"
    ]
) -> str:
    """
    Set what action is needed for Tool Executor.
    
    Args:
        action: The action that needs to be performed
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        _state_ref['action_needed'] = action
    
    return f"Action set to '{action}'."


@tool
@register_gatherer_tool("set_action_params")
def set_action_params(action_params: Dict[str, Any]) -> str:
    """
    Set parameters for the action (only non-default values).
    
    Args:
        action_params: Dictionary of parameters for the action
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        _state_ref['action_params'] = action_params
    
    param_count = len(action_params)
    return f"Set {param_count} action parameters: {list(action_params.keys())}"


@tool
@register_gatherer_tool("set_missing_params")
def set_missing_params(missing_params: List[str]) -> str:
    """
    Set what parameters are still needed from user.
    
    Args:
        missing_params: List of parameter names that are still needed
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        _state_ref['missing_params'] = missing_params
    
    if missing_params:
        return f"Still need {len(missing_params)} parameters: {', '.join(missing_params)}"
    else:
        return "All required parameters have been collected"


@tool
@register_gatherer_tool("update_action_params")
def update_action_params(key: str, value: Any) -> str:
    """
    Add or update a specific parameter (for progressive gathering).
    
    Args:
        key: Parameter name to update
        value: New value for the parameter
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        if 'action_params' not in _state_ref:
            _state_ref['action_params'] = {}
        _state_ref['action_params'][key] = value
    
    return f"Updated parameter '{key}' with value: {value}"


@tool
@register_gatherer_tool("add_error")
def add_error(
    error_type: Literal["api", "auth", "validation", "not_found", "unknown"], 
    message: str
) -> str:
    """
    Add an error message when operations fail.
    
    Args:
        error_type: Type of error (api, auth, validation, not_found, unknown)
        message: Error message description
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        if 'errors' not in _state_ref:
            _state_ref['errors'] = {}
        _state_ref['errors'][error_type] = message
    
    return f"Error recorded: {error_type} - {message}"
