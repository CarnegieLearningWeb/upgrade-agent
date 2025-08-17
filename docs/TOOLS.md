# UpGradeAgent Tools Documentation

## Overview

UpGradeAgent uses a **node-based tool architecture** that aligns with the 5-node LangGraph structure. Each node has access to specific tools that match its responsibilities, enforcing architectural boundaries and maintaining clear separation of concerns.

## Architecture Principles

- **Node-specific tool access**: Each node only has access to tools appropriate for its function
- **Auto-storage pattern**: Gatherer tools automatically store results in `gathered_info` with predictable keys
- **State mutation control**: Only Information Gatherer can modify state (except execution_log)
- **Error propagation**: Automatic error handling with manual override capabilities
- **Type safety**: All tools use TypedDict for parameter validation

## Tool Organization

### 1. Conversation Analyzer Tools (`/tools/analyzer/`)

**Purpose**: Intent classification and conversation orchestration

**Available Tools**:

#### `analyze_user_request`
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

### 2. Information Gatherer Tools (`/tools/gatherer/`)

**Purpose**: Data collection, validation, and state management

#### API Functions (Store in Static Variables)

```python
from src.api.client import upgrade_api
from src.exceptions import APIError, AuthenticationError, ValidationError, ExperimentNotFoundError

@auto_store("upgrade_health")
async def check_upgrade_health() -> Dict[str, str]:
    """
    Check UpGrade service health and version information.
    
    Returns:
        Dict with keys: name, version, description
    """
    try:
        response = await upgrade_api.health_check()
        return {
            "name": response.name,
            "version": response.version, 
            "description": response.description
        }
    except APIError as e:
        if isinstance(e, ExperimentNotFoundError):
            add_error("not_found", f"Experiment {experiment_id} not found: {str(e)}")
        else:
            add_error("api", f"Failed to check UpGrade health: {str(e)}")
        raise
    except AuthenticationError as e:
        add_error("auth", f"Authentication failed: {str(e)}")
        raise
    except ValidationError as e:
        add_error("validation", f"Validation error: {str(e)}")
        raise
    except Exception as e:
        add_error("unknown", f"Unexpected error: {str(e)}")
        raise

@auto_store_static("context_metadata")
async def get_context_metadata() -> Dict[str, Dict[str, List[str]]]:
    """
    Get available app contexts and their supported values.
    
    Returns:
        Dict mapping context names to their metadata:
        {
            "assign-prog": {
                "conditions": ["control", "variant"],
                "group_types": ["schoolId", "classId", "instructorId"], 
                "sites": ["SelectSection"],
                "targets": ["absolute_value_plot_equality", "analyzing_step_functions"]
            }
        }
    """
    try:
        response = await upgrade_api.get_context_metadata()
        # Transform the API response to our simplified format
        context_data = {}
        for context_name, metadata in response.contextMetadata.items():
            context_data[context_name] = {
                "conditions": metadata.CONDITIONS,
                "group_types": metadata.GROUP_TYPES,
                "sites": metadata.EXP_POINTS,  # API calls them EXP_POINTS
                "targets": metadata.EXP_IDS    # API calls them EXP_IDS
            }
        return context_data
    except APIError as e:
        add_error("api", f"Failed to get context metadata: {str(e)}")
        raise
    except AuthenticationError as e:
        add_error("auth", f"Authentication failed: {str(e)}")
        raise
    except Exception as e:
        add_error("unknown", f"Unexpected error getting context metadata: {str(e)}")
        raise

@auto_store_static("experiment_names")
async def get_experiment_names() -> List[Dict[str, str]]:
    """
    Get all experiment names and IDs.
    
    Returns:
        List of dicts with keys: id, name
        [{"id": "uuid", "name": "My Experiment"}, ...]
    """
    try:
        response = await upgrade_api.get_experiment_names()
        return [{"id": exp.id, "name": exp.name} for exp in response]
    except APIError as e:
        add_error("api", f"Failed to get experiment names: {str(e)}")
        raise
    except AuthenticationError as e:
        add_error("auth", f"Authentication failed: {str(e)}")
        raise
    except Exception as e:
        add_error("unknown", f"Unexpected error getting experiment names: {str(e)}")
        raise

@auto_store_static("all_experiments")
async def get_all_experiments() -> List[Dict[str, Any]]:
    """
    Get all experiments with simplified format.
    
    Returns:
        List of experiment dicts with keys:
        created_at, updated_at, id, status, name, description, tags, context, 
        type, assignment_unit, group_type, consistency_rule, post_experiment_rule,
        decision_points, conditions, filter_mode, inclusion_users, inclusion_groups,
        exclusion_users, exclusion_groups
    """
    try:
        response = await upgrade_api.get_all_experiments()
        return [_transform_experiment_data(exp) for exp in response]
    except APIError as e:
        add_error("api", f"Failed to get experiments: {str(e)}")
        raise
    except AuthenticationError as e:
        add_error("auth", f"Authentication failed: {str(e)}")
        raise
    except Exception as e:
        add_error("unknown", f"Unexpected error getting experiments: {str(e)}")
        raise

@auto_store("experiment_details")
async def get_experiment_details(experiment_id: str) -> Dict[str, Any]:
    """
    Get detailed experiment configuration.
    
    Args:
        experiment_id: UUID of the experiment
        
    Returns:
        Experiment dict with same format as get_all_experiments elements
    """
    if not experiment_id or not experiment_id.strip():
        add_error("validation", "experiment_id is required and cannot be empty")
        raise ValueError("experiment_id is required")
        
    try:
        response = await upgrade_api.get_experiment_by_id(experiment_id)
        return _transform_experiment_data(response)
    except ExperimentNotFoundError as e:
        add_error("not_found", f"Experiment {experiment_id} not found: {str(e)}")
        raise
    except APIError as e:
        add_error("api", f"Failed to get experiment details for {experiment_id}: {str(e)}")
        raise
    except AuthenticationError as e:
        add_error("auth", f"Authentication failed: {str(e)}")
        raise
    except Exception as e:
        add_error("unknown", f"Unexpected error getting experiment {experiment_id}: {str(e)}")
        raise

def _transform_experiment_data(experiment: Experiment) -> Dict[str, Any]:
    """Transform raw Experiment object to simplified format."""
    # Extract decision points
    decision_points = []
    for partition in getattr(experiment, 'partitions', []):
        decision_points.append({
            "site": partition.site,
            "target": partition.target,
            "exclude_if_reached": getattr(partition, 'excludeIfReached', False)
        })
    
    # Extract conditions
    conditions = []
    for condition in getattr(experiment, 'conditions', []):
        conditions.append({
            "code": condition.conditionCode,
            "weight": condition.assignmentWeight
        })
    
    # Extract inclusion/exclusion data
    inclusion_users = []
    inclusion_groups = []
    exclusion_users = []
    exclusion_groups = []
    
    # Parse experimentSegmentInclusion
    if hasattr(experiment, 'experimentSegmentInclusion') and experiment.experimentSegmentInclusion:
        segment = experiment.experimentSegmentInclusion.segment
        inclusion_users = [user.userId for user in getattr(segment, 'individualForSegment', [])]
        inclusion_groups = [
            {"type": group.type, "group_id": group.groupId} 
            for group in getattr(segment, 'groupForSegment', [])
        ]
    
    # Parse experimentSegmentExclusion  
    if hasattr(experiment, 'experimentSegmentExclusion') and experiment.experimentSegmentExclusion:
        segment = experiment.experimentSegmentExclusion.segment
        exclusion_users = [user.userId for user in getattr(segment, 'individualForSegment', [])]
        exclusion_groups = [
            {"type": group.type, "group_id": group.groupId}
            for group in getattr(segment, 'groupForSegment', [])
        ]
    
    # Extract post experiment rule
    post_experiment_rule = {
        "rule": getattr(experiment, 'postExperimentRule', 'continue'),
        "condition_code": getattr(experiment, 'revertTo', None) or "None"
    }
    
    return {
        "created_at": experiment.createdAt,
        "updated_at": experiment.updatedAt, 
        "id": experiment.id,
        "status": experiment.state,
        "name": experiment.name,
        "description": getattr(experiment, 'description', ''),
        "tags": getattr(experiment, 'tags', []),
        "context": experiment.context[0] if experiment.context else None,  # Single context
        "type": getattr(experiment, 'type', 'Simple'),
        "assignment_unit": getattr(experiment, 'assignmentUnit', 'individual'),
        "group_type": getattr(experiment, 'group', None) or "None",
        "consistency_rule": getattr(experiment, 'consistencyRule', 'individual'),
        "post_experiment_rule": post_experiment_rule,
        "decision_points": decision_points,
        "conditions": conditions,
        "filter_mode": getattr(experiment, 'filterMode', 'excludeAll'),
        "inclusion_users": inclusion_users,
        "inclusion_groups": inclusion_groups,
        "exclusion_users": exclusion_users,
        "exclusion_groups": exclusion_groups
    }
```

#### Utility Functions (Auto-store in gathered_info)

```python
@auto_store("core_terms")
def get_core_terms() -> Dict[str, Any]:
    """Get basic A/B testing and UpGrade terminology"""
    return {
        "app_context": "Indicates where the experiment will run...",
        "unit_of_assignment": "Specifies the level at which conditions are assigned...",
        "consistency_rule": "Defines whether a unit's condition stays the same...",
        # ... comprehensive terminology definitions (TODO)
    }

@auto_store("assignment_terms") 
def get_assignment_terms() -> Dict[str, Any]:
    """Get assignment rules, consistency, and algorithm information"""
    return {
        "individual_assignment_individual_consistency": "Each user gets their own random condition...",
        "group_assignment_individual_consistency": "Users are assigned conditions based on group...",
        "group_assignment_group_consistency": "All users within the same group receive identical...",
        # ... detailed assignment behavior explanations (TODO)
    }

@auto_store("available_contexts")
def get_available_contexts() -> List[str]:
    """Get list of available context names"""
    # Extract context names from stored context_metadata
    if not hasattr(get_available_contexts, '_state_ref') or 'context_metadata' not in get_available_contexts._state_ref:
        raise RuntimeError("Context metadata not available. Call get_context_metadata() first.")
    
    context_metadata = get_available_contexts._state_ref['context_metadata']
    return list(context_metadata.keys())

@auto_store("create_experiment_schema")
def get_create_experiment_schema() -> Dict[str, Any]:
    """Get schema and validation rules for experiment creation"""
    return {
        "required_parameters": {
            "name": {
                "type": "str",
                "validation": "Must be unique across all experiments",
                "helper_tool": "get_experiment_names() to check existing names"
            },
            "context": {
                "type": "str", 
                "validation": "Must be from available contexts",
                "helper_tool": "get_available_contexts() to get valid options"
            },
            "decision_points": {
                "type": "List[Dict[str, Any]]",
                "format": [{"site": "str", "target": "str", "exclude_if_reached": "bool"}],
                "validation": "site and target must be valid for the chosen context",
                "helper_tool": "get_decision_points_for_context(context) for valid site/target pairs"
            },
            "conditions": {
                "type": "List[Dict[str, Any]]", 
                "format": [{"code": "str", "weight": "int"}],
                "validation": "codes must be valid for context, weights must sum to 100",
                "helper_tool": "get_conditions_for_context(context) for valid condition codes"
            }
        },
        "optional_parameters": {
            "description": {"type": "str", "default": ""},
            "tags": {"type": "List[str]", "default": []},
            "assignment_unit": {"type": "str", "default": "individual", "choices": ["individual", "group"]},
            "group_type": {
                "type": "str", 
                "default": "None",
                "validation": "Required when assignment_unit='group'",
                "helper_tool": "get_group_types_for_context(context) for valid group types"
            },
            "consistency_rule": {"type": "str", "default": "individual", "choices": ["individual", "group"]},
            "post_experiment_rule": {
                "type": "Dict[str, str]",
                "default": {"rule": "continue", "condition_code": "None"},
                "format": {"rule": "continue|assign", "condition_code": "None|condition_code"}
            },
            "filter_mode": {"type": "str", "default": "excludeAll", "choices": ["excludeAll", "includeAll"]},
            "inclusion_users": {"type": "List[str]", "default": []},
            "inclusion_groups": {
                "type": "List[Dict[str, str]]", 
                "default": [],
                "format": [{"type": "group_type", "group_id": "group_identifier"}]
            },
            "exclusion_users": {"type": "List[str]", "default": []},
            "exclusion_groups": {
                "type": "List[Dict[str, str]]",
                "default": [],
                "format": [{"type": "group_type", "group_id": "group_identifier"}]
            }
        },
        "validation_dependencies": {
            "group_type": "Required when assignment_unit='group', must be valid for chosen context",
            "consistency_rule": "Can only be 'group' when assignment_unit='group'",
            "condition_weights": "Must sum to exactly 100 across all conditions",
            "post_experiment_condition_code": "Must be valid condition code when rule='assign'"
        },
        "parameter_gathering_flow": [
            "1. Get context → call get_available_contexts()",
            "2. Get decision points → call get_decision_points_for_context(context)", 
            "3. Get conditions → call get_conditions_for_context(context)",
            "4. If assignment_unit='group' → call get_group_types_for_context(context)",
            "5. Validate all parameters before calling set_action_params()"
        ]
    }

@auto_store("update_experiment_schema")
def get_update_experiment_schema() -> Dict[str, Any]:
    """Get schema and validation rules for experiment updates"""
    return {
        "required_parameters": {
            "experiment_id": {
                "type": "str",
                "validation": "Must be valid experiment ID",
                "helper_tool": "get_experiment_names() to get valid experiment IDs"
            }
        },
        "optional_parameters": {
            "name": {
                "type": "str",
                "validation": "Must be unique across all experiments if provided",
                "helper_tool": "get_experiment_names() to check existing names"
            },
            "description": {"type": "str"},
            "tags": {"type": "List[str]"},
            "context": {
                "type": "str", 
                "validation": "Must be from available contexts if provided",
                "helper_tool": "get_available_contexts() to get valid options"
            },
            "decision_points": {
                "type": "List[Dict[str, Any]]",
                "format": [{"site": "str", "target": "str", "exclude_if_reached": "bool"}],
                "validation": "site and target must be valid for the chosen context",
                "helper_tool": "get_decision_points_for_context(context) for valid site/target pairs"
            },
            "conditions": {
                "type": "List[Dict[str, Any]]", 
                "format": [{"code": "str", "weight": "int"}],
                "validation": "codes must be valid for context, weights must sum to 100",
                "helper_tool": "get_conditions_for_context(context) for valid condition codes"
            },
            "assignment_unit": {"type": "str", "choices": ["individual", "group"]},
            "group_type": {
                "type": "str", 
                "validation": "Required when assignment_unit='group'",
                "helper_tool": "get_group_types_for_context(context) for valid group types"
            },
            "consistency_rule": {"type": "str", "choices": ["individual", "group"]},
            "post_experiment_rule": {
                "type": "Dict[str, str]",
                "format": {"rule": "continue|assign", "condition_code": "None|condition_code"}
            },
            "filter_mode": {"type": "str", "choices": ["excludeAll", "includeAll"]},
            "inclusion_users": {"type": "List[str]"},
            "inclusion_groups": {
                "type": "List[Dict[str, str]]", 
                "format": [{"type": "group_type", "group_id": "group_identifier"}]
            },
            "exclusion_users": {"type": "List[str]"},
            "exclusion_groups": {
                "type": "List[Dict[str, str]]",
                "format": [{"type": "group_type", "group_id": "group_identifier"}]
            }
        },
        "update_behavior": "PARTIAL UPDATE - Only provide fields that need to be changed. Current experiment settings will be preserved for unspecified fields.",
        "validation_dependencies": {
            "group_type": "Required when assignment_unit='group', must be valid for chosen context",
            "consistency_rule": "Can only be 'group' when assignment_unit='group'", 
            "condition_weights": "Must sum to exactly 100 across all conditions if conditions provided",
            "post_experiment_condition_code": "Must be valid condition code when rule='assign'"
        },
        "parameter_gathering_flow": [
            "1. Validate experiment exists → call get_experiment_details(experiment_id)",
            "2. Identify which parameters need updating based on user request", 
            "3. For context-dependent changes → call appropriate helper tools",
            "4. Only set parameters that are being changed in action_params",
            "5. Tool will automatically merge with existing experiment data"
        ]
    }

@auto_store("update_experiment_status_schema")
def get_update_experiment_status_schema() -> Dict[str, Any]:
    """Get schema for experiment status updates"""
    return {
        "required_parameters": {
            "experiment_id": {
                "type": "str",
                "validation": "Must be valid experiment ID",
                "helper_tool": "get_experiment_names() to get valid experiment IDs"
            },
            "status": {
                "type": "str",
                "validation": "Must be valid experiment status",
                "choices": ["inactive", "preview", "scheduled", "enrolling", "enrollmentComplete", "cancelled", "archived"],
                "common_transitions": {
                    "inactive": ["preview", "scheduled", "enrolling"],
                    "preview": ["inactive", "scheduled", "enrolling"],
                    "scheduled": ["inactive", "enrolling", "cancelled"],
                    "enrolling": ["enrollmentComplete", "cancelled"],
                    "enrollmentComplete": ["archived"],
                    "cancelled": ["archived"]
                }
            }
        },
        "optional_parameters": {},
        "validation_dependencies": {
            "experiment_existence": "Experiment must exist before status can be updated",
            "status_transition": "Some status transitions may not be allowed depending on current state"
        },
        "parameter_gathering_flow": [
            "1. Validate experiment exists → call get_experiment_names() or get_experiment_details()",
            "2. Validate status is valid → check against choices list",
            "3. Set experiment_id and status in action_params",
            "4. No confirmation needed for status updates (non-destructive)"
        ]
    }

@auto_store("delete_experiment_schema")
def get_delete_experiment_schema() -> Dict[str, Any]:
    """Get schema for experiment deletion"""
    return {
        "required_parameters": {
            "experiment_id": {
                "type": "str",
                "validation": "Must be valid experiment ID",
                "helper_tool": "get_experiment_names() to get valid experiment IDs"
            }
        },
        "optional_parameters": {},
        "validation_dependencies": {
            "experiment_existence": "Experiment must exist before deletion"
        },
        "parameter_gathering_flow": [
            "1. Validate experiment exists → call get_experiment_names() or get_experiment_details()",
            "2. Set experiment_id in action_params",
            "3. Confirmation will be handled automatically by Confirmation Handler"
        ]
    }

@auto_store("init_experiment_user_schema")
def get_init_experiment_user_schema() -> Dict[str, Any]:
    """Get schema for user initialization parameters"""
    return {
        "required_parameters": {
            "user_id": {
                "type": "str",
                "validation": "Must be unique user identifier"
            }
        },
        "optional_parameters": {
            "group": {
                "type": "Dict[str, List[str]]",
                "format": {"schoolId": ["school1"], "classId": ["class1"], "instructorId": ["instructor1"]},
                "validation": "group_types must be valid for the context",
                "helper_tool": "get_group_types_for_context(context) for valid group types"
            },
            "working_group": {
                "type": "Dict[str, str]", 
                "format": {"schoolId": "school1", "classId": "class1", "instructorId": "instructor1"},
                "validation": "group_types must be valid for the context",
                "helper_tool": "get_group_types_for_context(context) for valid group types"
            }
        },
        "validation_dependencies": {
            "group_types": "All group types in both 'group' and 'working_group' must be valid for the context",
            "working_group_subset": "working_group values should correspond to entries in group lists"
        },
        "parameter_gathering_flow": [
            "1. Get user_id from user request",
            "2. If group membership needed → call get_group_types_for_context(context) for validation",
            "3. Set parameters in action_params",
            "4. Note: user_id will be passed as header, other params as request body"
        ]
    }

@auto_store("get_decision_point_assignments_schema")
def get_get_decision_point_assignments_schema() -> Dict[str, Any]:
    """Get schema for decision point assignment requests"""
    return {
        "required_parameters": {
            "context": {
                "type": "str",
                "validation": "Must be from available contexts",
                "helper_tool": "get_available_contexts() to get valid options"
            }
        },
        "optional_parameters": {},
        "validation_dependencies": {
            "context_existence": "Context must exist in UpGrade system"
        },
        "parameter_gathering_flow": [
            "1. Get context from user request or experiment details",
            "2. Validate context → call get_available_contexts()",
            "3. Set context in action_params",
            "4. Note: user_id will be passed as header, context as request body"
        ]
    }

@auto_store("mark_decision_point_schema")
def get_mark_decision_point_schema() -> Dict[str, Any]:
    """Get schema for marking decision point visits"""
    return {
        "required_parameters": {
            "decision_point": {
                "type": "Dict[str, str]",
                "format": {"site": "site_name", "target": "target_name"},
                "validation": "No validation possible - use values from assignment response"
            },
            "assigned_condition": {
                "type": "Dict[str, str]",
                "format": {"condition_code": "variant", "experiment_id": "uuid"},
                "validation": "Should use assigned_condition object from get_decision_point_assignments response",
                "helper_tool": "get_experiment_names() to convert experiment name to ID if needed"
            }
        },
        "optional_parameters": {},
        "validation_dependencies": {
            "assignment_response": "assigned_condition should come from prior get_decision_point_assignments call",
            "experiment_id": "experiment_id must be valid if provided by name"
        },
        "parameter_gathering_flow": [
            "1. Get decision_point (site, target) from user request",
            "2. Get assigned_condition from prior assignment call or user specification",
            "3. If experiment specified by name → call get_experiment_names() to get ID",
            "4. Set parameters in action_params",
            "5. Note: user_id will be passed as header, decision_point and assigned_condition as request body"
        ]
    }

def get_conditions_for_context(context: str) -> List[str]:
    """Get available conditions for a specific context"""
    # Validate context parameter
    if not context or not context.strip():
        add_error("validation", "context is required and cannot be empty")
        raise ValidationError("context is required")
    
    # Check if context metadata is available
    if not hasattr(get_conditions_for_context, '_state_ref') or 'context_metadata' not in get_conditions_for_context._state_ref:
        add_error("gathering", "Context metadata not available. Call get_context_metadata() first.")
        raise RuntimeError("Context metadata not available")
    
    context_metadata = get_conditions_for_context._state_ref['context_metadata']
    
    # Validate context exists
    if context not in context_metadata:
        available_contexts = list(context_metadata.keys())
        add_error("validation", f"Context '{context}' not found. Available contexts: {available_contexts}")
        raise ValidationError(f"Invalid context: {context}")
    
    # Extract and store conditions
    conditions = context_metadata[context].get("conditions", [])
    
    # Auto-store with predictable key
    if "gathered_info" not in get_conditions_for_context._state_ref:
        get_conditions_for_context._state_ref["gathered_info"] = {}
    get_conditions_for_context._state_ref["gathered_info"][f"conditions_for_{context}"] = conditions
    
    return conditions

def get_decision_points_for_context(context: str) -> List[Dict[str, List[str]]]:
    """Get available decision points (sites/targets) for a specific context"""
    # Validate context parameter
    if not context or not context.strip():
        add_error("validation", "context is required and cannot be empty")
        raise ValidationError("context is required")
    
    # Check if context metadata is available
    if not hasattr(get_decision_points_for_context, '_state_ref') or 'context_metadata' not in get_decision_points_for_context._state_ref:
        add_error("gathering", "Context metadata not available. Call get_context_metadata() first.")
        raise RuntimeError("Context metadata not available")
    
    context_metadata = get_decision_points_for_context._state_ref['context_metadata']
    
    # Validate context exists
    if context not in context_metadata:
        available_contexts = list(context_metadata.keys())
        add_error("validation", f"Context '{context}' not found. Available contexts: {available_contexts}")
        raise ValidationError(f"Invalid context: {context}")
    
    # Extract sites and targets
    metadata = context_metadata[context]
    decision_points = {
        "sites": metadata.get("sites", []),
        "targets": metadata.get("targets", [])
    }
    
    # Auto-store with predictable key
    if "gathered_info" not in get_decision_points_for_context._state_ref:
        get_decision_points_for_context._state_ref["gathered_info"] = {}
    get_decision_points_for_context._state_ref["gathered_info"][f"decision_points_for_{context}"] = decision_points
    
    return decision_points

def get_group_types_for_context(context: str) -> List[str]:
    """Get available group types for a specific context"""
    # Validate context parameter
    if not context or not context.strip():
        add_error("validation", "context is required and cannot be empty")
        raise ValidationError("context is required")
    
    # Check if context metadata is available
    if not hasattr(get_group_types_for_context, '_state_ref') or 'context_metadata' not in get_group_types_for_context._state_ref:
        add_error("gathering", "Context metadata not available. Call get_context_metadata() first.")
        raise RuntimeError("Context metadata not available")
    
    context_metadata = get_group_types_for_context._state_ref['context_metadata']
    
    # Validate context exists
    if context not in context_metadata:
        available_contexts = list(context_metadata.keys())
        add_error("validation", f"Context '{context}' not found. Available contexts: {available_contexts}")
        raise ValidationError(f"Invalid context: {context}")
    
    # Extract and store group types
    group_types = context_metadata[context].get("group_types", [])
    
    # Auto-store with predictable key
    if "gathered_info" not in get_group_types_for_context._state_ref:
        get_group_types_for_context._state_ref["gathered_info"] = {}
    get_group_types_for_context._state_ref["gathered_info"][f"group_types_for_{context}"] = group_types
    
    return group_types
```

#### State Management Tools

```python
@tool
def set_action_needed(
    action: Literal[
        "create_experiment", "update_experiment", "delete_experiment",
        "update_experiment_status", "init_experiment_user", 
        "get_decision_point_assignments", "mark_decision_point"
    ],
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

#### Error Handling Tools

```python
@tool
def add_error(error_type: Literal["gathering", "validation"], message: str) -> str:
    """Add an error message when operations fail"""
```

### 3. Confirmation Handler (`/tools/confirmation/`)

**Purpose**: Generate safety confirmations for destructive actions

**Implementation**: Pure static logic, no tools required

```python
def confirmation_handler(state):
    """Generate confirmation messages based on action type"""
    # Static implementation - no tools needed
```

### 4. Tool Executor (`/tools/executor/`)

**Purpose**: Execute UpGrade API calls using prepared parameters

#### API Execution Tools

```python
def create_experiment(**params) -> Dict:
    """POST /experiments - Create new experiment"""

def update_experiment(experiment_id: str, **params) -> Dict:
    """PUT /experiments/<experiment_id> - Update experiment with partial parameters
    
    Automatically fetches current experiment data and merges with provided updates.
    Only specify parameters that need to be changed.
    """

def update_experiment_status(experiment_id: str, status: str) -> Dict:
    """POST /experiments/state - Update experiment status
    
    Args:
        experiment_id: UUID of the experiment to update
        status: New status for the experiment 
                (inactive, preview, scheduled, enrolling, enrollmentComplete, cancelled, archived)
    
    Returns:
        Updated experiment details with new status
    
    Note: Status transitions may have restrictions based on current experiment state.
    """

def delete_experiment(experiment_id: str) -> Dict:
    """DELETE /experiments/<experiment_id> - Delete experiment"""

def init_experiment_user(**params) -> Dict:
    """POST /v6/init - Initialize users with group memberships"""

def get_decision_point_assignments(**params) -> List[Dict]:
    """POST /v6/assign - Get experiment condition assignments for users"""

def mark_decision_point(**params) -> Dict:
    """POST /v6/mark - Record decision point visits"""
```

#### Utility Workflows

```python
def visit_decision_point(**params) -> Dict:
    """Compound workflow: init → assign → mark in sequence"""
```

### 5. Response Generator Tools (`/tools/response/`)

**Purpose**: Format responses and access state data for user communication

#### State Access Tools

```python
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

@tool
def get_all_gathered_info() -> Dict:
    """Get all gathered information (query-specific data)"""
    return state.get("gathered_info", {})

@tool
def get_execution_log() -> List[Dict[str, Any]]:
    """Get chronological log of all executed actions"""
    return state.get("execution_log", [])

@tool
def get_errors() -> Dict[str, str]:
    """Get any errors that occurred during processing"""
    return state.get("errors", {})
```

## Type Definitions

```python
# /tools/types.py
from typing import TypedDict, List, Optional, Literal, Dict, Any

class HealthCheckData(TypedDict):
    name: str
    version: str
    description: str

class ContextMetadata(TypedDict):
    conditions: List[str]
    group_types: List[str]
    sites: List[str]
    targets: List[str]

class ExperimentName(TypedDict):
    id: str
    name: str

class DecisionPoint(TypedDict):
    site: str
    target: str
    exclude_if_reached: bool

class Condition(TypedDict):
    code: str
    weight: int

class InclusionExclusionGroup(TypedDict):
    type: str
    group_id: str

class PostExperimentRule(TypedDict):
    rule: Literal["continue", "assign"]
    condition_code: str  # "None", "default", or condition_code

class SimplifiedExperiment(TypedDict):
    created_at: str
    updated_at: str
    id: str
    status: Literal["inactive", "preview", "scheduled", "enrolling", "enrollmentComplete", "cancelled", "archived"]
    name: str
    description: str
    tags: List[str]
    context: str
    type: Literal["Simple", "Factorial"]
    assignment_unit: Literal["individual", "group"]
    group_type: str  # "None" or actual group type like "schoolId"
    consistency_rule: Literal["individual", "group"]
    post_experiment_rule: PostExperimentRule
    decision_points: List[DecisionPoint]
    conditions: List[Condition]
    filter_mode: Literal["excludeAll", "includeAll"]
    inclusion_users: List[str]
    inclusion_groups: List[InclusionExclusionGroup]
    exclusion_users: List[str]
    exclusion_groups: List[InclusionExclusionGroup]

class ConditionConfig(TypedDict):
    id: str
    conditionCode: str
    assignmentWeight: int
    description: Optional[str]
    order: int
    name: str

class PartitionConfig(TypedDict):
    id: str
    site: str
    target: str
    description: str
    order: int
    excludeIfReached: bool

class CreateExperimentParams(TypedDict):
    name: str
    description: str
    context: List[str]
    conditions: List[ConditionConfig]
    partitions: List[PartitionConfig]
    # ... additional fields

class UpdateExperimentStatusParams(TypedDict):
    experimentId: str
    state: Literal["inactive", "preview", "scheduled", "enrolling", "enrollmentComplete", "cancelled", "archived"]

class InitUserParams(TypedDict):
    user_id: str
    group: Optional[Dict[str, List[str]]]
    workingGroup: Optional[Dict[str, str]]

class AssignmentParams(TypedDict):
    context: str

class DecisionPointData(TypedDict):
    site: str
    target: str

class AssignedConditionData(TypedDict):
    condition_code: str
    experiment_id: str

class MarkDecisionPointParams(TypedDict):
    decision_point: DecisionPointData
    assigned_condition: AssignedConditionData
```

## Decorators and Utilities

```python
# /tools/decorators.py
from functools import wraps
from typing import Callable, Optional, Any
import asyncio

def auto_store(key_pattern: Optional[str] = None):
    """Auto-store results in gathered_info with predictable keys"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            key = key_pattern or func.__name__.replace('get_', '')
            if not hasattr(async_wrapper, '_state_ref'):
                raise RuntimeError("State reference not set")
            if "gathered_info" not in async_wrapper._state_ref:
                async_wrapper._state_ref["gathered_info"] = {}
            async_wrapper._state_ref["gathered_info"][key] = result
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            key = key_pattern or func.__name__.replace('get_', '')
            if not hasattr(sync_wrapper, '_state_ref'):
                raise RuntimeError("State reference not set")
            if "gathered_info" not in sync_wrapper._state_ref:
                sync_wrapper._state_ref["gathered_info"] = {}
            sync_wrapper._state_ref["gathered_info"][key] = result
            return result
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def auto_store_static(storage_key: str):
    """Auto-store results in static state variables"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if not hasattr(async_wrapper, '_state_ref'):
                raise RuntimeError("State reference not set")
            async_wrapper._state_ref[storage_key] = result
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not hasattr(sync_wrapper, '_state_ref'):
                raise RuntimeError("State reference not set")
            sync_wrapper._state_ref[storage_key] = result
            return result
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def handle_errors(auto_add: bool = True, error_type: str = "gathering"):
    """Automatic error handling with manual override"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if auto_add:
                    # Import here to avoid circular imports
                    from .gatherer import add_error
                    add_error(error_type, str(e))
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if auto_add:
                    from .gatherer import add_error
                    add_error(error_type, str(e))
                raise
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def set_state_reference(tools: Dict[str, Callable], state: Dict[str, Any]):
    """Set state reference for all tools that use auto-storage decorators"""
    for tool_func in tools.values():
        if hasattr(tool_func, '__wrapped__'):  # Decorated function
            tool_func._state_ref = state
```

## Tool Registry

```python
# /tools/registry.py
from typing import Dict, List, Callable

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.node_permissions: Dict[str, List[str]] = {
            "analyzer": ["analyze_user_request"],
            "gatherer": [
                "check_upgrade_health", "get_context_metadata", "get_experiment_names",
                "get_all_experiments", "get_experiment_details", "get_core_terms",
                "get_assignment_terms", "get_*_schema", "get_*_for_context",
                "set_action_needed", "set_action_params", "set_missing_params", 
                "update_action_params", "add_error"
            ],
            "executor": [
                "create_experiment", "update_experiment", "delete_experiment",
                "update_experiment_status", "init_experiment_user", 
                "get_decision_point_assignments", "mark_decision_point"
            ],
            "response": [
                "get_context_metadata", "get_experiment_names", "get_all_experiments",
                "get_all_gathered_info", "get_execution_log", "get_errors"
            ]
        }
    
    def register_tool(self, name: str, func: Callable, nodes: List[str]):
        """Register a tool for specific nodes"""
        self.tools[name] = func
        for node in nodes:
            if node not in self.node_permissions:
                self.node_permissions[node] = []
            self.node_permissions[node].append(name)
    
    def get_tools_for_node(self, node_name: str) -> Dict[str, Callable]:
        """Get tools available for a specific node"""
        allowed_tools = self.node_permissions.get(node_name, [])
        return {name: func for name, func in self.tools.items() if name in allowed_tools}
    
    def validate_access(self, node_name: str, tool_name: str) -> bool:
        """Validate if a node can access a specific tool"""
        return tool_name in self.node_permissions.get(node_name, [])
```

## Error Handling Strategy

### Error Types
- **API errors** (`"api"`): API connectivity and response issues
- **Authentication errors** (`"auth"`): Invalid or missing tokens  
- **Validation errors** (`"validation"`): Invalid parameters or schema violations
- **Not found errors** (`"not_found"`): Requested resources don't exist
- **Unknown errors** (`"unknown"`): Unexpected exceptions

### Error Mapping
```python
# From your exceptions.py
APIError -> "api"
AuthenticationError -> "auth" 
ValidationError -> "validation"
ExperimentNotFoundError -> "not_found"
InvalidExperimentStateError -> "validation"
Unknown Exception -> "unknown"
```

### Error Propagation
```python
# Specific error handling per exception type
try:
    # API operation
    pass
except ExperimentNotFoundError as e:
    add_error("not_found", f"Experiment {id} not found: {str(e)}")
    raise
except AuthenticationError as e:
    add_error("auth", f"Authentication failed: {str(e)}")
    raise
except ValidationError as e:
    add_error("validation", f"Validation error: {str(e)}")
    raise
except APIError as e:
    add_error("api", f"API operation failed: {str(e)}")
    raise
except Exception as e:
    add_error("unknown", f"Unexpected error: {str(e)}")
    raise
```

## Implementation Notes

### Async Tool Pattern
All tools are async to match the underlying API client and provide optimal performance for I/O-bound operations:

```python
# ✅ Recommended pattern
@tool
async def get_experiment_details(experiment_id: str) -> Dict[str, Any]:
    """Async tool that naturally calls async API"""
    response = await upgrade_api.get_experiment_by_id(experiment_id)
    return _transform_experiment_data(response)

# ❌ Avoid sync wrappers  
@tool
def get_experiment_details_sync(experiment_id: str) -> Dict[str, Any]:
    """Problematic sync wrapper"""
    response = asyncio.run(upgrade_api.get_experiment_by_id(experiment_id))  # Can cause issues
    return _transform_experiment_data(response)
```

### LangGraph Async Tool Usage
```python
# LangGraph handles async tools automatically
from langgraph.prebuilt import ToolExecutor

# Tools can be async
async_tools = [get_experiment_details, get_context_metadata]
tool_executor = ToolExecutor(async_tools)
```

### Data Storage Patterns
- **Static variables**: Large, frequently referenced data (contexts, experiment lists)
- **gathered_info**: Small, query-specific data with predictable keys
- **execution_log**: Chronological record of all actions taken
- **Auto-storage**: Tools automatically store results for later access

### Security Considerations
- All destructive operations require explicit confirmation
- Parameter validation prevents malformed API calls
- Error messages help users understand issues without exposing internals
- Authentication tokens managed through environment variables

### Performance Optimization
- Response Generator only accesses large data when needed
- gathered_info contains relevant data for most responses
- Auto-storage prevents redundant API calls within sessions
- Confirmation Handler and Tool Executor use static logic for speed

## Testing Strategy

```python
# /tests/tools/test_gatherer.py
def test_get_core_terms():
    result = get_core_terms()
    assert "gathered_info" in state
    assert "core_terms" in state["gathered_info"]

# /tests/tools/test_executor.py  
def test_create_experiment():
    params = {"name": "Test", "context": ["assign-prog"]}
    result = create_experiment(**params)
    assert result["id"] is not None

def test_update_experiment_status():
    params = {"experiment_id": "test-id", "status": "enrolling"}
    result = update_experiment_status(**params)
    assert result["state"] == "enrolling"

# /tests/tools/test_registry.py
def test_node_tool_access():
    registry = ToolRegistry()
    analyzer_tools = registry.get_tools_for_node("analyzer")
    assert "analyze_user_request" in analyzer_tools
    assert "create_experiment" not in analyzer_tools
```
