"""
Tool Executor action tools.

These tools execute the actual API calls for modifying UpGrade state.
They use the prepared parameters from the Information Gatherer and
log all executions in the execution_log.
"""

from langchain.tools import tool
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime

from src.tools.registry import register_executor_tool
from src.api.endpoints.experiments import (
    create_experiment as api_create_experiment,
    update_experiment as api_update_experiment,
    update_experiment_status as api_update_experiment_status,
    delete_experiment as api_delete_experiment
)
from src.api.endpoints.simulation import (
    init_experiment_user as api_init_experiment_user,
    get_decision_point_assignments as api_get_decision_point_assignments,
    mark_decision_point as api_mark_decision_point
)
from src.models.types import (
    CreateExperimentRequest, CreateCondition, CreatePartition,
    CreateExperimentSegment, CreateSegment, CreateIndividualForSegment, CreateGroupForSegment
)
from src.models.enums import (
    ExperimentState, ExperimentType, AssignmentUnit, ConsistencyRule, 
    FilterMode, PostExperimentRule, AssignmentAlgorithm, ConditionOrder, SegmentType
)


def _log_execution(action: str, success: bool, result: Any = None, error: str = None):
    """Log tool execution to the execution_log."""
    from src.tools.decorators import _state_ref
    if _state_ref is None:
        return
        
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "success": success,
        "result": result if success else None,
        "error": error if not success else None
    }
    
    if "execution_log" not in _state_ref:
        _state_ref["execution_log"] = []
    _state_ref["execution_log"].append(log_entry)


def _validate_required_params(params: Dict[str, Any], required_keys: List[str]):
    """Validate that all required parameters are present."""
    missing = [key for key in required_keys if key not in params or params[key] is None]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")


def _create_experiment_segment(
    inclusion_users: List[str] = None,
    inclusion_groups: List[Dict[str, str]] = None,
    exclusion_users: List[str] = None,
    exclusion_groups: List[Dict[str, str]] = None,
    is_inclusion: bool = True
) -> CreateExperimentSegment:
    """
    Create experiment segment for inclusion or exclusion.
    
    Args:
        inclusion_users: List of user IDs for inclusion (only used if is_inclusion=True)
        inclusion_groups: List of group data for inclusion (only used if is_inclusion=True)
        exclusion_users: List of user IDs for exclusion (only used if is_inclusion=False)
        exclusion_groups: List of group data for exclusion (only used if is_inclusion=False)
        is_inclusion: Whether this is for inclusion (True) or exclusion (False)
    
    Returns:
        CreateExperimentSegment with proper structure
    """
    # Choose the appropriate lists based on whether this is inclusion or exclusion
    if is_inclusion:
        users = inclusion_users or []
        groups = inclusion_groups or []
    else:
        users = exclusion_users or []
        groups = exclusion_groups or []
    
    # Transform user IDs to CreateIndividualForSegment format
    individual_for_segment: List[CreateIndividualForSegment] = []
    for user_id in users:
        individual_for_segment.append(CreateIndividualForSegment(
            userId=user_id
        ))
    
    # Transform group data to CreateGroupForSegment format
    group_for_segment: List[CreateGroupForSegment] = []
    for group in groups:
        group_for_segment.append(CreateGroupForSegment(
            groupId=group['group_id'],
            type=group['type']
        ))
    
    # Create the segment
    segment: CreateSegment = {
        'individualForSegment': individual_for_segment,
        'groupForSegment': group_for_segment,
        'subSegments': [],
        'type': SegmentType('private')
    }
    
    return CreateExperimentSegment(segment=segment)


def _create_conditions(conditions_data: List[Dict[str, Any]]) -> tuple[List[CreateCondition], Dict[str, str]]:
    """
    Create conditions from simplified format and return condition code to UUID mapping.
    
    Args:
        conditions_data: List of condition dictionaries with {code, weight} format
        
    Returns:
        Tuple of (conditions_list, condition_code_to_id_mapping)
    """
    condition_code_to_id: Dict[str, str] = {}
    conditions: List[CreateCondition] = []
    
    for i, condition in enumerate(conditions_data):
        condition_id = str(uuid4())
        condition_code_to_id[condition['code']] = condition_id
        
        conditions.append(CreateCondition(
            id=condition_id,
            twoCharacterId=None,
            conditionCode=condition['code'],
            assignmentWeight=condition['weight'],
            description=None,
            order=i,
            name=condition.get('name', condition['code']),
            levelCombinationElements=None
        ))
    
    return conditions, condition_code_to_id


def _create_partitions(decision_points_data: List[Dict[str, Any]]) -> List[CreatePartition]:
    """
    Create partitions from simplified decision points format.
    
    Args:
        decision_points_data: List of decision point dictionaries with {site, target, exclude_if_reached} format
        
    Returns:
        List of CreatePartition objects
    """
    partitions: List[CreatePartition] = []
    
    for i, dp in enumerate(decision_points_data):
        partitions.append(CreatePartition(
            id=str(uuid4()),
            twoCharacterId=None,
            site=dp['site'],
            target=dp.get('target'),
            description=None,
            order=i,
            excludeIfReached=dp.get('exclude_if_reached', False)
        ))
    
    return partitions


def _transform_to_create_experiment_request(action_params: Dict[str, Any]) -> CreateExperimentRequest:
    """
    Transform simplified tool parameters to CreateExperimentRequest format.
    
    Args:
        action_params: Simplified parameters from Information Gatherer with keys:
                      - name: str
                      - context: str  
                      - decision_points: List[Dict] with {site, target, exclude_if_reached}
                      - conditions: List[Dict] with {code, weight}
        
    Returns:
        Complete CreateExperimentRequest for API call
    """
    # Validate required parameters
    required_keys = ['name', 'context', 'decision_points', 'conditions']
    _validate_required_params(action_params, required_keys)
    
    # Transform conditions from simplified format and get condition code to UUID mapping
    conditions, condition_code_to_id = _create_conditions(action_params['conditions'])
    
    # Transform decision_points to partitions format
    partitions = _create_partitions(action_params['decision_points'])

    experiment_segment_inclusion = _create_experiment_segment(
        inclusion_users=action_params.get('inclusion_users', []),
        inclusion_groups=action_params.get('inclusion_groups', []),
        is_inclusion=True
    )

    experiment_segment_exclusion = _create_experiment_segment(
        exclusion_users=action_params.get('exclusion_users', []),
        exclusion_groups=action_params.get('exclusion_groups', []),
        is_inclusion=False
    )
    
    # Build the complete request with defaults for required fields
    request: CreateExperimentRequest = {
        'name': action_params['name'],
        'description': action_params.get('description', ''),
        'consistencyRule': ConsistencyRule(action_params.get('consistency_rule', 'individual')),
        'assignmentUnit': AssignmentUnit(action_params.get('assignment_unit', 'individual')),
        'group': action_params.get('group_type', None),
        'type': ExperimentType('Simple'),
        'context': [action_params['context']],
        'assignmentAlgorithm': AssignmentAlgorithm('random'),
        'tags': action_params.get('tags', []),
        'conditions': conditions,
        'partitions': partitions,
        'experimentSegmentInclusion': experiment_segment_inclusion,
        'experimentSegmentExclusion': experiment_segment_exclusion,
        'filterMode': FilterMode(action_params.get('filter_mode', 'excludeAll')),
        'queries': [],
        'state': ExperimentState('inactive'),
        'postExperimentRule': PostExperimentRule(
            action_params.get('post_experiment_rule', {}).get('rule', 'continue')
        ),
        'revertTo': (
            condition_code_to_id.get(action_params.get('post_experiment_rule', {}).get('condition_code'))
            if action_params.get('post_experiment_rule', {}).get('rule') == 'assign' 
            else None
        )
    }
    
    return request


@tool
@register_executor_tool("create_experiment")
async def create_experiment(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create new experiment using prepared parameters.
    
    This tool transforms simplified parameters from the Information Gatherer 
    into the full CreateExperimentRequest format required by the API.
    
    Required parameters in action_params:
    - name: string
    - context: string 
    - decision_points: list of {site: str, target: str, exclude_if_reached: bool}
    - conditions: list of {code: str, weight: int}
    
    Optional parameters:
    - description: string
    - tags: list of strings
    - assignment_unit: 'individual' or 'group' (default: 'individual')
    - consistency_rule: 'individual' or 'group' (default: 'individual')
    - group_type: string (required if assignment_unit is 'group')
    - filter_mode: 'includeAll' or 'excludeAll' (default: 'excludeAll')
    - post_experiment_rule: {rule: 'continue'|'assign', condition_code: str}
    - inclusion_users: list of user IDs to include in experiment
    - inclusion_groups: list of {type: str, group_id: str} to include in experiment
    - exclusion_users: list of user IDs to exclude from experiment  
    - exclusion_groups: list of {type: str, group_id: str} to exclude from experiment
    
    Returns:
        Created experiment details
        
    Raises:
        ValueError: If required parameters are missing or invalid
    """
    try:
        # Transform simplified parameters to full API request
        experiment_request = _transform_to_create_experiment_request(action_params)
        
        # Call the API with the complete request
        result = await api_create_experiment(experiment_request)
        _log_execution("create_experiment", True, result)
        return result
    except Exception as e:
        _log_execution("create_experiment", False, error=str(e))
        raise


@tool
@register_executor_tool("update_experiment")
async def update_experiment(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update existing experiment using prepared parameters.
    
    Required parameters in action_params:
    - experiment_id: string
    
    Optional parameters: Any valid experiment field for partial update
    
    Returns:
        Updated experiment details
    """
    try:
        _validate_required_params(action_params, ['experiment_id'])
        experiment_id = action_params.pop('experiment_id')
        result = await api_update_experiment(experiment_id, action_params)
        _log_execution("update_experiment", True, result)
        return result
    except Exception as e:
        _log_execution("update_experiment", False, error=str(e))
        raise


@tool
@register_executor_tool("update_experiment_status")
async def update_experiment_status(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update experiment status.
    
    Required parameters in action_params:
    - experiment_id: string
    - status: string ('inactive', 'preview', 'enrolling', 'enrollmentComplete', 'cancelled')
    
    Returns:
        Updated experiment details
    """
    try:
        _validate_required_params(action_params, ['experiment_id', 'status'])
        experiment_id = action_params['experiment_id']
        status = action_params['status']
        
        result = await api_update_experiment_status(experiment_id, status)
        _log_execution("update_experiment_status", True, result)
        return result
    except Exception as e:
        _log_execution("update_experiment_status", False, error=str(e))
        raise


@tool
@register_executor_tool("delete_experiment")
async def delete_experiment(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete experiment.
    
    Required parameters in action_params:
    - experiment_id: string
    
    Returns:
        Deletion confirmation
    """
    try:
        _validate_required_params(action_params, ['experiment_id'])
        experiment_id = action_params['experiment_id']
        
        result = await api_delete_experiment(experiment_id)
        _log_execution("delete_experiment", True, result)
        return result
    except Exception as e:
        _log_execution("delete_experiment", False, error=str(e))
        raise


@tool
@register_executor_tool("init_experiment_user")
async def init_experiment_user(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize users with group memberships.
    
    Required parameters in action_params:
    - user_id: string
    
    Optional parameters:
    - group: dict of {group_type: [group_ids]}
    - working_group: dict of {group_type: group_id}
    
    Returns:
        User initialization results
    """
    try:
        _validate_required_params(action_params, ['user_id'])
        user_id = action_params.pop('user_id')
        
        result = await api_init_experiment_user(user_id, action_params)
        _log_execution("init_experiment_user", True, result)
        return result
    except Exception as e:
        _log_execution("init_experiment_user", False, error=str(e))
        raise


@tool
@register_executor_tool("get_decision_point_assignments")
async def get_decision_point_assignments(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get decision point assignments for a user.
    
    Required parameters in action_params:
    - user_id: string (passed as header)
    - context: string
    
    Returns:
        Decision point assignments
    """
    try:
        _validate_required_params(action_params, ['user_id', 'context'])
        user_id = action_params['user_id']
        context = action_params['context']
        
        result = await api_get_decision_point_assignments(user_id, {'context': context})
        _log_execution("get_decision_point_assignments", True, result)
        return result
    except Exception as e:
        _log_execution("get_decision_point_assignments", False, error=str(e))
        raise


@tool
@register_executor_tool("mark_decision_point")
async def mark_decision_point(action_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mark decision point as visited.
    
    Required parameters in action_params:
    - user_id: string (passed as header)
    - decision_point: dict with site and target
    
    Returns:
        Mark decision point results
    """
    try:
        _validate_required_params(action_params, ['user_id', 'decision_point'])
        user_id = action_params['user_id']
        decision_point = action_params['decision_point']
        
        result = await api_mark_decision_point(user_id, decision_point)
        _log_execution("mark_decision_point", True, result)
        return result
    except Exception as e:
        _log_execution("mark_decision_point", False, error=str(e))
        raise
