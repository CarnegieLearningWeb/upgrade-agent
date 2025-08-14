# Streamlined UpGradeAgent Architecture

## Overview

This document defines a **streamlined but complete architecture** for UpGradeAgent that handles all core requirements without over-engineering. The architecture addresses the key challenges identified in the original router-based approach while maintaining simplicity and reliability.

## Why This Architecture

### Problems with Original Router-Based Approach
1. **Premature commitment**: Router makes decisions without full context
2. **Poor ambiguity handling**: Can't handle queries like "What's the status?"
3. **No multi-step support**: Each interaction treated independently
4. **Safety concerns**: No confirmation before potentially destructive actions
5. **Limited conversation memory**: Can't build on previous exchanges

### Our Solution: Context-Aware Conversation Flow
Instead of simple routing, we use an **intelligent conversation analyzer** that:
- Analyzes queries with full conversational and system context
- Handles ambiguous queries by asking for clarification
- Progressively gathers missing information through natural conversation
- **Orchestrates multi-step operations by making tool execution decisions recursively**
- Always confirms before executing actions
- Maintains conversation memory and context

## Essential Nodes and Their Necessity

After careful review, here are the **5 essential nodes** that provide complete functionality without redundancy:

### 1. **Conversation Analyzer** (The Brain & Orchestrator)
**Why Necessary**: Core intelligence that replaces unreliable router approach. Analyzes user input with full context and makes intelligent decisions about what to do next.

**What it handles**:
- Greetings: "Hi, how are you?" → Direct friendly response
- General questions: "What is A/B testing?" → Direct explanation  
- UpGrade queries: "What's the status?" → Asks for clarification
- Action requests: "Create experiment" → Determines what info is needed
- **Multi-step orchestration**: "Test condition balance" → Plans sequence of API calls
- **Recursive decision making**: After each tool execution, decides if more steps are needed

**Why not multiple nodes**: One intelligent analyzer is better than multiple simple routers because it has full context and can make nuanced decisions about complex workflows.

### 2. **Information Gatherer** 
**Why Necessary**: Many UpGrade operations require multiple parameters. Handles progressive collection naturally.

**What it handles**:
- Missing required info: "Create experiment" → Asks for name, context, etc.
- Contextual prompts: Shows available contexts, experiments, etc.
- User-friendly collection: Accepts various input formats
- Cancellation: Allows users to abort mid-process

**Why essential**: Without this, the app would either fail on incomplete requests or make dangerous assumptions.

### 3. **Confirmation Handler**
**Why Necessary**: UpGrade operations can have significant impact. User confirmation is a safety requirement.

**What it handles**:
- Action confirmation: Shows what will be done before doing it
- Risk awareness: Warns about irreversible actions  
- User control: Allows modification or cancellation
- **Multi-step confirmation**: For complex workflows, confirms the overall plan

**Why essential**: Safety and user trust. Never execute potentially impactful actions without explicit confirmation.

### 4. **Tool Executor**
**Why Necessary**: Executes actual UpGrade API calls with proper error handling.

**What it handles**:
- API tool execution: Calls individual API functions (get_experiments, create_experiment, etc.)
- Error handling: Graceful failure with helpful messages
- Result collection: Gathers tool outputs for analyzer to process
- **Single tool focus**: Executes one tool at a time, returns control to analyzer

**Why essential**: This is where the actual work gets done. Keeps tool execution simple and focused.

### 5. **Response Generator**
**Why Necessary**: Converts tool results and system state into natural, helpful responses.

**What it handles**:
- Tool result synthesis: Converts API responses to user-friendly messages
- Error communication: Explains what went wrong and how to fix it
- Conversation flow: Provides next steps and suggestions
- **Progress updates**: For multi-step operations, can provide status updates

**Why essential**: Raw tool outputs aren't user-friendly. This makes the interaction natural and helpful.

## Multi-Step Operation Flow

### How Complex Operations Work

Instead of pre-built workflow tools, the agent orchestrates multiple simple tools:

```
User: "Test condition balance for experiment ABC"

1. Analyzer → "Need experiment details first" 
   → Executor (get_experiment_details) 
   → Back to Analyzer

2. Analyzer → "Experiment is inactive, need to start it"
   → Executor (update_experiment_status: enrolling)
   → Back to Analyzer

3. Analyzer → "Now simulate 100 users"
   → Executor (init_user + assign_condition loop)
   → Back to Analyzer

4. Analyzer → "Analyze results and stop experiment"
   → Executor (update_experiment_status: inactive)
   → Response Generator

5. Response Generator → Natural summary of balance results
```

### Key Benefits of This Approach

✅ **Flexible orchestration** - Agent adapts to different scenarios  
✅ **Self-correcting** - Can handle unexpected API responses  
✅ **Natural conversation** - Can explain what it's doing step-by-step  
✅ **Simpler tools** - No complex workflow tools to maintain  
✅ **Intelligent adaptation** - Learns from each API response  

## What We Removed (Avoiding Over-Engineering)

1. **Separate routing nodes**: Replaced with one intelligent analyzer
2. **Complex workflow tools**: Agent orchestrates simple tools instead
3. **Pre-planned multi-step tools**: Dynamic orchestration based on results
4. **Complex state enums**: Simplified to just 5 clear states
5. **Risk assessment node**: Integrated into confirmation handler  
6. **Separate clarification node**: Handled by the analyzer
7. **Multiple response types**: Simplified to essential types

## Architecture Benefits

1. **Handles ambiguity**: "What's the status?" gets proper clarification
2. **Supports multi-step operations**: Dynamically orchestrates tool sequences
3. **Adapts to results**: Can change plans based on API responses
4. **Maintains safety**: Always confirms before actions
5. **Stays conversational**: Handles greetings and general questions
6. **Remains simple**: 5 nodes with clear responsibilities
7. **Enables testing**: Each node and tool can be tested independently

## Implementation

Minimal but complete architecture for reliable conversation handling

```python
from typing import TypedDict, Optional, List, Dict, Any, Literal
from enum import Enum

class ConversationState(Enum):
    ANALYZING = "analyzing"           # Understanding user input
    GATHERING_INFO = "gathering_info" # Collecting missing parameters
    CONFIRMING = "confirming"         # Getting user approval
    EXECUTING = "executing"           # Running tools
    RESPONDING = "responding"         # Generating final response

class AgentState(TypedDict):
    # === Core Conversation ===
    user_input: str
    conversation_history: List[Dict[str, str]]  # Recent context
    current_state: ConversationState
    
    # === Operation Context ===
    intended_action: Optional[str]        # What user wants to do
    action_confidence: float              # How sure we are (0.0-1.0)
    required_params: Dict[str, Any]       # What we need for this action
    gathered_params: Dict[str, Any]       # What we've collected
    missing_params: List[str]             # What's still needed
    
    # === Multi-Step Task Tracking ===
    task_in_progress: bool                # Is a multi-step task running?
    task_type: Optional[str]              # Type of task (e.g., "test_balance")
    steps_completed: List[str]            # What steps have been done
    next_planned_steps: List[str]         # What steps are planned next
    step_results: List[Dict[str, Any]]    # Results from each step
    
    # === Tool Execution ===
    planned_tools: List[Dict[str, Any]]   # Tools to execute (usually one at a time)
    tool_results: List[Dict[str, Any]]    # Execution results
    
    # === Response ===
    bot_response: str
    response_type: Literal["answer", "question", "confirmation", "clarification"]
    suggested_actions: List[str]          # Quick action buttons
    
    # === System Context (cached) ===
    available_experiments: Optional[List[Dict]]
    context_metadata: Optional[Dict]
    
    # === Error Handling ===
    errors: List[str]

# =============================================================================
# NODE 1: CONVERSATION ANALYZER (The Brain & Orchestrator)
# =============================================================================

class ConversationAnalyzer:
    """
    Single intelligent node that analyzes user input with full context
    and determines what to do next, including orchestrating multi-step operations
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.1)
        self.action_templates = self._load_action_templates()
    
    def _load_action_templates(self) -> Dict:
        """Define what parameters each action needs and what tools they use"""
        return {
            "create_experiment": {
                "required": ["name", "context"],
                "optional": ["conditions", "decision_points", "assignment_unit"],
                "tools": ["create_experiment"],
                "defaults": {
                    "assignment_unit": "individual",
                    "conditions": [{"code": "control", "weight": 50}, {"code": "variant", "weight": 50}]
                }
            },
            "test_condition_balance": {
                "required": ["experiment_id"],
                "optional": ["num_users"],
                "tools": ["get_experiment_details", "update_experiment_status", "init_user", "assign_condition"],
                "defaults": {"num_users": 100}
            },
            "update_experiment_status": {
                "required": ["experiment_id", "new_status"],
                "tools": ["update_experiment_status"]
            },
            "list_experiments": {
                "optional": ["context_filter", "status_filter"],
                "tools": ["get_all_experiments"]
            }
        }
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Analyze input and determine next action"""
        
        # Check if we're in the middle of a multi-step task
        if state.get("task_in_progress"):
            return self._handle_ongoing_task(state)
        
        # Build analysis context for new request
        analysis_prompt = f"""
        You are UpGradeAgent, an expert assistant for A/B testing with UpGrade.
        
        CONVERSATION CONTEXT:
        {self._format_conversation_history(state)}
        
        SYSTEM STATE:
        - Available experiments: {len(state.get('available_experiments', []))}
        - Available contexts: {list(state.get('context_metadata', {}).keys())}
        
        CURRENT USER INPUT: "{state['user_input']}"
        
        AVAILABLE TOOLS (simple 1:1 API mappings):
        - check_upgrade_health: Check service status
        - get_context_metadata: Get available contexts  
        - get_all_experiments: List experiments
        - get_experiment_details: Get experiment configuration
        - create_experiment: Create new experiment
        - update_experiment_status: Change experiment status
        - delete_experiment: Delete experiment
        - init_user: Initialize user for testing
        - assign_condition: Get condition assignment
        - mark_decision_point: Record decision point visit
        
        CAPABILITIES:
        - Answer questions about A/B testing and UpGrade concepts (no tools needed)
        - Health checks and system status (single tool)
        - List, create, update, delete experiments (single or few tools)
        - Complex operations like testing balance (orchestrate multiple tools)
        - Handle greetings and general conversation (no tools)
        
        For complex operations, you'll orchestrate multiple simple tools step by step.
        
        Analyze this input and respond with JSON:
        {{
            "intent_type": "direct_answer|needs_tools|needs_info|unclear|greeting",
            "confidence": 0.85,
            "intended_action": "create_experiment|test_condition_balance|list_experiments|greeting|etc",
            "is_multi_step": false,
            "extracted_params": {{"param": "value"}},
            "missing_params": ["param1", "param2"],
            "response_strategy": "answer_directly|gather_info|ask_clarification|execute_tools",
            "direct_answer": "answer if can respond directly",
            "clarification_needed": "what to ask if unclear"
        }}
        """
        
        response = self.llm.invoke(analysis_prompt)
        analysis = json.loads(response.content)
        
        return self._process_analysis(state, analysis)
    
    def _handle_ongoing_task(self, state: AgentState) -> Dict[str, Any]:
        """Handle ongoing multi-step task by analyzing last results and deciding next step"""
        
        last_results = state.get("tool_results", [])
        task_type = state.get("task_type")
        steps_completed = state.get("steps_completed", [])
        
        planning_prompt = f"""
        You are orchestrating a multi-step task: {task_type}
        
        TASK CONTEXT:
        - Steps completed: {steps_completed}
        - Last tool results: {json.dumps(last_results[-1] if last_results else {}, indent=2)}
        - Original parameters: {state.get("gathered_params", {})}
        
        Based on the results, determine the next step. Respond with JSON:
        {{
            "continue_task": true,
            "next_tool": "tool_name",
            "next_params": {{"param": "value"}},
            "step_description": "what this step accomplishes",
            "task_complete": false
        }}
        
        OR if task is complete:
        {{
            "continue_task": false,
            "task_complete": true,
            "completion_summary": "what was accomplished"
        }}
        """
        
        response = self.llm.invoke(planning_prompt)
        plan = json.loads(response.content)
        
        if plan.get("task_complete"):
            return {
                "current_state": ConversationState.RESPONDING,
                "task_in_progress": False,
                "bot_response": plan.get("completion_summary", "Task completed successfully.")
            }
        else:
            return {
                "current_state": ConversationState.EXECUTING,
                "planned_tools": [{
                    "tool": plan.get("next_tool"),
                    "params": plan.get("next_params", {})
                }],
                "next_planned_steps": [plan.get("step_description")]
            }
    
    def _process_analysis(self, state: AgentState, analysis: Dict) -> Dict[str, Any]:
        """Process analysis results and set next state"""
        
        confidence = analysis.get("confidence", 0.0)
        intent_type = analysis.get("intent_type")
        strategy = analysis.get("response_strategy")
        is_multi_step = analysis.get("is_multi_step", False)
        
        # Handle different scenarios
        if intent_type == "greeting" or strategy == "answer_directly":
            # Can respond directly
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": analysis.get("direct_answer", ""),
                "response_type": "answer"
            }
        
        elif confidence < 0.7 or strategy == "ask_clarification":
            # Need clarification
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": analysis.get("clarification_needed", "I'm not sure what you mean. Could you clarify?"),
                "response_type": "clarification"
            }
        
        elif strategy == "gather_info":
            # Need to collect information
            return {
                "current_state": ConversationState.GATHERING_INFO,
                "intended_action": analysis.get("intended_action"),
                "action_confidence": confidence,
                "gathered_params": analysis.get("extracted_params", {}),
                "missing_params": analysis.get("missing_params", [])
            }
        
        elif strategy == "execute_tools":
            # Ready to execute - set up for potential multi-step
            action = analysis.get("intended_action")
            gathered_params = analysis.get("extracted_params", {})
            
            if is_multi_step:
                # Start multi-step task
                first_tool = self._plan_first_tool(action, gathered_params)
                return {
                    "current_state": ConversationState.CONFIRMING,
                    "intended_action": action,
                    "gathered_params": gathered_params,
                    "task_in_progress": True,
                    "task_type": action,
                    "steps_completed": [],
                    "planned_tools": [first_tool]
                }
            else:
                # Single tool execution
                return {
                    "current_state": ConversationState.CONFIRMING,
                    "intended_action": action,
                    "gathered_params": gathered_params,
                    "planned_tools": self._plan_tool_execution(action, gathered_params)
                }
        
        else:
            # Default fallback
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": "I'm not sure how to help with that. Could you try rephrasing?",
                "response_type": "clarification"
            }

# =============================================================================
# NODE 2: INFORMATION GATHERER
# =============================================================================

class InformationGatherer:
    """
    Handles collecting missing information through natural conversation
    """
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Gather next piece of missing information"""
        
        missing_params = state.get("missing_params", [])
        intended_action = state.get("intended_action")
        
        if not missing_params:
            # All info collected, move to confirmation
            return {
                "current_state": ConversationState.CONFIRMING,
                "missing_params": []
            }
        
        # Get next parameter to collect
        next_param = missing_params[0]
        prompt = self._generate_parameter_prompt(next_param, intended_action, state)
        
        return {
            "current_state": ConversationState.GATHERING_INFO,
            "bot_response": prompt,
            "response_type": "question",
            "suggested_actions": self._get_quick_options(next_param, state)
        }
    
    def _generate_parameter_prompt(self, param: str, action: str, state: AgentState) -> str:
        """Generate contextual prompt for specific parameter"""
        
        prompts = {
            "name": "What would you like to name this experiment?",
            "context": f"Which app context? Available: {', '.join(state.get('context_metadata', {}).keys())}",
            "experiment_id": "Which experiment? " + self._format_experiment_options(state),
            "num_users": "How many users should I simulate? (default: 100)",
            "concept": "What concept would you like me to explain?"
        }
        
        return prompts.get(param, f"Please provide {param}:")
    
    def _get_quick_options(self, param: str, state: AgentState) -> List[str]:
        """Generate quick action options for the parameter"""
        if param == "context" and state.get("context_metadata"):
            return list(state["context_metadata"].keys())
        elif param == "num_users":
            return ["100", "500", "1000"]
        return []
    
    def _format_experiment_options(self, state: AgentState) -> str:
        """Format available experiments for display"""
        experiments = state.get("available_experiments", [])
        if experiments:
            options = [f"{exp['name']} ({exp['id'][:8]}...)" for exp in experiments[:5]]
            return f"Options: {', '.join(options)}"
        return "Loading experiments..."
    
    def process_user_response(self, state: AgentState) -> Dict[str, Any]:
        """Process user's response to information request"""
        
        user_input = state["user_input"]
        missing_params = state.get("missing_params", [])
        
        if not missing_params:
            return {"current_state": ConversationState.CONFIRMING}
        
        current_param = missing_params[0]
        
        # Handle cancellation
        if user_input.lower() in ["cancel", "stop", "nevermind"]:
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": "No problem! What else can I help you with?",
                "response_type": "answer"
            }
        
        # Extract value (simplified - in real implementation, use LLM)
        extracted_value = self._extract_parameter_value(current_param, user_input, state)
        
        if extracted_value:
            # Add to gathered params
            gathered = state.get("gathered_params", {})
            gathered[current_param] = extracted_value
            remaining_missing = missing_params[1:]
            
            return {
                "gathered_params": gathered,
                "missing_params": remaining_missing,
                "current_state": ConversationState.GATHERING_INFO if remaining_missing else ConversationState.CONFIRMING
            }
        
        else:
            # Couldn't understand, ask again
            return {
                "bot_response": f"I didn't understand that. {self._generate_parameter_prompt(current_param, state.get('intended_action'), state)}",
                "response_type": "question"
            }
    
    def _extract_parameter_value(self, param: str, user_input: str, state: AgentState) -> Any:
        """Extract parameter value from user input (simplified implementation)"""
        user_input = user_input.strip()
        
        if param == "num_users":
            # Try to extract number
            import re
            numbers = re.findall(r'\d+', user_input)
            return int(numbers[0]) if numbers else None
        elif param == "context":
            # Check if input matches available contexts
            available_contexts = state.get("context_metadata", {}).keys()
            for context in available_contexts:
                if context.lower() in user_input.lower():
                    return context
            return None
        else:
            # For simple params, return the input
            return user_input if len(user_input) > 0 else None

# =============================================================================
# NODE 3: CONFIRMATION HANDLER
# =============================================================================

class ConfirmationHandler:
    """
    Handles user confirmation before executing actions
    """
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Generate confirmation message or process confirmation response"""
        
        if state.get("current_state") == ConversationState.CONFIRMING:
            # Generate confirmation
            return self._generate_confirmation(state)
        else:
            # Process user's confirmation response
            return self._process_confirmation_response(state)
    
    def _generate_confirmation(self, state: AgentState) -> Dict[str, Any]:
        """Generate confirmation message"""
        
        action = state.get("intended_action")
        params = state.get("gathered_params", {})
        is_multi_step = state.get("task_in_progress", False)
        
        if action == "create_experiment":
            confirmation = f"""
Ready to create experiment:

**Name**: {params.get('name')}
**Context**: {params.get('context')}
**Conditions**: {params.get('conditions', 'control 50%, variant 50%')}

Proceed?
"""
        elif action == "test_condition_balance":
            confirmation = f"""
Ready to test condition balance:

**Experiment**: {params.get('experiment_id')}
**Users to simulate**: {params.get('num_users', 100)}

This will involve multiple steps:
1. Get experiment details
2. Start experiment if needed
3. Simulate users
4. Analyze results
5. Stop experiment

Proceed?
"""
        elif action == "delete_experiment":
            confirmation = f"""
⚠️ **Confirm Experiment Deletion**

**Experiment**: {params.get('experiment_id')}

🚨 **Warning**: This action cannot be undone
- Experiment configuration will be permanently deleted
- All associated data will be lost

Type "DELETE" to confirm, or "cancel" to abort.
"""
        else:
            confirmation = f"Ready to execute {action} with parameters: {params}. Proceed?"
        
        return {
            "current_state": ConversationState.CONFIRMING,
            "bot_response": confirmation,
            "response_type": "confirmation",
            "suggested_actions": ["Yes", "No", "Modify"]
        }
    
    def _process_confirmation_response(self, state: AgentState) -> Dict[str, Any]:
        """Process user's confirmation response"""
        
        user_input = state["user_input"].lower()
        action = state.get("intended_action")
        
        # Special handling for dangerous operations
        if action == "delete_experiment" and "delete" not in user_input:
            return {
                "bot_response": 'Please type "DELETE" to confirm deletion, or "cancel" to abort.',
                "response_type": "confirmation"
            }
        
        if any(word in user_input for word in ["yes", "confirm", "proceed", "go ahead", "delete"]):
            # User confirmed - execute
            return {
                "current_state": ConversationState.EXECUTING
            }
        
        elif any(word in user_input for word in ["no", "cancel", "abort"]):
            # User cancelled
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": "Cancelled. What else can I help you with?",
                "response_type": "answer",
                "task_in_progress": False  # Reset any ongoing task
            }
        
        else:
            # Unclear response
            return {
                "bot_response": "Please confirm with 'yes' to proceed or 'no' to cancel.",
                "response_type": "confirmation"
            }

# =============================================================================
# NODE 4: TOOL EXECUTOR (Updated for Single Tool Focus)
# =============================================================================

class ToolExecutor:
    """
    Executes one tool at a time and returns control to analyzer for orchestration
    """
    
    def __init__(self, tools: List):
        self.tools = {tool.name: tool for tool in tools}
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Execute planned tools (typically one at a time)"""
        
        planned_tools = state.get("planned_tools", [])
        
        if not planned_tools:
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": "No tools to execute.",
                "response_type": "answer"
            }
        
        # Execute tools (usually just one)
        results = []
        for tool_plan in planned_tools:
            try:
                tool_name = tool_plan["tool"]
                tool_params = tool_plan["params"]
                
                if tool_name in self.tools:
                    result = self.tools[tool_name].invoke(tool_params)
                    results.append({"tool": tool_name, "success": True, "result": result})
                else:
                    results.append({"tool": tool_name, "success": False, "error": f"Tool {tool_name} not found"})
            
            except Exception as e:
                results.append({"tool": tool_name, "success": False, "error": str(e)})
        
        # Check if this is part of a multi-step task
        if state.get("task_in_progress"):
            # Update task progress
            steps_completed = state.get("steps_completed", [])
            if planned_tools:
                steps_completed.append(planned_tools[0]["tool"])
            
            return {
                "current_state": ConversationState.ANALYZING,  # Return to analyzer for next step
                "tool_results": results,
                "steps_completed": steps_completed,
                "step_results": state.get("step_results", []) + results
            }
        else:
            # Single operation complete
            return {
                "current_state": ConversationState.RESPONDING,
                "tool_results": results
            }

# =============================================================================
# NODE 5: RESPONSE GENERATOR
# =============================================================================

class ResponseGenerator:
    """
    Generates final responses based on conversation state and tool results
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Generate final response"""
        
        # If response already set, return as-is
        if state.get("bot_response"):
            return {"bot_response": state["bot_response"]}
        
        # Check if this was a multi-step task completion
        if state.get("task_in_progress") == False and state.get("step_results"):
            return self._synthesize_multi_step_response(state)
        
        # Generate response based on tool results
        tool_results = state.get("tool_results", [])
        
        if tool_results:
            return self._synthesize_tool_response(state, tool_results)
        
        # Fallback response
        return {
            "bot_response": "I'm not sure how to help with that. Could you please rephrase your question?",
            "response_type": "answer"
        }
    
    def _synthesize_multi_step_response(self, state: AgentState) -> Dict[str, Any]:
        """Synthesize response for completed multi-step task"""
        
        task_type = state.get("task_type")
        step_results = state.get("step_results", [])
        steps_completed = state.get("steps_completed", [])
        
        synthesis_prompt = f"""
        The user requested: "{state['user_input']}"
        
        I completed a multi-step task: {task_type}
        
        Steps completed: {steps_completed}
        All step results: {json.dumps(step_results, indent=2)}
        
        Create a comprehensive, natural response that:
        1. Summarizes what was accomplished
        2. Highlights key findings or results
        3. Provides actionable insights
        4. Suggests next steps if appropriate
        
        Be friendly, helpful, and thorough.
        """
        
        response = self.llm.invoke(synthesis_prompt)
        
        return {
            "bot_response": response.content,
            "response_type": "answer",
            "task_in_progress": False,  # Ensure task is marked complete
            "step_results": [],  # Clear step results
            "steps_completed": []  # Clear completed steps
        }
    
    def _synthesize_tool_response(self, state: AgentState, tool_results: List) -> Dict[str, Any]:
        """Synthesize natural response from tool results"""
        
        successful_results = [r for r in tool_results if r.get("success")]
        failed_results = [r for r in tool_results if not r.get("success")]
        
        if not successful_results and failed_results:
            # All tools failed
            error_details = [r.get("error", "Unknown error") for r in failed_results]
            return {
                "bot_response": f"I encountered errors while processing your request: {'; '.join(error_details)}. Please try again.",
                "response_type": "answer"
            }
        
        # Use LLM to create natural response
        context = {
            "user_request": state['user_input'],
            "successful_results": successful_results,
            "failed_results": failed_results if failed_results else None,
            "intended_action": state.get("intended_action"),
            "conversation_context": state.get("conversation_history", [])[-3:]  # Last 3 exchanges
        }
        
        synthesis_prompt = f"""
        The user asked: "{state['user_input']}"
        
        Tool execution results: {json.dumps(successful_results, indent=2)}
        
        {f"Some tools failed: {json.dumps(failed_results, indent=2)}" if failed_results else ""}
        
        Create a helpful, natural response that addresses the user's request using these results.
        Be concise but informative. If there were any failures, acknowledge them briefly but focus on what was successful.
        
        Include relevant data and suggest logical next steps if appropriate.
        """
        
        response = self.llm.invoke(synthesis_prompt)
        
        return {
            "bot_response": response.content,
            "response_type": "answer"
        }

# =============================================================================
# HELPER FUNCTIONS FOR CONVERSATION ANALYZER
# =============================================================================

# These helper functions should be added to the ConversationAnalyzer class above:

    def _format_conversation_history(self, state: AgentState) -> str:
        """Format conversation history for context"""
        history = state.get("conversation_history", [])
        if not history:
            return "No previous conversation"
        
        formatted = []
        for exchange in history[-3:]:  # Last 3 exchanges
            formatted.append(f"User: {exchange.get('user', '')}")
            formatted.append(f"Bot: {exchange.get('bot', '')}")
        
        return "\n".join(formatted)
    
    def _plan_tool_execution(self, action: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan tool execution for single-step actions"""
        action_mapping = {
            "create_experiment": [{
                "tool": "create_experiment",
                "params": params
            }],
            "list_experiments": [{
                "tool": "get_all_experiments", 
                "params": {
                    "context_filter": params.get("context_filter"),
                    "status_filter": params.get("status_filter")
                }
            }],
            "update_experiment_status": [{
                "tool": "update_experiment_status",
                "params": params
            }],
            "delete_experiment": [{
                "tool": "delete_experiment",
                "params": {"experiment_id": params.get("experiment_id")}
            }],
            "check_health": [{
                "tool": "check_upgrade_health",
                "params": {}
            }]
        }
        
        return action_mapping.get(action, [])
    
    def _plan_first_tool(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Plan the first tool for multi-step actions"""
        if action == "test_condition_balance":
            # Always start by getting experiment details
            return {
                "tool": "get_experiment_details",
                "params": {"experiment_id": params.get("experiment_id")}
            }
        elif action == "simulate_user_journey":
            # Start with user initialization
            return {
                "tool": "init_user", 
                "params": {
                    "user_id": params.get("user_id"),
                    "context": params.get("context")
                }
            }
        else:
            # Default to single tool execution
            return self._plan_tool_execution(action, params)[0] if self._plan_tool_execution(action, params) else {}

# =============================================================================
# GRAPH CONSTRUCTION (Updated Edges)
# =============================================================================

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

def build_streamlined_upgrade_agent(tools: List):
    """Build the streamlined UpGradeAgent graph with recursive orchestration"""
    
    # Initialize components
    analyzer = ConversationAnalyzer()
    gatherer = InformationGatherer()
    confirmer = ConfirmationHandler()
    executor = ToolExecutor(tools)
    responder = ResponseGenerator()
    
    # Create graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("analyzer", analyzer)
    graph.add_node("gatherer", gatherer)
    graph.add_node("confirmer", confirmer)
    graph.add_node("executor", executor)
    graph.add_node("responder", responder)
    
    # Define routing
    def route_from_analyzer(state: AgentState) -> str:
        current_state = state.get("current_state")
        
        if current_state == ConversationState.GATHERING_INFO:
            return "gatherer"
        elif current_state == ConversationState.CONFIRMING:
            return "confirmer"
        elif current_state == ConversationState.EXECUTING:
            return "executor"
        else:  # RESPONDING
            return "responder"
    
    def route_from_gatherer(state: AgentState) -> str:
        current_state = state.get("current_state")
        
        if current_state == ConversationState.CONFIRMING:
            return "confirmer"
        else:
            return END  # Wait for user input
    
    def route_from_confirmer(state: AgentState) -> str:
        current_state = state.get("current_state")
        
        if current_state == ConversationState.EXECUTING:
            return "executor"
        else:
            return END  # Wait for user confirmation or return response
    
    def route_from_executor(state: AgentState) -> str:
        """Route from executor - may return to analyzer for multi-step tasks"""
        current_state = state.get("current_state")
        
        if current_state == ConversationState.ANALYZING:
            return "analyzer"  # Multi-step task continues
        else:  # RESPONDING
            return "responder"  # Task complete
    
    # Set up edges
    graph.set_entry_point("analyzer")
    
    graph.add_conditional_edges("analyzer", route_from_analyzer)
    graph.add_conditional_edges("gatherer", route_from_gatherer)
    graph.add_conditional_edges("confirmer", route_from_confirmer)
    graph.add_conditional_edges("executor", route_from_executor)  # Key change: conditional routing
    graph.add_edge("responder", END)
    
    # Add memory
    memory = InMemorySaver()
    
    return graph.compile(checkpointer=memory)
```

## Example Multi-Step Flow

```python
def complex_operation_example():
    """Example of multi-step operation"""
    config = {"configurable": {"thread_id": "user-1"}}
    
    # User request
    result = app.invoke({
        "user_input": "Test condition balance for my homepage experiment with 200 users",
        "conversation_history": [],
        "current_state": ConversationState.ANALYZING
    }, config=config)
    
    # The agent will:
    # 1. Analyze → Confirm → Execute get_experiment_details 
    # 2. → Back to Analyze → Execute update_experiment_status (start)
    # 3. → Back to Analyze → Execute user simulations
    # 4. → Back to Analyze → Execute update_experiment_status (stop)
    # 5. → Response with balance analysis
```

This architecture provides the flexibility of agent orchestration while maintaining the simplicity of single-purpose tools and clear node responsibilities.