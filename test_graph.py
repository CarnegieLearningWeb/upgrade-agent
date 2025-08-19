#!/usr/bin/env python3
"""
Test script to verify the UpGradeAgent graph builds correctly.
"""

import asyncio
import sys
import os

# Add src to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state


async def test_graph_build():
    """Test that the graph builds without errors."""
    print("Testing UpGradeAgent graph build...")
    
    try:
        # Build the graph
        app = build_upgrade_agent_graph()
        print("✅ Graph built successfully!")
        
        # Test configuration creation
        config = create_conversation_config("test_session")
        print("✅ Configuration created successfully!")
        
        # Test initial state creation
        state = create_initial_state()
        print("✅ Initial state created successfully!")
        
        # Test a simple workflow execution (just analyzing a basic input)
        state["user_input"] = "Hello"
        print("Testing workflow execution...")
        
        result = await app.ainvoke(state, config=config)
        print("✅ Workflow executed successfully!")
        print(f"Final response: {result.get('final_response', 'No response generated')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_graph_build())
    sys.exit(0 if success else 1)
