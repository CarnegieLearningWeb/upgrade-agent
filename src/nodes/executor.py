"""
Tool Executor Node.

This node executes UpGrade API calls using prepared parameters.
It's a non-LLM node that maps actions to specific tool functions.
"""

import asyncio
from typing import Dict, Any

from src.graph.state import AgentState
from src.tools import get_tools_for_node


def executor_node(state: AgentState) -> AgentState:
    """
    Tool Executor node implementation.
    
    This node executes the action specified in action_needed using the
    prepared parameters from action_params.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with execution results
    """
    
    # Update current state
    state["current_state"] = "EXECUTING"
    
    action = state.get("action_needed")
    params = state.get("action_params", {})
    
    if not action:
        # No action to execute
        return state
    
    # Get executor tools
    executor_tools = get_tools_for_node("executor")
    
    # Map action to tool function
    if action in executor_tools:
        tool_func = executor_tools[action]
        
        try:
            # Execute the tool (most are async)
            if asyncio.iscoroutinefunction(tool_func):
                # For now, we'll skip async execution in this placeholder
                # In the real implementation, this would be handled by LangGraph
                result = {"status": "Would execute async", "action": action, "params": params}
            else:
                # Pass action_params as a single dictionary argument
                result = tool_func(params)
            
            # Clear the action since it's been executed
            state["action_needed"] = None
            state["action_params"] = {}
            
        except Exception as e:
            # Log the error
            if "errors" not in state:
                state["errors"] = {}
            state["errors"]["execution"] = str(e)
    
    else:
        # Unknown action
        if "errors" not in state:
            state["errors"] = {}
        state["errors"]["execution"] = f"Unknown action: {action}"
    
    return state
