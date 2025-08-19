#!/usr/bin/env python3
"""
Test with detailed logging to see what's happening.
"""

import asyncio
import sys
import os
import logging

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state


async def test_with_logging():
    """Test with detailed logging."""
    print("Testing with detailed logging...")
    
    try:
        app = build_upgrade_agent_graph()
        config = create_conversation_config("test_logging")
        
        state = create_initial_state()
        state["user_input"] = "What contexts are available?"
        
        result = await app.ainvoke(state, config=config)
        
        print("\n=== FINAL STATE ===")
        print(f"Context metadata in final state: {bool(result.get('context_metadata'))}")
        if result.get("context_metadata"):
            print(f"Keys: {list(result['context_metadata'].keys())}")
        
        print(f"\nFinal response: {result.get('final_response', 'No response')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_with_logging())
    sys.exit(0 if success else 1)
