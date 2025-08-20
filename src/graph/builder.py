"""
LangGraph builder for UpGradeAgent.

This module builds the single-node LangGraph workflow with one intelligent
agent that can handle all requests end-to-end with iterative tool calling.
"""

import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from .state import AgentState
from ..nodes.intelligent_agent import intelligent_agent_node, intelligent_agent_routing

logger = logging.getLogger(__name__)


def build_upgrade_agent_graph():
    """
    Build the complete UpGradeAgent LangGraph workflow.
    
    Creates a single-node graph with the following architecture:
    1. Intelligent Agent (LLM) - Handles all requests end-to-end with iterative tool calling
    
    The agent has access to all tools from the original 5-node architecture:
    - API tools for data gathering and system interaction
    - Action tools for experiment management and user simulation  
    - Utility tools for schema information and educational content
    - State management tools for complex workflows
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Building UpGradeAgent single-node LangGraph workflow")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add the single intelligent agent node
    workflow.add_node("intelligent_agent", intelligent_agent_node)
    
    # Set entry point
    workflow.set_entry_point("intelligent_agent")
    
    # Add conditional edge (always routes to END)
    workflow.add_conditional_edges(
        "intelligent_agent",
        intelligent_agent_routing,
        {
            "END": END
        }
    )
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile the workflow
    app = workflow.compile(checkpointer=memory)
    
    logger.info("UpGradeAgent single-node LangGraph workflow compiled successfully")
    return app


def create_conversation_config(conversation_id: str = "default") -> RunnableConfig:
    """
    Create configuration for a conversation session.
    
    Args:
        conversation_id: Unique identifier for the conversation
        
    Returns:
        Configuration dict for LangGraph execution
    """
    return RunnableConfig(
        configurable={
            "thread_id": conversation_id
        }
    )
