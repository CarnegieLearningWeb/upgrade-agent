#!/usr/bin/env python3
"""
Debug script to test each node individually.
"""

import asyncio
import sys
import os

# Add src to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_initial_state
from src.nodes.analyzer import analyzer_node, analyzer_routing


def test_analyzer():
    """Test just the analyzer node."""
    print("Testing analyzer node...")
    
    try:
        # Create initial state
        state = create_initial_state()
        state["user_input"] = "Hello"
        
        print(f"Initial state: {state}")
        
        # Run analyzer
        result = analyzer_node(state)
        print(f"Analyzer result: {result}")
        
        # Update state with result (manual merge)
        for key, value in result.items():
            state[key] = value
        
        # Test routing
        next_node = analyzer_routing(state)
        print(f"Next node: {next_node}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
