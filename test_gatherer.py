"""
Test script for the Information Gatherer node.

This script tests basic functionality of the gatherer node to ensure
it can handle different types of requests and route appropriately.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.state import create_initial_state
from src.nodes.gatherer import gatherer_node, gatherer_routing
from src.config.config import config


async def test_gatherer_basic_functionality():
    """Test basic gatherer functionality with a simple terminology request."""
    print("Testing gatherer node with terminology request...")
    
    # Create initial state with a terminology question
    state = create_initial_state()
    state["user_input"] = "What is A/B testing?"
    state["intent_type"] = "needs_info"
    state["user_request_summary"] = "User wants to understand A/B testing terminology"
    state["current_state"] = "GATHERING_INFO"
    
    # Run the gatherer node
    try:
        result = await gatherer_node(state)
        print(f"Gatherer result: {result}")
        
        # Update state with result
        for key, value in result.items():
            state[key] = value
        
        # Test routing
        next_node = gatherer_routing(state)
        print(f"Next node: {next_node}")
        
        # Check if we have gathered information
        if state.get("gathered_info"):
            print(f"Gathered info keys: {list(state['gathered_info'].keys())}")
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_gatherer_experiment_request():
    """Test gatherer with an experiment-related request."""
    print("\nTesting gatherer node with experiment request...")
    
    # Create initial state with an experiment question
    state = create_initial_state()
    state["user_input"] = "What contexts are available?"
    state["intent_type"] = "needs_info"
    state["user_request_summary"] = "User wants to know available app contexts"
    state["current_state"] = "GATHERING_INFO"
    
    # Run the gatherer node
    try:
        result = await gatherer_node(state)
        print(f"Gatherer result: {result}")
        
        # Update state with result
        for key, value in result.items():
            state[key] = value
        
        # Test routing
        next_node = gatherer_routing(state)
        print(f"Next node: {next_node}")
        
        # Check if we have gathered information
        if state.get("gathered_info"):
            print(f"Gathered info keys: {list(state['gathered_info'].keys())}")
        
        print("✅ Experiment request test passed")
        return True
        
    except Exception as e:
        print(f"❌ Experiment request test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_gatherer_action_request():
    """Test gatherer with an action that needs parameters."""
    print("\nTesting gatherer node with action request...")
    
    # Create initial state with an action request
    state = create_initial_state()
    state["user_input"] = "Create an experiment called 'Test Experiment'"
    state["intent_type"] = "needs_info"
    state["user_request_summary"] = "User wants to create a new experiment"
    state["current_state"] = "GATHERING_INFO"
    
    # Run the gatherer node
    try:
        result = await gatherer_node(state)
        print(f"Gatherer result: {result}")
        
        # Update state with result
        for key, value in result.items():
            state[key] = value
        
        # Test routing
        next_node = gatherer_routing(state)
        print(f"Next node: {next_node}")
        
        # Check what was gathered or what's missing
        if state.get("action_needed"):
            print(f"Action needed: {state['action_needed']}")
        if state.get("missing_params"):
            print(f"Missing params: {state['missing_params']}")
        if state.get("gathered_info"):
            print(f"Gathered info keys: {list(state['gathered_info'].keys())}")
        
        print("✅ Action request test passed")
        return True
        
    except Exception as e:
        print(f"❌ Action request test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("Running Information Gatherer node tests...\n")
    
    # Validate configuration first
    try:
        config.validate()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Run tests
    results = []
    results.append(await test_gatherer_basic_functionality())
    results.append(await test_gatherer_experiment_request())  
    results.append(await test_gatherer_action_request())
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All gatherer node tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    asyncio.run(main())
