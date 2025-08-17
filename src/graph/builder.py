"""
LangGraph builder for UpGradeAgent.

This module constructs the 5-node LangGraph with proper routing
and state management.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.graph.state import AgentState
from src.nodes import (
    analyzer_node,
    gatherer_node,
    confirmation_node,
    executor_node,
    response_node
)
from src.graph.routing import (
    analyzer_routing,
    gatherer_routing,
    confirmation_routing,
    executor_routing,
    response_routing
)


def create_graph():
    """
    Create and configure the LangGraph for UpGradeAgent.
    
    Returns:
        Configured LangGraph instance
    """
    
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("conversation_analyzer", analyzer_node)
    graph.add_node("information_gatherer", gatherer_node)
    graph.add_node("confirmation_handler", confirmation_node)
    graph.add_node("tool_executor", executor_node)
    graph.add_node("response_generator", response_node)
    
    # Add edges with routing
    graph.add_conditional_edges(
        "conversation_analyzer",
        analyzer_routing,
        {
            "response_generator": "response_generator",
            "information_gatherer": "information_gatherer", 
            "tool_executor": "tool_executor"
        }
    )
    
    graph.add_conditional_edges(
        "information_gatherer",
        gatherer_routing,
        {
            "response_generator": "response_generator",
            "confirmation_handler": "confirmation_handler"
        }
    )
    
    graph.add_conditional_edges(
        "confirmation_handler",
        confirmation_routing,
        {
            "response_generator": "response_generator"
        }
    )
    
    graph.add_conditional_edges(
        "tool_executor", 
        executor_routing,
        {
            "conversation_analyzer": "conversation_analyzer"
        }
    )
    
    graph.add_conditional_edges(
        "response_generator",
        response_routing,
        {
            "END": END,
            "conversation_analyzer": "conversation_analyzer"
        }
    )
    
    # Set entry point
    graph.add_edge(START, "conversation_analyzer")
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile the graph
    compiled_graph = graph.compile(checkpointer=memory)
    
    return compiled_graph
