"""
Tool Executor action tools.

These tools execute the actual API calls for modifying UpGrade state.
They use the prepared parameters from the Information Gatherer and
log all executions in the execution_log.
"""

from langchain.tools import tool
from typing import Dict, List, Any, Optional, Union

from src.tools.registry import register_executor_tool
from src.api.endpoints.experiments import (
    create_experiment as api_create_experiment,
    get_experiment_details as api_get_experiment_details,
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
    InitExperimentUserRequest, ExperimentAssignmentRequest, MarkExperimentRequest,
    MarkData, MarkAssignedCondition
)
from src.models.tool_types import ( 
    SimplifiedExperiment, ToolInitExperimentUserResponse, ToolAssignedCondition,
    ToolExperimentAssignment, ToolMarkExperimentResponse
)
from src.utils.execution_logging import _log_execution
from src.utils.tool_validation import _validate_required_params
from src.utils.experiment_transforms import _transform_experiment_data
from src.utils.experiment_builders import (
    _transform_to_create_experiment_request,
    _convert_experiment_to_create_request,
    _apply_updates_to_experiment_request
)

@tool
@register_executor_tool("create_experiment")
async def create_experiment(action_params: Dict[str, Any]) -> SimplifiedExperiment:
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
    """
    try:
        _validate_required_params(action_params, ['name', 'context', 'decision_points', 'conditions'])
        
        # Transform simplified parameters to full API request
        experiment_request = _transform_to_create_experiment_request(action_params)
        
        # Call the API with the complete request
        result = await api_create_experiment(experiment_request)
        
        # Transform the API response to simplified format
        simplified_result = _transform_experiment_data(result)
        _log_execution("create_experiment", True, simplified_result)
        return simplified_result
    except Exception as e:
        _log_execution("create_experiment", False, error=str(e))
        raise


@tool
@register_executor_tool("update_experiment")
async def update_experiment(action_params: Dict[str, Any]) -> SimplifiedExperiment:
    """
    Update existing experiment using prepared parameters.
    
    This tool implements a fetch-modify-update pattern:
    1. Fetches current experiment configuration
    2. Converts it to update request format
    3. Applies partial updates from action_params
    4. Sends the complete updated configuration to the API
    
    Required parameters in action_params:
    - experiment_id: string
    
    Optional parameters: Any valid experiment field for partial update including:
    - name: string
    - description: string
    - conditions: list of {code: str, weight: int} (simplified format)
    - decision_points: list of {site: str, target: str, exclude_if_reached: bool}
    - inclusion_users, exclusion_users: list of user IDs
    - inclusion_groups, exclusion_groups: list of {type: str, group_id: str}
    - post_experiment_rule: {rule: 'continue'|'assign', condition_code: str}
    - tags: list of strings
    - state: experiment state
    - assignment_unit: 'individual' or 'group'
    - consistency_rule: 'individual' or 'group'
    - filter_mode: 'excludeAll' or 'includeAll'
    - context: string (will be converted to list format)
    - And other experiment configuration fields
    """
    try:
        _validate_required_params(action_params, ['experiment_id'])
        experiment_id = action_params['experiment_id']
        
        # Remove experiment_id from action_params to avoid including it in updates
        update_params = action_params.copy()
        del update_params['experiment_id']
        
        # Step 1: Fetch current experiment configuration
        current_experiment = await api_get_experiment_details(experiment_id)
        
        # Step 2: Convert current experiment to CreateExperimentRequest format
        base_request = _convert_experiment_to_create_request(current_experiment)
        
        # Step 3: Apply partial updates from action_params
        updated_request = _apply_updates_to_experiment_request(base_request, update_params)
        
        # Step 4: Send the complete updated configuration to the API
        result = await api_update_experiment(experiment_id, updated_request)
        
        # Transform the API response to simplified format
        simplified_result = _transform_experiment_data(result)
        _log_execution("update_experiment", True, simplified_result)
        return simplified_result
    except Exception as e:
        _log_execution("update_experiment", False, error=str(e))
        raise


@tool
@register_executor_tool("update_experiment_status")
async def update_experiment_status(action_params: Dict[str, Any]) -> SimplifiedExperiment:
    """
    Update experiment status.
    
    Required parameters in action_params:
    - experiment_id: string
    - status: string ('inactive', 'preview', 'enrolling', 'enrollmentComplete', 'cancelled')
    """
    try:
        _validate_required_params(action_params, ['experiment_id', 'status'])
        experiment_id = action_params['experiment_id']
        status = action_params['status']
        
        result = await api_update_experiment_status(experiment_id, status)
        
        # Transform the API response to simplified format
        simplified_result = _transform_experiment_data(result)
        _log_execution("update_experiment_status", True, simplified_result)
        return simplified_result
    except Exception as e:
        _log_execution("update_experiment_status", False, error=str(e))
        raise


@tool
@register_executor_tool("delete_experiment")
async def delete_experiment(action_params: Dict[str, Any]) -> SimplifiedExperiment:
    """
    Delete experiment.
    
    Required parameters in action_params:
    - experiment_id: string
    """
    try:
        _validate_required_params(action_params, ['experiment_id'])
        experiment_id = action_params['experiment_id']
        
        result = await api_delete_experiment(experiment_id)
        
        # Transform the API response to simplified format
        simplified_result = _transform_experiment_data(result)
        _log_execution("delete_experiment", True, simplified_result)
        return simplified_result
    except Exception as e:
        _log_execution("delete_experiment", False, error=str(e))
        raise


@tool
@register_executor_tool("init_experiment_user")
async def init_experiment_user(action_params: Dict[str, Any]) -> ToolInitExperimentUserResponse:
    """
    Initialize users with group memberships.
    
    Required parameters in action_params:
    - user_id: string
    
    Optional parameters:
    - group: dict of {group_type: [group_ids]}
    - working_group: dict of {group_type: group_id}
    """
    try:
        _validate_required_params(action_params, ['user_id'])
        user_id = action_params.pop('user_id')
        
        # Build InitExperimentUserRequest from action_params
        init_request: InitExperimentUserRequest = {}
        
        if 'group' in action_params:
            init_request['group'] = action_params['group']
            
        if 'working_group' in action_params:
            init_request['workingGroup'] = action_params['working_group']
        
        response = await api_init_experiment_user(user_id, init_request)

        tool_response: ToolInitExperimentUserResponse = {
            'user_id': response.get('id', 'unknown'),
            'group': response.get('group', None),
            'working_group': response.get('workingGroup', None)
        }

        _log_execution("init_experiment_user", True, tool_response)
        return tool_response
    except Exception as e:
        _log_execution("init_experiment_user", False, error=str(e))
        raise


@tool
@register_executor_tool("get_decision_point_assignments")
async def get_decision_point_assignments(action_params: Dict[str, Any]) -> List[ToolExperimentAssignment]:
    """
    Get decision point assignments for a user.
    
    Required parameters in action_params:
    - user_id: string
    - context: string
    """
    try:
        _validate_required_params(action_params, ['user_id', 'context'])
        user_id = action_params['user_id']
        
        # Build ExperimentAssignmentRequest from action_params
        assignment_request: ExperimentAssignmentRequest = {
            'context': action_params['context']
        }
        
        response = await api_get_decision_point_assignments(user_id, assignment_request)

        # Response format: {"data": [ExperimentAssignment, ...]}
        tool_assignments: List[ToolExperimentAssignment] = []
        
        if 'data' in response and isinstance(response['data'], list):
            for assignment in response['data']:
                # Convert assigned conditions from API format to tool format
                assigned_conditions: List[ToolAssignedCondition] = [
                    {
                        'condition_code': condition.get('conditionCode', ''),
                        'experiment_id': condition.get('experimentId', None)
                    }
                    for condition in assignment.get('assignedCondition', [])
                ]

                tool_assignment: ToolExperimentAssignment = {
                    'site': assignment.get('site', 'unknown'),
                    'target': assignment.get('target', 'unknown'),
                    'assigned_conditions': assigned_conditions
                }
                tool_assignments.append(tool_assignment)

        _log_execution("get_decision_point_assignments", True, tool_assignments)
        return tool_assignments
    except Exception as e:
        _log_execution("get_decision_point_assignments", False, error=str(e))
        raise


@tool
@register_executor_tool("mark_decision_point")
async def mark_decision_point(action_params: Dict[str, Any]) -> ToolMarkExperimentResponse:
    """
    Mark decision point as visited.
    
    Required parameters in action_params:
    - user_id: string
    - decision_point: dict with site and target
    - assigned_condition: dict with condition_code and experiment_id
    """
    try:
        _validate_required_params(action_params, ['user_id', 'decision_point', 'assigned_condition'])
        user_id = action_params['user_id']
        
        # Build MarkData from action_params
        decision_point = action_params['decision_point']
        assigned_condition = action_params['assigned_condition']
        
        # Build MarkAssignedCondition
        mark_assigned_condition: Optional[MarkAssignedCondition] = None
        if assigned_condition:
            mark_assigned_condition = {
                'conditionCode': assigned_condition.get('condition_code', None),
                'experimentId': assigned_condition.get('experiment_id', None)
            }
        
        # Build MarkData
        mark_data: MarkData = {
            'site': decision_point['site'],
            'target': decision_point['target'],
            'assignedCondition': mark_assigned_condition
        }
        
        # Build MarkExperimentRequest
        mark_request: MarkExperimentRequest = {
            'data': mark_data
        }
        
        response = await api_mark_decision_point(user_id, mark_request)

        tool_response: ToolMarkExperimentResponse = {
            'user_id': response.get('userId', 'unknown'),
            'site': response.get('site', 'unknown'),
            'target': response.get('target', 'unknown'),
            'experiment_id': response.get('experimentId', None),
            'condition_code': response.get('condition', None)
        }

        _log_execution("mark_decision_point", True, tool_response)
        return tool_response
    except Exception as e:
        _log_execution("mark_decision_point", False, error=str(e))
        raise
