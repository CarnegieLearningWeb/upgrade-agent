"""
Information Gatherer Node.

This node handles data collection, validation, and parameter building.
It gathers all information needed for user requests and validates parameters.
"""

from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from src.graph.state import AgentState
from src.tools import get_tools_for_node
from src.config.config import config


# Create the LLM instance  
llm = ChatAnthropic(
    model=config.MODEL_NAME,
    api_key=config.ANTHROPIC_API_KEY,
    temperature=0.1
)

# Get tools for this node
gatherer_tools = get_tools_for_node("gatherer")

# Bind tools to LLM (done lazily to avoid import issues)
llm_with_tools = None

def get_llm_with_tools():
    """Get LLM with tools bound (lazy initialization)."""
    global llm_with_tools
    if llm_with_tools is None:
        llm_with_tools = llm.bind_tools(list(gatherer_tools.values()))
    return llm_with_tools


def gatherer_node(state: AgentState) -> AgentState:
    """
    Information Gatherer node implementation.
    
    This node collects, validates, and prepares all information needed for user requests.
    It uses various tools to gather data from APIs and build complete parameter sets.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with gathered information
    """
    
    # Update current state
    state["current_state"] = "GATHERING_INFO"
    
    # TODO: Implement LLM-based information gathering logic
    # This will use the gatherer tools to:
    # 1. Collect API data as needed
    # 2. Validate user parameters
    # 3. Build complete parameter sets
    # 4. Set action_needed when ready
    # 5. Identify missing_params when more info needed
    
    # For now, just mark as placeholder
    if "gathered_info" not in state:
        state["gathered_info"] = {}
    
    state["gathered_info"]["placeholder"] = "Gatherer node implementation pending"
    
    return state
