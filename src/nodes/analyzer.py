"""
Conversation Analyzer Node.

This node handles intent classification and conversation orchestration.
It determines whether user queries can be answered directly or need more information.
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
analyzer_tools = get_tools_for_node("analyzer")

# Bind tools to LLM
llm_with_tools = llm.bind_tools(list(analyzer_tools.values()))


def analyzer_node(state: AgentState) -> AgentState:
    """
    Conversation Analyzer node implementation.
    
    This node classifies user intent and determines the next action in the conversation flow.
    It decides whether a query can be answered directly or needs information gathering.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with intent classification
    """
    
    # Update current state
    state["current_state"] = "ANALYZING"
    
    # Create the prompt for intent analysis
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a conversation analyzer for an A/B testing chatbot.

Your job is to analyze user input and classify the intent:

1. **direct_answer**: The query can be answered with existing knowledge (definitions, explanations, static info)
2. **needs_info**: The query requires gathering information from APIs or performing actions

Consider the conversation history and current context. Use the analyze_user_request tool to classify the intent.

Examples of direct_answer:
- "What is A/B testing?"
- "Explain assignment consistency"  
- "What does post-experiment rule mean?"

Examples of needs_info:
- "List my experiments"
- "Create an experiment called Math Hints"
- "What's the status of experiment ABC?"
- "Delete the old experiment"

Be confident in your classification and provide clear reasoning."""),
        
        ("human", """Current user input: {user_input}

Conversation history: {conversation_history}

Please analyze this input and classify the intent using the analyze_user_request tool.""")
    ])
    
    # Create the chain
    chain = prompt | llm_with_tools
    
    # Invoke the chain
    chain.invoke({
        "user_input": state["user_input"],
        "conversation_history": state.get("conversation_history", [])
    })
    
    # The tool calls will have updated the state through decorators
    # Add this conversation turn to history
    if "conversation_history" not in state:
        state["conversation_history"] = []
    
    state["conversation_history"].append({
        "role": "user",
        "content": state["user_input"],
        "timestamp": "now"
    })
    
    return state
