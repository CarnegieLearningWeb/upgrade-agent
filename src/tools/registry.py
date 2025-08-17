"""
Tool registry for UpGradeAgent.

This module manages tool organization, access control, and registration
for the 5-node LangGraph architecture.
"""

from typing import Dict, List, Callable, Any
from enum import Enum

from src.models.enums import NodeType


class ToolRegistry:
    """
    Registry for managing tools across different nodes.
    
    Enforces node-specific tool access patterns to maintain
    architectural boundaries in the LangGraph implementation.
    """
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Callable]] = {
            "analyzer": {},
            "gatherer": {},
            "executor": {},
            "response": {}
        }
        
    def register_tool(self, node_type: str, tool_name: str, tool_func: Callable) -> None:
        """
        Register a tool for a specific node type.
        
        Args:
            node_type: The node type ("analyzer", "gatherer", "executor", "response")
            tool_name: Name of the tool
            tool_func: The tool function
        """
        if node_type not in self._tools:
            raise ValueError(f"Invalid node type: {node_type}")
        
        self._tools[node_type][tool_name] = tool_func
        
    def get_tools_for_node(self, node_type: str) -> Dict[str, Callable]:
        """
        Get all tools available for a specific node type.
        
        Args:
            node_type: The node type to get tools for
            
        Returns:
            Dictionary of tool names to tool functions
        """
        if node_type not in self._tools:
            raise ValueError(f"Invalid node type: {node_type}")
        
        return self._tools[node_type].copy()
    
    def get_all_tools(self) -> Dict[str, Callable]:
        """
        Get all tools from all nodes (useful for LangGraph tool executor).
        
        Returns:
            Dictionary of all tool names to tool functions
        """
        all_tools = {}
        for node_tools in self._tools.values():
            all_tools.update(node_tools)
        return all_tools
    
    def list_tools_by_node(self) -> Dict[str, List[str]]:
        """
        List all tool names organized by node type.
        
        Returns:
            Dictionary mapping node types to lists of tool names
        """
        return {
            node_type: list(tools.keys())
            for node_type, tools in self._tools.items()
        }


# Global registry instance
tool_registry = ToolRegistry()


def register_analyzer_tool(tool_name: str):
    """Decorator to register a tool for the Conversation Analyzer node."""
    def decorator(func: Callable) -> Callable:
        tool_registry.register_tool("analyzer", tool_name, func)
        return func
    return decorator


def register_gatherer_tool(tool_name: str):
    """Decorator to register a tool for the Information Gatherer node."""
    def decorator(func: Callable) -> Callable:
        tool_registry.register_tool("gatherer", tool_name, func)
        return func
    return decorator


def register_executor_tool(tool_name: str):
    """Decorator to register a tool for the Tool Executor node."""
    def decorator(func: Callable) -> Callable:
        tool_registry.register_tool("executor", tool_name, func)
        return func
    return decorator


def register_response_tool(tool_name: str):
    """Decorator to register a tool for the Response Generator node."""
    def decorator(func: Callable) -> Callable:
        tool_registry.register_tool("response", tool_name, func)
        return func
    return decorator


def get_tools_for_node(node_type: str) -> Dict[str, Callable]:
    """Convenience function to get tools for a node type."""
    return tool_registry.get_tools_for_node(node_type)


def get_all_tools() -> Dict[str, Callable]:
    """Convenience function to get all tools."""
    return tool_registry.get_all_tools()
