"""
Execution logging utilities.

Functions for logging tool execution events and tracking execution state.
"""

from typing import Any, Optional
from datetime import datetime


def _log_execution(action: str, success: bool, result: Any = None, error: Optional[str] = None):
    """Log tool execution to the execution_log."""
    from src.tools.decorators import _state_ref
    if _state_ref is None:
        return
        
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "success": success,
        "result": result if success else None,
        "error": error if not success else None
    }
    
    if "execution_log" not in _state_ref:
        _state_ref["execution_log"] = []
    _state_ref["execution_log"].append(log_entry)
