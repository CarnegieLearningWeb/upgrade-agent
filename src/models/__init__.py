"""
Models package for UpGrade API types and data structures.

This package contains:
- enums.py: Enumeration types and constants
- types.py: TypedDict classes for raw API request/response structures  
- tool_types.py: TypedDict classes for tool-specific simplified types
- constants.py: Shared constants for HTTP headers and common values
"""

from .enums import (
    ExperimentState,
    ConsistencyRule,
    AssignmentUnit,
    PostExperimentRule,
    AssignmentAlgorithm,
    ConditionOrder,
    ExperimentType,
    PayloadType,
    RepeatedMeasure,
    FilterMode,
    SegmentType,
    MetricType,
    OperationType,
)

from .constants import (
    CONTENT_TYPE_JSON,
    ACCEPT_JSON,
)

from .types import (
    HealthResponse,
    ContextMetadata,
    ContextMetadataResponse,
    ExperimentName,
    EnrollmentCompleteCondition,
    StratificationFactor,
    Payload,
    Level,
    LevelCombinationElement,
    ConditionPayload,
    ConditionPayloadWithParent,
    Condition,
    Partition,
    Metric,
    Query,
    IndividualForSegment,
    GroupForSegment,
    Segment,
    ExperimentSegment,
    StateTimeLog,
    Experiment,
    CreateLevel,
    CreateFactor,
    CreateLevelCombinationElement,
    CreateCondition,
    CreateConditionPayload,
    CreatePartition,
    CreateIndividualForSegment,
    CreateGroupForSegment,
    CreateSegment,
    CreateExperimentSegment,
    CreateMetric,
    CreateQuery,
    CreateExperimentRequest,
    UpdateExperimentStateRequest,
    UpdateExperimentRequest,
    ExperimentListResponse,
    ExperimentNamesResponse,
    InitExperimentUserRequest,
    InitExperimentUserResponse,
    ExperimentAssignmentRequest,
    AssignedCondition,
    ExperimentAssignment,
    MarkAssignedCondition,
    MarkData,
    MarkExperimentRequest,
    MonitoredDecisionPoint,
    ExperimentAssignmentResponse,
)

from .tool_types import (
    # Simplified API Response Types (some are aliases to types.py)
    ToolHealthResponse,
    ToolContextMetadata,
    ToolExperimentName,
    
    # Tool-Specific Domain Types
    DecisionPoint,
    Condition as ToolCondition,
    InclusionExclusionGroup,
    ToolPostExperimentRule,
    SimplifiedExperiment,
    
    # Tool Workflow Types
    DecisionPointData,
    AssignedConditionData,
    
    # Tool State Management Types
    ToolActionType,
    ToolErrorType,
    ToolExecutionResult,
    GatheredInfo,
)

__all__ = [
    # Enums
    "ExperimentState",
    "ConsistencyRule", 
    "AssignmentUnit",
    "PostExperimentRule",
    "AssignmentAlgorithm",
    "ConditionOrder",
    "ExperimentType",
    "PayloadType",
    "RepeatedMeasure",
    "FilterMode",
    "SegmentType",
    "MetricType",
    "OperationType",
    
    # Raw API Types
    "HealthResponse",
    "ContextMetadata",
    "ContextMetadataResponse",
    "ExperimentName",
    "EnrollmentCompleteCondition",
    "StratificationFactor",
    "Payload",
    "Level",
    "LevelCombinationElement",
    "ConditionPayload",
    "ConditionPayloadWithParent",
    "Condition",
    "Partition",
    "Metric",
    "Query",
    "IndividualForSegment",
    "GroupForSegment",
    "Segment",
    "ExperimentSegment",
    "StateTimeLog",
    "Experiment",
    "CreateLevel",
    "CreateFactor",
    "CreateLevelCombinationElement",
    "CreateCondition",
    "CreateConditionPayload",
    "CreatePartition",
    "CreateIndividualForSegment",
    "CreateGroupForSegment",
    "CreateSegment",
    "CreateExperimentSegment",
    "CreateMetric",
    "CreateQuery",
    "CreateExperimentRequest",
    "UpdateExperimentStateRequest",
    "UpdateExperimentRequest",
    "ExperimentListResponse",
    "ExperimentNamesResponse",
    "InitExperimentUserRequest",
    "InitExperimentUserResponse",
    "ExperimentAssignmentRequest",
    "AssignedCondition",
    "ExperimentAssignment",
    "MarkAssignedCondition",
    "MarkData",
    "MarkExperimentRequest",
    "MonitoredDecisionPoint",
    "ExperimentAssignmentResponse",
    
    # Tool Types - Simplified API Response Types
    "ToolHealthResponse",
    "ToolContextMetadata",
    "ToolExperimentName",
    
    # Tool Types - Domain Types
    "DecisionPoint",
    "ToolCondition",
    "InclusionExclusionGroup",
    "ToolPostExperimentRule",
    "SimplifiedExperiment",
    
    # Tool Types - Parameter Types
    "ConditionConfig",
    "PartitionConfig",
    "CreateExperimentParams",
    "UpdateExperimentStatusParams",
    "InitUserParams",
    
    # Tool Types - Workflow Types
    "AssignmentParams",
    "DecisionPointData",
    "AssignedConditionData",
    "MarkDecisionPointParams",
    
    # Tool Types - State Management
    "ToolActionType",
    "ToolErrorType",
    "ToolExecutionResult",
    "GatheredInfo",
    
    # HTTP Constants
    "CONTENT_TYPE_JSON",
    "ACCEPT_JSON",
]
