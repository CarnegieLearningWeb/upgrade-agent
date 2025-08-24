"""
Enumeration types for the UpGrade API endpoints.

This module defines essential enum types needed for system and experiments 
endpoints based on actual API examples and TypeScript reference.
"""

from enum import Enum


class ExperimentState(str, Enum):
    """Possible states of an experiment."""
    INACTIVE = "inactive"
    PREVIEW = "preview"
    SCHEDULED = "scheduled"
    ENROLLING = "enrolling"
    ENROLLMENT_COMPLETE = "enrollmentComplete"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    DRAFT = "draft"


class ConsistencyRule(str, Enum):
    """Rules for maintaining assignment consistency."""
    INDIVIDUAL = "individual"
    EXPERIMENT = "experiment"
    GROUP = "group"


class AssignmentUnit(str, Enum):
    """Units for participant assignment."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    WITHIN_SUBJECTS = "within-subjects"


class PostExperimentRule(str, Enum):
    """Rules for post-experiment behavior."""
    CONTINUE = "continue"
    REVERT = "revert"
    ASSIGN = "assign"


class AssignmentAlgorithm(str, Enum):
    """Algorithms for assigning participants to conditions."""
    RANDOM = "random"
    STRATIFIED_RANDOM_SAMPLING = "stratified random sampling"
    MOOCLET_TS_CONFIGURABLE = "ts_configurable"


class ExperimentType(str, Enum):
    """Types of experiments supported."""
    SIMPLE = "Simple"
    FACTORIAL = "Factorial"


class FilterMode(str, Enum):
    """Filtering modes for experiments."""
    INCLUDE_ALL = "includeAll"
    EXCLUDE_ALL = "excludeAll"


class PayloadType(str, Enum):
    """Types of payloads that can be attached to conditions."""
    STRING = "string"
    JSON = "json"
    CSV = "csv"


class ConditionOrder(str, Enum):
    """Order for condition assignment."""
    RANDOM = "random"
    RANDOM_ROUND_ROBIN = "random round robin"
    ORDERED_ROUND_ROBIN = "ordered round robin"


class RepeatedMeasure(str, Enum):
    """Repeated measure options for queries."""
    MEAN = "MEAN"
    EARLIEST = "EARLIEST"
    MOST_RECENT = "MOST RECENT"
    COUNT = "COUNT"
    PERCENTAGE = "PERCENTAGE"


class SegmentType(str, Enum):
    """Types of segments."""
    PUBLIC = "public"
    PRIVATE = "private"
    GLOBAL_EXCLUDE = "global_exclude"


class MetricType(str, Enum):
    """Types of metrics."""
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"


class OperationType(str, Enum):
    """Operation types for queries."""
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    AVERAGE = "avg"
    MODE = "mode"
    MEDIAN = "median"
    STDEV = "stddev"
    PERCENTAGE = "percentage"


class MarkedDecisionPointStatus(str, Enum):
    """Status for marked decision points."""
    CONDITION_APPLIED = "condition applied"
    CONDITION_FAILED_TO_APPLY = "condition not applied"
    NO_CONDITION_ASSIGNED = "no condition assigned"


class ToolActionType(str, Enum):
    """Types of actions that can be executed by the Tool Executor."""
    CREATE_EXPERIMENT = "create_experiment"
    UPDATE_EXPERIMENT = "update_experiment"
    UPDATE_EXPERIMENT_STATUS = "update_experiment_status"
    DELETE_EXPERIMENT = "delete_experiment"
    INIT_EXPERIMENT_USER = "init_experiment_user"
    GET_DECISION_POINT_ASSIGNMENTS = "get_decision_point_assignments"
    MARK_DECISION_POINT = "mark_decision_point"
    VISIT_DECISION_POINT = "visit_decision_point"


class ToolErrorType(str, Enum):
    """Types of errors that can occur in tool execution."""
    API = "api"
    AUTH = "auth"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"
    GATHERING = "gathering"


class NodeType(str, Enum):
    """Node types in the LangGraph architecture."""
    CONVERSATION_ANALYZER = "conversation_analyzer"
    INFORMATION_GATHERER = "information_gatherer"
    CONFIRMATION_HANDLER = "confirmation_handler"
    TOOL_EXECUTOR = "tool_executor"
    RESPONSE_GENERATOR = "response_generator"
