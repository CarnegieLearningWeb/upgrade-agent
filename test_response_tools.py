#!/usr/bin/env python3
"""
Test the response generator tools directly.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.decorators import set_global_state
from src.tools.response.access_tools import get_context_metadata
from src.graph.state import create_initial_state

def test_response_tools():
    """Test response generator tools directly."""
    print("Testing response generator tools...")
    
    # Create a state with context metadata (simulating what gatherer provides)
    state = create_initial_state()
    state["context_metadata"] = {
        "test-context-1": {"conditions": ["control", "treatment"]},
        "test-context-2": {"conditions": ["variant1", "variant2"]}
    }
    
    print(f"State context_metadata: {bool(state.get('context_metadata'))}")
    
    # Set global state
    from typing import Dict, Any, cast
    set_global_state(cast(Dict[str, Any], state))
    
    # Test the tool (it's a langchain tool, so call invoke)
    result = get_context_metadata.invoke({})
    print(f"Tool result: {type(result)} - {bool(result)}")
    if result:
        print(f"Tool result keys: {list(result.keys())}")
    else:
        print("Tool returned None")

if __name__ == "__main__":
    test_response_tools()
