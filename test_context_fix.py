#!/usr/bin/env python3
"""
Test the specific context metadata issue.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state


async def test_context_query():
    """Test the specific context metadata query."""
    print("Testing 'What contexts are available?' query...")
    
    try:
        app = build_upgrade_agent_graph()
        config = create_conversation_config("test_context")
        
        # Test the specific query that was failing
        state = create_initial_state()
        state["user_input"] = "What contexts are available?"
        
        result = await app.ainvoke(state, config=config)
        
        print("=== RESULT ===")
        print("Final response:")
        print(result.get("final_response", "No response"))
        print("\n=== DEBUG INFO ===")
        print(f"Context metadata present: {bool(result.get('context_metadata'))}")
        if result.get("context_metadata"):
            print(f"Number of contexts: {len(result['context_metadata'])}")
            print("Context names:", list(result['context_metadata'].keys()))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_context_query())
    sys.exit(0 if success else 1)
