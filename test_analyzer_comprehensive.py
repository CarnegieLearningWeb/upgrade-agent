#!/usr/bin/env python3
"""
Comprehensive test for the updated analyzer node.

Tests various user inputs to verify correct intent classification.
"""

import sys
import os
import logging
from typing import cast

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.state import AgentState, create_initial_state
from src.nodes.analyzer import analyzer_node, analyzer_routing
from src.tools import tool_registry
from src.models.enums import ToolActionType

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


def update_state(state: AgentState, updates: dict) -> AgentState:
    """Safely update state dictionary."""
    new_state = {**state, **updates}
    return cast(AgentState, new_state)


def test_single_input(user_input: str, description: str = "") -> None:
    """Test a single user input and display results."""
    print(f"\n=== Test: {description or user_input} ===")
    print(f"Input: '{user_input}'")
    
    # Create fresh state
    state = create_initial_state()
    state["user_input"] = user_input
    
    # Run analyzer
    result = analyzer_node(state)
    state = update_state(state, result)
    
    # Get routing
    next_node = analyzer_routing(state)
    
    # Display results
    print(f"Intent Type: {state.get('intent_type')}")
    print(f"Confidence: {state.get('confidence')}")
    print(f"Summary: {state.get('user_request_summary')}")
    print(f"Next Node: {next_node}")
    print(f"State: {state.get('current_state')}")
    if state.get('errors'):
        print(f"Errors: {state.get('errors')}")


def test_confirmation_flow() -> None:
    """Test confirmation flow separately."""
    print("\n=== Test: Confirmation Flow ===")
    
    # Set up state as if we're waiting for confirmation
    state = create_initial_state()
    state["user_input"] = "yes"
    state["needs_confirmation"] = True
    state["confirmation_message"] = "Create experiment 'Test Exp'?"
    state["action_needed"] = ToolActionType.CREATE_EXPERIMENT
    
    print("Input: 'yes' (with confirmation context)")
    print(f"Needs Confirmation: {state['needs_confirmation']}")
    print(f"Confirmation Message: {state['confirmation_message']}")
    
    # Run analyzer
    result = analyzer_node(state)
    state = update_state(state, result)
    
    # Get routing
    next_node = analyzer_routing(state)
    
    # Display results
    print(f"Intent Type: {state.get('intent_type')}")
    print(f"Confidence: {state.get('confidence')}")
    print(f"Summary: {state.get('user_request_summary')}")
    print(f"Next Node: {next_node}")
    print(f"State: {state.get('current_state')}")


def run_all_tests():
    """Run all test cases."""
    print("Testing UpGradeAgent Analyzer Node - Updated Version")
    print("=" * 60)
    
    # Test cases from user request
    test_cases = [
        ("Hello!", "Greeting"),
        ("What is A/B testing?", "Educational Question - General"),
        ("Tell me the list of experiment names", "API Data Request"),
        ("Can you create an experiment named 'Foo'?", "Experiment Creation"),
        ("What is decision point in UpGrade?", "Educational Question - Specific Term"),
        ("I like pizza!", "Unrelated Statement"),
        ("Let's call /init with the user 'test_user1'", "API Call Request")
    ]
    
    for user_input, description in test_cases:
        test_single_input(user_input, description)
    
    # Test confirmation flow
    test_confirmation_flow()
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    
    # Summary of expected classifications
    print("\nEXPECTED CLASSIFICATIONS:")
    print("- 'Hello!' → direct_answer (greeting)")
    print("- 'What is A/B testing?' → direct_answer (general terminology)")
    print("- 'Tell me the list of experiment names' → needs_info (API data)")
    print("- 'Can you create an experiment named Foo?' → needs_info (experiment creation)")
    print("- 'What is decision point in UpGrade?' → needs_info (UpGrade terminology)")
    print("- 'I like pizza!' → direct_answer (unrelated, no clarification needed)")
    print("- 'Let's call /init with user test_user1' → needs_info (API operation)")
    print("- 'yes' (with confirmation) → direct_answer + route to tool_executor")


if __name__ == "__main__":
    run_all_tests()
