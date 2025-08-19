#!/usr/bin/env python3
"""
Test script for the analyzer node implementation.

This script tests the analyzer node functionality to ensure it works correctly
before integrating into the full LangGraph.
"""

import sys
import os
import asyncio
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.state import AgentState, create_initial_state
from src.nodes.analyzer import analyzer_node, analyzer_routing
from src.tools import tool_registry
from src.models.enums import ToolActionType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from typing import cast


def update_state(state: AgentState, updates: dict) -> AgentState:
    """Safely update state dictionary."""
    # Create a new state dict with updates - use casting for TypedDict
    new_state = {**state, **updates}
    return cast(AgentState, new_state)


def test_analyzer_node():
    """Test the analyzer node with different types of input."""
    
    # Test 1: Direct answer question
    print("=== Test 1: Direct Answer Question ===")
    state = create_initial_state()
    state["user_input"] = "What is A/B testing?"
    
    result = analyzer_node(state)
    print(f"Result: {result}")
    
    # Update state with result
    state = update_state(state, result)
    
    # Test routing
    next_node = analyzer_routing(state)
    print(f"Next node: {next_node}")
    print(f"Intent type: {state.get('intent_type')}")
    print(f"Confidence: {state.get('confidence')}")
    print(f"Summary: {state.get('user_request_summary')}")
    print()
    
    # Test 2: Needs info question
    print("=== Test 2: Needs Info Question ===")
    state = create_initial_state()
    state["user_input"] = "Create a new experiment called 'Math Test' in assign-prog context"
    
    result = analyzer_node(state)
    print(f"Result: {result}")
    
    # Update state with result
    state = update_state(state, result)
    
    # Test routing
    next_node = analyzer_routing(state)
    print(f"Next node: {next_node}")
    print(f"Intent type: {state.get('intent_type')}")
    print(f"Confidence: {state.get('confidence')}")
    print(f"Summary: {state.get('user_request_summary')}")
    print()
    
    # Test 3: Confirmation response
    print("=== Test 3: Confirmation Response ===")
    state = create_initial_state()
    state["user_input"] = "yes"
    state["needs_confirmation"] = True
    state["confirmation_message"] = "Create experiment 'Math Test'?"
    state["action_needed"] = ToolActionType.CREATE_EXPERIMENT
    
    result = analyzer_node(state)
    print(f"Result: {result}")
    
    # Update state with result
    state = update_state(state, result)
    
    # Test routing
    next_node = analyzer_routing(state)
    print(f"Next node: {next_node}")
    print()


def test_tool_registry():
    """Test that analyzer tools are properly registered."""
    print("=== Tool Registry Test ===")
    
    analyzer_tools = tool_registry.get_tools_for_node("analyzer")
    print(f"Analyzer tools: {list(analyzer_tools.keys())}")
    
    if "analyze_user_request" in analyzer_tools:
        tool_func = analyzer_tools["analyze_user_request"]
        print(f"Tool function: {tool_func}")
        print(f"Tool type: {type(tool_func)}")
        # Try to access tool properties if they exist
        if hasattr(tool_func, 'name'):
            print(f"Tool name: {getattr(tool_func, 'name')}")
        if hasattr(tool_func, 'description'):
            print(f"Tool description: {getattr(tool_func, 'description')}")
        if hasattr(tool_func, '__name__'):
            print(f"Function name: {tool_func.__name__}")
    else:
        print("ERROR: analyze_user_request tool not found!")
    print()


if __name__ == "__main__":
    print("Testing UpGradeAgent Analyzer Node")
    print("=" * 50)
    
    # Test tool registry first
    test_tool_registry()
    
    # Test analyzer node
    test_analyzer_node()
    
    print("Testing completed!")
