#!/usr/bin/env python3
"""
Debug what tools are actually being called.
"""

import asyncio
import sys
import os
import logging

# Set up logging to capture tool calls
logging.basicConfig(level=logging.INFO)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state

async def test_tool_calls():
    """Test and see what tools are actually called."""
    print("Testing tool calls...")
    
    app = build_upgrade_agent_graph()
    config = create_conversation_config("test_tools")
    
    state = create_initial_state()
    state["user_input"] = "What contexts are available?"
    
    # Capture logs
    tool_calls = []
    original_info = logging.getLogger('src.nodes.response').info
    
    def capture_tool_calls(msg):
        if "Tool" in msg and "result:" in msg:
            tool_calls.append(msg)
        original_info(msg)
    
    logging.getLogger('src.nodes.response').info = capture_tool_calls
    
    try:
        result = await app.ainvoke(state, config=config)
        
        print("\n=== TOOL CALLS MADE BY RESPONSE GENERATOR ===")
        for call in tool_calls:
            print(call)
        
        print(f"\n=== FINAL STATE ===")
        print(f"Context metadata present: {bool(result.get('context_metadata'))}")
        print(f"Gathered info present: {bool(result.get('gathered_info'))}")
        if result.get('gathered_info'):
            print(f"Gathered info keys: {list(result['gathered_info'].keys())}")
        
        print(f"\nResponse: {result.get('final_response', 'No response')}")
        
    finally:
        # Restore original logging
        logging.getLogger('src.nodes.response').info = original_info

if __name__ == "__main__":
    asyncio.run(test_tool_calls())
