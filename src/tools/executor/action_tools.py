"""
Tool Executor action tools.

These tools execute the actual API calls for modifying UpGrade state.
They use the prepared parameters from the Information Gatherer and
log all executions in the execution_log.
"""

from langchain.tools import tool
from typing import Dict, List, Any, Optional, Union
from uuid import uuid4

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
    ToolExperimentAssignment, ToolMarkExperimentResponse, ToolConditionBalanceResponse
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
    """
    try:
        _validate_required_params(action_params, ['user_id'])
        user_id = action_params['user_id']
        
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


@tool
@register_executor_tool("visit_decision_point")
async def visit_decision_point(action_params: Dict[str, Any]) -> ToolMarkExperimentResponse:
    """
    Simulate a decision point visit (calls /init, /assign, and /mark)
    """
    try:
        _validate_required_params(action_params, ['user_id', 'context', 'site', 'target'])
        user_id = action_params['user_id']
        context = action_params['context']
        site = action_params['site']
        target = action_params['target']

        # Build InitExperimentUserRequest from action_params
        init_request: InitExperimentUserRequest = {}
        
        if 'group' in action_params:
            init_request['group'] = action_params['group']
            
        if 'working_group' in action_params:
            init_request['workingGroup'] = action_params['working_group']
        
        await api_init_experiment_user(user_id, init_request)

        # Build ExperimentAssignmentRequest from action_params
        assignment_request: ExperimentAssignmentRequest = {
            'context': context
        }
        
        assign_response = await api_get_decision_point_assignments(user_id, assignment_request)

        # Response format: {"data": [ExperimentAssignment, ...]}
        tool_assignments: List[ToolExperimentAssignment] = []
        mark_assigned_condition: Optional[MarkAssignedCondition] = None
        
        if 'data' in assign_response and isinstance(assign_response['data'], list):
            for assignment in assign_response['data']:
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

                # Set the mark_assigned_condition that matches the site and target
                if tool_assignment['site'] == site and tool_assignment['target'] == target and assigned_conditions:
                    mark_assigned_condition = {
                        'conditionCode': assigned_conditions[0].get('condition_code', None),
                        'experimentId': assigned_conditions[0].get('experiment_id', None)
                    }
                    break
        
        # Build MarkData
        mark_data: MarkData = {
            'site': site,
            'target': target,
            'assignedCondition': mark_assigned_condition
        }
        
        # Build MarkExperimentRequest
        mark_request: MarkExperimentRequest = {
            'data': mark_data
        }
        
        mark_response = await api_mark_decision_point(user_id, mark_request)

        tool_response: ToolMarkExperimentResponse = {
            'user_id': mark_response.get('userId', 'unknown'),
            'site': mark_response.get('site', 'unknown'),
            'target': mark_response.get('target', 'unknown'),
            'experiment_id': mark_response.get('experimentId', None),
            'condition_code': mark_response.get('condition', None)
        }

        _log_execution("visit_decision_point", True, tool_response)
        return tool_response
    except Exception as e:
        _log_execution("visit_decision_point", False, error=str(e))
        raise


@tool
@register_executor_tool("test_condition_balance")
async def test_condition_balance(action_params: Dict[str, Any]) -> ToolConditionBalanceResponse:
    """
    Simulate multiple decision point visits for testing condition balance (calls /init, /assign, and /mark interatively)
    """
    try:
        _validate_required_params(action_params, ['num_users', 'context', 'site', 'target'])
        num_users = action_params['num_users']
        context = action_params['context']
        site = action_params['site']
        target = action_params['target']

        # Enrollment by condition dict (condition_code: enrollment_data)
        enrollment_by_condition: Dict[str, int] = {}

        for i in range(min(num_users, 1000)):
            user_id = str(uuid4())

            # Build InitExperimentUserRequest from action_params
            init_request: InitExperimentUserRequest = {}

            if 'group' in action_params:
                init_request['group'] = action_params['group']

            if 'working_group' in action_params:
                init_request['workingGroup'] = action_params['working_group']

            await api_init_experiment_user(user_id, init_request)

            # Build ExperimentAssignmentRequest from action_params
            assignment_request: ExperimentAssignmentRequest = {
                'context': context
            }

            assign_response = await api_get_decision_point_assignments(user_id, assignment_request)

            # Response format: {"data": [ExperimentAssignment, ...]}
            tool_assignments: List[ToolExperimentAssignment] = []
            mark_assigned_condition: Optional[MarkAssignedCondition] = None
            
            if 'data' in assign_response and isinstance(assign_response['data'], list):
                for assignment in assign_response['data']:
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

                    # Set the mark_assigned_condition that matches the site and target
                    if tool_assignment['site'] == site and tool_assignment['target'] == target and assigned_conditions:
                        mark_assigned_condition = {
                            'conditionCode': assigned_conditions[0].get('condition_code', None),
                            'experimentId': assigned_conditions[0].get('experiment_id', None)
                        }
                        break
            
            # Build MarkData
            mark_data: MarkData = {
                'site': site,
                'target': target,
                'assignedCondition': mark_assigned_condition
            }
            
            # Build MarkExperimentRequest
            mark_request: MarkExperimentRequest = {
                'data': mark_data
            }

            mark_response = await api_mark_decision_point(user_id, mark_request)
            condition_code = mark_response.get('condition', None)

            if condition_code:
                enrollment_by_condition[condition_code] = enrollment_by_condition.get(condition_code, 0) + 1

        tool_response: ToolConditionBalanceResponse = {
            'num_users': num_users,
            'site': site,
            'target': target,
            'enrollment_by_condition': enrollment_by_condition
        }

        _log_execution("test_condition_balance", True, tool_response)
        return tool_response
    except Exception as e:
        _log_execution("test_condition_balance", False, error=str(e))
        raise