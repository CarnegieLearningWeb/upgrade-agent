"""
UpGrade API endpoint functions.

Simple wrapper functions that call API endpoints and return raw responses.
"""

from .system import check_upgrade_health, get_context_metadata
from .experiments import (
    get_experiment_names,
    get_all_experiments, 
    get_experiment_details,
    get_enrollment_details,
    create_experiment,
    update_experiment,
    update_experiment_status,
    delete_experiment,
)
from .simulation import (
    init_experiment_user,
    get_decision_point_assignments,
    mark_decision_point,
)

__all__ = [
    # System endpoints
    "check_upgrade_health",
    "get_context_metadata",
    
    # Experiment endpoints
    "get_experiment_names",
    "get_all_experiments",
    "get_experiment_details",
    "get_enrollment_details",
    "create_experiment",
    "update_experiment",
    "update_experiment_status",
    "delete_experiment",
    
    # Simulation endpoints
    "init_experiment_user",
    "get_decision_point_assignments", 
    "mark_decision_point",
]
