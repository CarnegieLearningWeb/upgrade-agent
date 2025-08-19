# UpGradeAgent Graph Structure Documentation

## Overview
UpGradeAgent is a LangGraph-based chatbot for UpGrade A/B testing platform. It explains terminology, manages experiments, and simulates user interactions through natural language commands.

## Graph Architecture

### 5-Node Structure
1. **Conversation Analyzer** (LLM) - Intent classification and orchestration
2. **Information Gatherer** (LLM) - Data collection and validation  
3. **Confirmation Handler** (Non-LLM) - Safety confirmations for destructive actions
4. **Tool Executor** (Non-LLM) - API execution layer
5. **Response Generator** (LLM) - All user-facing communication

---
## LLM
### How to create the LLM instance  
llm = ChatAnthropic(
    api_key=SecretStr(config.ANTHROPIC_API_KEY),
    model_name=config.MODEL_NAME
    temperature=0.1,
    timeout=30,
    stop=None
)

## State Schema

```python
from typing import Dict, List, Optional, Literal
from typing_extensions import TypedDict

class AgentState(TypedDict):
    # === Core Context ===
    user_input: str
    conversation_history: List[Dict[str, str]]
    current_state: Literal["ANALYZING", "GATHERING_INFO", "CONFIRMING", "EXECUTING", "RESPONDING"]
    
    # === Analyzer Outputs ===
    intent_type: Literal["direct_answer", "needs_info"]
    confidence: float  # 0.0 to 1.0
    user_request_summary: Optional[str]  # For other nodes to understand context, can be updated by Gatherer
    
    # === Gatherer Outputs ===
    action_needed: Optional[Literal[
        "create_experiment", "update_experiment", "delete_experiment",
        "update_experiment_status", "init_experiment_user", 
        "get_decision_point_assignments", "mark_decision_point"
    ]]
    action_params: Dict[str, Any]  # Collected/validated parameters
    missing_params: List[str]  # What we still need from user
    
    # === Large Static Data (Accessed On-Demand) ===
    context_metadata: Optional[Dict]  # Available contexts and their details
    experiment_names: Optional[List[Dict]]  # Experiment names and IDs
    all_experiments: Optional[List[Dict]]  # Full details of all experiments
    
    # === Dynamic Gathered Information ===
    gathered_info: Dict[str, Any]  # Query-specific data with predictable keys
    
    # === Confirmation Flow ===
    needs_confirmation: bool
    confirmation_message: Optional[str]
    user_confirmed: bool
    
    # === Execution Log ===
    execution_log: List[Dict[str, Any]]  # Chronological log of all executed actions
    
    # === Error Handling ===
    errors: Dict[str, str]  # {"api": "Failed to connect", "auth": "Invalid token", "validation": "Invalid params"}
    
    # === Response ===
    final_response: Optional[str]
    conversation_complete: bool
```

---

## Node Specifications

### 1. Conversation Analyzer

**Type**: LLM-based  
**Purpose**: Central orchestrator that classifies user intent and manages conversation flow

**Tools Available**:
```python
@tool
def analyze_user_request(
    intent_type: Literal["direct_answer", "needs_info"],
    confidence: float,  # 0.0 to 1.0
    user_request_summary: str,  # Summary for other nodes
    reasoning: str  # Why this classification was chosen
) -> str:
    """Analyze user input and determine next action"""
```

**Routing Logic**:
```python
def analyzer_routing(state):
    if state.get("intent_type") == "direct_answer":
        return "response_generator"
    elif state.get("intent_type") == "needs_info":
        return "information_gatherer" 
    elif state.get("user_confirmed") and state.get("action_needed"):
        return "tool_executor"
    else:
        return "response_generator"
```

**Key Responsibilities**:
- Classify whether query can be answered directly or needs more information
- Understand conversation context and references ("that experiment we created")
- Generate summaries for other nodes
- Orchestrate overall conversation flow

### 2. Information Gatherer

**Type**: LLM-based  
**Purpose**: Collect, validate, and prepare all information needed for user requests

**Tools Available**:

*API Functions (Store Results in Static Variables)*:
```python
# These store large data in static variables for optional access
check_upgrade_health() -> stores in gathered_info["upgrade_health"]
get_context_metadata() -> context_metadata  
get_experiment_names() -> experiment_names
get_all_experiments() -> all_experiments
get_experiment_details(experiment_id) -> stores in gathered_info["experiment_details"]
```

*Utility Functions (Auto-Store in gathered_info)*:
```python
# These automatically store results in gathered_info with predictable keys
get_core_terms() -> gathered_info["core_terms"]
get_assignment_terms() -> gathered_info["assignment_terms"]
get_available_contexts() -> gathered_info["available_contexts"]
get_create_experiment_schema() -> gathered_info["create_experiment_schema"]
get_update_experiment_schema() -> gathered_info["update_experiment_schema"]
get_update_experiment_status_schema() -> gathered_info["update_experiment_status_schema"]
get_delete_experiment_schema() -> gathered_info["delete_experiment_schema"]
get_init_experiment_user_schema() -> gathered_info["init_experiment_user_schema"]
get_get_decision_point_assignments_schema() -> gathered_info["get_decision_point_assignments_schema"]
get_mark_decision_point_schema() -> gathered_info["mark_decision_point_schema"]
get_conditions_for_context(context: str) -> gathered_info[f"conditions_for_{context}"]
get_decision_points_for_context(context: str) -> gathered_info[f"decision_points_for_{context}"]
get_group_types_for_context(context: str) -> gathered_info[f"group_types_for_{context}"]
```

*State Management Tools*:
```python
@tool
def set_action_needed(
    action: Literal["create_experiment", "update_experiment", "delete_experiment",
                   "update_experiment_status", "init_experiment_user", 
                   "get_decision_point_assignments", "mark_decision_point"],
    reasoning: str
) -> str:
    """Set what action is needed for Tool Executor"""

@tool  
def set_action_params(action_params: Dict[str, Any]) -> str:
    """Set parameters for the action (only non-default values)"""

@tool
def set_missing_params(missing_params: List[str]) -> str:
    """Set what parameters are still needed from user"""

@tool
def update_action_params(key: str, value: Any) -> str:
    """Add or update a specific parameter (for progressive gathering)"""
```

*Error Handling Tools*:
```python
@tool
def add_error(error_type: Literal["api", "auth", "validation", "not_found", "unknown"], message: str) -> str:
    """Add an error message when operations fail"""
    state["errors"][error_type] = message
    return f"Error recorded: {error_type} - {message}"
```

**Tool Behavior**: All utility functions automatically store their results in `gathered_info` with predictable keys and return the data for immediate LLM use.

**Routing Logic**:
```python
def gatherer_routing(state):
    if not state.get("action_needed"):
        return "response_generator"  # Pure information gathering, ready to respond
    elif state.get("missing_params"):
        return "response_generator"  # Need more info from user first
    else:
        return "confirmation_handler"  # Ready for execution after confirmation
```

**Key Responsibilities**:
- Handle complex multi-step information gathering internally
- Validate user-provided parameters against UpGrade schemas
- Build complete parameter sets with proper defaults
- Set final action for Tool Executor only after all info is gathered
- Determine what information is still missing
- Store query-specific data in gathered_info automatically

**Example Flow for Complex Request**:
```python
# User: "What conditions are available for assign-prog context?"
1. get_conditions_for_context("assign-prog")  # Auto-stores in gathered_info["conditions_for_assign-prog"]
2. # No action_needed set - this is informational
3. Routes to Response Generator

# User: "Create experiment with first context"
1. get_context_metadata()  # Stores in context_metadata
2. get_available_contexts()  # Stores in gathered_info["available_contexts"]
3. get_create_experiment_schema()  # Stores in gathered_info["create_experiment_schema"]
4. set_action_params({"context": "first_context", "name": "..."})
5. set_action_needed("create_experiment")  # Ready for confirmation & execution

# User: "Start the Math Hints experiment"
1. get_experiment_names()  # Find experiment ID for "Math Hints"
2. get_update_experiment_status_schema()  # Stores in gathered_info["update_experiment_status_schema"]
3. set_action_params({"experiment_id": "uuid", "status": "enrolling"})
4. set_action_needed("update_experiment_status")  # Ready for confirmation & execution
```

### 3. Confirmation Handler

**Type**: Non-LLM (Static Logic)  
**Purpose**: Generate safety confirmations for ALL operations executed through Tool Executor

**Tools Available**: None

**Implementation**:
```python
def confirmation_handler(state):
    action = state.get("action_needed")
    params = state.get("action_params", {})
    
    # Generate confirmation messages based on action type
    if action == "create_experiment":
        message = f"Create experiment '{params['name']}' in context '{params['context']}'?"
        
    elif action == "delete_experiment":
        message = f"⚠️ PERMANENTLY DELETE experiment '{params['name']}'? This cannot be undone!"
        
    elif action == "update_experiment":
        message = f"Update experiment '{params['name']}' with new settings?"
        
    elif action == "update_experiment_status":
        status = params.get('status', 'unknown')
        exp_name = params.get('name', params.get('experiment_id', 'unknown'))
        message = f"Change experiment '{exp_name}' status to '{status}'?"
        
    elif action == "init_experiment_user":
        message = f"Initialize user '{params.get('user_id', 'unknown')}' for experiment simulation?"
        
    elif action == "get_decision_point_assignments":
        message = f"Get condition assignments for context '{params.get('context', 'unknown')}'?"
        
    elif action == "mark_decision_point":
        message = f"Mark decision point visit for experiment '{params.get('assigned_condition', {}).get('experiment_id', 'unknown')}'?"
    
    state["confirmation_message"] = message
    state["needs_confirmation"] = True
    return state
```

**Routing Logic**:
```python
def confirmation_routing(state):
    return "response_generator"  # Always show confirmation to user
```

**Key Responsibilities**:
- Generate appropriate confirmation messages for each action type
- Add warning indicators for irreversible operations
- Require confirmation for ALL operations that modify state
- Fast, predictable confirmation generation

### 4. Tool Executor

**Type**: Non-LLM (Static Logic)  
**Purpose**: Execute UpGrade API calls using prepared parameters

**Tools Available**:
```python
# All UpGrade API modification endpoints
create_experiment(**params) -> created_experiment_details
update_experiment(experiment_id, **params) -> updated_experiment_details 
update_experiment_status(experiment_id, status) -> updated_experiment_details
delete_experiment(experiment_id) -> deleted_experiment_details
init_experiment_user(**params) -> experiment_user
get_decision_point_assignments(**params) -> decision_point_assignments
mark_decision_point(**params) -> marked_decision_point
```

**Implementation**:
```python
def tool_executor(state):
    from datetime import datetime
    
    action = state.get("action_needed")
    params = state.get("action_params", {})
    
    ACTION_MAP = {
        "create_experiment": create_experiment,
        "delete_experiment": delete_experiment,
        "update_experiment": update_experiment,
        "update_experiment_status": update_experiment_status,
        "init_experiment_user": init_experiment_user,
        "get_decision_point_assignments": get_decision_point_assignments,
        "mark_decision_point": mark_decision_point
    }
    
    if action in ACTION_MAP:
        try:
            result = ACTION_MAP[action](**params)
            
            # Log successful execution
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "params": params,
                "result": result,
                "status": "success",
                "error_message": None
            }
            
        except Exception as e:
            # Log failed execution
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "params": params,
                "result": None,
                "status": "error",
                "error_message": str(e)
            }
            state["errors"]["execution"] = str(e)
        
        # Add to execution log
        if "execution_log" not in state:
            state["execution_log"] = []
        state["execution_log"].append(log_entry)
    
    return state
```

**Routing Logic**:
```python
def executor_routing(state):
    return "conversation_analyzer"  # Always return to analyzer to process results
```

**Key Responsibilities**:
- Execute single action specified by action_needed
- Handle API errors gracefully and store in errors dict
- Log all executions (success and failure) in chronological execution_log
- Simple mapping from action string to tool function

### 5. Response Generator

**Type**: LLM-based  
**Purpose**: All user-facing communication and response formatting

**Tools Available**:
```python
# Access large static data when needed
@tool
def get_context_metadata() -> Optional[Dict]:
    """Get stored context metadata (large data)"""
    return state.get("context_metadata")

@tool
def get_experiment_names() -> Optional[List[Dict]]:
    """Get stored experiment names (large data)"""
    return state.get("experiment_names")

@tool
def get_all_experiments() -> Optional[List[Dict]]:
    """Get all experiment details (large data)"""
    return state.get("all_experiments")

# Access gathered information
@tool
def get_all_gathered_info() -> Dict:
    """Get all gathered information (query-specific data)"""
    return state.get("gathered_info", {})

# Access execution results
@tool
def get_execution_log() -> List[Dict[str, Any]]:
    """Get chronological log of all executed actions"""
    return state.get("execution_log", [])

# Check for errors
@tool
def get_errors() -> Dict[str, str]:
    """Get any errors that occurred during processing"""
    return state.get("errors", {})
```

**Routing Logic**:
```python
def response_routing(state):
    if state.get("conversation_complete"):
        return "END"
    else:
        return "conversation_analyzer"  # Wait for next user input
```

**Key Responsibilities**:
- Format all responses in natural, helpful language
- Present confirmation requests clearly
- Explain results and provide next steps
- Handle error communication using error information from specific error types
- Generate reports based on execution log history
- Maintain consistent conversational tone
- Access large static data only when needed for token efficiency
- Use gathered_info for query-specific responses

---

## Flow Examples

### Simple Question Flow
```
User: "What is A/B testing?"
Analyzer (direct_answer) → Response Generator → END
```

### Information Gathering Flow  
```
User: "What conditions are available for assign-prog?"
Analyzer (needs_info) → Gatherer (get_conditions_for_context, stores in gathered_info) → 
Response Generator (get_all_gathered_info, formats response) → END
```

### Schema Information Flow
```
User: "What parameters are required to create an experiment?"
Analyzer (needs_info) → Gatherer (get_create_experiment_schema, stores in gathered_info) →
Response Generator (get_all_gathered_info, explains schema) → END
```

### Experiment Status Update Flow
```
User: "Start the Math Hints experiment"
Analyzer → Gatherer (find experiment ID, set_action_needed("update_experiment_status")) → 
Confirmation Handler → Response Generator ("Change status to 'enrolling'?") →
User: "yes" → Analyzer → Tool Executor → 
Analyzer → Response Generator ("Experiment 'Math Hints' status changed to enrolling") → END
```

### Action with Missing Information Flow
```
User: "Create experiment Foo"
Analyzer → Gatherer (missing context, set_missing_params) → Response Generator ("Which context?") → 
User: "assign-prog" → Analyzer → Gatherer (set_action_needed, complete params) → 
Confirmation Handler → Response Generator ("Confirm creation?") →
User: "yes" → Analyzer → Tool Executor → Analyzer → Response Generator → END
```

### Complete Action Flow
```
User: "Delete experiment Foo" 
Analyzer → Gatherer (validates experiment exists, set_action_needed) → Confirmation Handler → 
Response Generator ("⚠️ Permanently delete?") → User: "yes" → 
Analyzer → Tool Executor → Analyzer → Response Generator → END
```

### Error Handling Flow
```
User: "Create experiment with invalid-context"
Analyzer → Gatherer (validation fails, add_error with type "validation") → 
Response Generator (get_errors, explains validation failure) → END
```

### Multi-Action Session Flow
```
User: "Create experiment Foo" → ... → Confirmation → Tool Executor (logs creation) →
User: "Start that experiment" → ... → Confirmation → Tool Executor (logs status update) →
User: "Update that experiment's weights" → ... → Confirmation → Tool Executor (logs update) →
User: "What have we accomplished?" → Response Generator (get_execution_log, summarizes all actions) → END
```

### Status Transition Flow
```
User: "Stop the Running Test experiment"
Analyzer → Gatherer (find experiment, validate current status is "enrolling") →
Gatherer (set_action_needed("update_experiment_status"), params: {status: "enrollmentComplete"}) →
Confirmation Handler → Response Generator ("Change status to 'enrollmentComplete'?") →
User: "yes" → Analyzer → Tool Executor → 
Analyzer → Response Generator ("Experiment stopped successfully") → END
```

---

## Implementation Guidelines

### Error Handling
- Gatherer validates parameters and uses add_error() tool for failures with specific error types
- Tool Executor stores execution errors in errors["execution"]
- Response Generator uses get_errors() to communicate failures to users with appropriate context
- missing_params is not an error - it's normal progressive gathering
- Error types: "api", "auth", "validation", "not_found", "unknown"

### State Management
- Large static data (context_metadata, experiment_names, all_experiments) accessed on-demand
- Query-specific data automatically stored in gathered_info with predictable keys
- Each node updates only its designated state variables
- action_needed is only set when ready for execution

### Performance Optimization
- Response Generator only calls large data tools when needed
- gathered_info contains small, relevant data for most responses
- Confirmation Handler and Tool Executor are non-LLM for speed
- Auto-storage prevents redundant tool calls within same gathering session

### Security
- All destructive operations require explicit confirmation
- Parameter validation prevents malformed API calls
- Error messages help users understand what went wrong without exposing sensitive details
- action_needed ensures only valid actions reach Tool Executor

### Data Storage Patterns
- **Static variables**: Large, frequently referenced data (contexts, experiment lists)
- **gathered_info**: Small, query-specific data with predictable keys
- **execution_log**: Chronological record of all actions taken (success/failure)
- **Auto-storage**: Tools automatically store results for later access
- **Token efficiency**: Response Generator chooses what data to access
- **Session history**: Execution log enables progress summaries and multi-action reporting

### Action Confirmation Patterns
- ALL actions executed through Tool Executor require user confirmation
- Confirmation messages are tailored to each action type
- Destructive operations (like delete) include warning indicators (⚠️)
- Status changes show both current and target states when possible
- Confirmation ensures users have full control over all system modifications
- Valid status transitions for experiments: 
  - inactive → enrolling (start experiment)
  - enrolling → enrollmentComplete (stop experiment)
  - any → cancelled (cancel experiment)
- Tool Executor logs all confirmed actions in execution_log for tracking