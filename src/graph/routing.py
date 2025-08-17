"""
Routing logic for UpGradeAgent LangGraph.

This module defines the routing functions that determine which node
to visit next based on the current state.
"""

from typing import Literal

from src.graph.state import AgentState


def analyzer_routing(state: AgentState) -> Literal["response_generator", "information_gatherer", "tool_executor"]:
    """
    Routing logic for the Conversation Analyzer node.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to visit
    """
    # Check if user confirmed an action
    if state.get("user_confirmed") and state.get("action_needed"):
        return "tool_executor"
    
    # Check intent type
    intent_type = state.get("intent_type")
    if intent_type == "direct_answer":
        return "response_generator"
    elif intent_type == "needs_info":
        return "information_gatherer"
    else:
        # Default to response generator for unknown states
        return "response_generator"


def gatherer_routing(state: AgentState) -> Literal["response_generator", "confirmation_handler"]:
    """
    Routing logic for the Information Gatherer node.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to visit
    """
    # Check if action is ready for execution
    action_needed = state.get("action_needed")
    missing_params = state.get("missing_params", [])
    
    if not action_needed:
        # Pure information gathering, ready to respond
        return "response_generator"
    elif missing_params:
        # Need more info from user first
        return "response_generator" 
    else:
        # Ready for execution after confirmation
        return "confirmation_handler"


def confirmation_routing(state: AgentState) -> Literal["response_generator"]:
    """
    Routing logic for the Confirmation Handler node.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to visit (always response generator)
    """
    # Always show confirmation to user
    return "response_generator"


def executor_routing(state: AgentState) -> Literal["conversation_analyzer"]:
    """
    Routing logic for the Tool Executor node.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to visit (always back to analyzer)
    """
    # Always return to analyzer to process results
    return "conversation_analyzer"


def response_routing(state: AgentState) -> Literal["END", "conversation_analyzer"]:
    """
    Routing logic for the Response Generator node.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to visit or END
    """
    if state.get("conversation_complete"):
        return "END"
    else:
        # Wait for next user input
        return "conversation_analyzer"
