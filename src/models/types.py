"""
Type definitions for UpGrade API interactions.

This module contains TypedDict classes that correspond to API request/response
structures. These are used for type safety and documentation throughout the
UpGrade client implementation.
"""

from typing import Dict, List, Optional, Any, TypedDict, NotRequired
from .enums import (
    PostExperimentRule,
    ExperimentState,
    ExperimentType,
    AssignmentUnit,
    ConsistencyRule,
    FilterMode,
    PayloadType,
    MetricType,
    RepeatedMeasure,
    SegmentType,
    ConditionOrder,
    AssignmentAlgorithm,
    MarkedDecisionPointStatus
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


class EnrollmentCompleteCondition(TypedDict, total=False):
    """Enrollment complete condition for experiments (all fields optional)."""
    userCount: int
    groupCount: int


class StratificationFactor(TypedDict):
    """Stratification factor for experiments."""
    stratificationFactorName: str


class Payload(TypedDict):
    """Payload attached to conditions."""
    type: PayloadType
    value: str


# Factorial experiment types
class Level(TypedDict):
    """Level definition for factorial experiments."""
    id: str
    name: str
    description: NotRequired[Optional[str]]
    order: NotRequired[Optional[int]]
    payload: Optional[Payload]


class LevelCombinationElement(TypedDict):
    """Level combination element for factorial experiments."""
    id: str
    level: Level


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
    id: str
    payload: Payload
    parentCondition: str
    decisionPoint: NotRequired[Optional[str]]


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
    levelCombinationElements: Optional[List[LevelCombinationElement]]
    conditionPayloads: Optional[List[ConditionPayload]]


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
    key: str


class Query(TypedDict):
    """Experiment query for metrics."""
    id: Optional[str]
    name: str
    query: Dict[str, Any]
    metric: Metric
    repeatedMeasure: RepeatedMeasure


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
    enrollmentCompleteCondition: Optional[EnrollmentCompleteCondition]
    endOn: Optional[str]
    revertTo: Optional[str]
    tags: List[str]
    group: Optional[str]
    conditionOrder: Optional[ConditionOrder]
    assignmentAlgorithm: AssignmentAlgorithm
    filterMode: FilterMode
    backendVersion: str
    type: ExperimentType
    stratificationFactor: Optional[StratificationFactor]
    conditions: List[Condition]
    partitions: List[Partition]
    factors: List[Any]  # For factorial experiments
    queries: List[Query]
    stateTimeLogs: List[StateTimeLog]
    experimentSegmentInclusion: ExperimentSegment
    experimentSegmentExclusion: ExperimentSegment
    conditionPayloads: List[ConditionPayloadWithParent]


# Request types for creating/updating experiments

# Factorial experiment request types
class CreateLevel(TypedDict):
    """Level data for creating factorial experiments."""
    id: str
    name: str
    description: NotRequired[Optional[str]]
    order: NotRequired[Optional[int]]
    payload: Optional[Payload]


class CreateFactor(TypedDict):
    """Factor data for creating factorial experiments."""
    id: NotRequired[Optional[str]]
    name: str
    description: NotRequired[Optional[str]]
    order: int
    levels: List[CreateLevel]


class CreateLevelCombinationElement(TypedDict):
    """Level combination element for creating factorial experiments."""
    id: str
    level: CreateLevel


class CreateCondition(TypedDict):
    """Condition data for creating experiments."""
    id: str
    twoCharacterId: NotRequired[Optional[str]]
    conditionCode: str
    assignmentWeight: int
    description: NotRequired[Optional[str]]
    order: int
    name: NotRequired[Optional[str]]
    levelCombinationElements: NotRequired[Optional[List[CreateLevelCombinationElement]]]


class CreateConditionPayload(TypedDict):
    """Condition payload for creating experiments."""
    id: str
    payload: Payload
    parentCondition: str
    decisionPoint: NotRequired[Optional[str]]


class CreatePartition(TypedDict):
    """Partition data for creating experiments."""
    id: str
    twoCharacterId: NotRequired[Optional[str]]
    site: str
    target: NotRequired[Optional[str]]
    description: NotRequired[Optional[str]]
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
    id: Optional[str]
    name: str
    query: Dict[str, Any]
    metric: CreateMetric
    repeatedMeasure: RepeatedMeasure


class CreateExperimentRequest(TypedDict):
    """Request payload for POST /experiments."""
    name: str
    description: str
    consistencyRule: ConsistencyRule
    assignmentUnit: AssignmentUnit
    group: NotRequired[Optional[str]]
    conditionOrder: NotRequired[ConditionOrder]
    type: ExperimentType
    context: List[str]
    assignmentAlgorithm: AssignmentAlgorithm
    stratificationFactor: NotRequired[Optional[StratificationFactor]]
    tags: List[str]
    conditions: List[CreateCondition]
    conditionPayloads: NotRequired[Optional[List[CreateConditionPayload]]]
    partitions: List[CreatePartition]
    experimentSegmentInclusion: CreateExperimentSegment
    experimentSegmentExclusion: CreateExperimentSegment
    filterMode: FilterMode
    factors: NotRequired[Optional[List[CreateFactor]]]
    queries: NotRequired[Optional[List[CreateQuery]]]
    endOn: NotRequired[Optional[str]]
    enrollmentCompleteCondition: NotRequired[Optional[EnrollmentCompleteCondition]]
    startOn: NotRequired[Optional[str]]
    state: ExperimentState
    postExperimentRule: PostExperimentRule
    revertTo: NotRequired[Optional[str]]
    moocletPolicyParameters: NotRequired[Any]
    rewardMetricKey: NotRequired[str]


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


# Simulation endpoint types for v6 API

# User initialization types (POST /v6/init)
class InitExperimentUserRequest(TypedDict):
    """Request payload for POST /v6/init."""
    group: NotRequired[Optional[Dict[str, List[str]]]]
    workingGroup: NotRequired[Optional[Dict[str, str]]]


class InitExperimentUserResponse(TypedDict):
    """Response from POST /v6/init."""
    id: str
    group: NotRequired[Optional[Dict[str, List[str]]]]
    workingGroup: NotRequired[Optional[Dict[str, str]]]


# Assignment types (POST /v6/assign)
class ExperimentAssignmentRequest(TypedDict):
    """Request payload for POST /v6/assign."""
    context: str


class AssignedCondition(TypedDict):
    """Assigned condition for a user."""
    conditionCode: str
    payload: Payload
    experimentId: Optional[str]
    id: str


class ExperimentAssignment(TypedDict):
    """Single experiment assignment for a decision point."""
    site: str
    target: str
    assignedCondition: List[AssignedCondition]
    assignedFactor: Optional[List[Dict[str, Dict[str, str]]]]
    experimentType: ExperimentType


class ExperimentAssignmentResponse(TypedDict):
    """Response from POST /v6/assign containing list of experiment assignments."""
    data: List[ExperimentAssignment]


# Mark endpoint types (POST /v6/mark)
class MarkAssignedCondition(TypedDict):
    """Assigned condition data for mark endpoint."""
    id: NotRequired[Optional[str]]
    conditionCode: NotRequired[Optional[str]]
    experimentId: NotRequired[Optional[str]]


class MarkData(TypedDict):
    """Data section for mark request."""
    site: str
    target: str
    assignedCondition: Optional[MarkAssignedCondition]


class MarkExperimentRequest(TypedDict):
    """Request payload for POST /v6/mark."""
    data: MarkData
    status: NotRequired[Optional[MarkedDecisionPointStatus]]
    uniquifier: NotRequired[Optional[str]]
    clientError: NotRequired[Optional[str]]


class MarkExperimentResponse(TypedDict):
    """Response from POST /v6/mark."""
    id: str
    userId: str
    site: str
    target: str
    experimentId: Optional[str]
    condition: Optional[str]
