"""
Confirmation Handler node for UpGradeAgent.

This node generates safety confirmations for ALL operations executed through 
Tool Executor. It's a Non-LLM node that uses static logic to create 
appropriate confirmation messages for each action type.
"""

import logging
from typing import Dict, Any

from ..graph.state import AgentState
from ..models.enums import ToolActionType

logger = logging.getLogger(__name__)


def _get_experiment_name(params: Dict[str, Any]) -> str:
    """Get experiment name from parameters, falling back to ID if needed."""
    experiment_name = params.get('experiment_name', params.get('name', 'Unknown'))
    if experiment_name == 'Unknown' and 'experiment_id' in params:
        experiment_name = f"ID: {params['experiment_id']}"
    return experiment_name


def _generate_experiment_confirmation(action: ToolActionType, params: Dict[str, Any]) -> str:
    """Generate confirmation messages for experiment-related actions."""
    if action == ToolActionType.CREATE_EXPERIMENT:
        experiment_name = params.get('name', 'Unknown')
        context = params.get('context', 'Unknown')
        return f"Create experiment '{experiment_name}' in context '{context}'?"
        
    elif action == ToolActionType.DELETE_EXPERIMENT:
        experiment_name = _get_experiment_name(params)
        return f"⚠️ PERMANENTLY DELETE experiment '{experiment_name}'? This cannot be undone!"
        
    elif action == ToolActionType.UPDATE_EXPERIMENT:
        experiment_name = _get_experiment_name(params)
        return f"Update experiment '{experiment_name}' with new settings?"
        
    elif action == ToolActionType.UPDATE_EXPERIMENT_STATUS:
        status = params.get('status', 'unknown')
        experiment_name = _get_experiment_name(params)
        return f"Change experiment '{experiment_name}' status to '{status}'?"
    
    return ""


def _generate_user_simulation_confirmation(action: ToolActionType, params: Dict[str, Any]) -> str:
    """Generate confirmation messages for user simulation actions."""
    if action == ToolActionType.INIT_EXPERIMENT_USER:
        user_id = params.get('user_id', 'unknown')
        context = params.get('context', 'unknown')
        return f"Initialize user '{user_id}' for experiment simulation in context '{context}'?"
        
    elif action == ToolActionType.GET_DECISION_POINT_ASSIGNMENTS:
        context = params.get('context', 'unknown')
        user_id = params.get('user_id', 'unknown')
        return f"Get condition assignments for user '{user_id}' in context '{context}'?"
        
    elif action == ToolActionType.MARK_DECISION_POINT:
        assigned_condition = params.get('assigned_condition', {})
        experiment_id = assigned_condition.get('experiment_id') if isinstance(assigned_condition, dict) else 'unknown'
        decision_point = params.get('decision_point', 'unknown')
        user_id = params.get('user_id', 'unknown')
        return f"Mark decision point '{decision_point}' visit for user '{user_id}' in experiment '{experiment_id}'?"
    
    return ""


def _generate_confirmation_message(action: ToolActionType, params: Dict[str, Any]) -> str:
    """
    Generate appropriate confirmation message based on action type and parameters.
    
    Args:
        action: The action that needs confirmation
        params: Parameters for the action
        
    Returns:
        Confirmation message string
    """
    # Handle experiment-related actions
    experiment_actions = {
        ToolActionType.CREATE_EXPERIMENT,
        ToolActionType.DELETE_EXPERIMENT,
        ToolActionType.UPDATE_EXPERIMENT,
        ToolActionType.UPDATE_EXPERIMENT_STATUS
    }
    
    if action in experiment_actions:
        return _generate_experiment_confirmation(action, params)
    
    # Handle user simulation actions
    user_simulation_actions = {
        ToolActionType.INIT_EXPERIMENT_USER,
        ToolActionType.GET_DECISION_POINT_ASSIGNMENTS,
        ToolActionType.MARK_DECISION_POINT
    }
    
    if action in user_simulation_actions:
        return _generate_user_simulation_confirmation(action, params)
    
    # Fallback for unknown actions
    return f"Execute action '{action}' with the provided parameters?"


def _is_destructive_action(action: ToolActionType) -> bool:
    """
    Determine if an action is destructive and needs special warning.
    
    Args:
        action: The action to check
        
    Returns:
        True if the action is destructive
    """
    destructive_actions = {
        ToolActionType.DELETE_EXPERIMENT,
        # Note: Other actions like UPDATE_EXPERIMENT_STATUS changing to 'archived' 
        # could also be considered destructive, but we handle that in the message
    }
    return action in destructive_actions


def confirmation_handler(state: AgentState) -> Dict[str, Any]:
    """
    Confirmation Handler node implementation.
    
    This node generates safety confirmations for ALL operations executed through 
    Tool Executor. It uses static logic to create appropriate confirmation messages
    for each action type.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with state updates
    """
    logger.info("Entering Confirmation Handler node")
    
    # Get the action that needs confirmation
    action_needed = state.get("action_needed")
    action_params = state.get("action_params", {})
    
    if not action_needed:
        logger.warning("Confirmation handler called without action_needed")
        return {
            "current_state": "RESPONDING",
            "errors": {
                **state.get("errors", {}), 
                "confirmation": "No action specified for confirmation"
            }
        }
    
    try:
        # Generate confirmation message
        confirmation_message = _generate_confirmation_message(action_needed, action_params)
        
        logger.info(f"Generated confirmation for action '{action_needed}': {confirmation_message}")
        
        # Update state with confirmation information
        return {
            "current_state": "CONFIRMING",
            "needs_confirmation": True,
            "confirmation_message": confirmation_message
        }
        
    except Exception as e:
        logger.error(f"Error in confirmation handler: {e}")
        return {
            "current_state": "RESPONDING",
            "errors": {
                **state.get("errors", {}), 
                "confirmation": f"Failed to generate confirmation: {str(e)}"
            }
        }


def confirmation_routing(state: AgentState) -> str:
    """
    Routing function for the Confirmation Handler node.
    
    Always routes to response_generator to show the confirmation to the user.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name (always "response_generator")
    """
    logger.info("Confirmation handler routing to response_generator")
    return "response_generator"
