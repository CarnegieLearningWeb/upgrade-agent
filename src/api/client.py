"""
Low-level HTTP client for the UpGrade API.

This module provides the core HTTP client functionality for making requests
to the UpGrade API with proper authentication, error handling, and response parsing.
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from src.config.config import config
from src.api.auth import auth_manager
from src.models.constants import CONTENT_TYPE_JSON, ACCEPT_JSON
from src.exceptions.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
    ExperimentNotFoundError,
    create_api_exception,
)


class UpGradeClient:
    """
    Low-level HTTP client for UpGrade API communication.
    
    This class handles:
    - HTTP request/response lifecycle
    - Authentication via auth_manager
    - Error handling and exception mapping
    - JSON serialization/deserialization
    - Timeout and retry logic
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the UpGrade API client.
        
        Args:
            base_url: Base URL for the UpGrade API (defaults to config)
            timeout: Request timeout in seconds (defaults to 30)
            session: Optional existing aiohttp session to reuse
        """
        self.base_url = base_url or config.UPGRADE_API_URL
        self.timeout = timeout or 30
        self._session = session
        self._owned_session = session is None
        
        # Ensure base_url ends with /
        if not self.base_url.endswith('/'):
            self.base_url += '/'
    
    async def __aenter__(self) -> "UpGradeClient":
        """Async context manager entry."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._owned_session and self._session:
            await self._session.close()
            self._session = None
    
    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create the HTTP session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session if we own it."""
        if self._owned_session and self._session:
            await self._session.close()
            self._session = None
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        # Remove leading slash if present to avoid double slashes
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        return urljoin(self.base_url, endpoint)
    
    def _get_auth_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers for authenticated endpoints."""
        try:
            return auth_manager.get_headers(include_auth=include_auth)
        except Exception as e:
            # Convert auth errors to our exception types
            if "Authentication failed" in str(e):
                raise AuthenticationError(f"Failed to get authentication headers: {str(e)}")
            raise APIError(f"Failed to build request headers: {str(e)}")
    
    def _get_user_headers(self, user_id: str) -> Dict[str, str]:
        """Get request headers for v6 user simulation endpoints."""
        return {
            "Content-Type": CONTENT_TYPE_JSON,
            "Accept": ACCEPT_JSON,
            "User-Id": user_id
        }
    
    def _handle_response_error(
        self, 
        status_code: int, 
        response_text: str, 
        endpoint: str
    ) -> None:
        """Handle HTTP error responses by raising appropriate exceptions."""
        # Try to parse error response for more details
        error_details = None
        try:
            error_data = json.loads(response_text)
            if isinstance(error_data, dict):
                error_details = error_data
        except (json.JSONDecodeError, TypeError):
            # If we can't parse JSON, use raw response text
            pass
        
        # Create appropriate exception based on status code
        exception = create_api_exception(
            status_code=status_code,
            response_body=response_text,
            endpoint=endpoint,
            message=f"HTTP {status_code} error for {endpoint}"
        )
        
        # Add parsed error details if available
        if error_details and hasattr(exception, 'details'):
            exception.details.update(error_details)
        
        raise exception
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the UpGrade API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base_url)
            data: Request body data (will be JSON encoded)
            params: URL query parameters
            include_auth: Whether to include authentication headers
            user_id: User ID for v6 endpoints (adds User-Id header, disables auth)
            **kwargs: Additional arguments for aiohttp request
        
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            APIError: For general API errors
            AuthenticationError: For auth-related errors
            ValidationError: For validation errors
            ExperimentNotFoundError: For 404 errors on experiment endpoints
        """
        url = self._build_url(endpoint)
        
        # Build headers based on endpoint type
        if user_id is not None:
            # v6 endpoints: User-Id header, no auth token
            headers = self._get_user_headers(user_id)
        else:
            # Regular endpoints: use auth manager
            headers = self._get_auth_headers(include_auth=include_auth)
        
        # Prepare request arguments
        request_kwargs = {
            'headers': headers,
            'params': params,
            **kwargs
        }
        
        # Add JSON data if provided
        if data is not None:
            request_kwargs['json'] = data
        
        try:
            async with self.session.request(method, url, **request_kwargs) as response:
                response_text = await response.text()
                
                # Check for HTTP errors
                if not response.ok:
                    self._handle_response_error(response.status, response_text, endpoint)
                
                # Parse JSON response
                try:
                    if response_text.strip():
                        return json.loads(response_text)
                    else:
                        # Empty response body (e.g., for DELETE requests)
                        return {}
                except json.JSONDecodeError as e:
                    raise APIError(
                        f"Invalid JSON response from {endpoint}: {str(e)}",
                        status_code=response.status,
                        response_body=response_text,
                        endpoint=endpoint
                    )
        
        except aiohttp.ClientError as e:
            # Network-level errors
            raise APIError(
                f"Network error communicating with UpGrade API: {str(e)}",
                endpoint=endpoint
            )
        except asyncio.TimeoutError:
            raise APIError(
                f"Request to {endpoint} timed out after {self.timeout} seconds",
                endpoint=endpoint
            )
    
    async def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request(
            'GET', endpoint, params=params, include_auth=include_auth, 
            user_id=user_id, **kwargs
        )
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._make_request(
            'POST', endpoint, data=data, params=params, include_auth=include_auth, 
            user_id=user_id, **kwargs
        )
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request(
            'PUT', endpoint, data=data, params=params, include_auth=include_auth,
            user_id=user_id, **kwargs
        )
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request(
            'DELETE', endpoint, params=params, include_auth=include_auth,
            user_id=user_id, **kwargs
        )


# Global client instance for convenience
_global_client: Optional[UpGradeClient] = None


def get_client() -> UpGradeClient:
    """
    Get or create a global UpGrade client instance.
    
    Returns:
        Shared UpGradeClient instance
    """
    global _global_client
    if _global_client is None:
        _global_client = UpGradeClient()
    return _global_client


async def close_global_client():
    """Close the global client session."""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None
