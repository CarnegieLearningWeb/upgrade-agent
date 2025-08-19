#!/usr/bin/env python3
"""
Simple test to check what data is available in final state.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state

async def test_final_state():
    """Check what data is in the final state."""
    print("Testing final state data...")
    
    app = build_upgrade_agent_graph()
    config = create_conversation_config("test_state")
    
    state = create_initial_state()
    state["user_input"] = "What contexts are available?"
    
    result = await app.ainvoke(state, config=config)
    
    print("=== FINAL STATE ANALYSIS ===")
    print(f"Context metadata: {bool(result.get('context_metadata'))}")
    if result.get('context_metadata'):
        print(f"  - Type: {type(result['context_metadata'])}")
        print(f"  - Keys: {list(result['context_metadata'].keys())[:3]}...")  # First 3 keys
    
    print(f"Gathered info: {bool(result.get('gathered_info'))}")
    if result.get('gathered_info'):
        print(f"  - Type: {type(result['gathered_info'])}")
        print(f"  - Keys: {list(result['gathered_info'].keys())}")
        if 'available_contexts' in result['gathered_info']:
            print(f"  - available_contexts: {result['gathered_info']['available_contexts']}")
    
    print(f"Final response length: {len(result.get('final_response', ''))}")
    print(f"Response preview: {result.get('final_response', '')[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_final_state())
