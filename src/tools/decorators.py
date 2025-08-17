"""
Tool decorators for UpGradeAgent.

This module provides decorators for automatic state management, error handling,
and tool function registration in the LangGraph architecture.
"""

import functools
from typing import Dict, Any, Callable, Optional
import logging
import asyncio

# Global state reference for decorator access
_state_ref: Optional[Dict[str, Any]] = None

logger = logging.getLogger(__name__)


def set_global_state(state: Dict[str, Any]) -> None:
    """
    Set the global state reference for decorators to use.
    
    This function should be called once when initializing the agent
    to provide decorators access to the current state.
    
    Args:
        state: The AgentState instance to use globally
    """
    global _state_ref
    _state_ref = state
    logger.debug("Global state reference set for decorators")


def get_global_state() -> Optional[Dict[str, Any]]:
    """
    Get the current global state reference.
    
    Returns:
        The current AgentState instance or None if not set
    """
    return _state_ref


def auto_store(key: str):
    """
    Decorator that automatically stores function results in agent state.
    
    The decorated function's return value will be stored in the
    gathered_info dictionary under the specified key.
    
    Args:
        key: The key to store the result under in state["gathered_info"]
        
    Example:
        @auto_store("experiment_list")
        def get_experiments():
            return ["exp1", "exp2"]
        
        # After calling get_experiments(), state["gathered_info"]["experiment_list"] 
        # will contain ["exp1", "exp2"]
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Store result in global state if available
                    if _state_ref is not None:
                        # Ensure gathered_info exists
                        if "gathered_info" not in _state_ref:
                            _state_ref["gathered_info"] = {}
                        _state_ref["gathered_info"][key] = result
                        logger.debug(f"Stored result under key '{key}' in gathered_info")
                    else:
                        logger.warning(f"Global state not available, cannot store result for key '{key}'")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in auto_store wrapper for {func.__name__}: {e}")
                    raise
                
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    
                    # Store result in global state if available
                    if _state_ref is not None:
                        # Ensure gathered_info exists
                        if "gathered_info" not in _state_ref:
                            _state_ref["gathered_info"] = {}
                        _state_ref["gathered_info"][key] = result
                        logger.debug(f"Stored result under key '{key}' in gathered_info")
                    else:
                        logger.warning(f"Global state not available, cannot store result for key '{key}'")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in auto_store wrapper for {func.__name__}: {e}")
                    raise
            
            return sync_wrapper
    
    return decorator


def auto_store_static(state_key: str):
    """
    Decorator that stores results in static data fields of agent state.
    
    This is used for large, relatively static data like experiment lists
    or context metadata that should be cached in the state.
    
    Args:
        state_key: The state key to store the result under (e.g., "experiment_names")
        
    Example:
        @auto_store_static("experiment_names")
        def get_all_experiment_names():
            return [{"id": 1, "name": "exp1"}]
        
        # After calling, state["experiment_names"] will contain the result
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Store result in global state if available
                    if _state_ref is not None:
                        _state_ref[state_key] = result
                        logger.debug(f"Stored result in state key '{state_key}'")
                    else:
                        logger.warning(f"Global state not available, cannot store result for key '{state_key}'")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in auto_store_static wrapper for {func.__name__}: {e}")
                    raise
                
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    
                    # Store result in global state if available
                    if _state_ref is not None:
                        _state_ref[state_key] = result
                        logger.debug(f"Stored result in state key '{state_key}'")
                    else:
                        logger.warning(f"Global state not available, cannot store result for key '{state_key}'")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in auto_store_static wrapper for {func.__name__}: {e}")
                    raise
            
            return sync_wrapper
    
    return decorator


def handle_errors(error_key: str = "general"):
    """
    Decorator that catches exceptions and stores them in agent state.
    
    Exceptions are caught and mapped to specific error types, then stored
    in state["errors"][error_key] for the agent to handle gracefully.
    
    Args:
        error_key: The key to store error messages under in state["errors"]
        
    Example:
        @handle_errors("api")
        def call_api():
            raise Exception("API failed")
        
        # After calling, state["errors"]["api"] will contain "API failed"
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                        
                except Exception as e:
                    _handle_error(e, func.__name__, error_key)
                    raise
                
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    _handle_error(e, func.__name__, error_key)
                    raise
            
            return sync_wrapper
    
    return decorator


def _handle_error(e: Exception, func_name: str, error_key: str):
    """Helper function to handle and categorize errors."""
    # Map exception types to error categories
    try:
        from src.exceptions import (
            APIError, 
            AuthenticationError, 
            ValidationError, 
            ExperimentNotFoundError
        )
        
        if isinstance(e, AuthenticationError):
            error_type = "auth"
        elif isinstance(e, ValidationError):
            error_type = "validation"
        elif isinstance(e, ExperimentNotFoundError):
            error_type = "not_found"
        elif isinstance(e, APIError):
            error_type = "api"
        else:
            error_type = "unknown"
    except ImportError:
        error_type = "unknown"
    
    error_msg = str(e)
    logger.error(f"Error in {func_name}: {error_msg} (type: {error_type})")
    
    # Store error in global state if available
    if _state_ref is not None:
        if "errors" not in _state_ref:
            _state_ref["errors"] = {}
        _state_ref["errors"][error_key] = f"{error_type}: {error_msg}"
        logger.debug(f"Stored {error_type} error under key '{error_key}' in errors")
    else:
        logger.warning(f"Global state not available, cannot store error for key '{error_key}'")


def tool_metadata(**metadata):
    """
    Decorator for adding metadata to tool functions.
    
    This decorator adds metadata attributes to tool functions that can be
    used by the registry system for documentation and introspection.
    
    Args:
        **metadata: Arbitrary metadata key-value pairs
        
    Example:
        @tool_metadata(description="Gets experiment list", category="query")
        def get_experiments():
            return []
    """
    def decorator(func: Callable) -> Callable:
        # Add metadata as function attributes
        for key, value in metadata.items():
            setattr(func, f"_tool_{key}", value)
        
        return func
    
    return decorator
