"""
Response Generator Node.

This node handles all user-facing communication and response formatting.
It accesses state data and formats responses in natural, helpful language.
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
    temperature=0.3  # Slightly higher temperature for more natural responses
)

# Get tools for this node
response_tools = get_tools_for_node("response")

# Bind tools to LLM (done lazily to avoid import issues)
llm_with_tools = None

def get_llm_with_tools():
    """Get LLM with tools bound (lazy initialization)."""
    global llm_with_tools
    if llm_with_tools is None:
        llm_with_tools = llm.bind_tools(list(response_tools.values()))
    return llm_with_tools


def response_node(state: AgentState) -> AgentState:
    """
    Response Generator node implementation.
    
    This node formats all responses in natural, helpful language and
    determines when conversations are complete.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with final response
    """
    
    # Update current state
    state["current_state"] = "RESPONDING"
    
    # TODO: Implement LLM-based response generation
    # This will use response tools to:
    # 1. Access large static data when needed
    # 2. Get gathered information for query-specific responses
    # 3. Format confirmation requests
    # 4. Explain results and provide next steps
    # 5. Handle error communication
    
    # For now, create a simple placeholder response
    user_input = state.get("user_input", "")
    intent_type = state.get("intent_type")
    errors = state.get("errors", {})
    confirmation_message = state.get("confirmation_message")
    
    if errors:
        # Handle errors
        error_msgs = []
        for error_type, error_msg in errors.items():
            error_msgs.append(f"{error_type}: {error_msg}")
        response = f"I encountered some issues: {'; '.join(error_msgs)}"
        
    elif confirmation_message:
        # Show confirmation request
        response = f"{confirmation_message}\n\nPlease respond with 'yes' to confirm or 'no' to cancel."
        
    elif intent_type == "direct_answer":
        # Provide direct answer (placeholder)
        response = f"I can provide information about: {user_input}. (Direct answer implementation pending)"
        
    elif intent_type == "needs_info":
        # Information gathering response (placeholder)
        response = f"I'm gathering information for: {user_input}. (Info gathering implementation pending)"
        
    else:
        # Default response
        response = "I'm processing your request. Please wait..."
    
    state["final_response"] = response
    
    # For now, mark conversations as complete after one response
    # In the real implementation, this would check various conditions
    state["conversation_complete"] = True
    
    return state
