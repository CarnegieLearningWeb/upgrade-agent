"""
Debug script to check what tools are registered for the gatherer node.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.registry import tool_registry


def debug_tools():
    """Check what tools are registered for each node."""
    print("Debugging tool registry...")
    
    # Import all tools to trigger registration
    try:
        from src.tools.gatherer import api_tools, utility_tools, state_tools
        from src.tools.analyzer import intent_tools
        print("✅ All tools imported successfully")
    except Exception as e:
        print(f"❌ Error importing tools: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check what's registered
    all_tools_by_node = tool_registry.list_tools_by_node()
    
    for node, tools in all_tools_by_node.items():
        print(f"\n{node.upper()} NODE TOOLS:")
        for tool_name in tools:
            print(f"  - {tool_name}")
    
    # Try getting gatherer tools specifically
    print("\nGATHERER TOOLS DETAILS:")
    gatherer_tools = tool_registry.get_tools_for_node("gatherer")
    for name, tool_func in gatherer_tools.items():
        print(f"  {name}: {type(tool_func)} - {tool_func}")
        
        # Check if it's async
        import inspect
        if inspect.iscoroutinefunction(tool_func):
            print(f"    WARNING: {name} is async!")


if __name__ == "__main__":
    debug_tools()
