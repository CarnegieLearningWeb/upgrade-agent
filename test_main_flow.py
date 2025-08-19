#!/usr/bin/env python3
"""
Test the main UpGradeAgent flow.

This script tests the complete LangGraph workflow with a simple interaction.
Useful for debugging and verifying the graph works correctly.

Usage:
    python test_main_flow.py

This file serves as a reference for:
- How to build and use the UpGradeAgent graph
- Basic interaction patterns
- Debugging workflow issues
"""

import asyncio
import sys
import os

# Add src to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state


async def test_main_flow():
    """Test the main conversation flow with a few exchanges."""
    print("Testing main conversation flow...")
    
    try:
        # Build the graph
        app = build_upgrade_agent_graph()
        config = create_conversation_config("test_session")
        
        # Test a few different types of inputs
        test_inputs = [
            "Hello",
            "What is A/B testing?",
            "What contexts are available?",
            "quit"
        ]
        
        for i, user_input in enumerate(test_inputs):
            print(f"\n--- Exchange {i+1} ---")
            print(f"User: {user_input}")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Bot: 👋 Thank you for using UpGradeAgent! Goodbye!")
                break
            
            # Process input
            initial_state = create_initial_state()
            initial_state["user_input"] = user_input
            
            result = await app.ainvoke(initial_state, config=config)
            response = result.get("final_response", "No response generated")
            
            print(f"Bot: {response}")
        
        print("\n✅ Main conversation flow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_main_flow())
    sys.exit(0 if success else 1)
