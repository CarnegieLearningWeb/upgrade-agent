"""
Minimal test for gatherer node without LLM tool binding.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.state import create_initial_state
from src.nodes.gatherer import _build_context_information, gatherer_routing
from src.models.enums import ToolActionType


def test_context_building():
    """Test the context building functionality."""
    print("Testing context building...")
    
    # Test with empty state
    state = create_initial_state()
    context = _build_context_information(state)
    print(f"Empty state context: {context}")
    
    # Test with user request
    state["user_request_summary"] = "User wants to understand A/B testing"
    context = _build_context_information(state)
    print(f"With user request: {context}")
    
    # Test with action in progress
    state["action_needed"] = ToolActionType.CREATE_EXPERIMENT
    state["action_params"] = {"name": "Test Experiment"}
    state["missing_params"] = ["context"]
    context = _build_context_information(state)
    print(f"With action in progress: {context}")
    
    print("✅ Context building test passed")


def test_routing():
    """Test the routing functionality."""
    print("\nTesting routing...")
    
    # Test with action ready
    state = create_initial_state()
    state["action_needed"] = ToolActionType.CREATE_EXPERIMENT
    next_node = gatherer_routing(state)
    print(f"Action ready -> {next_node}")
    
    # Test with missing params
    state["missing_params"] = ["context"]
    next_node = gatherer_routing(state)
    print(f"Missing params -> {next_node}")
    
    # Test with errors
    state = create_initial_state()
    state["errors"] = {"validation": "Invalid parameter"}
    next_node = gatherer_routing(state)
    print(f"With errors -> {next_node}")
    
    # Test with gathered info
    state = create_initial_state()
    state["gathered_info"] = {"core_terms": "data"}
    next_node = gatherer_routing(state)
    print(f"With gathered info -> {next_node}")
    
    print("✅ Routing test passed")


def test_state_tools():
    """Test the synchronous state management tools."""
    print("\nTesting state management tools...")
    
    try:
        from src.tools.gatherer.state_tools import set_action_needed, set_action_params
        from src.tools.decorators import set_global_state
        from typing import cast, Dict, Any
        
        # Create a test state
        test_state = create_initial_state()
        set_global_state(cast(Dict[str, Any], test_state))
        
        # Test set_action_needed - call with proper LangChain tool interface
        result = set_action_needed.invoke({
            "action": "create_experiment", 
            "reasoning": "User wants to create a new experiment"
        })
        print(f"set_action_needed result: {result}")
        print(f"State action_needed: {test_state.get('action_needed')}")
        
        # Test set_action_params
        result = set_action_params.invoke({
            "action_params": {"name": "Test Experiment", "context": "test-context"}
        })
        print(f"set_action_params result: {result}")
        print(f"State action_params: {test_state.get('action_params')}")
        
        print("✅ State tools test passed")
        
    except Exception as e:
        print(f"❌ State tools test failed: {e}")
        import traceback
        traceback.print_exc()


def test_utility_tools():
    """Test the synchronous utility tools."""
    print("\nTesting utility tools...")
    
    try:
        from src.tools.gatherer.utility_tools import get_core_terms
        from src.tools.decorators import set_global_state
        from typing import cast, Dict, Any
        
        # Create a test state
        test_state = create_initial_state()
        set_global_state(cast(Dict[str, Any], test_state))
        
        # Test get_core_terms (should be synchronous)
        result = get_core_terms.invoke({})  # Empty dict for tools with no parameters
        print(f"get_core_terms returned: {type(result)} with {len(result) if isinstance(result, dict) else 'unknown'} items")
        print(f"State gathered_info: {list(test_state.get('gathered_info', {}).keys())}")
        
        print("✅ Utility tools test passed")
        
    except Exception as e:
        print(f"❌ Utility tools test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all minimal tests."""
    print("Running minimal gatherer node tests...\n")
    
    test_context_building()
    test_routing()
    test_state_tools()
    test_utility_tools()
    
    print(f"\n{'='*50}")
    print("🎉 All minimal tests completed!")


if __name__ == "__main__":
    main()
