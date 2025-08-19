"""
LangGraph builder for UpGradeAgent.

This module builds the 5-node LangGraph workflow with proper routing
between nodes based on the conversation state.
"""

import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from .state import AgentState
from ..nodes.analyzer import analyzer_node, analyzer_routing
from ..nodes.gatherer import gatherer_node, gatherer_routing
from ..nodes.confirmation import confirmation_handler, confirmation_routing
from ..nodes.executor import tool_executor, executor_routing
from ..nodes.response import response_generator_node, response_routing

logger = logging.getLogger(__name__)


def build_upgrade_agent_graph():
    """
    Build the complete UpGradeAgent LangGraph workflow.
    
    Creates a 5-node graph with the following architecture:
    1. Conversation Analyzer (LLM) - Intent classification and orchestration
    2. Information Gatherer (LLM) - Data collection and validation
    3. Confirmation Handler (Non-LLM) - Safety confirmations for destructive actions
    4. Tool Executor (Non-LLM) - API execution layer
    5. Response Generator (LLM) - All user-facing communication
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Building UpGradeAgent LangGraph workflow")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("conversation_analyzer", analyzer_node)
    workflow.add_node("information_gatherer", gatherer_node)
    workflow.add_node("confirmation_handler", confirmation_handler)
    workflow.add_node("tool_executor", tool_executor)
    workflow.add_node("response_generator", response_generator_node)
    
    # Set entry point
    workflow.set_entry_point("conversation_analyzer")
    
    # Add conditional edges with routing functions
    workflow.add_conditional_edges(
        "conversation_analyzer",
        analyzer_routing,
        {
            "information_gatherer": "information_gatherer",
            "tool_executor": "tool_executor", 
            "response_generator": "response_generator"
        }
    )
    
    workflow.add_conditional_edges(
        "information_gatherer",
        gatherer_routing,
        {
            "confirmation_handler": "confirmation_handler",
            "response_generator": "response_generator"
        }
    )
    
    workflow.add_conditional_edges(
        "confirmation_handler", 
        confirmation_routing,
        {
            "response_generator": "response_generator"
        }
    )
    
    workflow.add_conditional_edges(
        "tool_executor",
        executor_routing,
        {
            "conversation_analyzer": "conversation_analyzer"
        }
    )
    
    workflow.add_conditional_edges(
        "response_generator",
        response_routing,
        {
            "conversation_analyzer": "conversation_analyzer",
            "END": END
        }
    )
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile the workflow
    app = workflow.compile(checkpointer=memory)
    
    logger.info("UpGradeAgent LangGraph workflow compiled successfully")
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
