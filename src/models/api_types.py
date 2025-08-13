from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class HealthCheckResponse(BaseModel):
    name: str
    version: str
    description: Optional[str] = None


class AppContext(BaseModel):
    app_context: str
    group_types: List[str]


class ContextMetadataItem(BaseModel):
    CONDITIONS: Optional[List[str]] = None
    GROUP_TYPES: Optional[List[str]] = None
    EXP_IDS: Optional[List[str]] = None
    EXP_POINTS: Optional[List[str]] = None

class ContextMetadata(BaseModel):
    contextMetadata: Dict[str, ContextMetadataItem]


class ExperimentName(BaseModel):
    id: str
    name: str


class Condition(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    conditionCode: str
    assignmentWeight: float
    order: Optional[int] = None
    twoCharacterId: Optional[str] = None
    experimentId: Optional[str] = None
    levelCombinationElements: Optional[List[Any]] = None
    conditionPayloads: Optional[List[Any]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None


# In UpGrade API, decision points are called 'partitions'
class Partition(BaseModel):
    id: Optional[str] = None
    site: str
    target: str
    description: Optional[str] = None
    order: Optional[int] = None
    excludeIfReached: Optional[bool] = False
    twoCharacterId: Optional[str] = None
    experimentId: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None

# Alias for backward compatibility
DecisionPoint = Partition


class GroupAssignment(BaseModel):
    groupId: str
    type: str
    
    
class ConsistencyRule(BaseModel):
    site: str
    target: str
    
    
class Experiment(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    context: List[str]
    state: Literal["inactive", "preview", "scheduled", "enrolling", "enrollmentComplete", "cancelled"] = "inactive"
    conditions: List[Condition]
    partitions: Optional[List[Partition]] = None  # Called partitions in API
    decisionPoints: Optional[List[Partition]] = None  # For backward compatibility
    postExperimentRule: Optional[Literal["continue", "revert", "assign"]] = "continue"
    enrollmentCompleteCondition: Optional[Condition] = None
    endOn: Optional[datetime] = None
    enrollOn: Optional[datetime] = None  # API calls this startOn
    startOn: Optional[datetime] = None
    consistencyRule: Literal["individual", "experiment", "group"] = "individual"
    assignmentUnit: Literal["individual", "group"] = "individual"
    group: Optional[str] = None
    type: Optional[str] = None
    assignmentAlgorithm: Optional[str] = None
    filterMode: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    versionNumber: Optional[int] = None
    backendVersion: Optional[str] = None
    tags: Optional[List[str]] = None
    conditionOrder: Optional[str] = None
    revertTo: Optional[str] = None
    factors: Optional[List[Any]] = None
    queries: Optional[List[Any]] = None
    conditionPayloads: Optional[List[Any]] = None
    stateTimeLogs: Optional[List[Any]] = None
    experimentSegmentInclusion: Optional[Any] = None
    experimentSegmentExclusion: Optional[Any] = None
    stratificationFactor: Optional[Any] = None
    groupSatisfied: Optional[Any] = None


class ExperimentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    context: List[str]
    state: Literal["inactive", "preview", "scheduled", "enrolling"] = "inactive"
    conditions: List[Condition]
    decisionPoints: List[DecisionPoint]
    postExperimentRule: Optional[Literal["continue", "revert"]] = "continue"
    enrollmentCompleteCondition: Optional[Condition] = None
    endOn: Optional[str] = None
    enrollOn: Optional[str] = None
    consistencyRule: Literal["individual", "experiment", "group"] = "individual"
    assignmentUnit: Literal["individual", "group"] = "individual"
    group: Optional[str] = None


class ExperimentStateUpdate(BaseModel):
    experimentId: str
    state: Literal["inactive", "preview", "scheduled", "enrolling", "enrollmentComplete", "cancelled"]


class InitUser(BaseModel):
    id: Optional[str] = None  # ID comes from User-Id header
    group: Optional[Dict[str, List[str]]] = None
    workingGroup: Optional[Dict[str, str]] = None


# Init request - API expects single user object or array
# According to docs, it should be a single object without id field
class InitRequestBody(BaseModel):
    group: Optional[Dict[str, List[str]]] = None
    workingGroup: Optional[Dict[str, str]] = None

InitRequest = InitRequestBody  # For single user init


class InitResponse(BaseModel):
    id: str
    group: Optional[Dict[str, List[str]]] = None
    workingGroup: Optional[Dict[str, str]] = None


class AssignRequest(BaseModel):
    context: str
    
    
class AssignmentCondition(BaseModel):
    id: str
    conditionCode: str
    payload: Dict[str, Any]
    experimentId: str

class AssignmentFactor(BaseModel):
    level: str
    payload: Dict[str, Any]

class AssignmentResult(BaseModel):
    site: str
    target: str
    experimentType: Optional[str] = None
    assignedCondition: Optional[List[AssignmentCondition]] = None
    assignedFactor: Optional[List[Dict[str, AssignmentFactor]]] = None

# v6/assign returns an array of AssignmentResult directly
AssignResponse = List[AssignmentResult]


class AssignedCondition(BaseModel):
    id: str
    conditionCode: str
    payload: Dict[str, Any]
    experimentId: str

class MarkData(BaseModel):
    target: str
    site: str
    assignedCondition: Optional[AssignedCondition] = None

class MarkRequest(BaseModel):
    data: MarkData
    status: Literal["condition applied", "condition not applied", "no condition assigned"]
    
    
class MarkResponse(BaseModel):
    id: str
    condition: Optional[str] = None
    userId: str
    site: str
    target: str
    experimentId: Optional[str] = None
    

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200