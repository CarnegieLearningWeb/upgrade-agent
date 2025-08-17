"""
Confirmation Handler Node.

This node generates safety confirmations for all operations executed through Tool Executor.
It's a non-LLM node that uses static logic to create appropriate confirmation messages.
"""

from typing import Dict, Any

from src.graph.state import AgentState


def confirmation_node(state: AgentState) -> AgentState:
    """
    Confirmation Handler node implementation.
    
    This node generates confirmation messages for ALL operations that modify state.
    It requires user confirmation before any action is executed.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with confirmation message
    """
    
    # Update current state
    state["current_state"] = "CONFIRMING"
    
    action = state.get("action_needed")
    params = state.get("action_params", {})
    
    # Generate confirmation messages based on action type
    if action == "create_experiment":
        exp_name = params.get('name', 'Unknown')
        context = params.get('context', ['unknown'])[0] if isinstance(params.get('context'), list) else params.get('context', 'unknown')
        message = f"Create experiment '{exp_name}' in context '{context}'?"
        
    elif action == "delete_experiment":
        exp_name = params.get('name', params.get('experiment_id', 'unknown'))
        message = f"⚠️ PERMANENTLY DELETE experiment '{exp_name}'? This cannot be undone!"
        
    elif action == "update_experiment":
        exp_name = params.get('name', params.get('experiment_id', 'unknown'))
        message = f"Update experiment '{exp_name}' with new settings?"
        
    elif action == "update_experiment_status":
        status = params.get('status', 'unknown')
        exp_name = params.get('name', params.get('experiment_id', 'unknown'))
        message = f"Change experiment '{exp_name}' status to '{status}'?"
        
    elif action == "init_experiment_user":
        user_id = params.get('user_id', 'unknown')
        message = f"Initialize user '{user_id}' for experiment simulation?"
        
    elif action == "get_decision_point_assignments":
        context = params.get('context', 'unknown')
        message = f"Get condition assignments for context '{context}'?"
        
    elif action == "mark_decision_point":
        exp_id = params.get('assigned_condition', {}).get('experiment_id', 'unknown')
        message = f"Mark decision point visit for experiment '{exp_id}'?"
        
    else:
        message = f"Proceed with action '{action}'?"
    
    state["confirmation_message"] = message
    state["needs_confirmation"] = True
    
    return state
