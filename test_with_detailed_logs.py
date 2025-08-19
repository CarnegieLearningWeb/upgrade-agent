#!/usr/bin/env python3
"""
Test with detailed logging to understand tool execution.
"""

import asyncio
import sys
import os
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state

async def test_with_logs():
    """Test with detailed logs to see tool execution."""
    print("Testing with detailed logging...")
    
    app = build_upgrade_agent_graph()
    config = create_conversation_config("test_detailed")
    
    state = create_initial_state()
    state["user_input"] = "What contexts are available?"
    
    result = await app.ainvoke(state, config=config)
    
    print("\n=== FINAL ANALYSIS ===")
    print(f"Response length: {len(result.get('final_response', ''))}")
    print(f"Full response: '{result.get('final_response', 'No response')}'")
    print(f"Context metadata available: {bool(result.get('context_metadata'))}")
    if result.get('context_metadata'):
        print(f"Number of contexts: {len(result['context_metadata'])}")

if __name__ == "__main__":
    asyncio.run(test_with_logs())
