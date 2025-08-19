"""
Conversation Analyzer node for UpGradeAgent.

This node serves as the central orchestrator that classifies user intent
and manages conversation flow in the LangGraph architecture.
"""

import logging
from typing import Dict, Any, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import SecretStr

from ..config.config import config
from ..graph.state import AgentState
from ..tools.decorators import set_global_state
from ..tools.registry import tool_registry

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatAnthropic(
    api_key=SecretStr(config.ANTHROPIC_API_KEY),
    model_name=config.MODEL_NAME,
    temperature=0.1,
    timeout=30,
    stop=None
)


def _build_conversation_context(state: AgentState) -> str:
    """Build conversation context from history."""
    if not state.get("conversation_history"):
        return ""
    
    recent_history = state["conversation_history"][-10:]  # Last 10 exchanges
    context = ""
    for exchange in recent_history:
        context += f"User: {exchange.get('user', '')}\nBot: {exchange.get('bot', '')}\n"
    return context


def _check_confirmation_context(state: AgentState) -> str:
    """Check if user is responding to a confirmation request."""
    if not (state.get("needs_confirmation") and state.get("confirmation_message")):
        return ""
    
    user_input_lower = state["user_input"].lower().strip()
    if any(word in user_input_lower for word in ["yes", "y", "confirm", "ok", "proceed", "go ahead"]):
        return "The user has CONFIRMED the pending action. Proceed accordingly."
    elif any(word in user_input_lower for word in ["no", "n", "cancel", "stop", "abort", "deny"]):
        return "The user has DENIED/CANCELLED the pending action. Do not proceed."
    return ""


def _create_system_prompt(conversation_context: str, confirmation_context: str) -> str:
    """Create the system prompt for the analyzer."""
    return f"""You are the Conversation Analyzer for UpGradeAgent, a chatbot for UpGrade A/B testing platform.

Your role is to analyze user input and classify intent to orchestrate the conversation flow.

CURRENT CONVERSATION CONTEXT:
{conversation_context}

{confirmation_context}

CLASSIFICATION GUIDELINES:

1. **direct_answer**: Choose when you can provide a complete answer immediately:
   - Greetings
   - Questions you can answer without needing specific information
   - Questions you can answer certainly based on the previous converstaion context
   - Totally unrelated questions that doesn't need clarifications

2. **needs_info**: Choose when you need to gather more information:
   - Terminology/concepts that might be used in UpGrade
   - Creating, updating, or deleting experiments
   - Checking specific experiment details or status
   - User simulation tasks (initialization, assignments, decision points)
   - Requests requiring specific data from UpGrade API
   - Complex queries needing parameter collection

CONVERSATION FLOW MANAGEMENT:
- If user is confirming/denying a previous action, classify appropriately
- Consider conversation history and references to "that experiment", "the one we created", etc.
- Pay attention to ambiguous requests that need clarification
- Look for implied context from previous exchanges

CONFIDENCE LEVELS:
- 0.9-1.0: Very clear intent, unambiguous request
- 0.7-0.8: Clear intent with minor ambiguity
- 0.5-0.6: Moderate confidence, some clarification may be needed
- 0.3-0.4: Low confidence, significant ambiguity
- 0.0-0.2: Very unclear intent

You MUST use the analyze_user_request tool to classify the intent."""


def _process_tool_calls(response: AIMessage, state: AgentState) -> Dict[str, Any]:
    """Process tool calls from the LLM response."""
    if not (hasattr(response, 'tool_calls') and response.tool_calls):
        logger.warning("Analyzer did not make any tool calls")
        return {
            "current_state": "RESPONDING",
            "intent_type": "direct_answer",
            "confidence": 0.3,
            "user_request_summary": state["user_input"]
        }
    
    logger.info(f"Analyzer made {len(response.tool_calls)} tool calls")
    
    # Execute each tool call (should be just analyze_user_request)
    for tool_call in response.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        
        # Get the tool function
        analyzer_tools = tool_registry.get_tools_for_node("analyzer")
        if tool_name in analyzer_tools:
            tool_func = analyzer_tools[tool_name]
            try:
                # Tool functions are langchain tools, call them directly
                tool_result = tool_func(**tool_args)
                logger.info(f"Tool {tool_name} result: {tool_result}")
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                return {
                    "current_state": "RESPONDING",
                    "errors": {**state.get("errors", {}), "analyzer": f"Tool execution failed: {str(e)}"}
                }
        else:
            logger.error(f"Unknown tool requested: {tool_name}")
            return {
                "current_state": "RESPONDING", 
                "errors": {**state.get("errors", {}), "analyzer": f"Unknown tool: {tool_name}"}
            }
    
    return {}


def analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    Conversation Analyzer node implementation.
    
    This node classifies user intent, understands conversation context,
    and provides orchestration for the overall conversation flow.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with state updates
    """
    logger.info("Entering Conversation Analyzer node")
    
    # Set global state for tools to access
    set_global_state(cast(Dict[str, Any], state))
    
    # Get analyzer tools
    analyzer_tools = list(tool_registry.get_tools_for_node("analyzer").values())
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(analyzer_tools)
    
    # Build conversation context
    conversation_context = _build_conversation_context(state)
    confirmation_context = _check_confirmation_context(state)
    
    # Create system prompt
    system_prompt = _create_system_prompt(conversation_context, confirmation_context)
    
    # Create messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User input: {state['user_input']}")
    ]
    
    try:
        # Get LLM response with tool calls
        response = cast(AIMessage, llm_with_tools.invoke(messages))
        
        # Process tool calls
        tool_result = _process_tool_calls(response, state)
        if tool_result:  # If there was an error or default fallback
            return tool_result
        
        # Determine next state based on intent_type
        intent_type = state.get("intent_type")
        
        if intent_type == "direct_answer":
            next_state = "RESPONDING"
        elif intent_type == "needs_info":
            next_state = "GATHERING_INFO"
        else:
            next_state = "RESPONDING"  # Default fallback
            
        logger.info(f"Analyzer routing to: {next_state}")
        
        return {"current_state": next_state}
        
    except Exception as e:
        logger.error(f"Error in analyzer node: {e}")
        return {
            "current_state": "RESPONDING",
            "errors": {**state.get("errors", {}), "analyzer": f"Analysis failed: {str(e)}"}
        }


def analyzer_routing(state: AgentState) -> str:
    """
    Routing function for the Conversation Analyzer node.
    
    Determines the next node based on analyzed intent and conversation state.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name
    """
    # Handle confirmation flow
    if state.get("needs_confirmation") and state.get("confirmation_message"):
        user_input_lower = state["user_input"].lower().strip()
        
        # Check for confirmation
        if any(word in user_input_lower for word in ["yes", "y", "confirm", "ok", "proceed", "go ahead"]):
            logger.info("User confirmed action, routing to tool_executor")
            return "tool_executor"
        elif any(word in user_input_lower for word in ["no", "n", "cancel", "stop", "abort", "deny"]):
            logger.info("User denied action, routing to response_generator")
            return "response_generator"
    
    # Check if we just executed something and need to analyze results
    if state.get("execution_log") and state.get("current_state") == "ANALYZING":
        logger.info("Post-execution analysis, routing to response_generator")
        return "response_generator"
    
    # Route based on intent classification
    intent_type = state.get("intent_type")
    
    if intent_type == "direct_answer":
        logger.info("Direct answer intent, routing to response_generator")
        return "response_generator"
    elif intent_type == "needs_info":
        logger.info("Needs info intent, routing to information_gatherer")
        return "information_gatherer"
    else:
        logger.info("No clear intent, routing to response_generator")
        return "response_generator"
