"""
LangGraph state definition for UpGradeAgent.

This module defines the AgentState TypedDict that flows through the 5-node
LangGraph architecture. The state manages conversation context, gathered
information, execution history, and error handling across all nodes.
"""

from typing import Dict, List, Optional, Any, Literal, TypedDict

from src.models.tool_types import (
    ToolHealthResponse,
    ToolExperimentName,
    SimplifiedExperiment,
    ToolExecutionResult
)


class AgentState(TypedDict):
    """
    Shared state that flows through the LangGraph nodes.
    
    This state maintains all conversation context, gathered information,
    and execution history throughout the agent's operation.
    """
    
    # === Core Context ===
    user_input: str
    conversation_history: List[Dict[str, str]]
    current_state: Literal[
        "ANALYZING", 
        "GATHERING_INFO", 
        "CONFIRMING", 
        "EXECUTING", 
        "RESPONDING"
    ]
    
    # === Analyzer Outputs ===
    intent_type: Optional[Literal["direct_answer", "needs_info"]]
    confidence: Optional[float]  # 0.0 to 1.0
    user_request_summary: Optional[str]  # For other nodes to understand context
    
    # === Gatherer Outputs ===
    action_needed: Optional[Literal[
        "create_experiment", 
        "update_experiment", 
        "delete_experiment",
        "update_experiment_status", 
        "init_experiment_user", 
        "get_decision_point_assignments", 
        "mark_decision_point"
    ]]
    action_params: Dict[str, Any]  # Collected/validated parameters
    missing_params: List[str]  # What we still need from user
    
    # === Large Static Data (Accessed On-Demand) ===
    context_metadata: Optional[Dict[str, Any]]  # Available contexts and their details
    experiment_names: Optional[List[ToolExperimentName]]  # Experiment names and IDs
    all_experiments: Optional[List[SimplifiedExperiment]]  # Full details of all experiments
    
    # === Dynamic Gathered Information ===
    gathered_info: Dict[str, Any]  # Query-specific data with predictable keys
    
    # === Confirmation Flow ===
    needs_confirmation: bool
    confirmation_message: Optional[str]
    user_confirmed: bool
    
    # === Execution Log ===
    execution_log: List[ToolExecutionResult]  # Chronological log of all executed actions
    
    # === Error Handling ===
    errors: Dict[str, str]  # {"api": "...", "auth": "...", "validation": "...", etc.}
    
    # === Response ===
    final_response: Optional[str]
    conversation_complete: bool


def create_initial_state(user_input: str) -> AgentState:
    """
    Create an initial AgentState with default values.
    
    Args:
        user_input: The user's input message
        
    Returns:
        AgentState with initialized default values
    """
    return AgentState(
        # Core context
        user_input=user_input,
        conversation_history=[],
        current_state="ANALYZING",
        
        # Analyzer outputs
        intent_type=None,
        confidence=None,
        user_request_summary=None,
        
        # Gatherer outputs
        action_needed=None,
        action_params={},
        missing_params=[],
        
        # Large static data
        context_metadata=None,
        experiment_names=None,
        all_experiments=None,
        
        # Dynamic gathered information
        gathered_info={},
        
        # Confirmation flow
        needs_confirmation=False,
        confirmation_message=None,
        user_confirmed=False,
        
        # Execution log
        execution_log=[],
        
        # Error handling
        errors={},
        
        # Response
        final_response=None,
        conversation_complete=False
    )
