"""
Conversation Analyzer tools.

Tools for intent classification and conversation orchestration.
"""

from langchain.tools import tool
from typing import Literal, Optional

from ..registry import register_analyzer_tool


@tool
@register_analyzer_tool("analyze_user_request")
def analyze_user_request(
    intent_type: Literal["direct_answer", "needs_info"],
    confidence: float,
    user_request_summary: str,
    reasoning: str,
    user_confirmed: Optional[bool] = None
) -> str:
    """Analyze user input and determine next action.
    
    This tool classifies user intent and provides context for other nodes.
    
    Args:
        intent_type: Whether the request can be answered directly or needs more info
        confidence: Confidence level in the classification (0.0 to 1.0)
        user_request_summary: Summary of what the user is asking for
        reasoning: Explanation of why this classification was chosen
        user_confirmed: True if user confirmed pending action, False if denied, None if not applicable
    """
    # Store the analysis results in global state
    from ..decorators import _state_ref
    
    if _state_ref:
        _state_ref['intent_type'] = intent_type
        _state_ref['confidence'] = confidence
        _state_ref['user_request_summary'] = user_request_summary
        if user_confirmed is not None:
            _state_ref['user_confirmed'] = user_confirmed
    
    confirmation_msg = ""
    if user_confirmed is not None:
        confirmation_msg = f" User confirmed: {user_confirmed}."
    
    return f"Intent classified as '{intent_type}' with {confidence:.2f} confidence. {reasoning}{confirmation_msg}"
