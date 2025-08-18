"""
Experiment request building utilities.

Functions for creating and converting experiment data structures for API requests.
"""

from typing import Dict, List, Any, Optional, Union
from uuid import uuid4

from src.models.types import (
    CreateExperimentRequest, CreateCondition, CreatePartition,
    CreateExperimentSegment, CreateSegment, CreateIndividualForSegment, CreateGroupForSegment,
    Experiment, Condition, Partition, ExperimentSegment
)
from src.models.enums import (
    ExperimentState, ExperimentType, AssignmentUnit, ConsistencyRule, 
    FilterMode, PostExperimentRule, AssignmentAlgorithm, SegmentType
)


def _create_experiment_segment(
    inclusion_users: Optional[List[str]] = None,
    inclusion_groups: Optional[List[Dict[str, str]]] = None,
    exclusion_users: Optional[List[str]] = None,
    exclusion_groups: Optional[List[Dict[str, str]]] = None,
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
    # Transform conditions from simplified format and get condition code to UUID mapping
    conditions, condition_code_to_id = _create_conditions(action_params['conditions'])
    
    # Transform decision_points to partitions format
    partitions = _create_partitions(action_params['decision_points'])

    # Handle filter_mode-specific logic for inclusion segment
    filter_mode = action_params.get('filter_mode', 'excludeAll')
    if filter_mode == 'includeAll':
        # When filter_mode is includeAll, override inclusion users/groups
        inclusion_users = []
        inclusion_groups = [{"type": "All", "group_id": "All"}]
    else:
        # For other filter modes (like excludeAll), use provided values
        inclusion_users = action_params.get('inclusion_users', [])
        inclusion_groups = action_params.get('inclusion_groups', [])

    experiment_segment_inclusion = _create_experiment_segment(
        inclusion_users=inclusion_users,
        inclusion_groups=inclusion_groups,
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


def _convert_condition_to_create_condition(condition: Condition) -> CreateCondition:
    """Convert API response Condition to CreateCondition format."""
    return CreateCondition(
        id=condition['id'],
        twoCharacterId=condition.get('twoCharacterId'),
        conditionCode=condition['conditionCode'],
        assignmentWeight=condition['assignmentWeight'],
        description=condition.get('description'),
        order=condition['order'],
        name=condition.get('name'),
        levelCombinationElements=condition.get('levelCombinationElements')
    )


def _convert_partition_to_create_partition(partition: Partition) -> CreatePartition:
    """Convert API response Partition to CreatePartition format."""
    return CreatePartition(
        id=partition['id'],
        twoCharacterId=partition.get('twoCharacterId'),
        site=partition['site'],
        target=partition.get('target'),
        description=partition.get('description'),
        order=partition['order'],
        excludeIfReached=partition['excludeIfReached']
    )


def _convert_experiment_segment_to_create_segment(exp_segment: ExperimentSegment) -> CreateExperimentSegment:
    """Convert API response ExperimentSegment to CreateExperimentSegment format."""
    segment = exp_segment['segment']
    
    # Convert individuals
    individuals = []
    for individual in segment['individualForSegment']:
        individuals.append(CreateIndividualForSegment(
            userId=individual['userId']
        ))
    
    # Convert groups  
    groups = []
    for group in segment['groupForSegment']:
        groups.append(CreateGroupForSegment(
            groupId=group['groupId'],
            type=group['type']
        ))
    
    create_segment: CreateSegment = {
        'individualForSegment': individuals,
        'groupForSegment': groups,
        'subSegments': segment.get('subSegments', []),
        'type': segment['type']
    }
    
    return CreateExperimentSegment(segment=create_segment)


def _convert_experiment_to_create_request(experiment: Union[Experiment, Dict[str, Any]]) -> CreateExperimentRequest:
    """
    Convert API response Experiment to CreateExperimentRequest format.
    
    This function handles the transformation of an existing experiment
    (with API response structure) back to the create request format
    needed for updates.
    
    Args:
        experiment: Full experiment object from API response
        
    Returns:
        CreateExperimentRequest suitable for update API calls
    """
    # Convert nested objects to create format
    conditions = [_convert_condition_to_create_condition(c) for c in experiment['conditions']]
    partitions = [_convert_partition_to_create_partition(p) for p in experiment['partitions']]
    
    # Convert segments
    inclusion_segment = _convert_experiment_segment_to_create_segment(experiment['experimentSegmentInclusion'])
    exclusion_segment = _convert_experiment_segment_to_create_segment(experiment['experimentSegmentExclusion'])
    
    # Build the complete request with the input experiment data
    request: CreateExperimentRequest = {
        'name': experiment['name'],
        'description': experiment['description'],
        'consistencyRule': experiment['consistencyRule'],
        'assignmentUnit': experiment['assignmentUnit'],
        'type': experiment['type'],
        'context': experiment['context'],
        'assignmentAlgorithm': experiment['assignmentAlgorithm'],
        'tags': experiment['tags'],
        'conditions': conditions,
        'partitions': partitions,
        'experimentSegmentInclusion': inclusion_segment,
        'experimentSegmentExclusion': exclusion_segment,
        'filterMode': experiment['filterMode'],
        'state': experiment['state'],
        'postExperimentRule': experiment['postExperimentRule']
    }
    
    # Only include optional fields if they exist and have values
    optional_fields = [
        'group', 'conditionOrder', 'stratificationFactor', 'conditionPayloads',
        'factors', 'queries', 'endOn', 'enrollmentCompleteCondition', 
        'startOn', 'revertTo', 'moocletPolicyParameters', 'rewardMetricKey'
    ]

    for field in optional_fields:
        if field in experiment and experiment[field] is not None:
            request[field] = experiment[field]
    
    return request


def _apply_simple_field_updates(
    updated_request: CreateExperimentRequest, 
    action_params: Dict[str, Any]
) -> None:
    """Apply simple field updates to the experiment request with proper key mapping."""
    
    # Direct 1:1 mappings for supported update fields (action_params key → CreateExperimentRequest key)
    direct_mappings = {
        'name': 'name',
        'description': 'description', 
        'tags': 'tags',
        'assignment_unit': 'assignmentUnit',
        'consistency_rule': 'consistencyRule',
        'filter_mode': 'filterMode',
        'group_type': 'group'
    }
    
    # Apply direct mappings (no enum conversion needed - these are just string values)
    for action_key, request_key in direct_mappings.items():
        if action_key in action_params:
            updated_request[request_key] = action_params[action_key]
    
    # Handle context (ensure it's a list)
    if 'context' in action_params:
        context = action_params['context']
        updated_request['context'] = [context] if isinstance(context, str) else context


def _build_condition_code_to_id_mapping(conditions: List[CreateCondition]) -> Dict[str, str]:
    """Build condition code to ID mapping from existing conditions."""
    return {condition['conditionCode']: condition['id'] for condition in conditions}


def _apply_conditions_update(
    updated_request: CreateExperimentRequest, 
    action_params: Dict[str, Any]
) -> Dict[str, str]:
    """Apply conditions update and return condition code to ID mapping."""
    # Start with mapping from existing conditions (for post-experiment rule reference)
    condition_code_to_id = _build_condition_code_to_id_mapping(updated_request['conditions'])
    
    if 'conditions' in action_params:
        conditions_data = action_params['conditions']
        if conditions_data and isinstance(conditions_data[0], dict) and 'code' in conditions_data[0]:
            # Simplified format - transform using existing function
            conditions, new_condition_code_to_id = _create_conditions(conditions_data)
            updated_request['conditions'] = conditions
            # Update the mapping with new conditions
            condition_code_to_id = new_condition_code_to_id
    
    return condition_code_to_id


def _apply_segments_update(
    updated_request: CreateExperimentRequest, 
    action_params: Dict[str, Any]
) -> None:
    """Apply segment updates (inclusion/exclusion) with filter_mode-specific logic."""
    
    # Handle inclusion segment with filter_mode logic
    should_update_inclusion = any(key in action_params for key in ['inclusion_users', 'inclusion_groups', 'filter_mode'])
    
    if should_update_inclusion:
        filter_mode = action_params.get('filter_mode')
        
        if filter_mode == 'includeAll':
            # When filter_mode is includeAll, override with 'All' group
            inclusion_users = []
            inclusion_groups = [{"type": "All", "group_id": "All"}]
        else:
            # For all other cases (excludeAll or no filter_mode change)
            # Only use action_params values if they are explicitly provided
            # Otherwise preserve existing values from updated_request
            
            existing_inclusion = updated_request.get('experimentSegmentInclusion', {}).get('segment', {})
            existing_users = [ind['userId'] for ind in existing_inclusion.get('individualForSegment', [])]
            existing_groups = [
                {"type": grp['type'], "group_id": grp['groupId']} 
                for grp in existing_inclusion.get('groupForSegment', [])
            ]
            
            # Use provided values only if explicitly present, otherwise preserve existing
            inclusion_users = action_params['inclusion_users'] if 'inclusion_users' in action_params else existing_users
            inclusion_groups = action_params['inclusion_groups'] if 'inclusion_groups' in action_params else existing_groups
        
        inclusion_segment = _create_experiment_segment(
            inclusion_users=inclusion_users,
            inclusion_groups=inclusion_groups,
            is_inclusion=True
        )
        updated_request['experimentSegmentInclusion'] = inclusion_segment
        
    # Handle exclusion segment (no filter_mode logic needed)
    if any(key in action_params for key in ['exclusion_users', 'exclusion_groups']):
        # Get existing exclusion data to preserve if not provided
        existing_exclusion = updated_request.get('experimentSegmentExclusion', {}).get('segment', {})
        existing_excl_users = [ind['userId'] for ind in existing_exclusion.get('individualForSegment', [])]
        existing_excl_groups = [
            {"type": grp['type'], "group_id": grp['groupId']} 
            for grp in existing_exclusion.get('groupForSegment', [])
        ]
        
        # Use provided values only if explicitly present, otherwise preserve existing
        exclusion_users = action_params['exclusion_users'] if 'exclusion_users' in action_params else existing_excl_users
        exclusion_groups = action_params['exclusion_groups'] if 'exclusion_groups' in action_params else existing_excl_groups
        
        exclusion_segment = _create_experiment_segment(
            exclusion_users=exclusion_users,
            exclusion_groups=exclusion_groups,
            is_inclusion=False
        )
        updated_request['experimentSegmentExclusion'] = exclusion_segment


def _apply_post_experiment_rule_update(
    updated_request: CreateExperimentRequest, 
    action_params: Dict[str, Any],
    condition_code_to_id: Dict[str, str]
) -> None:
    """Apply post-experiment rule updates with proper field mapping."""
    if 'post_experiment_rule' not in action_params:
        return
        
    rule_data = action_params['post_experiment_rule']
    rule_type = rule_data.get('rule', 'continue')
    
    # Map to the correct field name (no enum conversion needed)
    updated_request['postExperimentRule'] = rule_type
    
    # Handle revertTo UUID mapping for 'assign' rule
    if rule_type == 'assign' and 'condition_code' in rule_data:
        condition_code = rule_data['condition_code']
        
        # Try to use the mapping from conditions update first (if conditions were also updated)
        if condition_code in condition_code_to_id:
            updated_request['revertTo'] = condition_code_to_id[condition_code]
        else:
            # Find the condition ID from existing conditions in the request
            for condition in updated_request['conditions']:
                if condition['conditionCode'] == condition_code:
                    updated_request['revertTo'] = condition['id']
                    break
            else:
                # If condition not found, log warning but don't fail
                # This could happen if the condition_code is invalid
                pass
    elif rule_type == 'continue':
        # For continue rule, revertTo should be None
        updated_request['revertTo'] = None


def _apply_updates_to_experiment_request(
    base_request: CreateExperimentRequest, 
    action_params: Dict[str, Any]
) -> CreateExperimentRequest:
    """
    Apply partial updates from action_params to a base CreateExperimentRequest.
    
    This function handles special cases where action_params might contain
    simplified formats that need transformation.
    
    Args:
        base_request: Base experiment request (converted from existing experiment)
        action_params: Partial updates to apply
        
    Returns:
        Updated CreateExperimentRequest with changes applied
    """
    # Create a copy to avoid modifying the original
    updated_request = base_request.copy()
    
    # Apply simple field updates
    _apply_simple_field_updates(updated_request, action_params)
    
    # Apply conditions update and get mapping
    condition_code_to_id = _apply_conditions_update(updated_request, action_params)
    
    # Handle decision_points to partitions transformation
    if 'decision_points' in action_params:
        partitions = _create_partitions(action_params['decision_points'])
        updated_request['partitions'] = partitions
    
    # Apply segment updates
    _apply_segments_update(updated_request, action_params)
    
    # Apply post-experiment rule updates
    _apply_post_experiment_rule_update(updated_request, action_params, condition_code_to_id)
    
    return updated_request
