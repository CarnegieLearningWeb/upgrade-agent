#!/usr/bin/env python3
"""
Test script for the confirmation node implementation.

This script tests the confirmation node functionality to ensure it works correctly
before integrating into the full LangGraph.
"""

import sys
import os
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.state import AgentState, create_initial_state
from src.nodes.confirmation import confirmation_handler, confirmation_routing
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


def test_confirmation_node():
    """Test the confirmation node with different types of actions."""
    
    # Test 1: Create experiment confirmation
    print("=== Test 1: Create Experiment Confirmation ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.CREATE_EXPERIMENT,
        "action_params": {
            "name": "Math Hints Test",
            "context": "assign-prog"
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()
    
    # Test 2: Delete experiment confirmation (destructive action)
    print("=== Test 2: Delete Experiment Confirmation ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.DELETE_EXPERIMENT,
        "action_params": {
            "experiment_name": "Math Hints Test",
            "experiment_id": "12345-67890"
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()
    
    # Test 3: Update experiment status confirmation
    print("=== Test 3: Update Experiment Status Confirmation ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.UPDATE_EXPERIMENT_STATUS,
        "action_params": {
            "experiment_name": "Math Hints Test",
            "experiment_id": "12345-67890",
            "status": "enrolling"
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()
    
    # Test 4: Init experiment user confirmation
    print("=== Test 4: Init Experiment User Confirmation ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.INIT_EXPERIMENT_USER,
        "action_params": {
            "user_id": "test_user_123",
            "context": "assign-prog"
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()
    
    # Test 5: Get decision point assignments confirmation
    print("=== Test 5: Get Decision Point Assignments Confirmation ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.GET_DECISION_POINT_ASSIGNMENTS,
        "action_params": {
            "user_id": "test_user_123",
            "context": "assign-prog"
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()
    
    # Test 6: Mark decision point confirmation
    print("=== Test 6: Mark Decision Point Confirmation ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.MARK_DECISION_POINT,
        "action_params": {
            "user_id": "test_user_123",
            "decision_point": "select_homework",
            "assigned_condition": {
                "experiment_id": "12345-67890"
            }
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()
    
    # Test 7: Edge case - no action needed
    print("=== Test 7: Edge Case - No Action Needed ===")
    state = create_initial_state()
    # Don't set action_needed
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Errors: {result.get('errors')}")
    print()
    
    # Test 8: Edge case - experiment with only ID (no name)
    print("=== Test 8: Edge Case - Experiment with Only ID ===")
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.DELETE_EXPERIMENT,
        "action_params": {
            "experiment_id": "abcd-1234-efgh-5678"
            # No experiment_name provided
        }
    })
    
    result = confirmation_handler(state)
    print(f"Result: {result}")
    print(f"Confirmation message: {result.get('confirmation_message')}")
    print(f"Current state: {result.get('current_state')}")
    print(f"Needs confirmation: {result.get('needs_confirmation')}")
    print()


def test_confirmation_routing():
    """Test the routing function for the confirmation node."""
    print("=== Test Confirmation Routing ===")
    
    # Create a state with confirmation needed
    state = create_initial_state()
    state = update_state(state, {
        "action_needed": ToolActionType.CREATE_EXPERIMENT,
        "needs_confirmation": True,
        "confirmation_message": "Create experiment 'Test' in context 'assign-prog'?"
    })
    
    next_node = confirmation_routing(state)
    print(f"Next node: {next_node}")
    
    # Routing should always go to response_generator
    assert next_node == "response_generator", f"Expected 'response_generator', got '{next_node}'"
    print("✓ Routing test passed")
    print()


def run_all_tests():
    """Run all confirmation node tests."""
    print("Starting Confirmation Node Tests")
    print("=" * 50)
    
    try:
        test_confirmation_node()
        test_confirmation_routing()
        
        print("=" * 50)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
