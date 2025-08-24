"""
UpGradeAgent Tools Package.

This package contains all tool functions organized by LangGraph node type.
Tools are automatically registered and enforce architectural boundaries.
"""

from .decorators import (
    set_global_state,
    auto_store,
    auto_store_static,
    handle_errors
)

from .registry import (
    tool_registry,
    # register_analyzer_tool,
    register_gatherer_tool,
    register_executor_tool,
    register_response_tool,
    get_tools_for_node,
    get_all_tools
)

# Import tool modules to trigger registration
try:
    from . import analyzer
    from . import gatherer
    from . import executor
    from . import response
except ImportError:
    # Handle import errors gracefully during development
    pass


__all__ = [
    # Decorators
    "set_global_state",
    "auto_store",
    "auto_store_static", 
    "handle_errors",
    
    # Registry
    "tool_registry",
    # "register_analyzer_tool",
    "register_gatherer_tool",
    "register_executor_tool",
    "register_response_tool",
    "get_tools_for_node",
    "get_all_tools"
]
