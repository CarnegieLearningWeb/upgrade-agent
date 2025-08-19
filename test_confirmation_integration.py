#!/usr/bin/env python3
"""
Integration test showing the confirmation node in the full workflow.

This demonstrates how the confirmation node integrates with the analyzer 
and gatherer nodes in a typical action flow.
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
    new_state = {**state, **updates}
    return cast(AgentState, new_state)


def test_full_confirmation_workflow():
    """Test a complete workflow involving confirmation."""
    
    print("=== Full Confirmation Workflow Test ===")
    print("Simulating: User wants to delete an experiment")
    print()
    
    # Step 1: Simulate state after analyzer and gatherer have processed
    # "Delete the Math Hints experiment"
    print("1. Initial state after analyzer and gatherer processing:")
    state = create_initial_state()
    state = update_state(state, {
        "user_input": "Delete the Math Hints experiment",
        "current_state": "CONFIRMING",
        "intent_type": "needs_info",
        "user_request_summary": "User wants to delete the 'Math Hints' experiment",
        "action_needed": ToolActionType.DELETE_EXPERIMENT,
        "action_params": {
            "experiment_id": "550e8400-e29b-41d4-a716-446655440000",
            "experiment_name": "Math Hints"
        },
        "gathered_info": {
            "experiment_details": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Math Hints",
                "context": "assign-prog"
            }
        }
    })
    print(f"  - User input: {state['user_input']}")
    print(f"  - Current state: {state['current_state']}")
    print(f"  - Action needed: {state['action_needed']}")
    print(f"  - Action params: {state['action_params']}")
    print()
    
    # Step 2: Process through confirmation handler
    print("2. Processing through confirmation handler:")
    result = confirmation_handler(state)
    state = update_state(state, result)
    
    print(f"  - New state: {state['current_state']}")
    print(f"  - Needs confirmation: {state['needs_confirmation']}")
    print(f"  - Confirmation message: {state['confirmation_message']}")
    print()
    
    # Step 3: Routing decision
    print("3. Routing decision:")
    next_node = confirmation_routing(state)
    print(f"  - Next node: {next_node}")
    print("  - This will send the confirmation message to the user via response_generator")
    print()
    
    # Step 4: Simulate user confirmation response
    print("4. Simulating user confirmation response:")
    print("  - User responds: 'yes, delete it'")
    
    # This would typically go through analyzer again to detect confirmation
    state = update_state(state, {
        "user_input": "yes, delete it",
        "user_confirmed": True,
        "current_state": "EXECUTING"
    })
    
    print(f"  - User confirmed: {state['user_confirmed']}")
    print(f"  - Ready for execution: {state['current_state'] == 'EXECUTING'}")
    print()
    
    print("✅ Full workflow test completed successfully!")
    print("Next step would be routing to tool_executor to perform the deletion.")


def test_confirmation_rejection_workflow():
    """Test workflow when user rejects the confirmation."""
    
    print("=== Confirmation Rejection Workflow Test ===")
    print("Simulating: User rejects a destructive action")
    print()
    
    # Set up state with a destructive action ready for confirmation
    state = create_initial_state()
    state = update_state(state, {
        "user_input": "Delete the Math Hints experiment",
        "action_needed": ToolActionType.DELETE_EXPERIMENT,
        "action_params": {
            "experiment_id": "550e8400-e29b-41d4-a716-446655440000",
            "experiment_name": "Math Hints"
        }
    })
    
    # Process through confirmation
    result = confirmation_handler(state)
    state = update_state(state, result)
    
    print(f"1. Confirmation generated: {state['confirmation_message']}")
    
    # Simulate user rejection
    print("2. User responds: 'no, cancel that'")
    state = update_state(state, {
        "user_input": "no, cancel that",
        "user_confirmed": False
    })
    
    print(f"3. User confirmed: {state['user_confirmed']}")
    print("4. Expected behavior: Action should be cancelled, response_generator should inform user")
    print()
    
    print("✅ Rejection workflow test completed successfully!")


if __name__ == "__main__":
    print("Testing Confirmation Node Integration")
    print("=" * 50)
    
    test_full_confirmation_workflow()
    print()
    test_confirmation_rejection_workflow()
    
    print("=" * 50)
    print("✅ All integration tests completed!")
