# UpGradeAgent Tools Documentation

This document defines all tools (functions) that the UpGradeAgent will use to interact with the UpGrade API and perform various operations. Tools are organized by bot capabilities and include comprehensive error handling and validation.

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

## Graph State Schema (Minimal)

```python
from typing import TypedDict

class AgentState(TypedDict):
    # User input and conversation
    user_input: str
    bot_response: str

    # Current context
    current_experiment_id: Optional[str]
    current_user_id: Optional[str]
    active_context: Optional[str]  # e.g., "assign-prog", "mathstream"

    # Cached data to avoid repeated API calls
    context_metadata: Optional[Dict]
    all_experiments: Optional[List[Dict]]

    # Error handling
    last_error: Optional[str]
    retry_count: int
```

## Authentication Utility

```python
# Not a tool - utility function for other tools to use
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

## 1. UpGrade Terminology & Help Capabilities

### `explain_upgrade_concept`

**Purpose**: Explain UpGrade terminology and concepts to users
**When to use**: When users ask about UpGrade terms, concepts, or how things work
**Data Source**: Built-in knowledge from CORE_TERMS.md and ASSIGNMENT_BEHAVIOR.md

```python
async def explain_upgrade_concept(
    concept: str,
    include_examples: bool = True,
    include_related_terms: bool = True
) -> Dict[str, Any]:
    """
    Explain UpGrade concepts and terminology

    Args:
        concept: The term/concept to explain (e.g., "app context", "decision point")
        include_examples: Whether to include practical examples
        include_related_terms: Whether to include related concepts

    Returns:
        {
            "success": bool,
            "data": {
                "concept": str,
                "definition": str,
                "detailed_explanation": str,
                "examples": Optional[List[str]],
                "related_concepts": Optional[List[{
                    "term": str,
                    "brief_description": str
                }]],
                "common_values": Optional[List[str]],  # For concepts with predefined options
                "usage_context": str,  # When/where this concept is used
                "concept_category": str  # "experiment_design", "assignment", "data_collection", etc.
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

**Supported Concepts**:

- App Context / Context
- Unit of Assignment / Assignment Unit
- Consistency Rule
- Post Experiment Rule / Post Rule
- Design Type
- Assignment Algorithm
- Decision Point
- Site and Target
- Condition
- Payload
- Segment (Inclusion/Exclusion)
- Filter Mode
- Experiment Status / State
- Group and Working Group
- Assignment Behavior Patterns

### `list_upgrade_concepts`

**Purpose**: List all available UpGrade concepts that can be explained
**When to use**: When users want to browse available help topics

```python
async def list_upgrade_concepts() -> Dict[str, Any]:
    """
    List all available UpGrade concepts for explanation

    Returns:
        {
            "success": bool,
            "data": {
                "categories": {
                    "experiment_design": List[str],
                    "assignment_rules": List[str],
                    "data_collection": List[str],
                    "user_management": List[str]
                },
                "all_concepts": List[str],
                "total_count": int
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

---

## 2. Version Check & Health Capabilities

### `check_upgrade_health`

**Purpose**: Check if UpGrade service is running and get version info
**When to use**: Health checks, version verification
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
                "status": "healthy" | "unhealthy"
            },
            "raw_response": dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

**Implementation Notes**:

- No authentication required
- Timeout: 5 seconds (health check should be fast)
- No retries needed for health checks

---

## 3. Experiment Management Capabilities

### `get_context_metadata`

**Purpose**: Get available app contexts, conditions, group types, sites, and targets
**When to use**: Before creating/updating experiments, for validation
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
                "metadata": Dict,       # Full contextMetadata object
                "by_context": {
                    "assign-prog": {
                        "conditions": List[str],
                        "group_types": List[str],
                        "sites": List[str],
                        "targets": List[str]
                    },
                    # ... other contexts
                }
            },
            "raw_response": dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `get_experiment_names`

**Purpose**: Get simple list of experiment names and IDs
**When to use**: Quick lookups, autocomplete suggestions
**API Endpoint**: `GET /experiments/names`

```python
async def get_experiment_names() -> Dict[str, Any]:
    """
    Get all experiment names and IDs

    Returns:
        {
            "success": bool,
            "data": {
                "experiments": List[{"id": str, "name": str}],
                "name_to_id": Dict[str, str],  # For easy lookup
                "count": int
            },
            "raw_response": List[Dict],
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `get_all_experiments`

**Purpose**: Retrieve all defined experiments with optional filtering
**When to use**: Listing experiments, searching by criteria
**API Endpoint**: `GET /experiments`

```python
async def get_all_experiments(
    context_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    date_filter: Optional[str] = None  # "today", "yesterday", "this_week"
) -> Dict[str, Any]:
    """
    Get all experiments with optional filtering

    Args:
        context_filter: Filter by app context (e.g., "assign-prog")
        status_filter: Filter by status ("inactive", "enrolling", "enrollmentComplete")
        date_filter: Filter by creation date

    Returns:
        {
            "success": bool,
            "data": {
                "experiments": List[Dict],
                "total_count": int,
                "filtered_count": int,
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
**When to use**: Showing experiment details, before updating
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
                "context": List[str],
                "assignment_unit": str,
                "consistency_rule": str,
                "post_experiment_rule": str,
                "conditions": List[{
                    "id": str,
                    "code": str,
                    "weight": int,
                    "payloads": List[Dict]
                }],
                "decision_points": List[{
                    "id": str,
                    "site": str,
                    "target": str
                }],
                "segments": {
                    "inclusion": List[str],  # User IDs
                    "exclusion": List[str],  # User IDs
                    "filter_mode": str
                },
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

**Purpose**: Create a new experiment with full validation
**When to use**: Creating new experiments
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
    exclusion_users: List[str] = None,
    inclusion_groups: List[Dict] = None,
    exclusion_groups: List[Dict] = None
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
        inclusion_groups: List of group specifications
        exclusion_groups: List of group specifications

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "name": str,
                "status": str,
                "validation_warnings": List[str],  # Non-blocking issues
                "created_conditions": List[Dict],
                "created_decision_points": List[Dict]
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

**Validation Logic**:

- Verify context exists in contextMetadata
- Verify conditions are supported by context
- Verify decision points (sites/targets) are supported
- Verify assignment weights sum to 100%
- Verify group types are supported (for group assignment)
- Check for unsupported features (factorial, within-subjects, etc.)

### `update_experiment`

**Purpose**: Update existing experiment configuration
**When to use**: Modifying experiment settings
**API Endpoint**: `PUT /experiments/<experiment_id>`

```python
async def update_experiment(
    experiment_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update experiment configuration

    Args:
        experiment_id: UUID of experiment to update
        updates: Dictionary of fields to update

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "updated_fields": List[str],
                "validation_warnings": List[str],
                "version_number": int
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `update_experiment_status`

**Purpose**: Change experiment status (inactive/enrolling/enrollmentComplete)
**When to use**: Starting/stopping experiments
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
                "status_changed_at": str,
                "state_log_created": bool
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
**When to use**: Removing test/unwanted experiments
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
                "deleted_at": str,
                "cleanup_completed": bool
            },
            "raw_response": List[Dict],
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

---

## 4. User Simulation & Decision Point Capabilities

### `initialize_user`

**Purpose**: Initialize a user in UpGrade system with group memberships
**When to use**: Before simulating user interactions
**API Endpoint**: `POST /v6/init`

```python
async def initialize_user(
    user_id: str,
    context: str,
    group_memberships: Optional[Dict[str, List[str]]] = None,
    working_group: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Initialize user with group memberships

    Args:
        user_id: Unique identifier for user
        context: App context for validation
        group_memberships: Dict of group types to group IDs (for segments)
        working_group: Dict of current active group memberships (for assignment)

    Returns:
        {
            "success": bool,
            "data": {
                "user_id": str,
                "initialized": bool,
                "group_memberships": Dict,
                "working_group": Dict,
                "eligible_experiments": List[str]  # Experiment IDs user is eligible for
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `get_user_assignments`

**Purpose**: Get experiment condition assignments for a user
**When to use**: When user visits decision points
**API Endpoint**: `POST /v6/assign`

```python
async def get_user_assignments(
    user_id: str,
    context: str,
    site_filter: Optional[str] = None,
    target_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get user's experiment condition assignments

    Args:
        user_id: User identifier (for header)
        context: App context
        site_filter: Optional site filter
        target_filter: Optional target filter

    Returns:
        {
            "success": bool,
            "data": {
                "assignments": List[{
                    "experiment_id": str,
                    "experiment_name": str,
                    "site": str,
                    "target": str,
                    "condition_code": str,
                    "condition_id": str,
                    "payload": Dict,
                    "experiment_type": str
                }],
                "assignment_count": int,
                "default_assignments": List[str],  # Decision points with no assignment
                "user_eligible": bool
            },
            "raw_response": List[Dict],
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `mark_decision_point_visit`

**Purpose**: Record that user visited decision point and received condition
**When to use**: After user gets assignment, to track enrollment
**API Endpoint**: `POST /v6/mark`

```python
async def mark_decision_point_visit(
    user_id: str,
    site: str,
    target: str,
    assigned_condition: Dict,
    status: str = "condition applied"
) -> Dict[str, Any]:
    """
    Mark that user visited decision point

    Args:
        user_id: User identifier (for header)
        site: Decision point site
        target: Decision point target
        assigned_condition: Condition data from /v6/assign
        status: "condition applied", "condition not applied", "no condition assigned"

    Returns:
        {
            "success": bool,
            "data": {
                "visit_recorded": bool,
                "visit_id": str,
                "user_id": str,
                "experiment_id": str,
                "condition_applied": str,
                "timestamp": str
            },
            "raw_response": Dict,
            "error": Optional[str],
            "error_type": Optional[str],
            "endpoint": str
        }
    """
```

### `simulate_user_journey`

**Purpose**: Complete user simulation (init + assign + mark) in one tool
**When to use**: For simple user visit simulations
**Combines**: `initialize_user` + `get_user_assignments` + `mark_decision_point_visit`

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
                "steps_completed": List[str],  # ["init", "assign", "mark"]
                "final_assignment": {
                    "condition_code": str,
                    "payload": Dict,
                    "experiment_id": str
                },
                "visit_recorded": bool
            },
            "error": Optional[str],
            "error_type": Optional[str],
            "failed_at_step": Optional[str]
        }
    """
```

---

## 5. Testing & Analysis Capabilities

### `test_condition_balance`

**Purpose**: Test condition distribution by enrolling multiple users
**When to use**: Verifying random assignment works correctly
**Combines**: Multiple `simulate_user_journey` calls

```python
async def test_condition_balance(
    experiment_id: str,
    num_users: int = 100,
    user_id_pattern: str = "test_user_{uuid}",
    group_settings: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Test condition balance by enrolling multiple users

    Args:
        experiment_id: Experiment to test
        num_users: Number of users to simulate (default 100)
        user_id_pattern: Pattern for user IDs ("{uuid}" will be replaced)
        group_settings: Optional group memberships for all users

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "experiment_name": str,
                "experiment_conditions": List[{
                    "condition_code": str,
                    "expected_weight": float,
                    "actual_count": int,
                    "actual_percentage": float,
                    "deviation": float
                }],
                "total_users_tested": int,
                "successful_enrollments": int,
                "condition_distribution": Dict[str, {  # Dynamic - matches actual conditions
                    "count": int,
                    "percentage": float,
                    "expected_percentage": float,
                    "deviation": float
                }],
                "balance_analysis": {
                    "is_balanced": bool,
                    "balance_threshold": float,  # e.g., 5% deviation acceptable
                    "max_deviation": float,  # Max deviation from expected percentage
                    "chi_square_p_value": Optional[float],
                    "conditions_within_threshold": List[str],
                    "conditions_outside_threshold": List[str]
                },
                "failed_enrollments": List[{"user_id": str, "error": str}],
                "default_condition_count": int,  # Users who got default (not enrolled)
                "test_duration_seconds": float
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

### `test_consistency_rules`

**Purpose**: Test assignment consistency across experiment phases
**When to use**: Verifying consistency rules work correctly
**Combines**: Multiple user simulations across status changes

```python
async def test_consistency_rules(
    experiment_id: str,
    test_users: List[str] = None,
    phases_to_test: List[str] = ["inactive", "enrolling", "enrollmentComplete"]
) -> Dict[str, Any]:
    """
    Test assignment consistency across experiment phases

    Args:
        experiment_id: Experiment to test
        test_users: List of user IDs to test (generates if None)
        phases_to_test: Which experiment phases to test

    Returns:
        {
            "success": bool,
            "data": {
                "experiment_id": str,
                "test_summary": {
                    "users_tested": int,
                    "phases_tested": List[str],
                    "consistency_verified": bool
                },
                "assignment_table": {
                    "headers": List[str],  # ["User", "Inactive", "Enrolling", "Complete"]
                    "rows": List[List[str]]  # User assignment data
                },
                "consistency_analysis": {
                    "individual_consistency": bool,
                    "group_consistency": bool,
                    "post_experiment_rule_applied": bool,
                    "violations": List[{"user_id": str, "issue": str}]
                },
                "behavior_verification": {
                    "assignment_unit_correct": bool,
                    "consistency_rule_correct": bool,
                    "post_rule_correct": bool
                }
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

### `generate_test_users`

**Purpose**: Generate test user data for simulations
**When to use**: Creating test data for balance/consistency testing

```python
async def generate_test_users(
    count: int,
    user_id_pattern: str = "test_user_{uuid}",
    group_distribution: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate test user data

    Args:
        count: Number of users to generate
        user_id_pattern: Pattern for user IDs
        group_distribution: Optional group membership distribution

    Returns:
        {
            "success": bool,
            "data": {
                "users": List[{
                    "user_id": str,
                    "group_memberships": Dict,
                    "working_group": Dict
                }],
                "count": int,
                "group_summary": Dict[str, int]  # Count by group
            },
            "error": Optional[str],
            "error_type": Optional[str]
        }
    """
```

---

## Error Handling Patterns

### Retry Logic

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

### Validation Helpers

```python
async def validate_experiment_config(config: Dict, context_metadata: Dict) -> List[str]:
    """Validate experiment configuration against context metadata"""
    errors = []

    context = config.get('context')

    # Validate context exists
    if context not in context_metadata:
        errors.append(f"Invalid context: {context}")
        return errors  # Can't validate further without valid context

    context_data = context_metadata[context]

    # Validate conditions
    context_conditions = context_data.get('CONDITIONS', [])
    for condition in config.get('conditions', []):
        condition_code = condition.get('conditionCode')
        if condition_code not in context_conditions:
            errors.append(f"Invalid condition '{condition_code}' for context '{context}'. Valid conditions: {context_conditions}")

    # Validate decision points (sites and targets)
    valid_sites = context_data.get('EXP_POINTS', [])  # Sites are EXP_POINTS
    valid_targets = context_data.get('EXP_IDS', [])   # Targets are EXP_IDS

    for decision_point in config.get('decision_points', []):
        site = decision_point.get('site')
        target = decision_point.get('target')

        if site and site not in valid_sites:
            errors.append(f"Invalid site '{site}' for context '{context}'. Valid sites: {valid_sites}")

        if target and target not in valid_targets:
            errors.append(f"Invalid target '{target}' for context '{context}'. Valid targets: {valid_targets}")

    # Validate group types (for group assignment and segments)
    valid_group_types = context_data.get('GROUP_TYPES', [])

    # Check assignment unit group type
    if config.get('assignment_unit') == 'group':
        group_type = config.get('group')  # This would be specified when creating group assignment
        if group_type and group_type not in valid_group_types:
            errors.append(f"Invalid group type '{group_type}' for context '{context}'. Valid group types: {valid_group_types}")

    # Check group memberships in segments
    for group_spec in config.get('inclusion_groups', []):
        group_type = group_spec.get('type')
        if group_type and group_type not in valid_group_types and group_type != "All":
            errors.append(f"Invalid inclusion group type '{group_type}' for context '{context}'. Valid group types: {valid_group_types}")

    for group_spec in config.get('exclusion_groups', []):
        group_type = group_spec.get('type')
        if group_type and group_type not in valid_group_types and group_type != "All":
            errors.append(f"Invalid exclusion group type '{group_type}' for context '{context}'. Valid group types: {valid_group_types}")

    # Validate assignment weights sum to 100%
    conditions = config.get('conditions', [])
    if conditions:
        total_weight = sum(condition.get('assignmentWeight', 0) for condition in conditions)
        if abs(total_weight - 100) > 0.01:  # Allow for small floating point errors
            errors.append(f"Condition assignment weights must sum to 100%, got {total_weight}%")

    # Validate unsupported experiment features
    if config.get('type') == 'Factorial':
        errors.append("Factorial experiments are not supported")

    if config.get('assignment_unit') == 'within-subjects':
        errors.append("Within-subjects experiments are not supported")

    assignment_algorithm = config.get('assignment_algorithm', '').lower()
    if assignment_algorithm in ['stratified_random_sampling', 'ts_configurable']:
        errors.append(f"Assignment algorithm '{assignment_algorithm}' is not supported")

    # Validate consistency rule matches assignment unit
    assignment_unit = config.get('assignment_unit')
    consistency_rule = config.get('consistency_rule')

    if assignment_unit == 'individual' and consistency_rule == 'group':
        errors.append("Cannot use group consistency rule with individual assignment unit")

    return errors

async def validate_user_groups(group_data: Dict, context: str, context_metadata: Dict) -> List[str]:
    """Validate user group memberships against context metadata"""
    errors = []

    if context not in context_metadata:
        errors.append(f"Invalid context: {context}")
        return errors

    valid_group_types = context_metadata[context].get('GROUP_TYPES', [])

    # Validate group memberships
    for group_type, group_ids in group_data.get('group', {}).items():
        if group_type not in valid_group_types:
            errors.append(f"Invalid group type '{group_type}' for context '{context}'. Valid group types: {valid_group_types}")

    # Validate working group
    for group_type, group_id in group_data.get('workingGroup', {}).items():
        if group_type not in valid_group_types:
            errors.append(f"Invalid working group type '{group_type}' for context '{context}'. Valid group types: {valid_group_types}")

    return errors

async def validate_decision_point(site: str, target: str, context: str, context_metadata: Dict) -> List[str]:
    """Validate a single decision point against context metadata"""
    errors = []

    if context not in context_metadata:
        errors.append(f"Invalid context: {context}")
        return errors

    context_data = context_metadata[context]
    valid_sites = context_data.get('EXP_POINTS', [])
    valid_targets = context_data.get('EXP_IDS', [])

    if site not in valid_sites:
        errors.append(f"Invalid site '{site}' for context '{context}'. Valid sites: {valid_sites}")

    if target not in valid_targets:
        errors.append(f"Invalid target '{target}' for context '{context}'. Valid targets: {valid_targets}")

    return errors
```

## Usage Patterns

### Basic Tool Usage in LangGraph

```python
from langgraph.prebuilt import ToolExecutor

# Tool execution
tools = [check_upgrade_health, get_all_experiments, create_experiment, ...]
tool_executor = ToolExecutor(tools)

# In graph node
def experiment_management_node(state: AgentState):
    if "list experiments" in state["user_input"].lower():
        result = tool_executor.invoke({"tool_name": "get_all_experiments"})
        # Process result and update state
    elif "create experiment" in state["user_input"].lower():
        # Extract parameters and call create_experiment
        pass
```

### State Management

```python
def update_state_with_tool_result(state: AgentState, tool_result: Dict) -> AgentState:
    """Helper to update state with tool results"""
    if tool_result["success"]:
        # Update relevant state fields
        if "experiments" in tool_result["data"]:
            state["all_experiments"] = tool_result["data"]["experiments"]
    else:
        state["last_error"] = tool_result["error"]
        state["retry_count"] += 1

    return state
```
