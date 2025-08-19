"""
Information Gatherer node for UpGradeAgent.

This node collects, validates, and prepares all information needed for user requests.
It uses LLM-based intelligence to understand context and progressively gather
the necessary parameters and data.
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


def _build_user_request_context(state: AgentState) -> str:
    """Build user request context information."""
    if state.get("user_request_summary"):
        return f"USER REQUEST: {state['user_request_summary']}"
    return ""


def _build_conversation_history_context(state: AgentState) -> str:
    """Build conversation history context."""
    if not state.get("conversation_history"):
        return ""
    
    recent_history = state["conversation_history"][-5:]  # Last 5 exchanges
    history_text = ""
    for exchange in recent_history:
        history_text += f"User: {exchange.get('user', '')}\nBot: {exchange.get('bot', '')}\n"
    
    return f"RECENT CONVERSATION:\n{history_text}" if history_text else ""


def _build_action_progress_context(state: AgentState) -> str:
    """Build current action progress context."""
    if not state.get("action_needed"):
        return ""
    
    context_parts = [f"CURRENT ACTION IN PROGRESS: {state['action_needed']}"]
    
    if state.get("action_params"):
        context_parts.append(f"COLLECTED PARAMETERS: {state['action_params']}")
    
    if state.get("missing_params"):
        context_parts.append(f"MISSING PARAMETERS: {state['missing_params']}")
    
    return "\n".join(context_parts)


def _build_gathered_info_context(state: AgentState) -> str:
    """Build gathered information context."""
    if not state.get("gathered_info"):
        return ""
    
    info_keys = list(state["gathered_info"].keys())
    return f"ALREADY GATHERED: {', '.join(info_keys)}" if info_keys else ""


def _build_error_context(state: AgentState) -> str:
    """Build error context."""
    if not state.get("errors"):
        return ""
    
    error_messages = [f"{error_type}: {message}" for error_type, message in state["errors"].items()]
    return f"PREVIOUS ERRORS: {'; '.join(error_messages)}" if error_messages else ""


def _build_context_information(state: AgentState) -> str:
    """Build context information from conversation history and current state."""
    context_parts = [
        _build_user_request_context(state),
        _build_conversation_history_context(state),
        _build_action_progress_context(state),
        _build_gathered_info_context(state),
        _build_error_context(state)
    ]
    
    context_info = [part for part in context_parts if part]
    return "\n\n".join(context_info) if context_info else "No additional context available."


def _create_system_prompt(context_info: str) -> str:
    """Create the system prompt for the information gatherer."""
    return f"""You are the Information Gatherer for UpGradeAgent, a chatbot for UpGrade A/B testing platform.

Your role is to collect, validate, and prepare all information needed to fulfill user requests.

CURRENT CONTEXT:
{context_info}

YOUR RESPONSIBILITIES:

1. **Information Collection**: Use available tools to gather necessary data from UpGrade API and documentation
2. **Parameter Validation**: Validate user-provided parameters against UpGrade schemas
3. **Progressive Gathering**: Build complete parameter sets step by step, asking for clarification when needed
4. **Action Preparation**: Set action_needed only when ALL required information is collected and validated

AVAILABLE TOOL CATEGORIES:

**API Functions** (Store results in static variables):
- check_upgrade_health() → stores system health info
- get_context_metadata() → stores available contexts and their details
- get_experiment_names() → stores experiment names and IDs
- get_all_experiments() → stores full experiment details
- get_experiment_details(experiment_id) → stores specific experiment details

**Utility Functions** (Auto-store in gathered_info):
- get_core_terms() → A/B testing terminology and definitions
- get_assignment_terms() → Assignment behavior explanations
- get_available_contexts() → list of available app contexts
- get_create_experiment_schema() → parameters for creating experiments
- get_update_experiment_schema() → parameters for updating experiments
- get_update_experiment_status_schema() → parameters for status changes
- get_delete_experiment_schema() → parameters for deleting experiments
- get_init_experiment_user_schema() → parameters for user initialization
- get_get_decision_point_assignments_schema() → parameters for getting assignments
- get_mark_decision_point_schema() → parameters for marking decision points
- get_conditions_for_context(context) → available conditions for a context
- get_decision_points_for_context(context) → available decision points for a context
- get_group_types_for_context(context) → available group types for a context

**State Management Tools**:
- set_action_needed(action, reasoning) → set what action Tool Executor should perform
- set_action_params(action_params) → set parameters for the action
- set_missing_params(missing_params) → set what parameters are still needed
- update_action_params(key, value) → add/update a specific parameter
- add_error(error_type, message) → record errors when operations fail

WORKFLOW GUIDELINES:

1. **Analyze the Request**: Understand what information or action the user needs
2. **Gather Required Data**: Use appropriate tools to collect necessary information
3. **Validate Parameters**: Check user inputs against schemas and constraints
4. **Handle Missing Information**: Use set_missing_params() if critical info is missing
5. **Prepare Actions**: Use set_action_needed() only when ready for execution
6. **Handle Errors**: Use add_error() to record any failures during gathering

INFORMATION GATHERING PATTERNS:

**For Educational Queries**:
- Use get_core_terms(), get_assignment_terms() for terminology questions
- Use schema tools to explain parameter requirements

**For Experiment Management**:
- Use get_context_metadata() to understand available options
- Use get_experiment_names() to find specific experiments
- Use get_experiment_details() for detailed information
- Validate parameters against appropriate schemas before setting action_needed

**For User Simulation**:
- Use context-specific tools to get available options
- Validate user groups, decision points, and conditions
- Build complete parameter sets progressively

ERROR HANDLING:
- Use add_error() with specific error types: "api", "auth", "validation", "not_found", "unknown"
- Provide helpful error messages that guide users toward solutions
- Don't set action_needed if there are validation errors

PARAMETER COLLECTION:
- Only set action_needed when ALL required parameters are collected and validated
- Use update_action_params() for progressive parameter building
- Provide clear guidance when parameters are missing or invalid
- Default values should be applied automatically where appropriate

Remember: Your goal is to ensure the Tool Executor receives complete, validated parameters for successful API execution."""


async def _execute_tool_calls_and_create_tool_messages(response: AIMessage, state: AgentState) -> list:
    """Execute tool calls and create ToolMessage objects for LangChain."""
    from langchain_core.messages import ToolMessage
    import inspect
    
    tool_messages = []
    gatherer_tools = tool_registry.get_tools_for_node("gatherer")
    
    for tool_call in response.tool_calls:
        try:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call['id']
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            
            if tool_name not in gatherer_tools:
                logger.error(f"Unknown tool requested: {tool_name}")
                tool_result = f"Unknown tool: {tool_name}"
            else:
                tool_func = gatherer_tools[tool_name]
                # Check if tool is async and handle accordingly
                if inspect.iscoroutinefunction(tool_func):
                    tool_result = await tool_func(**tool_args)
                else:
                    tool_result = tool_func(**tool_args)
                logger.info(f"Tool {tool_name} executed successfully")
            
            # Create ToolMessage with the result
            tool_message = ToolMessage(
                content=str(tool_result),
                name=tool_name,
                tool_call_id=tool_id
            )
            tool_messages.append(tool_message)
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_call['name']}: {e}")
            # Create ToolMessage with error
            error_message = ToolMessage(
                content=f"Tool {tool_call['name']} failed: {str(e)}",
                name=tool_call['name'],
                tool_call_id=tool_call['id']
            )
            tool_messages.append(error_message)
    
    return tool_messages


async def _handle_single_iteration(llm_with_tools, conversation: list, state: AgentState) -> tuple[AIMessage, list]:
    """Handle a single iteration of tool calling."""
    # Get LLM response (potentially with tool calls)
    response = cast(AIMessage, llm_with_tools.invoke(conversation))
    
    # Check if there are tool calls to execute
    if not (hasattr(response, 'tool_calls') and response.tool_calls):
        return response, []
    
    # Execute tool calls and create tool messages
    tool_messages = await _execute_tool_calls_and_create_tool_messages(response, state)
    return response, tool_messages


async def _execute_iterative_tool_calls(llm_with_tools, messages: list, state: AgentState, max_iterations: int = 3) -> bool:
    """Execute iterative tool calls until the LLM stops making tool calls or max iterations reached.
    
    Returns:
        bool: True if completed successfully, False if there was an error
    """
    conversation = messages[:]
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        logger.info(f"Tool calling iteration {iteration}/{max_iterations}")
        
        response, tool_messages = await _handle_single_iteration(llm_with_tools, conversation, state)
        conversation.append(response)
        
        # If no tool calls, we're done
        if not tool_messages:
            logger.info(f"Iteration {iteration}: No more tool calls, gathering complete")
            return True
        
        # Continue with next iteration
        conversation.extend(tool_messages)
        logger.info(f"Iteration {iteration}: Executed {len(tool_messages)} tools, continuing...")
    
    # Max iterations reached
    logger.info(f"Max iterations ({max_iterations}) reached, gathering complete")
    return True


async def _process_tool_calls(response: AIMessage, llm_with_tools, messages: list, state: AgentState) -> Dict[str, Any]:
    """Process tool calls from the LLM response using iterative tool calling pattern."""
    if not (hasattr(response, 'tool_calls') and response.tool_calls):
        logger.warning("Gatherer did not make any tool calls")
        # If no tool calls, assume we're providing information based on existing data
        return {"current_state": "RESPONDING"}
    
    logger.info(f"Gatherer made {len(response.tool_calls)} initial tool calls - starting iterative execution")
    
    try:
        # Use iterative tool calling to handle multiple rounds
        success = await _execute_iterative_tool_calls(llm_with_tools, messages, state)
        
        if not success:
            return {
                "current_state": "RESPONDING",
                "errors": {**state.get("errors", {}), "gatherer": "Tool execution failed during iterative processing"}
            }
        
        logger.info("All iterative tool executions completed successfully")
        return {}
        
    except Exception as e:
        logger.error(f"Error in iterative tool calling: {e}")
        return {
            "current_state": "RESPONDING",
            "errors": {**state.get("errors", {}), "gatherer": f"Iterative tool execution failed: {str(e)}"}
        }


async def gatherer_node(state: AgentState) -> Dict[str, Any]:
    """
    Information Gatherer node implementation.
    
    This node collects, validates, and prepares all information needed for user requests.
    It uses LLM-based intelligence to understand context and progressively gather
    the necessary parameters and data.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with state updates
    """
    logger.info("Entering Information Gatherer node")
    
    # Set global state for tools to access
    set_global_state(cast(Dict[str, Any], state))
    
    # Get gatherer tools
    gatherer_tools = list(tool_registry.get_tools_for_node("gatherer").values())
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(gatherer_tools)
    
    # Build context information
    context_info = _build_context_information(state)
    
    # Create system prompt
    system_prompt = _create_system_prompt(context_info)
    
    # Create messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User input: {state['user_input']}")
    ]
    
    try:
        # Get LLM response with tool calls
        response = cast(AIMessage, llm_with_tools.invoke(messages))
        
        # Process tool calls using iterative pattern
        tool_result = await _process_tool_calls(response, llm_with_tools, messages, state)
        if tool_result:  # If there was an error or completion signal
            return tool_result
        
        # Tools have updated the global state, need to get those updates
        from ..tools.decorators import _state_ref
        
        # Determine next state based on what was accomplished
        if state.get("action_needed") or (_state_ref and _state_ref.get("action_needed")):
            # We have an action ready for execution
            next_state = "CONFIRMING"
        elif state.get("missing_params") or (_state_ref and _state_ref.get("missing_params")):
            # We need more information from the user
            next_state = "RESPONDING"
        elif state.get("errors") or (_state_ref and _state_ref.get("errors")):
            # There were errors that need to be communicated
            next_state = "RESPONDING"
        else:
            # We gathered information to answer the question
            next_state = "RESPONDING"
            
        logger.info(f"Gatherer routing to: {next_state}")
        
        # Return state updates including tool modifications
        result = {"current_state": next_state}
        
        # Copy any state updates from tool execution
        if _state_ref:
            # Copy static data fields
            for key in ["context_metadata", "experiment_names", "all_experiments"]:
                if key in _state_ref:
                    result[key] = _state_ref[key]
            
            # Copy gathered_info
            if "gathered_info" in _state_ref:
                result["gathered_info"] = _state_ref["gathered_info"]
            
            # Copy action-related fields  
            for key in ["action_needed", "action_params", "missing_params"]:
                if key in _state_ref:
                    result[key] = _state_ref[key]
            
            # Copy errors
            if "errors" in _state_ref:
                result["errors"] = _state_ref["errors"]
        
        return result
        
    except Exception as e:
        logger.error(f"Error in gatherer node: {e}")
        return {
            "current_state": "RESPONDING",
            "errors": {**state.get("errors", {}), "gatherer": f"Information gathering failed: {str(e)}"}
        }


def gatherer_routing(state: AgentState) -> str:
    """
    Routing function for the Information Gatherer node.
    
    Determines the next node based on what information was gathered
    and whether an action is ready for execution.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name
    """
    # If we have an action ready and all parameters, go to confirmation
    if state.get("action_needed") and not state.get("missing_params"):
        logger.info("Action ready for confirmation, routing to confirmation_handler")
        return "confirmation_handler"
    
    # If we have missing parameters or errors, go to response generator
    if state.get("missing_params") or state.get("errors"):
        logger.info("Missing parameters or errors present, routing to response_generator")
        return "response_generator"
    
    # If we just gathered information to answer a question, go to response generator
    if state.get("gathered_info"):
        logger.info("Information gathered, routing to response_generator")
        return "response_generator"
    
    # Default fallback to response generator
    logger.info("Default routing to response_generator")
    return "response_generator"
