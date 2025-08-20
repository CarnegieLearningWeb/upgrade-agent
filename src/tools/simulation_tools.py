"""User simulation tools for UpGrade API operations."""

import uuid
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from src.api.upgrade_api import upgrade_api, UpGradeAPIError
from src.models.api_types import (
    InitRequest,
    MarkRequest,
    MarkData,
    AssignedCondition
)


@tool
async def init_user(
    user_id: str,
    group: Optional[Dict[str, List[str]]] = None,
    working_group: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Initialize a user in the UpGrade system.
    
    Args:
        user_id: Unique identifier for the user
        group: Group memberships as dict with string keys and list values
        working_group: Current working group as dict with string key-value pairs
    
    Returns:
        Dict with success status, user data, and error information.
    """
    try:
        init_request = InitRequest(group=group, workingGroup=working_group)
        response = await upgrade_api.init_user(user_id, init_request)
        
        return {
            "success": True,
            "data": {
                "user_id": response.id,
                "group": response.group if response.group else None,
                "working_group": response.workingGroup if response.workingGroup else None
            },
            "error": None
        }
    except UpGradeAPIError as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "api"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "unknown"
        }


@tool
async def assign_condition(
    user_id: str,
    context: str
) -> Dict[str, Any]:
    """
    Get experiment condition assignments for a user.
    
    Args:
        user_id: Unique identifier for the user
        context: Application context for experiments
    
    Returns:
        Dict with success status, assignment data, and error information.
    """
    try:
        assignments = await upgrade_api.assign_condition(user_id, context)
        
        formatted_assignments = []
        for assignment in assignments:
            assigned_conditions = []
            
            if hasattr(assignment, 'assignedCondition') and assignment.assignedCondition:
                for condition in assignment.assignedCondition:
                    assigned_conditions.append({
                        "id": condition.id if hasattr(condition, 'id') else None,
                        "conditionCode": condition.conditionCode if hasattr(condition, 'conditionCode') else None,
                        "payload": condition.payload if hasattr(condition, 'payload') else None,
                        "experimentId": condition.experimentId if hasattr(condition, 'experimentId') else None
                    })
            
            formatted_assignments.append({
                "site": assignment.site,
                "target": assignment.target,
                "experimentType": assignment.experimentType if hasattr(assignment, 'experimentType') else None,
                "assignedCondition": assigned_conditions,
                "assignedFactor": assignment.assignedFactor if hasattr(assignment, 'assignedFactor') else None
            })
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "context": context,
                "assignments": formatted_assignments,
                "assignment_count": len(formatted_assignments)
            },
            "error": None
        }
    except UpGradeAPIError as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "api"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "unknown"
        }


@tool
async def mark_decision_point(
    user_id: str,
    site: str,
    target: str,
    assigned_condition: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record that a user has visited a decision point.
    
    Args:
        user_id: Unique identifier for the user
        site: Decision point site identifier
        target: Decision point target identifier
        assigned_condition: Condition object from assign_condition response
    
    Returns:
        Dict with success status, mark data, and error information.
    """
    try:
        assigned_condition_obj = None
        status = "no condition assigned"
        
        if assigned_condition:
            assigned_condition_obj = AssignedCondition(
                id=assigned_condition.get("id"),
                conditionCode=assigned_condition.get("conditionCode"),
                payload=assigned_condition.get("payload", {}),
                experimentId=assigned_condition.get("experimentId")
            )
            status = "condition applied"
        
        mark_data = MarkData(target=target, site=site, assignedCondition=assigned_condition_obj)
        mark_request = MarkRequest(data=mark_data, status=status)
        response = await upgrade_api.mark_decision_point(user_id, mark_request)
        
        formatted_response = {
            "mark_id": response.id if hasattr(response, 'id') else None,
            "user_id": response.userId if hasattr(response, 'userId') else user_id,
            "site": response.site if hasattr(response, 'site') else site,
            "target": response.target if hasattr(response, 'target') else target,
            "condition": response.condition if hasattr(response, 'condition') else None,
            "experiment_id": response.experimentId if hasattr(response, 'experimentId') else None
        }
        
        return {
            "success": True,
            "data": formatted_response,
            "error": None
        }
    except UpGradeAPIError as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "api"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "unknown"
        }