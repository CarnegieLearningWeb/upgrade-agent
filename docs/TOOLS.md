# UpGradeAgent Tools Documentation

This document defines all tools (functions) that the UpGradeAgent will use to interact with the UpGrade API and perform various operations. Tools are designed to integrate seamlessly with the streamlined 5-node architecture.

## Dependencies

```python
import httpx
import asyncio
import uuid
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from typing import Dict, List, Optional, Any, Union
import os
from datetime import datetime
import json
```

## Integration with Streamlined Architecture

These tools are designed to work with our 5-node architecture:

1. **Conversation Analyzer** - Uses tools to check system state and validate parameters
2. **Information Gatherer** - Uses metadata tools to provide context-aware prompts
3. **Confirmation Handler** - Uses tools to show current state before actions
4. **Tool Executor** - Executes these tools based on planned actions
5. **Response Generator** - Uses tool results to create natural responses

## State Schema Integration

```python
from typing import TypedDict, Optional, List, Dict, Any, Literal
from enum import Enum

class ConversationState(Enum):
    ANALYZING = "analyzing"
    GATHERING_INFO = "gathering_info"
    CONFIRMING = "confirming"
    EXECUTING = "executing"
    RESPONDING = "responding"

class AgentState(TypedDict):
    # Core Conversation
    user_input: str
    conversation_history: List[Dict[str, str]]
    current_state: ConversationState
    
    # Operation Context
    intended_action: Optional[str]
    action_confidence: float
    required_params: Dict[str, Any]
    gathered_params: Dict[str, Any]
    missing_params: List[str]
    
    # Tool Execution
    planned_tools: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    
    # Response
    bot_response: str
    response_type: Literal["answer", "question", "confirmation", "clarification"]
    suggested_actions: List[str]
    
    # System Context (cached)
    available_experiments: Optional[List[Dict]]
    context_metadata: Optional[Dict]
    
    # Error Handling
    errors: List[str]
```

## Authentication Utility

```python
class UpGradeAuth:
    def __init__(self):
        self.cached_token = None
        self.credentials = None

    async def get_access_token(self) -> str:
        """Get or refresh access token for UpGrade API"""
        try:
            if not self.credentials:
                credentials_path = os.getenv('UPGRADE_SERVICE_ACCOUNT_KEY_PATH')
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )

            if not self.cached_token or self.credentials.expired:
                self.credentials.refresh(Request())
                self.cached_token = self.credentials.token

            return self.cached_token

        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")

# Global auth instance
auth_manager = UpGradeAuth()
```

## Tool Response Format

All tools return a standardized response format:

```python
{
    "success": bool,
    "data": Any,          # Processed/formatted data
    "raw_response": Any,  # Original API response (when applicable)
    "error": Optional[str],
    "error_type": Optional[str],  # "network", "validation", "api", "auth"
    "endpoint": Optional[str]     # API endpoint called
}
```

---

## 1. System Information & Health Tools

### `check_upgrade_health`

**Purpose**: Check if UpGrade service is running and get version info
**Used by**: Conversation Analyzer (for "status" queries), Tool Executor
**API Endpoint**: `GET /`

```python
async def check_upgrade_health() -> Dict[str, Any]:
    """
    Check UpGrade service health and version

    Returns:
        {
            "success": bool,
            "data": {
                "name": str,
                "version": str,
                "description": str,
                "status": "healthy" | "unhealthy",
                "response_time_ms": int
            },
            "raw_response": dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `get_context_metadata`

**Purpose**: Get available app contexts and their supported values
**Used by**: Conversation Analyzer (for validation), Information Gatherer (for prompts)
**API Endpoint**: `GET /experiments/contextMetaData`

```python
async def get_context_metadata() -> Dict[str, Any]:
    """
    Get all available app contexts and their supported values

    Returns:
        {
            "success": bool,
            "data": {
                "contexts": List[str],  # ["assign-prog", "mathstream", ...]
                "by_context": {
                    "assign-prog": {
                        "conditions": List[str],
                        "group_types": List[str],
                        "sites": List[str],
                        "targets": List[str]
                    }
                }
            },
            "raw_response": dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

---

## 2. Concept Explanation Tools

### `explain_upgrade_concept`

**Purpose**: Explain UpGrade terminology and concepts
**Used by**: Conversation Analyzer (for concept questions), Response Generator
**Data Source**: Built-in knowledge from documentation

```python
async def explain_upgrade_concept(
    concept: str,
    include_examples: bool = True
) -> Dict[str, Any]:
    """
    Explain UpGrade concepts and terminology

    Args:
        concept: The term/concept to explain (e.g., "app context", "decision point")
        include_examples: Whether to include practical examples

    Returns:
        {
            "success": bool,
            "data": {
                "concept": str,
                "definition": str,
                "explanation": str,
                "examples": Optional[List[str]],
                "related_terms": Optional[List[str]],
                "usage_context": str
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

**Supported Concepts**: App Context, Unit of Assignment, Consistency Rule, Post Experiment Rule, Decision Point, Condition, Payload, Segment, Filter Mode, Experiment Status, Assignment Algorithm

---

## 3. Experiment Management Tools

### `get_all_experiments`

**Purpose**: Retrieve experiments with optional filtering
**Used by**: Information Gatherer (for experiment lists), Confirmation Handler
**API Endpoint**: `GET /experiments`

```python
async def get_all_experiments(
    context_filter: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all experiments with optional filtering

    Args:
        context_filter: Filter by app context (e.g., "assign-prog")
        status_filter: Filter by status ("inactive", "enrolling", "enrollmentComplete")

    Returns:
        {
            "success": bool,
            "data": {
                "experiments": List[{
                    "id": str,
                    "name": str,
                    "context": str,
                    "status": str,
                    "created_at": str
                }],
                "count": int,
                "summary": {
                    "by_status": Dict[str, int],
                    "by_context": Dict[str, int]
                }
            },
            "raw_response": List[Dict],
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `get_experiment_details`

**Purpose**: Get complete configuration for a specific experiment
**Used by**: Confirmation Handler (before updates), Response Generator
**API Endpoint**: `GET /experiments/single/<experiment_id>`

```python
async def get_experiment_details(experiment_id: str) -> Dict[str, Any]:
    """
    Get detailed experiment configuration

    Args:
        experiment_id: UUID of the experiment

    Returns:
        {
            "success": bool,
            "data": {
                "id": str,
                "name": str,
                "status": str,
                "context": str,
                "assignment_unit": str,
                "consistency_rule": str,
                "post_experiment_rule": str,
                "conditions": List[{
                    "code": str,
                    "weight": int
                }],
                "decision_points": List[{
                    "site": str,
                    "target": str
                }],
                "inclusion_users": List[str],
                "exclusion_users": List[str],
                "filter_mode": str,
                "created_at": str,
                "updated_at": str
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `create_experiment`

**Purpose**: Create a new experiment with validation
**Used by**: Tool Executor (after confirmation)
**API Endpoint**: `POST /experiments`

```python
async def create_experiment(
    name: str,
    context: str,
    assignment_unit: str = "individual",
    consistency_rule: str = "individual",
    conditions: List[Dict] = None,
    decision_points: List[Dict] = None,
    description: str = "",
    post_experiment_rule: str = "continue",
    filter_mode: str = "excludeAll",
    inclusion_users: List[str] = None,
    exclusion_users: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new experiment with validation

    Args:
        name: Experiment name
        context: App context (must be valid from contextMetadata)
        assignment_unit: "individual" or "group"
        consistency_rule: "individual" or "group"
        conditions: List of conditions with codes and weights
        decision_points: List of decision points with site/target
        description: Optional description
        post_experiment_rule: "continue" or "assign"
        filter_mode: "excludeAll" or "includeAll"
        inclusion_users: List of user IDs to include
        exclusion_users: List of user IDs to exclude

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "name": str,
                "status": str,
                "validation_warnings": List[str]
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `update_experiment_status`

**Purpose**: Change experiment status
**Used by**: Tool Executor (for start/stop commands)
**API Endpoint**: `POST /experiments/state`

```python
async def update_experiment_status(
    experiment_id: str,
    new_status: str
) -> Dict[str, Any]:
    """
    Update experiment status

    Args:
        experiment_id: UUID of experiment
        new_status: "inactive", "enrolling", or "enrollmentComplete"

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "old_status": str,
                "new_status": str,
                "status_changed_at": str
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `delete_experiment`

**Purpose**: Delete an experiment
**Used by**: Tool Executor (after confirmation)
**API Endpoint**: `DELETE /experiments/<experiment_id>`

```python
async def delete_experiment(experiment_id: str) -> Dict[str, Any]:
    """
    Delete an experiment

    Args:
        experiment_id: UUID of experiment to delete

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "experiment_name": str,
                "deleted_at": str
            },
            "raw_response": List[Dict],
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

---

## 4. User Simulation Tools (UPDATED: maybe we don't need these)

### `simulate_user_journey`

**Purpose**: Complete user simulation (init + assign + mark)
**Used by**: Tool Executor (for user simulation requests)
**Combines**: Multiple API calls

```python
async def simulate_user_journey(
    user_id: str,
    context: str,
    site: str,
    target: str,
    group_memberships: Optional[Dict] = None,
    working_group: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Complete user journey simulation

    Args:
        user_id: User identifier
        context: App context
        site: Decision point site
        target: Decision point target
        group_memberships: Optional group memberships
        working_group: Optional working group

    Returns:
        {
            "success": bool,
            "data": {
                "user_id": str,
                "journey_completed": bool,
                "final_assignment": {
                    "condition_code": str,
                    "experiment_id": str,
                    "payload": Dict
                },
                "steps_completed": List[str]
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

---

## 5. Testing & Analysis Tools

### `test_condition_balance`

**Purpose**: Test condition distribution by enrolling multiple users
**Used by**: Tool Executor (for balance testing)
**Combines**: Multiple user simulations

```python
async def test_condition_balance(
    experiment_id: str,
    num_users: int = 100
) -> Dict[str, Any]:
    """
    Test condition balance by enrolling multiple users

    Args:
        experiment_id: Experiment to test
        num_users: Number of users to simulate

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "experiment_name": str,
                "total_users_tested": int,
                "successful_enrollments": int,
                "condition_distribution": Dict[str, {
                    "count": int,
                    "percentage": float,
                    "expected_percentage": float,
                    "deviation": float
                }],
                "balance_analysis": {
                    "is_balanced": bool,
                    "max_deviation": float,
                    "balance_summary": str
                },
                "test_duration_seconds": float
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

---

## Integration Patterns

### Tool Usage in Nodes

```python
# In Conversation Analyzer
def analyze_with_context(state: AgentState) -> Dict[str, Any]:
    # Get system context if needed
    if not state.get("context_metadata"):
        metadata_result = await get_context_metadata()
        if metadata_result["success"]:
            state["context_metadata"] = metadata_result["data"]
    
    # Get experiments if needed for context
    if "experiment" in state["user_input"] and not state.get("available_experiments"):
        experiments_result = await get_all_experiments()
        if experiments_result["success"]:
            state["available_experiments"] = experiments_result["data"]["experiments"]
    
    # Continue with analysis...

# In Information Gatherer
def generate_context_aware_prompt(param: str, state: AgentState) -> str:
    if param == "context" and state.get("context_metadata"):
        contexts = state["context_metadata"]["contexts"]
        return f"Which app context? Available: {', '.join(contexts)}"
    
    if param == "experiment_id" and state.get("available_experiments"):
        experiments = state["available_experiments"]
        options = [f"{exp['name']} ({exp['id'][:8]}...)" for exp in experiments[:5]]
        return f"Which experiment? Options: {', '.join(options)}"
    
    return f"Please provide {param}:"

# In Tool Executor
def execute_planned_tools(state: AgentState) -> Dict[str, Any]:
    planned_tools = state.get("planned_tools", [])
    results = []
    
    for tool_plan in planned_tools:
        tool_name = tool_plan["tool"]
        params = tool_plan["params"]
        
        if tool_name == "create_experiment":
            result = await create_experiment(**params)
        elif tool_name == "test_condition_balance":
            result = await test_condition_balance(**params)
        # ... other tools
        
        results.append(result)
    
    return {"tool_results": results}
```

### Error Handling

```python
async def make_api_request_with_retry(
    method: str,
    url: str,
    max_retries: int = 3,
    timeout: float = 30.0,
    **kwargs
) -> httpx.Response:
    """Standard retry logic for all API calls"""
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
        except httpx.TimeoutException:
            if attempt == max_retries:
                raise Exception(f"Request timed out after {max_retries} retries")
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [500, 502, 503, 504] and attempt < max_retries:
                await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
                continue
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            if attempt == max_retries:
                raise Exception(f"Request failed: {str(e)}")
            await asyncio.sleep(0.5)
```

### Validation

```python
async def validate_experiment_params(params: Dict, context_metadata: Dict) -> List[str]:
    """Validate experiment parameters against context metadata"""
    errors = []
    
    context = params.get('context')
    if context not in context_metadata.get('contexts', []):
        errors.append(f"Invalid context: {context}")
        return errors
    
    context_data = context_metadata['by_context'][context]
    
    # Validate conditions
    for condition in params.get('conditions', []):
        if condition['code'] not in context_data['conditions']:
            errors.append(f"Invalid condition '{condition['code']}' for context '{context}'")
    
    # Validate decision points
    for dp in params.get('decision_points', []):
        if dp['site'] not in context_data['sites']:
            errors.append(f"Invalid site '{dp['site']}' for context '{context}'")
        if dp['target'] not in context_data['targets']:
            errors.append(f"Invalid target '{dp['target']}' for context '{context}'")
    
    return errors
```

## Key Changes from Original

1. **Simplified State**: Aligned with streamlined architecture state schema
2. **Clear Node Integration**: Each tool specifies which nodes use it
3. **Streamlined Responses**: Removed overly detailed response fields
4. **Better Error Handling**: Simplified but robust error handling
5. **Context Integration**: Tools work together to maintain conversation context
6. **Validation Integration**: Built-in validation that works with the conversation flow
