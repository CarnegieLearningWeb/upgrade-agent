"""
Information Gatherer utility tools.

These tools provide schema information, documentation, and static data
that help guide parameter collection and user interactions.
"""

from langchain.tools import tool
from typing import Dict, Any, List

from src.tools.decorators import auto_store
from src.tools.registry import register_gatherer_tool
from src.api.endpoints import get_context_metadata as api_get_context_metadata


@tool
@register_gatherer_tool("get_core_terms")
@auto_store("core_terms")
def get_core_terms() -> Dict[str, Any]:
    """Get comprehensive A/B testing and UpGrade terminology with definitions and options."""
    return {
        "app_context": {
            "definition": "Indicates where the experiment will run, known to UpGrade. In general, this is the name of the client application.",
            "notes": "Available options are read from the context metadata."
        },
        "unit_of_assignment": {
            "definition": "Specifies the level at which conditions are assigned when the experiment is running ('Enrolling' status).",
            "options": {
                "individual": "Condition will be assigned individually.",
                "group": "Condition will be assigned by group (e.g., school, class, teacher). Requires specifying the Group Type.",
                "within_subjects": "Condition will be assigned within subjects (NOT SUPPORTED in MVP)"
            }
        },
        "consistency_rule": {
            "definition": "Defines whether a unit's condition stays the same during the experiment's Enrolling phase.",
            "options": {
                "individual": "Individual students have a consistent experience.",
                "group": "All students in a group have a common experience (only available when Group Unit of Assignment is selected)."
            },
            "notes": "Determined based on the user's 'workingGroup' membership when the /v6/init request is made."
        },
        "post_experiment_rule": {
            "definition": "Specifies what happens to participants' conditions after the experiment ends (when status changes from 'Enrolling' to 'Enrollment Complete').",
            "options": {
                "continue": "Students will remain in their current assigned conditions without any changes.",
                "assign": "All students will receive the same specified condition moving forward.",
                "assign_default": "Everyone gets the default condition (same as Inactive status)",
                "assign_specific": "Everyone gets assigned to one of the defined conditions (e.g., 'condition-a')"
            }
        },
        "design_type": {
            "definition": "Specifies how conditions are structured in the experiment.",
            "options": {
                "simple_experiment": "Conditions are independent (SUPPORTED in MVP).",
                "factorial_experiment": "Conditions vary on two or more dimensions (NOT SUPPORTED in MVP)"
            }
        },
        "assignment_algorithm": {
            "definition": "Determines how participants are assigned to conditions.",
            "options": {
                "random": "Each participant has an equal chance of being assigned to any condition (SUPPORTED in MVP).",
                "stratified_random_sampling": "Random assignment within balanced subgroups to ensure representation (NOT SUPPORTED in MVP)",
                "ts_configurable": "Uses the TS Configurable algorithm to adaptively assign conditions based on reward metrics (NOT SUPPORTED in MVP)"
            }
        },
        "decision_point": {
            "definition": "A location in your application where an experiment condition needs to be determined.",
            "components": {
                "site": "A category of locations within the app (e.g., a function name, a page)",
                "target": "A specific element within that category (e.g., a hint button, specific content, a problem ID)"
            },
            "example": "If a math exercise page is the site, the targets could be the hint button, the problem difficulty, or the timer display.",
            "notes": "Available options for both site and target are read from the context metadata."
        },
        "exclude_if_reached": {
            "definition": "Determines whether users who visit the decision point during the inactive phase should be permanently excluded from the experiment.",
            "behavior": {
                "enabled": "Users are excluded and continue receiving the default condition.",
                "disabled": "Users can still be enrolled and receive experimental conditions when the experiment starts (default behavior)."
            }
        },
        "condition": {
            "definition": "A specific experimental treatment or variation that a user can be assigned to within an experiment.",
            "properties": {
                "code": "A unique identifier for the condition (e.g., 'control', 'variant')",
                "weight": "The percentage chance a user has of being assigned to this condition (must sum to 100% across all conditions)"
            }
        },
        "payload": {
            "definition": "The actual data or configuration that gets delivered to the client application when a user is assigned to a specific condition at a decision point.",
            "notes": "Each condition can have different payloads for different decision points (NOT SUPPORTED in MVP)"
        },
        "segment": {
            "definition": "A way to include or exclude specific users or groups from an experiment.",
            "components": {
                "inclusion_users_groups": "Defines who is eligible to participate in the experiment",
                "exclusion_users_groups": "Defines who should be prevented from participating in the experiment"
            },
            "filter_modes": {
                "excludeAll": "Users/groups in the inclusion can participate except those in the exclusion",
                "includeAll": "All users can participate except those in the exclusion (inclusion will be ignored)"
            },
            "notes": "Determined based on the user's 'group' membership (not 'workingGroup') when the /v6/init request is made. Exclusion precedes inclusion."
        },
        "experiment_status": {
            "definition": "The current operational phase of an experiment.",
            "statuses": {
                "inactive": "Default condition is served to all users; no experimental conditions are distributed",
                "preview": "Preview condition assignments with test users (NOT SUPPORTED in MVP)",
                "scheduled": "Same as Inactive but scheduled to start on specified date (NOT SUPPORTED in MVP)",
                "enrolling": "Experiment is actively running; included users are assigned experimental conditions based on assignment rules",
                "enrollment_complete": "Experiment has ended; Post Experiment Rule determines what conditions users receive",
                "cancelled": "Experiment has been cancelled for some reason (NOT SUPPORTED in MVP)"
            }
        }
    }


@tool
@register_gatherer_tool("get_assignment_terms")
@auto_store("assignment_terms")
def get_assignment_terms() -> Dict[str, Any]:
    """Get comprehensive assignment behavior rules, consistency patterns, and interaction examples."""
    return {
        "assignment_combinations": {
            "individual_assignment_individual_consistency": {
                "behavior": "Each user gets their own random condition assignment",
                "during_enrolling": "Users maintain their assigned condition consistently",
                "post_experiment": "Follows the Post Experiment Rule (Continue or Assign to specific condition)",
                "example": "In a class of 5 students, each might get different conditions (A, B, C, etc.) and stick with them",
                "use_case": "Best for individual-level interventions where each student needs independent treatment"
            },
            "group_assignment_individual_consistency": {
                "behavior": "Users are assigned conditions based on their group membership, but individuals can have different conditions within the experiment",
                "during_enrolling": "Each individual maintains their own assigned condition",
                "post_experiment": "Follows the Post Experiment Rule (Continue or Assign to specific condition)",
                "example": "Students from the same school might get assigned to the same condition initially, but once assigned, each student maintains their individual condition",
                "use_case": "Useful when you want group-based initial assignment but individual consistency thereafter"
            },
            "group_assignment_group_consistency": {
                "behavior": "All users within the same group receive identical conditions",
                "during_enrolling": "All group members share the same condition and change together",
                "post_experiment": "Follows the Post Experiment Rule (Continue or Assign to specific condition)",
                "example": "All students in 'Group A' get Condition A, all students in 'Group B' get Condition B, and they all transition together",
                "use_case": "Ideal for interventions where group cohesion is important (e.g., classroom-level treatments)"
            }
        },
        "experiment_status_impact": {
            "inactive": {
                "behavior": "All users receive the default condition regardless of assignment rules",
                "assignment_rules": "No experimental conditions are distributed",
                "exclude_if_reached_effect": "Users who visit may be excluded from future experimental conditions if 'Exclude If Reached' is enabled"
            },
            "enrolling": {
                "behavior": "Assignment and consistency rules are actively applied",
                "assignment_rules": "Users receive experimental conditions based on the configured rules",
                "exclude_if_reached_effect": "Previously excluded users continue getting default condition"
            },
            "enrollment_complete": {
                "behavior": "Post Experiment Rule takes effect",
                "assignment_rules": {
                    "continue": "Users keep their last assigned experimental condition",
                    "assign": "All users switch to a specified condition (default or specific condition)"
                },
                "exclude_if_reached_effect": "Excluded users remain on default condition unless Post Rule overrides"
            }
        },
        "exclude_if_reached_behavior": {
            "disabled": {
                "description": "Default behavior - users who visit during Inactive can still participate",
                "impact": "Users who visit during Inactive can still be enrolled and receive experimental conditions when the experiment starts",
                "recommended_for": "Most experiments where you want maximum participation"
            },
            "enabled": {
                "description": "Strict exclusion - users who visit during Inactive are permanently excluded",
                "impact": "Users who visit during Inactive are permanently excluded from the experiment",
                "group_consistency_effect": "With Group Consistency, one excluded user can affect the entire group's assignment",
                "recommended_for": "Experiments where contamination from pre-exposure must be avoided"
            }
        },
        "key_behavioral_patterns": {
            "consistency_determination": {
                "individual_consistency": "Based on individual user identity and assignment",
                "group_consistency": "Based on user's 'workingGroup' membership when /v6/init request is made",
                "timing": "Consistency rule is applied throughout the entire experiment duration"
            },
            "group_membership_types": {
                "group": "Used for segment inclusion/exclusion determination during /v6/init",
                "workingGroup": "Used for consistency rule determination and group assignment logic",
                "precedence": "Exclusion precedes inclusion when both are specified"
            },
            "late_arrivals": {
                "individual_consistency": "New users get fresh random assignments",
                "group_consistency": "New users get the same condition as their existing group members",
                "enrollment_complete": "Follow Post Experiment Rule regardless of when they arrive"
            }
        },
        "testing_verification_patterns": {
            "what_to_verify": [
                "Each student gets expected condition type based on assignment rules",
                "Students maintain consistency according to consistency rule",
                "Post-experiment behavior follows configured Post Experiment Rule",
                "Exclude If Reached behavior works correctly for pre-exposed users",
                "Group consistency affects all group members uniformly"
            ],
            "test_scenarios": {
                "basic_flow": "Students visit during different experiment phases",
                "exclusion_testing": "Some students visit during Inactive phase with Exclude If Reached enabled",
                "group_consistency": "Multiple students from same group visit at different times",
                "late_arrivals": "Students who don't visit during Enrolling phase"
            }
        },
        "common_patterns": {
            "classroom_experiments": {
                "recommended": "Group Assignment + Group Consistency",
                "reason": "Maintains classroom unity and prevents within-class contamination"
            },
            "individual_interventions": {
                "recommended": "Individual Assignment + Individual Consistency",
                "reason": "Maximizes statistical power and individual-level effects"
            },
            "pilot_testing": {
                "recommended": "Individual Assignment + Individual Consistency with Exclude If Reached disabled",
                "reason": "Allows maximum participation and easier debugging"
            }
        }
    }


@tool
@register_gatherer_tool("get_create_experiment_schema")
@auto_store("create_experiment_schema")
def get_create_experiment_schema() -> Dict[str, Any]:
    """Get schema and validation rules for experiment creation."""
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


@tool
@register_gatherer_tool("get_update_experiment_schema")
@auto_store("update_experiment_schema")
def get_update_experiment_schema() -> Dict[str, Any]:
    """Get schema and validation rules for experiment updates."""
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


@tool
@register_gatherer_tool("get_update_experiment_status_schema")
@auto_store("update_experiment_status_schema")
def get_update_experiment_status_schema() -> Dict[str, Any]:
    """Get schema for experiment status updates."""
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


@tool
@register_gatherer_tool("get_delete_experiment_schema")
@auto_store("delete_experiment_schema")
def get_delete_experiment_schema() -> Dict[str, Any]:
    """Get schema for experiment deletion."""
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


@tool
@register_gatherer_tool("get_init_experiment_user_schema")
@auto_store("init_experiment_user_schema")
def get_init_experiment_user_schema() -> Dict[str, Any]:
    """Get schema for init_experiment_user (Makes /init request) tool parameters."""
    return {
        "required_parameters": {
            "user_id": {
                "type": "str"
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
            "3. Set parameters in action_params"
        ]
    }


@tool
@register_gatherer_tool("get_get_decision_point_assignments_schema")
@auto_store("get_decision_point_assignments_schema")
def get_get_decision_point_assignments_schema() -> Dict[str, Any]:
    """Get schema for get_decision_point_assignments (Makes /assign request) tool parameters."""
    return {
        "required_parameters": {
            "user_id": {
                "type": "str"
            },
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
            "1. Get user_id from user request",
            "2. Get context from user request or experiment details",
            "3. Validate context → call get_available_contexts()",
            "4. Set parameters in action_params"
        ]
    }


@tool
@register_gatherer_tool("get_mark_decision_point_schema")
@auto_store("mark_decision_point_schema")
def get_mark_decision_point_schema() -> Dict[str, Any]:
    """Get schema for mark_decision_point tool (Makes /mark request) parameters."""
    return {
        "required_parameters": {
            "user_id": {
                "type": "str"
            },
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
            "1. Get user_id from user request",
            "2. Get decision_point (site, target) from user request",
            "3. Get assigned_condition from prior assignment call or user specification",
            "4. If experiment specified by name → call get_experiment_names() to get ID",
            "5. Set parameters in action_params"
        ]
    }


@tool
@register_gatherer_tool("get_available_contexts")
@auto_store("available_contexts")
async def get_available_contexts() -> List[str]:
    """Get list of available context names."""
    try:
        response = await api_get_context_metadata()
        context_metadata = response.get("contextMetadata", {})
        return list(context_metadata.keys())
    except Exception as e:
        raise RuntimeError(f"Failed to get available contexts: {str(e)}")


@tool
@register_gatherer_tool("get_conditions_for_context")
async def get_conditions_for_context(context: str) -> List[str]:
    """Get available conditions for a specific context."""
    if not context or not context.strip():
        raise ValueError("context is required and cannot be empty")
    
    try:
        response = await api_get_context_metadata()
        context_metadata = response.get("contextMetadata", {})
        
        # Validate context exists
        if context not in context_metadata:
            available_contexts = list(context_metadata.keys())
            raise ValueError(f"Context '{context}' not found. Available contexts: {available_contexts}")
        
        context_data = context_metadata.get(context, {})
        conditions = context_data.get('CONDITIONS', [])  # API uses uppercase keys
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to get conditions for context '{context}': {str(e)}")
    
    # Auto-store with dynamic key
    from src.tools.decorators import _state_ref
    if _state_ref:
        if "gathered_info" not in _state_ref:
            _state_ref["gathered_info"] = {}
        _state_ref["gathered_info"][f"conditions_for_{context}"] = conditions
    
    return conditions


@tool
@register_gatherer_tool("get_decision_points_for_context")
async def get_decision_points_for_context(context: str) -> List[Dict[str, str]]:
    """Get available decision points (sites/targets) for a specific context."""
    if not context or not context.strip():
        raise ValueError("context is required and cannot be empty")
    
    try:
        response = await api_get_context_metadata()
        context_metadata = response.get("contextMetadata", {})
        
        # Validate context exists
        if context not in context_metadata:
            available_contexts = list(context_metadata.keys())
            raise ValueError(f"Context '{context}' not found. Available contexts: {available_contexts}")
            
        context_data = context_metadata.get(context, {})
        sites = context_data.get('EXP_POINTS', [])    # API uses EXP_POINTS for sites
        targets = context_data.get('EXP_IDS', [])     # API uses EXP_IDS for targets
        
        # Combine sites and targets into decision points
        decision_points = []
        for site in sites:
            for target in targets:
                decision_points.append({"site": site, "target": target})
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to get decision points for context '{context}': {str(e)}")
    
    # Auto-store with dynamic key
    from src.tools.decorators import _state_ref
    if _state_ref:
        if "gathered_info" not in _state_ref:
            _state_ref["gathered_info"] = {}
        _state_ref["gathered_info"][f"decision_points_for_{context}"] = decision_points
    
    return decision_points


@tool
@register_gatherer_tool("get_group_types_for_context")
async def get_group_types_for_context(context: str) -> List[str]:
    """Get available group types for a specific context."""
    if not context or not context.strip():
        raise ValueError("context is required and cannot be empty")
    
    try:
        response = await api_get_context_metadata()
        context_metadata = response.get("contextMetadata", {})
        
        # Validate context exists
        if context not in context_metadata:
            available_contexts = list(context_metadata.keys())
            raise ValueError(f"Context '{context}' not found. Available contexts: {available_contexts}")
            
        context_data = context_metadata.get(context, {})
        group_types = context_data.get('GROUP_TYPES', [])  # API uses uppercase keys
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to get group types for context '{context}': {str(e)}")
    
    # Auto-store with dynamic key
    from src.tools.decorators import _state_ref
    if _state_ref:
        if "gathered_info" not in _state_ref:
            _state_ref["gathered_info"] = {}
        _state_ref["gathered_info"][f"group_types_for_{context}"] = group_types
    
    return group_types
