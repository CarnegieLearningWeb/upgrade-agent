"""
TypedDict classes for UpGradeAgent tools.

This module defines types specifically used by the LangGraph tools, which are
simplified, user-friendly representations of UpGrade concepts. These differ from
the raw API types in types.py as they focus on tool functionality rather than
direct API request/response mapping.

Tool types are organized by their usage:
- Simplified API Response Types: User-friendly versions of API responses
- Tool-Specific Domain Types: Tool-specific representations of UpGrade concepts
- Tool Workflow Types: Types for multi-step tool workflows
"""

from typing import Dict, List, Optional, Any, TypedDict, Literal
from .enums import (
    PostExperimentRule as PostExperimentRuleEnum,
    ExperimentState,
    ExperimentType,
    AssignmentUnit,
    ConsistencyRule,
    FilterMode,
    ToolActionType as ToolActionTypeEnum,
    ToolErrorType as ToolErrorTypeEnum,
    NodeType as NodeTypeEnum
)
from .types import HealthResponse, ExperimentName


# ============================================================================
# Simplified API Response Types
# ============================================================================

# Reuse identical types from types.py
ToolHealthResponse = HealthResponse
"""Alias for HealthResponse - tool and API types are identical."""

ToolExperimentName = ExperimentName
"""Alias for ExperimentName - tool and API types are identical."""


# Tool-specific types where structure differs from API
class ToolContextMetadata(TypedDict):
    """Context metadata for tools (different structure from API).
    
    Note: This differs from ContextMetadata in types.py:
    - API uses UPPERCASE keys: CONDITIONS, GROUP_TYPES, EXP_IDS, EXP_POINTS
    - Tools use lowercase, semantic keys: conditions, group_types, sites, targets
    """
    conditions: List[str]
    group_types: List[str]
    sites: List[str]  
    targets: List[str]


# ============================================================================
# Tool-Specific Domain Types  
# ============================================================================

class DecisionPoint(TypedDict):
    """Tool representation of experiment decision points."""
    site: str
    target: str
    exclude_if_reached: bool


class Condition(TypedDict):
    """Tool representation of experiment conditions."""
    code: str
    weight: int


class InclusionExclusionGroup(TypedDict):
    """Tool representation of inclusion/exclusion groups."""
    type: str
    group_id: str


class ToolPostExperimentRule(TypedDict):
    """Tool representation of post-experiment rules."""
    rule: PostExperimentRuleEnum
    condition_code: Optional[str]  # None, or actual condition_code


class SimplifiedExperiment(TypedDict):
    """Simplified experiment representation for tool responses.
    
    This is a user-friendly view of experiments that focuses on the most
    important information for tool interactions, unlike the comprehensive
    Experiment type in types.py.
    """
    created_at: str
    updated_at: str
    id: str
    status: ExperimentState
    name: str
    description: str
    tags: List[str]
    context: str
    type: ExperimentType
    assignment_unit: AssignmentUnit
    group_type: str  # "None" or actual group type like "schoolId"
    consistency_rule: ConsistencyRule
    post_experiment_rule: ToolPostExperimentRule
    decision_points: List[DecisionPoint]
    conditions: List[Condition]
    filter_mode: FilterMode
    inclusion_users: List[str]
    inclusion_groups: List[InclusionExclusionGroup]
    exclusion_users: List[str]
    exclusion_groups: List[InclusionExclusionGroup]


# ============================================================================
# Tool Workflow Types
# ============================================================================

class DecisionPointData(TypedDict):
    """Decision point data for workflow tools."""
    site: str
    target: str


class AssignedConditionData(TypedDict):
    """Assigned condition data for workflow tools."""
    condition_code: str
    experiment_id: str


# ============================================================================
# Tool State Management Types
# ============================================================================

class ToolActionType(TypedDict):
    """Supported tool action types."""
    action: ToolActionTypeEnum


class ToolErrorType(TypedDict):
    """Tool error classification."""
    error_type: ToolErrorTypeEnum
    message: str


# ============================================================================ 
# Tool Response Types
# ============================================================================

class ToolExecutionResult(TypedDict):
    """Result from tool execution."""
    success: bool
    timestamp: str
    action: str
    data: Optional[Dict[str, Any]]
    error: Optional[ToolErrorType]


class GatheredInfo(TypedDict, total=False):
    """Structure for gathered_info state storage.
    
    This defines the predictable keys used by auto-storage decorators.
    All fields are optional since different tools store different information.
    """
    # Core information
    core_terms: Dict[str, Any]
    assignment_terms: Dict[str, Any]
    available_contexts: List[str]
    
    # Schema information  
    create_experiment_schema: Dict[str, Any]
    update_experiment_schema: Dict[str, Any]
    update_experiment_status_schema: Dict[str, Any]
    delete_experiment_schema: Dict[str, Any]
    init_experiment_user_schema: Dict[str, Any]
    get_decision_point_assignments_schema: Dict[str, Any]
    mark_decision_point_schema: Dict[str, Any]
    
    # Context-specific information (dynamic keys like "conditions_for_assign-prog")
    # These will be stored with pattern: f"{info_type}_for_{context}"
    
    # Health and experiment details
    upgrade_health: ToolHealthResponse
    experiment_details: Dict[str, Any]


# ============================================================================
# Tool Registry and Node Organization Types
# ============================================================================

class NodeType(TypedDict):
    """Supported node types in the LangGraph architecture."""
    node: NodeTypeEnum


class StateManagementActionParams(TypedDict):
    """Parameters for state management tools in Information Gatherer."""
    action_needed: Optional[str]
    action_params: Optional[Dict[str, Any]]
    missing_params: Optional[List[str]]


class ContextSpecificInfo(TypedDict):
    """Types for context-specific information gathering."""
    conditions: List[str]
    decision_points: List[Dict[str, Any]]
    group_types: List[str]
