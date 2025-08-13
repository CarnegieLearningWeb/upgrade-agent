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
- Always confirms before executing actions
- Maintains conversation memory and context

## Essential Nodes and Their Necessity

After careful review, here are the **5 essential nodes** that provide complete functionality without redundancy:

### 1. **Conversation Analyzer** (The Brain)
**Why Necessary**: Core intelligence that replaces unreliable router approach. Analyzes user input with full context and makes intelligent decisions.

**What it handles**:
- Greetings: "Hi, how are you?" → Direct friendly response
- General questions: "What is A/B testing?" → Direct explanation  
- UpGrade queries: "What's the status?" → Asks for clarification
- Action requests: "Create experiment" → Determines what info is needed

**Why not multiple nodes**: One intelligent analyzer is better than multiple simple routers because it has full context and can make nuanced decisions.

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

**Why essential**: Safety and user trust. Never execute potentially impactful actions without explicit confirmation.

### 4. **Tool Executor**
**Why Necessary**: Executes actual UpGrade API calls with proper error handling.

**What it handles**:
- API tool execution: Calls create_experiment, test_balance, etc.
- Error handling: Graceful failure with helpful messages
- Result collection: Gathers tool outputs for response generation

**Why essential**: This is where the actual work gets done. Without it, the app is just a chatbot with no functionality.

### 5. **Response Generator**
**Why Necessary**: Converts tool results and system state into natural, helpful responses.

**What it handles**:
- Tool result synthesis: Converts API responses to user-friendly messages
- Error communication: Explains what went wrong and how to fix it
- Conversation flow: Provides next steps and suggestions

**Why essential**: Raw tool outputs aren't user-friendly. This makes the interaction natural and helpful.

## What We Removed (Avoiding Over-Engineering)

1. **Separate routing nodes**: Replaced with one intelligent analyzer
2. **Complex state enums**: Simplified to just 5 clear states
3. **Risk assessment node**: Integrated into confirmation handler  
4. **Separate clarification node**: Handled by the analyzer
5. **Multiple response types**: Simplified to essential types
6. **Over-engineered error handling**: Basic but sufficient error handling

## Architecture Benefits

1. **Handles ambiguity**: "What's the status?" gets proper clarification
2. **Supports multi-step operations**: Naturally collects missing information
3. **Maintains safety**: Always confirms before actions
4. **Stays conversational**: Handles greetings and general questions
5. **Remains simple**: 5 nodes with clear responsibilities
6. **Enables testing**: Each node can be tested independently

## Implementation

Minimal but complete architecture for reliable conversation handling

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
    
    # === Tool Execution ===
    planned_tools: List[Dict[str, Any]]   # Tools to execute
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
# NODE 1: CONVERSATION ANALYZER (The Brain)
# =============================================================================

class ConversationAnalyzer:
    """
    Single intelligent node that analyzes user input with full context
    and determines what to do next
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.1)
        self.action_templates = self._load_action_templates()
    
    def _load_action_templates(self) -> Dict:
        """Define what parameters each action needs"""
        return {
            "create_experiment": {
                "required": ["name", "context"],
                "optional": ["conditions", "decision_points", "assignment_unit"],
                "defaults": {
                    "assignment_unit": "individual",
                    "conditions": [{"code": "control", "weight": 50}, {"code": "variant", "weight": 50}]
                }
            },
            "test_condition_balance": {
                "required": ["experiment_id"],
                "optional": ["num_users"],
                "defaults": {"num_users": 100}
            },
            "update_experiment_status": {
                "required": ["experiment_id", "new_status"]
            },
            "explain_concept": {
                "required": ["concept"]
            },
            "list_experiments": {
                "optional": ["context_filter", "status_filter"]
            }
        }
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Analyze input and determine next action"""
        
        # Build analysis context
        analysis_prompt = f"""
        You are UpGradeAgent, an expert assistant for A/B testing with UpGrade.
        
        CONVERSATION CONTEXT:
        {self._format_conversation_history(state)}
        
        SYSTEM STATE:
        - Available experiments: {len(state.get('available_experiments', []))}
        - Available contexts: {list(state.get('context_metadata', {}).keys())}
        
        CURRENT USER INPUT: "{state['user_input']}"
        
        CAPABILITIES:
        - Answer questions about A/B testing and UpGrade concepts
        - Health checks and system status  
        - List, create, update, delete experiments
        - Simulate users and test experiment balance
        - Handle greetings and general conversation
        
        Analyze this input and respond with JSON:
        {{
            "intent_type": "direct_answer|needs_tools|needs_info|unclear|greeting",
            "confidence": 0.85,
            "intended_action": "create_experiment|list_experiments|explain_concept|greeting|etc",
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
    
    def _process_analysis(self, state: AgentState, analysis: Dict) -> Dict[str, Any]:
        """Process analysis results and set next state"""
        
        confidence = analysis.get("confidence", 0.0)
        intent_type = analysis.get("intent_type")
        strategy = analysis.get("response_strategy")
        
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
            # Ready to execute
            return {
                "current_state": ConversationState.CONFIRMING,
                "intended_action": analysis.get("intended_action"),
                "gathered_params": analysis.get("extracted_params", {}),
                "planned_tools": self._plan_tool_execution(analysis.get("intended_action"), analysis.get("extracted_params", {}))
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

This will temporarily set the experiment to 'enrolling' status. Proceed?
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
        
        if any(word in user_input for word in ["yes", "confirm", "proceed", "go ahead"]):
            # User confirmed - execute
            return {
                "current_state": ConversationState.EXECUTING
            }
        
        elif any(word in user_input for word in ["no", "cancel", "abort"]):
            # User cancelled
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": "Cancelled. What else can I help you with?",
                "response_type": "answer"
            }
        
        else:
            # Unclear response
            return {
                "bot_response": "Please confirm with 'yes' to proceed or 'no' to cancel.",
                "response_type": "confirmation"
            }

# =============================================================================
# NODE 4: TOOL EXECUTOR
# =============================================================================

class ToolExecutor:
    """
    Executes the planned tools and handles results
    """
    
    def __init__(self, tools: List):
        self.tools = {tool.name: tool for tool in tools}
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Execute planned tools"""
        
        planned_tools = state.get("planned_tools", [])
        
        if not planned_tools:
            return {
                "current_state": ConversationState.RESPONDING,
                "bot_response": "No tools to execute.",
                "response_type": "answer"
            }
        
        # Execute tools
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
        
        # Generate response based on tool results
        tool_results = state.get("tool_results", [])
        
        if tool_results:
            return self._synthesize_tool_response(state, tool_results)
        
        # Fallback response
        return {
            "bot_response": "I'm not sure how to help with that. Could you please rephrase your question?",
            "response_type": "answer"
        }
    
    def _synthesize_tool_response(self, state: AgentState, tool_results: List) -> Dict[str, Any]:
        """Synthesize natural response from tool results"""
        
        successful_results = [r for r in tool_results if r.get("success")]
        
        if not successful_results:
            return {
                "bot_response": "I encountered an error while processing your request. Please try again.",
                "response_type": "answer"
            }
        
        # Use LLM to create natural response
        synthesis_prompt = f"""
        The user asked: "{state['user_input']}"
        
        Tool execution results: {json.dumps(successful_results, indent=2)}
        
        Create a helpful, natural response that addresses the user's request using these results.
        Be concise but informative.
        """
        
        response = self.llm.invoke(synthesis_prompt)
        
        return {
            "bot_response": response.content,
            "response_type": "answer"
        }

# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

def build_streamlined_upgrade_agent(tools: List):
    """Build the streamlined UpGradeAgent graph"""
    
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
    
    # Set up edges
    graph.set_entry_point("analyzer")
    
    graph.add_conditional_edges("analyzer", route_from_analyzer)
    graph.add_conditional_edges("gatherer", route_from_gatherer)
    graph.add_conditional_edges("confirmer", route_from_confirmer)
    graph.add_edge("executor", "responder")
    graph.add_edge("responder", END)
    
    # Add memory
    memory = InMemorySaver()
    
    return graph.compile(checkpointer=memory)

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

# Initialize with UpGrade tools
app = build_streamlined_upgrade_agent([
    check_upgrade_health,
    get_all_experiments,
    create_experiment,
    test_condition_balance,
    # ... other tools
])

def chat_example():
    """Example conversation"""
    config = {"configurable": {"thread_id": "user-1"}}
    
    # Example 1: Greeting
    result = app.invoke({
        "user_input": "Hi, how are you?",
        "conversation_history": [],
        "current_state": ConversationState.ANALYZING
    }, config=config)
    
    print("Bot:", result["bot_response"])
    # Expected: "Hello! I'm doing well, thank you. I'm here to help you with UpGrade A/B testing..."
    
    # Example 2: General question
    result = app.invoke({
        "user_input": "What is A/B testing?",
        "current_state": ConversationState.ANALYZING
    }, config=config)
    
    print("Bot:", result["bot_response"])
    # Expected: Direct explanation of A/B testing
    
    # Example 3: UpGrade-specific action
    result = app.invoke({
        "user_input": "Create a new experiment",
        "current_state": ConversationState.ANALYZING
    }, config=config)
    
    print("Bot:", result["bot_response"])
    # Expected: "What would you like to name this experiment?"