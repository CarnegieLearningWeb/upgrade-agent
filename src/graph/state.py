"""
Agent state definition for UpGradeAgent LangGraph.

This module defines the AgentState TypedDict that flows through
the 5-node LangGraph architecture.
"""

from typing import Dict, List, Optional, Any, Literal
from typing_extensions import TypedDict

from ..models.enums import ToolActionType


class AgentState(TypedDict):
    """
    State definition for UpGradeAgent LangGraph.
    
    This state flows through all 5 nodes and maintains context
    throughout the conversation.
    """
    
    # === Core Context ===
    user_input: str
    conversation_history: List[Dict[str, str]]
    current_state: Literal["ANALYZING", "GATHERING_INFO", "CONFIRMING", "EXECUTING", "RESPONDING"]
    
    # === Analyzer Outputs ===
    intent_type: Optional[Literal["direct_answer", "needs_info"]]
    confidence: Optional[float]  # 0.0 to 1.0
    user_request_summary: Optional[str]  # For other nodes to understand context, can be updated by Gatherer
    
    # === Gatherer Outputs ===
    action_needed: Optional[ToolActionType]
    action_params: Dict[str, Any]  # Collected/validated parameters
    missing_params: List[str]  # What we still need from user
    
    # === Large Static Data (Accessed On-Demand) ===
    context_metadata: Optional[Dict]  # Available contexts and their details
    experiment_names: Optional[List[Dict]]  # Experiment names and IDs
    all_experiments: Optional[List[Dict]]  # Full details of all experiments
    
    # === Dynamic Gathered Information ===
    gathered_info: Dict[str, Any]  # Query-specific data with predictable keys
    
    # === Confirmation Flow ===
    needs_confirmation: bool
    confirmation_message: Optional[str]
    user_confirmed: Optional[bool]
    
    # === Execution Log ===
    execution_log: List[Dict[str, Any]]  # Chronological log of all executed actions
    
    # === Error Handling ===
    errors: Dict[str, str]  # {"api": "Failed to connect", "auth": "Invalid token", etc.}
    
    # === Response ===
    final_response: Optional[str]
    conversation_complete: bool


def create_initial_state() -> AgentState:
    """
    Create initial state for a new conversation.
    
    Returns:
        AgentState with default values
    """
    return AgentState(
        user_input="",
        conversation_history=[],
        current_state="ANALYZING",
        
        intent_type=None,
        confidence=None,
        user_request_summary=None,
        
        action_needed=None,
        action_params={},
        missing_params=[],
        
        context_metadata=None,
        experiment_names=None,
        all_experiments=None,
        
        gathered_info={},
        
        needs_confirmation=False,
        confirmation_message=None,
        user_confirmed=None,
        
        execution_log=[],
        
        errors={},
        
        final_response=None,
        conversation_complete=False
    )
