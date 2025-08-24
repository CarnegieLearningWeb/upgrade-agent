"""
Intelligent Agent node for UpGradeAgent.

This is a single node that combines all functionality from the 5-node architecture
into one intelligent agent with LLM that can iteratively call all available tools
until it finds all the information needed to properly answer or execute user requests.
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
    timeout=config.ANTHROPIC_API_TIMEOUT,
    model_name=config.ANTHROPIC_MODEL_NAME,
    temperature=0.1,
    stop=None
)


def _build_conversation_context(state: AgentState) -> str:
    """Build conversation context from state."""
    context_parts = []
    
    # Add conversation history
    if state.get("conversation_history"):
        recent_history = state["conversation_history"][-10:]  # Last 10 exchanges
        history_text = ""
        for exchange in recent_history:
            history_text += f"User: {exchange.get('user', '')}\nBot: {exchange.get('bot', '')}\n"
        
        if history_text:
            context_parts.append(f"RECENT CONVERSATION:\n{history_text}")
    
    # Add any gathered info
    if state.get("gathered_info"):
        info_keys = list(state["gathered_info"].keys())
        context_parts.append(f"PREVIOUSLY GATHERED INFO: {', '.join(info_keys)}")
    
    # Add execution log if any
    if state.get("execution_log"):
        recent_executions = state["execution_log"][-10:]  # Last 10 executions
        exec_summary = []
        for exec_log in recent_executions:
            status = exec_log.get("status", "unknown")
            action = exec_log.get("action", "unknown")
            exec_summary.append(f"{action} ({status})")
        context_parts.append(f"RECENT EXECUTIONS: {', '.join(exec_summary)}")
    
    # Add any errors
    if state.get("errors"):
        error_messages = [f"{error_type}: {message}" for error_type, message in state["errors"].items()]
        context_parts.append(f"PREVIOUS ERRORS: {'; '.join(error_messages)}")
    
    return "\n\n".join(context_parts) if context_parts else "No additional context available."


def _create_system_prompt(context_info: str) -> str:
    """Create the system prompt for the intelligent agent."""
    return f"""You are UpGradeAgent, an intelligent AI assistant for the UpGrade A/B testing platform. 
You can help users with everything related to UpGrade - from explaining concepts to managing experiments to simulating user interactions.

CURRENT CONTEXT:
{context_info}

You have access to comprehensive tools for information gathering, experiment management, user simulation, and system administration. Use them iteratively to fully handle user requests.

BEHAVIOR GUIDELINES:

1. **Be Direct and Concise**: Give clear, brief answers by default. Only provide detailed explanations when:
   - User explicitly asks for details/examples
   - Explaining complex concepts that require context
   - Error situations that need troubleshooting guidance

2. **Use Iterative Tool Calling**: Feel free to call multiple tools in sequence to gather all needed information. 
   Don't hesitate to make follow-up tool calls based on the results of previous calls.

3. **Handle Everything End-to-End**: 
   - For questions: Gather info and provide focused answers
   - For actions: Collect required parameters, validate them, and execute directly
   - No need to ask for confirmation before executing tools (including delete_experiment)

4. **Be Smart About Information Gathering**:
   - Validate parameters against schemas before execution
   - Use context metadata to understand what options are available
   - Look up experiment IDs from names when needed
   - Gather missing information progressively

5. **Response Format**:
   - Use bullet points for lists and multiple items
   - Lead with the direct answer, then supporting details if needed
   - For successful actions, confirm briefly what was done
   - For errors, explain what went wrong and suggest solutions concisely

6. **No Confirmation Required**: You can execute all tools directly, including potentially destructive ones 
   like delete_experiment. The goal is to make the app work simply and straightforwardly.

EXAMPLE WORKFLOWS:

User: "What contexts are available?"
→ Call get_available_contexts() 
→ Response: "Available contexts: assign-prog, retail-app, survey-tool"

User: "Create an experiment called 'Math Hints' in assign-prog context"
→ Call get_create_experiment_schema() to check the required params
→ Call get_available_contexts() to validate context
→ Call get_decision_points_for_context() and get_conditions_for_context() to get available options
→ Once all params collected, call create_experiment()
→ Response: "✅ Created 'Math Hints' experiment in assign-prog context with control/treatment conditions."

User: "Delete the Math Hints experiment"
→ Call get_experiment_names() to find experiment ID  
→ Call delete_experiment() directly
→ Response: "✅ Deleted 'Math Hints' experiment."

Remember: Be concise but complete. Work iteratively until you have fully addressed the user's request.
Offer more details only if asked or if the situation requires explanation."""


async def _execute_tool_calls_and_create_tool_messages(response: AIMessage, state: AgentState) -> list:
    """Execute tool calls and create ToolMessage objects for LangChain."""
    from langchain_core.messages import ToolMessage
    import inspect
    
    tool_messages = []
    
    # Get all tools from all categories, handling duplicates properly
    # Priority: gatherer > executor > analyzer > response (gatherer tools are more comprehensive)
    all_tools = {}
    
    # Start with response tools (lowest priority)
    response_tools = tool_registry.get_tools_for_node("response")
    all_tools.update(response_tools)
    
    # Add analyzer tools (these shouldn't overlap)
    analyzer_tools = tool_registry.get_tools_for_node("analyzer")
    all_tools.update(analyzer_tools)
    
    # Add executor tools (these shouldn't overlap)
    executor_tools = tool_registry.get_tools_for_node("executor")
    all_tools.update(executor_tools)
    
    # Add gatherer tools (highest priority, will overwrite any duplicates)
    gatherer_tools = tool_registry.get_tools_for_node("gatherer")
    all_tools.update(gatherer_tools)
    
    for tool_call in response.tool_calls:
        try:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call['id']
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            
            if tool_name not in all_tools:
                logger.error(f"Unknown tool requested: {tool_name}")
                tool_result = f"Unknown tool: {tool_name}"
            else:
                tool_func = all_tools[tool_name]
                # Use LangChain's proper tool invocation method
                if hasattr(tool_func, 'ainvoke'):
                    tool_result = await tool_func.ainvoke(tool_args)
                elif hasattr(tool_func, 'invoke'):
                    tool_result = tool_func.invoke(tool_args)
                else:
                    # Fallback to direct function call for non-LangChain tools
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


async def _execute_iterative_tool_calls(llm_with_tools, messages: list, state: AgentState, max_iterations: int = 30) -> tuple[bool, str]:
    """Execute iterative tool calls until the LLM provides a final response.
    
    Returns:
        tuple: (success: bool, final_response: str)
    """
    conversation = messages[:]
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        logger.info(f"Tool calling iteration {iteration}/{max_iterations}")
        
        response, tool_messages = await _handle_single_iteration(llm_with_tools, conversation, state)
        conversation.append(response)
        
        # If no tool calls, we have the final response
        if not tool_messages:
            logger.info(f"Iteration {iteration}: Final response received")
            return True, response.content # type: ignore
        
        # Continue with next iteration
        conversation.extend(tool_messages)
        logger.info(f"Iteration {iteration}: Executed {len(tool_messages)} tools, continuing...")
    
    # Max iterations reached, return the last response
    logger.warning(f"Max iterations ({max_iterations}) reached")
    return True, conversation[-1].content if conversation else "I apologize, but I couldn't complete your request within the allowed processing time."


async def intelligent_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Single intelligent agent node that can handle all user requests end-to-end.
    
    This node combines all functionality from the original 5-node architecture
    into one intelligent agent that can iteratively call tools until it has
    all the information needed to fully address user requests.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with state updates including final_response
    """
    logger.info("Entering Intelligent Agent node")
    
    # Set global state for tools to access
    set_global_state(cast(Dict[str, Any], state))
    
    # Get all available tools, handling duplicates properly
    # Priority: gatherer > executor > analyzer > response (gatherer tools are more comprehensive)
    all_tools_dict = {}
    
    # Start with response tools (lowest priority)
    response_tools = tool_registry.get_tools_for_node("response")
    all_tools_dict.update(response_tools)
    
    # Add analyzer tools (these shouldn't overlap)
    analyzer_tools = tool_registry.get_tools_for_node("analyzer")
    all_tools_dict.update(analyzer_tools)
    
    # Add executor tools (these shouldn't overlap)
    executor_tools = tool_registry.get_tools_for_node("executor")
    all_tools_dict.update(executor_tools)
    
    # Add gatherer tools (highest priority, will overwrite any duplicates)
    gatherer_tools = tool_registry.get_tools_for_node("gatherer")
    all_tools_dict.update(gatherer_tools)
    
    # Convert to list for LLM binding
    all_tools = list(all_tools_dict.values())
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(all_tools)
    
    # Build context information
    context_info = _build_conversation_context(state)
    
    # Create system prompt
    system_prompt = _create_system_prompt(context_info)
    
    # Create messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User input: {state['user_input']}")
    ]
    
    try:
        # Execute iterative tool calling to get final response
        success, final_response = await _execute_iterative_tool_calls(llm_with_tools, messages, state)
        
        if not success:
            final_response = "I apologize, but I encountered an error while processing your request. Please try again."
        
        # Update conversation history with this exchange
        conversation_history = state.get("conversation_history", [])
        conversation_history.append({
            "user": state["user_input"],
            "bot": final_response
        })
        
        # Get any state updates from tool execution
        result = {
            "final_response": final_response,
            "conversation_complete": True,
            "current_state": "RESPONDING",
            "conversation_history": conversation_history
        }
        
        # Copy any state updates from tool execution
        from ..tools.decorators import _state_ref
        if _state_ref:
            # Copy static data fields
            for key in ["context_metadata", "experiment_names", "all_experiments"]:
                if key in _state_ref:
                    result[key] = _state_ref[key]
            
            # Copy gathered_info
            if "gathered_info" in _state_ref:
                current_gathered = state.get("gathered_info", {})
                new_gathered = _state_ref["gathered_info"]
                result["gathered_info"] = {**current_gathered, **new_gathered}
            
            # Copy action-related fields (for debugging/logging)
            for key in ["action_needed", "action_params", "missing_params"]:
                if key in _state_ref:
                    result[key] = _state_ref[key]
            
            # Copy/merge errors
            if "errors" in _state_ref:
                current_errors = state.get("errors", {})
                new_errors = _state_ref["errors"]
                result["errors"] = {**current_errors, **new_errors}
            
            # Copy execution log
            if "execution_log" in _state_ref:
                current_log = state.get("execution_log", [])
                new_log = _state_ref["execution_log"]
                result["execution_log"] = current_log + new_log
        
        logger.info("Intelligent Agent completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in intelligent agent node: {e}")
        return {
            "final_response": f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again.",
            "conversation_complete": True,
            "current_state": "RESPONDING",
            "errors": {**state.get("errors", {}), "agent": f"Processing failed: {str(e)}"}
        }


def intelligent_agent_routing(state: AgentState) -> str:
    """
    Routing function for the Intelligent Agent node.
    
    Since this is a single-node architecture, it always routes to END.
    
    Args:
        state: Current agent state
        
    Returns:
        Always "END"
    """
    return "END"