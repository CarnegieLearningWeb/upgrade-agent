"""
Shared constants for the UpGrade API client.

This module contains application-wide constants that are used across
multiple modules, including HTTP headers, content types, and other
shared string literals to maintain consistency and avoid duplication.
"""

# HTTP Header Values
CONTENT_TYPE_JSON = "application/json"
ACCEPT_JSON = "application/json"

# System endpoint paths
HEALTH_ENDPOINT = "/"
CONTEXT_METADATA_ENDPOINT = "/experiments/contextMetaData"

# Experiment endpoint paths
EXPERIMENTS_ENDPOINT = "/experiments"
EXPERIMENT_NAMES_ENDPOINT = "/experiments/names"
EXPERIMENT_SINGLE_ENDPOINT = "/experiments/single"
EXPERIMENT_STATE_ENDPOINT = "/experiments/state"
ENROLLMENT_DETAILS_ENDPOINT = "/stats/enrollment/detail"

# Simulation endpoint paths
INIT_ENDPOINT = "/v6/init"
ASSIGN_ENDPOINT = "/v6/assign"
MARK_ENDPOINT = "/v6/mark"

