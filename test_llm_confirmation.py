#!/usr/bin/env python3
"""
Test the improved LLM-based confirmation handling.
"""

import sys
import os
from typing import cast

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.state import AgentState, create_initial_state
from src.nodes.analyzer import analyzer_node, analyzer_routing
from src.models.enums import ToolActionType


def update_state(state: AgentState, updates: dict) -> AgentState:
    """Safely update state dictionary."""
    new_state = {**state, **updates}
    return cast(AgentState, new_state)


def test_confirmation_responses():
    """Test various confirmation responses with LLM-based analysis."""
    
    confirmation_tests = [
        ("yes", "Simple affirmative"),
        ("Sure, let's do it", "Natural affirmative"),
        ("Absolutely!", "Enthusiastic affirmative"),
        ("no", "Simple negative"),
        ("I don't think so", "Natural negative"),
        ("Cancel that", "Cancel request"),
        ("Maybe later", "Ambiguous response"),
        ("What was the question again?", "Unclear response"),
        ("I'm not sure about this", "Hesitant response")
    ]
    
    print("Testing LLM-Based Confirmation Analysis")
    print("=" * 50)
    
    for user_input, description in confirmation_tests:
        print(f"\n=== {description} ===")
        print(f"Input: '{user_input}'")
        
        # Set up confirmation state
        state = create_initial_state()
        state["user_input"] = user_input
        state["needs_confirmation"] = True
        state["confirmation_message"] = "Create experiment 'Test Exp' in context 'assign-prog'?"
        state["action_needed"] = ToolActionType.CREATE_EXPERIMENT
        
        # Run analyzer
        result = analyzer_node(state)
        state = update_state(state, result)
        
        # Get routing
        next_node = analyzer_routing(state)
        
        # Display results
        print(f"Intent: {state.get('intent_type')}")
        print(f"Confidence: {state.get('confidence')}")
        print(f"User Confirmed: {state.get('user_confirmed')}")
        print(f"Next Node: {next_node}")
        print(f"Summary: {state.get('user_request_summary')}")
        
        if state.get('errors'):
            print(f"Errors: {state.get('errors')}")


if __name__ == "__main__":
    test_confirmation_responses()
