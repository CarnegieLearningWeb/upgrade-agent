# UpGradeAgent Graph Structure Documentation

This document defines the LangGraph architecture for UpGradeAgent, including node structure, state management, routing logic, and error handling patterns.

## Architecture Overview

UpGradeAgent uses a **router-based architecture** with specialized capability nodes. This design provides clear separation of concerns, easy debugging, and maintainable code structure.

```
User Input → Router → Capability Node → Response Formatter → User
             ↓
        Error Handler (if needed)
```

## Graph State Schema

```python
from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum

class NodeStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    RETRY = "retry"
    INCOMPLETE = "incomplete"

class AgentState(TypedDict):
    # User interaction
    user_input: str
    bot_response: str
    conversation_history: List[Dict[str, str]]  # [{"user": "...", "bot": "..."}]
    
    # Routing and flow control
    detected_capability: Optional[str]  # "terminology", "version_check", "experiments", etc.
    routing_confidence: Optional[float]  # 0.0 to 1.0
    needs_clarification: bool
    clarification_options: Optional[List[str]]
    
    # Current operation context
    current_experiment_id: Optional[str]
    current_user_id: Optional[str] 
    active_context: Optional[str]  # App context like "assign-prog"
    operation_type: Optional[str]  # "create", "update", "test", "simulate"
    
    # Cached data (to avoid repeated API calls)
    context_metadata: Optional[Dict[str, Any]]
    all_experiments: Optional[List[Dict]]
    experiment_details: Optional[Dict]
    
    # Multi-step operations
    step_counter: int
    total_steps: Optional[int]
    step_results: List[Dict[str, Any]]
    pending_confirmations: List[str]
    
    # Error handling and retry logic
    last_error: Optional[str]
    error_type: Optional[str]  # "api", "validation", "network", "user_input"
    retry_count: int
    max_retries: int
    node_status: NodeStatus
    
    # Tool execution results
    tool_results: List[Dict[str, Any]]
    raw_api_responses: List[Dict[str, Any]]  # For users who want raw data
```

## Node Architecture

### 1. Entry Node: `input_router`

**Purpose**: Analyze user input and route to appropriate capability nodes
**Inputs**: User input, conversation history
**Outputs**: Detected capability, routing confidence

```python
def input_router(state: AgentState) -> AgentState:
    """
    Route user input to appropriate capability node
    
    Logic:
    1. Analyze user input using Claude
    2. Detect intent and capability needed
    3. Extract parameters and context
    4. Set routing information in state
    """
```

**Routing Categories**:
- `terminology`: Questions about UpGrade concepts
- `version_check`: Health/version requests
- `list_experiments`: List/search experiments
- `experiment_details`: Get specific experiment info
- `experiment_management`: Create/update/delete experiments
- `user_simulation`: Simulate user visits
- `testing`: Balance testing, consistency testing
- `clarification_needed`: Ambiguous input
- `unsupported`: Requests for unsupported features

### 2. Capability Nodes

#### 2.1 `terminology_node`

**Purpose**: Handle UpGrade concept explanations
**Tools Used**: `explain_upgrade_concept`, `list_upgrade_concepts`

```python
def terminology_node(state: AgentState) -> AgentState:
    """
    Handle terminology and concept explanation requests
    
    Supported patterns:
    - "What is [concept]?"
    - "Explain [concept]"
    - "How do [concept1] and [concept2] work together?"
    - "What concepts can you explain?"
    - "Help with [topic]"
    """
```

#### 2.2 `version_check_node`

**Purpose**: Handle health checks and version info
**Tools Used**: `check_upgrade_health`

```python
def version_check_node(state: AgentState) -> AgentState:
    """
    Handle version and health check requests
    
    Supported patterns:
    - "What version?"
    - "Is UpGrade running?"
    - "Health check"
    """
```

#### 2.3 `experiment_listing_node`

**Purpose**: List and search experiments
**Tools Used**: `get_all_experiments`, `get_experiment_names`

```python
def experiment_listing_node(state: AgentState) -> AgentState:
    """
    Handle experiment listing and searching
    
    Supported patterns:
    - "List all experiments"
    - "Show experiments in [context]"
    - "Find experiments created today"
    - "What experiments are running?"
    """
```

#### 2.4 `experiment_details_node`

**Purpose**: Get detailed experiment information
**Tools Used**: `get_experiment_details`, `get_context_metadata`

```python
def experiment_details_node(state: AgentState) -> AgentState:
    """
    Handle detailed experiment information requests
    
    Supported patterns:
    - "Show details for [experiment]"
    - "What are the conditions in [experiment]?"
    - "Explain the setup of [experiment]"
    """
```

#### 2.5 `experiment_management_node`

**Purpose**: Create, update, delete experiments
**Tools Used**: `create_experiment`, `update_experiment`, `update_experiment_status`, `delete_experiment`

```python
def experiment_management_node(state: AgentState) -> AgentState:
    """
    Handle experiment CRUD operations
    
    Supported patterns:
    - "Create an experiment with..."
    - "Update [experiment] to..."
    - "Start/stop [experiment]"
    - "Delete [experiment]"
    
    Multi-step process:
    1. Validate parameters
    2. Get user confirmation
    3. Execute operation
    4. Verify result
    """
```

#### 2.6 `user_simulation_node`

**Purpose**: Simulate user decision point visits
**Tools Used**: `initialize_user`, `get_user_assignments`, `mark_decision_point_visit`, `simulate_user_journey`

```python
def user_simulation_node(state: AgentState) -> AgentState:
    """
    Handle user simulation requests
    
    Supported patterns:
    - "Simulate user [id] visiting [decision point]"
    - "Initialize user [id] with groups [...]"
    - "What condition would user [id] get?"
    """
```

#### 2.7 `testing_node`

**Purpose**: Perform balance and consistency testing
**Tools Used**: `test_condition_balance`, `test_consistency_rules`, `generate_test_users`

```python
def testing_node(state: AgentState) -> AgentState:
    """
    Handle testing and analysis requests
    
    Supported patterns:
    - "Test condition balance for [experiment]"
    - "Test consistency rules for [experiment]" 
    - "Enroll 100 users in [experiment]"
    
    Multi-step process:
    1. Prepare experiment (ensure correct status)
    2. Generate/validate test parameters
    3. Execute test
    4. Analyze results
    5. Generate report
    """
```

### 3. Support Nodes

#### 3.1 `clarification_node`

**Purpose**: Handle ambiguous inputs and gather missing information
**Tools Used**: Context-specific validation tools

```python
def clarification_node(state: AgentState) -> AgentState:
    """
    Handle requests that need clarification
    
    Examples:
    - Multiple experiments with similar names
    - Missing required parameters
    - Ambiguous experiment references
    """
```

#### 3.2 `error_handler_node`

**Purpose**: Handle errors and determine retry strategies
**Tools Used**: None (pure logic)

```python
def error_handler_node(state: AgentState) -> AgentState:
    """
    Handle errors and implement retry logic
    
    Error types:
    - API errors (network, timeout, 500s)
    - Validation errors (invalid parameters)
    - User input errors (typos, missing info)
    - Unsupported feature requests
    """
```

#### 3.3 `response_formatter_node`

**Purpose**: Format final responses for user consumption
**Tools Used**: None (pure formatting)

```python
def response_formatter_node(state: AgentState) -> AgentState:
    """
    Format responses based on capability and user preferences
    
    Formatting options:
    - Detailed vs summary
    - Include raw API responses
    - Table formatting for test results
    - Error message formatting
    """
```

## Routing Logic

### Conditional Edges

```python
def route_after_input(state: AgentState) -> str:
    """Route based on detected capability"""
    capability = state["detected_capability"]
    confidence = state["routing_confidence"]
    
    if confidence < 0.7:
        return "clarification_node"
    
    capability_routes = {
        "terminology": "terminology_node",
        "version_check": "version_check_node", 
        "list_experiments": "experiment_listing_node",
        "experiment_details": "experiment_details_node",
        "experiment_management": "experiment_management_node",
        "user_simulation": "user_simulation_node",
        "testing": "testing_node",
        "unsupported": "error_handler_node"
    }
    
    return capability_routes.get(capability, "clarification_node")

def route_after_capability(state: AgentState) -> str:
    """Route after capability node execution"""
    if state["node_status"] == NodeStatus.ERROR:
        if state["retry_count"] < state["max_retries"]:
            return "error_handler_node"
        else:
            return "response_formatter_node"
    
    if state["needs_clarification"]:
        return "clarification_node"
    
    return "response_formatter_node"

def route_after_error(state: AgentState) -> str:
    """Route after error handling"""
    if state["node_status"] == NodeStatus.RETRY:
        # Return to the capability node that failed
        return state["detected_capability"] + "_node"
    
    return "response_formatter_node"
```

## Multi-Step Operation Patterns

### Pattern 1: Simple Request-Response
```
User Input → Router → Capability Node → Response Formatter → End
```
Examples: Version check, terminology explanations, experiment listing

### Pattern 2: Validation Required
```
User Input → Router → Capability Node → Validation → Response Formatter → End
                                    ↓ (if validation fails)
                               Clarification Node ↑
```
Examples: Creating experiments, user simulation with missing parameters

### Pattern 3: Multi-Step Process
```
User Input → Router → Capability Node (Step 1) → ... → Capability Node (Step N) → Response Formatter → End
```
Examples: Condition balance testing, consistency rule testing

### Pattern 4: Error Recovery
```
Any Node → Error Handler → Retry (if possible) → Original Node
                      ↓ (if not retryable)
                 Response Formatter → End
```

## State Management Patterns

### Cache Management
```python
def update_experiment_cache(state: AgentState, experiment_data: Dict) -> AgentState:
    """Update cached experiment data to avoid repeated API calls"""
    if not state["all_experiments"]:
        state["all_experiments"] = []
    
    # Update or add experiment data
    existing_ids = {exp["id"] for exp in state["all_experiments"]}
    if experiment_data["id"] not in existing_ids:
        state["all_experiments"].append(experiment_data)
    
    return state
```

### Multi-Step Progress Tracking
```python
def init_multi_step_operation(state: AgentState, total_steps: int) -> AgentState:
    """Initialize multi-step operation tracking"""
    state["step_counter"] = 0
    state["total_steps"] = total_steps
    state["step_results"] = []
    return state

def advance_step(state: AgentState, step_result: Dict) -> AgentState:
    """Advance to next step and record result"""
    state["step_counter"] += 1
    state["step_results"].append(step_result)
    return state
```

## Error Handling Strategy

### Error Types and Responses

1. **API Errors**:
   - Network timeouts → Retry with exponential backoff
   - 500/502/503 errors → Retry up to 3 times
   - 404 errors → Inform user, suggest alternatives
   - 401/403 errors → Check authentication, inform user

2. **Validation Errors**:
   - Invalid experiment parameters → Explain what's wrong, suggest fixes
   - Unsupported features → Explain limitations, suggest alternatives
   - Missing required data → Ask for missing information

3. **User Input Errors**:
   - Typos in experiment names → Suggest similar names
   - Ambiguous references → Ask for clarification
   - Missing context → Guide user to provide needed info

### Retry Logic
```python
def should_retry_error(error_type: str, retry_count: int) -> bool:
    """Determine if error should be retried"""
    if retry_count >= 3:
        return False
    
    retryable_errors = ["network", "timeout", "api_500", "api_502", "api_503"]
    return error_type in retryable_errors
```

## Graph Definition

```python
from langgraph.graph import StateGraph, END

def create_upgrade_agent_graph():
    """Create the complete UpGradeAgent graph"""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("input_router", input_router)
    graph.add_node("terminology_node", terminology_node)
    graph.add_node("version_check_node", version_check_node)
    graph.add_node("experiment_listing_node", experiment_listing_node)
    graph.add_node("experiment_details_node", experiment_details_node)
    graph.add_node("experiment_management_node", experiment_management_node)
    graph.add_node("user_simulation_node", user_simulation_node)
    graph.add_node("testing_node", testing_node)
    graph.add_node("clarification_node", clarification_node)
    graph.add_node("error_handler_node", error_handler_node)
    graph.add_node("response_formatter_node", response_formatter_node)
    
    # Define entry point
    graph.set_entry_point("input_router")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "input_router",
        route_after_input,
        {
            "terminology_node": "terminology_node",
            "version_check_node": "version_check_node",
            "experiment_listing_node": "experiment_listing_node",
            "experiment_details_node": "experiment_details_node",
            "experiment_management_node": "experiment_management_node",
            "user_simulation_node": "user_simulation_node",
            "testing_node": "testing_node",
            "clarification_node": "clarification_node",
            "error_handler_node": "error_handler_node"
        }
    )
    
    # Add edges from capability nodes
    capability_nodes = [
        "terminology_node", "version_check_node", "experiment_listing_node",
        "experiment_details_node", "experiment_management_node", 
        "user_simulation_node", "testing_node"
    ]
    
    for node in capability_nodes:
        graph.add_conditional_edges(
            node,
            route_after_capability,
            {
                "clarification_node": "clarification_node",
                "error_handler_node": "error_handler_node",
                "response_formatter_node": "response_formatter_node"
            }
        )
    
    # Add edges from support nodes
    graph.add_conditional_edges(
        "error_handler_node",
        route_after_error,
        {
            # Dynamic routing back to failed nodes
            "terminology_node": "terminology_node",
            "version_check_node": "version_check_node",
            "experiment_listing_node": "experiment_listing_node",
            "experiment_details_node": "experiment_details_node",
            "experiment_management_node": "experiment_management_node",
            "user_simulation_node": "user_simulation_node", 
            "testing_node": "testing_node",
            "response_formatter_node": "response_formatter_node"
        }
    )
    
    graph.add_edge("clarification_node", "input_router")  # Loop back for re-routing
    graph.add_edge("response_formatter_node", END)
    
    return graph.compile()
```

## Usage Example

```python
# Initialize the graph
app = create_upgrade_agent_graph()

# Run a conversation
initial_state = {
    "user_input": "Test condition balance for My Experiment with 100 users",
    "bot_response": "",
    "conversation_history": [],
    "retry_count": 0,
    "max_retries": 3,
    "node_status": NodeStatus.SUCCESS,
    "step_counter": 0,
    "needs_clarification": False
}

# Execute the graph
final_state = app.invoke(initial_state)
print(final_state["bot_response"])
```

## Development and Testing

### Unit Testing Nodes
```python
def test_terminology_node():
    """Test terminology explanation functionality"""
    state = AgentState(
        user_input="What is app context?",
        detected_capability="terminology"
    )
    
    result = terminology_node(state)
    assert "App Context" in result["bot_response"]
    assert result["node_status"] == NodeStatus.SUCCESS
```

### Integration Testing
```python
def test_full_workflow():
    """Test complete user interaction workflow"""
    app = create_upgrade_agent_graph()
    
    state = {"user_input": "List all experiments in assign-prog context"}
    result = app.invoke(state)
    
    assert result["detected_capability"] == "list_experiments"
    assert "experiments" in result["bot_response"].lower()
```
