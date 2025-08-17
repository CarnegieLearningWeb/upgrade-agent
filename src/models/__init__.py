"""
Models package for UpGrade API types and data structures.

This package contains:
- enums.py: Enumeration types and constants
- types.py: TypedDict classes for complex data structures  
- constants.py: Shared constants for HTTP headers and common values
- requests.py: Request and response model definitions
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
    Payload,
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
    
    # Types
    "HealthResponse",
    "ContextMetadata",
    "ContextMetadataResponse",
    "ExperimentName",
    "Payload",
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
    # HTTP Constants
    "CONTENT_TYPE_JSON",
    "ACCEPT_JSON",
]
