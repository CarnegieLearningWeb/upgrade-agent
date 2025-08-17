"""
TypedDict classes for the UpGrade API endpoints.

This module defines types needed for system and experiments endpoints based on 
actual API request/response examples from docs/api-reference.md.
"""

from typing import Dict, List, Optional, Any, TypedDict
from .enums import (
    ExperimentState, 
    ConsistencyRule, 
    AssignmentUnit, 
    PostExperimentRule, 
    AssignmentAlgorithm, 
    FilterMode, 
    ExperimentType,
    PayloadType,
    ConditionOrder,
    RepeatedMeasure,
    SegmentType,
    MetricType,
    OperationType
)


# System endpoint types
class HealthResponse(TypedDict):
    """Response from GET / health check endpoint."""
    name: str
    version: str
    description: str


class ContextMetadata(TypedDict):
    """Context metadata for a single app context."""
    CONDITIONS: List[str]
    GROUP_TYPES: List[str]
    EXP_IDS: List[str]
    EXP_POINTS: List[str]


class ContextMetadataResponse(TypedDict):
    """Response from GET /experiments/contextMetaData endpoint."""
    contextMetadata: Dict[str, ContextMetadata]


# Experiment endpoint types
class ExperimentName(TypedDict):
    """Simple experiment name and ID from GET /experiments/names."""
    id: str
    name: str


class Payload(TypedDict):
    """Payload attached to conditions."""
    type: PayloadType
    value: str


class ConditionPayload(TypedDict):
    """Condition payload with metadata (from API responses)."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    payloadValue: str
    payloadType: PayloadType


class ConditionPayloadWithParent(TypedDict):
    """Condition payload with parent references (from full experiment responses)."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    parentCondition: str
    decisionPoint: str
    payload: Payload


class Condition(TypedDict):
    """Experiment condition/arm."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    twoCharacterId: str
    name: str
    description: Optional[str]
    conditionCode: str
    assignmentWeight: int
    order: int
    levelCombinationElements: List[Any]  # For factorial experiments
    conditionPayloads: List[ConditionPayload]


class Partition(TypedDict):
    """Experiment partition (decision point)."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    twoCharacterId: str
    site: str
    target: str
    description: str
    order: int
    excludeIfReached: bool


class Metric(TypedDict):
    """Metric definition for queries."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    key: str
    type: MetricType
    allowedData: Optional[Any]
    context: List[str]


class Query(TypedDict):
    """Experiment query for metrics."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    name: str
    query: Dict[str, Any]  # Contains operationType like {"operationType": "avg"}
    repeatedMeasure: RepeatedMeasure
    metric: Metric


class IndividualForSegment(TypedDict):
    """Individual membership in a segment."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    segmentId: str
    userId: str


class GroupForSegment(TypedDict):
    """Group membership in a segment."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    segmentId: str
    groupId: str
    type: str


class Segment(TypedDict):
    """Segment for inclusion/exclusion."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    name: str
    description: str
    listType: Optional[str]
    context: str
    type: SegmentType
    tags: Optional[List[str]]
    individualForSegment: List[IndividualForSegment]
    groupForSegment: List[GroupForSegment]
    subSegments: List[Any]


class ExperimentSegment(TypedDict):
    """Experiment segment inclusion/exclusion."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    segmentId: str
    experimentId: str
    segment: Segment


class StateTimeLog(TypedDict):
    """Log of state changes."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    fromState: ExperimentState
    toState: ExperimentState
    timeLog: str


class Experiment(TypedDict):
    """Full experiment object from API responses."""
    createdAt: str
    updatedAt: str
    versionNumber: int
    id: str
    name: str
    description: str
    context: List[str]
    state: ExperimentState
    startOn: Optional[str]
    consistencyRule: ConsistencyRule
    assignmentUnit: AssignmentUnit
    postExperimentRule: PostExperimentRule
    enrollmentCompleteCondition: Optional[Dict[str, Any]]
    endOn: Optional[str]
    revertTo: Optional[str]
    tags: List[str]
    group: Optional[str]
    conditionOrder: Optional[ConditionOrder]
    assignmentAlgorithm: AssignmentAlgorithm
    filterMode: FilterMode
    backendVersion: str
    type: ExperimentType
    conditions: List[Condition]
    partitions: List[Partition]
    factors: List[Any]  # For factorial experiments
    queries: List[Query]
    stateTimeLogs: List[StateTimeLog]
    experimentSegmentInclusion: ExperimentSegment
    experimentSegmentExclusion: ExperimentSegment
    conditionPayloads: List[ConditionPayloadWithParent]


# Request types for creating/updating experiments
class CreateCondition(TypedDict):
    """Condition data for creating experiments."""
    id: str
    conditionCode: str
    assignmentWeight: int
    description: Optional[str]
    order: int
    name: str


class CreateConditionPayload(TypedDict):
    """Condition payload for creating experiments."""
    id: str
    payload: Payload
    parentCondition: str
    decisionPoint: str


class CreatePartition(TypedDict):
    """Partition data for creating experiments."""
    id: str
    site: str
    target: str
    description: str
    order: int
    excludeIfReached: bool


class CreateIndividualForSegment(TypedDict):
    """Individual for segment creation."""
    userId: str


class CreateGroupForSegment(TypedDict):
    """Group for segment creation."""
    groupId: str
    type: str


class CreateSegment(TypedDict):
    """Segment data for creating experiments."""
    individualForSegment: List[CreateIndividualForSegment]
    groupForSegment: List[CreateGroupForSegment]
    subSegments: List[Any]
    type: SegmentType


class CreateExperimentSegment(TypedDict):
    """Experiment segment for creating experiments."""
    segment: CreateSegment


class CreateMetric(TypedDict):
    """Metric reference for creating queries."""
    key: str


class CreateQuery(TypedDict):
    """Query data for creating experiments."""
    name: str
    query: Dict[str, Any]  # {"operationType": "avg"}
    metric: CreateMetric
    repeatedMeasure: RepeatedMeasure


class CreateExperimentRequest(TypedDict):
    """Request payload for POST /experiments."""
    name: str
    description: str
    consistencyRule: ConsistencyRule
    assignmentUnit: AssignmentUnit
    type: ExperimentType
    context: List[str]
    assignmentAlgorithm: AssignmentAlgorithm
    stratificationFactor: Optional[Any]
    tags: List[str]
    conditions: List[CreateCondition]
    conditionPayloads: List[CreateConditionPayload]
    partitions: List[CreatePartition]
    experimentSegmentInclusion: CreateExperimentSegment
    experimentSegmentExclusion: CreateExperimentSegment
    filterMode: FilterMode
    queries: List[CreateQuery]
    endOn: Optional[str]
    enrollmentCompleteCondition: Optional[Dict[str, Any]]
    startOn: Optional[str]
    state: ExperimentState
    postExperimentRule: PostExperimentRule
    revertTo: Optional[str]


class UpdateExperimentStateRequest(TypedDict):
    """Request payload for POST /experiments/state."""
    experimentId: str
    state: ExperimentState


# For PUT /experiments/{id}, the request can be a partial or full experiment object
# Using the same type as creation for simplicity, as the API accepts full objects
UpdateExperimentRequest = CreateExperimentRequest

# Type aliases for common response types
ExperimentListResponse = List[Experiment]
ExperimentNamesResponse = List[ExperimentName]
