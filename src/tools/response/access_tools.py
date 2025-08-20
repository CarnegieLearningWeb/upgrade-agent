"""
Response Generator access tools.

These tools provide access to state data for the Response Generator node.
They allow the LLM to selectively access large static data and gathered information.
"""

from langchain.tools import tool
from typing import Dict, Any, List, Optional

from src.tools.registry import register_response_tool
from src.models.tool_types import ToolExperimentName, SimplifiedExperiment


@tool
@register_response_tool("get_context_metadata")
def get_context_metadata() -> Optional[Dict[str, Any]]:
    """
    Get stored context metadata (large data).
    
    Returns:
        Context metadata dictionary or None if not loaded
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        result = _state_ref.get("context_metadata")
        return result
    return None


@tool
@register_response_tool("get_experiment_names")
def get_experiment_names() -> Optional[List[ToolExperimentName]]:
    """
    Get stored experiment names (large data).
    
    Returns:
        List of experiment names and IDs or None if not loaded
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("experiment_names")
    return None


@tool
@register_response_tool("get_all_experiments")
def get_all_experiments() -> Optional[List[SimplifiedExperiment]]:
    """
    Get all experiment details (large data).
    
    Returns:
        List of all experiments or None if not loaded
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("all_experiments")
    return None


@tool
@register_response_tool("get_all_gathered_info")
def get_all_gathered_info() -> Dict[str, Any]:
    """
    Get all gathered information (query-specific data).
    
    Returns:
        Dictionary of all gathered information
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("gathered_info", {})
    return {}


@tool
@register_response_tool("get_execution_log")
def get_execution_log() -> List[Dict[str, Any]]:
    """
    Get chronological log of all executed actions.
    
    Returns:
        List of execution log entries
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("execution_log", [])
    return []


@tool
@register_response_tool("get_errors")
def get_errors() -> Dict[str, str]:
    """
    Get any errors that occurred during processing.
    
    Returns:
        Dictionary of error types to error messages
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("errors", {})
    return {}


@tool
@register_response_tool("get_current_state")
def get_current_state() -> str:
    """
    Get the current state of the conversation.
    
    Returns:
        Current state string
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("current_state", "UNKNOWN")
    return "UNKNOWN"


@tool
@register_response_tool("get_user_request_summary")
def get_user_request_summary() -> Optional[str]:
    """
    Get the summary of what the user is requesting.
    
    Returns:
        User request summary or None
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("user_request_summary")
    return None


@tool
@register_response_tool("get_action_status")
def get_action_status() -> Dict[str, Any]:
    """
    Get the current action status and parameters.
    
    Returns:
        Dictionary with action information
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return {
            "action_needed": _state_ref.get("action_needed"),
            "action_params": _state_ref.get("action_params", {}),
            "missing_params": _state_ref.get("missing_params", []),
            "needs_confirmation": _state_ref.get("needs_confirmation", False),
            "confirmation_message": _state_ref.get("confirmation_message")
        }
    return {}


@tool
@register_response_tool("get_conversation_history")
def get_conversation_history() -> List[Dict[str, str]]:
    """
    Get the conversation history.
    
    Returns:
        List of conversation turns
    """
    from src.tools.decorators import _state_ref
    
    if _state_ref:
        return _state_ref.get("conversation_history", [])
    return []
