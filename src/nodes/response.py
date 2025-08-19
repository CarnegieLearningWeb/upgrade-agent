"""
Response Generator node for UpGradeAgent.

This node handles all user-facing communication and response formatting.
It's an LLM-based node that formats responses naturally and manages
conversation completion.
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
    """Build conversation context from recent history."""
    if not state.get("conversation_history"):
        return ""
    
    recent_history = state["conversation_history"][-5:]  # Last 5 exchanges
    context = ""
    for exchange in recent_history:
        context += f"User: {exchange.get('user', '')}\nBot: {exchange.get('bot', '')}\n"
    return f"RECENT CONVERSATION:\n{context}" if context else ""


def _build_request_context(state: AgentState) -> str:
    """Build current request context."""
    user_input = state.get("user_input", "")
    user_summary = state.get("user_request_summary", "")
    
    context_parts = [f"CURRENT USER INPUT: {user_input}"]
    if user_summary and user_summary != user_input:
        context_parts.append(f"REQUEST SUMMARY: {user_summary}")
    
    return "\n".join(context_parts)


def _build_state_context(state: AgentState) -> str:
    """Build current conversation state context."""
    current_state = state.get("current_state", "UNKNOWN")
    intent_type = state.get("intent_type", "unknown")
    confidence = state.get("confidence", 0.0)
    
    context_parts = [f"CURRENT STATE: {current_state}"]
    
    if intent_type != "unknown":
        context_parts.append(f"ANALYZED INTENT: {intent_type}")
    
    if confidence and confidence > 0:
        context_parts.append(f"CONFIDENCE: {confidence:.1f}")
    
    return "\n".join(context_parts)


def _build_confirmation_context(state: AgentState) -> str:
    """Build confirmation context if applicable."""
    if not state.get("needs_confirmation"):
        return ""
    
    confirmation_msg = state.get("confirmation_message", "")
    user_confirmed = state.get("user_confirmed")
    
    context_parts = [f"CONFIRMATION REQUIRED: {confirmation_msg}"]
    
    if user_confirmed is not None:
        confirmation_status = "CONFIRMED" if user_confirmed else "DENIED"
        context_parts.append(f"USER RESPONSE: {confirmation_status}")
    
    return "\n".join(context_parts)


def _build_error_context(state: AgentState) -> str:
    """Build error context if any errors occurred."""
    errors = state.get("errors", {})
    if not errors:
        return ""
    
    error_lines = []
    for error_type, message in errors.items():
        error_lines.append(f"{error_type.upper()}: {message}")
    
    return f"ERRORS ENCOUNTERED:\n{chr(10).join(error_lines)}"


def _create_system_prompt(conversation_context: str, request_context: str, 
                         state_context: str, confirmation_context: str, 
                         error_context: str) -> str:
    """Create the system prompt for the response generator."""
    return f"""You are the Response Generator for UpGradeAgent, a chatbot for UpGrade A/B testing platform.

Your role is to provide all user-facing communication in natural, helpful language.

CONTEXT INFORMATION:
{conversation_context}

{request_context}

{state_context}

{confirmation_context}

{error_context}

YOUR RESPONSIBILITIES:

1. **Natural Communication**: Respond in conversational, helpful language
2. **Information Presentation**: Format data clearly and explain next steps
3. **Confirmation Handling**: Present confirmation requests clearly
4. **Error Communication**: Explain errors in user-friendly terms with guidance
5. **Conversation Management**: Determine when conversations are complete

AVAILABLE TOOLS (First call the relevant tools before generating the final response):

**State Access Tools** (Use selectively to avoid token overload):
- get_all_gathered_info() → Get query-specific information collected during this request
- get_execution_log() → Get chronological log of executed actions
- get_errors() → Get detailed error information
- get_action_status() → Get current action and parameter status
- get_user_request_summary() → Get the analyzed request summary

**Large Data Access Tools** (Use only when you can't answer properly after the get_all_gathered_info() tool call):
- get_context_metadata() → Context metadata that includes full list of contexts with supported configurations (use sparingly)
- get_experiment_names() → Full list of experiments with name and IDs (use sparingly)
- get_all_experiments() → Full list of experiments with more details (use sparingly)
- get_conversation_history() → Full conversation history (use sparingly)

**Utility Tools**:
- get_current_state() → Current conversation state

RESPONSE GUIDELINES:

**For Direct Answers**:
- Answer immediately if you have the information
- Use gathered_info for terminology, schemas, or educational content
- Keep responses concise but complete

**For Information Requests**:
- Use gathered_info to present collected data clearly
- Format lists and details in readable formats
- Explain what the information means and suggest next steps

**For Confirmations**:
- Present the confirmation message clearly
- Explain what will happen if they confirm
- Add warnings for destructive actions (⚠️)
- Ask for yes/no response

**For Missing Information**:
- Clearly explain what information is needed
- Provide examples or guidance on acceptable values
- Reference available options from gathered_info

**For Execution Results**:
- Use execution_log to report what was accomplished
- Provide specific details about the results
- Suggest logical next steps

**For Errors**:
- Use get_errors() to get detailed error information
- Explain errors in plain language
- Provide specific guidance on how to fix issues
- Don't expose technical details unless helpful

**Conversation Completion**:
- Mark conversation_complete=True when:
  - User's request has been fully addressed
  - No further action is needed or expected
  - User indicates they're done
- Continue conversation when:
  - Waiting for confirmation response
  - Missing parameters need to be collected
  - User might have follow-up questions

FORMATTING GUIDELINES:

- Use bullet points for lists
- Use clear headings for sections
- Add spacing for readability
- Use **bold** for important information
- Use ⚠️ for warnings
- Use ✅ for successful completions
- Keep technical details minimal unless requested

TOKEN EFFICIENCY:
- Only call large data access tools when you specifically need that data
- Use gathered_info first for most information needs
- Don't call tools unless you need the specific information they provide

Remember: You are the voice of UpGradeAgent. Be helpful, accurate, and conversational while maintaining professionalism."""


def _execute_single_tool_call(tool_call: Any) -> str:
    """Execute a single tool call and return the result string."""
    tool_name = tool_call['name']
    tool_args = tool_call['args']
    
    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
    
    response_tools = tool_registry.get_tools_for_node("response")
    if tool_name not in response_tools:
        logger.error(f"Unknown tool requested: {tool_name}")
        return f"Unknown tool: {tool_name}"
    
    tool_func = response_tools[tool_name]
    try:
        tool_result = tool_func(**tool_args)
        logger.info(f"Tool {tool_name} result: {tool_result}")
        return f"Tool {tool_name}: {tool_result}"
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return f"Tool {tool_name} failed: {str(e)}"


def _extract_text_from_content(content: Any) -> str:
    """Extract text content from LLM response content."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extract text parts from list content
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get('type') == 'text':
                text_parts.append(part.get('text', ''))
            elif isinstance(part, str):
                text_parts.append(part)
        return " ".join(text_parts).strip()
    return ""


def _process_tool_calls(response: AIMessage) -> Dict[str, Any]:
    """Process tool calls from the LLM response."""
    updates = {}
    
    if not (hasattr(response, 'tool_calls') and response.tool_calls):
        # No tool calls - use the response content directly
        if hasattr(response, 'content') and response.content:
            updates["final_response"] = response.content
        else:
            updates["final_response"] = "I apologize, but I'm having trouble generating a response. Please try rephrasing your request."
        return updates
    
    logger.info(f"Response generator made {len(response.tool_calls)} tool calls")
    
    # Execute tool calls to gather additional information
    for tool_call in response.tool_calls:
        _execute_single_tool_call(tool_call)
    
    # Extract text content from response (excluding tool calls)
    text_content = ""
    if hasattr(response, 'content') and response.content:
        text_content = _extract_text_from_content(response.content)
    
    # Use extracted text content or create fallback response
    if text_content:
        updates["final_response"] = text_content
    else:
        # Fallback response - the LLM made tool calls but didn't provide explanatory text
        updates["final_response"] = "I've processed your request and gathered the necessary information to provide a complete response."
    
    return updates


def response_generator_node(state: AgentState) -> Dict[str, Any]:
    """
    Response Generator node implementation.
    
    This node handles all user-facing communication and response formatting.
    It uses LLM intelligence to create natural, helpful responses based on
    the current conversation state and gathered information.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with state updates including final_response
    """
    logger.info("Entering Response Generator node")
    
    # Set global state for tools to access
    set_global_state(cast(Dict[str, Any], state))
    
    # Get response tools
    response_tools = list(tool_registry.get_tools_for_node("response").values())
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(response_tools)
    
    # Build context information
    conversation_context = _build_conversation_context(state)
    request_context = _build_request_context(state)
    state_context = _build_state_context(state)
    confirmation_context = _build_confirmation_context(state)
    error_context = _build_error_context(state)
    
    # Create system prompt
    system_prompt = _create_system_prompt(
        conversation_context, request_context, state_context, 
        confirmation_context, error_context
    )
    
    # Create messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Generate an appropriate response for the user based on the current context.")
    ]
    
    try:
        # Get LLM response with potential tool calls
        response = cast(AIMessage, llm_with_tools.invoke(messages))
        
        # Process tool calls and generate final response
        updates = _process_tool_calls(response)
        
        # Determine if conversation should be complete
        # Conversation is complete if:
        # 1. We provided a direct answer and no further action is expected
        # 2. We executed an action successfully
        # 3. User denied a confirmation (conversation stopped)
        # 4. We're providing error feedback that doesn't require user action
        # 5. We displayed information that doesn't require follow-up
        
        # First, check if we should NOT complete (highest priority)
        should_not_complete = (
            # Waiting for confirmation response
            (state.get("needs_confirmation") and state.get("user_confirmed") is None) or
            # Missing parameters need to be collected
            bool(state.get("missing_params"))
        )
        
        if should_not_complete:
            conversation_complete = False
        else:
            # Check for completion conditions
            conversation_complete = (
                # Direct answer provided
                (state.get("intent_type") == "direct_answer") or
                # User denied confirmation
                (state.get("user_confirmed") is False) or
                # Successful execution completed
                (bool(state.get("execution_log")) and not state.get("errors")) or
                # Error occurred but no missing params to collect
                (bool(state.get("errors")) and not state.get("missing_params")) or
                # Information was gathered and displayed (intent was needs_info but no action/missing params)
                (state.get("intent_type") == "needs_info" and not state.get("action_needed") and not state.get("missing_params"))
            )
        
        updates["conversation_complete"] = conversation_complete
        updates["current_state"] = "RESPONDING"
        
        logger.info(f"Response generated. Conversation complete: {conversation_complete}")
        
        return updates
        
    except Exception as e:
        logger.error(f"Error in response generator node: {e}")
        return {
            "final_response": f"I apologize, but I encountered an error while generating a response: {str(e)}",
            "conversation_complete": True,
            "current_state": "RESPONDING",
            "errors": {**state.get("errors", {}), "response": f"Response generation failed: {str(e)}"}
        }


def response_routing(state: AgentState) -> str:
    """
    Routing function for the Response Generator node.
    
    Determines whether the conversation is complete or if we need to
    continue to the analyzer for further processing.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END if conversation is complete
    """
    if state.get("conversation_complete"):
        logger.info("Conversation complete, ending")
        return "END"
    else:
        # If we showed a confirmation and are waiting for user response,
        # the next user input should go back to the analyzer
        logger.info("Conversation continuing, routing to conversation_analyzer")
        return "conversation_analyzer"
