"""
Complete UpGrade API Type Definitions

This module provides comprehensive, enterprise-grade Pydantic models for all UpGrade API endpoints.
All models are designed for complete API compliance, type safety, and production reliability.

Created for educational software serving thousands of students - every field matters.
"""

from typing import Dict, List, Any, Optional, Literal, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid

# =============================================================================
# TYPE ALIASES AND ENUMS
# =============================================================================

# Experiment states
ExperimentState = Literal["inactive", "preview", "scheduled", "enrolling", "enrollmentComplete", "cancelled"]

# Assignment units  
AssignmentUnit = Literal["individual", "group"]

# Consistency rules
ConsistencyRule = Literal["individual", "experiment", "group"]

# Post experiment rules
PostExperimentRule = Literal["continue", "revert", "assign"]

# Filter modes
FilterMode = Literal["excludeAll", "includeAll"]

# Experiment types
ExperimentType = Literal["Simple", "Factorial", "Stratified", "Within-Subject"]

# Assignment algorithms
AssignmentAlgorithm = Literal["random", "stratified", "weightedRandom"]

# Payload types
PayloadType = Literal["string", "number", "json", "csv"]

# Mark status types
MarkStatus = Literal["condition applied", "condition not applied", "no condition assigned"]

# Segment types
SegmentType = Literal["private", "public"]

# Metric types
MetricType = Literal["continuous", "categorical", "binary"]

# Repeated measure types
RepeatedMeasureType = Literal["MOST RECENT", "EARLIEST", "ALL"]

# =============================================================================
# BASIC RESPONSE MODELS (Working - No Changes Needed)
# =============================================================================

class HealthCheckResponse(BaseModel):
    """Health check endpoint response"""
    name: str
    version: str
    description: Optional[str] = None


class ContextMetadataItem(BaseModel):
    """Context metadata for a specific app context"""
    CONDITIONS: Optional[List[str]] = None
    GROUP_TYPES: Optional[List[str]] = None
    EXP_IDS: Optional[List[str]] = None
    EXP_POINTS: Optional[List[str]] = None


class ContextMetadata(BaseModel):
    """Complete context metadata response"""
    contextMetadata: Dict[str, ContextMetadataItem]


class ExperimentName(BaseModel):
    """Experiment name and ID pair"""
    id: str
    name: str


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200

# =============================================================================
# PAYLOAD SYSTEM MODELS
# =============================================================================

class PayloadValue(BaseModel):
    """Represents a payload value with type information"""
    type: PayloadType
    value: Union[str, int, float, Dict[str, Any], List[Any]]
    
    @validator('value')
    def validate_value_matches_type(cls, v, values):
        """Ensure payload value matches declared type"""
        payload_type = values.get('type')
        if payload_type == 'string' and not isinstance(v, str):
            raise ValueError('String payload must have string value')
        elif payload_type == 'number' and not isinstance(v, (int, float)):
            raise ValueError('Number payload must have numeric value')
        elif payload_type == 'json' and not isinstance(v, (dict, list)):
            raise ValueError('JSON payload must have dict or list value')
        return v


class ConditionPayload(BaseModel):
    """Payload associated with a specific condition and decision point"""
    id: Optional[str] = None
    payload: PayloadValue
    parentCondition: str  # UUID of parent condition
    decisionPoint: str    # UUID of decision point
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    
    @validator('id', pre=True, always=True)
    def generate_id_if_missing(cls, v):
        """Auto-generate UUID if not provided"""
        return v or str(uuid.uuid4())

# =============================================================================
# CORE EXPERIMENT STRUCTURE MODELS
# =============================================================================

class Condition(BaseModel):
    """Experiment condition with complete field support"""
    id: Optional[str] = None
    name: Optional[str] = ""
    description: Optional[str] = None
    conditionCode: str
    assignmentWeight: float
    order: Optional[int] = None
    twoCharacterId: Optional[str] = None
    experimentId: Optional[str] = None
    levelCombinationElements: Optional[List[Any]] = None
    conditionPayloads: Optional[List[Any]] = None  # Can be ConditionPayload objects
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    
    @validator('id', pre=True, always=True)
    def generate_id_if_missing(cls, v):
        """Auto-generate UUID if not provided"""
        return v or str(uuid.uuid4())
    
    @validator('assignmentWeight')
    def validate_weight(cls, v):
        """Validate assignment weight is between 0 and 100"""
        if not 0 <= v <= 100:
            raise ValueError('Assignment weight must be between 0 and 100')
        return v


class Partition(BaseModel):
    """Decision point (partition) with complete field support"""
    id: Optional[str] = None
    site: str
    target: str
    description: Optional[str] = ""
    order: Optional[int] = None
    excludeIfReached: Optional[bool] = False
    twoCharacterId: Optional[str] = None
    experimentId: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    
    @validator('id', pre=True, always=True)
    def generate_id_if_missing(cls, v):
        """Auto-generate UUID if not provided"""
        return v or str(uuid.uuid4())


# Alias for backward compatibility and API consistency
DecisionPoint = Partition

# =============================================================================
# USER SEGMENT MODELS (For Inclusion/Exclusion)
# =============================================================================

class IndividualForSegment(BaseModel):
    """Individual user in a segment"""
    userId: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    segmentId: Optional[str] = None


class GroupForSegment(BaseModel):
    """Group in a segment"""
    groupId: str
    type: str  # e.g., "schoolId", "classId", "All"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    segmentId: Optional[str] = None


class Segment(BaseModel):
    """User segment for inclusion/exclusion"""
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    listType: Optional[str] = None
    context: Optional[str] = None
    type: SegmentType = "private"
    tags: Optional[List[str]] = None
    individualForSegment: List[IndividualForSegment] = []
    groupForSegment: List[GroupForSegment] = []
    subSegments: List[Union[str, Dict[str, Any]]] = []  # Can be UUIDs or full objects
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None


class ExperimentSegmentInclusion(BaseModel):
    """Experiment inclusion segment relationship"""
    segmentId: Optional[str] = None
    experimentId: Optional[str] = None
    segment: Segment
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None


class ExperimentSegmentExclusion(BaseModel):
    """Experiment exclusion segment relationship"""
    segmentId: Optional[str] = None
    experimentId: Optional[str] = None
    segment: Segment
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None

# =============================================================================
# METRICS AND QUERY MODELS
# =============================================================================

class Metric(BaseModel):
    """Metric definition for experiment measurement"""
    key: str
    type: MetricType = "continuous"
    allowedData: Optional[List[str]] = None
    context: List[str]
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None


class Query(BaseModel):
    """Query definition for metric analysis"""
    id: Optional[str] = None
    name: str
    query: Dict[str, Any]  # e.g., {"operationType": "avg"}
    repeatedMeasure: RepeatedMeasureType = "MOST RECENT"
    metric: Metric
    experimentId: Optional[str] = None
    experiment: Optional[Dict[str, Any]] = None  # Can contain full experiment object
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    
    @validator('id', pre=True, always=True)
    def generate_id_if_missing(cls, v):
        """Auto-generate UUID if not provided"""
        return v or str(uuid.uuid4())

# =============================================================================
# STATE MANAGEMENT MODELS
# =============================================================================

class StateTimeLog(BaseModel):
    """Log of experiment state changes"""
    id: Optional[str] = None
    fromState: ExperimentState
    toState: ExperimentState
    timeLog: datetime
    experiment: Optional[Dict[str, Any]] = None  # Can contain full experiment object
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None

# =============================================================================
# COMPLETE EXPERIMENT MODELS
# =============================================================================

class ExperimentCreateRequest(BaseModel):
    """Complete experiment creation request matching API specification"""
    
    # Basic Information
    name: str
    description: Optional[str] = ""
    type: ExperimentType = "Simple"
    context: List[str]
    
    # Assignment Configuration
    assignmentUnit: AssignmentUnit = "individual"
    consistencyRule: ConsistencyRule = "individual"
    assignmentAlgorithm: AssignmentAlgorithm = "random"
    
    # State and Timing
    state: Literal["inactive", "preview", "scheduled", "enrolling"] = "inactive"
    startOn: Optional[datetime] = None
    endOn: Optional[datetime] = None
    postExperimentRule: PostExperimentRule = "continue"
    revertTo: Optional[str] = None  # Condition ID to revert to
    enrollmentCompleteCondition: Optional[Condition] = None
    
    # Experiment Structure
    conditions: List[Condition]
    partitions: List[Partition]  # API calls these partitions
    conditionPayloads: List[ConditionPayload]
    
    # User Targeting
    filterMode: FilterMode = "excludeAll"
    experimentSegmentInclusion: ExperimentSegmentInclusion
    experimentSegmentExclusion: ExperimentSegmentExclusion
    
    # Metrics and Analysis
    queries: List[Query] = []
    
    # Organization
    tags: List[str] = []
    group: Optional[str] = None
    stratificationFactor: Optional[str] = None
    
    @validator('conditions')
    def validate_conditions(cls, v):
        """Validate conditions are properly configured"""
        if not v:
            raise ValueError('At least one condition is required')
        
        # Check weights sum to 100
        total_weight = sum(c.assignmentWeight for c in v)
        if abs(total_weight - 100.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f'Condition weights must sum to 100, got {total_weight}')
        
        return v
    
    @validator('partitions')
    def validate_partitions(cls, v):
        """Validate partitions are provided"""
        if not v:
            raise ValueError('At least one partition (decision point) is required')
        return v


class Experiment(BaseModel):
    """Complete experiment model matching API responses"""
    
    # Metadata
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    backendVersion: Optional[str] = None
    
    # Basic Information
    name: str
    description: Optional[str] = None
    type: Optional[ExperimentType] = None
    context: List[str]
    
    # Assignment Configuration
    assignmentUnit: AssignmentUnit = "individual"
    consistencyRule: ConsistencyRule = "individual"
    assignmentAlgorithm: Optional[AssignmentAlgorithm] = None
    
    # State and Timing
    state: ExperimentState = "inactive"
    startOn: Optional[datetime] = None
    endOn: Optional[datetime] = None
    postExperimentRule: Optional[PostExperimentRule] = None
    revertTo: Optional[str] = None
    enrollmentCompleteCondition: Optional[Condition] = None
    
    # Experiment Structure
    conditions: List[Condition] = []  # Default to empty list if missing
    partitions: Optional[List[Partition]] = None
    decisionPoints: Optional[List[Partition]] = None  # Alias for partitions
    conditionPayloads: Optional[List[ConditionPayload]] = None
    
    @validator('conditions', pre=True)
    def handle_missing_conditions(cls, v):
        """Handle cases where API doesn't return conditions field"""
        return v if v is not None else []
    
    # User Targeting
    filterMode: Optional[FilterMode] = None
    experimentSegmentInclusion: Optional[ExperimentSegmentInclusion] = None
    experimentSegmentExclusion: Optional[ExperimentSegmentExclusion] = None
    
    # Metrics and Analysis
    queries: Optional[List[Query]] = None
    
    # Organization
    tags: Optional[List[str]] = None
    group: Optional[str] = None
    conditionOrder: Optional[str] = None
    stratificationFactor: Optional[str] = None
    
    # Advanced Features
    factors: Optional[List[Any]] = None  # For factorial experiments
    stateTimeLogs: Optional[List[StateTimeLog]] = None
    groupSatisfied: Optional[Any] = None


class ExperimentStateUpdate(BaseModel):
    """Request to update experiment state"""
    experimentId: str
    state: ExperimentState

# =============================================================================
# USER SIMULATION MODELS (Working - Minimal Changes)
# =============================================================================

class InitRequest(BaseModel):
    """User initialization request"""
    group: Optional[Dict[str, List[str]]] = None
    workingGroup: Optional[Dict[str, str]] = None


class InitResponse(BaseModel):
    """User initialization response"""
    id: str
    group: Optional[Dict[str, List[str]]] = None
    workingGroup: Optional[Dict[str, str]] = None


class AssignRequest(BaseModel):
    """Assignment request"""
    context: str


class AssignmentCondition(BaseModel):
    """Assigned condition information"""
    id: str
    conditionCode: str
    payload: Dict[str, Any]
    experimentId: str


class AssignmentFactor(BaseModel):
    """Assigned factor information for factorial experiments"""
    level: str
    payload: Dict[str, Any]


class AssignmentResult(BaseModel):
    """Assignment result for a decision point"""
    site: str
    target: str
    experimentType: Optional[str] = None
    assignedCondition: Optional[List[AssignmentCondition]] = None
    assignedFactor: Optional[List[Dict[str, AssignmentFactor]]] = None


# Assignment response is an array of results
AssignResponse = List[AssignmentResult]


class AssignedCondition(BaseModel):
    """Condition information for marking"""
    id: str
    conditionCode: str
    payload: Dict[str, Any]
    experimentId: str


class MarkData(BaseModel):
    """Data for marking a decision point visit"""
    target: str
    site: str
    assignedCondition: Optional[AssignedCondition] = None


class MarkRequest(BaseModel):
    """Request to mark a decision point visit"""
    data: MarkData
    status: MarkStatus


class MarkResponse(BaseModel):
    """Response from marking a decision point"""
    id: str
    condition: Optional[str] = None
    userId: str
    site: str
    target: str
    experimentId: Optional[str] = None

# =============================================================================
# HELPER BUILDER CLASSES
# =============================================================================

class SimpleExperimentBuilder:
    """Helper class to build valid ExperimentCreateRequest objects"""
    
    @staticmethod
    def create_simple_experiment(
        name: str,
        context: str,
        site: str,
        target: str,
        conditions: List[Dict[str, Any]] = None,
        description: str = "",
        assignment_unit: AssignmentUnit = "individual",
        consistency_rule: ConsistencyRule = "individual"
    ) -> ExperimentCreateRequest:
        """
        Create a simple, valid experiment with all required fields
        
        Args:
            name: Experiment name
            context: App context (e.g., "assign-prog")
            site: Decision point site
            target: Decision point target
            conditions: List of condition dicts with 'code' and 'weight' keys
            description: Optional description
            assignment_unit: "individual" or "group"
            consistency_rule: "individual", "experiment", or "group"
            
        Returns:
            Complete ExperimentCreateRequest ready for API submission
        """
        
        # Default conditions if none provided
        if not conditions:
            conditions = [
                {"code": "control", "weight": 50.0},
                {"code": "variant", "weight": 50.0}
            ]
        
        # Validate weights sum to 100
        total_weight = sum(c.get("weight", 0) for c in conditions)
        if abs(total_weight - 100.0) > 0.01:
            raise ValueError(f"Condition weights must sum to 100, got {total_weight}")
        
        # Create condition objects with proper ordering
        condition_objects = []
        for i, cond in enumerate(conditions, 1):
            condition_objects.append(Condition(
                conditionCode=cond["code"],
                assignmentWeight=cond["weight"],
                name=cond.get("name", cond["code"]),
                description=cond.get("description", ""),
                order=i
            ))
        
        # Create partition object
        partition = Partition(
            site=site,
            target=target,
            description="",
            order=1
        )
        
        # Create condition payloads linking conditions to partition
        condition_payloads = []
        for condition in condition_objects:
            condition_payloads.append(ConditionPayload(
                payload=PayloadValue(
                    type="string",
                    value=condition.conditionCode
                ),
                parentCondition=condition.id,
                decisionPoint=partition.id
            ))
        
        # Create minimal segments (required but can be empty)
        inclusion_segment = ExperimentSegmentInclusion(
            segment=Segment(
                type="private",
                individualForSegment=[],
                groupForSegment=[],
                subSegments=[]
            )
        )
        
        exclusion_segment = ExperimentSegmentExclusion(
            segment=Segment(
                type="private",
                individualForSegment=[],
                groupForSegment=[],
                subSegments=[]
            )
        )
        
        return ExperimentCreateRequest(
            name=name,
            description=description,
            context=[context],
            type="Simple",
            assignmentUnit=assignment_unit,
            consistencyRule=consistency_rule,
            assignmentAlgorithm="random",
            conditions=condition_objects,
            partitions=[partition],
            conditionPayloads=condition_payloads,
            experimentSegmentInclusion=inclusion_segment,
            experimentSegmentExclusion=exclusion_segment,
            filterMode="excludeAll",
            queries=[],
            tags=[]
        )