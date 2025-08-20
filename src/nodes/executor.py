"""
Tool Executor node for UpGradeAgent.

This node executes UpGrade API calls using prepared parameters from the Information Gatherer.
It's a Non-LLM node that uses static logic to map actions to tool functions and handle
API execution with proper error handling.

Note: Execution logging is handled by the individual tool functions, not by this node.
"""

import logging
from typing import Dict, Any, cast

from ..graph.state import AgentState
from ..models.enums import ToolActionType
from ..tools.decorators import set_global_state
from ..tools.registry import tool_registry

logger = logging.getLogger(__name__)


async def _execute_action(action: ToolActionType, params: Dict[str, Any]) -> Any:
    """
    Execute a single action using the appropriate tool function.
    
    Args:
        action: The action to execute
        params: Parameters for the action
        
    Returns:
        Result from the tool execution
        
    Raises:
        Exception: If tool execution fails
    """
    # Get executor tools
    executor_tools = tool_registry.get_tools_for_node("executor")
    
    # Map action to tool function
    action_str = action.value if isinstance(action, ToolActionType) else str(action)
    
    if action_str not in executor_tools:
        raise ValueError(f"Unknown action: {action_str}")
    
    tool_func = executor_tools[action_str]
    
    logger.info(f"Executing action '{action_str}' with parameters: {params}")
    
    # Execute the tool function
    # Note: Tool functions expect action_params as a single argument
    result = await tool_func(params)
    
    logger.info(f"Action '{action_str}' completed successfully")
    return result


async def tool_executor(state: AgentState) -> Dict[str, Any]:
    """
    Tool Executor node implementation.
    
    This node executes UpGrade API calls using prepared parameters from the Information Gatherer.
    It uses static logic to map actions to tool functions and handles API execution with
    proper error handling and logging.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with state updates
    """
    logger.info("Entering Tool Executor node")
    
    # Set global state for tools to access (for execution logging)
    set_global_state(cast(Dict[str, Any], state))
    
    # Get the action and parameters from state
    action_needed = state.get("action_needed")
    action_params = state.get("action_params", {})
    
    if not action_needed:
        logger.error("Tool executor called without action_needed")
        return {
            "current_state": "RESPONDING",
            "errors": {
                **state.get("errors", {}),
                "executor": "No action specified for execution"
            }
        }
    
    try:
        logger.info(f"Executing action: {action_needed}")
        
        # Execute the action
        result = await _execute_action(action_needed, action_params)
        
        logger.info(f"Action {action_needed} executed successfully")
        
        # Clear the action and confirmation state since it's completed
        updates = {
            "current_state": "ANALYZING",  # Return to analyzer to process results
            "action_needed": None,
            "action_params": {},
            "needs_confirmation": False,
            "confirmation_message": None,
            "user_confirmed": None
        }
        
        # Store the execution result for potential use by other nodes
        # The result is already logged in execution_log by the tool function
        gathered_info = state.get("gathered_info", {})
        gathered_info["last_execution_result"] = result
        updates["gathered_info"] = gathered_info
        
        return updates
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error executing action {action_needed}: {error_message}")
        
        # Note: Error logging is handled by the tool function itself
        
        # Determine error type based on exception details
        error_type = "unknown"
        if "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
            error_type = "auth"
        elif "not found" in error_message.lower() or "404" in error_message:
            error_type = "not_found"
        elif ("validation" in error_message.lower() or "invalid" in error_message.lower() or 
              "missing required parameters" in error_message.lower() or "required" in error_message.lower()):
            error_type = "validation"
        elif "api" in error_message.lower() or "request" in error_message.lower():
            error_type = "api"
        
        return {
            "current_state": "RESPONDING",
            "errors": {
                **state.get("errors", {}),
                error_type: f"Execution failed: {error_message}"
            },
            # Clear the action state on error
            "action_needed": None,
            "action_params": {},
            "needs_confirmation": False,
            "confirmation_message": None,
            "user_confirmed": None
        }


def executor_routing(state: AgentState) -> str:
    """
    Routing function for the Tool Executor node.
    
    Always routes back to the conversation analyzer to process the execution results
    and determine the next appropriate response.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name (always "conversation_analyzer")
    """
    logger.info("Tool executor routing to conversation_analyzer")
    return "conversation_analyzer"
