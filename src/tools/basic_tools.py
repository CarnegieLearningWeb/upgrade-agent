"""
Basic LangGraph tools for UpGrade API operations.

These tools wrap the UpGrade API client methods for use in the LangGraph agent.
Each tool makes a single API call and returns a standardized response format.
"""

import asyncio
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from src.api.upgrade_api import upgrade_api, UpGradeAPIError
from src.models.api_types import (
    ExperimentCreateRequest,
    ExperimentStateUpdate,
    SimpleExperimentBuilder,
    Condition,
    Partition
)


@tool
async def check_upgrade_health() -> Dict[str, Any]:
    """
    Check UpGrade service health and version information.
    
    Returns:
        Dict containing service health status, version, and response time.
    """
    try:
        response = await upgrade_api.health_check()
        return {
            "success": True,
            "data": {
                "name": response.name,
                "version": response.version,
                "description": getattr(response, 'description', 'UpGrade A/B Testing Service'),
                "status": "healthy",
                "response_time_ms": getattr(response, 'response_time_ms', None)
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
async def get_context_metadata() -> Dict[str, Any]:
    """
    Get available app contexts and their supported values (conditions, sites, targets, etc).
    
    Returns:
        Dict containing all available contexts and their metadata.
    """
    try:
        response = await upgrade_api.get_context_metadata()
        
        # Format the response for easier consumption
        contexts_list = []
        contexts_by_name = {}
        
        for context_name, context_data in response.contextMetadata.items():
            contexts_list.append(context_name)
            contexts_by_name[context_name] = {
                "conditions": context_data.CONDITIONS if context_data.CONDITIONS else [],
                "group_types": context_data.GROUP_TYPES if context_data.GROUP_TYPES else [],
                "sites": context_data.EXP_POINTS if context_data.EXP_POINTS else [],
                "targets": context_data.EXP_IDS if context_data.EXP_IDS else []
            }
        
        return {
            "success": True,
            "data": {
                "contexts": contexts_list,
                "by_context": contexts_by_name
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
async def get_all_experiments(
    context_filter: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all experiments with optional filtering by context or status.
    
    Args:
        context_filter: Optional filter by app context (e.g., "assign-prog")
        status_filter: Optional filter by status ("inactive", "enrolling", "enrollmentComplete")
    
    Returns:
        Dict containing list of experiments and summary statistics.
    """
    try:
        experiments = await upgrade_api.get_all_experiments()
        
        # Apply filters if provided
        filtered = experiments
        if context_filter:
            filtered = [exp for exp in filtered if exp.context and exp.context[0] == context_filter]
        if status_filter:
            filtered = [exp for exp in filtered if exp.state == status_filter]
        
        # Create summary statistics
        by_status = {}
        by_context = {}
        
        for exp in filtered:
            # Count by status
            status = exp.state if exp.state else "unknown"
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by context
            context = exp.context[0] if exp.context else "unknown"
            by_context[context] = by_context.get(context, 0) + 1
        
        # Format experiment data
        experiments_data = []
        for exp in filtered:
            experiments_data.append({
                "id": exp.id,
                "name": exp.name,
                "context": exp.context[0] if exp.context else None,
                "status": exp.state,
                "created_at": exp.createdAt.isoformat() if exp.createdAt else None,
                "updated_at": exp.updatedAt.isoformat() if exp.updatedAt else None
            })
        
        return {
            "success": True,
            "data": {
                "experiments": experiments_data,
                "count": len(experiments_data),
                "summary": {
                    "by_status": by_status,
                    "by_context": by_context
                }
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
async def get_experiment_details(experiment_id: str) -> Dict[str, Any]:
    """
    Get detailed configuration for a specific experiment.
    
    Args:
        experiment_id: UUID of the experiment to retrieve
    
    Returns:
        Dict containing complete experiment configuration.
    """
    try:
        experiment = await upgrade_api.get_experiment_by_id(experiment_id)
        
        # Format conditions
        conditions = []
        if experiment.conditions:
            for cond in experiment.conditions:
                conditions.append({
                    "id": cond.id,
                    "code": cond.conditionCode,
                    "weight": cond.assignmentWeight,
                    "name": cond.name,
                    "description": cond.description
                })
        
        # Format decision points
        decision_points = []
        if experiment.partitions:
            for partition in experiment.partitions:
                decision_points.append({
                    "id": partition.id,
                    "site": partition.site,
                    "target": partition.target,
                    "description": partition.description
                })
        
        return {
            "success": True,
            "data": {
                "id": experiment.id,
                "name": experiment.name,
                "status": experiment.state,
                "context": experiment.context[0] if experiment.context else None,
                "assignment_unit": experiment.assignmentUnit,
                "consistency_rule": experiment.consistencyRule,
                "post_experiment_rule": experiment.postExperimentRule,
                "conditions": conditions,
                "decision_points": decision_points,
                "filter_mode": experiment.filterMode if hasattr(experiment, 'filterMode') else None,
                "created_at": experiment.createdAt.isoformat() if experiment.createdAt else None,
                "updated_at": experiment.updatedAt.isoformat() if experiment.updatedAt else None
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
async def create_experiment(
    name: str,
    context: str,
    decision_point_site: str,
    decision_point_target: str,
    conditions: Optional[List[Dict[str, Any]]] = None,
    assignment_unit: str = "individual",
    consistency_rule: str = "individual",
    post_experiment_rule: str = "continue",
    filter_mode: str = "excludeAll",
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a new experiment with the specified configuration.
    
    Args:
        name: Experiment name
        context: App context (e.g., "assign-prog", "mathstream")
        decision_point_site: Site for the decision point
        decision_point_target: Target for the decision point
        conditions: List of conditions with 'code' and 'weight' (defaults to 50/50 control/variant)
        assignment_unit: "individual" or "group"
        consistency_rule: "individual" or "group"
        post_experiment_rule: "continue" or "assign"
        filter_mode: "excludeAll" or "includeAll"
        description: Optional experiment description
    
    Returns:
        Dict containing created experiment details.
    """
    try:
        # Default conditions if not provided
        if not conditions:
            conditions = [
                {"code": "control", "weight": 50},
                {"code": "variant", "weight": 50}
            ]
        
        # Use enterprise-grade SimpleExperimentBuilder
        try:
            experiment_request = SimpleExperimentBuilder.create_simple_experiment(
                name=name,
                context=context,
                site=decision_point_site,
                target=decision_point_target,
                conditions=conditions,
                description=description,
                assignment_unit=assignment_unit,
                consistency_rule=consistency_rule
            )
        except ValueError as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "error_type": "validation"
            }
        
        # Create the experiment
        experiment = await upgrade_api.create_experiment(experiment_request)
        
        return {
            "success": True,
            "data": {
                "experiment_id": experiment.id,
                "name": experiment.name,
                "status": experiment.state,
                "context": context,
                "validation_warnings": []
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
async def update_experiment_status(
    experiment_id: str,
    new_status: str
) -> Dict[str, Any]:
    """
    Update the status of an experiment (start/stop enrollment).
    
    Args:
        experiment_id: UUID of the experiment to update
        new_status: New status ("inactive", "enrolling", or "enrollmentComplete")
    
    Returns:
        Dict containing updated experiment status information.
    """
    try:
        # Validate status
        valid_statuses = ["inactive", "enrolling", "enrollmentComplete"]
        if new_status not in valid_statuses:
            return {
                "success": False,
                "data": None,
                "error": f"Invalid status '{new_status}'. Must be one of: {valid_statuses}",
                "error_type": "validation"
            }
        
        # Get current experiment to capture old status
        current = await upgrade_api.get_experiment_by_id(experiment_id)
        old_status = current.state
        
        # Create state update request
        state_update = ExperimentStateUpdate(
            experimentId=experiment_id,
            state=new_status
        )
        
        # Update the experiment state
        updated = await upgrade_api.update_experiment_state(state_update)
        
        return {
            "success": True,
            "data": {
                "experiment_id": updated.id,
                "experiment_name": updated.name,
                "old_status": old_status,
                "new_status": updated.state,
                "status_changed_at": updated.updatedAt.isoformat() if updated.updatedAt else None
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
async def delete_experiment(experiment_id: str) -> Dict[str, Any]:
    """
    Delete an experiment permanently.
    
    Args:
        experiment_id: UUID of the experiment to delete
    
    Returns:
        Dict confirming deletion.
    """
    try:
        # Get experiment details before deletion for the response
        experiment = await upgrade_api.get_experiment_by_id(experiment_id)
        experiment_name = experiment.name
        
        # Delete the experiment
        await upgrade_api.delete_experiment(experiment_id)
        
        return {
            "success": True,
            "data": {
                "experiment_id": experiment_id,
                "experiment_name": experiment_name,
                "deleted_at": "now"
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