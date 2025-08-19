"""
Quick test to verify executor node implementation.
"""

import asyncio
from src.nodes.executor import tool_executor, executor_routing
from src.graph.state import create_initial_state
from src.models.enums import ToolActionType

async def test_executor_basic():
    """Test basic executor functionality."""
    
    # Test 1: No action needed (should return error)
    print("=== Test 1: No action needed ===")
    state = create_initial_state()
    state["user_input"] = "test"
    
    result = await tool_executor(state)
    print(f"Result: {result}")
    print(f"Should have error: {'executor' in result.get('errors', {})}")
    print()
    
    # Test 2: Unknown action (should return error)  
    print("=== Test 2: Unknown action ===")
    state = create_initial_state()
    state["user_input"] = "test"
    # Simulate an unknown action by setting it directly as a string
    state["action_needed"] = "unknown_action"  # type: ignore
    state["action_params"] = {}
    
    result = await tool_executor(state)
    print(f"Result: {result}")
    print(f"Should have error: {'unknown' in result.get('errors', {})}")
    print()
    
    # Test 3: Valid action but missing parameters (should return validation error)
    print("=== Test 3: Valid action, missing params ===")
    state = create_initial_state()
    state["user_input"] = "test"
    state["action_needed"] = ToolActionType.CREATE_EXPERIMENT
    state["action_params"] = {}  # Missing required params
    
    result = await tool_executor(state)
    print(f"Result: {result}")
    print(f"Should have validation error: {'validation' in result.get('errors', {})}")
    print()
    
    # Test 4: Routing function
    print("=== Test 4: Routing function ===")
    state = create_initial_state()
    routing_result = executor_routing(state)
    print(f"Routing result: {routing_result}")
    print(f"Should be 'conversation_analyzer': {routing_result == 'conversation_analyzer'}")
    print()

if __name__ == "__main__":
    asyncio.run(test_executor_basic())
