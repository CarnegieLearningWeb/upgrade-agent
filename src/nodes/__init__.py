"""
Node implementations for UpGradeAgent LangGraph.

This package contains the single-node architecture implementation:
- Intelligent Agent (LLM) - Handles all requests end-to-end with iterative tool calling

The original 5-node architecture implementations are also available for reference:
- Conversation Analyzer (LLM)
- Information Gatherer (LLM) 
- Confirmation Handler (Non-LLM)
- Tool Executor (Non-LLM)
- Response Generator (LLM)
"""

from .intelligent_agent import intelligent_agent_node, intelligent_agent_routing
from .analyzer import analyzer_node, analyzer_routing
from .gatherer import gatherer_node, gatherer_routing
from .confirmation import confirmation_handler, confirmation_routing
from .executor import tool_executor, executor_routing
from .response import response_generator_node, response_routing

__all__ = [
    "intelligent_agent_node",
    "intelligent_agent_routing",
    "analyzer_node",
    "analyzer_routing", 
    "gatherer_node",
    "gatherer_routing",
    "confirmation_handler",
    "confirmation_routing",
    "tool_executor", 
    "executor_routing",
    "response_generator_node",
    "response_routing"
]
